#!/usr/bin/env python3
"""Pre-execution failure-evidence counterexamples for G1-C-007."""

from __future__ import annotations

import argparse
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
    }
    write_read_only(run_dir / "attempt-context.json", context)
    (run_dir / "environment.txt").write_text("captured\n", encoding="utf-8")
    (run_dir / "environment.txt").chmod(0o444)
    write_read_only(run_dir / "input-manifest.json", {
        "archives": {
            label: {
                "path": f"{label}.bin",
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
        "model": {},
        "ordinary_dependency_transport": {
            "index_url": "http://mirrors.cloud.aliyuncs.com/pypi/simple/",
            "trusted_host": "mirrors.cloud.aliyuncs.com",
        },
        "patches": [],
        "schema_version": 1,
        "static_inputs": {},
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
    write_read_only(run_dir / filename, {
        "available_free_bytes": available,
        "minimum_free_bytes": minimum,
        "path": str(run_dir.resolve()),
        "schema_version": 1,
        "stage": stage,
        "total_bytes": minimum * 2,
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


class G1C007PreExecutionTests(unittest.TestCase):
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
