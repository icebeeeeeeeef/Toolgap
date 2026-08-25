#!/usr/bin/env python3
"""Create/verify round-trip regression for the G1-C-007 input manifest."""

from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

MODULE = Path(__file__).with_name("g1_c_007_bundle_manifest.py")
SPEC = importlib.util.spec_from_file_location("g1_c_007_bundle_manifest", MODULE)
assert SPEC is not None and SPEC.loader is not None
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


def manifest() -> dict[str, object]:
    return {
        "schema_version": 1,
        "identity": {"bundle_id": "G1-C-007"},
        "archives": {name: {} for name in BUILDER.ARCHIVE_NAMES},
        "model": {},
        "patches": [],
        "ordinary_dependency_transport": {},
        "storage_preflight": {"minimum_free_bytes": BUILDER.MINIMUM_FREE_BYTES},
        "static_inputs": {},
    }


class G1C007BundleManifestTests(unittest.TestCase):
    def test_create_then_verify_preserves_exact_manifest_schema(self) -> None:
        expected = manifest()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "input-manifest.json"
            with mock.patch.object(BUILDER, "manifest_expected", return_value=expected):
                self.assertEqual(
                    BUILDER.create(argparse.Namespace(output=output)),
                    0,
                )
                self.assertEqual(
                    BUILDER.verify(argparse.Namespace(manifest=output)),
                    0,
                )
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), expected)
            self.assertEqual(output.stat().st_mode & 0o777, 0o444)


if __name__ == "__main__":
    unittest.main()
