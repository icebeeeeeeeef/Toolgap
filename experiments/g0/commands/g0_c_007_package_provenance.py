#!/usr/bin/env python3
"""Prove that a G0 arm imports modules from its installed wheel, not a checkout."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from pathlib import Path


MODULES = {
    "session_ref_tracker": (
        "sglang.srt.mem_cache.unified_cache.session_ref_tracker",
        "python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py",
    ),
    "unified_tree_core": (
        "sglang.srt.mem_cache.unified_cache.unified_tree_core",
        "python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py",
    ),
    "unified_tree_core_interface": (
        "sglang.srt.mem_cache.unified_cache.unified_tree_core_interface",
        "python/sglang/srt/mem_cache/unified_cache/unified_tree_core_interface.py",
    ),
    "unified_radix_cache": (
        "sglang.srt.mem_cache.unified_radix_cache",
        "python/sglang/srt/mem_cache/unified_radix_cache.py",
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    if not (source_root / "python" / "sglang").is_dir():
        raise ValueError(f"not a complete SGLang checkout: {source_root}")

    modules: dict[str, dict[str, object]] = {}
    passed = True
    for label, (module_name, relative_source) in MODULES.items():
        module = importlib.import_module(module_name)
        installed = Path(module.__file__).resolve()
        source = source_root / relative_source
        match = source.is_file() and sha256(installed) == sha256(source)
        outside_checkout = not under(installed, source_root)
        passed = passed and match and outside_checkout
        modules[label] = {
            "module": module_name,
            "installed_path": str(installed),
            "source_path": str(source),
            "installed_sha256": sha256(installed),
            "source_sha256": sha256(source) if source.is_file() else None,
            "hash_matches_source": match,
            "outside_source_checkout": outside_checkout,
        }

    document = {
        "interpreter": sys.executable,
        "sys_path": sys.path,
        "source_root": str(source_root),
        "modules": modules,
        "passed": passed,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
