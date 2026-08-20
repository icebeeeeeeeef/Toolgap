#!/usr/bin/env python3
"""Write and verify immutable G0-C-ATOMIC-010 phase and terminal receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


FAILURE_STATUSES = {
    "BLOCKED_BEFORE_EXECUTION",
    "EXECUTION_FAILED_AFTER_START",
    "INVALID_SCOPE",
}
PHASE_STATUSES = {"ADMITTED_PRE_ARM", "CONTROLS_PASSED", "SERVING_PASSED"}
SEALED_EXCLUSIONS = {"artifact-index.json", "completion-receipt.json"}
PHASE_RECEIPTS = (
    ("preflight-status.json", "ADMITTED_PRE_ARM"),
    ("controls-passed.json", "CONTROLS_PASSED"),
    ("serving-passed.json", "SERVING_PASSED"),
)
FAILURE_PREDECESSORS = {
    "preflight": (),
    "contract-controls": PHASE_RECEIPTS[:1],
    "serving-arms": PHASE_RECEIPTS[:2],
    "final-verification": PHASE_RECEIPTS,
}
FAILURE_PHASE_STATUSES = {
    "preflight": {"BLOCKED_BEFORE_EXECUTION"},
    "contract-controls": {"INVALID_SCOPE"},
    "serving-arms": {"EXECUTION_FAILED_AFTER_START", "INVALID_SCOPE"},
    "final-verification": {"INVALID_SCOPE"},
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_exclusive(path: Path, document: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(document, indent=2, sort_keys=True) + "\n"
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode=0o444)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(encoded)
    path.chmod(0o444)


def load_json_object(path: Path, label: str) -> dict[str, object]:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{label} must be a JSON object: {path}")
    return document


def require_exact_keys(
    document: dict[str, object], expected: set[str], label: str
) -> None:
    actual = set(document)
    if actual != expected:
        raise ValueError(
            f"{label} fields differ: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )


def require_hex(value: object, length: int, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        rf"[0-9a-f]{{{length}}}", value
    ):
        raise ValueError(f"invalid {label}")
    return value


def require_relative_file(run_dir: Path, relative: object, label: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError(f"invalid {label} path")
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError(f"{label} escapes the attempt directory: {relative}")
    path = run_dir / relative_path
    if not path.is_file():
        raise ValueError(f"missing {label}: {relative}")
    return path


def validate_attempt_context(run_dir: Path) -> dict[str, object]:
    context = load_json_object(run_dir / "attempt-context.json", "attempt context")
    require_exact_keys(
        context,
        {
            "admission_manifest",
            "attempt_id",
            "created_at",
            "experiment_id",
            "spec_path",
            "spec_sha256",
            "toolgap_commit",
            "toolgap_tracked_clean",
            "toolgap_tree",
        },
        "attempt context",
    )
    if context["experiment_id"] != "G0-C-ATOMIC-010":
        raise ValueError("attempt context has the wrong experiment identity")
    if not isinstance(context["attempt_id"], str) or not re.fullmatch(
        r"[A-Za-z0-9._-]+", context["attempt_id"]
    ):
        raise ValueError("attempt context has an invalid attempt ID")
    if context["spec_path"] != "experiments/g0/SPEC.g0-c-010.md":
        raise ValueError("attempt context has the wrong SPEC path")
    require_hex(context["spec_sha256"], 64, "attempt SPEC SHA-256")
    require_hex(context["toolgap_commit"], 40, "ToolGap commit")
    require_hex(context["toolgap_tree"], 40, "ToolGap tree")
    if not isinstance(context["toolgap_tracked_clean"], bool):
        raise ValueError("attempt tracked-clean readback is not boolean")
    for field in ("admission_manifest", "created_at"):
        if not isinstance(context[field], str) or not context[field]:
            raise ValueError(f"attempt context has invalid {field}")
    return context


def validate_phase_receipts(
    run_dir: Path,
    manifest_sha256: str,
    receipts: tuple[tuple[str, str], ...],
) -> None:
    for name, status in receipts:
        receipt = load_json_object(run_dir / name, f"phase receipt {name}")
        require_exact_keys(
            receipt, {"created_at", "manifest_sha256", "status"}, name
        )
        if (
            receipt["status"] != status
            or receipt["manifest_sha256"] != manifest_sha256
            or not isinstance(receipt["created_at"], str)
            or not receipt["created_at"]
        ):
            raise ValueError(f"invalid phase receipt: {name}")


def validate_manifest(
    run_dir: Path, context: dict[str, object]
) -> tuple[dict[str, object], str]:
    manifest_path = run_dir / "manifest.json"
    manifest = load_json_object(manifest_path, "admission manifest")
    checksum_path = run_dir / "manifest.sha256"
    if not checksum_path.is_file():
        raise ValueError("missing manifest.sha256")
    checksum_fields = checksum_path.read_text(encoding="utf-8").split()
    manifest_sha256 = sha256(manifest_path)
    if not checksum_fields or checksum_fields[0] != manifest_sha256:
        raise ValueError("manifest.sha256 does not match manifest.json")
    identity = manifest.get("identity")
    outcome = manifest.get("outcome")
    if not isinstance(identity, dict) or not isinstance(outcome, dict):
        raise ValueError("manifest lacks identity or outcome")
    expected_identity = {
        "attempt_id": context["attempt_id"],
        "experiment_id": "G0-C-ATOMIC-010",
        "gate": "G0",
        "spec_path": context["spec_path"],
        "spec_sha256": context["spec_sha256"],
        "toolgap_commit": context["toolgap_commit"],
        "toolgap_tree": context["toolgap_tree"],
        "toolgap_tracked_clean": True,
    }
    for field, expected in expected_identity.items():
        if identity.get(field) != expected:
            raise ValueError(f"manifest identity mismatch: {field}")
    if context["toolgap_tracked_clean"] is not True:
        raise ValueError("admitted manifest is paired with a dirty attempt context")
    if (
        outcome.get("claim_state") != "roadmap"
        or outcome.get("gate_decision")
        != "N/A: manifest sealed before runtime arms"
    ):
        raise ValueError("manifest outcome exceeds the pre-runtime claim")
    return manifest, manifest_sha256


def validate_success_bundle(
    run_dir: Path, indexed_paths: set[str] | None = None
) -> None:
    context = validate_attempt_context(run_dir)
    manifest, manifest_sha256 = validate_manifest(run_dir, context)
    validate_phase_receipts(run_dir, manifest_sha256, PHASE_RECEIPTS)
    planned = manifest.get("planned_success_artifacts")
    if (
        not isinstance(planned, list)
        or not planned
        or any(not isinstance(item, str) for item in planned)
        or len(set(planned)) != len(planned)
    ):
        raise ValueError("manifest has an invalid planned-success artifact set")
    for relative in planned:
        require_relative_file(run_dir, relative, "planned success artifact")
    if indexed_paths is not None and not set(planned).issubset(indexed_paths):
        raise ValueError("artifact index omits planned success artifacts")


def validate_failure_prerequisites(
    run_dir: Path, phase: str, attempt_status: str
) -> None:
    if phase not in FAILURE_PREDECESSORS:
        raise ValueError(f"unsupported failure phase: {phase}")
    if attempt_status not in FAILURE_PHASE_STATUSES[phase]:
        raise ValueError(f"failure status {attempt_status} is invalid for {phase}")
    context = validate_attempt_context(run_dir)
    predecessors = FAILURE_PREDECESSORS[phase]
    if predecessors:
        _, manifest_sha256 = validate_manifest(run_dir, context)
        validate_phase_receipts(run_dir, manifest_sha256, predecessors)


def require_terminal_paths_absent(run_dir: Path) -> None:
    for name in ("execution-status.json", "artifact-index.json", "completion-receipt.json"):
        if (run_dir / name).exists():
            raise ValueError(f"refusing to replace terminal artifact: {name}")


def build_index(run_dir: Path) -> Path:
    output = run_dir / "artifact-index.json"
    if output.exists():
        raise ValueError(f"refusing to replace artifact index: {output}")
    files: list[dict[str, object]] = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(run_dir).as_posix()
        if relative in SEALED_EXCLUSIONS:
            continue
        files.append(
            {
                "path": relative,
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    write_json_exclusive(output, {"artifact_dir": ".", "files": files})
    return output


def write_receipt(args: argparse.Namespace) -> int:
    if args.status not in PHASE_STATUSES:
        raise ValueError(f"unsupported phase receipt status: {args.status}")
    if not re.fullmatch(r"[0-9a-f]{64}", args.manifest_sha256):
        raise ValueError("manifest SHA-256 must be 64 lowercase hex characters")
    write_json_exclusive(
        args.output,
        {
            "status": args.status,
            "manifest_sha256": args.manifest_sha256,
            "created_at": now(),
        },
    )
    print(args.output)
    return 0


def write_failure(args: argparse.Namespace) -> int:
    if args.attempt_status not in FAILURE_STATUSES:
        raise ValueError(f"unsupported failure status: {args.attempt_status}")
    run_dir = args.run_dir.resolve()
    if not run_dir.is_dir():
        raise ValueError(f"missing attempt directory: {run_dir}")
    require_terminal_paths_absent(run_dir)
    validate_failure_prerequisites(run_dir, args.phase, args.attempt_status)
    write_json_exclusive(
        run_dir / "execution-status.json",
        {
            "attempt_status": args.attempt_status,
            "claim_state": "roadmap",
            "exit_code": args.exit_code,
            "gate_decision": "N/A",
            "line": args.line,
            "phase": args.phase,
            "recorded_at": now(),
        },
    )
    build_index(run_dir)
    return 0


def write_success(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    if not run_dir.is_dir():
        raise ValueError(f"missing attempt directory: {run_dir}")
    if args.phase != "final-verification":
        raise ValueError("success may only be sealed during final-verification")
    require_terminal_paths_absent(run_dir)
    validate_success_bundle(run_dir)
    status_path = run_dir / "execution-status.json"
    write_json_exclusive(
        status_path,
        {
            "attempt_status": "N/A: completion receipt not sealed",
            "claim_state": "roadmap",
            "gate_decision": "N/A",
            "phase": args.phase,
            "protocol_status": "ALL_PREDECLARED_CHECKS_PASSED",
            "recorded_at": now(),
        },
    )
    index_path = build_index(run_dir)
    write_json_exclusive(
        run_dir / "completion-receipt.json",
        {
            "artifact_index_sha256": sha256(index_path),
            "attempt_status": "COMPLETED",
            "claim_state": "roadmap",
            "execution_status_sha256": sha256(status_path),
            "gate_decision": "N/A: independent review pending",
            "sealed_at": now(),
            "status": "PROTOCOL_COMPLETE_AWAITING_INDEPENDENT_REVIEW",
        },
    )
    print(f"SEALED_SUCCESS_AWAITING_INDEPENDENT_REVIEW: {run_dir}")
    return 0


def verify_index(run_dir: Path) -> dict[str, object]:
    index_path = run_dir / "artifact-index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    indexed: dict[str, dict[str, object]] = {}
    for item in index["files"]:
        relative = item["path"]
        if relative in indexed or relative in SEALED_EXCLUSIONS:
            raise ValueError(f"invalid duplicate or excluded index path: {relative}")
        indexed[relative] = item
    actual = {
        path.relative_to(run_dir).as_posix()
        for path in run_dir.rglob("*")
        if path.is_file()
        and path.relative_to(run_dir).as_posix() not in SEALED_EXCLUSIONS
    }
    if actual != set(indexed):
        raise ValueError(
            f"indexed file set differs from attempt: missing={sorted(actual - set(indexed))}, "
            f"extra={sorted(set(indexed) - actual)}"
        )
    for relative, item in indexed.items():
        path = run_dir / relative
        if path.stat().st_size != item["size_bytes"] or sha256(path) != item["sha256"]:
            raise ValueError(f"artifact identity mismatch: {relative}")
    if "execution-status.json" not in indexed:
        raise ValueError("artifact index does not contain execution-status.json")
    return index


def verify_seal(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    index = verify_index(run_dir)
    indexed_paths = {item["path"] for item in index["files"]}
    status_path = run_dir / "execution-status.json"
    status = load_json_object(status_path, "execution status")
    receipt_path = run_dir / "completion-receipt.json"
    if receipt_path.exists():
        require_exact_keys(
            status,
            {
                "attempt_status",
                "claim_state",
                "gate_decision",
                "phase",
                "protocol_status",
                "recorded_at",
            },
            "successful execution status",
        )
        if (
            status["attempt_status"] != "N/A: completion receipt not sealed"
            or status["claim_state"] != "roadmap"
            or status["gate_decision"] != "N/A"
            or status["phase"] != "final-verification"
            or status["protocol_status"] != "ALL_PREDECLARED_CHECKS_PASSED"
            or not isinstance(status["recorded_at"], str)
            or not status["recorded_at"]
        ):
            raise ValueError("successful execution status has invalid semantics")
        validate_success_bundle(run_dir, indexed_paths)
        receipt = load_json_object(receipt_path, "completion receipt")
        require_exact_keys(
            receipt,
            {
                "artifact_index_sha256",
                "attempt_status",
                "claim_state",
                "execution_status_sha256",
                "gate_decision",
                "sealed_at",
                "status",
            },
            "completion receipt",
        )
        index_path = run_dir / "artifact-index.json"
        if (
            receipt["attempt_status"] != "COMPLETED"
            or receipt["claim_state"] != "roadmap"
            or receipt["gate_decision"] != "N/A: independent review pending"
            or receipt["status"]
            != "PROTOCOL_COMPLETE_AWAITING_INDEPENDENT_REVIEW"
            or receipt["artifact_index_sha256"] != sha256(index_path)
            or receipt["execution_status_sha256"] != sha256(status_path)
            or not isinstance(receipt["sealed_at"], str)
            or not receipt["sealed_at"]
        ):
            raise ValueError("completion receipt has invalid semantics or hashes")
    else:
        require_exact_keys(
            status,
            {
                "attempt_status",
                "claim_state",
                "exit_code",
                "gate_decision",
                "line",
                "phase",
                "recorded_at",
            },
            "failure execution status",
        )
        if (
            status["attempt_status"] not in FAILURE_STATUSES
            or status["claim_state"] != "roadmap"
            or status["gate_decision"] != "N/A"
            or not isinstance(status["exit_code"], int)
            or not isinstance(status["line"], int)
            or not isinstance(status["recorded_at"], str)
            or not status["recorded_at"]
        ):
            raise ValueError("failure execution status has invalid semantics")
        validate_failure_prerequisites(
            run_dir, str(status["phase"]), str(status["attempt_status"])
        )
    print(f"VERIFIED_SEAL: {run_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    receipt = subparsers.add_parser("receipt")
    receipt.add_argument("--output", required=True, type=Path)
    receipt.add_argument("--status", required=True)
    receipt.add_argument("--manifest-sha256", required=True)
    receipt.set_defaults(handler=write_receipt)

    failure = subparsers.add_parser("failure")
    failure.add_argument("--run-dir", required=True, type=Path)
    failure.add_argument("--attempt-status", required=True)
    failure.add_argument("--phase", required=True)
    failure.add_argument("--exit-code", required=True, type=int)
    failure.add_argument("--line", required=True, type=int)
    failure.set_defaults(handler=write_failure)

    success = subparsers.add_parser("success")
    success.add_argument("--run-dir", required=True, type=Path)
    success.add_argument("--phase", required=True)
    success.set_defaults(handler=write_success)

    verify = subparsers.add_parser("verify")
    verify.add_argument("--run-dir", required=True, type=Path)
    verify.set_defaults(handler=verify_seal)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
