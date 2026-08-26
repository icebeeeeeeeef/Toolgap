#!/usr/bin/env python3
"""Pre-execution failure-evidence counterexamples for G1-C-013."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("g1_c_013_finalize.py")
SPEC = importlib.util.spec_from_file_location("g1_c_013_finalize", MODULE)
assert SPEC is not None and SPEC.loader is not None
FINALIZE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FINALIZE)


def write_read_only(path: Path, document: object) -> None:
    path.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o444)


def replace_read_only(path: Path, document: object) -> None:
    path.chmod(0o644)
    write_read_only(path, document)


def prepare_run(directory: str) -> Path:
    run_dir = Path(directory)
    context = {
        "attempt_id": "attempt-001",
        "bundle_id": "G1-C-013",
        "claim_state": "roadmap",
        "created_at": "2026-08-25T00:00:00Z",
        "gate": "G1",
        "kind": "formal_checked_demote_runtime",
        "spec_path": "experiments/g1/SPEC.g1-c-013.md",
        "spec_sha256": "1" * 64,
        "toolgap_commit": "2" * 40,
        "toolgap_tracked_clean": True,
        "toolgap_tree": "3" * 40,
        "work_root": str((run_dir / "work").resolve()),
    }
    write_read_only(run_dir / "attempt-context.json", context)
    (run_dir / "environment.txt").write_text("captured\n", encoding="utf-8")
    (run_dir / "environment.txt").chmod(0o444)
    write_read_only(run_dir / "input-manifest.json", {
        "archives": {
            label: {
                "path": FINALIZE.RUNTIME_WHEEL_FILENAME if label == "runtime_wheel" else f"{label}.bin",
                "sha256": str(index) * 64,
                "size_bytes": 1,
            }
            for index, label in enumerate((
                "cuda_wheelhouse",
                "model_snapshot",
                "runtime_wheel",
                "runtime_wheel_provenance",
                "sglang_source_seed",
                "toolgap_source_seed",
            ), start=1)
        },
        "identity": {
            "bundle_id": "G1-C-013",
            "claim_state": "roadmap",
            "gate": "G1",
            "kind": "formal_checked_demote_runtime",
            "sglang_base_commit": "92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2",
            "sglang_base_tree": "25e9bf86d04c27fe380024d9c8c421c3b5b51f3c",
            "toolgap_commit": context["toolgap_commit"],
            "toolgap_remote": "git@example.invalid:Toolgap.git",
            "toolgap_tree": context["toolgap_tree"],
        },
        "model": {
            "inventory_sha256": "a" * 64,
            "repository": "Qwen/Qwen3-0.6B",
            "revision": "c1899de289a04d12100db370d81485cdf75e47ca",
        },
        "ordinary_dependency_transport": {
            "index_url": "http://mirrors.cloud.aliyuncs.com/pypi/simple/",
            "trusted_host": "mirrors.cloud.aliyuncs.com",
        },
        "patches": [{"path": f"patch-{index}.patch", "sha256": str(index) * 64} for index in range(1, 4)],
        "schema_version": 1,
        "static_inputs": {
            "experiments/g1/commands/00-g1-c-013-bootstrap.sh": {
                "sha256": "b" * 64,
                "size_bytes": 1,
            },
        },
        "storage_preflight": {"minimum_free_bytes": FINALIZE.MINIMUM_FREE_BYTES},
    })
    return run_dir


def write_failure(run_dir: Path, phase: str, exit_code: object = 1) -> None:
    write_read_only(run_dir / "pre-execution-failure.json", {
        "exit_code": exit_code,
        "failure_phase": phase,
        "schema_version": 1,
    })


def failure_reason(phase: str, exit_code: int = 1) -> str:
    return f"runner failure at phase {phase}, exit {exit_code}"


def write_preflight(
    run_dir: Path,
    filename: str,
    stage: str,
    *,
    passed: bool,
) -> None:
    minimum = FINALIZE.MINIMUM_FREE_BYTES
    available = minimum if passed else minimum - 1
    context = json.loads((run_dir / "attempt-context.json").read_text(encoding="utf-8"))
    write_read_only(run_dir / filename, {
        "available_free_bytes": available,
        "minimum_free_bytes": minimum,
        "path": context["work_root"],
        "schema_version": 1,
        "stage": stage,
        "total_bytes": minimum * 2,
    })


def write_input_binding_milestone(run_dir: Path) -> None:
    manifest_path = run_dir / "input-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    wheel = run_dir / FINALIZE.RUNTIME_WHEEL_FILENAME
    wheel.write_bytes(b"wheel")
    provenance = {
        "identity": "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite",
        "base_wheel": {
            "filename": FINALIZE.RUNTIME_WHEEL_FILENAME,
            "sha256": "0874acca7b27e45ae39606eb12ee24a5f4cb17cd3791bb60fdccb95c332bf59e",
        },
        "output_wheel": {},
        "patches": [],
    }
    for label, binding in zip(("patch_one", "patch_two", "patch_three"), manifest["patches"]):
        provenance["patches"].append({
            "label": label,
            "path": str((run_dir / binding["path"]).resolve()),
            "sha256": binding["sha256"],
        })
    provenance_path = run_dir / "runtime-wheel-provenance.json"
    provenance_path.write_text(json.dumps(provenance, sort_keys=True) + "\n", encoding="utf-8")
    manifest["archives"]["runtime_wheel"] = {
        "path": wheel.name,
        "sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
        "size_bytes": wheel.stat().st_size,
    }
    manifest["archives"]["runtime_wheel_provenance"] = {
        "path": provenance_path.name,
        "sha256": hashlib.sha256(provenance_path.read_bytes()).hexdigest(),
        "size_bytes": provenance_path.stat().st_size,
    }
    provenance["output_wheel"] = {
        "filename": wheel.name,
        "sha256": manifest["archives"]["runtime_wheel"]["sha256"],
        "size_bytes": wheel.stat().st_size,
    }
    provenance_path.write_text(json.dumps(provenance, sort_keys=True) + "\n", encoding="utf-8")
    manifest["archives"]["runtime_wheel_provenance"].update({
        "sha256": hashlib.sha256(provenance_path.read_bytes()).hexdigest(),
        "size_bytes": provenance_path.stat().st_size,
    })
    replace_read_only(manifest_path, manifest)
    wheel.chmod(0o444)
    provenance_path.chmod(0o444)
    objects = {}
    for label, binding in manifest["archives"].items():
        objects[label] = {
            "object_uri": f"oss://fixture/{binding['path']}",
            "sha256": binding["sha256"],
            "size_bytes": binding["size_bytes"],
            "version_id": "fixture-version",
        }
    bootstrap = manifest["static_inputs"]["experiments/g1/commands/00-g1-c-013-bootstrap.sh"]
    objects["bootstrap_script"] = {
        "object_uri": "oss://fixture/00-g1-c-013-bootstrap.sh",
        "sha256": bootstrap["sha256"],
        "size_bytes": bootstrap["size_bytes"],
        "version_id": "fixture-version",
    }
    write_read_only(run_dir / "input-oss-receipt.json", {
        "schema_version": 1,
        "identity": manifest["identity"],
        "objects": objects,
    })
    write_read_only(run_dir / "bootstrap-receipt.json", {
        "input_manifest_path": str(manifest_path.resolve()),
        "input_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "toolgap_checkout": str(run_dir.resolve()),
        "toolgap_commit": manifest["identity"]["toolgap_commit"],
        "toolgap_remote": manifest["identity"]["toolgap_remote"],
        "toolgap_seed_path": str((run_dir / "toolgap_source_seed.bin").resolve()),
        "toolgap_seed_sha256": manifest["archives"]["toolgap_source_seed"]["sha256"],
        "toolgap_tree": manifest["identity"]["toolgap_tree"],
    })
    (run_dir / "input-manifest-verify.log").write_text("input_manifest=verified\n", encoding="utf-8")
    (run_dir / "input-manifest-verify.log").chmod(0o444)


def write_source_restore_milestone(run_dir: Path) -> None:
    manifest = json.loads((run_dir / "input-manifest.json").read_text(encoding="utf-8"))
    (run_dir / "source-restore.log").write_text("restored\n", encoding="utf-8")
    (run_dir / "source-restore.log").chmod(0o444)
    write_read_only(run_dir / "sglang-provenance.json", {
        "base_commit": manifest["identity"]["sglang_base_commit"],
        "base_tree": manifest["identity"]["sglang_base_tree"],
        "patched_commit": "c" * 40,
        "patched_tree": "d" * 40,
        "patches": [{
            "label": f"patch_{index}",
            "path": str((run_dir / binding["path"]).resolve()),
            "sha256": binding["sha256"],
        } for index, binding in enumerate(manifest["patches"], start=1)],
    })


def write_model_milestone(run_dir: Path) -> None:
    context = json.loads((run_dir / "attempt-context.json").read_text(encoding="utf-8"))
    manifest = json.loads((run_dir / "input-manifest.json").read_text(encoding="utf-8"))
    (run_dir / "model-seed-prepare.log").write_text("prepared\n", encoding="utf-8")
    (run_dir / "model-seed-prepare.log").chmod(0o444)
    write_read_only(run_dir / "model-snapshot.json", {
        "archive_sha256": manifest["archives"]["model_snapshot"]["sha256"],
        "file_count": 1,
        "inventory_sha256": manifest["model"]["inventory_sha256"],
        "model_root": str(Path(context["work_root"]) / "model-input/model-snapshot"),
        "repository": manifest["model"]["repository"],
        "revision": manifest["model"]["revision"],
        "total_bytes": 1,
    })


def write_plan(run_dir: Path) -> None:
    write_read_only(run_dir / "arm-plan.json", {
        "arms": [
            {"arm": arm, "selector": FINALIZE.SELECTORS[arm]}
            for arm in FINALIZE.ARMS
        ],
        "fresh_process_per_arm": True,
        "selector_module": "test_toolgap_g1_forced_demote",
    })


def write_resolver_milestone(run_dir: Path) -> None:
    context = json.loads((run_dir / "attempt-context.json").read_text(encoding="utf-8"))
    manifest = json.loads((run_dir / "input-manifest.json").read_text(encoding="utf-8"))
    for name, content in (
        ("resolver-install.log", "resolved\n"),
        ("ordinary-requirements.txt", "packaging\n"),
        ("arm-runner.py", "raise SystemExit(0)\n"),
    ):
        path = run_dir / name
        path.write_text(content, encoding="utf-8")
        path.chmod(0o444)
    write_read_only(run_dir / "runtime-wheel-validation.json", {
        "provenance_identity": "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite",
        "runtime_wheel_filename": FINALIZE.RUNTIME_WHEEL_FILENAME,
        "runtime_wheel_sha256": manifest["archives"]["runtime_wheel"]["sha256"],
        "runtime_wheel_size_bytes": manifest["archives"]["runtime_wheel"]["size_bytes"],
        "source_rebuild": False,
    })
    wheels = {
        label: {"path": f"{label}.whl", "sha256": str(index) * 64, "size_bytes": 1}
        for index, label in enumerate((
            "sglang_kernel", "sgl_deep_ep", "sgl_deep_gemm",
            "torch", "torchvision", "torchaudio",
        ), start=1)
    }
    wheelhouse_index = run_dir / "cuda-wheelhouse-index.json"
    write_read_only(wheelhouse_index, {"schema_version": 1, "wheels": wheels})
    write_read_only(run_dir / "cuda-wheelhouse-validation.json", {
        "archive_sha256": manifest["archives"]["cuda_wheelhouse"]["sha256"],
        "archive_size_bytes": manifest["archives"]["cuda_wheelhouse"]["size_bytes"],
        "index_sha256": FINALIZE.sha256(wheelhouse_index),
        "wheels": wheels,
    })
    work_root = Path(context["work_root"])
    modules = {
        label: {
            "hash_matches_source": True,
            "installed_under_root": True,
            "outside_source_checkout": True,
        }
        for label in (
            "session_ref_tracker", "unified_tree_core",
            "unified_tree_core_interface", "unified_radix_cache",
        )
    }
    write_read_only(run_dir / "sglang-package-provenance.json", {
        "expected_interpreter": str(work_root / "runtime-venv/bin/python"),
        "install_root": str(work_root / "runtime-venv"),
        "interpreter": str(work_root / "runtime-venv/bin/python"),
        "interpreter_matches": True,
        "modules": modules,
        "package_path": str(work_root / "runtime-venv/site-packages/sglang"),
        "package_under_install_root": True,
        "passed": True,
        "source_root": str(work_root / "sglang"),
        "sys_path": [],
    })
    distributions = [
        {"name": name, "version": "1"}
        for name in (
            "sglang", "sglang-kernel", "sgl-deep-ep", "sgl-deep-gemm",
            "torch", "torchvision", "torchaudio", "flashinfer-python",
        )
    ]
    write_read_only(run_dir / "installed-distributions.json", distributions)
    write_read_only(run_dir / "omitted-dependency-exception.json", {
        "allowed_uninstalled_requirement": "cuda-tile==1.6.0rc5",
        "installed_without_dependency_resolution": "flashinfer_python[cu12]==0.6.17",
        "reason": "CUDA12 wheel route must not source-build cuda-tile on ECS",
    })
    write_plan(run_dir)
    runtime_env = "\n".join((
        "HF_HUB_OFFLINE=1",
        "TRANSFORMERS_OFFLINE=1",
        "SGLANG_ENABLE_UNIFIED_RADIX_TREE=1",
        f"TOOLGAP_G1_MODEL_PATH={work_root / 'model-input/model-snapshot'}",
        f"TREATMENT={work_root / 'sglang'}",
        f"RUNTIME_PYTHON={work_root / 'runtime-venv/bin/python'}",
        "ORDINARY_PYPI_INDEX=http://mirrors.cloud.aliyuncs.com/pypi/simple/",
    )) + "\n"
    (run_dir / "runtime.env").write_text(runtime_env, encoding="utf-8")
    (run_dir / "runtime.env").chmod(0o444)


def write_formal_arms_milestone(run_dir: Path) -> None:
    arms_root = run_dir / "arms"
    arms_root.mkdir(exist_ok=True)
    records = []
    cleanup_rows = []
    for index, arm in enumerate(FINALIZE.ARMS, start=1):
        pid = 1000 + index
        record = {
            "arm": arm,
            "operation": {},
            "target": {},
            "component_qualification": {},
            "priority_release": "RELEASED",
            "released_component_leaves": 0,
            "facade": {},
            "nodes": [],
            "freed_device_ids": [],
            "route_counters": {},
            "capacity": {},
            "host_pool": {},
        }
        if arm == "stock_eviction_liveness":
            record["stock_eviction"] = {}
        records.append(record)
        row = {
            "arm": arm, "pid": pid, "pgid": pid,
            "listener_clean": True, "pgid_clean": True, "gpu_delta_clean": True,
        }
        cleanup_rows.append(row)
        files = {
            "command.txt": FINALIZE.SELECTORS[arm] + "\n",
            "log": "completed\n",
            "pid": f"{pid}\n",
            "pgid": f"{pid}\n",
            "gpu-before.txt": "",
            "gpu-during.txt": "",
            "gpu-attributable.txt": "",
            "gpu-after.txt": "",
            "gpu-leaked.txt": "",
            "listeners-before.txt": "",
            "listeners-after.txt": "",
            "listeners-leaked.txt": "",
            "process-group-after.txt": "",
        }
        for suffix, content in files.items():
            path = arms_root / f"{arm}.{suffix}"
            path.write_text(content, encoding="utf-8")
            path.chmod(0o444)
        write_read_only(arms_root / f"{arm}.record.json", record)
        write_read_only(arms_root / f"{arm}.cleanup.json", row)
        write_read_only(arms_root / f"{arm}.launcher-handshake.json", {
            "pgid": pid, "pid": pid, "schema_version": 1,
        })
        write_read_only(arms_root / f"{arm}.launcher-ack.json", {
            "pid": pid, "schema_version": 1,
        })
        write_read_only(arms_root / f"{arm}.gpu-samples.json", {
            "arm_pid": pid,
            "poll_seconds": 0.25,
            "samples": [{"captured_at": "2026-08-25T00:00:00Z", "pids": []}],
        })
    write_read_only(run_dir / "arm-records.json", records)
    write_read_only(run_dir / "cleanup.json", {"all_clean": True, "arms": cleanup_rows})


def write_scope_milestone(run_dir: Path) -> None:
    (run_dir / "scope-scan.log").write_text("scope=clean\n", encoding="utf-8")
    (run_dir / "scope-scan.log").chmod(0o444)


def reseal_index(run_dir: Path) -> None:
    for name in ("artifact-index.json", "completion-receipt.json"):
        path = run_dir / name
        path.chmod(0o644)
        path.unlink()
    artifact_index = FINALIZE.index(run_dir)
    FINALIZE.write_exclusive(run_dir / "completion-receipt.json", {
        "artifact_index_sha256": FINALIZE.sha256(artifact_index),
        "claim_state": "roadmap",
        "execution_status_sha256": FINALIZE.sha256(run_dir / "execution-status.json"),
        "gate": "G1",
        "gate_decision": "INVALID",
        "status": "G1_C_013_TERMINAL_SEALED",
    })


def refresh_receipt_for_index(run_dir: Path) -> None:
    receipt_path = run_dir / "completion-receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["artifact_index_sha256"] = FINALIZE.sha256(run_dir / "artifact-index.json")
    replace_read_only(receipt_path, receipt)


class G1C007PreExecutionTests(unittest.TestCase):
    def test_plan_binds_importable_selector_module_stem(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            write_plan(run_dir)
            FINALIZE.validate_plan(run_dir)
            plan_path = run_dir / "arm-plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            replace_read_only(plan_path, {
                **plan,
                "selector_module": "test.registered.scripted_runtime.test_toolgap_g1_forced_demote",
            })
            with self.assertRaises(ValueError):
                FINALIZE.validate_plan(run_dir)

    def test_render_failure_seals_without_manifest_and_replays_clean_scope(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = prepare_run(directory)
            write_failure(run_dir, "render")
            write_preflight(run_dir, "storage-preflight-source-restore.json", "source_restore", passed=True)
            write_preflight(run_dir, "storage-preflight-resolver.json", "resolver", passed=True)
            write_input_binding_milestone(run_dir)
            write_source_restore_milestone(run_dir)
            write_model_milestone(run_dir)
            write_resolver_milestone(run_dir)
            write_formal_arms_milestone(run_dir)
            write_scope_milestone(run_dir)
            self.assertEqual(FINALIZE.invalid(argparse.Namespace(
                run_dir=run_dir,
                reason=failure_reason("render"),
            )), 0)
            self.assertFalse((run_dir / "manifest.json").exists())
            handshake = run_dir / "arms/enabled.launcher-handshake.json"
            handshake_document = json.loads(handshake.read_text(encoding="utf-8"))
            handshake.chmod(0o644)
            write_read_only(handshake, {**handshake_document, "pgid": handshake_document["pgid"] + 1})
            reseal_index(run_dir)
            with self.assertRaises(ValueError):
                FINALIZE.verify(argparse.Namespace(run_dir=run_dir))
            handshake.chmod(0o644)
            write_read_only(handshake, handshake_document)
            reseal_index(run_dir)
            self.assertEqual(FINALIZE.verify(argparse.Namespace(run_dir=run_dir)), 0)
            scope = run_dir / "scope-scan.log"
            scope.chmod(0o644)
            scope.write_text("scope=invalid\n", encoding="utf-8")
            scope.chmod(0o444)
            reseal_index(run_dir)
            with self.assertRaises(ValueError):
                FINALIZE.verify(argparse.Namespace(run_dir=run_dir))

    def test_unindexed_regular_file_cannot_verify(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = prepare_run(directory)
            write_failure(run_dir, "input_binding")
            FINALIZE.invalid(argparse.Namespace(run_dir=run_dir, reason=failure_reason("input_binding")))
            (run_dir / "unindexed.txt").write_text("extra\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                FINALIZE.verify(argparse.Namespace(run_dir=run_dir))

    def test_unindexed_symlink_cannot_verify(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = prepare_run(directory)
            write_failure(run_dir, "input_binding")
            FINALIZE.invalid(argparse.Namespace(run_dir=run_dir, reason=failure_reason("input_binding")))
            (run_dir / "alias").symlink_to("environment.txt")
            with self.assertRaises(ValueError):
                FINALIZE.verify(argparse.Namespace(run_dir=run_dir))

    def test_reordered_index_cannot_verify_with_refreshed_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = prepare_run(directory)
            write_failure(run_dir, "input_binding")
            FINALIZE.invalid(argparse.Namespace(run_dir=run_dir, reason=failure_reason("input_binding")))
            index_path = run_dir / "artifact-index.json"
            index_doc = json.loads(index_path.read_text(encoding="utf-8"))
            index_doc["files"].reverse()
            replace_read_only(index_path, index_doc)
            refresh_receipt_for_index(run_dir)
            with self.assertRaises(ValueError):
                FINALIZE.verify(argparse.Namespace(run_dir=run_dir))

    def test_missing_failure_record_cannot_seal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = prepare_run(directory)
            with self.assertRaises(ValueError):
                FINALIZE.invalid(argparse.Namespace(run_dir=run_dir, reason="runner failed"))
            self.assertFalse((run_dir / "execution-status.json").exists())

    def test_missing_failure_record_cannot_verify(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = prepare_run(directory)
            write_failure(run_dir, "input_binding")
            FINALIZE.invalid(argparse.Namespace(run_dir=run_dir, reason=failure_reason("input_binding")))
            (run_dir / "pre-execution-failure.json").unlink()
            reseal_index(run_dir)
            with self.assertRaises(ValueError):
                FINALIZE.verify(argparse.Namespace(run_dir=run_dir))

    def test_tampered_failure_record_cannot_verify_even_with_fresh_index(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = prepare_run(directory)
            write_failure(run_dir, "input_binding")
            FINALIZE.invalid(argparse.Namespace(run_dir=run_dir, reason=failure_reason("input_binding")))
            evidence = run_dir / "pre-execution-failure.json"
            evidence.chmod(0o644)
            write_read_only(evidence, {
                "exit_code": "1",
                "failure_phase": "input_binding",
                "schema_version": 1,
            })
            reseal_index(run_dir)
            with self.assertRaises(ValueError):
                FINALIZE.verify(argparse.Namespace(run_dir=run_dir))

    def test_wrong_stage_preflight_cannot_seal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = prepare_run(directory)
            write_failure(run_dir, "source_restore")
            write_preflight(
                run_dir,
                "storage-preflight-source-restore.json",
                "resolver",
                passed=False,
            )
            with self.assertRaises(ValueError):
                FINALIZE.invalid(argparse.Namespace(run_dir=run_dir, reason=failure_reason("source_restore")))

    def test_preflight_path_must_match_context_work_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = prepare_run(directory)
            write_failure(run_dir, "source_restore")
            write_preflight(
                run_dir,
                "storage-preflight-source-restore.json",
                "source_restore",
                passed=False,
            )
            preflight = run_dir / "storage-preflight-source-restore.json"
            preflight.chmod(0o644)
            document = json.loads(preflight.read_text(encoding="utf-8"))
            document["path"] = str((run_dir / "different-work").resolve())
            write_read_only(preflight, document)
            with self.assertRaises(ValueError):
                FINALIZE.invalid(argparse.Namespace(
                    run_dir=run_dir,
                    reason=failure_reason("source_restore"),
                ))

    def test_earlier_failed_preflight_cannot_be_hidden_by_later_phase(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = prepare_run(directory)
            write_failure(run_dir, "formal_arms")
            write_preflight(
                run_dir,
                "storage-preflight-source-restore.json",
                "source_restore",
                passed=True,
            )
            write_preflight(
                run_dir,
                "storage-preflight-resolver.json",
                "resolver",
                passed=False,
            )
            with self.assertRaises(ValueError):
                FINALIZE.invalid(argparse.Namespace(run_dir=run_dir, reason=failure_reason("formal_arms")))

    def test_fake_formal_arms_phase_without_completed_milestones_cannot_seal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = prepare_run(directory)
            write_failure(run_dir, "formal_arms")
            write_preflight(
                run_dir,
                "storage-preflight-source-restore.json",
                "source_restore",
                passed=True,
            )
            write_preflight(
                run_dir,
                "storage-preflight-resolver.json",
                "resolver",
                passed=True,
            )
            with self.assertRaises(ValueError):
                FINALIZE.invalid(argparse.Namespace(
                    run_dir=run_dir,
                    reason=failure_reason("formal_arms"),
                ))

    def test_current_preflight_may_record_insufficient_space(self) -> None:
        cases = (
            ("source_restore", (("storage-preflight-source-restore.json", "source_restore", False),)),
            ("resolver", (
                ("storage-preflight-source-restore.json", "source_restore", True),
                ("storage-preflight-resolver.json", "resolver", False),
            )),
        )
        for phase, preflights in cases:
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as directory:
                run_dir = prepare_run(directory)
                write_failure(run_dir, phase)
                for filename, stage, passed in preflights:
                    write_preflight(run_dir, filename, stage, passed=passed)
                write_input_binding_milestone(run_dir)
                if phase == "resolver":
                    write_source_restore_milestone(run_dir)
                    write_model_milestone(run_dir)
                self.assertEqual(
                    FINALIZE.invalid(argparse.Namespace(run_dir=run_dir, reason=failure_reason(phase))),
                    0,
                )

    def test_future_preflight_record_cannot_appear_before_its_phase(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = prepare_run(directory)
            write_failure(run_dir, "model")
            write_preflight(
                run_dir,
                "storage-preflight-source-restore.json",
                "source_restore",
                passed=True,
            )
            write_preflight(
                run_dir,
                "storage-preflight-resolver.json",
                "resolver",
                passed=True,
            )
            with self.assertRaises(ValueError):
                FINALIZE.invalid(argparse.Namespace(run_dir=run_dir, reason=failure_reason("model")))


if __name__ == "__main__":
    unittest.main()
