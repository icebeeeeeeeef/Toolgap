#!/usr/bin/env python3
"""Pre-execution failure-evidence counterexamples for G1-C-007."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("g1_c_007_finalize.py")
SPEC = importlib.util.spec_from_file_location("g1_c_007_finalize", MODULE)
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
        "bundle_id": "G1-C-007",
        "claim_state": "roadmap",
        "created_at": "2026-08-25T00:00:00Z",
        "gate": "G1",
        "kind": "formal_checked_demote_runtime",
        "spec_path": "experiments/g1/SPEC.g1-c-007.md",
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
            "bundle_id": "G1-C-007",
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
            "experiments/g1/commands/00-g1-c-007-bootstrap.sh": {
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
    bootstrap = manifest["static_inputs"]["experiments/g1/commands/00-g1-c-007-bootstrap.sh"]
    objects["bootstrap_script"] = {
        "object_uri": "oss://fixture/00-g1-c-007-bootstrap.sh",
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
        "status": "G1_C_007_TERMINAL_SEALED",
    })


def refresh_receipt_for_index(run_dir: Path) -> None:
    receipt_path = run_dir / "completion-receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["artifact_index_sha256"] = FINALIZE.sha256(run_dir / "artifact-index.json")
    replace_read_only(receipt_path, receipt)


class G1C007PreExecutionTests(unittest.TestCase):
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
