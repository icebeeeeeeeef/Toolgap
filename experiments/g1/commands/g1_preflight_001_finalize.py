#!/usr/bin/env python3
"""Seal one no-action G1-PREFLIGHT-001 runtime admission attempt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SUCCESS_ARTIFACTS = (
    "attempt-context.json",
    "environment.txt",
    "source-seed.txt",
    "input-manifest-verify.log",
    "input-manifest.json",
    "bootstrap-receipt.json",
    "toolgap-seed-verify.log",
    "source-restore.log",
    "model-seed-prepare.log",
    "model-snapshot.json",
    "build-install.log",
    "dependency-lock.txt",
    "runtime-install-report.json",
    "sglang-provenance.json",
    "test-module-provenance.json",
    "runtime.env",
    "manifest.json",
    "manifest.sha256",
    "schema.log",
    "smoke.log",
    "smoke.pid",
    "smoke.pgid",
    "smoke-gpu-pids-before.txt",
    "smoke-gpu-pids-during.txt",
    "smoke-gpu-pids-attributable.txt",
    "smoke-gpu-pids-after.txt",
    "smoke-gpu-pids-leaked.txt",
    "smoke-process-group-after.txt",
    "smoke-listeners-after.txt",
    "shutdown.log",
)
TERMINALS = {"artifact-index.json", "completion-receipt.json", "execution-status.json"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path, label: str) -> dict[str, object]:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{label} must be a JSON object")
    return document


def write_json_exclusive(path: Path, document: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(document, indent=2, sort_keys=True) + "\n"
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(encoded)
    path.chmod(0o444)


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True
    ).strip()


def relative(path: Path, root: Path, label: str) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"{label} escapes the attempt directory") from error


def read_smoke(path: Path) -> dict[str, object]:
    records = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and value.get("kind") == "G1_PREFLIGHT_SERVER_STARTED":
            records.append(value)
    if len(records) != 1:
        raise ValueError("smoke log must contain exactly one startup record")
    if records[0].get("skip_server_warmup") is not True:
        raise ValueError("smoke startup did not disable generation warmup")
    return records[0]


def validate_context(run_dir: Path) -> dict[str, object]:
    context = load_json(run_dir / "attempt-context.json", "attempt context")
    expected = {
        "attempt_id",
        "bundle_id",
        "claim_state",
        "created_at",
        "gate",
        "gate_decision",
        "spec_path",
        "spec_sha256",
        "toolgap_commit",
        "toolgap_tracked_clean",
        "toolgap_tree",
    }
    if set(context) != expected:
        raise ValueError("attempt context fields differ")
    if (
        context["bundle_id"] != "G1-PREFLIGHT-001"
        or context["claim_state"] != "roadmap"
        or context["gate"] != "G1"
        or context["gate_decision"] != "N/A"
        or context["spec_path"] != "experiments/g1/SPEC.g1-preflight-001.md"
        or context["toolgap_tracked_clean"] is not True
    ):
        raise ValueError("attempt context exceeds the preformal contract")
    if not isinstance(context["attempt_id"], str) or not re.fullmatch(
        r"[A-Za-z0-9._-]+", context["attempt_id"]
    ):
        raise ValueError("invalid attempt ID")
    for field, length in (("spec_sha256", 64), ("toolgap_commit", 40), ("toolgap_tree", 40)):
        if not isinstance(context[field], str) or not re.fullmatch(
            rf"[0-9a-f]{{{length}}}", context[field]
        ):
            raise ValueError(f"invalid {field}")
    return context


def render(args: argparse.Namespace) -> int:
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"refusing to replace manifest: {output}")
    repo = args.repo_root.resolve()
    run_dir = output.parent
    if git(repo, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("ToolGap tracked files must be clean")
    context = validate_context(run_dir)
    template = load_json(args.template.resolve(), "manifest template")
    inputs = {
        "environment": run_dir / "environment.txt",
        "input_manifest": run_dir / "input-manifest.json",
        "input_manifest_verification": run_dir / "input-manifest-verify.log",
        "bootstrap_receipt": run_dir / "bootstrap-receipt.json",
        "toolgap_seed_verification": run_dir / "toolgap-seed-verify.log",
        "model_snapshot": run_dir / "model-snapshot.json",
        "provenance": run_dir / "sglang-provenance.json",
        "runtime_env": run_dir / "runtime.env",
        "test_module_provenance": run_dir / "test-module-provenance.json",
    }
    for label, path in inputs.items():
        if not path.is_file():
            raise ValueError(f"missing manifest input {label}: {path}")
    input_manifest = load_json(inputs["input_manifest"], "input manifest")
    archives = input_manifest.get("archives")
    if not isinstance(archives, dict) or set(archives) != {
        "model_snapshot", "sglang_source_seed", "toolgap_source_seed"
    }:
        raise ValueError("input manifest archive set differs")
    template["identity"].update(
        {
            "attempt_id": context["attempt_id"],
            "spec_sha256": context["spec_sha256"],
            "toolgap_commit": context["toolgap_commit"],
            "toolgap_tree": context["toolgap_tree"],
        }
    )
    template["runtime_inputs"] = {
        label: {"path": relative(path, run_dir, label), "sha256": sha256(path)}
        for label, path in inputs.items()
    }
    template["offline_archives"] = archives
    template["rendered_at"] = now()
    write_json_exclusive(output, template)
    return 0


def index(run_dir: Path) -> Path:
    output = run_dir / "artifact-index.json"
    if output.exists():
        raise ValueError("refusing to replace artifact index")
    files = []
    for path in sorted(run_dir.rglob("*")):
        relative = path.relative_to(run_dir).as_posix()
        if path.is_file() and relative not in {"artifact-index.json", "completion-receipt.json"}:
            files.append(
                {
                    "path": relative,
                    "sha256": sha256(path),
                    "size_bytes": path.stat().st_size,
                }
            )
    write_json_exclusive(output, {"artifact_dir": ".", "files": files})
    return output


def finish(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    if any((run_dir / name).exists() for name in TERMINALS):
        raise ValueError("attempt already has a terminal artifact")
    context = validate_context(run_dir)
    for name in SUCCESS_ARTIFACTS:
        if not (run_dir / name).is_file():
            raise ValueError(f"missing successful-attempt artifact: {name}")
    manifest = load_json(run_dir / "manifest.json", "manifest")
    if manifest.get("identity", {}).get("attempt_id") != context["attempt_id"]:
        raise ValueError("manifest attempt identity differs")
    expected_manifest_sha = sha256(run_dir / "manifest.json")
    checksum = (run_dir / "manifest.sha256").read_text(encoding="utf-8").split()
    if not checksum or checksum[0] != expected_manifest_sha:
        raise ValueError("manifest checksum differs")
    if "OK" not in (run_dir / "schema.log").read_text(encoding="utf-8", errors="replace"):
        raise ValueError("schema test did not report OK")
    smoke = read_smoke(run_dir / "smoke.log")
    shutdown = (run_dir / "shutdown.log").read_text(encoding="utf-8")
    if "cleanup=true\n" not in shutdown or "smoke_exit_status=0\n" not in shutdown:
        raise ValueError("scripted runtime did not prove clean teardown")
    write_json_exclusive(
        run_dir / "execution-status.json",
        {
            "attempt_status": "COMPLETED",
            "claim_state": "roadmap",
            "gate_decision": "N/A",
            "kind": "preformal_runtime_validation",
            "recorded_at": now(),
            "smoke": smoke,
        },
    )
    artifact_index = index(run_dir)
    write_json_exclusive(
        run_dir / "completion-receipt.json",
        {
            "artifact_index_sha256": sha256(artifact_index),
            "claim_state": "roadmap",
            "execution_status_sha256": sha256(run_dir / "execution-status.json"),
            "gate_decision": "N/A",
            "sealed_at": now(),
            "status": "PREFORMAL_RUNTIME_ADMISSION_COMPLETE",
        },
    )
    return 0


def fail(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    if any((run_dir / name).exists() for name in TERMINALS):
        raise ValueError("attempt already has a terminal artifact")
    if args.status not in {"BLOCKED_BEFORE_RUNTIME", "RUNTIME_FAILED"}:
        raise ValueError("unsupported failure status")
    write_json_exclusive(
        run_dir / "execution-status.json",
        {
            "attempt_status": args.status,
            "claim_state": "roadmap",
            "exit_code": args.exit_code,
            "gate_decision": "N/A",
            "phase": args.phase,
            "recorded_at": now(),
        },
    )
    index(run_dir)
    return 0


def verify_index(run_dir: Path) -> dict[str, dict[str, object]]:
    index_doc = load_json(run_dir / "artifact-index.json", "artifact index")
    if set(index_doc) != {"artifact_dir", "files"} or index_doc["artifact_dir"] != ".":
        raise ValueError("artifact index fields differ")
    if not isinstance(index_doc["files"], list):
        raise ValueError("artifact index files must be a list")
    indexed: dict[str, dict[str, object]] = {}
    for item in index_doc["files"]:
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "size_bytes"}:
            raise ValueError("invalid artifact index entry")
        relative = item["path"]
        candidate = Path(relative) if isinstance(relative, str) else Path()
        if (
            not isinstance(relative, str)
            or candidate.is_absolute()
            or ".." in candidate.parts
            or relative in indexed
            or not re.fullmatch(r"[0-9a-f]{64}", str(item["sha256"]))
            or not isinstance(item["size_bytes"], int)
            or item["size_bytes"] < 0
        ):
            raise ValueError("invalid artifact index identity")
        indexed[relative] = item
    actual = {
        path.relative_to(run_dir).as_posix()
        for path in run_dir.rglob("*")
        if path.is_file()
        and path.relative_to(run_dir).as_posix()
        not in {"artifact-index.json", "completion-receipt.json"}
    }
    if actual != set(indexed):
        raise ValueError("artifact index file set differs from attempt")
    for relative, item in indexed.items():
        path = run_dir / relative
        if path.stat().st_size != item["size_bytes"] or sha256(path) != item["sha256"]:
            raise ValueError(f"artifact index mismatch: {relative}")
    return indexed


def verify(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    validate_context(run_dir)
    indexed = verify_index(run_dir)
    status_path = run_dir / "execution-status.json"
    status = load_json(status_path, "execution status")
    terminal = status.get("attempt_status")
    if terminal == "COMPLETED":
        expected_status = {
            "attempt_status", "claim_state", "gate_decision", "kind", "recorded_at", "smoke"
        }
        if (
            set(status) != expected_status
            or status["claim_state"] != "roadmap"
            or status["gate_decision"] != "N/A"
            or status["kind"] != "preformal_runtime_validation"
            or not isinstance(status["recorded_at"], str)
        ):
            raise ValueError("successful status exceeds the preformal contract")
        smoke = read_smoke(run_dir / "smoke.log")
        if status["smoke"] != smoke:
            raise ValueError("successful status smoke record differs")
        receipt_path = run_dir / "completion-receipt.json"
        receipt = load_json(receipt_path, "completion receipt")
        expected_receipt = {
            "artifact_index_sha256", "claim_state", "execution_status_sha256",
            "gate_decision", "sealed_at", "status",
        }
        if (
            set(receipt) != expected_receipt
            or receipt["claim_state"] != "roadmap"
            or receipt["gate_decision"] != "N/A"
            or receipt["status"] != "PREFORMAL_RUNTIME_ADMISSION_COMPLETE"
            or receipt["artifact_index_sha256"] != sha256(run_dir / "artifact-index.json")
            or receipt["execution_status_sha256"] != sha256(status_path)
            or not isinstance(receipt["sealed_at"], str)
        ):
            raise ValueError("completion receipt does not bind the terminal")
    elif terminal in {"BLOCKED_BEFORE_RUNTIME", "RUNTIME_FAILED"}:
        expected_status = {
            "attempt_status", "claim_state", "exit_code", "gate_decision", "phase", "recorded_at"
        }
        if (
            set(status) != expected_status
            or status["claim_state"] != "roadmap"
            or status["gate_decision"] != "N/A"
            or not isinstance(status["exit_code"], int)
            or not isinstance(status["phase"], str)
            or not isinstance(status["recorded_at"], str)
            or (run_dir / "completion-receipt.json").exists()
        ):
            raise ValueError("failure status exceeds the preformal contract")
    else:
        raise ValueError("unknown terminal status")
    if "execution-status.json" not in indexed:
        raise ValueError("artifact index omits execution status")
    print(f"VERIFIED_PREFLIGHT_TERMINAL: {run_dir}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    render_parser = commands.add_parser("render")
    render_parser.add_argument("--template", required=True, type=Path)
    render_parser.add_argument("--repo-root", required=True, type=Path)
    render_parser.add_argument("--output", required=True, type=Path)
    render_parser.set_defaults(handler=render)
    finish_parser = commands.add_parser("finish")
    finish_parser.add_argument("--run-dir", required=True, type=Path)
    finish_parser.set_defaults(handler=finish)
    fail_parser = commands.add_parser("fail")
    fail_parser.add_argument("--run-dir", required=True, type=Path)
    fail_parser.add_argument("--status", required=True)
    fail_parser.add_argument("--phase", required=True)
    fail_parser.add_argument("--exit-code", required=True, type=int)
    fail_parser.set_defaults(handler=fail)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--run-dir", required=True, type=Path)
    verify_parser.set_defaults(handler=verify)
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
