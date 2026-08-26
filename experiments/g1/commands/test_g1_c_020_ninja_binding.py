#!/usr/bin/env python3
"""Direct runtime-venv Ninja admission checks for the C020 runner."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RUNNER = Path(__file__).with_name("20-g1-c-020.sh")


def binding_helper() -> str:
    source = RUNNER.read_text(encoding="utf-8")
    return source.split("# BEGIN_C020_NINJA_BINDING_HELPER\n", 1)[1].split(
        "# END_C020_NINJA_BINDING_HELPER\n", 1
    )[0]


def run_binding(root: Path, *, runtime_ninja: bool) -> subprocess.CompletedProcess[str]:
    runtime, cuda, host = root / "runtime-venv", root / "cuda", root / "host-bin"
    for directory in (runtime / "bin", cuda / "bin", host):
        directory.mkdir(parents=True)
    (runtime / "bin/python").symlink_to(sys.executable)
    if runtime_ninja:
        ninja = runtime / "bin/ninja"
        ninja.write_text("#!/usr/bin/env bash\nprintf '1.13.0\\n'\n", encoding="utf-8")
        ninja.chmod(0o755)
    shadow = host / "ninja"
    shadow.write_text("#!/usr/bin/env bash\nprintf 'host-ninja\\n'\n", encoding="utf-8")
    shadow.chmod(0o755)
    harness = root / "bind-ninja.sh"
    harness.write_text(
        "#!/usr/bin/env bash\nset -Eeuo pipefail\n"
        "die() { printf '%s\\n' \"$*\" >&2; exit 2; }\n"
        + binding_helper()
        + "bind_runtime_ninja \"$OUTPUT\" \"$RUNTIME\" \"$CUDA\"\n",
        encoding="utf-8",
    )
    harness.chmod(0o755)
    return subprocess.run(
        ["bash", str(harness)],
        env={
            **os.environ,
            "CUDA": str(cuda),
            "OUTPUT": str(root / "ninja-runtime.json"),
            "PATH": f"{host}:{os.environ.get('PATH', '/usr/bin:/bin')}",
            "PYTHON": sys.executable,
            "RUNTIME": str(runtime),
        },
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class NinjaBindingTests(unittest.TestCase):
    def test_runtime_venv_ninja_is_recorded_not_host_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = run_binding(root, runtime_ninja=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            ninja = root / "runtime-venv/bin/ninja"
            evidence = json.loads((root / "ninja-runtime.json").read_text(encoding="utf-8"))
            self.assertEqual(evidence["ninja_path"], str(ninja))
            self.assertEqual(evidence["command_resolution"], str(ninja))
            self.assertEqual(evidence["python_resolution"], str(ninja))
            self.assertEqual(evidence["version"], "1.13.0")
            self.assertEqual(evidence["sha256"], hashlib.sha256(ninja.read_bytes()).hexdigest())

    def test_missing_runtime_venv_ninja_is_not_satisfied_by_host_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_binding(Path(directory), runtime_ninja=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing executable runtime-venv Ninja", result.stderr)


if __name__ == "__main__":
    unittest.main()
