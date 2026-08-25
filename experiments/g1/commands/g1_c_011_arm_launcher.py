#!/usr/bin/env python3
"""Create an arm session and wait for the parent handshake before exec."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path


def write_exclusive(path: Path, document: dict[str, object]) -> None:
    payload = (json.dumps(document, sort_keys=True) + "\n").encode()
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    with os.fdopen(descriptor, "wb") as output:
        output.write(payload)
        output.flush()
        os.fsync(output.fileno())
    path.chmod(0o444)


def wait_for_ack(path: Path, pid: int, timeout_seconds: float = 10) -> None:
    deadline = time.monotonic() + timeout_seconds
    while True:
        if path.is_symlink():
            raise ValueError("launcher ack must not be a symlink")
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            document = None
        except (UnicodeDecodeError, json.JSONDecodeError):
            document = None
        if document is not None:
            if (
                document != {"pid": pid, "schema_version": 1}
                or type(document.get("pid")) is not int
                or type(document.get("schema_version")) is not int
                or path.stat().st_mode & 0o222
                or not path.is_file()
            ):
                raise ValueError("launcher ack differs")
            return
        if time.monotonic() >= deadline:
            raise TimeoutError("launcher ack deadline exceeded")
        time.sleep(0.01)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--handshake", required=True, type=Path)
    parser.add_argument("--ack", required=True, type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        raise ValueError("launcher command is absent")
    handshake, ack = args.handshake.resolve(), args.ack.resolve()
    if handshake.parent != ack.parent or not handshake.parent.is_dir():
        raise ValueError("launcher evidence directory differs")
    os.setsid()
    pid = os.getpid()
    if os.getpgid(pid) != pid:
        raise ValueError("launcher did not form its own process group")
    write_exclusive(handshake, {"pgid": pid, "pid": pid, "schema_version": 1})
    wait_for_ack(ack, pid)
    os.execvp(command[0], command)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
