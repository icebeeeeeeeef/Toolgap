#!/usr/bin/env python3
"""Bind G1-PREFLIGHT-001's three offline archives to one clean source commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path


STATIC_PATHS = (
    "experiments/g1/SPEC.g1-preflight-001.md",
    "experiments/g1/artifacts/model-files.g1-preflight-001.json",
    "experiments/g1/manifest.g1-preflight-001.template.json",
    "experiments/g1/commands/00-g1-preflight-001-bootstrap.sh",
    "experiments/g1/commands/20-g1-preflight-001.sh",
    "experiments/g1/commands/g1_preflight_001_finalize.py",
    "experiments/g1/commands/g1_preflight_001_bundle_manifest.py",
    "upstream/sglang/pin.g1-preflight-001.toml",
    "upstream/sglang/patches/0001-atomic-checked-demote.patch",
    "upstream/sglang/patches/0002-g1-scripted-forced-demote.patch",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True
    ).strip()


def write_json_exclusive(path: Path, document: dict[str, object]) -> None:
    encoded = json.dumps(document, indent=2, sort_keys=True) + "\n"
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(encoded)
    path.chmod(0o444)


def read_pin(root: Path) -> dict[str, object]:
    pin = tomllib.loads(
        (root / "upstream/sglang/pin.g1-preflight-001.toml").read_text(
            encoding="utf-8"
        )
    )
    if pin.get("bundle", {}).get("id") != "G1-PREFLIGHT-001":
        raise ValueError("wrong preflight pin")
    if pin.get("bundle", {}).get("gate_decision") != "N/A: this bundle cannot produce a G1 PASS or STOP":
        raise ValueError("pin would permit a Gate result")
    return pin


def static_hashes(root: Path) -> dict[str, dict[str, object]]:
    hashes = {}
    for relative in STATIC_PATHS:
        path = root / relative
        if not path.is_file():
            raise ValueError(f"missing static input: {relative}")
        try:
            git(root, "cat-file", "-e", f"HEAD:{relative}")
        except subprocess.CalledProcessError as error:
            raise ValueError(
                f"static input is not present in the frozen ToolGap commit: {relative}"
            ) from error
        hashes[relative] = {"sha256": sha256(path), "size_bytes": path.stat().st_size}
    return hashes


def archive_entry(path: Path, label: str) -> dict[str, object]:
    path = path.resolve()
    if not path.is_file() or not path.is_absolute():
        raise ValueError(f"{label} must be an existing absolute archive path")
    return {"path": path.name, "sha256": sha256(path), "size_bytes": path.stat().st_size}


def expected(root: Path, toolgap: Path, sglang: Path, model: Path) -> dict[str, object]:
    if git(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("ToolGap tracked source must be clean before bundling")
    pin = read_pin(root)
    model_inventory = root / str(pin["model"]["inventory"])
    model_doc = json.loads(model_inventory.read_text(encoding="utf-8"))
    if (
        model_doc.get("repository") != pin["model"]["repository"]
        or model_doc.get("revision") != pin["model"]["revision"]
    ):
        raise ValueError("model inventory differs from pin")
    sglang_entry = archive_entry(sglang, "SGLang seed")
    if sglang_entry["sha256"] != pin["sglang"]["source_seed_sha256"]:
        raise ValueError("SGLang seed differs from fixed pin")
    return {
        "schema_version": 1,
        "identity": {
            "bundle_id": "G1-PREFLIGHT-001",
            "claim_state": "roadmap",
            "gate": "G1",
            "gate_decision": "N/A: preformal runtime validation only",
            "toolgap_commit": git(root, "rev-parse", "HEAD"),
            "toolgap_remote": git(root, "remote", "get-url", "origin"),
            "toolgap_tree": git(root, "rev-parse", "HEAD^{tree}"),
        },
        "archives": {
            "model_snapshot": archive_entry(model, "model snapshot"),
            "sglang_source_seed": sglang_entry,
            "toolgap_source_seed": archive_entry(toolgap, "ToolGap seed"),
        },
        "model": {
            "inventory_path": str(pin["model"]["inventory"]),
            "inventory_sha256": sha256(model_inventory),
            "local_only": pin["model"]["local_only"],
            "repository": pin["model"]["repository"],
            "revision": pin["model"]["revision"],
        },
        "static_inputs": static_hashes(root),
    }


def create(args: argparse.Namespace) -> int:
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"refusing to replace input manifest: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json_exclusive(
        output,
        expected(
            args.repo_root.resolve(),
            args.toolgap_seed,
            args.sglang_seed,
            args.model_snapshot,
        ),
    )
    print(output)
    return 0


def verify(args: argparse.Namespace) -> int:
    manifest = args.manifest.resolve()
    if not manifest.is_file():
        raise ValueError("missing input manifest")
    observed = json.loads(manifest.read_text(encoding="utf-8"))
    actual = expected(
        args.repo_root.resolve(),
        args.toolgap_seed,
        args.sglang_seed,
        args.model_snapshot,
    )
    if observed != actual:
        raise ValueError("input manifest differs from current clean inputs")
    print(f"VERIFIED_G1_PREFLIGHT_INPUT_MANIFEST: {manifest}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    for name, handler in (("create", create), ("verify", verify)):
        command = commands.add_parser(name)
        command.add_argument("--repo-root", required=True, type=Path)
        command.add_argument("--toolgap-seed", required=True, type=Path)
        command.add_argument("--sglang-seed", required=True, type=Path)
        command.add_argument("--model-snapshot", required=True, type=Path)
        if name == "create":
            command.add_argument("--output", required=True, type=Path)
        else:
            command.add_argument("--manifest", required=True, type=Path)
        command.set_defaults(handler=handler)
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
