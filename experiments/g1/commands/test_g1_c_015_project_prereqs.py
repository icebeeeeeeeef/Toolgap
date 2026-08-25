#!/usr/bin/env python3
"""Executable counterexamples for the G1-C-015 Ninja prerequisite command."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).with_name("19-g1-c-015-project-prereqs.sh")


class PrerequisiteCommandTests(unittest.TestCase):
    def prepare(self, root: Path, *, existing: bool) -> tuple[Path, Path, dict[str, str]]:
        fake_bin = root / "bin"
        fake_bin.mkdir()
        ninja = root / "usr/bin/ninja"
        os_release = root / "os-release"
        log = root / "privileged.log"
        os_release.write_text('ID=ubuntu\nVERSION_ID="24.04"\n', encoding="utf-8")

        source = SOURCE.read_text(encoding="utf-8")
        source = source.replace("/usr/bin/ninja", str(ninja))
        source = source.replace("/etc/os-release", str(os_release))
        script = root / SOURCE.name
        script.write_text(source, encoding="utf-8")
        script.chmod(0o755)

        apt = fake_bin / "apt-get"
        apt.write_text(
            "#!/usr/bin/env bash\n"
            "printf '%s\\n' \"$*\" >>\"$PRIVILEGED_LOG\"\n"
            "if [[ \"${1:-}\" == install ]]; then\n"
            "  mkdir -p \"$(dirname -- \"$NINJA_DEST\")\"\n"
            "  printf '%s\\n' '#!/usr/bin/env bash' \"printf '1.11.1\\\\n'\" >\"$NINJA_DEST\"\n"
            "  chmod 0755 \"$NINJA_DEST\"\n"
            "fi\n",
            encoding="utf-8",
        )
        apt.chmod(0o755)
        sudo = fake_bin / "sudo"
        sudo.write_text('#!/usr/bin/env bash\nexec "$@"\n', encoding="utf-8")
        sudo.chmod(0o755)
        uname = fake_bin / "uname"
        uname.write_text(
            "#!/usr/bin/env bash\n"
            "case \"${1:-}\" in\n"
            "  -s) printf 'Linux\\n' ;;\n"
            "  -m) printf 'x86_64\\n' ;;\n"
            "  *) exit 2 ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        uname.chmod(0o755)
        dpkg = fake_bin / "dpkg-query"
        dpkg.write_text("#!/usr/bin/env bash\nprintf '1.11.1-2\\n'\n", encoding="utf-8")
        dpkg.chmod(0o755)
        if existing:
            ninja.parent.mkdir(parents=True)
            ninja.write_text("#!/usr/bin/env bash\nprintf '1.11.1\\n'\n", encoding="utf-8")
            ninja.chmod(0o755)

        manifest = root / "input-manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "identity": {"bundle_id": "G1-C-015"},
                    "static_inputs": {
                        "experiments/g1/commands/19-g1-c-015-project-prereqs.sh": {
                            "sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
                            "size_bytes": script.stat().st_size,
                        }
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )
        env = {
            **os.environ,
            "PATH": f"{fake_bin}:/usr/bin:/bin",
            "G1_C_015_INPUT_MANIFEST": str(manifest),
            "G1_C_015_PYTHON": sys.executable,
            "NINJA_DEST": str(ninja),
            "PRIVILEGED_LOG": str(log),
        }
        return script, log, env

    def run_script(self, script: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(script)], env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )

    def test_missing_ninja_installs_only_ninja_build(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            script, log, env = self.prepare(Path(directory), existing=False)
            result = self.run_script(script, env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                log.read_text(encoding="utf-8").splitlines(),
                ["update", "install -y --no-install-recommends ninja-build"],
            )
            self.assertIn("NINJA_PATH=", result.stdout)
            self.assertIn("NINJA_BUILD_PACKAGE_VERSION=1.11.1-2", result.stdout)

    def test_existing_ninja_skips_apt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            script, log, env = self.prepare(Path(directory), existing=True)
            result = self.run_script(script, env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(log.exists())

    def test_byte_mismatch_fails_before_privileged_action(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            script, log, env = self.prepare(Path(directory), existing=False)
            script.write_text(script.read_text(encoding="utf-8") + "# mutation\n", encoding="utf-8")
            result = self.run_script(script, env)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(log.exists())


if __name__ == "__main__":
    unittest.main()
