#!/usr/bin/env python3
"""Executable counterexamples for the C018 runtime-venv Ninja binding."""

from __future__ import annotations

import json
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RUNNER = Path(__file__).with_name("20-g1-c-018.sh")
PRE_EXECUTION_TESTS = Path(__file__).with_name("test_g1_c_018_pre_execution.py")
PRE_EXECUTION_SPEC = importlib.util.spec_from_file_location(
    "g1_c_018_pre_execution_fixture", PRE_EXECUTION_TESTS
)
assert PRE_EXECUTION_SPEC is not None and PRE_EXECUTION_SPEC.loader is not None
PRE_EXECUTION = importlib.util.module_from_spec(PRE_EXECUTION_SPEC)
PRE_EXECUTION_SPEC.loader.exec_module(PRE_EXECUTION)


def helper_source() -> str:
    source = RUNNER.read_text(encoding="utf-8")
    return source.split("# BEGIN_C018_NINJA_BINDING_HELPER\n", 1)[1].split(
        "# END_C018_NINJA_BINDING_HELPER\n", 1
    )[0]


def binding_source() -> str:
    source = RUNNER.read_text(encoding="utf-8")
    return source.split("# BEGIN_C018_NINJA_BINDING\n", 1)[1].split(
        "# END_C018_NINJA_BINDING\n", 1
    )[0]


class NinjaBindingTests(unittest.TestCase):
    def prepare(self, root: Path, *, with_runtime_ninja: bool = True) -> tuple[Path, dict[str, str]]:
        runtime = root / "runtime-venv"
        cuda = root / "cuda"
        fake_host = root / "fake-host"
        for directory in (runtime / "bin", cuda / "bin", fake_host):
            directory.mkdir(parents=True)
        (runtime / "bin/python").symlink_to(sys.executable)
        if with_runtime_ninja:
            ninja = runtime / "bin/ninja"
            ninja.write_text("#!/usr/bin/env bash\nprintf 'runtime-ninja\\n'\n", encoding="utf-8")
            ninja.chmod(0o755)
        shadow = fake_host / "ninja"
        shadow.write_text("#!/usr/bin/env bash\nprintf 'shadow-ninja\\n'\n", encoding="utf-8")
        shadow.chmod(0o755)
        harness = root / "harness.sh"
        harness.write_text(
            "#!/usr/bin/env bash\nset -Eeuo pipefail\n"
            "die() { printf '%s\\n' \"$*\" >&2; exit 2; }\n"
            + helper_source()
            + "bind_runtime_ninja \"$OUTPUT\" \"$RUNTIME\" \"$CUDA\"\n",
            encoding="utf-8",
        )
        harness.chmod(0o755)
        env = {
            **os.environ,
            "PATH": f"{fake_host}:{os.environ.get('PATH', '/usr/bin:/bin')}",
            "OUTPUT": str(root / "ninja-runtime.json"),
            "RUNTIME": str(runtime),
            "CUDA": str(cuda),
            "PYTHON": sys.executable,
        }
        return harness, env

    def test_shadowing_host_path_cannot_select_fake_ninja(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            harness, env = self.prepare(root)
            result = subprocess.run(
                ["bash", str(harness)], env=env, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            evidence = json.loads((root / "ninja-runtime.json").read_text(encoding="utf-8"))
            expected = str(root / "runtime-venv/bin/ninja")
            self.assertEqual(evidence["command_resolution"], expected)
            self.assertEqual(evidence["python_resolution"], expected)
            executed = subprocess.check_output(
                ["ninja"], env={**env, "PATH": evidence["arm_path"]}, text=True
            )
            self.assertEqual(executed, "runtime-ninja\n")

    def test_missing_runtime_ninja_is_pre_execution_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness, env = self.prepare(Path(directory), with_runtime_ninja=False)
            result = subprocess.run(
                ["bash", str(harness)], env=env, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing executable runtime-venv Ninja", result.stderr)

    def test_missing_ninja_stops_complete_pre_arm_transition_and_seals_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "run").mkdir()
            run_dir = PRE_EXECUTION.prepare_run(str(root / "run"))
            context_path = run_dir / "attempt-context.json"
            context = json.loads(context_path.read_text(encoding="utf-8"))
            context["work_root"] = str((root / "work").resolve())
            PRE_EXECUTION.replace_read_only(context_path, context)
            PRE_EXECUTION.write_input_binding_milestone(run_dir)
            PRE_EXECUTION.write_preflight(
                run_dir, "storage-preflight-source-restore.json", "source_restore", passed=True
            )
            PRE_EXECUTION.write_source_restore_milestone(run_dir)
            PRE_EXECUTION.write_model_milestone(run_dir)
            PRE_EXECUTION.write_preflight(
                run_dir, "storage-preflight-resolver.json", "resolver", passed=True
            )

            work_root = root / "work"
            runtime = work_root / "runtime-venv"
            cuda = root / "cuda"
            (runtime / "bin").mkdir(parents=True)
            (cuda / "bin").mkdir(parents=True)
            (run_dir / "arms").mkdir()
            (runtime / "bin/python").symlink_to(sys.executable)
            harness = root / "complete-pre-arm-transition.sh"
            harness.write_text(
                "#!/usr/bin/env bash\nset -Eeuo pipefail\n"
                "die() { printf '%s\\n' \"$*\" >&2; exit 2; }\n"
                f"PYTHON={sys.executable!s}\n"
                f"RUN_DIR={run_dir!s}\n"
                f"RUNTIME_VENV={runtime!s}\n"
                f"CUDA_HOME={cuda!s}\n"
                + helper_source()
                + binding_source()
                + "PHASE=\"formal_arms\"\n"
                + "printf selector >\"$RUN_DIR/arms/enabled.command.txt\"\n"
                + "printf 123 >\"$RUN_DIR/arms/enabled.pid\"\n"
                + "printf handshake >\"$RUN_DIR/arms/enabled.launcher-handshake.json\"\n"
                + "printf launched >\"$RUN_DIR/arms/enabled.log\"\n",
                encoding="utf-8",
            )
            harness.chmod(0o755)
            result = subprocess.run(
                ["bash", str(harness)], text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing executable runtime-venv Ninja", result.stderr)
            PRE_EXECUTION.write_failure(run_dir, "resolver", result.returncode)
            self.assertEqual(
                PRE_EXECUTION.FINALIZE.invalid(
                    PRE_EXECUTION.argparse.Namespace(
                        run_dir=run_dir,
                        reason=PRE_EXECUTION.failure_reason("resolver", result.returncode),
                    )
                ),
                0,
            )
            self.assertEqual(
                PRE_EXECUTION.FINALIZE.verify(
                    PRE_EXECUTION.argparse.Namespace(run_dir=run_dir)
                ),
                0,
            )
            status = json.loads((run_dir / "execution-status.json").read_text(encoding="utf-8"))
            failure = json.loads(
                (run_dir / "pre-execution-failure.json").read_text(encoding="utf-8")
            )
            self.assertEqual(status["attempt_status"], "INVALID")
            self.assertEqual(status["evidence_scope"], "pre_execution")
            self.assertEqual(failure["failure_phase"], "resolver")
            self.assertFalse((run_dir / "ninja-runtime.json").exists())
            for pattern in ("*.command.txt", "*.pid", "*.launcher-*", "*.log"):
                self.assertEqual(list((run_dir / "arms").glob(pattern)), [], pattern)


if __name__ == "__main__":
    unittest.main()
