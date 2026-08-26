#!/usr/bin/env python3
"""Full-verifier mutations for C017 ordering and privilege escapes."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERIFIER = ROOT / "scripts/verify-g1-c-017-bundle.sh"
RUNNER = ROOT / "experiments/g1/commands/20-g1-c-017.sh"
BOOTSTRAP = ROOT / "experiments/g1/commands/00-g1-c-017-bootstrap.sh"


def marked_block(source: str, name: str) -> str:
    begin = f"# BEGIN_C017_{name}\n"
    end = f"# END_C017_{name}\n"
    prefix, remainder = source.split(begin, 1)
    body, suffix = remainder.split(end, 1)
    del prefix, suffix
    return begin + body + end


def run_full_verifier(**overrides: str) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "G1_C_017_SKIP_ORACLE_MUTATIONS": "1",
        **overrides,
    }
    return subprocess.run(
        ["bash", str(VERIFIER)], cwd=ROOT, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )


class OracleMutationTests(unittest.TestCase):
    def test_binding_moved_after_all_run_arm_calls_makes_full_verifier_red(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        binding = marked_block(source, "NINJA_BINDING")
        mutation = source.replace(binding, "", 1)
        call = 'for arm in "${ARMS[@]}"; do run_arm "$arm" "$(selector_for "$arm")"; done\n'
        self.assertEqual(mutation.count(call), 1)
        mutation = mutation.replace(call, call + binding, 1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / RUNNER.name
            path.write_text(mutation, encoding="utf-8")
            result = run_full_verifier(G1_C_017_VERIFY_RUNNER=str(path))
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("C017 Ninja binding ordering differs", result.stdout)

    def test_gpu_conditional_package_install_makes_full_verifier_red(self) -> None:
        source = BOOTSTRAP.read_text(encoding="utf-8")
        mutation = source.replace(
            "set -Eeuo pipefail\n",
            "set -Eeuo pipefail\n"
            "if command -v nvidia-smi >/dev/null; then\n"
            "  apt install -y linux-modules-nvidia-*\n"
            "fi\n",
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / BOOTSTRAP.name
            path.write_text(mutation, encoding="utf-8")
            result = run_full_verifier(G1_C_017_VERIFY_BOOTSTRAP=str(path))
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("runtime identity differs: bootstrap", result.stdout)


if __name__ == "__main__":
    unittest.main()
