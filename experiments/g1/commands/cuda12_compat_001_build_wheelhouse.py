#!/usr/bin/env python3
"""Create the exact CUDA12-COMPAT-001 wheelhouse archive from six wheels."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import tarfile
import zipfile
from pathlib import Path

import cuda12_compat_001_bundle_manifest as bundle


WHEEL_ARGS = {
    "sglang_kernel": "sglang_kernel",
    "sgl_deep_ep": "sgl_deep_ep",
    "sgl_deep_gemm": "sgl_deep_gemm",
    "torch": "torch",
    "torchvision": "torchvision",
    "torchaudio": "torchaudio",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def wheel_identity(path: Path, label: str) -> tuple[str, str]:
    try:
        with zipfile.ZipFile(path) as archive:
            metadata = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
            if len(metadata) != 1:
                raise ValueError(f"{label} must have exactly one wheel METADATA file")
            text = archive.read(metadata[0]).decode("utf-8")
    except (UnicodeDecodeError, zipfile.BadZipFile) as error:
        raise ValueError(f"{label} is not a readable wheel") from error
    values = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            if key in {"Name", "Version"} and key not in values:
                values[key] = value.strip()
    if set(values) != {"Name", "Version"}:
        raise ValueError(f"{label} METADATA omits Name or Version")
    return values["Name"], values["Version"]


def checked_wheels(args: argparse.Namespace) -> dict[str, Path]:
    pin = bundle.read_pin(args.repo_root.resolve())
    packaging = pin["cuda12_packaging"]
    assert isinstance(packaging, dict)
    expectations = bundle.wheelhouse_expectations(packaging)
    wheels: dict[str, Path] = {}
    names: set[str] = set()
    for label, argument in WHEEL_ARGS.items():
        path = getattr(args, argument).resolve()
        if not path.is_absolute() or not path.is_file() or path.is_symlink() or path.suffix != ".whl":
            raise ValueError(f"{label} must be an absolute regular wheel")
        if path.name in names:
            raise ValueError("wheelhouse filenames must be unique")
        names.add(path.name)
        name, version = wheel_identity(path, label)
        expected_name, expected_version = expectations[label]
        if (
            bundle.canonical_distribution(name) != bundle.canonical_distribution(expected_name)
            or version != expected_version
        ):
            raise ValueError(f"wheel identity differs from pinned CUDA12 route: {label}")
        wheels[label] = path
    return wheels


def archive_member(name: str, size: int) -> tarfile.TarInfo:
    member = tarfile.TarInfo(name)
    member.size = size
    member.mode = 0o444
    member.uid = 0
    member.gid = 0
    member.uname = ""
    member.gname = ""
    member.mtime = 0
    return member


def create(args: argparse.Namespace) -> int:
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"refusing to overwrite wheelhouse archive: {output}")
    wheels = checked_wheels(args)
    index = {
        "schema_version": 1,
        "wheels": {
            label: {
                "path": path.name,
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
            for label, path in wheels.items()
        },
    }
    index_bytes = (json.dumps(index, indent=2, sort_keys=True) + "\n").encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    try:
        with os.fdopen(descriptor, "wb") as raw, gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, mtime=0
        ) as compressed, tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
            archive.addfile(
                archive_member("cuda-wheelhouse/wheelhouse-index.json", len(index_bytes)),
                fileobj=io.BytesIO(index_bytes),
            )
            for label in bundle.WHEELHOUSE_KEYS:
                path = wheels[label]
                with path.open("rb") as payload:
                    archive.addfile(
                        archive_member(f"cuda-wheelhouse/{path.name}", path.stat().st_size),
                        fileobj=payload,
                    )
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    output.chmod(0o444)
    pin = bundle.read_pin(args.repo_root.resolve())
    packaging = pin["cuda12_packaging"]
    assert isinstance(packaging, dict)
    bundle.validate_cuda_wheelhouse(output, packaging)
    print(f"CUDA12_COMPAT_WHEELHOUSE_CREATED: {output}")
    print(f"sha256={sha256(output)}")
    print(f"size_bytes={output.stat().st_size}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    for argument in WHEEL_ARGS.values():
        parser.add_argument(f"--{argument.replace('_', '-')}", dest=argument, required=True, type=Path)
    args = parser.parse_args()
    return create(args)


if __name__ == "__main__":
    raise SystemExit(main())
