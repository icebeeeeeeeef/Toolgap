#!/usr/bin/env python3
"""Contract test for the fixed-pin session priority-release seam."""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path


def load_tracker_module(checkout: Path):
    module_path = checkout / (
        "python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py"
    )
    if not module_path.is_file():
        raise FileNotFoundError(f"missing fixed-source module: {module_path}")
    spec = importlib.util.spec_from_file_location("g0_session_ref_tracker", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module spec: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class FakeNode:
    id: int


@dataclass(frozen=True)
class FakeComponentType:
    name: str


class FakeComponent:
    def __init__(self, name: str):
        self.component_type = FakeComponentType(name)
        self.release_calls: list[str] = []
        self.reset_session_state()

    def reset_session_state(self) -> None:
        self._session_leaves: dict[str, set[FakeNode]] = {}

    def set_frontiers(self, session_id: str, *node_ids: int) -> None:
        self._session_leaves[session_id] = {
            FakeNode(node_id) for node_id in node_ids
        }

    def release_session(self, session_id: str) -> int:
        self.release_calls.append(session_id)
        return len(self._session_leaves.pop(session_id, set()))


class SessionPriorityReleaseContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tracker_module = load_tracker_module(CHECKOUT)

    def make_tracker(self, *, enabled: bool = True):
        full = FakeComponent("FULL")
        auxiliary = FakeComponent("AUXILIARY")
        tracker = self.tracker_module.UnifiedSessionRefTracker(
            components=(full, auxiliary),
            tree_core=object(),
            enable_session_radix_cache=enabled,
        )
        return tracker, full, auxiliary

    def call_contract(self, tracker, session_id: str, generation: int):
        self.assertTrue(
            hasattr(tracker, "release_session_priority"),
            "fixed source lacks release_session_priority",
        )
        return tracker.release_session_priority(session_id, generation)

    def test_contract_exists_on_tracker(self) -> None:
        tracker, _, _ = self.make_tracker()
        self.assertTrue(
            hasattr(tracker, "release_session_priority"),
            "fixed source lacks release_session_priority",
        )

    def test_release_snapshots_frontiers_and_keeps_generation_open(self) -> None:
        tracker, full, auxiliary = self.make_tracker()
        generation = tracker.open_radix_session("session-a")
        full.set_frontiers("session-a", 7, 2)
        auxiliary.set_frontiers("session-a", 9)

        result = self.call_contract(tracker, "session-a", generation)

        self.assertIsNotNone(result)
        self.assertEqual(result.session_id, "session-a")
        self.assertEqual(result.generation, generation)
        self.assertEqual(result.released_component_leaves, 3)
        self.assertEqual(
            result.frontier_node_ids,
            (("FULL", (2, 7)), ("AUXILIARY", (9,))),
        )
        self.assertEqual(tracker.ensure_session_generation("session-a"), generation)
        self.assertNotIn("session-a", tracker._closed_session_ids)
        self.assertNotIn("session-a", full._session_leaves)
        self.assertNotIn("session-a", auxiliary._session_leaves)
        self.assertEqual(full.release_calls, ["session-a"])
        self.assertEqual(auxiliary.release_calls, ["session-a"])

    def test_stale_generation_fails_closed_without_mutation(self) -> None:
        tracker, full, auxiliary = self.make_tracker()
        generation = tracker.open_radix_session("session-a")
        full.set_frontiers("session-a", 4)
        auxiliary.set_frontiers("session-a", 5)

        result = self.call_contract(tracker, "session-a", generation + 1)

        self.assertIsNone(result)
        self.assertEqual(full.release_calls, [])
        self.assertEqual(auxiliary.release_calls, [])
        self.assertEqual({node.id for node in full._session_leaves["session-a"]}, {4})
        self.assertEqual(
            {node.id for node in auxiliary._session_leaves["session-a"]}, {5}
        )
        self.assertEqual(tracker.ensure_session_generation("session-a"), generation)

    def test_disabled_tracking_is_a_noop(self) -> None:
        tracker, full, _ = self.make_tracker(enabled=False)
        generation = tracker.open_radix_session("session-a")
        full.set_frontiers("session-a", 4)

        result = self.call_contract(tracker, "session-a", generation)

        self.assertIsNone(result)
        self.assertEqual(full.release_calls, [])
        self.assertEqual({node.id for node in full._session_leaves["session-a"]}, {4})

    def test_release_result_is_immutable(self) -> None:
        tracker, full, _ = self.make_tracker()
        generation = tracker.open_radix_session("session-a")
        full.set_frontiers("session-a", 4)
        result = self.call_contract(tracker, "session-a", generation)

        self.assertIsNotNone(result)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            result.generation = generation + 1


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", required=True, type=Path)
    return parser.parse_known_args()


if __name__ == "__main__":
    ARGS, UNITTEST_ARGS = parse_args()
    CHECKOUT = ARGS.checkout.resolve()
    unittest.main(argv=[sys.argv[0], *UNITTEST_ARGS], verbosity=2)
