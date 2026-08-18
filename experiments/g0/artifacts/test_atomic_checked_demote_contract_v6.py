#!/usr/bin/env python3
"""Revision 006 counterexample oracle for the atomic checked-demote seam."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import sys
import types
import unittest
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
DEPENDENCIES = {
    ARTIFACT_DIR / "test_atomic_checked_demote_contract.py": (
        "90a3aeb69f8ca9a23b8f77f0dafa8d04e2698116d79947fe4dac91dd9906fd95"
    ),
    ARTIFACT_DIR / "test_atomic_checked_demote_contract_v5.py": (
        "f3ec1863a58d7e8cde1f68945cbaee7fb8d220dc88a4f0eadc5673528edf3cec"
    ),
}
for dependency, expected_hash in DEPENDENCIES.items():
    actual_hash = hashlib.sha256(dependency.read_bytes()).hexdigest()
    if actual_hash != expected_hash:
        raise RuntimeError(
            f"frozen executable dependency drift: {dependency.name} "
            f"expected {expected_hash}, got {actual_hash}"
        )


V5_TEST = ARTIFACT_DIR / "test_atomic_checked_demote_contract_v5.py"
V5_MODULE_NAME = "g0_atomic_contract_v5_basis"
V5_SPEC = importlib.util.spec_from_file_location(V5_MODULE_NAME, V5_TEST)
if V5_SPEC is None or V5_SPEC.loader is None:
    raise RuntimeError(f"cannot load {V5_TEST}")
v5 = importlib.util.module_from_spec(V5_SPEC)
sys.modules[V5_MODULE_NAME] = v5
V5_SPEC.loader.exec_module(v5)
base = v5.base


class CoverageFakeComponent(base.FakeComponent):
    def __init__(self):
        super().__init__()
        self.coverage: dict[int, int] = {}

    def release_session(self, session_id: str) -> int:
        self.release_calls.append(session_id)
        leaves = self._session_leaves.pop(session_id, set())
        for leaf in leaves:
            remaining = self.coverage[leaf.id] - 1
            if remaining:
                self.coverage[leaf.id] = remaining
            else:
                self.coverage.pop(leaf.id)
        return len(leaves)


class AtomicCheckedDemoteContractV6Test(v5.AtomicCheckedDemoteContractV5Test):
    def test_all_safe_frontiers_are_accepted_and_drained_once(self):
        result, cache, core, _ = self.run_cache([base.Node(7), base.Node(8)], [7, 8])
        self.assertEqual(result.disposition, "ACCEPTED")
        self.assertEqual(result.priority_release, "RELEASED")
        self.assertEqual(result.released_component_leaves, 2)
        self.assertEqual([node.node_id for node in result.nodes], [7, 8])
        self.assertEqual(core.demote_calls, [7, 8])
        self.assertEqual(result.nodes[0].freed_device_ids, (70,))
        self.assertEqual(result.nodes[1].freed_device_ids, (80,))
        self.assertEqual(cache.session_refs.release_count, 1)
        self.assertEqual((cache.device_drains, cache.host_drains), (2, 2))
        self.assertTrue(
            all(resource.owner_count == 0 for resource in core.device_resources)
        )
        self.assertTrue(
            all(resource.owner_count == 0 for resource in core.host_resources)
        )

    def test_partial_safe_and_write_pending_is_clipped(self):
        pending = base.Node(8, write_through_pending_id=4)
        result, cache, core, _ = self.run_cache([base.Node(7), pending], [7, 8])
        self.assertEqual(result.disposition, "CLIPPED")
        self.assertEqual([node.node_id for node in result.nodes], [7, 8])
        self.assertEqual(core.demote_calls, [7])
        self.assertEqual(cache.session_refs.release_count, 1)
        self.assertEqual(result.nodes[1].reason, "WRITE_THROUGH_PENDING")

    def test_pending_first_safe_second_is_clipped_without_short_circuit(self):
        pending = base.Node(7, write_through_pending_id=4)
        result, _, core, _ = self.run_cache([pending, base.Node(8)], [7, 8])
        self.assertEqual(result.disposition, "CLIPPED")
        self.assertEqual([node.node_id for node in result.nodes], [7, 8])
        self.assertEqual(result.nodes[0].reason, "WRITE_THROUGH_PENDING")
        self.assertEqual(result.nodes[1].reason, "DEMOTED")
        self.assertEqual(core.demote_calls, [8])

    def test_dead_node_is_rejected_after_release(self):
        result, cache, core, _ = self.run_cache([], [7])
        self.assertEqual(result.disposition, "REJECTED")
        self.assertEqual(result.priority_release, "RELEASED")
        self.assertEqual(result.released_component_leaves, 1)
        self.assertEqual([node.node_id for node in result.nodes], [7])
        self.assertEqual(result.nodes[0].reason, "NODE_NOT_LIVE")
        self.assertEqual(cache.session_refs.release_count, 1)
        self.assertEqual(core.demote_calls, [])

    def test_tracker_release_preserves_generation_and_omits_tombstone(self):
        self.require_surface()
        tracker = base._load_module(
            "g0_atomic_tracker_v6", CHECKOUT / base.TRACKER_FILE
        )
        full = CoverageFakeComponent()
        refs = tracker.UnifiedSessionRefTracker(
            components=(full,),
            tree_core=object(),
            enable_session_radix_cache=True,
        )
        generation_a = refs.open_radix_session("session-a")
        generation_b = refs.open_radix_session("session-b")
        leaf_7 = base.FrontierNode(7)
        leaf_9 = base.FrontierNode(9)
        full._session_leaves["session-a"] = {leaf_7}
        full._session_leaves["session-b"] = {leaf_7, leaf_9}
        full.coverage = {7: 2, 9: 1}

        stale = refs.release_session_priority("session-a", generation_a + 99)
        self.assertIsNone(stale)
        self.assertEqual(full.release_calls, [])
        self.assertEqual(full._session_leaves["session-a"], {leaf_7})
        self.assertEqual(full._session_leaves["session-b"], {leaf_7, leaf_9})
        self.assertEqual(full.coverage, {7: 2, 9: 1})

        result = refs.release_session_priority("session-a", generation_a)
        self.assertEqual(result.session_id, "session-a")
        self.assertEqual(result.generation, generation_a)
        self.assertEqual(result.frontier_node_ids, (("FULL", (7,)),))
        self.assertEqual(result.released_component_leaves, 1)
        self.assertEqual(full.release_calls, ["session-a"])
        self.assertNotIn("session-a", full._session_leaves)
        self.assertEqual(full._session_leaves["session-b"], {leaf_7, leaf_9})
        self.assertEqual(full.coverage, {7: 1, 9: 1})
        self.assertEqual(refs.ensure_session_generation("session-a"), generation_a)
        self.assertEqual(refs.ensure_session_generation("session-b"), generation_b)
        self.assertNotIn("session-a", refs._closed_session_ids)
        self.assertNotIn("session-b", refs._closed_session_ids)

    def test_vertical_cache_forwards_and_returns_exact_caller_identity(self):
        interface, core, cache_method = self.make_registered_probe([base.Node(42)])
        release = base.PriorityRelease(
            "session-z", 41, (("FULL", (42,)),), 1
        )
        cache = base.FakeCache(core, release)
        result = cache_method(cache, "session-z", 41)
        self.assertEqual(cache.session_refs.calls, [("session-z", 41)])
        self.assertEqual(result.session_id, "session-z")
        self.assertEqual(result.generation, 41)
        self.assertEqual(result.priority_release, "RELEASED")
        self.assertEqual(result.disposition, "ACCEPTED")
        self.assertEqual(result.released_component_leaves, 1)
        self.assertEqual(result.reason, "ACCEPTED")
        self.assertEqual([node.node_id for node in result.nodes], [42])
        self.assertEqual(result.nodes[0].reason, "DEMOTED")
        self.assertEqual(result.nodes[0].freed_device_ids, (420,))
        self.assertEqual(core.demote_calls, [42])
        self.assertIsInstance(result, self.actual_session_outcome_type)
        self.assertIsInstance(result.nodes[0], self.actual_node_outcome_type)
        self.assertIsNotNone(interface)

    def test_dead_first_safe_second_is_clipped_without_short_circuit(self):
        result, _, core, _ = self.run_cache([base.Node(8)], [7, 8])
        self.assertEqual(result.disposition, "CLIPPED")
        self.assertEqual([node.node_id for node in result.nodes], [7, 8])
        self.assertEqual([node.reason for node in result.nodes], ["NODE_NOT_LIVE", "DEMOTED"])
        self.assertEqual(core.demote_calls, [8])

    def test_host_lock_alone_does_not_block_device_demotion(self):
        node = base.Node(7)
        node.component_data[base.FULL].host_lock_ref = 1
        result, _, core, _ = self.run_cache([node], [7])
        self.assertEqual(result.disposition, "ACCEPTED")
        self.assertEqual(result.nodes[0].reason, "DEMOTED")
        self.assertEqual(core.demote_calls, [7])

    def test_registered_legacy_backend_rejects_after_one_way_release(self):
        interface, registry = self.load_actual_interface_and_registry()
        _, cache_method = self.compile_atomic_methods(interface)
        demote_calls = []

        def recording_demote(backend, node_id):
            demote_calls.append(node_id)
            raise AssertionError("legacy cache path invoked physical demote")

        legacy_type = self.concrete_backend_type(
            interface,
            "RegisteredLegacyVerticalV6",
            {"demote": recording_demote},
        )
        legacy = legacy_type()
        registry.register_tree_core_backend(
            "g0-legacy-vertical-v6", lambda params, components: legacy
        )
        registered = registry.create_tree_core("g0-legacy-vertical-v6", None, {})
        release = base.PriorityRelease(
            "legacy-session", 17, (("FULL", (7,)),), 1
        )
        cache = base.FakeCache(registered, release)
        result = cache_method(cache, "legacy-session", 17)
        self.assertEqual(cache.session_refs.calls, [("legacy-session", 17)])
        self.assertEqual(cache.session_refs.release_count, 1)
        self.assertEqual(result.session_id, "legacy-session")
        self.assertEqual(result.generation, 17)
        self.assertEqual(result.priority_release, "RELEASED")
        self.assertEqual(result.disposition, "REJECTED")
        self.assertEqual(result.released_component_leaves, 1)
        self.assertEqual([node.node_id for node in result.nodes], [7])
        self.assertEqual(result.nodes[0].reason, "UNSUPPORTED_BACKEND")
        self.assertEqual(result.nodes[0].freed_device_ids, ())
        self.assertEqual(demote_calls, [])

    def test_exact_freed_ids_preserve_every_index_in_one_value(self):
        interface, core, cache_method = self.make_registered_probe([base.Node(7)])

        def multi_id_demote(backend, node_id):
            backend.demote_calls.append(node_id)
            device = base.OwnedResource(block_ids=(70, 71, 72))
            host = base.OwnedResource(block_ids=(700,))
            backend.device_resources.append(device)
            backend.host_resources.append(host)
            backend.nodes[node_id].component_data[base.FULL].value = None
            return interface.DemoteResult(
                device_frees={base.FULL: [device]},
                host_frees={base.FULL: [host]},
                tracker={base.FULL: 3},
            )

        core.demote = types.MethodType(multi_id_demote, core)
        release = base.PriorityRelease("session-a", 3, (("FULL", (7,)),), 1)
        cache = base.FakeCache(core, release)
        result = cache_method(cache, "session-a", 3)
        self.assertEqual(result.disposition, "ACCEPTED")
        self.assertEqual(result.nodes[0].node_id, 7)
        self.assertEqual(result.nodes[0].freed_device_ids, (70, 71, 72))
        self.assertEqual(core.device_resources[0].drain_count, 1)
        self.assertEqual(core.host_resources[0].drain_count, 1)
        self.assertEqual(core.device_resources[0].owner_count, 0)
        self.assertEqual(core.host_resources[0].owner_count, 0)
        self.assertEqual((cache.device_drains, cache.host_drains), (1, 1))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", required=True, type=Path)
    return parser.parse_known_args()


if __name__ == "__main__":
    ARGS, UNITTEST_ARGS = parse_args()
    CHECKOUT = ARGS.checkout.resolve()
    v5.CHECKOUT = CHECKOUT
    base.CHECKOUT = CHECKOUT
    unittest.main(argv=[sys.argv[0], *UNITTEST_ARGS], verbosity=2)
