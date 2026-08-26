#!/usr/bin/env python3
"""Create or verify the immutable input manifest for formal G1-C-018."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

BUNDLE_ID = "G1-C-018"
BASE_COMMIT = "92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2"
BASE_TREE = "25e9bf86d04c27fe380024d9c8c421c3b5b51f3c"
SGLANG_SEED_SHA256 = "2d40db92ff1a21cb78e95f4da98352f1fa17086e1a16a82e95070f05e1460400"
MODEL_REPOSITORY = "Qwen/Qwen3-0.6B"
MODEL_REVISION = "c1899de289a04d12100db370d81485cdf75e47ca"
MODEL_INVENTORY = "experiments/g1/artifacts/model-files.g1-preflight-001.json"
RUNTIME_PROVENANCE = "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite"
G0_RUNTIME_WHEEL = "sglang-0.0.0.dev2+g734a8e921-cp312-cp312-linux_x86_64.whl"
G0_RUNTIME_WHEEL_SHA256 = "0874acca7b27e45ae39606eb12ee24a5f4cb17cd3791bb60fdccb95c332bf59e"
PYPI_INDEX_URL = "http://mirrors.cloud.aliyuncs.com/pypi/simple/"
PYPI_TRUSTED_HOST = "mirrors.cloud.aliyuncs.com"
MINIMUM_FREE_BYTES = 24 * 1024 * 1024 * 1024
PATCH_PATHS = (
    "upstream/sglang/patches/0001-atomic-checked-demote.patch",
    "upstream/sglang/patches/0002-g1-scripted-forced-demote-c018.patch",
    "upstream/sglang/patches/0003-cuda12-compat-packaging.patch",
)
STATIC_PATHS = (
    "experiments/g1/SPEC.g1-c-018.md",
    "experiments/g1/manifest.g1-c-018.template.json",
    "experiments/g1/commands/00-g1-c-018-bootstrap.sh",
    "experiments/g1/commands/20-g1-c-018.sh",
    "experiments/g1/commands/g1_c_018_bundle_manifest.py",
    "experiments/g1/commands/g1_c_018_arm_launcher.py",
    "experiments/g1/commands/g1_c_018_finalize.py",
    "experiments/g1/commands/g1_c_018_extract_records.py",
    "experiments/g1/commands/g1_c_018_gpu_sampler.py",
    "experiments/g1/commands/test_g1_c_018_finalize.py",
    "experiments/g1/commands/test_g1_c_018_arm_launcher.py",
    "experiments/g1/commands/test_g1_c_018_gpu_sampler.py",
    "experiments/g1/commands/test_g1_c_018_signal_cleanup.sh",
    "experiments/g1/commands/test_g1_c_018_source_restore.sh",
    "experiments/g1/commands/test_g1_c_018_runtime_wheel_name.sh",
    "experiments/g1/commands/test_g1_c_018_arm_runner_spawn.sh",
    "experiments/g1/commands/test_g1_c_018_anchor_offline.sh",
    "experiments/g1/commands/test_g1_c_018_request_admission.py",
    "experiments/g1/commands/test_g1_c_018_shared_coverage.py",
    "experiments/g1/commands/test_g1_c_018_rejection_guards.py",
    "experiments/g1/commands/test_g1_c_018_storage_preflight.sh",
    "experiments/g1/commands/test_g1_c_018_bundle_manifest.py",
    "experiments/g1/commands/test_g1_c_018_pre_execution.py",
    "experiments/g1/commands/test_g1_c_018_failure_evidence.sh",
    "experiments/g1/commands/test_g1_c_018_cleanup_failure.sh",
    "experiments/g1/commands/test_g1_c_018_host_mismatch.sh",
    "experiments/g1/commands/test_g1_c_018_ninja_binding.py",
    "experiments/g1/commands/test_g1_c_018_oracle_mutations.py",
    "scripts/verify-g1-c-018-bundle.sh",
    "scripts/anchor-g1-c-018-oss.sh",
    MODEL_INVENTORY,
    *PATCH_PATHS,
)
ARCHIVE_NAMES = {
    "cuda_wheelhouse",
    "model_snapshot",
    "runtime_wheel",
    "runtime_wheel_provenance",
    "sglang_source_seed",
    "toolgap_source_seed",
}
WHEELHOUSE_ROOT = "cuda-wheelhouse"
WHEELHOUSE_NAMES = {
    "sglang_kernel": "sglang-kernel",
    "sgl_deep_ep": "sgl-deep-ep",
    "sgl_deep_gemm": "sgl-deep-gemm",
    "torch": "torch",
    "torchvision": "torchvision",
    "torchaudio": "torchaudio",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def require_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError(f"invalid {label}")
    return value


def load_json(path: Path, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid {label}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def archive_entry(path: Path, label: str) -> dict[str, object]:
    path = path.resolve()
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} must be an absolute regular file")
    return {"path": path.name, "sha256": digest(path), "size_bytes": path.stat().st_size}


def write_exclusive(path: Path, document: dict[str, object]) -> None:
    payload = json.dumps(document, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        output.write(payload)
    path.chmod(0o444)


def safe_seed(archive_path: Path, top_level: str) -> None:
    names: set[str] = set()
    try:
        with tarfile.open(archive_path, "r:*") as archive:
            for member in archive.getmembers():
                name = member.name.rstrip("/")
                pure = PurePosixPath(member.name)
                if (
                    not pure.parts or pure.is_absolute() or ".." in pure.parts
                    or pure.parts[0] != top_level or name in names
                    or not (member.isdir() or member.isfile())
                ):
                    raise ValueError(f"unsafe archive member: {member.name}")
                names.add(name)
    except tarfile.TarError as error:
        raise ValueError(f"{top_level} seed is unreadable") from error
    if not names:
        raise ValueError(f"{top_level} seed is empty")


def canonical_distribution(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def wheel_identity(path: Path) -> tuple[str, str]:
    try:
        with zipfile.ZipFile(path) as wheel:
            metadata = [name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")]
            if len(metadata) != 1:
                raise ValueError("wheel metadata count differs")
            text = wheel.read(metadata[0]).decode("utf-8")
    except (UnicodeDecodeError, zipfile.BadZipFile) as error:
        raise ValueError("invalid wheel") from error
    fields = {}
    for line in text.splitlines():
        if ":" in line:
            name, value = line.split(":", 1)
            if name in {"Name", "Version"} and name not in fields:
                fields[name] = value.strip()
    if set(fields) != {"Name", "Version"}:
        raise ValueError("wheel identity is incomplete")
    return fields["Name"], fields["Version"]


def validate_wheelhouse(archive_path: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="g1-c-018-wheelhouse-") as directory:
        root = Path(directory) / WHEELHOUSE_ROOT
        root.mkdir()
        members: dict[str, Path] = {}
        try:
            with tarfile.open(archive_path, "r:*") as archive:
                for member in archive.getmembers():
                    pure, name = PurePosixPath(member.name), member.name.rstrip("/")
                    if (
                        not pure.parts or pure.is_absolute() or ".." in pure.parts
                        or pure.parts[0] != WHEELHOUSE_ROOT or name in members
                        or not (member.isdir() or member.isfile())
                    ):
                        raise ValueError(f"unsafe wheelhouse member: {member.name}")
                    if member.isdir():
                        continue
                    if len(pure.parts) != 2:
                        raise ValueError(f"nested wheelhouse member: {member.name}")
                    source = archive.extractfile(member)
                    if source is None:
                        raise ValueError("unreadable wheelhouse member")
                    destination = root / pure.name
                    with source, destination.open("xb") as output:
                        shutil.copyfileobj(source, output)
                    members[name] = destination
        except tarfile.TarError as error:
            raise ValueError("wheelhouse archive is unreadable") from error
        index_file = members.get(f"{WHEELHOUSE_ROOT}/wheelhouse-index.json")
        if index_file is None:
            raise ValueError("wheelhouse index is absent")
        index = load_json(index_file, "wheelhouse index")
        if set(index) != {"schema_version", "wheels"} or type(index["schema_version"]) is not int or index["schema_version"] != 1:
            raise ValueError("wheelhouse index schema differs")
        wheels = index["wheels"]
        if not isinstance(wheels, dict) or set(wheels) != set(WHEELHOUSE_NAMES):
            raise ValueError("wheelhouse package set differs")
        expected = {f"{WHEELHOUSE_ROOT}/wheelhouse-index.json"}
        for label, expected_name in WHEELHOUSE_NAMES.items():
            entry = wheels[label]
            if (
                not isinstance(entry, dict) or set(entry) != {"path", "sha256", "size_bytes"}
                or not isinstance(entry.get("path"), str)
                or PurePosixPath(entry["path"]).name != entry["path"]
                or not entry["path"].endswith(".whl")
                or type(entry.get("size_bytes")) is not int or entry["size_bytes"] < 1
            ):
                raise ValueError(f"invalid wheelhouse entry: {label}")
            require_digest(entry["sha256"], f"{label} wheel SHA-256")
            member_name = f"{WHEELHOUSE_ROOT}/{entry['path']}"
            wheel = members.get(member_name)
            if wheel is None or wheel.stat().st_size != entry["size_bytes"] or digest(wheel) != entry["sha256"]:
                raise ValueError(f"wheelhouse entry differs: {label}")
            name, _ = wheel_identity(wheel)
            if canonical_distribution(name) != canonical_distribution(expected_name):
                raise ValueError(f"wheelhouse package differs: {label}")
            expected.add(member_name)
        if set(members) != expected:
            raise ValueError("wheelhouse includes files outside the six-wheel boundary")


def patch_entries(root: Path) -> list[dict[str, str]]:
    entries = []
    for path in PATCH_PATHS:
        entries.append({"path": path, "sha256": digest(root / path)})
    return entries


def validate_runtime_provenance(root: Path, wheel: Path, provenance_path: Path) -> None:
    provenance = load_json(provenance_path, "runtime wheel provenance")
    if type(provenance.get("schema_version")) is not int or provenance.get("schema_version") != 1 or provenance.get("identity") != RUNTIME_PROVENANCE:
        raise ValueError("runtime wheel provenance identity differs")
    rebuild = provenance.get("source_rebuild")
    if not isinstance(rebuild, dict) or rebuild.get("performed") is not False:
        raise ValueError("runtime wheel provenance permits a source rebuild")
    output = provenance.get("output_wheel")
    if (
        not isinstance(output, dict)
        or wheel.name != G0_RUNTIME_WHEEL
        or output.get("filename") != G0_RUNTIME_WHEEL
        or output.get("sha256") != digest(wheel)
        or type(output.get("size_bytes")) is not int
        or output.get("size_bytes") != wheel.stat().st_size
    ):
        raise ValueError("runtime wheel provenance does not bind output wheel")
    for field in ("metadata_sha256", "record_sha256"):
        require_digest(output.get(field), f"runtime output {field}")
    patches = provenance.get("patches")
    expected_patches = patch_entries(root)
    if not isinstance(patches, list) or len(patches) != len(expected_patches):
        raise ValueError("runtime wheel provenance patch set differs")
    for label, observed, expected in zip(("patch_one", "patch_two", "patch_three"), patches, expected_patches):
        if (
            not isinstance(observed, dict)
            or observed.get("label") != label
            or not isinstance(observed.get("path"), str)
            or not Path(observed["path"]).is_absolute()
            or observed.get("sha256") != expected["sha256"]
        ):
            raise ValueError("runtime wheel provenance patch binding differs")
    base = provenance.get("base_wheel")
    if not isinstance(base, dict) or base.get("filename") != G0_RUNTIME_WHEEL or base.get("sha256") != G0_RUNTIME_WHEEL_SHA256:
        raise ValueError("runtime wheel provenance base payload differs")
    rewrite = provenance.get("metadata_rewrite")
    expected_rewrite = [
        {"from": before, "to": after, "input_occurrences": 1, "output_occurrences": 1}
        for before, after in (
            ("cuda-python>=13.0", "cuda-python>=12,<13"),
            ("flashinfer_python[cu13]", "flashinfer_python[cu12]"),
            ("humming-kernels[cu13]==0.1.10", "humming-kernels[cu12]==0.1.10"),
            ("nvidia-cutlass-dsl[cu13]==4.6.2", "nvidia-cutlass-dsl==4.6.2"),
        )
    ]
    if (
        not isinstance(rewrite, dict)
        or rewrite.get("exact_substitutions") != expected_rewrite
        or any(
            type(item.get(field)) is not int
            for item in rewrite.get("exact_substitutions", [])
            if isinstance(item, dict)
            for field in ("input_occurrences", "output_occurrences")
        )
    ):
        raise ValueError("runtime wheel metadata rewrite differs")


def static_inputs(root: Path) -> dict[str, dict[str, object]]:
    if git(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("tracked ToolGap files must be clean before freezing G1-C-018")
    result = {}
    for relative in STATIC_PATHS:
        path = root / relative
        if not path.is_file():
            raise ValueError(f"missing static input: {relative}")
        try:
            git(root, "cat-file", "-e", f"HEAD:{relative}")
        except subprocess.CalledProcessError as error:
            raise ValueError(f"static input is absent from HEAD: {relative}") from error
        result[relative] = {"sha256": digest(path), "size_bytes": path.stat().st_size}
    return result


def manifest_expected(args: argparse.Namespace) -> dict[str, object]:
    root = args.repo_root.resolve()
    inventory = load_json(root / MODEL_INVENTORY, "model inventory")
    if inventory.get("repository") != MODEL_REPOSITORY or inventory.get("revision") != MODEL_REVISION:
        raise ValueError("model inventory identity differs")
    sglang = archive_entry(args.sglang_seed, "SGLang source seed")
    if sglang["sha256"] != SGLANG_SEED_SHA256:
        raise ValueError("SGLang source seed differs from formal pin")
    toolgap = archive_entry(args.toolgap_seed, "ToolGap source seed")
    model = archive_entry(args.model_snapshot, "model snapshot")
    runtime = archive_entry(args.runtime_wheel, "runtime wheel")
    provenance = archive_entry(args.runtime_wheel_provenance, "runtime wheel provenance")
    wheelhouse = archive_entry(args.cuda_wheelhouse, "CUDA wheelhouse")
    safe_seed(args.toolgap_seed.resolve(), "toolgap-source.git")
    safe_seed(args.sglang_seed.resolve(), "sglang-source.git")
    validate_runtime_provenance(root, args.runtime_wheel.resolve(), args.runtime_wheel_provenance.resolve())
    validate_wheelhouse(args.cuda_wheelhouse.resolve())
    return {
        "schema_version": 1,
        "identity": {
            "bundle_id": BUNDLE_ID,
            "claim_state": "roadmap",
            "gate": "G1",
            "kind": "formal_checked_demote_runtime",
            "sglang_base_commit": BASE_COMMIT,
            "sglang_base_tree": BASE_TREE,
            "toolgap_commit": git(root, "rev-parse", "HEAD"),
            "toolgap_remote": git(root, "remote", "get-url", "origin"),
            "toolgap_tree": git(root, "rev-parse", "HEAD^{tree}"),
        },
        "archives": {
            "cuda_wheelhouse": wheelhouse,
            "model_snapshot": model,
            "runtime_wheel": runtime,
            "runtime_wheel_provenance": provenance,
            "sglang_source_seed": sglang,
            "toolgap_source_seed": toolgap,
        },
        "model": {
            "inventory_path": MODEL_INVENTORY,
            "inventory_sha256": digest(root / MODEL_INVENTORY),
            "local_only": True,
            "repository": MODEL_REPOSITORY,
            "revision": MODEL_REVISION,
        },
        "patches": patch_entries(root),
        "ordinary_dependency_transport": {
            "index_url": PYPI_INDEX_URL,
            "trusted_host": PYPI_TRUSTED_HOST,
        },
        "storage_preflight": {"minimum_free_bytes": MINIMUM_FREE_BYTES},
        "static_inputs": static_inputs(root),
    }


def validate_schema(document: dict[str, object]) -> None:
    if set(document) != {
        "archives", "identity", "model", "ordinary_dependency_transport",
        "patches", "schema_version", "static_inputs", "storage_preflight",
    } or type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise ValueError("input manifest schema differs")
    identity = document["identity"]
    if not isinstance(identity, dict) or identity.get("bundle_id") != BUNDLE_ID:
        raise ValueError("input manifest identity differs")
    if not isinstance(document["archives"], dict) or set(document["archives"]) != ARCHIVE_NAMES:
        raise ValueError("input manifest archive set differs")
    for label, entry in document["archives"].items():
        if not isinstance(entry, dict) or type(entry.get("size_bytes")) is not int or entry["size_bytes"] < 1:
            raise ValueError(f"input manifest archive size differs: {label}")
    model = document.get("model")
    if not isinstance(model, dict) or type(model.get("local_only")) is not bool:
        raise ValueError("input manifest model schema differs")
    storage = document.get("storage_preflight")
    if not isinstance(storage, dict) or type(storage.get("minimum_free_bytes")) is not int:
        raise ValueError("input manifest storage schema differs")
    static = document.get("static_inputs")
    if not isinstance(static, dict) or any(
        not isinstance(entry, dict) or type(entry.get("size_bytes")) is not int or entry["size_bytes"] < 1
        for entry in static.values()
    ):
        raise ValueError("input manifest static input schema differs")


def create(args: argparse.Namespace) -> int:
    output = args.output.resolve()
    if output.exists():
        raise ValueError("refusing to replace input manifest")
    document = manifest_expected(args)
    validate_schema(document)
    write_exclusive(output, document)
    print(output)
    return 0


def verify(args: argparse.Namespace) -> int:
    observed = load_json(args.manifest.resolve(), "input manifest")
    expected = manifest_expected(args)
    validate_schema(observed)
    if observed != expected:
        raise ValueError("input manifest differs from frozen inputs")
    print(f"VERIFIED_G1_C_018_INPUT_MANIFEST: {args.manifest.resolve()}")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="command", required=True)
    for name, handler in (("create", create), ("verify", verify)):
        command = commands.add_parser(name)
        command.add_argument("--repo-root", required=True, type=Path)
        command.add_argument("--toolgap-seed", required=True, type=Path)
        command.add_argument("--sglang-seed", required=True, type=Path)
        command.add_argument("--model-snapshot", required=True, type=Path)
        command.add_argument("--runtime-wheel", required=True, type=Path)
        command.add_argument("--runtime-wheel-provenance", required=True, type=Path)
        command.add_argument("--cuda-wheelhouse", required=True, type=Path)
        if name == "create":
            command.add_argument("--output", required=True, type=Path)
        else:
            command.add_argument("--manifest", required=True, type=Path)
        command.set_defaults(handler=handler)
    return root


if __name__ == "__main__":
    arguments = parser().parse_args()
    raise SystemExit(arguments.handler(arguments))
