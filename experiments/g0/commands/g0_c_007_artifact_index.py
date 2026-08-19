#!/usr/bin/env python3
"""Hash the immutable evidence emitted by a completed G0-C-ATOMIC-007 attempt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    artifact_dir = args.artifact_dir.resolve()
    output = args.output.resolve()
    if output.parent != artifact_dir:
        raise ValueError("artifact index must live directly inside artifact directory")
    if output.exists():
        raise ValueError(f"refusing to rewrite artifact index: {output}")

    files = []
    for path in sorted(artifact_dir.rglob("*")):
        if not path.is_file() or path.resolve() == output:
            continue
        files.append(
            {
                "path": str(path.relative_to(artifact_dir)),
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    document = {"artifact_dir": str(artifact_dir), "files": files}
    encoded = json.dumps(document, indent=2, sort_keys=True) + "\n"
    with output.open("x", encoding="utf-8") as handle:
        handle.write(encoded)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
