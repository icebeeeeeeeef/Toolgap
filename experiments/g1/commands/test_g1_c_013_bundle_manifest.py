#!/usr/bin/env python3
"""Local create/verify round-trip regression for the G1-C-013 builder."""

from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

MODULE = Path(__file__).with_name("g1_c_013_bundle_manifest.py")
SPEC = importlib.util.spec_from_file_location("g1_c_013_bundle_manifest", MODULE)
assert SPEC is not None and SPEC.loader is not None
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


def write_seed(path: Path, top_level: str) -> None:
    payload = b"fixture\n"
    member = tarfile.TarInfo(f"{top_level}/fixture")
    member.size = len(payload)
    with tarfile.open(path, "w:gz") as archive:
        archive.addfile(member, io.BytesIO(payload))


def write_wheel(path: Path, distribution: str) -> None:
    metadata = f"Metadata-Version: 2.1\nName: {distribution}\nVersion: 1.0\n"
    dist_info = distribution.replace("-", "_") + "-1.0.dist-info"
    with zipfile.ZipFile(path, "w") as wheel:
        wheel.writestr(f"{dist_info}/METADATA", metadata)


def write_wheelhouse(path: Path, root: Path) -> None:
    wheelhouse = root / BUILDER.WHEELHOUSE_ROOT
    wheelhouse.mkdir()
    entries = {}
    for label, distribution in BUILDER.WHEELHOUSE_NAMES.items():
        wheel = wheelhouse / f"{distribution.replace('-', '_')}-1.0-py3-none-any.whl"
        write_wheel(wheel, distribution)
        entries[label] = {
            "path": wheel.name,
            "sha256": BUILDER.digest(wheel),
            "size_bytes": wheel.stat().st_size,
        }
    (wheelhouse / "wheelhouse-index.json").write_text(
        json.dumps({"schema_version": 1, "wheels": entries}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with tarfile.open(path, "w:gz") as archive:
        for member in sorted(wheelhouse.iterdir()):
            archive.add(member, arcname=f"{BUILDER.WHEELHOUSE_ROOT}/{member.name}")


def write_repository(root: Path) -> None:
    for relative in BUILDER.STATIC_PATHS:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if relative == BUILDER.MODEL_INVENTORY:
            path.write_text(json.dumps({
                "repository": BUILDER.MODEL_REPOSITORY,
                "revision": BUILDER.MODEL_REVISION,
            }) + "\n", encoding="utf-8")
        else:
            path.write_text(f"fixture:{relative}\n", encoding="utf-8")
    commands = (
        ("git", "init", "-q"),
        ("git", "config", "user.name", "G1-C-013 Test"),
        ("git", "config", "user.email", "g1-c-013-test@invalid"),
        ("git", "remote", "add", "origin", "https://example.invalid/Toolgap.git"),
        ("git", "add", "."),
        ("git", "commit", "-q", "-m", "fixture"),
    )
    for command in commands:
        subprocess.run(command, cwd=root, check=True)


def write_runtime_provenance(root: Path, wheel: Path, output: Path) -> None:
    substitutions = [
        {"from": before, "to": after, "input_occurrences": 1, "output_occurrences": 1}
        for before, after in (
            ("cuda-python>=13.0", "cuda-python>=12,<13"),
            ("flashinfer_python[cu13]", "flashinfer_python[cu12]"),
            ("humming-kernels[cu13]==0.1.10", "humming-kernels[cu12]==0.1.10"),
            ("nvidia-cutlass-dsl[cu13]==4.6.2", "nvidia-cutlass-dsl==4.6.2"),
        )
    ]
    patches = []
    for label, relative in zip(("patch_one", "patch_two", "patch_three"), BUILDER.PATCH_PATHS):
        patch = (root / relative).resolve()
        patches.append({"label": label, "path": str(patch), "sha256": BUILDER.digest(patch)})
    output.write_text(json.dumps({
        "base_wheel": {
            "filename": BUILDER.G0_RUNTIME_WHEEL,
            "sha256": BUILDER.G0_RUNTIME_WHEEL_SHA256,
        },
        "identity": BUILDER.RUNTIME_PROVENANCE,
        "metadata_rewrite": {"exact_substitutions": substitutions},
        "output_wheel": {
            "filename": BUILDER.G0_RUNTIME_WHEEL,
            "metadata_sha256": "1" * 64,
            "record_sha256": "2" * 64,
            "sha256": BUILDER.digest(wheel),
            "size_bytes": wheel.stat().st_size,
        },
        "patches": patches,
        "schema_version": 1,
        "source_rebuild": {"performed": False},
    }, sort_keys=True) + "\n", encoding="utf-8")


class G1C007BundleManifestTests(unittest.TestCase):
    def test_cli_parser_create_then_verify_uses_local_frozen_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            repo = fixture / "repo"
            repo.mkdir()
            write_repository(repo)

            toolgap_seed = fixture / "toolgap-source.tar.gz"
            sglang_seed = fixture / "sglang-source.tar.gz"
            model_snapshot = fixture / "model-snapshot.tar"
            runtime_wheel = fixture / BUILDER.G0_RUNTIME_WHEEL
            runtime_provenance = fixture / "runtime-wheel-provenance.json"
            cuda_wheelhouse = fixture / "cuda-wheelhouse.tar.gz"
            output = fixture / "input-manifest.json"
            write_seed(toolgap_seed, "toolgap-source.git")
            write_seed(sglang_seed, "sglang-source.git")
            model_snapshot.write_bytes(b"model fixture\n")
            write_wheel(runtime_wheel, "sglang")
            write_runtime_provenance(repo, runtime_wheel, runtime_provenance)
            write_wheelhouse(cuda_wheelhouse, fixture)

            common = [
                "--repo-root", str(repo),
                "--toolgap-seed", str(toolgap_seed),
                "--sglang-seed", str(sglang_seed),
                "--model-snapshot", str(model_snapshot),
                "--runtime-wheel", str(runtime_wheel),
                "--runtime-wheel-provenance", str(runtime_provenance),
                "--cuda-wheelhouse", str(cuda_wheelhouse),
            ]
            original_seed_digest = BUILDER.SGLANG_SEED_SHA256
            BUILDER.SGLANG_SEED_SHA256 = BUILDER.digest(sglang_seed)
            try:
                create_args = BUILDER.parser().parse_args(["create", *common, "--output", str(output)])
                self.assertEqual(create_args.handler(create_args), 0)
                verify_args = BUILDER.parser().parse_args(["verify", *common, "--manifest", str(output)])
                self.assertEqual(verify_args.handler(verify_args), 0)
            finally:
                BUILDER.SGLANG_SEED_SHA256 = original_seed_digest

            manifest = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(
                manifest["storage_preflight"],
                {"minimum_free_bytes": BUILDER.MINIMUM_FREE_BYTES},
            )
            self.assertEqual(set(manifest["static_inputs"]), set(BUILDER.STATIC_PATHS))
            self.assertEqual(output.stat().st_mode & 0o777, 0o444)
            for mutate in (
                lambda value: value.__setitem__("schema_version", True),
                lambda value: value["archives"]["runtime_wheel"].__setitem__("size_bytes", True),
                lambda value: value["storage_preflight"].__setitem__("minimum_free_bytes", True),
                lambda value: next(iter(value["static_inputs"].values())).__setitem__("size_bytes", True),
            ):
                with self.subTest(mutate=mutate):
                    malformed = json.loads(json.dumps(manifest))
                    mutate(malformed)
                    with self.assertRaises(ValueError):
                        BUILDER.validate_schema(malformed)


if __name__ == "__main__":
    unittest.main()
