#!/usr/bin/env python3
"""Focused handshake tests for the internal G1-C-009 arm launcher."""

from __future__ import annotations

import json
import importlib.util
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

LAUNCHER = Path(__file__).with_name("g1_c_009_arm_launcher.py")
SPEC = importlib.util.spec_from_file_location("g1_c_009_arm_launcher", LAUNCHER)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def wait_for(path: Path) -> None:
    deadline = time.monotonic() + 5
    while not path.exists():
        if time.monotonic() >= deadline:
            raise AssertionError(f"timed out waiting for {path}")
        time.sleep(0.01)


class G1C007ArmLauncherTests(unittest.TestCase):
    def test_ack_schema_version_rejects_bool(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ack = Path(directory) / "ack.json"
            ack.write_text(json.dumps({"pid": os.getpid(), "schema_version": True}), encoding="utf-8")
            ack.chmod(0o444)
            with self.assertRaises(ValueError):
                MODULE.wait_for_ack(ack, os.getpid(), timeout_seconds=0.01)

    def test_workload_waits_for_read_only_exclusive_handshake_ack(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            handshake = root / "handshake.json"
            ack = root / "ack.json"
            marker = root / "workload-started"
            command = [
                sys.executable, str(LAUNCHER),
                "--handshake", str(handshake), "--ack", str(ack), "--",
                sys.executable, "-c", "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('started')", str(marker),
            ]
            process = subprocess.Popen(command)
            wait_for(handshake)
            document = json.loads(handshake.read_text(encoding="utf-8"))
            self.assertEqual(document, {"pgid": process.pid, "pid": process.pid, "schema_version": 1})
            self.assertEqual(os.getpgid(process.pid), process.pid)
            self.assertEqual(handshake.stat().st_mode & 0o777, 0o444)
            self.assertFalse(marker.exists())
            ack_payload = (json.dumps({"pid": process.pid, "schema_version": 1}, sort_keys=True) + "\n").encode()
            descriptor = os.open(ack, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
            os.write(descriptor, ack_payload[:5])
            time.sleep(0.05)
            self.assertIsNone(process.poll())
            self.assertFalse(marker.exists())
            os.write(descriptor, ack_payload[5:])
            os.close(descriptor)
            ack.chmod(0o444)
            self.assertEqual(process.wait(timeout=5), 0)
            self.assertEqual(marker.read_text(encoding="utf-8"), "started")

            second_marker = root / "second-workload"
            second = subprocess.run([
                *command[:-1], str(second_marker),
            ], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertFalse(second_marker.exists())


if __name__ == "__main__":
    unittest.main()
