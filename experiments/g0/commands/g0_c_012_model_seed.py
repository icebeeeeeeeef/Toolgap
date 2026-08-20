#!/usr/bin/env python3
"""Safely prepare and revalidate the fixed G0-C-012 offline model seed."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tarfile
from pathlib import Path, PurePosixPath


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json_object(path: Path, label: str) -> dict[str, object]:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{label} must be a JSON object")
    return document


def require_exact_keys(
    document: dict[str, object], expected: set[str], label: str
) -> None:
    actual = set(document)
    if actual != expected:
        raise ValueError(
            f"{label} fields differ: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )


def load_inventory(path: Path) -> tuple[dict[str, object], dict[str, dict[str, object]]]:
    document = load_json_object(path, "model inventory")
    require_exact_keys(
        document, {"schema_version", "repository", "revision", "files"},
        "model inventory",
    )
    if document["schema_version"] != 1:
        raise ValueError("unsupported model inventory schema")
    if not isinstance(document["repository"], str) or not document["repository"]:
        raise ValueError("invalid model repository")
    if not isinstance(document["revision"], str) or not re.fullmatch(
        r"[0-9a-f]{40}", document["revision"]
    ):
        raise ValueError("invalid model revision")
    raw_files = document["files"]
    if not isinstance(raw_files, list) or not raw_files:
        raise ValueError("model inventory must contain files")
    files: dict[str, dict[str, object]] = {}
    previous = ""
    for item in raw_files:
        if not isinstance(item, dict):
            raise ValueError("model inventory file entry must be an object")
        require_exact_keys(item, {"path", "sha256", "size"}, "model file entry")
        relative = item["path"]
        if not isinstance(relative, str) or not relative:
            raise ValueError("invalid model file path")
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or str(pure) != relative:
            raise ValueError(f"unsafe model file path: {relative}")
        if relative <= previous or relative in files:
            raise ValueError("model inventory paths must be unique and sorted")
        previous = relative
        if not isinstance(item["size"], int) or item["size"] < 0:
            raise ValueError(f"invalid model file size: {relative}")
        if not isinstance(item["sha256"], str) or not re.fullmatch(
            r"[0-9a-f]{64}", item["sha256"]
        ):
            raise ValueError(f"invalid model file SHA-256: {relative}")
        files[relative] = item
    return document, files


def verify_tree(
    model_root: Path, expected: dict[str, dict[str, object]]
) -> tuple[int, int]:
    if not model_root.is_dir() or model_root.is_symlink():
        raise ValueError(f"missing or unsafe model root: {model_root}")
    observed: dict[str, Path] = {}
    for path in sorted(model_root.rglob("*")):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise ValueError(f"model snapshot contains a link: {path}")
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            raise ValueError(f"model snapshot contains a non-file: {path}")
        relative = path.relative_to(model_root).as_posix()
        observed[relative] = path
    if set(observed) != set(expected):
        raise ValueError(
            "model file set differs: "
            f"missing={sorted(set(expected) - set(observed))}, "
            f"extra={sorted(set(observed) - set(expected))}"
        )
    total = 0
    for relative, item in expected.items():
        path = observed[relative]
        size = path.stat().st_size
        if size != item["size"] or sha256(path) != item["sha256"]:
            raise ValueError(f"model file identity mismatch: {relative}")
        total += size
    return len(observed), total


def write_json_exclusive(path: Path, document: dict[str, object]) -> None:
    encoded = json.dumps(document, indent=2, sort_keys=True) + "\n"
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode=0o444)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(encoded)
    path.chmod(0o444)


def safe_extract(archive: Path, input_root: Path) -> Path:
    if input_root.exists():
        raise ValueError(f"model input root already exists: {input_root}")
    input_root.mkdir()
    names: set[str] = set()
    try:
        with tarfile.open(archive, "r:*") as bundle:
            members = bundle.getmembers()
            if not members:
                raise ValueError("empty model archive")
            for member in members:
                pure = PurePosixPath(member.name)
                if (
                    pure.is_absolute()
                    or ".." in pure.parts
                    or not pure.parts
                    or pure.parts[0] != "model-snapshot"
                    or str(pure) != member.name.rstrip("/")
                    or member.name in names
                ):
                    raise ValueError(f"unsafe model archive member: {member.name}")
                names.add(member.name)
                destination = input_root.joinpath(*pure.parts)
                if member.isdir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                if not member.isfile():
                    raise ValueError(f"model archive links/devices are prohibited: {member.name}")
                destination.parent.mkdir(parents=True, exist_ok=True)
                source = bundle.extractfile(member)
                if source is None:
                    raise ValueError(f"cannot read model archive member: {member.name}")
                descriptor = os.open(
                    destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode=0o444
                )
                with source, os.fdopen(descriptor, "wb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
                destination.chmod(0o444)
        return input_root / "model-snapshot"
    except BaseException:
        shutil.rmtree(input_root, ignore_errors=True)
        raise


def prepare(args: argparse.Namespace) -> int:
    archive = args.archive.resolve()
    inventory_path = args.inventory.resolve()
    input_root = args.input_root.resolve()
    receipt = args.receipt.resolve()
    if not archive.is_file():
        raise ValueError(f"missing model archive: {archive}")
    if not re.fullmatch(r"[0-9a-f]{64}", args.archive_sha256):
        raise ValueError("invalid expected model archive SHA-256")
    observed_archive_sha = sha256(archive)
    if observed_archive_sha != args.archive_sha256:
        raise ValueError("model archive SHA-256 mismatch")
    if receipt.exists():
        raise ValueError(f"model receipt already exists: {receipt}")
    inventory, files = load_inventory(inventory_path)
    model_root = safe_extract(archive, input_root)
    try:
        file_count, total_bytes = verify_tree(model_root, files)
        document = {
            "archive_sha256": observed_archive_sha,
            "file_count": file_count,
            "inventory_sha256": sha256(inventory_path),
            "model_root": str(model_root.resolve()),
            "repository": inventory["repository"],
            "revision": inventory["revision"],
            "total_bytes": total_bytes,
        }
        write_json_exclusive(receipt, document)
    except BaseException:
        shutil.rmtree(input_root, ignore_errors=True)
        raise
    print(f"MODEL_SEED_PREPARED: {model_root}")
    return 0


def verify(args: argparse.Namespace) -> int:
    model_root = args.model_root.resolve()
    inventory_path = args.inventory.resolve()
    receipt_path = args.receipt.resolve()
    inventory, files = load_inventory(inventory_path)
    receipt = load_json_object(receipt_path, "model receipt")
    require_exact_keys(
        receipt,
        {
            "archive_sha256", "file_count", "inventory_sha256", "model_root",
            "repository", "revision", "total_bytes",
        },
        "model receipt",
    )
    if receipt["model_root"] != str(model_root):
        raise ValueError("model root differs from admission")
    if receipt["inventory_sha256"] != sha256(inventory_path):
        raise ValueError("model inventory differs from admission")
    if receipt["repository"] != inventory["repository"] or receipt["revision"] != inventory["revision"]:
        raise ValueError("model repository or revision differs from admission")
    file_count, total_bytes = verify_tree(model_root, files)
    if receipt["file_count"] != file_count or receipt["total_bytes"] != total_bytes:
        raise ValueError("model file totals differ from admission")
    print(f"MODEL_SEED_VERIFIED: {model_root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--archive", required=True, type=Path)
    prepare_parser.add_argument("--archive-sha256", required=True)
    prepare_parser.add_argument("--input-root", required=True, type=Path)
    prepare_parser.add_argument("--inventory", required=True, type=Path)
    prepare_parser.add_argument("--receipt", required=True, type=Path)
    prepare_parser.set_defaults(handler=prepare)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--model-root", required=True, type=Path)
    verify_parser.add_argument("--inventory", required=True, type=Path)
    verify_parser.add_argument("--receipt", required=True, type=Path)
    verify_parser.set_defaults(handler=verify)
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
