#!/usr/bin/env python3
"""Executable counterexamples for the C016 runtime-venv Ninja binding."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RUNNER = Path(__file__).with_name("20-g1-c-016.sh")


def helper_source() -> str:
    source = RUNNER.read_text(encoding="utf-8")
    return source.split("# BEGIN_C016_NINJA_BINDING_HELPER\n", 1)[1].split(
        "# END_C016_NINJA_BINDING_HELPER\n", 1
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


if __name__ == "__main__":
    unittest.main()
