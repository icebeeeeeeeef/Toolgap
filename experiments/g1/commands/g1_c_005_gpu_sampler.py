#!/usr/bin/env python3
"""Capture GPU PID samples continuously through one formal arm's lifetime."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


def captured_at() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def arm_is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def gpu_pids() -> list[int]:
    result = subprocess.run(
        ["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader,nounits"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("nvidia-smi GPU PID query failed")
    pids = []
    for line in result.stdout.splitlines():
        value = line.strip()
        if value and not re.fullmatch(r"[1-9][0-9]*", value):
            raise ValueError(f"nvidia-smi returned an invalid PID: {value!r}")
        if value:
            pids.append(int(value))
    return sorted(set(pids))


def capture_until_arm_exit(
    arm_pid: int,
    poll_seconds: float,
    *,
    read_pids: Callable[[], list[int]] = gpu_pids,
    is_alive: Callable[[int], bool] = arm_is_alive,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], str] = captured_at,
) -> list[dict[str, object]]:
    """Return every sample from sampler start through the arm's observed exit."""
    samples = []
    while True:
        pids = read_pids()
        if (
            not isinstance(pids, list)
            or any(type(pid) is not int or pid < 1 for pid in pids)
            or pids != sorted(set(pids))
        ):
            raise ValueError("GPU PID sampler received a noncanonical sample")
        samples.append({"captured_at": clock(), "pids": pids})
        if not is_alive(arm_pid):
            return samples
        sleep(poll_seconds)


def write_exclusive(path: Path, payload: str) -> None:
    if not path.is_absolute() or not path.parent.is_dir() or path.exists():
        raise ValueError(f"refusing to replace sampler output: {path}")
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        output.write(payload)
    path.chmod(0o444)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm-pid", type=int, required=True)
    parser.add_argument("--poll-seconds", type=float, required=True)
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--union", type=Path, required=True)
    args = parser.parse_args()
    if args.arm_pid < 1 or args.poll_seconds <= 0 or args.poll_seconds > 1:
        raise ValueError("invalid sampler parameters")
    samples = capture_until_arm_exit(args.arm_pid, args.poll_seconds)
    document = {
        "arm_pid": args.arm_pid,
        "poll_seconds": args.poll_seconds,
        "samples": samples,
    }
    union = sorted({pid for sample in samples for pid in sample["pids"]})
    write_exclusive(args.samples.resolve(), json.dumps(document, indent=2, sort_keys=True) + "\n")
    write_exclusive(args.union.resolve(), "".join(f"{pid}\n" for pid in union))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
