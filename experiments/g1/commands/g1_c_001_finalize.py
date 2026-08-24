#!/usr/bin/env python3
"""Render, seal, and off-host verify one formal G1-C-001 attempt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BUNDLE_ID = "G1-C-001"
KIND = "formal_checked_demote_runtime"
SPEC_PATH = "experiments/g1/SPEC.g1-c-001.md"
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
BASE_ARTIFACTS = (
    "attempt-context.json", "environment.txt", "input-manifest.json",
    "input-manifest-verify.log", "input-oss-receipt.json", "bootstrap-receipt.json",
    "runtime-wheel.whl", "runtime-wheel-provenance.json", "runtime-wheel-validation.json",
    "cuda-wheelhouse-index.json", "cuda-wheelhouse-validation.json",
    "source-restore.log", "sglang-provenance.json", "model-seed-prepare.log",
    "model-snapshot.json", "resolver-install.log", "installed-distributions.json",
    "omitted-dependency-exception.json", "runtime.env", "arm-plan.json", "arm-records.json", "cleanup.json",
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
        "toolgap_tracked_clean", "toolgap_tree",
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
    return context


def validate_input_manifest(run_dir: Path, context: dict[str, object]) -> dict[str, object]:
    document = load_json(run_dir / "input-manifest.json", "input manifest")
    required = {
        "archives", "identity", "model", "ordinary_dependency_transport",
        "patches", "schema_version", "static_inputs",
    }
    if set(document) != required or document["schema_version"] != 1:
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
            or not isinstance(entry.get("size_bytes"), int) or entry["size_bytes"] < 1
        ):
            raise ValueError(f"invalid input archive: {label}")
    if document["ordinary_dependency_transport"] != {
        "index_url": "http://mirrors.cloud.aliyuncs.com/pypi/simple/",
        "trusted_host": "mirrors.cloud.aliyuncs.com",
    }:
        raise ValueError("ordinary dependency transport differs")
    return document


def validate_input_oss_receipt(run_dir: Path, manifest: dict[str, object]) -> None:
    receipt = load_json(run_dir / "input-oss-receipt.json", "input OSS receipt")
    if set(receipt) != {"schema_version", "identity", "objects"} or receipt["schema_version"] != 1:
        raise ValueError("input OSS receipt schema differs")
    if receipt["identity"] != manifest["identity"]:
        raise ValueError("input OSS receipt identity differs")
    objects = receipt["objects"]
    archives = manifest["archives"]
    expected = set(archives) | {"bootstrap_script"}
    if not isinstance(objects, dict) or set(objects) != expected:
        raise ValueError("input OSS receipt object set differs")
    bootstrap = manifest["static_inputs"].get("experiments/g1/commands/00-g1-c-001-bootstrap.sh")
    if not isinstance(bootstrap, dict):
        raise ValueError("input manifest omits bootstrap binding")
    bindings = {**archives, "bootstrap_script": {"path": "00-g1-c-001-bootstrap.sh", **bootstrap}}
    for label, expected_binding in bindings.items():
        observed = objects[label]
        if (
            not isinstance(observed, dict) or set(observed) != {"object_uri", "sha256", "size_bytes", "version_id"}
            or not isinstance(observed.get("object_uri"), str)
            or not re.fullmatch(r"oss://[^/]+/.+", observed["object_uri"])
            or Path(observed["object_uri"]).name != expected_binding["path"]
            or observed.get("sha256") != expected_binding["sha256"]
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


def validate_runtime_inputs(run_dir: Path, manifest: dict[str, object]) -> None:
    archives = manifest["archives"]
    bindings = {
        "runtime-wheel.whl": archives["runtime_wheel"],
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
        or output_wheel.get("filename") != "sglang-0.0.0.dev2+g734a8e921-cp312-cp312-linux_x86_64.whl"
        or output_wheel.get("sha256") != archives["runtime_wheel"]["sha256"]
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
    validation = load_json(run_dir / "runtime-wheel-validation.json", "runtime wheel validation")
    if validation != {
        "provenance_identity": "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite",
        "runtime_wheel_sha256": archives["runtime_wheel"]["sha256"],
        "runtime_wheel_size_bytes": archives["runtime_wheel"]["size_bytes"],
        "source_rebuild": False,
    }:
        raise ValueError("runtime wheel validation differs")


def validate_plan(run_dir: Path) -> None:
    plan = load_json(run_dir / "arm-plan.json", "arm plan")
    if set(plan) != {"arms", "fresh_process_per_arm", "selector_module"}:
        raise ValueError("arm plan schema differs")
    if plan["fresh_process_per_arm"] is not True or plan["selector_module"] != "test.registered.scripted_runtime.test_toolgap_g1_forced_demote":
        raise ValueError("arm plan does not require fresh formal arms")
    arms = plan["arms"]
    if not isinstance(arms, list) or [item.get("arm") for item in arms if isinstance(item, dict)] != list(ARMS):
        raise ValueError("arm plan differs")
    for item in arms:
        if not isinstance(item, dict) or set(item) != {"arm", "selector"} or item["selector"] != SELECTORS[item["arm"]]:
            raise ValueError("invalid arm plan row")


def record_errors(record: object, expected_arm: str) -> list[str]:
    errors = []
    allowed = RECORD_FIELDS | ({"stock_eviction"} if expected_arm == "stock_eviction_liveness" else set())
    if not isinstance(record, dict) or set(record) != allowed:
        return ["schema"]
    if record["arm"] != expected_arm:
        errors.append("arm")
    qualification = record["component_qualification"]
    if not isinstance(qualification, dict) or qualification.get("components") != ["FULL"] or qualification.get("supports_swa") is not False or not isinstance(qualification.get("page_size"), int) or qualification["page_size"] < 1:
        errors.append("qualification")
    operation = record["operation"]
    if not isinstance(operation, dict) or not isinstance(operation.get("session_id"), str) or not isinstance(operation.get("supplied_generation"), int):
        errors.append("operation")
    target = record["target"]
    if not isinstance(target, dict) or set(target) != TARGET_FIELDS:
        errors.append("target")
    else:
        for key in ("requested_node_ids", "eligible_node_ids", "scheduled_node_ids", "completed_node_ids"):
            if not isinstance(target[key], list) or not all(isinstance(value, int) for value in target[key]):
                errors.append(f"target:{key}")
        if not isinstance(target["before"], list) or not isinstance(target["after"], list):
            errors.append("target:observations")
    counters = record["route_counters"]
    if not isinstance(counters, dict) or set(counters) != COUNTER_FIELDS or any(
        not isinstance(counters.get(key), int) or counters[key] < 0
        for key in COUNTER_FIELDS if key != "physical_demote_node_ids"
    ) or not isinstance(counters.get("physical_demote_node_ids"), list) or not all(isinstance(item, int) for item in counters["physical_demote_node_ids"]):
        errors.append("route_counters")
    capacity = record["capacity"]
    if not isinstance(capacity, dict) or set(capacity) != {"before", "after"}:
        errors.append("capacity")
    else:
        for sample in capacity.values():
            if not isinstance(sample, dict) or set(sample) != {"available_size", "is_not_in_free_group"} or not isinstance(sample["available_size"], int) or sample["available_size"] < 0 or sample["is_not_in_free_group"] is not True:
                errors.append("capacity:sample")
    if record["priority_release"] not in {"RELEASED", "NOT_RELEASED"}:
        errors.append("priority_release")
    if not isinstance(record["freed_device_ids"], list) or not all(isinstance(value, int) for value in record["freed_device_ids"]):
        errors.append("freed_device_ids")
    return errors


def no_physical(record: dict[str, object], *, release: str) -> bool:
    counters = record["route_counters"]
    capacity = record["capacity"]
    return (
        record["priority_release"] == release
        and record["freed_device_ids"] == []
        and counters["physical_demote"] == 0
        and counters["cache_owned_drain"] == 0
        and counters["stock_evict"] == 0
        and capacity["before"]["available_size"] == capacity["after"]["available_size"]
    )


def enabled_passes(record: dict[str, object]) -> bool:
    target, counters, capacity = record["target"], record["route_counters"], record["capacity"]
    before, after = target["before"], target["after"]
    if not before or len(before) != len(after):
        return False
    expected_ids = sorted(
        value for observation in before if isinstance(observation, dict)
        for value in observation.get("device_ids", []) if isinstance(value, int)
    )
    return (
        record["priority_release"] == "RELEASED"
        and record["facade"] == {"disposition": "ACCEPTED", "reason": "ACCEPTED"}
        and bool(expected_ids)
        and sorted(record["freed_device_ids"]) == expected_ids
        and all(isinstance(item, dict) and item.get("host_committed") is True and item.get("device_leaf") is True for item in before)
        and all(isinstance(item, dict) and item.get("live") is True and item.get("device_ids") == [] for item in after)
        and counters["checked_facade"] == 1 and counters["checked_backend"] >= 1
        and counters["physical_demote"] >= 1 and counters["cache_owned_drain"] >= 1
        and counters["stock_evict"] == 0
        and sorted(counters["physical_demote_node_ids"]) == sorted(target["requested_node_ids"])
        and capacity["after"]["available_size"] > capacity["before"]["available_size"]
    )


def bypass_passes(record: dict[str, object]) -> bool:
    return (
        record["facade"] == {"disposition": "BYPASSED", "reason": "PRIORITY_RELEASE_ONLY"}
        and record["route_counters"]["checked_facade"] == 0
        and record["route_counters"]["checked_backend"] == 0
        and no_physical(record, release="RELEASED")
    )


def rejection_passes(record: dict[str, object], reason: str) -> bool:
    counters = record["route_counters"]
    required_release = "NOT_RELEASED" if reason == "STALE_GENERATION" else "RELEASED"
    expected_backend = 0 if reason == "STALE_GENERATION" else 1
    return (
        record["facade"] == {"disposition": "DEFERRED", "reason": reason}
        and record["priority_release"] == required_release
        and counters["checked_facade"] == 1
        and (counters["checked_backend"] == 0 if expected_backend == 0 else counters["checked_backend"] >= 1)
        and no_physical(record, release=required_release)
    )


def liveness_passes(record: dict[str, object]) -> bool:
    stock = record.get("stock_eviction")
    if not isinstance(stock, dict):
        return False
    victims, results = stock.get("victims"), stock.get("results")
    return (
        bypass_passes({**record, "route_counters": {**record["route_counters"], "stock_evict": 0}})
        and isinstance(stock.get("candidate_ids_before"), list) and bool(stock["candidate_ids_before"])
        and isinstance(stock.get("observed_calls"), int) and stock["observed_calls"] > 0
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
    causal_stop = []
    if not enabled_passes(enabled):
        causal_stop.append("enabled lacks checked allocator-visible reclaim")
    if not bypass_passes(bypass):
        causal_stop.append("bypass is not priority-only")
    if causal_stop:
        return "STOP", causal_stop
    failures = []
    for arm, reason in REJECTION_REASONS.items():
        if not rejection_passes(by_arm[arm], reason):
            failures.append(f"{arm} does not preserve rejection contract")
    if not liveness_passes(by_arm["stock_eviction_liveness"]):
        failures.append("stock eviction liveness is absent")
    return ("INVALID", failures) if failures else ("PASS", ["all formal G1 predicates observed"])


def validate_cleanup(run_dir: Path) -> None:
    cleanup = load_json(run_dir / "cleanup.json", "cleanup")
    if set(cleanup) != {"arms", "all_clean"} or cleanup["all_clean"] is not True:
        raise ValueError("cleanup summary differs")
    arms = cleanup["arms"]
    if not isinstance(arms, list) or [item.get("arm") for item in arms if isinstance(item, dict)] != list(ARMS):
        raise ValueError("cleanup arm set differs")
    for item in arms:
        if not isinstance(item, dict) or set(item) != {"arm", "listener_clean", "pgid_clean", "gpu_delta_clean"}:
            raise ValueError("cleanup row differs")
        if not all(item[key] is True for key in ("listener_clean", "pgid_clean", "gpu_delta_clean")):
            raise ValueError("an arm leaked a runtime resource")


def required_artifacts(run_dir: Path) -> tuple[str, ...]:
    dynamic = tuple(
        f"arms/{arm}.{suffix}" for arm in ARMS for suffix in ("command.txt", "log", "record.json", "cleanup.json")
    )
    return BASE_ARTIFACTS + dynamic


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


def seal(run_dir: Path, terminal: str, reasons: list[str]) -> None:
    write_exclusive(run_dir / "execution-status.json", {
        "attempt_status": terminal, "claim_state": "roadmap", "gate": "G1",
        "kind": KIND, "recorded_at": now(), "reasons": reasons,
    })
    artifact_index = index(run_dir)
    write_exclusive(run_dir / "completion-receipt.json", {
        "artifact_index_sha256": sha256(artifact_index),
        "claim_state": "roadmap",
        "execution_status_sha256": sha256(run_dir / "execution-status.json"),
        "gate": "G1", "gate_decision": terminal, "status": "G1_C_001_TERMINAL_SEALED",
    })


def finish(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    if any((run_dir / item).exists() for item in TERMINAL_ARTIFACTS):
        raise ValueError("attempt is already sealed")
    context = validate_context(run_dir)
    manifest = validate_input_manifest(run_dir, context)
    validate_input_oss_receipt(run_dir, manifest)
    validate_bootstrap(run_dir, manifest)
    validate_runtime_inputs(run_dir, manifest)
    exception = load_json(run_dir / "omitted-dependency-exception.json", "omitted dependency exception")
    if exception != {
        "allowed_uninstalled_requirement": "cuda-tile==1.6.0rc5",
        "installed_without_dependency_resolution": "flashinfer_python[cu12]==0.6.17",
        "reason": "CUDA12 wheel route must not source-build cuda-tile on ECS",
    }:
        raise ValueError("omitted dependency exception differs")
    validate_plan(run_dir)
    validate_cleanup(run_dir)
    for path in required_artifacts(run_dir):
        absolute_regular(run_dir / path, f"required artifact {path}")
    scope = (run_dir / "scope-scan.log").read_text(encoding="utf-8", errors="replace")
    if "scope=clean\n" not in scope:
        raise ValueError("scope scanner did not pass")
    records = json.loads((run_dir / "arm-records.json").read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("arm records must be a list")
    individual_records = [
        load_json(run_dir / "arms" / f"{arm}.record.json", f"{arm} record")
        for arm in ARMS
    ]
    if records != individual_records:
        raise ValueError("arm record aggregate differs from individual evidence")
    terminal, reasons = classify_records(records)
    validate_rendered_manifest(run_dir, context, terminal)
    seal(run_dir, terminal, reasons)
    verify(argparse.Namespace(run_dir=run_dir))
    return 0


def invalid(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    if any((run_dir / item).exists() for item in TERMINAL_ARTIFACTS):
        raise ValueError("attempt is already sealed")
    validate_context(run_dir)
    if not (run_dir / "environment.txt").is_file():
        raise ValueError("invalid terminal requires environment evidence")
    seal(run_dir, "INVALID", [args.reason])
    verify(argparse.Namespace(run_dir=run_dir))
    return 0


def verify(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    status = load_json(run_dir / "execution-status.json", "execution status")
    if set(status) != {"attempt_status", "claim_state", "gate", "kind", "recorded_at", "reasons"}:
        raise ValueError("execution status schema differs")
    if status["attempt_status"] not in {"PASS", "STOP", "INVALID"} or status["claim_state"] != "roadmap" or status["gate"] != "G1" or status["kind"] != KIND:
        raise ValueError("execution status identity differs")
    receipt = load_json(run_dir / "completion-receipt.json", "completion receipt")
    if receipt.get("gate_decision") != status["attempt_status"] or receipt.get("status") != "G1_C_001_TERMINAL_SEALED":
        raise ValueError("completion receipt differs")
    index_doc = load_json(run_dir / "artifact-index.json", "artifact index")
    if set(index_doc) != {"artifact_dir", "files"} or index_doc["artifact_dir"] != "." or not isinstance(index_doc["files"], list):
        raise ValueError("artifact index schema differs")
    seen = set()
    for item in index_doc["files"]:
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "size_bytes"}:
            raise ValueError("artifact index entry differs")
        path = item.get("path")
        if not isinstance(path, str) or Path(path).is_absolute() or ".." in Path(path).parts or path in seen:
            raise ValueError("unsafe indexed path")
        seen.add(path)
        candidate = run_dir / path
        absolute_regular(candidate, path)
        if candidate.stat().st_size != item["size_bytes"] or sha256(candidate) != item["sha256"]:
            raise ValueError(f"indexed artifact differs: {path}")
    if "execution-status.json" not in seen:
        raise ValueError("artifact index omits execution status")
    if receipt.get("artifact_index_sha256") != sha256(run_dir / "artifact-index.json") or receipt.get("execution_status_sha256") != sha256(run_dir / "execution-status.json"):
        raise ValueError("completion receipt checksums differ")
    print(f"VERIFIED_G1_C_001_ATTEMPT: {run_dir}")
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
