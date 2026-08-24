#!/usr/bin/env python3
"""Repackage a proven G0 wheel with the CUDA 12 metadata transformation.

This is deliberately not a source build.  It accepts a prebuilt G0 Linux wheel
only when its Python package payload is byte-for-byte the same as the supplied
three-patch source tree, except for the build-generated ``sglang/_version.py``.
"""

from __future__ import annotations

import argparse
import base64
import copy
import csv
import fnmatch
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import zipfile


class RepackageError(RuntimeError):
    """The input wheel or source tree cannot establish the required identity."""


REPLACEMENTS = (
    (b"cuda-python>=13.0", b"cuda-python>=12,<13"),
    (b"flashinfer_python[cu13]", b"flashinfer_python[cu12]"),
    (b"humming-kernels[cu13]==0.1.10", b"humming-kernels[cu12]==0.1.10"),
    (b"nvidia-cutlass-dsl[cu13]==4.6.2", b"nvidia-cutlass-dsl==4.6.2"),
)
ALLOWED_DIFFERENCE = "sglang/_version.py"
IDENTITY = "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite"
G0_BASE_WHEEL_FILENAME = "sglang-0.0.0.dev2+g734a8e921-cp312-cp312-linux_x86_64.whl"
G0_BASE_WHEEL_SHA256 = "0874acca7b27e45ae39606eb12ee24a5f4cb17cd3791bb60fdccb95c332bf59e"
EXPECTED_SOURCE_EXCLUSION_PATTERNS = ("kernels/aot/*", "kernels/aot/**/*")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_hash(value: bytes) -> str:
    encoded = base64.urlsafe_b64encode(hashlib.sha256(value).digest()).rstrip(b"=")
    return "sha256=" + encoded.decode("ascii")


def reject_unsafe_zip_name(name: str) -> None:
    if not name or "\\" in name or name.startswith("/"):
        raise RepackageError(f"wheel has an unsafe archive name: {name!r}")
    parts = PurePosixPath(name).parts
    if any(part in {"", ".", ".."} for part in parts):
        raise RepackageError(f"wheel has an unsafe archive name: {name!r}")


def read_wheel_entries(wheel: Path) -> tuple[zipfile.ZipFile, list[zipfile.ZipInfo]]:
    archive = zipfile.ZipFile(wheel, "r")
    infos = archive.infolist()
    names: set[str] = set()
    for info in infos:
        reject_unsafe_zip_name(info.filename)
        if info.filename in names:
            archive.close()
            raise RepackageError(f"wheel has a duplicate archive entry: {info.filename}")
        names.add(info.filename)
    return archive, infos


def find_metadata_and_record(infos: list[zipfile.ZipInfo]) -> tuple[str, str]:
    metadata = [info.filename for info in infos if info.filename.endswith(".dist-info/METADATA")]
    records = [info.filename for info in infos if info.filename.endswith(".dist-info/RECORD")]
    if len(metadata) != 1 or len(records) != 1:
        raise RepackageError(
            "wheel must contain exactly one .dist-info/METADATA and one .dist-info/RECORD"
        )
    metadata_path = metadata[0]
    record_path = records[0]
    if metadata_path.rsplit("/", 1)[0] != record_path.rsplit("/", 1)[0]:
        raise RepackageError("wheel METADATA and RECORD must be in the same .dist-info directory")
    return metadata_path, record_path


def parse_record(record_bytes: bytes, expected_paths: set[str], record_path: str) -> list[list[str]]:
    try:
        rows = list(csv.reader(io.StringIO(record_bytes.decode("utf-8"), newline="")))
    except UnicodeDecodeError as error:
        raise RepackageError("wheel RECORD is not UTF-8") from error
    if not rows:
        raise RepackageError("wheel RECORD is empty")

    recorded_paths: set[str] = set()
    for row in rows:
        if len(row) != 3 or not row[0]:
            raise RepackageError("wheel RECORD must contain exactly three fields per entry")
        path, digest, size = row
        reject_unsafe_zip_name(path)
        if path in recorded_paths:
            raise RepackageError(f"wheel RECORD has a duplicate entry: {path}")
        recorded_paths.add(path)
        if path not in expected_paths:
            raise RepackageError(f"wheel RECORD refers to a missing entry: {path}")
        if path == record_path:
            if digest or size:
                raise RepackageError("wheel RECORD entry must not hash or size itself")
        elif not digest.startswith("sha256=") or not size.isdecimal():
            raise RepackageError(f"wheel RECORD entry is not a SHA-256 digest and size: {path}")

    if recorded_paths != expected_paths:
        missing = sorted(expected_paths - recorded_paths)
        extra = sorted(recorded_paths - expected_paths)
        raise RepackageError(
            f"wheel RECORD does not cover wheel entries; missing={missing[:3]!r} extra={extra[:3]!r}"
        )
    return rows


def validate_record_payloads(
    archive: zipfile.ZipFile, rows: list[list[str]], record_path: str
) -> None:
    for path, digest, size in rows:
        if path == record_path:
            continue
        value = archive.read(path)
        if digest != record_hash(value) or size != str(len(value)):
            raise RepackageError(f"wheel RECORD does not match payload: {path}")


def wheel_python_payload(archive: zipfile.ZipFile, infos: list[zipfile.ZipInfo]) -> dict[str, bytes]:
    payload: dict[str, bytes] = {}
    for info in infos:
        name = info.filename
        if not info.is_dir() and name.startswith("sglang/") and name.endswith(".py"):
            payload[name] = archive.read(name)
    if not payload:
        raise RepackageError("wheel has no sglang Python package payload")
    return payload


def source_exclusion_patterns(pyproject: Path) -> list[str]:
    """Read the one setuptools package-data list needed for payload identity.

    The experiment has to run with the G0 Python 3.8 control tool as well as
    the cp312 payload, so this deliberately parses only the simple quoted list
    in the pinned pyproject instead of depending on Python 3.11 ``tomllib``.
    """

    try:
        lines = pyproject.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise RepackageError(f"cannot read source pyproject: {pyproject}") from error

    in_section = False
    assignment: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if in_section:
                break
            in_section = stripped == "[tool.setuptools.exclude-package-data]"
            continue
        if not in_section:
            continue
        if not assignment:
            if re.match(r'^"sglang"\s*=\s*\[', stripped):
                assignment.append(stripped)
                if "]" in stripped:
                    break
        else:
            assignment.append(stripped)
            if "]" in stripped:
                break
    if not assignment:
        raise RepackageError(
            "source root must provide [tool.setuptools.exclude-package-data] sglang patterns"
        )
    list_text = "\n".join(assignment).split("=", 1)[1]
    patterns = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', list_text)
    if tuple(patterns) != EXPECTED_SOURCE_EXCLUSION_PATTERNS:
        raise RepackageError(
            "source package exclusion patterns differ from the pinned G0 package payload rule"
        )
    return patterns


def validate_source_cuda12_metadata(pyproject: Path) -> None:
    try:
        contents = pyproject.read_bytes()
    except OSError as error:
        raise RepackageError(f"cannot read source pyproject: {pyproject}") from error
    for before, after in REPLACEMENTS:
        if contents.count(before) != 0 or contents.count(after) != 1:
            raise RepackageError(
                "source pyproject does not contain exactly the required CUDA12 metadata "
                f"transformation: {before!r} -> {after!r}"
            )


def source_python_payload(
    source_root: Path,
) -> tuple[dict[str, bytes], dict[str, str], list[str], str]:
    package_root = source_root / "python" / "sglang"
    if not package_root.is_dir():
        raise RepackageError(f"source root does not contain python/sglang: {source_root}")

    pyproject = source_root / "python" / "pyproject.toml"
    excluded_patterns = source_exclusion_patterns(pyproject)
    validate_source_cuda12_metadata(pyproject)

    payload: dict[str, bytes] = {}
    excluded: dict[str, str] = {}
    for path in sorted(package_root.rglob("*.py")):
        if path.is_symlink() or not path.is_file():
            raise RepackageError(f"source Python payload must be a regular file: {path}")
        relative = path.relative_to(source_root / "python").as_posix()
        package_relative = path.relative_to(package_root).as_posix()
        value = path.read_bytes()
        if any(fnmatch.fnmatchcase(package_relative, pattern) for pattern in excluded_patterns):
            excluded[relative] = sha256_bytes(value)
        else:
            payload[relative] = value
    if not payload:
        raise RepackageError("source root has no Python files under python/sglang")
    return payload, excluded, excluded_patterns, sha256_file(pyproject)


def validate_python_payload(
    wheel_payload: dict[str, bytes], source_payload: dict[str, bytes]
) -> tuple[dict[str, str], dict[str, object]]:
    wheel_paths = set(wheel_payload) - {ALLOWED_DIFFERENCE}
    source_paths = set(source_payload) - {ALLOWED_DIFFERENCE}
    if wheel_paths != source_paths:
        missing = sorted(source_paths - wheel_paths)
        extra = sorted(wheel_paths - source_paths)
        raise RepackageError(
            "wheel/source Python package payload paths differ; "
            f"missing_in_wheel={missing[:5]!r} extra_in_wheel={extra[:5]!r}"
        )
    if ALLOWED_DIFFERENCE not in wheel_payload:
        raise RepackageError(f"wheel payload lacks required allowed difference: {ALLOWED_DIFFERENCE}")

    matching_hashes: dict[str, str] = {}
    for path in sorted(wheel_paths):
        wheel_value = wheel_payload[path]
        source_value = source_payload[path]
        if path == ALLOWED_DIFFERENCE:
            continue
        if wheel_value != source_value:
            raise RepackageError(f"wheel/source Python payload differs outside {ALLOWED_DIFFERENCE}: {path}")
        matching_hashes[path] = sha256_bytes(wheel_value)

    source_version = source_payload.get(ALLOWED_DIFFERENCE)
    allowed = {
        "path": ALLOWED_DIFFERENCE,
        "base_wheel_sha256": sha256_bytes(wheel_payload[ALLOWED_DIFFERENCE]),
        "source_sha256": sha256_bytes(source_version) if source_version is not None else None,
        "source_present": source_version is not None,
        "bytes_equal": wheel_payload[ALLOWED_DIFFERENCE] == source_version,
        "statement": "The wheel may carry setuptools-scm generated sglang/_version.py even when the source checkout does not.",
    }
    return matching_hashes, allowed


def rewrite_metadata(metadata: bytes) -> tuple[bytes, list[dict[str, object]]]:
    rewritten = metadata
    substitutions: list[dict[str, object]] = []
    for before, after in REPLACEMENTS:
        if rewritten.count(before) != 1:
            raise RepackageError(f"METADATA must contain exactly one occurrence of {before!r}")
        if rewritten.count(after) != 0:
            raise RepackageError(f"METADATA already contains replacement {after!r}")
        rewritten = rewritten.replace(before, after)
        substitutions.append(
            {
                "from": before.decode("ascii"),
                "to": after.decode("ascii"),
                "input_occurrences": 1,
                "output_occurrences": 1,
            }
        )
    return rewritten, substitutions


def rewrite_record(rows: list[list[str]], metadata_path: str, rewritten_metadata: bytes) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    found_metadata = False
    for path, digest, size in rows:
        if path == metadata_path:
            writer.writerow((path, record_hash(rewritten_metadata), str(len(rewritten_metadata))))
            found_metadata = True
        else:
            writer.writerow((path, digest, size))
    if not found_metadata:
        raise RepackageError("wheel RECORD does not contain its METADATA entry")
    return output.getvalue().encode("utf-8")


def write_wheel(
    source: zipfile.ZipFile,
    infos: list[zipfile.ZipInfo],
    metadata_path: str,
    record_path: str,
    rewritten_metadata: bytes,
    rewritten_record: bytes,
    temporary_output: Path,
) -> None:
    with zipfile.ZipFile(temporary_output, "w", allowZip64=True) as destination:
        destination.comment = source.comment
        for info in infos:
            if info.filename == metadata_path:
                value = rewritten_metadata
            elif info.filename == record_path:
                value = rewritten_record
            else:
                value = source.read(info.filename)
            # ZipFile updates header offsets on the ZipInfo it is given.  Keep the
            # source info intact because later entries still read from that archive.
            destination.writestr(copy.copy(info), value, compress_type=info.compress_type)


def verify_output_wheel(
    output: Path,
    source: zipfile.ZipFile,
    original_entries: list[zipfile.ZipInfo],
    metadata_path: str,
    record_path: str,
    rewritten_metadata: bytes,
    input_rows: list[list[str]],
) -> tuple[str, str]:
    archive, infos = read_wheel_entries(output)
    try:
        if [info.filename for info in infos] != [info.filename for info in original_entries]:
            raise RepackageError("output wheel changed the archive entry list")
        found_metadata, found_record = find_metadata_and_record(infos)
        if (found_metadata, found_record) != (metadata_path, record_path):
            raise RepackageError("output wheel changed .dist-info identity")
        if archive.read(metadata_path) != rewritten_metadata:
            raise RepackageError("output wheel METADATA does not equal the requested rewrite")
        expected_paths = {info.filename for info in infos if not info.is_dir()}
        rows = parse_record(archive.read(record_path), expected_paths, record_path)
        validate_record_payloads(archive, rows, record_path)
        if len(rows) != len(input_rows):
            raise RepackageError("output wheel changed RECORD entry count")
        for input_row, output_row in zip(input_rows, rows):
            if input_row[0] != output_row[0]:
                raise RepackageError("output wheel changed RECORD entry order")
            if input_row[0] == metadata_path:
                if output_row != [
                    metadata_path,
                    record_hash(rewritten_metadata),
                    str(len(rewritten_metadata)),
                ]:
                    raise RepackageError("output wheel RECORD has an invalid METADATA entry")
            elif input_row != output_row:
                raise RepackageError(f"output wheel changed unrelated RECORD entry: {input_row[0]}")
        for info in original_entries:
            if info.is_dir() or info.filename in {metadata_path, record_path}:
                continue
            if archive.read(info.filename) != source.read(info.filename):
                raise RepackageError(f"output wheel changed unrelated payload: {info.filename}")
        return sha256_bytes(archive.read(metadata_path)), sha256_bytes(archive.read(record_path))
    finally:
        archive.close()


def publish_exclusive(temporary_path: Path, final_path: Path) -> None:
    try:
        os.link(temporary_path, final_path)
    except FileExistsError as error:
        raise RepackageError(f"refusing to overwrite existing output: {final_path}") from error
    finally:
        temporary_path.unlink(missing_ok=True)


def write_json_exclusive(path: Path, value: dict[str, object]) -> None:
    encoded = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as error:
        raise RepackageError(f"refusing to overwrite existing provenance: {path}") from error
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def require_new_output(path: Path, label: str) -> None:
    if not path.parent.is_dir():
        raise RepackageError(f"{label} parent directory does not exist: {path.parent}")
    if path.exists() or path.is_symlink():
        raise RepackageError(f"refusing to overwrite existing {label}: {path}")


def repackage(args: argparse.Namespace) -> dict[str, object]:
    base_wheel = args.base_wheel.resolve(strict=True)
    if not base_wheel.is_file():
        raise RepackageError(f"base wheel is not a regular file: {base_wheel}")
    if (
        base_wheel.name != G0_BASE_WHEEL_FILENAME
        or sha256_file(base_wheel) != G0_BASE_WHEEL_SHA256
    ):
        raise RepackageError("base wheel is not the pinned G0-C-011 treatment artifact")
    output_wheel = args.output_wheel.absolute()
    provenance = args.provenance.absolute()
    if output_wheel == base_wheel:
        raise RepackageError("output wheel must not overwrite the base wheel")
    require_new_output(output_wheel, "output wheel")
    require_new_output(provenance, "provenance")

    source_root = args.source_root.resolve(strict=True)
    patches = []
    for label, path in (
        ("patch_one", args.patch_one),
        ("patch_two", args.patch_two),
        ("patch_three", args.patch_three),
    ):
        resolved = path.resolve(strict=True)
        if not resolved.is_file() or resolved.is_symlink():
            raise RepackageError(f"{label} is not a regular patch file: {resolved}")
        patches.append({"label": label, "path": str(resolved), "sha256": sha256_file(resolved)})

    archive, infos = read_wheel_entries(base_wheel)
    try:
        metadata_path, record_path = find_metadata_and_record(infos)
        expected_paths = {info.filename for info in infos if not info.is_dir()}
        input_record = archive.read(record_path)
        input_rows = parse_record(input_record, expected_paths, record_path)
        validate_record_payloads(archive, input_rows, record_path)

        wheel_payload = wheel_python_payload(archive, infos)
        source_payload, source_excluded, exclusion_patterns, pyproject_sha256 = source_python_payload(
            source_root
        )
        matching_hashes, allowed_difference = validate_python_payload(wheel_payload, source_payload)

        input_metadata = archive.read(metadata_path)
        rewritten_metadata, substitutions = rewrite_metadata(input_metadata)
        rewritten_record = rewrite_record(input_rows, metadata_path, rewritten_metadata)

        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{output_wheel.name}.", suffix=".tmp", dir=output_wheel.parent
        )
        os.close(descriptor)
        temporary_output = Path(temporary_name)
        try:
            write_wheel(
                archive,
                infos,
                metadata_path,
                record_path,
                rewritten_metadata,
                rewritten_record,
                temporary_output,
            )
            output_metadata_sha256, output_record_sha256 = verify_output_wheel(
                temporary_output,
                archive,
                infos,
                metadata_path,
                record_path,
                rewritten_metadata,
                input_rows,
            )
            output_sha256 = sha256_file(temporary_output)
            output_size = temporary_output.stat().st_size
            publish_exclusive(temporary_output, output_wheel)
        finally:
            temporary_output.unlink(missing_ok=True)
    finally:
        archive.close()

    payload_manifest = json.dumps(
        matching_hashes, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    provenance_value: dict[str, object] = {
        "schema_version": 1,
        "identity": IDENTITY,
        "source_rebuild": {
            "performed": False,
            "statement": "This is not a current three-patch source rebuild; it is a G0 prebuilt runtime payload with only the documented CUDA12 METADATA rewrite.",
        },
        "base_wheel": {
            "filename": base_wheel.name,
            "sha256": sha256_file(base_wheel),
            "size_bytes": base_wheel.stat().st_size,
            "metadata_path": metadata_path,
            "metadata_sha256": sha256_bytes(input_metadata),
            "record_path": record_path,
            "record_sha256": sha256_bytes(input_record),
        },
        "output_wheel": {
            "filename": output_wheel.name,
            "sha256": output_sha256,
            "size_bytes": output_size,
            "metadata_sha256": output_metadata_sha256,
            "record_sha256": output_record_sha256,
        },
        "patches": patches,
        "metadata_rewrite": {"exact_substitutions": substitutions},
        "source_payload_validation": {
            "source_root": str(source_root),
            "package_root": str(source_root / "python" / "sglang"),
            "comparison": "all package-payload sglang/**/*.py paths must match; files excluded by the source pyproject package-data rule are not package payload; every remaining file except sglang/_version.py must be byte-identical",
            "source_pyproject_sha256": pyproject_sha256,
            "source_cuda12_metadata_transformation_verified": True,
            "source_package_exclusion_patterns": exclusion_patterns,
            "source_excluded_by_package_data_sha256": source_excluded,
            "matched_non_version_python_file_count": len(matching_hashes),
            "matched_non_version_python_files_sha256": matching_hashes,
            "matched_non_version_manifest_sha256": sha256_bytes(payload_manifest),
            "allowed_difference": allowed_difference,
        },
    }
    write_json_exclusive(provenance, provenance_value)
    provenance_value["provenance_path"] = str(provenance)
    return provenance_value


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-wheel", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--patch-one", required=True, type=Path)
    parser.add_argument("--patch-two", required=True, type=Path)
    parser.add_argument("--patch-three", required=True, type=Path)
    parser.add_argument("--output-wheel", required=True, type=Path)
    parser.add_argument("--provenance", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        result = repackage(parse_args(argv))
    except (OSError, RepackageError, zipfile.BadZipFile) as error:
        print(f"cuda12 wheel repackage failed: {error}", file=sys.stderr)
        return 2
    print(
        "CUDA12_COMPAT_001_WHEEL_REPACKAGED "
        f"output_sha256={result['output_wheel']['sha256']} "
        f"provenance={result['provenance_path']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
