#!/usr/bin/env python3
"""Full-verifier counterexamples for the C019 external-basis oracle."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[3]
RUNNER_REL = Path("experiments/g1/commands/20-g1-c-019.sh")
BOOTSTRAP_REL = Path("experiments/g1/commands/00-g1-c-019-bootstrap.sh")
VERIFIER_REL = Path("scripts/verify-g1-c-019-bundle.sh")


def normalize_to_c016(source: str) -> str:
    for current, predecessor in (
        ("G1-C-019", "G1-C-016"), ("G1_C_019", "G1_C_016"),
        ("g1-c-019", "g1-c-016"), ("g1_c_019", "g1_c_016"),
        ("c019", "c016"), ("C019", "C016"),
    ):
        source = source.replace(current, predecessor)
    return source


def canonical_runtime_is_unmodified(root: Path) -> bool:
    pairs = (
        (RUNNER_REL, Path("experiments/g1/commands/20-g1-c-016.sh")),
        (BOOTSTRAP_REL, Path("experiments/g1/commands/00-g1-c-016-bootstrap.sh")),
    )
    return all(
        normalize_to_c016((root / current).read_text(encoding="utf-8"))
        == (root / predecessor).read_text(encoding="utf-8")
        for current, predecessor in pairs
    )


def marked_block(source: str, name: str) -> str:
    begin = f"# BEGIN_C019_{name}\n"
    end = f"# END_C019_{name}\n"
    _, remainder = source.split(begin, 1)
    body, _ = remainder.split(end, 1)
    return begin + body + end


def copy_c019_files(destination: Path) -> None:
    roots = (
        ROOT / "experiments/g1",
        ROOT / "scripts",
        ROOT / "upstream/sglang/patches",
        ROOT / "worklog/plans",
    )
    tokens = ("c-019", "c_019", "c019")
    for source_root in roots:
        for source in source_root.rglob("*"):
            if not source.is_file() or not any(token in source.name for token in tokens):
                continue
            relative = source.relative_to(ROOT)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


@contextmanager
def temporary_repo() -> Iterator[Path]:
    with tempfile.TemporaryDirectory(prefix="g1-c-019-oracle-") as directory:
        repo = Path(directory) / "repo"
        subprocess.run(
            ["git", "clone", "-q", "--shared", str(ROOT), str(repo)], check=True
        )
        copy_c019_files(repo)
        yield repo


def run_full_verifier(root: Path, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    clean_env = dict(os.environ)
    for variable in (
        "PYTHON", "BASH_ENV", "ENV", "PYTHONHOME", "PYTHONPATH",
        "PYTHONPYCACHEPREFIX", "CDPATH", "GLOBIGNORE",
        "G1_C_019_VERIFY_RUNNER", "G1_C_019_VERIFY_BOOTSTRAP",
        "G1_C_019_SKIP_ORACLE_MUTATIONS",
    ):
        clean_env.pop(variable, None)
    return subprocess.run(
        ["bash", str(root / VERIFIER_REL)], cwd=root,
        env={**clean_env, **(env or {})}, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )


class OracleMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not canonical_runtime_is_unmodified(ROOT):
            raise AssertionError(
                "C019 mutation suite requires canonical runtime equal to frozen C016"
            )

    def move_after_arm_calls(self, source: str, name: str) -> str:
        block = marked_block(source, name)
        mutation = source.replace(block, "", 1)
        call = 'for arm in "${ARMS[@]}"; do run_arm "$arm" "$(selector_for "$arm")"; done\n'
        self.assertEqual(mutation.count(call), 1)
        return mutation.replace(call, call + block, 1)

    def test_helper_moved_after_all_arm_calls_makes_full_verifier_red(self) -> None:
        with temporary_repo() as repo:
            path = repo / RUNNER_REL
            path.write_text(
                self.move_after_arm_calls(path.read_text(encoding="utf-8"), "NINJA_BINDING_HELPER"),
                encoding="utf-8",
            )
            result = run_full_verifier(repo)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("C019 Ninja helper ordering differs", result.stdout)

    def test_runtime_env_moved_after_all_arm_calls_makes_full_verifier_red(self) -> None:
        with temporary_repo() as repo:
            path = repo / RUNNER_REL
            path.write_text(
                self.move_after_arm_calls(path.read_text(encoding="utf-8"), "NINJA_RUNTIME_ENV"),
                encoding="utf-8",
            )
            result = run_full_verifier(repo)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("C019 Ninja runtime environment ordering differs", result.stdout)

    def test_joint_block_and_inline_digest_rebaseline_makes_full_verifier_red(self) -> None:
        with temporary_repo() as repo:
            runner_path = repo / RUNNER_REL
            source = runner_path.read_text(encoding="utf-8")
            block = marked_block(source, "NINJA_BINDING")
            mutated_block = block.replace(
                "bind_runtime_ninja ",
                "if command -v true >/dev/null; then :; fi\nbind_runtime_ninja ",
                1,
            )
            runner_path.write_text(source.replace(block, mutated_block, 1), encoding="utf-8")
            digest = hashlib.sha256(mutated_block.encode()).hexdigest()
            verifier_path = repo / VERIFIER_REL
            verifier = verifier_path.read_text(encoding="utf-8")
            verifier_path.write_text(
                verifier.replace(
                    "set -euo pipefail\n",
                    f"set -euo pipefail\n# attacker inline Ninja digest: {digest}\n",
                    1,
                ),
                encoding="utf-8",
            )
            result = run_full_verifier(repo)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("runner Ninja block differs from frozen C016: NINJA_BINDING", result.stdout)

    def test_top_level_path_override_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            alternate = Path(directory) / RUNNER_REL.name
            shutil.copy2(ROOT / RUNNER_REL, alternate)
            result = run_full_verifier(
                ROOT, env={"G1_C_019_VERIFY_RUNNER": str(alternate)}
            )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("pre-set interpreter/injection variables are forbidden", result.stdout)

    def test_selective_python_wrapper_is_rejected_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            called = root / "called"
            wrapper = root / "python-wrapper"
            wrapper.write_text(
                "#!/bin/sh\n"
                f"touch {called}\n"
                "if [ \"${1:-}\" = -I ]; then\n"
                "  printf '%s\\n' G1_C_019_INLINE_ORACLE_COMPLETE_C016_EXTERNAL_BASIS\n"
                "  exit 0\n"
                "fi\n"
                "exec /usr/bin/python3 \"$@\"\n",
                encoding="utf-8",
            )
            wrapper.chmod(0o755)
            result = run_full_verifier(ROOT, env={"PYTHON": str(wrapper)})
            self.assertFalse(called.exists(), result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(
            "pre-set interpreter/injection variables are forbidden: PYTHON",
            result.stdout,
        )

    def test_gpu_only_system_pip_branch_makes_full_verifier_red(self) -> None:
        with temporary_repo() as repo:
            path = repo / BOOTSTRAP_REL
            source = path.read_text(encoding="utf-8")
            mutation = source.replace(
                "set -Eeuo pipefail\n",
                "set -Eeuo pipefail\n"
                "if command -v nvidia-smi >/dev/null; then\n"
                "  \"$PYTHON\" -m pip install nvidia-driver-helper\n"
                "fi\n",
                1,
            )
            path.write_text(mutation, encoding="utf-8")
            result = run_full_verifier(repo)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("raw runtime pip-install surface differs: bootstrap", result.stdout)


if __name__ == "__main__":
    unittest.main()
