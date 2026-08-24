#!/usr/bin/env python3
"""Seal one CUDA12-COMPAT-001 no-action compatibility attempt."""

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


BUNDLE_ID = "CUDA12-COMPAT-001"
KIND = "preformal_cuda12_compatibility_probe"
SPEC_PATH = "experiments/g1/SPEC.cuda12-compat-001.md"
INPUT_GATE_DECISION = "N/A: CUDA 12 compatibility probe only"
TERMINAL_SUCCESS = "COMPATIBLE_FOR_RESTRICTED_STARTUP_ONLY"
FAILURE_TERMINALS = {
    "BLOCKED_HOST_IDENTITY",
    "BLOCKED_DEPENDENCY_TRANSPORT",
    "BLOCKED_DEPENDENCY_RESOLUTION",
    "RUNTIME_INCOMPATIBLE",
    "TOOLKIT_COMPILER_FAILED",
    "SGLANG_STARTUP_JIT_FAILED",
    "SGLANG_STARTUP_FAILED_OTHER",
    "INVALID_SCOPE",
}
EXPECTED_TERMINALS = [
    "BLOCKED_HOST_IDENTITY",
    "BLOCKED_DEPENDENCY_TRANSPORT",
    "BLOCKED_DEPENDENCY_RESOLUTION",
    "RUNTIME_INCOMPATIBLE",
    "TOOLKIT_COMPILER_FAILED",
    "SGLANG_STARTUP_JIT_FAILED",
    "SGLANG_STARTUP_FAILED_OTHER",
    "INVALID_SCOPE",
    TERMINAL_SUCCESS,
]
TERMINALS = {"artifact-index.json", "completion-receipt.json", "execution-status.json"}
SUCCESS_ARTIFACTS = (
    "attempt-context.json",
    "environment.txt",
    "source-seed.txt",
    "input-manifest-verify.log",
    "input-manifest.json",
    "input-oss-receipt.json",
    "bootstrap-receipt.json",
    "runtime-wheel.whl",
    "runtime-wheel-provenance.json",
    "runtime-wheel-validation.json",
    "cuda-wheelhouse-index.json",
    "cuda-wheelhouse-validation.json",
    "toolgap-seed-verify.log",
    "source-restore.log",
    "model-seed-prepare.log",
    "model-snapshot.json",
    "resolver-install.log",
    "cu13-distributions-before-removal.txt",
    "cu13-distributions-after-removal.txt",
    "dependency-lock.txt",
    "installed-distributions.json",
    "runtime-install-report.json",
    "cuda-wheelhouse-install-report.json",
    "ordinary-dependency-requirements.txt",
    "flashinfer-exception-install-report.json",
    "omitted-dependency-exception.json",
    "ordinary-dependency-report.json",
    "torch-cuda-probe.log",
    "cuda-sm86.cu",
    "cuda-sm86-build.log",
    "cuda-sm86-output.log",
    "sglang-provenance.json",
    "test-module-provenance.json",
    "runtime.env",
    "manifest.json",
    "manifest.sha256",
    "restricted-startup-command.txt",
    "restricted-startup.log",
    "startup.pid",
    "startup.pgid",
    "startup-gpu-pids-before.txt",
    "startup-gpu-pids-during.txt",
    "startup-gpu-pids-attributable.txt",
    "startup-gpu-pids-after.txt",
    "startup-gpu-pids-leaked.txt",
    "startup-process-group-after.txt",
    "startup-listeners-after.txt",
    "shutdown.log",
    "scope-scan.log",
)
RUNTIME_INPUTS = {
    "environment": "environment.txt",
    "input_manifest": "input-manifest.json",
    "input_manifest_verification": "input-manifest-verify.log",
    "input_oss_receipt": "input-oss-receipt.json",
    "bootstrap_receipt": "bootstrap-receipt.json",
    "runtime_wheel": "runtime-wheel.whl",
    "runtime_wheel_provenance": "runtime-wheel-provenance.json",
    "runtime_wheel_validation": "runtime-wheel-validation.json",
    "cuda_wheelhouse_index": "cuda-wheelhouse-index.json",
    "cuda_wheelhouse_validation": "cuda-wheelhouse-validation.json",
    "model_snapshot": "model-snapshot.json",
    "resolved_dependencies": "dependency-lock.txt",
    "installed_distributions": "installed-distributions.json",
    "resolver_report": "runtime-install-report.json",
    "cuda_wheelhouse_install_report": "cuda-wheelhouse-install-report.json",
    "ordinary_dependency_report": "ordinary-dependency-report.json",
    "flashinfer_exception_install_report": "flashinfer-exception-install-report.json",
    "omitted_dependency_exception": "omitted-dependency-exception.json",
    "cuda13_cleanup_before": "cu13-distributions-before-removal.txt",
    "cuda13_cleanup_after": "cu13-distributions-after-removal.txt",
    "torch_cuda_probe": "torch-cuda-probe.log",
    "cuda_sm86_output": "cuda-sm86-output.log",
    "provenance": "sglang-provenance.json",
    "runtime_env": "runtime.env",
    "test_module_provenance": "test-module-provenance.json",
}
ARCHIVE_NAMES = {
    "cuda_wheelhouse", "model_snapshot", "runtime_wheel",
    "runtime_wheel_provenance", "sglang_source_seed", "toolgap_source_seed",
}


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
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def relative(path: Path, root: Path, label: str) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"{label} escapes the attempt directory") from error


def validate_context(run_dir: Path) -> dict[str, object]:
    context = load_json(run_dir / "attempt-context.json", "attempt context")
    expected_fields = {
        "attempt_id", "bundle_id", "claim_state", "created_at", "gate",
        "gate_decision", "spec_path", "spec_sha256", "toolgap_commit",
        "toolgap_tracked_clean", "toolgap_tree",
    }
    if set(context) != expected_fields:
        raise ValueError("attempt context fields differ")
    if (
        context["bundle_id"] != BUNDLE_ID
        or context["claim_state"] != "roadmap"
        or context["gate"] != "G1"
        or context["gate_decision"] != "N/A"
        or context["spec_path"] != SPEC_PATH
        or context["toolgap_tracked_clean"] is not True
    ):
        raise ValueError("attempt context exceeds the compatibility contract")
    if not isinstance(context["attempt_id"], str) or not re.fullmatch(
        r"[A-Za-z0-9._-]+", context["attempt_id"]
    ):
        raise ValueError("invalid attempt ID")
    for field, length in (("spec_sha256", 64), ("toolgap_commit", 40), ("toolgap_tree", 40)):
        if not isinstance(context[field], str) or not re.fullmatch(rf"[0-9a-f]{{{length}}}", context[field]):
            raise ValueError(f"invalid {field}")
    return context


def validate_input_manifest(
    run_dir: Path, context: dict[str, object]
) -> tuple[dict[str, object], dict[str, object]]:
    document = load_json(run_dir / "input-manifest.json", "input manifest")
    if set(document) != {"archives", "identity", "model", "schema_version", "static_inputs"}:
        raise ValueError("input manifest fields differ")
    identity = document["identity"]
    if not isinstance(identity, dict) or identity != {
        "bundle_id": BUNDLE_ID,
        "claim_state": "roadmap",
        "gate": "G1",
        "gate_decision": INPUT_GATE_DECISION,
        "toolgap_commit": context["toolgap_commit"],
        "toolgap_remote": identity.get("toolgap_remote"),
        "toolgap_tree": context["toolgap_tree"],
    } or not isinstance(identity["toolgap_remote"], str):
        raise ValueError("input manifest identity differs")
    if document["schema_version"] != 1:
        raise ValueError("input manifest schema differs")
    archives = document["archives"]
    if not isinstance(archives, dict) or set(archives) != ARCHIVE_NAMES:
        raise ValueError("input manifest archive set differs")
    for name, archive in archives.items():
        if (
            not isinstance(archive, dict)
            or set(archive) != {"path", "sha256", "size_bytes"}
            or not isinstance(archive["path"], str)
            or Path(archive["path"]).name != archive["path"]
            or not re.fullmatch(r"[0-9a-f]{64}", str(archive["sha256"]))
            or not isinstance(archive["size_bytes"], int)
            or archive["size_bytes"] < 1
        ):
            raise ValueError(f"invalid input manifest archive: {name}")
    static_inputs = document["static_inputs"]
    required_static_inputs = {
        "experiments/g1/commands/00-cuda12-compat-001-bootstrap.sh",
        "experiments/g1/commands/19-cuda12-compat-001-project-prereqs.sh",
    }
    if not isinstance(static_inputs, dict) or not required_static_inputs <= set(static_inputs):
        raise ValueError("input manifest static bindings differ")
    for path in required_static_inputs:
        binding = static_inputs[path]
        if (
            not isinstance(binding, dict)
            or set(binding) != {"sha256", "size_bytes"}
            or not isinstance(binding["sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", binding["sha256"])
            or not isinstance(binding["size_bytes"], int)
            or binding["size_bytes"] < 1
        ):
            raise ValueError(f"invalid input manifest static binding: {path}")
    return document, identity


def validate_input_oss_receipt(run_dir: Path, input_manifest: dict[str, object]) -> None:
    receipt = load_json(run_dir / "input-oss-receipt.json", "input OSS receipt")
    if set(receipt) != {"schema_version", "identity", "objects"}:
        raise ValueError("input OSS receipt fields differ")
    if receipt["schema_version"] != 1 or receipt["identity"] != input_manifest["identity"]:
        raise ValueError("input OSS receipt identity differs")
    objects = receipt["objects"]
    archives = input_manifest["archives"]
    static_inputs = input_manifest["static_inputs"]
    expected = {
        "input_manifest": {
            "sha256": sha256(run_dir / "input-manifest.json"),
            "size_bytes": (run_dir / "input-manifest.json").stat().st_size,
        },
        **{
            label: {"sha256": archive["sha256"], "size_bytes": archive["size_bytes"]}
            for label, archive in archives.items()
        },
        "bootstrap": static_inputs["experiments/g1/commands/00-cuda12-compat-001-bootstrap.sh"],
        "prereqs": static_inputs["experiments/g1/commands/19-cuda12-compat-001-project-prereqs.sh"],
    }
    if not isinstance(objects, dict) or set(objects) != set(expected):
        raise ValueError("input OSS receipt object set differs")
    prefixes: set[str] = set()
    for label, expected_binding in expected.items():
        object_record = objects[label]
        if not isinstance(object_record, dict) or set(object_record) != {
            "object_uri", "sha256", "size_bytes", "version_id"
        }:
            raise ValueError(f"invalid input OSS receipt object: {label}")
        uri = object_record["object_uri"]
        version = object_record["version_id"]
        expected_name = "input-manifest.json" if label == "input_manifest" else (
            archives[label]["path"] if label in archives else (
                "00-cuda12-compat-001-bootstrap.sh" if label == "bootstrap"
                else "19-cuda12-compat-001-project-prereqs.sh"
            )
        )
        if (
            not isinstance(uri, str)
            or not re.fullmatch(r"oss://[^/]+/.+", uri)
            or uri.rsplit("/", 1)[1] != expected_name
            or not isinstance(version, str)
            or not version
            or object_record["sha256"] != expected_binding["sha256"]
            or object_record["size_bytes"] != expected_binding["size_bytes"]
        ):
            raise ValueError(f"input OSS receipt binding differs: {label}")
        prefixes.add(uri.rsplit("/", 1)[0])
    if len(prefixes) != 1:
        raise ValueError("input OSS receipt objects do not share a prefix")


def read_startup(path: Path) -> dict[str, object]:
    records = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and value.get("kind") == "G1_PREFLIGHT_SERVER_STARTED":
            records.append(value)
    if len(records) != 1:
        raise ValueError("restricted startup log must contain exactly one startup record")
    record = records[0]
    if record.get("skip_server_warmup") is not True:
        raise ValueError("restricted startup did not disable generation warmup")
    if not isinstance(record.get("base_url"), str) or not re.fullmatch(
        r"http://127\.0\.0\.1:[1-9][0-9]{0,4}", record["base_url"]
    ):
        raise ValueError("restricted startup did not identify a loopback listener")
    return record


def validate_template(template: dict[str, object]) -> None:
    identity = template.get("identity")
    expected_identity = {
        "attempt_id": "__GENERATED__",
        "bundle_id": BUNDLE_ID,
        "claim_state": "roadmap",
        "gate": "G1",
        "gate_decision": "N/A",
        "kind": KIND,
        "spec_path": SPEC_PATH,
        "spec_sha256": "__GENERATED__",
        "toolgap_commit": "__GENERATED__",
        "toolgap_tree": "__GENERATED__",
    }
    if identity != expected_identity:
        raise ValueError("manifest template identity differs")
    if template.get("outcome") != {
        "claim_state": "roadmap",
        "gate_decision": "N/A: CUDA 12 compatibility probe only",
    }:
        raise ValueError("manifest template outcome exceeds compatibility scope")
    if template.get("planned_success_artifacts") != list(SUCCESS_ARTIFACTS):
        raise ValueError("manifest template success artifact set differs")
    if template.get("terminals") != EXPECTED_TERMINALS:
        raise ValueError("manifest template terminal set differs")


def validate_manifest_binding(run_dir: Path, context: dict[str, object]) -> dict[str, object]:
    manifest = load_json(run_dir / "manifest.json", "manifest")
    input_manifest, input_identity = validate_input_manifest(run_dir, context)
    validate_input_oss_receipt(run_dir, input_manifest)
    expected_identity = {
        "attempt_id": context["attempt_id"],
        "bundle_id": BUNDLE_ID,
        "claim_state": "roadmap",
        "gate": "G1",
        "gate_decision": "N/A",
        "kind": KIND,
        "spec_path": SPEC_PATH,
        "spec_sha256": context["spec_sha256"],
        "toolgap_commit": context["toolgap_commit"],
        "toolgap_tree": context["toolgap_tree"],
    }
    if manifest.get("identity") != expected_identity:
        raise ValueError("manifest identity differs from attempt context")
    if manifest.get("outcome") != {
        "claim_state": "roadmap",
        "gate_decision": "N/A: CUDA 12 compatibility probe only",
    }:
        raise ValueError("manifest outcome exceeds compatibility scope")
    if manifest.get("planned_success_artifacts") != list(SUCCESS_ARTIFACTS):
        raise ValueError("manifest success artifact set differs")
    runtime_inputs = manifest.get("runtime_inputs")
    if not isinstance(runtime_inputs, dict) or set(runtime_inputs) != set(RUNTIME_INPUTS):
        raise ValueError("manifest runtime input set differs")
    for label, filename in RUNTIME_INPUTS.items():
        path = run_dir / filename
        if runtime_inputs[label] != {"path": filename, "sha256": sha256(path)}:
            raise ValueError(f"manifest runtime input differs: {label}")
    if manifest.get("offline_archives") != input_manifest["archives"]:
        raise ValueError("manifest offline archives differ from input manifest")
    receipt = load_json(run_dir / "bootstrap-receipt.json", "bootstrap receipt")
    expected_receipt = {
        "input_manifest_path", "input_manifest_sha256", "toolgap_checkout",
        "toolgap_commit", "toolgap_remote", "toolgap_seed_path",
        "toolgap_seed_sha256", "toolgap_tree",
    }
    if set(receipt) != expected_receipt:
        raise ValueError("bootstrap receipt fields differ")
    if (
        receipt["input_manifest_sha256"] != sha256(run_dir / "input-manifest.json")
        or receipt["toolgap_seed_sha256"] != input_manifest["archives"]["toolgap_source_seed"]["sha256"]
        or receipt["toolgap_commit"] != input_identity["toolgap_commit"]
        or receipt["toolgap_tree"] != input_identity["toolgap_tree"]
        or receipt["toolgap_remote"] != input_identity["toolgap_remote"]
        or any(
            not isinstance(receipt[field], str) or not Path(receipt[field]).is_absolute()
            for field in ("input_manifest_path", "toolgap_checkout", "toolgap_seed_path")
        )
    ):
        raise ValueError("bootstrap receipt differs from input manifest")
    runtime_wheel = input_manifest["archives"]["runtime_wheel"]
    runtime_provenance = input_manifest["archives"]["runtime_wheel_provenance"]
    wheel_path = run_dir / "runtime-wheel.whl"
    provenance_path = run_dir / "runtime-wheel-provenance.json"
    if (
        wheel_path.stat().st_size != runtime_wheel["size_bytes"]
        or sha256(wheel_path) != runtime_wheel["sha256"]
        or provenance_path.stat().st_size != runtime_provenance["size_bytes"]
        or sha256(provenance_path) != runtime_provenance["sha256"]
    ):
        raise ValueError("staged runtime wheel inputs differ from input manifest")
    wheel_validation = load_json(run_dir / "runtime-wheel-validation.json", "runtime wheel validation")
    if wheel_validation != {
        "metadata_path": wheel_validation.get("metadata_path"),
        "metadata_sha256": wheel_validation.get("metadata_sha256"),
        "runtime_wheel_sha256": runtime_wheel["sha256"],
        "runtime_wheel_size_bytes": runtime_wheel["size_bytes"],
        "source_rebuild": False,
        "provenance_identity": "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite",
    } or not isinstance(wheel_validation["metadata_path"], str) or not re.fullmatch(
        r"[0-9a-f]{64}", str(wheel_validation["metadata_sha256"])
    ):
        raise ValueError("runtime wheel validation differs from the sealed input")
    wheelhouse = input_manifest["archives"]["cuda_wheelhouse"]
    wheelhouse_validation = load_json(run_dir / "cuda-wheelhouse-validation.json", "CUDA wheelhouse validation")
    wheelhouse_index = run_dir / "cuda-wheelhouse-index.json"
    wheelhouse_index_document = load_json(wheelhouse_index, "CUDA wheelhouse index")
    if (
        wheelhouse_validation.get("archive_sha256") != wheelhouse["sha256"]
        or wheelhouse_validation.get("archive_size_bytes") != wheelhouse["size_bytes"]
        or not isinstance(wheelhouse_validation.get("archive_path"), str)
        or not Path(wheelhouse_validation["archive_path"]).is_absolute()
        or wheelhouse_validation.get("wheels") != wheelhouse_index_document.get("wheels")
        or wheelhouse_validation.get("index_sha256") != sha256(wheelhouse_index)
    ):
        raise ValueError("CUDA wheelhouse validation differs from input manifest")
    checksum = (run_dir / "manifest.sha256").read_text(encoding="utf-8").split()
    if not checksum or checksum[0] != sha256(run_dir / "manifest.json"):
        raise ValueError("manifest checksum differs")
    return manifest


def read_installed_distributions(run_dir: Path) -> dict[str, str]:
    path = run_dir / "installed-distributions.json"
    try:
        inventory = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("installed distribution inventory is not valid JSON") from error
    if not isinstance(inventory, list):
        raise ValueError("installed distribution inventory is not a list")
    distributions: dict[str, str] = {}
    for entry in inventory:
        if not isinstance(entry, dict) or set(entry) != {"name", "version"}:
            raise ValueError("installed distribution inventory entry differs")
        name = entry["name"]
        version = entry["version"]
        if not isinstance(name, str) or not isinstance(version, str) or not name or not version:
            raise ValueError("installed distribution inventory entry is invalid")
        canonical = re.sub(r"[-_.]+", "-", name).lower()
        if canonical in distributions:
            raise ValueError("installed distribution inventory has duplicate normalized names")
        distributions[canonical] = version
    return distributions


def validate_omitted_dependency_exception(run_dir: Path) -> None:
    exception = load_json(
        run_dir / "omitted-dependency-exception.json", "omitted dependency exception"
    )
    if exception != {
        "allowed_uninstalled_requirement": "cuda-tile==1.6.0rc5",
        "installed_without_dependency_resolution": "flashinfer_python[cu12]==0.6.17",
        "reason": "G0-C-011 built this CUDA 13.1+-only source distribution; CUDA12-COMPAT-001 must not source-build on ECS",
        "success_scope": "restricted startup only; no claim that cuda-tile-dependent execution is compatible",
    }:
        raise ValueError("omitted dependency exception differs from the compatibility scope")
    distributions = read_installed_distributions(run_dir)
    if "cuda-tile" in distributions:
        raise ValueError("installed inventory unexpectedly contains cuda-tile")
    if distributions.get("flashinfer-python") != "0.6.17":
        raise ValueError("installed inventory omits the fixed FlashInfer exception wheel")


def validate_cuda13_absence(run_dir: Path) -> None:
    cuda13 = (run_dir / "cu13-distributions-after-removal.txt").read_text(encoding="utf-8")
    if cuda13:
        raise ValueError("successful attempt retains CUDA13 distributions")
    for canonical, version in read_installed_distributions(run_dir).items():
        if canonical.endswith("-cu13") or (
            canonical in {
                "nvidia-cuda-runtime",
                "nvidia-cuda-cccl",
                "nvidia-cuda-nvcc",
                "nvidia-cuda-nvrtc",
            }
            and re.fullmatch(r"13(?:[.].*)?", version)
        ):
            raise ValueError(f"successful installed inventory retains CUDA13 distribution: {canonical}=={version}")


def render(args: argparse.Namespace) -> int:
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"refusing to replace manifest: {output}")
    repo = args.repo_root.resolve()
    if git(repo, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("ToolGap tracked files must be clean")
    run_dir = output.parent
    context = validate_context(run_dir)
    template = load_json(args.template.resolve(), "manifest template")
    validate_template(template)
    inputs = {label: run_dir / filename for label, filename in RUNTIME_INPUTS.items()}
    for label, path in inputs.items():
        if not path.is_file():
            raise ValueError(f"missing manifest input {label}: {path}")
    input_manifest, _ = validate_input_manifest(run_dir, context)
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
    template["offline_archives"] = input_manifest["archives"]
    template["rendered_at"] = now()
    write_json_exclusive(output, template)
    return 0


def index(run_dir: Path) -> Path:
    output = run_dir / "artifact-index.json"
    if output.exists():
        raise ValueError("refusing to replace artifact index")
    files = []
    for path in sorted(run_dir.rglob("*")):
        item = path.relative_to(run_dir).as_posix()
        if path.is_file() and item not in {"artifact-index.json", "completion-receipt.json"}:
            files.append({"path": item, "sha256": sha256(path), "size_bytes": path.stat().st_size})
    write_json_exclusive(output, {"artifact_dir": ".", "files": files})
    return output


def seal_terminal(run_dir: Path, status: dict[str, object]) -> None:
    write_json_exclusive(run_dir / "execution-status.json", status)
    artifact_index = index(run_dir)
    write_json_exclusive(
        run_dir / "completion-receipt.json",
        {
            "artifact_index_sha256": sha256(artifact_index),
            "claim_state": "roadmap",
            "execution_status_sha256": sha256(run_dir / "execution-status.json"),
            "gate_decision": "N/A",
            "status": "CUDA12_COMPAT_TERMINAL_SEALED",
        },
    )


def finish(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    if any((run_dir / name).exists() for name in TERMINALS):
        raise ValueError("attempt already has a terminal artifact")
    context = validate_context(run_dir)
    for name in SUCCESS_ARTIFACTS:
        if not (run_dir / name).is_file():
            raise ValueError(f"missing successful-attempt artifact: {name}")
    manifest = validate_manifest_binding(run_dir, context)
    validate_omitted_dependency_exception(run_dir)
    validate_cuda13_absence(run_dir)
    if manifest["identity"]["attempt_id"] != context["attempt_id"]:
        raise ValueError("manifest attempt identity differs")
    startup = read_startup(run_dir / "restricted-startup.log")
    shutdown = (run_dir / "shutdown.log").read_text(encoding="utf-8", errors="replace")
    if "cleanup=true\n" not in shutdown or "startup_exit_status=0\n" not in shutdown:
        raise ValueError("restricted startup did not prove clean teardown")
    scope = (run_dir / "scope-scan.log").read_text(encoding="utf-8", errors="replace")
    if "scope=clean\n" not in scope:
        raise ValueError("runtime scope scanner did not prove clean scope")
    seal_terminal(
        run_dir,
        {
            "attempt_status": TERMINAL_SUCCESS,
            "claim_state": "roadmap",
            "gate_decision": "N/A",
            "kind": KIND,
            "recorded_at": now(),
            "startup": startup,
        },
    )
    return 0


FAILURE_PHASES = {
    "BLOCKED_HOST_IDENTITY": {"host_identity", "inputs", "restore"},
    "BLOCKED_DEPENDENCY_TRANSPORT": {"resolver"},
    "BLOCKED_DEPENDENCY_RESOLUTION": {"resolver"},
    "RUNTIME_INCOMPATIBLE": {"torch_cuda"},
    "TOOLKIT_COMPILER_FAILED": {"compiler"},
    "SGLANG_STARTUP_JIT_FAILED": {"startup"},
    "SGLANG_STARTUP_FAILED_OTHER": {"startup"},
    "INVALID_SCOPE": {"scope"},
}
TRANSPORT_FAILURE_PATTERN = re.compile(
    r"(connection (reset|refused|timed out)|connecttimeout|readtimeout|httpsconnectionpool|proxyerror|sslerror|temporary failure|name or service not known|network is unreachable|failed to establish a new connection|could not fetch url|http error [45][0-9]{2}|[45][0-9]{2} (client|server) error|timed out|timeout)",
    re.IGNORECASE,
)
STARTUP_JIT_FAILURE_PATTERN = re.compile(
    r"(^|[^a-z])(nvrtc|nvcc)([^a-z]|$)|"
    r"cuda[^a-z]*(compile|compiler)|FileNotFoundError:.*ninja",
    re.IGNORECASE,
)


def startup_log_has_jit_failure(text: str) -> bool:
    last_traceback = text.rfind("Traceback (most recent call last):")
    failure = text[last_traceback:] if last_traceback >= 0 else text
    return bool(STARTUP_JIT_FAILURE_PATTERN.search(failure))


def validate_failure_evidence(run_dir: Path, status: dict[str, object]) -> None:
    terminal = status["attempt_status"]
    phase = status["phase"]
    exit_code = status["exit_code"]
    if phase not in FAILURE_PHASES[terminal] or exit_code == 0:
        raise ValueError("failure terminal phase or exit code differs from the runner contract")
    required_logs = {
        "resolver": "resolver-install.log",
        "torch_cuda": "torch-cuda-probe.log",
        "compiler": "cuda-sm86-build.log",
        "startup": "restricted-startup.log",
        "scope": "scope-scan.log",
    }
    required_log = required_logs.get(phase)
    if required_log and not (run_dir / required_log).is_file():
        raise ValueError(f"failure terminal omits {required_log}")
    if phase == "resolver":
        resolver_log = (run_dir / "resolver-install.log").read_text(
            encoding="utf-8", errors="replace"
        )
        has_transport_failure = bool(TRANSPORT_FAILURE_PATTERN.search(resolver_log))
        if terminal == "BLOCKED_DEPENDENCY_TRANSPORT" and not has_transport_failure:
            raise ValueError("dependency transport terminal lacks affirmative transport evidence")
        if terminal == "BLOCKED_DEPENDENCY_RESOLUTION" and has_transport_failure:
            raise ValueError("dependency resolution terminal contains transport-failure evidence")
    if phase == "startup":
        startup_log = (run_dir / "restricted-startup.log").read_text(
            encoding="utf-8", errors="replace"
        )
        has_jit_evidence = startup_log_has_jit_failure(startup_log)
        if terminal == "SGLANG_STARTUP_JIT_FAILED" and not has_jit_evidence:
            raise ValueError("startup JIT terminal lacks JIT/compiler evidence")
        if terminal == "SGLANG_STARTUP_FAILED_OTHER" and has_jit_evidence:
            raise ValueError("other startup terminal contains JIT/compiler evidence")
    if phase == "scope":
        scope_log = (run_dir / "scope-scan.log").read_text(
            encoding="utf-8", errors="replace"
        )
        if "scope=invalid\n" not in scope_log:
            raise ValueError("invalid-scope terminal lacks scope=invalid evidence")


def fail(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    if any((run_dir / name).exists() for name in TERMINALS):
        raise ValueError("attempt already has a terminal artifact")
    validate_context(run_dir)
    if not (run_dir / "environment.txt").is_file():
        raise ValueError("failure terminal requires best-effort environment evidence")
    if args.status not in FAILURE_TERMINALS:
        raise ValueError("unsupported compatibility failure status")
    status = {
        "attempt_status": args.status,
        "claim_state": "roadmap",
        "exit_code": args.exit_code,
        "gate_decision": "N/A",
        "phase": args.phase,
        "recorded_at": now(),
    }
    validate_failure_evidence(run_dir, status)
    seal_terminal(run_dir, status)
    verify(argparse.Namespace(run_dir=run_dir))
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
        relative_path = item["path"]
        candidate = Path(relative_path) if isinstance(relative_path, str) else Path()
        if (
            not isinstance(relative_path, str)
            or candidate.is_absolute()
            or ".." in candidate.parts
            or relative_path in indexed
            or not re.fullmatch(r"[0-9a-f]{64}", str(item["sha256"]))
            or not isinstance(item["size_bytes"], int)
            or item["size_bytes"] < 0
        ):
            raise ValueError("invalid artifact index identity")
        indexed[relative_path] = item
    actual = {
        path.relative_to(run_dir).as_posix()
        for path in run_dir.rglob("*")
        if path.is_file() and path.relative_to(run_dir).as_posix() not in {"artifact-index.json", "completion-receipt.json"}
    }
    if actual != set(indexed):
        raise ValueError("artifact index file set differs from attempt")
    for relative_path, item in indexed.items():
        path = run_dir / relative_path
        if path.stat().st_size != item["size_bytes"] or sha256(path) != item["sha256"]:
            raise ValueError(f"artifact index mismatch: {relative_path}")
    return indexed


def verify(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    context = validate_context(run_dir)
    indexed = verify_index(run_dir)
    status_path = run_dir / "execution-status.json"
    status = load_json(status_path, "execution status")
    terminal = status.get("attempt_status")
    if terminal == TERMINAL_SUCCESS:
        expected_status = {"attempt_status", "claim_state", "gate_decision", "kind", "recorded_at", "startup"}
        if (
            set(status) != expected_status
            or status["claim_state"] != "roadmap"
            or status["gate_decision"] != "N/A"
            or status["kind"] != KIND
            or not isinstance(status["recorded_at"], str)
            or status["startup"] != read_startup(run_dir / "restricted-startup.log")
        ):
            raise ValueError("successful status exceeds compatibility scope")
        validate_manifest_binding(run_dir, context)
    elif terminal in FAILURE_TERMINALS:
        expected_status = {"attempt_status", "claim_state", "exit_code", "gate_decision", "phase", "recorded_at"}
        if (
            set(status) != expected_status
            or status["claim_state"] != "roadmap"
            or status["gate_decision"] != "N/A"
            or not isinstance(status["exit_code"], int)
            or not isinstance(status["phase"], str)
            or not isinstance(status["recorded_at"], str)
        ):
            raise ValueError("failure status exceeds compatibility scope")
        if not (run_dir / "environment.txt").is_file():
            raise ValueError("failure terminal omits best-effort environment evidence")
        validate_failure_evidence(run_dir, status)
    else:
        raise ValueError("unknown compatibility terminal status")
    receipt = load_json(run_dir / "completion-receipt.json", "completion receipt")
    if receipt != {
        "artifact_index_sha256": sha256(run_dir / "artifact-index.json"),
        "claim_state": "roadmap",
        "execution_status_sha256": sha256(status_path),
        "gate_decision": "N/A",
        "status": "CUDA12_COMPAT_TERMINAL_SEALED",
    }:
        raise ValueError("completion receipt does not bind terminal")
    if "execution-status.json" not in indexed:
        raise ValueError("artifact index omits execution status")
    print(f"VERIFIED_CUDA12_COMPAT_TERMINAL_INTERNAL: {run_dir}")
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
