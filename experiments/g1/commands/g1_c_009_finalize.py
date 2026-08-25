#!/usr/bin/env python3
"""Render, seal, and off-host verify one formal G1-C-009 attempt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

BUNDLE_ID = "G1-C-009"
KIND = "formal_checked_demote_runtime"
SPEC_PATH = "experiments/g1/SPEC.g1-c-009.md"
SCRIPTED_TEST_PATH = "test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py"
SELECTOR_MODULE = PurePosixPath(SCRIPTED_TEST_PATH).stem
ARMS = (
    "enabled",
    "bypass",
    "reject_write_through_pending",
    "reject_non_target_session_coverage",
    "reject_device_locked",
    "reject_stale_generation",
    "stock_eviction_liveness",
)
SELECTORS = {
    "enabled": "TestG1EnabledArm.test_enabled_checked_demotion_records_allocator_visible_release",
    "bypass": "TestG1BypassArm.test_bypass_releases_priority_without_physical_reclamation",
    "reject_write_through_pending": "TestG1WriteThroughPending.test_uncommitted_host_copy_is_deferred_without_physical_free",
    "reject_non_target_session_coverage": "TestG1NonTargetCoverage.test_shared_target_is_deferred_for_the_other_session",
    "reject_device_locked": "TestG1DeviceLocked.test_active_request_is_deferred_at_the_device_lock_check",
    "reject_stale_generation": "TestG1StaleGeneration.test_stale_generation_is_rejected_before_priority_release",
    "stock_eviction_liveness": "TestG1StockEvictionLiveness.test_stock_eviction_remains_reachable_after_bypass",
}
REJECTION_REASONS = {
    "reject_write_through_pending": "WRITE_THROUGH_PENDING",
    "reject_non_target_session_coverage": "NON_TARGET_SESSION_COVERAGE",
    "reject_device_locked": "DEVICE_LOCKED",
    "reject_stale_generation": "STALE_GENERATION",
}
RECORD_FIELDS = {
    "arm", "operation", "target", "component_qualification", "priority_release",
    "released_component_leaves", "facade", "nodes", "freed_device_ids",
    "route_counters", "capacity",
}
COUNTER_FIELDS = {
    "checked_facade", "checked_backend", "physical_demote", "cache_owned_drain",
    "stock_evict", "physical_demote_node_ids",
}
TARGET_FIELDS = {
    "requested_node_ids", "eligible_node_ids", "scheduled_node_ids",
    "completed_node_ids", "before", "after",
}
LIVE_OBSERVATION_FIELDS = {
    "node_id", "live", "device_ids", "host_committed",
    "write_through_pending", "load_back_pending", "lock_refs",
    "session_ref", "device_leaf",
}
MISSING_OBSERVATION_FIELDS = {"node_id", "live"}
RUNTIME_WHEEL_FILENAME = "sglang-0.0.0.dev2+g734a8e921-cp312-cp312-linux_x86_64.whl"
MINIMUM_FREE_BYTES = 24 * 1024 * 1024 * 1024
FAILURE_PHASES = (
    "bootstrap",
    "input_binding",
    "source_restore",
    "model",
    "resolver",
    "formal_arms",
    "scope",
    "render",
    "seal",
)
BASE_ARTIFACTS = (
    "attempt-context.json", "environment.txt", "input-manifest.json",
    "input-manifest-verify.log", "input-oss-receipt.json", "bootstrap-receipt.json",
    "storage-preflight-source-restore.json", "storage-preflight-resolver.json",
    "runtime-wheel-provenance.json", "runtime-wheel-validation.json",
    "cuda-wheelhouse-index.json", "cuda-wheelhouse-validation.json",
    "source-restore.log", "sglang-provenance.json", "model-seed-prepare.log",
    "model-snapshot.json", "resolver-install.log", "installed-distributions.json",
    "omitted-dependency-exception.json", "sglang-package-provenance.json",
    "runtime.env", "arm-plan.json", "arm-records.json", "cleanup.json",
    "scope-scan.log", "manifest.json", "manifest.sha256",
)
TERMINAL_ARTIFACTS = {"execution-status.json", "artifact-index.json", "completion-receipt.json"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid {label}: {path}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def write_exclusive(path: Path, document: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        output.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
    path.chmod(0o444)


def absolute_regular(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} must be a regular file")


def relative(path: Path, root: Path, label: str) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"{label} escapes attempt directory") from error


def valid_digest(value: object, length: int = 64) -> bool:
    return isinstance(value, str) and re.fullmatch(rf"[0-9a-f]{{{length}}}", value) is not None


def validate_context(run_dir: Path) -> dict[str, object]:
    context = load_json(run_dir / "attempt-context.json", "attempt context")
    required = {
        "attempt_id", "bundle_id", "claim_state", "created_at", "gate",
        "kind", "spec_path", "spec_sha256", "toolgap_commit",
        "toolgap_tracked_clean", "toolgap_tree", "work_root",
    }
    if set(context) != required:
        raise ValueError("attempt context fields differ")
    if (
        context["bundle_id"] != BUNDLE_ID or context["claim_state"] != "roadmap"
        or context["gate"] != "G1" or context["kind"] != KIND
        or context["spec_path"] != SPEC_PATH or context["toolgap_tracked_clean"] is not True
    ):
        raise ValueError("attempt context identity differs")
    if not isinstance(context["attempt_id"], str) or not re.fullmatch(r"[A-Za-z0-9._-]+", context["attempt_id"]):
        raise ValueError("attempt ID is invalid")
    for field, length in (("spec_sha256", 64), ("toolgap_commit", 40), ("toolgap_tree", 40)):
        if not valid_digest(context[field], length):
            raise ValueError(f"attempt context {field} is invalid")
    work_root = context["work_root"]
    if (
        not isinstance(work_root, str)
        or not Path(work_root).is_absolute()
        or str(Path(work_root)) != work_root
        or ".." in Path(work_root).parts
    ):
        raise ValueError("attempt context work root is invalid")
    return context


def validate_input_manifest(run_dir: Path, context: dict[str, object]) -> dict[str, object]:
    document = load_json(run_dir / "input-manifest.json", "input manifest")
    required = {
        "archives", "identity", "model", "ordinary_dependency_transport",
        "patches", "schema_version", "static_inputs", "storage_preflight",
    }
    if set(document) != required or type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise ValueError("input manifest schema differs")
    identity = document["identity"]
    expected = {
        "bundle_id": BUNDLE_ID, "claim_state": "roadmap", "gate": "G1",
        "kind": KIND, "toolgap_commit": context["toolgap_commit"],
        "toolgap_tree": context["toolgap_tree"],
        "sglang_base_commit": "92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2",
        "sglang_base_tree": "25e9bf86d04c27fe380024d9c8c421c3b5b51f3c",
    }
    if not isinstance(identity, dict) or any(identity.get(key) != value for key, value in expected.items()):
        raise ValueError("input manifest identity differs")
    if not isinstance(identity.get("toolgap_remote"), str):
        raise ValueError("input manifest ToolGap remote differs")
    archives = document["archives"]
    expected_archives = {
        "cuda_wheelhouse", "model_snapshot", "runtime_wheel",
        "runtime_wheel_provenance", "sglang_source_seed", "toolgap_source_seed",
    }
    if not isinstance(archives, dict) or set(archives) != expected_archives:
        raise ValueError("input manifest archive set differs")
    for label, entry in archives.items():
        if (
            not isinstance(entry, dict) or set(entry) != {"path", "sha256", "size_bytes"}
            or not isinstance(entry.get("path"), str) or Path(entry["path"]).name != entry["path"]
            or not valid_digest(entry.get("sha256"))
            or type(entry.get("size_bytes")) is not int or entry["size_bytes"] < 1
        ):
            raise ValueError(f"invalid input archive: {label}")
    if document["ordinary_dependency_transport"] != {
        "index_url": "http://mirrors.cloud.aliyuncs.com/pypi/simple/",
        "trusted_host": "mirrors.cloud.aliyuncs.com",
    }:
        raise ValueError("ordinary dependency transport differs")
    if document["storage_preflight"] != {"minimum_free_bytes": MINIMUM_FREE_BYTES}:
        raise ValueError("storage preflight manifest differs")
    return document


def validate_input_oss_receipt(run_dir: Path, manifest: dict[str, object]) -> None:
    receipt = load_json(run_dir / "input-oss-receipt.json", "input OSS receipt")
    if set(receipt) != {"schema_version", "identity", "objects"} or type(receipt["schema_version"]) is not int or receipt["schema_version"] != 1:
        raise ValueError("input OSS receipt schema differs")
    if receipt["identity"] != manifest["identity"]:
        raise ValueError("input OSS receipt identity differs")
    objects = receipt["objects"]
    archives = manifest["archives"]
    expected = set(archives) | {"bootstrap_script"}
    if not isinstance(objects, dict) or set(objects) != expected:
        raise ValueError("input OSS receipt object set differs")
    bootstrap = manifest["static_inputs"].get("experiments/g1/commands/00-g1-c-009-bootstrap.sh")
    if not isinstance(bootstrap, dict):
        raise ValueError("input manifest omits bootstrap binding")
    bindings = {**archives, "bootstrap_script": {"path": "00-g1-c-009-bootstrap.sh", **bootstrap}}
    for label, expected_binding in bindings.items():
        observed = objects[label]
        if (
            not isinstance(observed, dict) or set(observed) != {"object_uri", "sha256", "size_bytes", "version_id"}
            or not isinstance(observed.get("object_uri"), str)
            or not re.fullmatch(r"oss://[^/]+/.+", observed["object_uri"])
            or Path(observed["object_uri"]).name != expected_binding["path"]
            or observed.get("sha256") != expected_binding["sha256"]
            or type(observed.get("size_bytes")) is not int
            or observed.get("size_bytes") != expected_binding["size_bytes"]
            or not isinstance(observed.get("version_id"), str) or not observed["version_id"]
        ):
            raise ValueError(f"input OSS receipt binding differs: {label}")


def validate_bootstrap(run_dir: Path, manifest: dict[str, object]) -> None:
    receipt = load_json(run_dir / "bootstrap-receipt.json", "bootstrap receipt")
    if set(receipt) != {
        "input_manifest_path", "input_manifest_sha256", "toolgap_checkout",
        "toolgap_commit", "toolgap_remote", "toolgap_seed_path",
        "toolgap_seed_sha256", "toolgap_tree",
    }:
        raise ValueError("bootstrap receipt schema differs")
    identity, archive = manifest["identity"], manifest["archives"]["toolgap_source_seed"]
    if (
        receipt["input_manifest_sha256"] != sha256(run_dir / "input-manifest.json")
        or receipt["toolgap_commit"] != identity["toolgap_commit"]
        or receipt["toolgap_tree"] != identity["toolgap_tree"]
        or receipt["toolgap_remote"] != identity["toolgap_remote"]
        or receipt["toolgap_seed_sha256"] != archive["sha256"]
        or any(not isinstance(receipt[field], str) or not Path(receipt[field]).is_absolute()
               for field in ("input_manifest_path", "toolgap_checkout", "toolgap_seed_path"))
    ):
        raise ValueError("bootstrap receipt differs from frozen input")


def runtime_wheel_filename(manifest: dict[str, object]) -> str:
    archives = manifest.get("archives")
    entry = archives.get("runtime_wheel") if isinstance(archives, dict) else None
    filename = entry.get("path") if isinstance(entry, dict) else None
    if (
        not isinstance(filename, str)
        or filename != RUNTIME_WHEEL_FILENAME
        or Path(filename).name != filename
        or not filename.endswith(".whl")
    ):
        raise ValueError("runtime wheel manifest filename differs")
    return filename


def storage_minimum_free_bytes(manifest: dict[str, object]) -> int:
    storage = manifest.get("storage_preflight")
    if storage != {"minimum_free_bytes": MINIMUM_FREE_BYTES}:
        raise ValueError("storage preflight manifest differs")
    return MINIMUM_FREE_BYTES


def validate_storage_preflight_record(
    path: Path,
    stage: str,
    minimum: int,
    expected_path: str,
    *,
    allow_insufficient: bool,
) -> None:
    absolute_regular(path, path.name)
    document = load_json(path, path.name)
    available = document.get("available_free_bytes")
    total = document.get("total_bytes")
    if (
        set(document) != {
            "available_free_bytes", "minimum_free_bytes", "path",
            "schema_version", "stage", "total_bytes",
        }
        or type(document["schema_version"]) is not int
        or document["schema_version"] != 1
        or document["stage"] != stage
        or document["minimum_free_bytes"] != minimum
        or document["path"] != expected_path
        or type(available) is not int
        or available < 0
        or type(total) is not int
        or total < available
        or (not allow_insufficient and available < minimum)
    ):
        raise ValueError(f"storage preflight differs: {stage}")


def validate_storage_preflight(
    run_dir: Path,
    manifest: dict[str, object],
    context: dict[str, object],
) -> None:
    minimum = storage_minimum_free_bytes(manifest)
    for filename, stage in (
        ("storage-preflight-source-restore.json", "source_restore"),
        ("storage-preflight-resolver.json", "resolver"),
    ):
        validate_storage_preflight_record(
            run_dir / filename,
            stage,
            minimum,
            context["work_root"],
            allow_insufficient=False,
        )


def validate_pre_execution_evidence(
    run_dir: Path,
    context: dict[str, object],
) -> tuple[dict[str, object], set[str]]:
    failure_path = run_dir / "pre-execution-failure.json"
    absolute_regular(failure_path, failure_path.name)
    if failure_path.stat().st_mode & 0o222:
        raise ValueError("pre-execution failure evidence must be read-only")
    failure = load_json(failure_path, "pre-execution failure evidence")
    phase = failure.get("failure_phase")
    exit_code = failure.get("exit_code")
    if (
        set(failure) != {"exit_code", "failure_phase", "schema_version"}
        or type(failure["schema_version"]) is not int
        or failure["schema_version"] != 1
        or phase not in FAILURE_PHASES
        or type(exit_code) is not int
        or not 1 <= exit_code <= 255
    ):
        raise ValueError("pre-execution failure evidence differs")

    phase_index = FAILURE_PHASES.index(phase)
    source_index = FAILURE_PHASES.index("source_restore")
    resolver_index = FAILURE_PHASES.index("resolver")
    preflights = (
        ("storage-preflight-source-restore.json", "source_restore", source_index),
        ("storage-preflight-resolver.json", "resolver", resolver_index),
    )
    required = {failure_path.name}
    expected_names = {
        filename for filename, _, stage_index in preflights
        if phase_index >= stage_index
    }
    observed_names = {
        filename for filename, _, _ in preflights
        if (run_dir / filename).exists()
    }
    if observed_names != expected_names:
        raise ValueError("pre-execution storage preflight set differs for failure phase")
    manifest = None
    if expected_names:
        manifest = validate_input_manifest(run_dir, context)
        minimum = storage_minimum_free_bytes(manifest)
        required.add("input-manifest.json")
        for filename, stage, stage_index in preflights:
            if filename in expected_names:
                validate_storage_preflight_record(
                    run_dir / filename,
                    stage,
                    minimum,
                    context["work_root"],
                    allow_insufficient=phase_index == stage_index,
                )
                required.add(filename)
    validate_phase_milestones(run_dir, context, manifest, phase)
    return failure, required


def pre_execution_failure_reason(failure: dict[str, object]) -> str:
    return f"runner failure at phase {failure['failure_phase']}, exit {failure['exit_code']}"


def validate_staged_runtime_inputs(run_dir: Path, manifest: dict[str, object]) -> None:
    archives = manifest["archives"]
    wheel_filename = runtime_wheel_filename(manifest)
    bindings = {
        wheel_filename: archives["runtime_wheel"],
        "runtime-wheel-provenance.json": archives["runtime_wheel_provenance"],
    }
    for filename, entry in bindings.items():
        path = run_dir / filename
        absolute_regular(path, filename)
        if path.stat().st_size != entry["size_bytes"] or sha256(path) != entry["sha256"]:
            raise ValueError(f"staged input differs: {filename}")
    provenance = load_json(run_dir / "runtime-wheel-provenance.json", "runtime provenance")
    if provenance.get("identity") != "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite":
        raise ValueError("runtime provenance identity differs")
    output_wheel = provenance.get("output_wheel")
    if (
        not isinstance(output_wheel, dict)
        or output_wheel.get("filename") != wheel_filename
        or output_wheel.get("sha256") != archives["runtime_wheel"]["sha256"]
        or type(output_wheel.get("size_bytes")) is not int
        or output_wheel.get("size_bytes") != archives["runtime_wheel"]["size_bytes"]
    ):
        raise ValueError("runtime provenance wheel binding differs")
    patches = provenance.get("patches")
    expected_patches = manifest["patches"]
    if not isinstance(patches, list) or not isinstance(expected_patches, list) or len(patches) != 3:
        raise ValueError("runtime provenance patch set differs")
    for label, observed, expected in zip(("patch_one", "patch_two", "patch_three"), patches, expected_patches):
        if (
            not isinstance(observed, dict) or not isinstance(expected, dict)
            or observed.get("label") != label
            or not isinstance(observed.get("path"), str) or not Path(observed["path"]).is_absolute()
            or observed.get("sha256") != expected.get("sha256")
        ):
            raise ValueError("runtime provenance patch binding differs")
    base = provenance.get("base_wheel")
    if not isinstance(base, dict) or base.get("filename") != "sglang-0.0.0.dev2+g734a8e921-cp312-cp312-linux_x86_64.whl" or base.get("sha256") != "0874acca7b27e45ae39606eb12ee24a5f4cb17cd3791bb60fdccb95c332bf59e":
        raise ValueError("runtime provenance base payload differs")


def validate_runtime_inputs(run_dir: Path, manifest: dict[str, object]) -> None:
    validate_staged_runtime_inputs(run_dir, manifest)
    archives = manifest["archives"]
    wheel_filename = runtime_wheel_filename(manifest)
    validation = load_json(run_dir / "runtime-wheel-validation.json", "runtime wheel validation")
    if type(validation.get("runtime_wheel_size_bytes")) is not int:
        raise ValueError("runtime wheel validation size differs")
    if validation != {
        "provenance_identity": "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite",
        "runtime_wheel_filename": wheel_filename,
        "runtime_wheel_sha256": archives["runtime_wheel"]["sha256"],
        "runtime_wheel_size_bytes": archives["runtime_wheel"]["size_bytes"],
        "source_rebuild": False,
    }:
        raise ValueError("runtime wheel validation differs")


def validate_plan(run_dir: Path) -> None:
    plan = load_json(run_dir / "arm-plan.json", "arm plan")
    if set(plan) != {"arms", "fresh_process_per_arm", "selector_module"}:
        raise ValueError("arm plan schema differs")
    if plan["fresh_process_per_arm"] is not True or plan["selector_module"] != SELECTOR_MODULE:
        raise ValueError("arm plan does not require fresh formal arms")
    arms = plan["arms"]
    if not isinstance(arms, list) or [item.get("arm") for item in arms if isinstance(item, dict)] != list(ARMS):
        raise ValueError("arm plan differs")
    for item in arms:
        if not isinstance(item, dict) or set(item) != {"arm", "selector"} or item["selector"] != SELECTORS[item["arm"]]:
            raise ValueError("invalid arm plan row")


def validate_source_provenance(run_dir: Path, manifest: dict[str, object]) -> None:
    source = load_json(run_dir / "sglang-provenance.json", "SGLang source provenance")
    required = {"base_commit", "base_tree", "patched_commit", "patched_tree", "patches"}
    if set(source) != required:
        raise ValueError("SGLang source provenance schema differs")
    identity = manifest["identity"]
    if source["base_commit"] != identity["sglang_base_commit"] or source["base_tree"] != identity["sglang_base_tree"]:
        raise ValueError("SGLang source provenance base differs")
    if not valid_digest(source["patched_commit"], 40) or not valid_digest(source["patched_tree"], 40):
        raise ValueError("SGLang patched identity is invalid")
    patches = source["patches"]
    expected = manifest["patches"]
    if not isinstance(patches, list) or not isinstance(expected, list) or len(patches) != 3 or len(expected) != 3:
        raise ValueError("SGLang source patch set differs")
    for index, (observed, binding) in enumerate(zip(patches, expected), start=1):
        if (
            not isinstance(observed, dict) or not isinstance(binding, dict)
            or observed.get("label") != f"patch_{index}"
            or not isinstance(observed.get("path"), str) or not Path(observed["path"]).is_absolute()
            or observed.get("sha256") != binding.get("sha256")
        ):
            raise ValueError("SGLang source patch binding differs")



def validate_installed_package_provenance(run_dir: Path) -> None:
    package = load_json(run_dir / "sglang-package-provenance.json", "installed SGLang package provenance")
    required_package = {
        "expected_interpreter", "install_root", "interpreter", "interpreter_matches", "modules",
        "package_path", "package_under_install_root", "passed", "source_root", "sys_path",
    }
    if set(package) != required_package or package["passed"] is not True:
        raise ValueError("installed SGLang package provenance does not pass")
    if package["interpreter_matches"] is not True or package["package_under_install_root"] is not True:
        raise ValueError("installed SGLang package is not bound to the runtime venv")
    if any(not isinstance(package.get(field), str) or not Path(package[field]).is_absolute() for field in (
        "expected_interpreter", "install_root", "interpreter", "package_path", "source_root",
    )):
        raise ValueError("installed SGLang package provenance path differs")
    modules = package["modules"]
    if not isinstance(modules, dict) or set(modules) != {
        "session_ref_tracker", "unified_tree_core", "unified_tree_core_interface", "unified_radix_cache",
    }:
        raise ValueError("installed SGLang module provenance set differs")
    for item in modules.values():
        if (
            not isinstance(item, dict)
            or item.get("hash_matches_source") is not True
            or item.get("installed_under_root") is not True
            or item.get("outside_source_checkout") is not True
        ):
            raise ValueError("installed SGLang module provenance differs")


def validate_sglang_provenance(run_dir: Path, manifest: dict[str, object]) -> None:
    validate_source_provenance(run_dir, manifest)
    validate_installed_package_provenance(run_dir)


def require_nonempty_regular(run_dir: Path, name: str) -> None:
    path = run_dir / name
    absolute_regular(path, name)
    if path.stat().st_size < 1:
        raise ValueError(f"completed milestone artifact is empty: {name}")


def validate_input_binding_milestone(
    run_dir: Path, context: dict[str, object], manifest: dict[str, object]
) -> None:
    validate_input_oss_receipt(run_dir, manifest)
    validate_bootstrap(run_dir, manifest)
    require_nonempty_regular(run_dir, "input-manifest-verify.log")
    if (run_dir / "input-manifest-verify.log").read_text(encoding="utf-8") != "input_manifest=verified\n":
        raise ValueError("input binding verification differs")
    validate_staged_runtime_inputs(run_dir, manifest)


def validate_source_restore_milestone(
    run_dir: Path, context: dict[str, object], manifest: dict[str, object]
) -> None:
    require_nonempty_regular(run_dir, "source-restore.log")
    validate_source_provenance(run_dir, manifest)


def validate_model_milestone(
    run_dir: Path, context: dict[str, object], manifest: dict[str, object]
) -> None:
    require_nonempty_regular(run_dir, "model-seed-prepare.log")
    receipt = load_json(run_dir / "model-snapshot.json", "model snapshot receipt")
    if set(receipt) != {
        "archive_sha256", "file_count", "inventory_sha256", "model_root",
        "repository", "revision", "total_bytes",
    }:
        raise ValueError("model snapshot receipt schema differs")
    model = manifest.get("model")
    archive = manifest.get("archives", {}).get("model_snapshot")
    if (
        not isinstance(model, dict) or not isinstance(archive, dict)
        or receipt["archive_sha256"] != archive.get("sha256")
        or receipt["inventory_sha256"] != model.get("inventory_sha256")
        or receipt["repository"] != model.get("repository")
        or receipt["revision"] != model.get("revision")
        or receipt["model_root"] != str(Path(context["work_root"]) / "model-input/model-snapshot")
        or type(receipt["file_count"]) is not int or receipt["file_count"] < 1
        or type(receipt["total_bytes"]) is not int or receipt["total_bytes"] < 1
    ):
        raise ValueError("model snapshot receipt binding differs")


def validate_wheelhouse_milestone(run_dir: Path, manifest: dict[str, object]) -> None:
    index_doc = load_json(run_dir / "cuda-wheelhouse-index.json", "CUDA wheelhouse index")
    validation = load_json(run_dir / "cuda-wheelhouse-validation.json", "CUDA wheelhouse validation")
    required = {"sglang_kernel", "sgl_deep_ep", "sgl_deep_gemm", "torch", "torchvision", "torchaudio"}
    wheels = index_doc.get("wheels")
    if set(index_doc) != {"schema_version", "wheels"} or type(index_doc["schema_version"]) is not int or index_doc["schema_version"] != 1 or not isinstance(wheels, dict) or set(wheels) != required:
        raise ValueError("CUDA wheelhouse index differs")
    for label, entry in wheels.items():
        if (
            not isinstance(entry, dict) or set(entry) != {"path", "sha256", "size_bytes"}
            or not isinstance(entry["path"], str) or Path(entry["path"]).name != entry["path"]
            or not valid_digest(entry["sha256"])
            or type(entry["size_bytes"]) is not int or entry["size_bytes"] < 1
        ):
            raise ValueError(f"CUDA wheelhouse entry differs: {label}")
    archive = manifest["archives"]["cuda_wheelhouse"]
    if type(validation.get("archive_size_bytes")) is not int:
        raise ValueError("CUDA wheelhouse validation size differs")
    if validation != {
        "archive_sha256": archive["sha256"],
        "archive_size_bytes": archive["size_bytes"],
        "index_sha256": sha256(run_dir / "cuda-wheelhouse-index.json"),
        "wheels": wheels,
    }:
        raise ValueError("CUDA wheelhouse validation differs")


def validate_runtime_environment(run_dir: Path, context: dict[str, object]) -> None:
    path = run_dir / "runtime.env"
    absolute_regular(path, path.name)
    values = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        key, separator, encoded = raw.partition("=")
        if not separator or key in values:
            raise ValueError("runtime environment schema differs")
        decoded = shlex.split(encoded)
        if len(decoded) != 1:
            raise ValueError("runtime environment value differs")
        values[key] = decoded[0]
    work_root = Path(context["work_root"])
    expected = {
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "SGLANG_ENABLE_UNIFIED_RADIX_TREE": "1",
        "TOOLGAP_G1_MODEL_PATH": str(work_root / "model-input/model-snapshot"),
        "TREATMENT": str(work_root / "sglang"),
        "RUNTIME_PYTHON": str(work_root / "runtime-venv/bin/python"),
        "ORDINARY_PYPI_INDEX": "http://mirrors.cloud.aliyuncs.com/pypi/simple/",
    }
    if values != expected:
        raise ValueError("runtime environment binding differs")


def validate_resolver_milestone(
    run_dir: Path, context: dict[str, object], manifest: dict[str, object]
) -> None:
    require_nonempty_regular(run_dir, "resolver-install.log")
    require_nonempty_regular(run_dir, "ordinary-requirements.txt")
    require_nonempty_regular(run_dir, "arm-runner.py")
    validate_runtime_inputs(run_dir, manifest)
    validate_wheelhouse_milestone(run_dir, manifest)
    validate_installed_package_provenance(run_dir)
    try:
        installed = json.loads((run_dir / "installed-distributions.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("installed distributions differ") from error
    if not isinstance(installed, list) or not all(isinstance(item, dict) for item in installed):
        raise ValueError("installed distributions differ")
    names = {re.sub(r"[-_.]+", "-", str(item.get("name", ""))).lower() for item in installed}
    if not {"sglang", "sglang-kernel", "sgl-deep-ep", "sgl-deep-gemm", "torch", "torchvision", "torchaudio", "flashinfer-python"}.issubset(names):
        raise ValueError("installed distribution set differs")
    exception = load_json(run_dir / "omitted-dependency-exception.json", "omitted dependency exception")
    if exception != {
        "allowed_uninstalled_requirement": "cuda-tile==1.6.0rc5",
        "installed_without_dependency_resolution": "flashinfer_python[cu12]==0.6.17",
        "reason": "CUDA12 wheel route must not source-build cuda-tile on ECS",
    }:
        raise ValueError("omitted dependency exception differs")
    validate_plan(run_dir)
    validate_runtime_environment(run_dir, context)


def validate_formal_arms_milestone(
    run_dir: Path, context: dict[str, object], manifest: dict[str, object]
) -> None:
    validate_plan(run_dir)
    validate_cleanup(run_dir)
    records = []
    for arm in ARMS:
        command = run_dir / "arms" / f"{arm}.command.txt"
        absolute_regular(command, f"{arm} command")
        if command.read_text(encoding="utf-8") != SELECTORS[arm] + "\n":
            raise ValueError(f"{arm} selector evidence differs")
        require_nonempty_regular(run_dir, f"arms/{arm}.log")
        record = load_json(run_dir / "arms" / f"{arm}.record.json", f"{arm} record")
        permitted = RECORD_FIELDS | ({"stock_eviction"} if arm == "stock_eviction_liveness" else set())
        if set(record) != permitted or record.get("arm") != arm:
            raise ValueError(f"{arm} completed record schema differs")
        records.append(record)
    try:
        aggregate = json.loads((run_dir / "arm-records.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("arm record aggregate differs") from error
    if aggregate != records:
        raise ValueError("arm record aggregate differs")


def validate_scope_milestone(
    run_dir: Path, context: dict[str, object], manifest: dict[str, object]
) -> None:
    require_nonempty_regular(run_dir, "scope-scan.log")
    if (run_dir / "scope-scan.log").read_text(encoding="utf-8") != "scope=clean\n":
        raise ValueError("runtime scope scanner did not prove clean scope")


def validate_manifest_milestone(
    run_dir: Path, context: dict[str, object], manifest: dict[str, object]
) -> None:
    rendered = load_json(run_dir / "manifest.json", "rendered manifest")
    identity = rendered.get("identity")
    terminal = identity.get("gate_decision") if isinstance(identity, dict) else None
    if terminal not in {"PASS", "STOP", "INVALID"}:
        raise ValueError("rendered manifest terminal differs")
    validate_rendered_manifest(run_dir, context, terminal)


MILESTONE_VALIDATORS = {
    "input_binding": validate_input_binding_milestone,
    "source_restore": validate_source_restore_milestone,
    "model": validate_model_milestone,
    "resolver": validate_resolver_milestone,
    "formal_arms": validate_formal_arms_milestone,
    "scope": validate_scope_milestone,
    "manifest": validate_manifest_milestone,
}
PHASE_REQUIRED_MILESTONES = {
    "bootstrap": (),
    "input_binding": (),
    "source_restore": ("input_binding",),
    "model": ("input_binding", "source_restore"),
    "resolver": ("input_binding", "source_restore", "model"),
    "formal_arms": ("input_binding", "source_restore", "model", "resolver"),
    "scope": ("input_binding", "source_restore", "model", "resolver", "formal_arms"),
    "render": ("input_binding", "source_restore", "model", "resolver", "formal_arms", "scope"),
    "seal": ("input_binding", "source_restore", "model", "resolver", "formal_arms", "scope", "manifest"),
}


def validate_phase_milestones(
    run_dir: Path, context: dict[str, object], manifest: dict[str, object] | None, phase: str
) -> None:
    required = PHASE_REQUIRED_MILESTONES[phase]
    if required and manifest is None:
        raise ValueError("failure phase requires input manifest")
    for milestone in required:
        MILESTONE_VALIDATORS[milestone](run_dir, context, manifest)


def record_errors(record: object, expected_arm: str) -> list[str]:
    errors = []
    allowed = RECORD_FIELDS | ({"stock_eviction"} if expected_arm == "stock_eviction_liveness" else set())
    if not isinstance(record, dict) or set(record) != allowed:
        return ["schema"]
    if record["arm"] != expected_arm:
        errors.append("arm")
    qualification = record["component_qualification"]
    if not isinstance(qualification, dict) or qualification.get("components") != ["FULL"] or qualification.get("supports_swa") is not False or type(qualification.get("page_size")) is not int or qualification["page_size"] < 1:
        errors.append("qualification")
    operation = record["operation"]
    if not isinstance(operation, dict) or not isinstance(operation.get("session_id"), str) or type(operation.get("supplied_generation")) is not int:
        errors.append("operation")
    target = record["target"]
    if not isinstance(target, dict) or set(target) != TARGET_FIELDS:
        errors.append("target")
    else:
        for key in ("requested_node_ids", "eligible_node_ids", "scheduled_node_ids", "completed_node_ids"):
            if not isinstance(target[key], list) or not all(type(value) is int for value in target[key]):
                errors.append(f"target:{key}")
        for phase in ("before", "after"):
            observations = target[phase]
            if not isinstance(observations, list):
                errors.append(f"target:{phase}")
                continue
            for index, observation in enumerate(observations):
                errors.extend(
                    f"target:{phase}[{index}]:{error}"
                    for error in observation_errors(observation)
                )
    counters = record["route_counters"]
    if not isinstance(counters, dict) or set(counters) != COUNTER_FIELDS or any(
        type(counters.get(key)) is not int or counters[key] < 0
        for key in COUNTER_FIELDS if key != "physical_demote_node_ids"
    ) or not isinstance(counters.get("physical_demote_node_ids"), list) or not all(type(item) is int for item in counters["physical_demote_node_ids"]):
        errors.append("route_counters")
    capacity = record["capacity"]
    if not isinstance(capacity, dict) or set(capacity) != {"before", "after"}:
        errors.append("capacity")
    else:
        for sample in capacity.values():
            errors.extend(f"capacity:{error}" for error in capacity_sample_errors(sample))
    if record["priority_release"] not in {"RELEASED", "NOT_RELEASED"}:
        errors.append("priority_release")
    if type(record["released_component_leaves"]) is not int or record["released_component_leaves"] < 0:
        errors.append("released_component_leaves")
    if (
        not isinstance(record["facade"], dict)
        or set(record["facade"]) != {"disposition", "reason"}
        or not all(isinstance(record["facade"].get(field), str) for field in ("disposition", "reason"))
    ):
        errors.append("facade")
    if not isinstance(record["nodes"], list) or not all(isinstance(item, dict) for item in record["nodes"]):
        errors.append("nodes")
    if not isinstance(record["freed_device_ids"], list) or not all(type(value) is int for value in record["freed_device_ids"]):
        errors.append("freed_device_ids")
    if expected_arm == "stock_eviction_liveness":
        errors.extend(stock_eviction_errors(record))
    return errors


def device_ids(observations: list[dict[str, object]]) -> list[int]:
    return sorted(value for observation in observations for value in observation["device_ids"])


def observation_errors(observation: object) -> list[str]:
    if not isinstance(observation, dict):
        return ["not_object"]
    if type(observation.get("node_id")) is not int or type(observation.get("live")) is not bool:
        return ["node_id_or_live"]
    if observation["live"] is False:
        return [] if set(observation) == MISSING_OBSERVATION_FIELDS else ["missing_node_schema"]
    if set(observation) != LIVE_OBSERVATION_FIELDS:
        return ["live_node_schema"]
    bool_fields = (
        "host_committed", "write_through_pending", "load_back_pending", "device_leaf",
    )
    if any(type(observation[field]) is not bool for field in bool_fields):
        return ["live_node_bool"]
    for field in ("device_ids", "lock_refs"):
        value = observation[field]
        if not isinstance(value, list) or not all(type(item) is int for item in value):
            return [f"{field}"]
    if type(observation["session_ref"]) is not int:
        return ["session_ref"]
    return []


def capacity_sample_errors(sample: object) -> list[str]:
    if not isinstance(sample, dict) or set(sample) != {"available_size", "is_not_in_free_group"}:
        return ["schema"]
    if type(sample["available_size"]) is not int or sample["available_size"] < 0:
        return ["available_size"]
    if sample["is_not_in_free_group"] is not True:
        return ["free_group"]
    return []


def stock_eviction_errors(record: dict[str, object]) -> list[str]:
    stock = record.get("stock_eviction")
    if not isinstance(stock, dict) or set(stock) != {
        "candidate_ids_before", "observed_calls", "results", "victims",
    }:
        return ["stock_eviction:schema"]
    candidates = stock["candidate_ids_before"]
    if (
        not isinstance(candidates, list)
        or not candidates
        or any(type(node_id) is not int for node_id in candidates)
        or candidates != sorted(set(candidates))
    ):
        return ["stock_eviction:candidates"]
    observed_calls, results, victims = stock["observed_calls"], stock["results"], stock["victims"]
    if type(observed_calls) is not int or observed_calls < 1:
        return ["stock_eviction:observed_calls"]
    if not isinstance(results, list) or len(results) != observed_calls:
        return ["stock_eviction:results"]
    for index, result in enumerate(results):
        if (
            not isinstance(result, dict)
            or set(result) != {"num_tokens_evicted", "swa_num_tokens_evicted", "mamba_num_evicted"}
            or any(type(result[field]) is not int or result[field] < 0 for field in result)
        ):
            return [f"stock_eviction:results[{index}]"]
    if not any(result["num_tokens_evicted"] > 0 for result in results):
        return ["stock_eviction:no_token_reclaim"]
    counters = record.get("route_counters")
    if not isinstance(counters, dict) or counters.get("stock_evict") != observed_calls:
        return ["stock_eviction:counter"]
    if not isinstance(victims, list) or not victims:
        return ["stock_eviction:victims"]
    victim_ids = []
    for index, victim in enumerate(victims):
        if not isinstance(victim, dict) or set(victim) != {
            "node_id", "before", "after", "capacity_before", "capacity_after",
        }:
            return [f"stock_eviction:victims[{index}]:schema"]
        node_id = victim["node_id"]
        if type(node_id) is not int or node_id not in candidates:
            return [f"stock_eviction:victims[{index}]:candidate"]
        before_errors = observation_errors(victim["before"])
        after_errors = observation_errors(victim["after"])
        if before_errors or after_errors:
            return [f"stock_eviction:victims[{index}]:observation"]
        before, after = victim["before"], victim["after"]
        if (
            before["node_id"] != node_id or before["live"] is not True
            or before["device_leaf"] is not True or not before["device_ids"]
            or after["node_id"] != node_id
            or (after["live"] is True and after["device_ids"] != [])
        ):
            return [f"stock_eviction:victims[{index}]:transition"]
        before_capacity_errors = capacity_sample_errors(victim["capacity_before"])
        after_capacity_errors = capacity_sample_errors(victim["capacity_after"])
        if before_capacity_errors or after_capacity_errors:
            return [f"stock_eviction:victims[{index}]:capacity"]
        if victim["capacity_after"]["available_size"] <= victim["capacity_before"]["available_size"]:
            return [f"stock_eviction:victims[{index}]:no_allocator_reclaim"]
        victim_ids.append(node_id)
    if len(victim_ids) != len(set(victim_ids)):
        return ["stock_eviction:duplicate_victim"]
    return []


def enabled_context_errors(record: dict[str, object]) -> list[str]:
    target, counters = record["target"], record["route_counters"]
    before = target["before"]
    errors = []
    if record["priority_release"] != "RELEASED":
        errors.append("enabled priority release differs")
    if record["facade"] != {"disposition": "ACCEPTED", "reason": "ACCEPTED"}:
        errors.append("enabled facade differs")
    if not before or not all(
        item.get("host_committed") is True and item.get("device_leaf") is True
        and isinstance(item.get("device_ids"), list) and item["device_ids"]
        for item in before
    ):
        errors.append("enabled does not begin with committed Full device tails")
    if len(before) != len(target["after"]):
        errors.append("enabled target observation count differs")
    if counters["checked_facade"] != 1 or counters["checked_backend"] < 1 or counters["stock_evict"] != 0:
        errors.append("enabled route is not the checked non-stock route")
    if not target["requested_node_ids"]:
        errors.append("enabled target is empty")
    return errors


def enabled_stop_reasons(record: dict[str, object]) -> list[str]:
    target, counters, capacity = record["target"], record["route_counters"], record["capacity"]
    expected_ids = device_ids(target["before"])
    reasons = []
    if sorted(record["freed_device_ids"]) != expected_ids:
        reasons.append("enabled freed IDs do not exactly cover the original device tail")
    if counters["physical_demote"] < 1 or counters["cache_owned_drain"] < 1:
        reasons.append("enabled did not take the physical checked-demote route")
    if sorted(counters["physical_demote_node_ids"]) != sorted(target["requested_node_ids"]):
        reasons.append("enabled physical target differs from the requested tail")
    if not all(item.get("live") is True and item.get("device_ids") == [] for item in target["after"]):
        reasons.append("enabled tail still retains device KV")
    if capacity["after"]["available_size"] <= capacity["before"]["available_size"]:
        reasons.append("enabled lacks allocator-visible reclaim")
    return reasons


def bypass_context_errors(record: dict[str, object]) -> list[str]:
    counters, capacity = record["route_counters"], record["capacity"]
    errors = []
    if record["priority_release"] != "RELEASED":
        errors.append("bypass priority release differs")
    if record["facade"] != {"disposition": "BYPASSED", "reason": "PRIORITY_RELEASE_ONLY"}:
        errors.append("bypass facade differs")
    if counters["checked_facade"] != 0 or counters["checked_backend"] != 0 or counters["stock_evict"] != 0:
        errors.append("bypass route differs")
    if capacity["after"]["available_size"] < capacity["before"]["available_size"]:
        errors.append("bypass allocator capacity regressed")
    before, after = record["target"]["before"], record["target"]["after"]
    if len(before) != len(after):
        errors.append("bypass target observation count differs")
    elif any(set(item.get("device_ids", [])) - set(before[index].get("device_ids", [])) for index, item in enumerate(after)):
        errors.append("bypass gained an unaccounted device ID")
    return errors


def bypass_stop_reasons(record: dict[str, object]) -> list[str]:
    counters, capacity = record["route_counters"], record["capacity"]
    before, after = record["target"]["before"], record["target"]["after"]
    reasons = []
    if record["freed_device_ids"]:
        reasons.append("bypass reported freed device IDs")
    if counters["physical_demote"] != 0 or counters["cache_owned_drain"] != 0:
        reasons.append("bypass took a physical checked-demote route")
    if capacity["after"]["available_size"] > capacity["before"]["available_size"]:
        reasons.append("bypass increased allocator capacity")
    if len(before) == len(after) and any(
        set(item.get("device_ids", [])) < set(before[index].get("device_ids", []))
        for index, item in enumerate(after)
    ):
        reasons.append("bypass removed device KV")
    return reasons


def rejection_observations_pass(
    record: dict[str, object], reason: str
) -> bool:
    operation = record["operation"]
    target = record["target"]
    requested = target["requested_node_ids"]
    if (
        set(operation) != {"session_id", "supplied_generation"}
        or type(operation["supplied_generation"]) is not int
        or not requested
        or len(requested) != len(set(requested))
        or target["eligible_node_ids"] != []
        or target["scheduled_node_ids"] != requested
        or target["completed_node_ids"] != []
    ):
        return False
    before = {item["node_id"]: item for item in target["before"]}
    after = {item["node_id"]: item for item in target["after"]}
    if (
        len(before) != len(target["before"])
        or len(after) != len(target["after"])
        or set(before) != set(requested)
        or set(after) != set(requested)
    ):
        return False
    if any(
        observation["live"] is not True
        or not observation["device_ids"]
        for observation in (*before.values(), *after.values())
    ) or any(after[node_id]["device_ids"] != before[node_id]["device_ids"] for node_id in requested):
        return False
    if reason == "WRITE_THROUGH_PENDING":
        return all(
            observation["write_through_pending"] is True
            and observation["host_committed"] is False
            for observation in (*before.values(), *after.values())
        )
    if reason == "NON_TARGET_SESSION_COVERAGE":
        return all(
            before[node_id]["session_ref"] == 2
            and after[node_id]["session_ref"] == 1
            and before[node_id]["host_committed"] is True
            and after[node_id]["host_committed"] is True
            and before[node_id]["device_leaf"] is True
            and after[node_id]["device_leaf"] is True
            for node_id in requested
        )
    if reason == "DEVICE_LOCKED":
        return all(
            any(value > 0 for value in before[node_id]["lock_refs"])
            and any(value > 0 for value in after[node_id]["lock_refs"])
            for node_id in requested
        )
    return False


def rejection_nodes_pass(record: dict[str, object], reason: str) -> bool:
    nodes = record["nodes"]
    if reason == "STALE_GENERATION":
        return nodes == []
    if not nodes or not all(
            set(node) == {"node_id", "disposition", "reason", "freed_device_ids"}
            and type(node["node_id"]) is int
            and node["disposition"] == "DEFERRED"
            and node["reason"] == reason
            and node["freed_device_ids"] == []
            for node in nodes
    ):
        return False
    return [node["node_id"] for node in nodes] == record["target"]["requested_node_ids"]


def stale_rejection_context_pass(record: dict[str, object]) -> bool:
    operation = record["operation"]
    target = record["target"]
    return (
        set(operation) == {"session_id", "supplied_generation", "current_generation"}
        and type(operation["supplied_generation"]) is int
        and type(operation["current_generation"]) is int
        and operation["supplied_generation"] != operation["current_generation"]
        and record["released_component_leaves"] == 0
        and all(target[field] == [] for field in TARGET_FIELDS)
    )


def rejection_passes(record: dict[str, object], reason: str) -> bool:
    counters = record["route_counters"]
    stale = reason == "STALE_GENERATION"
    required_release = "NOT_RELEASED" if stale else "RELEASED"
    expected_facade = (
        {"disposition": "REJECTED", "reason": reason}
        if stale else {"disposition": "DEFERRED", "reason": "DEFERRED"}
    )
    return (
        record["facade"] == expected_facade
        and record["priority_release"] == required_release
        and counters["checked_facade"] == 1
        and (counters["checked_backend"] == 0 if stale else counters["checked_backend"] >= 1)
        and rejection_nodes_pass(record, reason)
        and (stale_rejection_context_pass(record) if stale else rejection_observations_pass(record, reason))
        and (record["released_component_leaves"] == 0 if stale else record["released_component_leaves"] > 0)
        and record["freed_device_ids"] == []
        and counters["physical_demote"] == 0
        and counters["physical_demote_node_ids"] == []
        and counters["cache_owned_drain"] == 0
        and counters["stock_evict"] == 0
        and record["capacity"]["before"]["available_size"] == record["capacity"]["after"]["available_size"]
    )


def liveness_passes(record: dict[str, object]) -> bool:
    stock = record.get("stock_eviction")
    if not isinstance(stock, dict):
        return False
    victims, results = stock.get("victims"), stock.get("results")
    return (
        record["priority_release"] == "RELEASED"
        and record["facade"] == {"disposition": "BYPASSED", "reason": "PRIORITY_RELEASE_ONLY"}
        and record["route_counters"]["checked_facade"] == 0
        and record["route_counters"]["checked_backend"] == 0
        and record["route_counters"]["physical_demote"] == 0
        and record["route_counters"]["cache_owned_drain"] == 0
        and record["freed_device_ids"] == []
        and isinstance(stock.get("candidate_ids_before"), list) and bool(stock["candidate_ids_before"])
        and type(stock.get("observed_calls")) is int and stock["observed_calls"] > 0
        and isinstance(victims, list) and bool(victims)
        and isinstance(results, list) and any(isinstance(item, dict) and item.get("num_tokens_evicted", 0) > 0 for item in results)
        and record["route_counters"]["stock_evict"] == stock["observed_calls"]
    )


def classify_records(records: object) -> tuple[str, list[str]]:
    if not isinstance(records, list) or len(records) != len(ARMS):
        return "INVALID", ["record set differs"]
    by_arm: dict[str, dict[str, object]] = {}
    structural = []
    for record in records:
        arm = record.get("arm") if isinstance(record, dict) else None
        if not isinstance(arm, str) or arm in by_arm:
            structural.append("duplicate or missing arm")
            continue
        by_arm[arm] = record
    if set(by_arm) != set(ARMS):
        structural.append("required arm set differs")
    for arm in ARMS:
        if arm in by_arm:
            structural.extend(f"{arm}:{error}" for error in record_errors(by_arm[arm], arm))
    if structural:
        return "INVALID", structural
    enabled, bypass = by_arm["enabled"], by_arm["bypass"]
    formal_errors = enabled_context_errors(enabled) + bypass_context_errors(bypass)
    if formal_errors:
        return "INVALID", formal_errors
    causal_stop = enabled_stop_reasons(enabled) + bypass_stop_reasons(bypass)
    if causal_stop:
        return "STOP", causal_stop
    failures = []
    for arm, reason in REJECTION_REASONS.items():
        if not rejection_passes(by_arm[arm], reason):
            failures.append(f"{arm} does not preserve rejection contract")
    if not liveness_passes(by_arm["stock_eviction_liveness"]):
        failures.append("stock eviction liveness is absent")
    return ("INVALID", failures) if failures else ("PASS", ["all formal G1 predicates observed"])


def validate_gpu_samples(path: Path, arm_pid: int, expected_union: list[int], arm: str) -> None:
    document = load_json(path, f"{arm} GPU samples")
    if set(document) != {"arm_pid", "poll_seconds", "samples"}:
        raise ValueError(f"{arm} GPU sample schema differs")
    if type(document["arm_pid"]) is not int or document["arm_pid"] != arm_pid or type(document["poll_seconds"]) not in {int, float} or document["poll_seconds"] != 0.25:
        raise ValueError(f"{arm} GPU sampler binding differs")
    samples = document["samples"]
    if not isinstance(samples, list) or not samples:
        raise ValueError(f"{arm} GPU samples are absent")
    observed_union: set[int] = set()
    previous = None
    for sample in samples:
        if not isinstance(sample, dict) or set(sample) != {"captured_at", "pids"} or not isinstance(sample["captured_at"], str):
            raise ValueError(f"{arm} GPU sample differs")
        try:
            captured = datetime.fromisoformat(sample["captured_at"].replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError(f"{arm} GPU sample timestamp differs") from error
        if captured.tzinfo is None or (previous is not None and captured < previous):
            raise ValueError(f"{arm} GPU sample order differs")
        previous = captured
        pids = sample["pids"]
        if (
            not isinstance(pids, list)
            or any(type(pid) is not int or pid < 1 for pid in pids)
            or pids != sorted(set(pids))
        ):
            raise ValueError(f"{arm} GPU sample PIDs differ")
        observed_union.update(pids)
    if sorted(observed_union) != expected_union:
        raise ValueError(f"{arm} GPU sampler union differs")


def validate_cleanup(run_dir: Path) -> None:
    cleanup = load_json(run_dir / "cleanup.json", "cleanup")
    if set(cleanup) != {"arms", "all_clean"} or cleanup["all_clean"] is not True:
        raise ValueError("cleanup summary differs")
    arms = cleanup["arms"]
    if not isinstance(arms, list) or [item.get("arm") for item in arms if isinstance(item, dict)] != list(ARMS):
        raise ValueError("cleanup arm set differs")
    for item in arms:
        if not isinstance(item, dict) or set(item) != {"arm", "pid", "pgid", "listener_clean", "pgid_clean", "gpu_delta_clean"}:
            raise ValueError("cleanup row differs")
        if type(item["pid"]) is not int or type(item["pgid"]) is not int or item["pid"] < 1 or item["pgid"] != item["pid"]:
            raise ValueError("cleanup PID/PGID binding differs")
        if not all(item[key] is True for key in ("listener_clean", "pgid_clean", "gpu_delta_clean")):
            raise ValueError("an arm leaked a runtime resource")
        arm = item["arm"]
        arm_root = run_dir / "arms"
        for suffix, expected in (("pid", str(item["pid"])), ("pgid", str(item["pgid"]))):
            source = arm_root / f"{arm}.{suffix}"
            absolute_regular(source, f"{arm} {suffix}")
            if source.read_text(encoding="utf-8") != expected + "\n":
                raise ValueError(f"{arm} {suffix} evidence differs")
        handshake_path = arm_root / f"{arm}.launcher-handshake.json"
        ack_path = arm_root / f"{arm}.launcher-ack.json"
        absolute_regular(handshake_path, f"{arm} launcher handshake")
        absolute_regular(ack_path, f"{arm} launcher ack")
        handshake = load_json(handshake_path, f"{arm} launcher handshake")
        ack = load_json(ack_path, f"{arm} launcher ack")
        if (
            handshake != {"pgid": item["pgid"], "pid": item["pid"], "schema_version": 1}
            or ack != {"pid": item["pid"], "schema_version": 1}
            or type(handshake.get("pid")) is not int
            or type(handshake.get("pgid")) is not int
            or type(handshake.get("schema_version")) is not int
            or type(ack.get("pid")) is not int
            or type(ack.get("schema_version")) is not int
            or handshake_path.stat().st_mode & 0o222
            or ack_path.stat().st_mode & 0o222
        ):
            raise ValueError(f"{arm} launcher handshake differs")
        if load_json(arm_root / f"{arm}.cleanup.json", f"{arm} cleanup row") != item:
            raise ValueError(f"{arm} cleanup row aggregate differs")
        for suffix in (
            "gpu-before.txt", "gpu-samples.json", "gpu-during.txt", "gpu-attributable.txt", "gpu-after.txt", "gpu-leaked.txt",
            "listeners-before.txt", "listeners-after.txt", "listeners-leaked.txt", "process-group-after.txt",
        ):
            absolute_regular(arm_root / f"{arm}.{suffix}", f"{arm} cleanup evidence")
        pids = {
            suffix: [int(value) for value in (arm_root / f"{arm}.{suffix}").read_text(encoding="utf-8").split()]
            for suffix in ("gpu-before.txt", "gpu-during.txt", "gpu-attributable.txt", "gpu-after.txt", "gpu-leaked.txt")
        }
        if any(values != sorted(set(values)) or any(value < 1 for value in values) for values in pids.values()):
            raise ValueError(f"{arm} GPU PID evidence differs")
        validate_gpu_samples(arm_root / f"{arm}.gpu-samples.json", item["pid"], pids["gpu-during.txt"], arm)
        if pids["gpu-attributable.txt"] != sorted(set(pids["gpu-during.txt"]) - set(pids["gpu-before.txt"])):
            raise ValueError(f"{arm} attributable GPU PID evidence differs")
        if pids["gpu-leaked.txt"] != sorted(set(pids["gpu-attributable.txt"]) & set(pids["gpu-after.txt"])):
            raise ValueError(f"{arm} leaked GPU PID evidence differs")
        listeners_before = (arm_root / f"{arm}.listeners-before.txt").read_text(encoding="utf-8").splitlines()
        listeners_after = (arm_root / f"{arm}.listeners-after.txt").read_text(encoding="utf-8").splitlines()
        listeners_leaked = (arm_root / f"{arm}.listeners-leaked.txt").read_text(encoding="utf-8").splitlines()
        if listeners_before != sorted(set(listeners_before)) or listeners_after != sorted(set(listeners_after)):
            raise ValueError(f"{arm} listener evidence is not canonical")
        if listeners_leaked != sorted(set(listeners_after) - set(listeners_before)):
            raise ValueError(f"{arm} listener leak evidence differs")
        if (arm_root / f"{arm}.process-group-after.txt").read_text(encoding="utf-8"):
            raise ValueError(f"{arm} process group survived cleanup")


def required_artifacts(run_dir: Path) -> tuple[str, ...]:
    dynamic = tuple(
        f"arms/{arm}.{suffix}" for arm in ARMS for suffix in (
            "command.txt", "log", "record.json", "cleanup.json", "pid", "pgid",
            "launcher-handshake.json", "launcher-ack.json",
            "gpu-before.txt", "gpu-samples.json", "gpu-during.txt", "gpu-attributable.txt", "gpu-after.txt", "gpu-leaked.txt",
            "listeners-before.txt", "listeners-after.txt", "listeners-leaked.txt", "process-group-after.txt",
        )
    )
    return BASE_ARTIFACTS + (runtime_wheel_filename(load_json(run_dir / "input-manifest.json", "input manifest")),) + dynamic


def validate_rendered_manifest(run_dir: Path, context: dict[str, object], terminal: str | None = None) -> None:
    manifest = load_json(run_dir / "manifest.json", "rendered manifest")
    identity = manifest.get("identity")
    expected = {
        "attempt_id": context["attempt_id"], "bundle_id": BUNDLE_ID,
        "claim_state": "roadmap", "gate": "G1",
        "gate_decision": terminal if terminal is not None else "__GENERATED__",
        "kind": KIND, "spec_path": SPEC_PATH, "spec_sha256": context["spec_sha256"],
        "toolgap_commit": context["toolgap_commit"], "toolgap_tree": context["toolgap_tree"],
    }
    if identity != expected:
        raise ValueError("rendered manifest identity differs")
    if manifest.get("planned_success_artifacts") != list(required_artifacts(run_dir)):
        raise ValueError("rendered manifest artifact plan differs")
    checksum = (run_dir / "manifest.sha256").read_text(encoding="utf-8").split()
    if not checksum or checksum[0] != sha256(run_dir / "manifest.json"):
        raise ValueError("rendered manifest checksum differs")


def render(args: argparse.Namespace) -> int:
    output = args.output.resolve()
    if output.exists():
        raise ValueError("refusing to replace manifest")
    run_dir = output.parent
    context = validate_context(run_dir)
    template = load_json(args.template.resolve(), "manifest template")
    if template.get("identity", {}).get("bundle_id") != BUNDLE_ID:
        raise ValueError("manifest template differs")
    template["identity"] = {
        "attempt_id": context["attempt_id"], "bundle_id": BUNDLE_ID,
        "claim_state": "roadmap", "gate": "G1", "gate_decision": args.terminal,
        "kind": KIND, "spec_path": SPEC_PATH, "spec_sha256": context["spec_sha256"],
        "toolgap_commit": context["toolgap_commit"], "toolgap_tree": context["toolgap_tree"],
    }
    template["planned_success_artifacts"] = list(required_artifacts(run_dir))
    template["rendered_at"] = now()
    write_exclusive(output, template)
    return 0


def index(run_dir: Path) -> Path:
    output = run_dir / "artifact-index.json"
    if output.exists():
        raise ValueError("artifact index already exists")
    files = []
    for path in sorted(run_dir.rglob("*")):
        item = path.relative_to(run_dir).as_posix()
        if path.is_file() and item not in {"artifact-index.json", "completion-receipt.json"}:
            absolute_regular(path, item)
            files.append({"path": item, "sha256": sha256(path), "size_bytes": path.stat().st_size})
    write_exclusive(output, {"artifact_dir": ".", "files": files})
    return output


def seal(run_dir: Path, terminal: str, reasons: list[str], *, evidence_scope: str) -> None:
    if evidence_scope not in {"formal_runtime", "pre_execution"}:
        raise ValueError("invalid evidence scope")
    write_exclusive(run_dir / "execution-status.json", {
        "attempt_status": terminal, "claim_state": "roadmap", "gate": "G1",
        "evidence_scope": evidence_scope, "kind": KIND, "recorded_at": now(), "reasons": reasons,
    })
    artifact_index = index(run_dir)
    write_exclusive(run_dir / "completion-receipt.json", {
        "artifact_index_sha256": sha256(artifact_index),
        "claim_state": "roadmap",
        "execution_status_sha256": sha256(run_dir / "execution-status.json"),
        "gate": "G1", "gate_decision": terminal, "status": "G1_C_009_TERMINAL_SEALED",
    })


def validate_full_evidence(run_dir: Path, context: dict[str, object]) -> tuple[str, list[str]]:
    manifest = validate_input_manifest(run_dir, context)
    validate_input_oss_receipt(run_dir, manifest)
    validate_bootstrap(run_dir, manifest)
    validate_storage_preflight(run_dir, manifest, context)
    validate_runtime_inputs(run_dir, manifest)
    validate_sglang_provenance(run_dir, manifest)
    exception = load_json(run_dir / "omitted-dependency-exception.json", "omitted dependency exception")
    if exception != {
        "allowed_uninstalled_requirement": "cuda-tile==1.6.0rc5",
        "installed_without_dependency_resolution": "flashinfer_python[cu12]==0.6.17",
        "reason": "CUDA12 wheel route must not source-build cuda-tile on ECS",
    }:
        raise ValueError("omitted dependency exception differs")
    validate_plan(run_dir)
    for path in required_artifacts(run_dir):
        absolute_regular(run_dir / path, f"required artifact {path}")
    validate_cleanup(run_dir)
    for arm in ARMS:
        command = (run_dir / "arms" / f"{arm}.command.txt").read_text(encoding="utf-8")
        if command != SELECTORS[arm] + "\n":
            raise ValueError(f"{arm} selector evidence differs")
    scope = (run_dir / "scope-scan.log").read_text(encoding="utf-8", errors="replace")
    if scope != "scope=clean\n":
        raise ValueError("runtime scope scanner did not prove clean scope")
    try:
        records = json.loads((run_dir / "arm-records.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("arm records are not valid JSON") from error
    if not isinstance(records, list):
        raise ValueError("arm records must be a list")
    individual_records = [
        load_json(run_dir / "arms" / f"{arm}.record.json", f"{arm} record")
        for arm in ARMS
    ]
    if records != individual_records:
        raise ValueError("arm record aggregate differs from individual evidence")
    return classify_records(records)


def finish(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    if any((run_dir / item).exists() for item in TERMINAL_ARTIFACTS):
        raise ValueError("attempt is already sealed")
    context = validate_context(run_dir)
    terminal, reasons = validate_full_evidence(run_dir, context)
    validate_rendered_manifest(run_dir, context, terminal)
    seal(run_dir, terminal, reasons, evidence_scope="formal_runtime")
    verify(argparse.Namespace(run_dir=run_dir))
    return 0


def invalid(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    if any((run_dir / item).exists() for item in TERMINAL_ARTIFACTS):
        raise ValueError("attempt is already sealed")
    context = validate_context(run_dir)
    if not (run_dir / "environment.txt").is_file():
        raise ValueError("invalid terminal requires environment evidence")
    failure, _ = validate_pre_execution_evidence(run_dir, context)
    if args.reason != pre_execution_failure_reason(failure):
        raise ValueError("pre-execution failure reason differs from structured evidence")
    seal(run_dir, "INVALID", [args.reason], evidence_scope="pre_execution")
    verify(argparse.Namespace(run_dir=run_dir))
    return 0


def verify(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    status = load_json(run_dir / "execution-status.json", "execution status")
    if set(status) != {"attempt_status", "claim_state", "evidence_scope", "gate", "kind", "recorded_at", "reasons"}:
        raise ValueError("execution status schema differs")
    if status["attempt_status"] not in {"PASS", "STOP", "INVALID"} or status["claim_state"] != "roadmap" or status["gate"] != "G1" or status["kind"] != KIND or status["evidence_scope"] not in {"formal_runtime", "pre_execution"}:
        raise ValueError("execution status identity differs")
    receipt = load_json(run_dir / "completion-receipt.json", "completion receipt")
    if (
        set(receipt) != {
            "artifact_index_sha256", "claim_state", "execution_status_sha256",
            "gate", "gate_decision", "status",
        }
        or receipt["claim_state"] != "roadmap"
        or receipt["gate"] != "G1"
        or receipt["gate_decision"] != status["attempt_status"]
        or receipt["status"] != "G1_C_009_TERMINAL_SEALED"
        or not valid_digest(receipt["artifact_index_sha256"])
        or not valid_digest(receipt["execution_status_sha256"])
    ):
        raise ValueError("completion receipt differs")
    index_doc = load_json(run_dir / "artifact-index.json", "artifact index")
    if set(index_doc) != {"artifact_dir", "files"} or index_doc["artifact_dir"] != "." or not isinstance(index_doc["files"], list):
        raise ValueError("artifact index schema differs")
    seen = set()
    indexed_paths = []
    for item in index_doc["files"]:
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "size_bytes"}:
            raise ValueError("artifact index entry differs")
        path = item.get("path")
        if (
            not isinstance(path, str) or Path(path).is_absolute()
            or ".." in Path(path).parts or path in seen
            or not valid_digest(item.get("sha256"))
            or type(item.get("size_bytes")) is not int or item["size_bytes"] < 0
        ):
            raise ValueError("unsafe indexed path")
        seen.add(path)
        indexed_paths.append(path)
        candidate = run_dir / path
        absolute_regular(candidate, path)
        if candidate.stat().st_size != item["size_bytes"] or sha256(candidate) != item["sha256"]:
            raise ValueError(f"indexed artifact differs: {path}")
    if indexed_paths != sorted(indexed_paths):
        raise ValueError("artifact index order differs")
    actual = set()
    for candidate in run_dir.rglob("*"):
        path = candidate.relative_to(run_dir).as_posix()
        if candidate.is_symlink():
            raise ValueError(f"sealed attempt contains a symlink: {path}")
        if candidate.is_dir():
            continue
        if not candidate.is_file():
            raise ValueError(f"sealed attempt contains a non-regular artifact: {path}")
        if path not in {"artifact-index.json", "completion-receipt.json"}:
            actual.add(path)
    if seen != actual:
        raise ValueError("artifact index does not equal the sealed regular-file set")
    if "execution-status.json" not in seen:
        raise ValueError("artifact index omits execution status")
    if receipt.get("artifact_index_sha256") != sha256(run_dir / "artifact-index.json") or receipt.get("execution_status_sha256") != sha256(run_dir / "execution-status.json"):
        raise ValueError("completion receipt checksums differ")
    context = validate_context(run_dir)
    if status["evidence_scope"] == "formal_runtime":
        terminal, reasons = validate_full_evidence(run_dir, context)
        if status["attempt_status"] != terminal or status["reasons"] != reasons:
            raise ValueError("execution status differs from offline classification")
        validate_rendered_manifest(run_dir, context, terminal)
    elif status["attempt_status"] != "INVALID":
        raise ValueError("pre-execution evidence cannot produce a Gate terminal")
    else:
        failure, required = validate_pre_execution_evidence(run_dir, context)
        if not required.issubset(seen):
            raise ValueError("artifact index omits pre-execution evidence")
        if status["reasons"] != [pre_execution_failure_reason(failure)]:
            raise ValueError("execution status differs from pre-execution evidence")
    print(f"VERIFIED_G1_C_009_ATTEMPT: {run_dir}")
    return 0


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    render_cmd = commands.add_parser("render")
    render_cmd.add_argument("--template", required=True, type=Path)
    render_cmd.add_argument("--output", required=True, type=Path)
    render_cmd.add_argument("--terminal", required=True, choices=("PASS", "STOP", "INVALID"))
    render_cmd.set_defaults(handler=render)
    finish_cmd = commands.add_parser("finish")
    finish_cmd.add_argument("--run-dir", required=True, type=Path)
    finish_cmd.set_defaults(handler=finish)
    invalid_cmd = commands.add_parser("invalid")
    invalid_cmd.add_argument("--run-dir", required=True, type=Path)
    invalid_cmd.add_argument("--reason", required=True)
    invalid_cmd.set_defaults(handler=invalid)
    verify_cmd = commands.add_parser("verify")
    verify_cmd.add_argument("--run-dir", required=True, type=Path)
    verify_cmd.set_defaults(handler=verify)
    return parser


if __name__ == "__main__":
    arguments = parser().parse_args()
    raise SystemExit(arguments.handler(arguments))
