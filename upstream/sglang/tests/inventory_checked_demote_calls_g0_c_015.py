#!/usr/bin/env python3
"""Freeze the BOM-safe source inventory for G0-C-ATOMIC-015."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


TARGETS = ("checked_demote_session", "demote_session_checked")


class CallInventory(ast.NodeVisitor):
    def __init__(self, relative_path: str) -> None:
        self.relative_path = relative_path
        self.scope: list[str] = []
        self.direct_calls: dict[str, list[dict[str, object]]] = {
            name: [] for name in TARGETS
        }
        self.dynamic_routes: list[dict[str, object]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute) and node.func.attr in TARGETS:
            self.direct_calls[node.func.attr].append(
                {
                    "path": self.relative_path,
                    "line": node.lineno,
                    "scope": ".".join(self.scope),
                }
            )
        if (
            isinstance(node.func, ast.Name)
            and node.func.id in {"getattr", "setattr"}
            and len(node.args) >= 2
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value in TARGETS
        ):
            self.dynamic_routes.append(
                {
                    "path": self.relative_path,
                    "line": node.lineno,
                    "scope": ".".join(self.scope),
                    "name": node.args[1].value,
                }
            )
        self.generic_visit(node)


def inventory(source_root: Path) -> dict[str, object]:
    package_root = source_root / "python" / "sglang"
    if not package_root.is_dir():
        raise ValueError(f"missing complete package tree: {package_root}")

    direct = {name: [] for name in TARGETS}
    dynamic: list[dict[str, object]] = []
    for path in sorted(package_root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        visitor = CallInventory(str(path.relative_to(source_root)))
        visitor.visit(tree)
        for name in TARGETS:
            direct[name].extend(visitor.direct_calls[name])
        dynamic.extend(visitor.dynamic_routes)
    return {
        "source_root": str(source_root.resolve()),
        "direct_calls": direct,
        "dynamic_routes": dynamic,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    result = inventory(args.source_root)
    checked = result["direct_calls"]["checked_demote_session"]
    backend = result["direct_calls"]["demote_session_checked"]
    expected_backend = [
        {
            "path": "python/sglang/srt/mem_cache/unified_radix_cache.py",
            "scope": "UnifiedRadixCache.checked_demote_session",
        }
    ]
    result["expected"] = {
        "checked_demote_session_calls": 0,
        "demote_session_checked_calls": 1,
        "backend_call_site": expected_backend[0],
        "dynamic_routes": 0,
    }
    result["passed"] = (
        len(checked) == 0
        and len(backend) == 1
        and all(backend[0][key] == value for key, value in expected_backend[0].items())
        and not result["dynamic_routes"]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
