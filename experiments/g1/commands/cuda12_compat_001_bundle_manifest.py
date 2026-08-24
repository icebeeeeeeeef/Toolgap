#!/usr/bin/env python3
"""Bind CUDA12-COMPAT-001's staged inputs to one clean ToolGap revision."""

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
import tomllib
import zipfile
from pathlib import Path, PurePosixPath


BUNDLE_ID = "CUDA12-COMPAT-001"
INPUT_GATE_DECISION = "N/A: CUDA 12 compatibility probe only"
ARCHIVE_NAMES = {
    "cuda_wheelhouse",
    "model_snapshot",
    "runtime_wheel",
    "runtime_wheel_provenance",
    "sglang_source_seed",
    "toolgap_source_seed",
}
WHEELHOUSE_TOP_LEVEL = "cuda-wheelhouse"
WHEELHOUSE_KEYS = (
    "sglang_kernel",
    "sgl_deep_ep",
    "sgl_deep_gemm",
    "torch",
    "torchvision",
    "torchaudio",
)
METADATA_REWRITE = (
    ("cuda-python>=13.0", "cuda-python>=12,<13"),
    ("flashinfer_python[cu13]", "flashinfer_python[cu12]"),
    ("humming-kernels[cu13]==0.1.10", "humming-kernels[cu12]==0.1.10"),
    ("nvidia-cutlass-dsl[cu13]==4.6.2", "nvidia-cutlass-dsl==4.6.2"),
)
STATIC_PATHS = (
    "experiments/g1/SPEC.cuda12-compat-001.md",
    "experiments/g1/artifacts/model-files.g1-preflight-001.json",
    "experiments/g1/manifest.cuda12-compat-001.template.json",
    "experiments/g1/commands/00-cuda12-compat-001-bootstrap.sh",
    "experiments/g1/commands/19-cuda12-compat-001-project-prereqs.sh",
    "experiments/g1/commands/20-cuda12-compat-001.sh",
    "experiments/g1/commands/cuda12_compat_001_bundle_manifest.py",
    "experiments/g1/commands/cuda12_compat_001_finalize.py",
    "experiments/g1/commands/cuda12_compat_001_build_wheelhouse.py",
    "experiments/g1/commands/cuda12_compat_001_repackage_wheel.py",
    "upstream/sglang/pin.cuda12-compat-001.toml",
    "upstream/sglang/patches/0001-atomic-checked-demote.patch",
    "upstream/sglang/patches/0002-g1-scripted-forced-demote.patch",
    "upstream/sglang/patches/0003-cuda12-compat-packaging.patch",
    "scripts/verify-cuda12-compat-001-bundle.sh",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def require_sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError(f"invalid {label}")
    return value


def write_json_exclusive(path: Path, document: dict[str, object]) -> None:
    encoded = json.dumps(document, indent=2, sort_keys=True) + "\n"
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(encoded)
    path.chmod(0o444)


def load_json(path: Path, label: str) -> dict[str, object]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{label} must be a JSON object")
    return document


def read_pin(root: Path) -> dict[str, object]:
    pin_path = root / "upstream/sglang/pin.cuda12-compat-001.toml"
    pin = tomllib.loads(pin_path.read_text(encoding="utf-8"))
    bundle = pin.get("bundle")
    sglang = pin.get("sglang")
    model = pin.get("model")
    runtime_wheel = pin.get("runtime_wheel")
    ordinary_transport = pin.get("ordinary_dependency_transport")
    packaging = pin.get("cuda12_packaging")
    if bundle != {
        "id": BUNDLE_ID,
        "kind": "preformal_cuda12_compatibility_probe",
        "claim_state": "roadmap",
        "gate_decision": "N/A: this bundle cannot produce a G1 Gate result",
    }:
        raise ValueError("wrong CUDA12 compatibility bundle pin")
    if not all(isinstance(value, dict) for value in (sglang, model, runtime_wheel, ordinary_transport, packaging)):
        raise ValueError("CUDA12 compatibility pin is incomplete")
    assert isinstance(sglang, dict) and isinstance(model, dict)
    assert isinstance(runtime_wheel, dict) and isinstance(ordinary_transport, dict) and isinstance(packaging, dict)
    for field, length in (("base_commit", 40), ("base_tree", 40), ("source_seed_sha256", 64)):
        value = sglang.get(field)
        if not isinstance(value, str) or not re.fullmatch(rf"[0-9a-f]{{{length}}}", value):
            raise ValueError(f"invalid SGLang {field}")
    if not isinstance(sglang.get("remote"), str):
        raise ValueError("invalid SGLang remote")
    patches = sglang.get("patches")
    if not isinstance(patches, list) or len(patches) != 3:
        raise ValueError("CUDA12 compatibility pin must bind three patches")
    for index, patch in enumerate(patches, start=1):
        if not isinstance(patch, dict) or set(patch) != {"path", "sha256", "changed_paths"}:
            raise ValueError(f"invalid patch entry {index}")
        path = patch["path"]
        changed_paths = patch["changed_paths"]
        if (
            not isinstance(path, str)
            or Path(path).is_absolute()
            or ".." in Path(path).parts
            or not isinstance(changed_paths, list)
            or not changed_paths
            or any(not isinstance(item, str) or Path(item).is_absolute() or ".." in Path(item).parts for item in changed_paths)
        ):
            raise ValueError(f"invalid patch path entry {index}")
        require_sha256(patch["sha256"], f"patch {index} SHA-256")
        if sha256(root / path) != patch["sha256"]:
            raise ValueError(f"patch hash differs from pin: {path}")
    if not isinstance(model.get("inventory"), str) or not isinstance(model.get("repository"), str):
        raise ValueError("CUDA12 compatibility model pin is incomplete")
    if not isinstance(model.get("revision"), str) or model.get("local_only") is not True:
        raise ValueError("CUDA12 compatibility model pin does not require an offline model")
    if runtime_wheel != {
        "provenance_identity": "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite",
        "source_rebuild": False,
        "payload": "prebuilt G0 treatment runtime payload; only CUDA12 wheel METADATA and RECORD are rewritten",
        "base_wheel_attempt": "G0-C-011 attempt 005 treatment",
        "base_wheel_filename": "sglang-0.0.0.dev2+g734a8e921-cp312-cp312-linux_x86_64.whl",
        "base_wheel_sha256": "0874acca7b27e45ae39606eb12ee24a5f4cb17cd3791bb60fdccb95c332bf59e",
    }:
        raise ValueError("CUDA12 compatibility runtime-wheel pin differs")
    if ordinary_transport != {
        "index_url": "http://mirrors.cloud.aliyuncs.com/pypi/simple/",
        "trusted_host": "mirrors.cloud.aliyuncs.com",
        "evidence": "G0-C-011 attempt 005 resolved ordinary dependencies through this provider-internal mirror",
    }:
        raise ValueError("CUDA12 compatibility ordinary-dependency transport differs")
    required_packaging = {
        "source_evidence", "metadata_patch", "torch_version", "torchvision_version", "torchaudio_version",
        "torch_index_url", "deep_ep_version", "deep_ep_index_url", "sglang_kernel_version",
        "sglang_kernel_wheel_template", "deep_gemm_version", "deep_gemm_wheel_template",
        "full_docker_reproduction",
    }
    if set(packaging) != required_packaging:
        raise ValueError("CUDA12 compatibility packaging pin differs")
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
    if not path.is_file() or not path.is_absolute() or path.is_symlink():
        raise ValueError(f"{label} must be an existing absolute regular file")
    return {"path": path.name, "sha256": sha256(path), "size_bytes": path.stat().st_size}


def validate_toolgap_seed(archive_path: Path) -> None:
    names: set[str] = set()
    try:
        with tarfile.open(archive_path, "r:*") as archive:
            for member in archive.getmembers():
                pure = PurePosixPath(member.name)
                name = member.name.rstrip("/")
                if (
                    pure.is_absolute()
                    or ".." in pure.parts
                    or not pure.parts
                    or pure.parts[0] != "toolgap-source.git"
                    or name in names
                    or not (member.isdir() or member.isfile())
                ):
                    raise ValueError(f"unsafe ToolGap seed member: {member.name}")
                names.add(name)
    except tarfile.TarError as error:
        raise ValueError("ToolGap seed is not a readable archive") from error
    if not names:
        raise ValueError("ToolGap seed is empty")


def canonical_distribution(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def wheel_metadata(path: Path, label: str) -> tuple[str, str]:
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            metadata = [name for name in names if name.endswith(".dist-info/METADATA")]
            if len(metadata) != 1:
                raise ValueError(f"{label} must have exactly one wheel METADATA file")
            text = archive.read(metadata[0]).decode("utf-8")
    except (UnicodeDecodeError, zipfile.BadZipFile) as error:
        raise ValueError(f"{label} is not a readable wheel") from error
    values: dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            if key in {"Name", "Version"} and key not in values:
                values[key] = value.strip()
    if set(values) != {"Name", "Version"}:
        raise ValueError(f"{label} METADATA omits Name or Version")
    return values["Name"], values["Version"]


def wheelhouse_expectations(packaging: dict[str, object]) -> dict[str, tuple[str, str]]:
    values = {
        "sglang_kernel": ("sglang-kernel", f"{packaging['sglang_kernel_version']}+cu129"),
        "sgl_deep_ep": ("sgl-deep-ep", f"{packaging['deep_ep_version']}+cu129"),
        "sgl_deep_gemm": ("sgl-deep-gemm", f"{packaging['deep_gemm_version']}+cu129"),
        "torch": ("torch", f"{packaging['torch_version']}+cu129"),
        "torchvision": ("torchvision", f"{packaging['torchvision_version']}+cu129"),
        "torchaudio": ("torchaudio", f"{packaging['torchaudio_version']}+cu129"),
    }
    if set(values) != set(WHEELHOUSE_KEYS):
        raise ValueError("wheelhouse expectation set differs")
    return values


def validate_cuda_wheelhouse(archive_path: Path, packaging: dict[str, object]) -> None:
    with tempfile.TemporaryDirectory(prefix="cuda12-wheelhouse-validate-") as temp_dir:
        root = Path(temp_dir) / WHEELHOUSE_TOP_LEVEL
        root.mkdir()
        files: dict[str, Path] = {}
        try:
            with tarfile.open(archive_path, "r:*") as archive:
                for member in archive.getmembers():
                    pure = PurePosixPath(member.name)
                    member_name = member.name.rstrip("/")
                    if (
                        pure.is_absolute()
                        or ".." in pure.parts
                        or not pure.parts
                        or pure.parts[0] != WHEELHOUSE_TOP_LEVEL
                        or member_name in files
                        or not (member.isdir() or member.isfile())
                    ):
                        raise ValueError(f"unsafe CUDA wheelhouse member: {member.name}")
                    if member.isdir():
                        continue
                    if len(pure.parts) != 2:
                        raise ValueError(f"nested CUDA wheelhouse member: {member.name}")
                    source = archive.extractfile(member)
                    if source is None:
                        raise ValueError(f"unreadable CUDA wheelhouse member: {member.name}")
                    destination = root / pure.name
                    with source, destination.open("xb") as output:
                        shutil.copyfileobj(source, output, length=1024 * 1024)
                    destination.chmod(0o444)
                    files[member_name] = destination
        except tarfile.TarError as error:
            raise ValueError("CUDA wheelhouse is not a readable archive") from error
        index_path = f"{WHEELHOUSE_TOP_LEVEL}/wheelhouse-index.json"
        index_file = files.get(index_path)
        if index_file is None:
            raise ValueError("CUDA wheelhouse omits wheelhouse-index.json")
        try:
            index = json.loads(index_file.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("CUDA wheelhouse index is not valid JSON") from error
        if not isinstance(index, dict) or set(index) != {"schema_version", "wheels"} or index["schema_version"] != 1:
            raise ValueError("CUDA wheelhouse index schema differs")
        wheels = index["wheels"]
        if not isinstance(wheels, dict) or set(wheels) != set(WHEELHOUSE_KEYS):
            raise ValueError("CUDA wheelhouse package set differs")
        expectations = wheelhouse_expectations(packaging)
        expected_files = {index_path}
        for label, expected in expectations.items():
            entry = wheels[label]
            if (
                not isinstance(entry, dict)
                or set(entry) != {"path", "sha256", "size_bytes"}
                or not isinstance(entry["path"], str)
                or PurePosixPath(entry["path"]).name != entry["path"]
                or not entry["path"].endswith(".whl")
                or not isinstance(entry["size_bytes"], int)
                or entry["size_bytes"] < 1
            ):
                raise ValueError(f"invalid CUDA wheelhouse entry: {label}")
            require_sha256(entry["sha256"], f"CUDA wheelhouse {label} SHA-256")
            member_name = f"{WHEELHOUSE_TOP_LEVEL}/{entry['path']}"
            wheel_file = files.get(member_name)
            expected_files.add(member_name)
            if (
                wheel_file is None
                or wheel_file.stat().st_size != entry["size_bytes"]
                or sha256(wheel_file) != entry["sha256"]
            ):
                raise ValueError(f"CUDA wheelhouse index does not bind {label}")
            name, version = wheel_metadata(wheel_file, f"CUDA wheelhouse {label}")
            if canonical_distribution(name) != canonical_distribution(expected[0]) or version != expected[1]:
                raise ValueError(f"CUDA wheelhouse package identity differs: {label}")
        if set(files) != expected_files:
            raise ValueError("CUDA wheelhouse contains files outside its six-package boundary")


def validate_runtime_wheel_provenance(
    pin: dict[str, object], runtime_wheel: Path, provenance_path: Path
) -> None:
    provenance = load_json(provenance_path, "runtime wheel provenance")
    runtime = pin["runtime_wheel"]
    sglang = pin["sglang"]
    assert isinstance(runtime, dict) and isinstance(sglang, dict)
    if provenance.get("schema_version") != 1 or provenance.get("identity") != runtime["provenance_identity"]:
        raise ValueError("runtime wheel provenance identity differs")
    rebuild = provenance.get("source_rebuild")
    if not isinstance(rebuild, dict) or rebuild.get("performed") is not runtime["source_rebuild"]:
        raise ValueError("runtime wheel provenance source-rebuild claim differs")
    output = provenance.get("output_wheel")
    if not isinstance(output, dict) or set(output) != {
        "filename", "sha256", "size_bytes", "metadata_sha256", "record_sha256"
    }:
        raise ValueError("runtime wheel provenance output differs")
    if (
        not isinstance(output["filename"], str)
        or runtime_wheel.name != runtime["base_wheel_filename"]
        or output["filename"] != runtime_wheel.name
        or output["sha256"] != sha256(runtime_wheel)
        or output["size_bytes"] != runtime_wheel.stat().st_size
        or not all(re.fullmatch(r"[0-9a-f]{64}", str(output[field])) for field in ("sha256", "metadata_sha256", "record_sha256"))
    ):
        raise ValueError("runtime wheel provenance does not bind the pinned wheel filename")
    base = provenance.get("base_wheel")
    if (
        not isinstance(base, dict)
        or base.get("filename") != runtime["base_wheel_filename"]
        or base.get("sha256") != runtime["base_wheel_sha256"]
    ):
        raise ValueError("runtime wheel provenance does not bind the pinned G0 base wheel")
    patches = provenance.get("patches")
    pinned_patches = sglang["patches"]
    assert isinstance(pinned_patches, list)
    if not isinstance(patches, list) or len(patches) != len(pinned_patches):
        raise ValueError("runtime wheel provenance patch set differs")
    for label, observed, pinned in zip(("patch_one", "patch_two", "patch_three"), patches, pinned_patches):
        if (
            not isinstance(observed, dict)
            or observed.get("label") != label
            or not isinstance(observed.get("path"), str)
            or not Path(observed["path"]).is_absolute()
            or observed.get("sha256") != pinned["sha256"]
        ):
            raise ValueError("runtime wheel provenance patch differs from pin")
    rewrite = provenance.get("metadata_rewrite")
    substitutions = rewrite.get("exact_substitutions") if isinstance(rewrite, dict) else None
    expected_substitutions = [
        {"from": before, "to": after, "input_occurrences": 1, "output_occurrences": 1}
        for before, after in METADATA_REWRITE
    ]
    if substitutions != expected_substitutions:
        raise ValueError("runtime wheel provenance metadata rewrite differs")


def validate_manifest_schema(document: dict[str, object]) -> None:
    archives = document.get("archives")
    if not isinstance(archives, dict) or set(archives) != ARCHIVE_NAMES:
        raise ValueError("input manifest archive set differs")
    for label, entry in archives.items():
        if (
            not isinstance(entry, dict)
            or set(entry) != {"path", "sha256", "size_bytes"}
            or not isinstance(entry["path"], str)
            or Path(entry["path"]).name != entry["path"]
            or not isinstance(entry["sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])
            or not isinstance(entry["size_bytes"], int)
            or entry["size_bytes"] < 1
        ):
            raise ValueError(f"invalid input archive: {label}")


def expected(
    root: Path,
    toolgap: Path,
    sglang: Path,
    model: Path,
    runtime_wheel: Path,
    runtime_wheel_provenance: Path,
    cuda_wheelhouse: Path,
) -> dict[str, object]:
    if subprocess.run(
        ["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", *STATIC_PATHS],
        check=False,
    ).returncode:
        raise ValueError("CUDA12 compatibility static inputs must match the frozen ToolGap commit")
    pin = read_pin(root)
    pin_sglang = pin["sglang"]
    pin_model = pin["model"]
    packaging = pin["cuda12_packaging"]
    assert isinstance(pin_sglang, dict) and isinstance(pin_model, dict) and isinstance(packaging, dict)
    model_inventory = root / str(pin_model["inventory"])
    model_doc = json.loads(model_inventory.read_text(encoding="utf-8"))
    if model_doc.get("repository") != pin_model["repository"] or model_doc.get("revision") != pin_model["revision"]:
        raise ValueError("model inventory differs from pin")
    sglang_entry = archive_entry(sglang, "SGLang seed")
    if sglang_entry["sha256"] != pin_sglang["source_seed_sha256"]:
        raise ValueError("SGLang seed differs from fixed pin")
    runtime_entry = archive_entry(runtime_wheel, "runtime wheel")
    provenance_entry = archive_entry(runtime_wheel_provenance, "runtime wheel provenance")
    cuda_wheelhouse_entry = archive_entry(cuda_wheelhouse, "CUDA wheelhouse")
    validate_toolgap_seed(toolgap.resolve())
    validate_runtime_wheel_provenance(pin, runtime_wheel.resolve(), runtime_wheel_provenance.resolve())
    validate_cuda_wheelhouse(cuda_wheelhouse.resolve(), packaging)
    document = {
        "schema_version": 1,
        "identity": {
            "bundle_id": BUNDLE_ID,
            "claim_state": "roadmap",
            "gate": "G1",
            "gate_decision": INPUT_GATE_DECISION,
            "toolgap_commit": git(root, "rev-parse", "HEAD"),
            "toolgap_remote": git(root, "remote", "get-url", "origin"),
            "toolgap_tree": git(root, "rev-parse", "HEAD^{tree}"),
        },
        "archives": {
            "cuda_wheelhouse": cuda_wheelhouse_entry,
            "model_snapshot": archive_entry(model, "model snapshot"),
            "runtime_wheel": runtime_entry,
            "runtime_wheel_provenance": provenance_entry,
            "sglang_source_seed": sglang_entry,
            "toolgap_source_seed": archive_entry(toolgap, "ToolGap seed"),
        },
        "model": {
            "inventory_path": str(pin_model["inventory"]),
            "inventory_sha256": sha256(model_inventory),
            "local_only": True,
            "repository": pin_model["repository"],
            "revision": pin_model["revision"],
        },
        "static_inputs": static_hashes(root),
    }
    validate_manifest_schema(document)
    return document


def create(args: argparse.Namespace) -> int:
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"refusing to replace input manifest: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json_exclusive(
        output,
        expected(
            args.repo_root.resolve(), args.toolgap_seed, args.sglang_seed,
            args.model_snapshot, args.runtime_wheel, args.runtime_wheel_provenance,
            args.cuda_wheelhouse,
        ),
    )
    print(output)
    return 0


def verify(args: argparse.Namespace) -> int:
    manifest = args.manifest.resolve()
    if not manifest.is_file():
        raise ValueError("missing input manifest")
    observed = load_json(manifest, "input manifest")
    actual = expected(
        args.repo_root.resolve(), args.toolgap_seed, args.sglang_seed,
        args.model_snapshot, args.runtime_wheel, args.runtime_wheel_provenance,
        args.cuda_wheelhouse,
    )
    validate_manifest_schema(observed)
    if observed != actual:
        raise ValueError("input manifest differs from current clean inputs")
    print(f"VERIFIED_CUDA12_COMPAT_INPUT_MANIFEST: {manifest}")
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
        command.add_argument("--runtime-wheel", required=True, type=Path)
        command.add_argument("--runtime-wheel-provenance", required=True, type=Path)
        command.add_argument("--cuda-wheelhouse", required=True, type=Path)
        if name == "create":
            command.add_argument("--output", required=True, type=Path)
        else:
            command.add_argument("--manifest", required=True, type=Path)
        command.set_defaults(handler=handler)
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
