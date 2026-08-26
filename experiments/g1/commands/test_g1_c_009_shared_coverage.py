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
        covered = node
        while covered is not None:
            covered.component_data["FULL"].session_ref += 1
            covered = getattr(covered, "parent", None)
        data = node.component_data["FULL"]
        if data.session_ids is None:
            data.session_ids = set()
        data.session_ids.add(session_id)

    def release_session(self, session_id: str) -> int:
        leaves = tuple(self._session_leaves.get(session_id, ()))
        for leaf in leaves:
            covered = leaf
            while covered is not None:
                covered.component_data["FULL"].session_ref -= 1
                covered = getattr(covered, "parent", None)
            data = leaf.component_data["FULL"]
            data.session_ids.remove(session_id)
            if not data.session_ids:
                data.session_ids = None
        self._session_leaves.pop(session_id, None)
        return len(leaves)


class FakeSessionRefs:
    def __init__(self, first_session: str, component: FakeComponent) -> None:
        self._session_generations = {first_session: 1}
        self._component = component

    def ensure_session_generation(self, session_id: str) -> int:
        assert session_id not in self._session_generations
        generation = max(self._session_generations.values()) + 1
        self._session_generations[session_id] = generation
        return generation

    def release_session_priority(self, session_id: str, generation: int):
        if self._session_generations.get(session_id) != generation:
            return None
        return SimpleNamespace(
            released_component_leaves=self._component.release_session(session_id)
        )


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
        ancestor = FakeNode(11)
        target = FakeNode(21)
        target.parent = ancestor
        ancestor.component_data["FULL"].session_ids = None
        target.component_data["FULL"].session_ids = {first_session}
        component = FakeComponent(first_session, target)
        cache = SimpleNamespace(
            tree_components=("FULL",),
            components={"FULL": component},
            tree_core=SimpleNamespace(node_by_id=lambda node_id: target),
            session_refs=FakeSessionRefs(first_session, component),
        )

        registered = register(cache, second_session, (target.id,))

        self.assertEqual(registered, (21,))
        self.assertEqual(component._session_leaves[second_session], {target})
        self.assertEqual(target.component_data["FULL"].session_ref, 2)
        self.assertEqual(target.component_data["FULL"].session_ids, {first_session, second_session})
        self.assertEqual(ancestor.component_data["FULL"].session_ref, 2)
        self.assertIsNone(ancestor.component_data["FULL"].session_ids)
        self.assertIn(second_session, cache.session_refs._session_generations)

        released = cache.session_refs.release_session_priority(first_session, 1)

        self.assertEqual(released.released_component_leaves, 1)
        self.assertEqual(target.component_data["FULL"].session_ref, 1)
        self.assertEqual(ancestor.component_data["FULL"].session_ref, 1)
        self.assertEqual(target.component_data["FULL"].session_ids, {second_session})
        self.assertNotIn(first_session, component._session_leaves)
        self.assertEqual(component._session_leaves[second_session], {target})


if __name__ == "__main__":
    unittest.main()
