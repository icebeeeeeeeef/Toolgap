#!/usr/bin/env python3
"""Create the one-way, pre-arm admission receipt for G0-C-ATOMIC-007."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(checkout: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(checkout), *args], text=True
    ).strip()


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    return path.resolve()


def no_placeholders(value: object) -> bool:
    if isinstance(value, dict):
        return all(no_placeholders(item) for item in value.values())
    if isinstance(value, list):
        return all(no_placeholders(item) for item in value)
    return not (isinstance(value, str) and value.startswith("__"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--stock-checkout", required=True, type=Path)
    parser.add_argument("--treatment-checkout", required=True, type=Path)
    parser.add_argument("--stock-wheel", required=True, type=Path)
    parser.add_argument("--treatment-wheel", required=True, type=Path)
    parser.add_argument("--dependency-lock", required=True, type=Path)
    parser.add_argument("--environment-readback", required=True, type=Path)
    parser.add_argument("--stock-interpreter", required=True, type=Path)
    parser.add_argument("--treatment-interpreter", required=True, type=Path)
    args = parser.parse_args()

    if args.output.exists():
        raise ValueError(f"refusing to replace sealed manifest: {args.output}")
    template = require_file(args.template, "template")
    spec = require_file(args.spec, "SPEC")
    stock = args.stock_checkout.resolve()
    treatment = args.treatment_checkout.resolve()
    inputs = {
        "stock_wheel": require_file(args.stock_wheel, "stock wheel"),
        "treatment_wheel": require_file(args.treatment_wheel, "treatment wheel"),
        "dependency_lock": require_file(args.dependency_lock, "dependency lock"),
        "environment_readback": require_file(
            args.environment_readback, "environment readback"
        ),
        "stock_interpreter": require_file(args.stock_interpreter, "stock interpreter"),
        "treatment_interpreter": require_file(
            args.treatment_interpreter, "treatment interpreter"
        ),
    }

    document = json.loads(template.read_text(encoding="utf-8"))
    document["identity"]["spec_path"] = str(spec)
    document["identity"]["spec_sha256"] = sha256(spec)
    document["identity"]["attempt_id"] = args.attempt_id
    document["source"].update(
        {
            "stock_checkout": str(stock),
            "treatment_checkout": str(treatment),
            "stock_commit": git(stock, "rev-parse", "HEAD"),
            "stock_tree": git(stock, "rev-parse", "HEAD^{tree}"),
            "treatment_commit": git(treatment, "rev-parse", "HEAD"),
            "treatment_tree": git(treatment, "rev-parse", "HEAD^{tree}"),
            "stock_wheel_sha256": sha256(inputs["stock_wheel"]),
            "treatment_wheel_sha256": sha256(inputs["treatment_wheel"]),
            "dependency_lock_sha256": sha256(inputs["dependency_lock"]),
        }
    )
    document["environment"].update(
        {
            "observed_readback": str(inputs["environment_readback"]),
            "observed_readback_sha256": sha256(inputs["environment_readback"]),
            "stock_interpreter": str(inputs["stock_interpreter"]),
            "treatment_interpreter": str(inputs["treatment_interpreter"]),
        }
    )
    if not no_placeholders(document):
        raise ValueError("admission manifest still has generated placeholders")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(document, indent=2, sort_keys=True) + "\n"
    descriptor = os.open(
        args.output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode=0o444
    )
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(encoded)
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
