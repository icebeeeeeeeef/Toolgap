#!/usr/bin/env python3
"""Revalidate the frozen Git and generated identity before each G0-C-008 phase."""

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


def require_digest(path: Path, expected: str, label: str) -> None:
    if not path.is_file() or sha256(path) != expected:
        raise ValueError(f"{label} identity mismatch: {path}")


def require_clean(checkout: Path, label: str) -> None:
    if git(checkout, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError(f"{label} has tracked changes")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--require-receipt")
    parser.add_argument("--receipt-status")
    args = parser.parse_args()
    if bool(args.require_receipt) != bool(args.receipt_status):
        raise ValueError("receipt path and expected status must be provided together")

    run_dir = args.run_dir.resolve()
    repo_root = args.repo_root.resolve()
    manifest_path = run_dir / "manifest.json"
    checksum_path = run_dir / "manifest.sha256"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checksum = checksum_path.read_text(encoding="utf-8").split()[0]
    if checksum != sha256(manifest_path):
        raise ValueError("manifest.sha256 does not match manifest.json")
    identity = manifest["identity"]
    source = manifest["source"]
    runtime = manifest["runtime"]
    environment = manifest["environment"]

    if Path(identity["toolgap_repository"]).resolve() != repo_root:
        raise ValueError("ToolGap repository path differs from admission")
    require_clean(repo_root, "ToolGap repository")
    if git(repo_root, "rev-parse", "HEAD") != identity["toolgap_commit"]:
        raise ValueError("ToolGap commit differs from admission")
    if git(repo_root, "rev-parse", "HEAD^{tree}") != identity["toolgap_tree"]:
        raise ValueError("ToolGap tree differs from admission")
    require_digest(
        repo_root / identity["spec_path"], identity["spec_sha256"], "SPEC"
    )
    require_digest(
        repo_root / source["patch_path"], source["patch_sha256"], "patch"
    )
    require_digest(
        repo_root / runtime["request_path"], runtime["request_sha256"], "request"
    )

    stock = Path(source["stock_checkout"]).resolve()
    treatment = Path(source["treatment_checkout"]).resolve()
    require_clean(stock, "stock checkout")
    require_clean(treatment, "treatment checkout")
    for checkout, prefix in ((stock, "stock"), (treatment, "treatment")):
        if git(checkout, "rev-parse", "HEAD") != source[f"{prefix}_commit"]:
            raise ValueError(f"{prefix} commit differs from admission")
        if git(checkout, "rev-parse", "HEAD^{tree}") != source[f"{prefix}_tree"]:
            raise ValueError(f"{prefix} tree differs from admission")

    evidence_digests = {
        source["stock_wheel_path"]: source["stock_wheel_sha256"],
        source["treatment_wheel_path"]: source["treatment_wheel_sha256"],
        environment["observed_readback_path"]: environment[
            "observed_readback_sha256"
        ],
        runtime["dependency_lock_path"]: runtime["dependency_lock_sha256"],
        runtime["model_snapshot_path"]: runtime["model_snapshot_sha256"],
        runtime["runtime_env_path"]: runtime["runtime_env_sha256"],
        runtime["stock_install_report_path"]: runtime[
            "stock_install_report_sha256"
        ],
        runtime["treatment_install_report_path"]: runtime[
            "treatment_install_report_sha256"
        ],
        runtime["stock_provenance_path"]: runtime["stock_provenance_sha256"],
        runtime["treatment_provenance_path"]: runtime[
            "treatment_provenance_sha256"
        ],
    }
    for relative, expected in evidence_digests.items():
        require_digest(run_dir / relative, expected, relative)
    stock_interpreter = Path(os.path.abspath(environment["stock_interpreter"]))
    treatment_interpreter = Path(os.path.abspath(environment["treatment_interpreter"]))
    if (
        not stock_interpreter.is_file()
        or not treatment_interpreter.is_file()
        or stock_interpreter == treatment_interpreter
    ):
        raise ValueError("admitted arm interpreters are missing or not distinct")

    if args.require_receipt:
        receipt_path = run_dir / args.require_receipt
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("status") != args.receipt_status:
            raise ValueError(f"unexpected phase receipt status: {receipt_path}")
        if receipt.get("manifest_sha256") != sha256(manifest_path):
            raise ValueError(f"phase receipt is not bound to the manifest: {receipt_path}")
    print(f"IDENTITY_VERIFIED: {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
