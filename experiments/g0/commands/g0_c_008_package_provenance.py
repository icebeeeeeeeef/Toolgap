#!/usr/bin/env python3
"""Bind one G0-C-008 arm to its interpreter, venv, wheel, and checkout."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
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


def write_json_exclusive(path: Path, document: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode=0o444)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
    path.chmod(0o444)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--install-root", required=True, type=Path)
    parser.add_argument("--expected-interpreter", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    install_root = args.install_root.resolve()
    expected_interpreter = Path(os.path.abspath(args.expected_interpreter))
    actual_interpreter = Path(os.path.abspath(sys.executable))
    if not (source_root / "python" / "sglang").is_dir():
        raise ValueError(f"not a complete SGLang checkout: {source_root}")

    package = importlib.import_module("sglang")
    package_path = Path(package.__file__).resolve()
    package_under_install_root = under(package_path, install_root)
    interpreter_matches = actual_interpreter == expected_interpreter
    modules: dict[str, dict[str, object]] = {}
    passed = package_under_install_root and interpreter_matches
    for label, (module_name, relative_source) in MODULES.items():
        module = importlib.import_module(module_name)
        installed = Path(module.__file__).resolve()
        source = source_root / relative_source
        match = source.is_file() and sha256(installed) == sha256(source)
        installed_under_root = under(installed, install_root)
        outside_checkout = not under(installed, source_root)
        passed = passed and match and installed_under_root and outside_checkout
        modules[label] = {
            "hash_matches_source": match,
            "installed_path": str(installed),
            "installed_sha256": sha256(installed),
            "installed_under_root": installed_under_root,
            "module": module_name,
            "outside_source_checkout": outside_checkout,
            "source_path": str(source),
            "source_sha256": sha256(source) if source.is_file() else None,
        }

    document = {
        "expected_interpreter": str(expected_interpreter),
        "install_root": str(install_root),
        "interpreter": str(actual_interpreter),
        "interpreter_matches": interpreter_matches,
        "modules": modules,
        "package_path": str(package_path),
        "package_under_install_root": package_under_install_root,
        "passed": passed,
        "source_root": str(source_root),
        "sys_path": sys.path,
    }
    write_json_exclusive(args.output, document)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
