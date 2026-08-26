#!/usr/bin/env python3
"""Extract exactly one canonical G1 scripted-runtime record from one arm log."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

REQUIRED = {
    "arm", "operation", "target", "component_qualification", "priority_release",
    "released_component_leaves", "facade", "nodes", "freed_device_ids",
    "route_counters", "capacity",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-arm", required=True)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("refusing to replace extracted record")
    records = []
    for line in args.log.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and value.get("arm") == args.expected_arm:
            records.append(value)
    if len(records) != 1:
        raise ValueError(f"expected exactly one {args.expected_arm} record, found {len(records)}")
    record = records[0]
    permitted = REQUIRED | ({"stock_eviction"} if args.expected_arm == "stock_eviction_liveness" else set())
    if set(record) != permitted:
        raise ValueError("record schema differs")
    if not isinstance(record["operation"], dict) or not isinstance(record["target"], dict):
        raise ValueError("record operation or target differs")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, indent=2, sort_keys=True) + "\n"
    descriptor = os.open(args.output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        output.write(payload)
    args.output.chmod(0o444)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
