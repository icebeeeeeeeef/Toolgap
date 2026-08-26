#!/usr/bin/env python3
"""Counterexample for GPU PIDs which appear after the former five-second window."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("g1_c_013_gpu_sampler.py")
SPEC = importlib.util.spec_from_file_location("g1_c_013_gpu_sampler", MODULE)
assert SPEC is not None and SPEC.loader is not None
SAMPLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SAMPLER)


class G1C001GpuSamplerTests(unittest.TestCase):
    def test_delayed_gpu_pid_after_five_samples_is_retained(self) -> None:
        samples = iter([[], [], [], [], [], [], [991], [991]])
        liveness = iter([True, True, True, True, True, True, True, False])
        observed = SAMPLER.capture_until_arm_exit(
            123,
            0.25,
            read_pids=lambda: next(samples),
            is_alive=lambda _pid: next(liveness),
            sleep=lambda _seconds: None,
            clock=lambda: "2026-08-25T00:00:00Z",
        )
        self.assertEqual([sample["pids"] for sample in observed][6], [991])
        self.assertEqual(
            sorted({pid for sample in observed for pid in sample["pids"]}), [991]
        )


if __name__ == "__main__":
    unittest.main()
