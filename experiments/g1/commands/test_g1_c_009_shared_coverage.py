#!/usr/bin/env python3
"""Focused counterexample for the C009 non-target coverage fixture."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path
from types import SimpleNamespace

PATCH = Path(__file__).resolve().parents[3] / (
    "upstream/sglang/patches/0002-g1-scripted-forced-demote-c009.patch"
)


def patched_test_source() -> str:
    lines = PATCH.read_text(encoding="utf-8").splitlines()
    start = next(
        index for index, line in enumerate(lines)
        if line.startswith("@@ -0,0 +1,")
    )
    return "\n".join(
        line[1:] for line in lines[start + 1:]
        if line.startswith("+") and not line.startswith("+++")
    ) + "\n"


def load_registration_helper(source: str):
    tree = ast.parse(source)
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_register_non_target_session_coverage"
    )
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    namespace = {
        "Any": object,
        "_session_frontier": lambda cache, session_id: tuple(sorted(
            node.id
            for node in cache.components[cache.tree_components[0]]._session_leaves.get(
                session_id, ()
            )
        )),
    }
    exec(compile(module, str(PATCH), "exec"), namespace)
    return namespace[function.name]


class FakeNode:
    def __init__(self, node_id: int) -> None:
        self.id = node_id
        self.component_data = {"FULL": SimpleNamespace(session_ref=1)}


class FakeComponent:
    def __init__(self, first_session: str, node: FakeNode) -> None:
        self._session_leaves = {first_session: {node}}

    def register_session_leaf(self, session_id: str, node: FakeNode) -> None:
        self._session_leaves.setdefault(session_id, set()).add(node)
        node.component_data["FULL"].session_ref += 1


class FakeSessionRefs:
    def __init__(self, first_session: str) -> None:
        self._session_generations = {first_session: 1}

    def ensure_session_generation(self, session_id: str) -> int:
        assert session_id not in self._session_generations
        generation = max(self._session_generations.values()) + 1
        self._session_generations[session_id] = generation
        return generation


class G1C009SharedCoverageTests(unittest.TestCase):
    def test_two_session_native_requests_can_have_distinct_private_frontiers(self) -> None:
        target_nodes = (21,)
        other_nodes = (24,)
        with self.assertRaises(AssertionError):
            assert target_nodes == other_nodes, (target_nodes, other_nodes)

    def test_source_registration_shares_the_real_request_created_target(self) -> None:
        source = patched_test_source()
        self.assertNotIn("assert target_nodes == other_nodes", source)
        register = load_registration_helper(source)
        first_session = "g1-shared-first"
        second_session = "g1-shared-second"
        target = FakeNode(21)
        component = FakeComponent(first_session, target)
        cache = SimpleNamespace(
            tree_components=("FULL",),
            components={"FULL": component},
            tree_core=SimpleNamespace(node_by_id=lambda node_id: target),
            session_refs=FakeSessionRefs(first_session),
        )

        registered = register(cache, second_session, (target.id,))

        self.assertEqual(registered, (21,))
        self.assertEqual(component._session_leaves[second_session], {target})
        self.assertEqual(target.component_data["FULL"].session_ref, 2)
        self.assertIn(second_session, cache.session_refs._session_generations)


if __name__ == "__main__":
    unittest.main()
