#!/usr/bin/env python3
"""Revision 005 counterexample oracle for the atomic checked-demote seam."""

from __future__ import annotations

import argparse
import ast
import copy
import importlib.util
import sys
import types
import unittest
from dataclasses import dataclass
from pathlib import Path


BASE_TEST = Path(__file__).with_name("test_atomic_checked_demote_contract.py")
BASE_MODULE_NAME = "g0_atomic_contract_v3_basis"
BASE_SPEC = importlib.util.spec_from_file_location(BASE_MODULE_NAME, BASE_TEST)
if BASE_SPEC is None or BASE_SPEC.loader is None:
    raise RuntimeError(f"cannot load {BASE_TEST}")
base = importlib.util.module_from_spec(BASE_SPEC)
sys.modules[BASE_MODULE_NAME] = base
BASE_SPEC.loader.exec_module(base)


def compile_actual_outcome_classes(node_outcome_node, session_outcome_node):
    module_name = "g0_actual_cache_outcomes_v5"
    module = types.ModuleType(module_name)
    module.__dict__.update({"dataclass": dataclass, "NodeId": int})
    sys.modules[module_name] = module
    future = ast.ImportFrom(
        module="__future__",
        names=[ast.alias(name="annotations")],
        level=0,
    )
    syntax = ast.fix_missing_locations(
        ast.Module(
            body=[
                future,
                copy.deepcopy(node_outcome_node),
                copy.deepcopy(session_outcome_node),
            ],
            type_ignores=[],
        )
    )
    exec(compile(syntax, "<g0-actual-cache-outcomes>", "exec"), module.__dict__)
    return (
        module.SessionNodeDemoteOutcome,
        module.SessionCheckedDemoteOutcome,
    )


class ObservationFailResource:
    def __init__(self, block_ids):
        self.block_ids = tuple(block_ids)
        self.owner_count = 1
        self.drain_count = 0

    def numel(self):
        return len(self.block_ids)

    def tolist(self):
        raise RuntimeError("injected observation failure")

    def drain(self):
        if self.owner_count != 1:
            raise AssertionError("resource lacks a unique cleanup owner")
        self.owner_count = 0
        self.drain_count += 1


class AtomicCheckedDemoteContractV5Test(base.AtomicCheckedDemoteContractTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.node_outcome_node = base.class_node(
            CHECKOUT,
            base.CACHE_FILE,
            "SessionNodeDemoteOutcome",
        )
        cls.session_outcome_node = base.class_node(
            CHECKOUT,
            base.CACHE_FILE,
            "SessionCheckedDemoteOutcome",
        )
        cls.actual_node_outcome_type = None
        cls.actual_session_outcome_type = None

    def require_surface(self):
        super().require_surface()
        self.assertIsNotNone(
            self.node_outcome_node,
            "fixed source lacks actual SessionNodeDemoteOutcome",
        )
        self.assertIsNotNone(
            self.session_outcome_node,
            "fixed source lacks actual SessionCheckedDemoteOutcome",
        )

    def compile_atomic_methods(self, interface):
        self.require_surface()
        node_type, session_type = compile_actual_outcome_classes(
            self.node_outcome_node,
            self.session_outcome_node,
        )
        type(self).actual_node_outcome_type = node_type
        type(self).actual_session_outcome_type = session_type
        core_method = base.compile_method(
            self.core_node,
            {
                "BASE_COMPONENT_TYPE": base.FULL,
                "SessionDemoteExecution": interface.SessionDemoteExecution,
            },
        )
        cache_method = base.compile_method(
            self.cache_node,
            {
                "BASE_COMPONENT_TYPE": base.FULL,
                "SessionNodeDemoteOutcome": node_type,
                "SessionCheckedDemoteOutcome": session_type,
            },
        )
        return core_method, cache_method

    def test_actual_interface_and_registry_keep_legacy_backend_fail_closed(self):
        interface, registry = self.load_actual_interface_and_registry()
        demote_calls = []

        def recording_demote(backend, node_id):
            demote_calls.append(node_id)
            raise AssertionError("legacy fail-closed path invoked physical demote")

        legacy_type = self.concrete_backend_type(
            interface,
            "RegisteredLegacyV5",
            {"demote": recording_demote},
        )
        legacy = legacy_type()
        registry.register_tree_core_backend(
            "g0-legacy-v5", lambda params, components: legacy
        )
        registered = registry.create_tree_core("g0-legacy-v5", None, {})
        result = registered.demote_session_checked(7)
        self.assertEqual(result.disposition, "REJECTED")
        self.assertEqual(result.reason, "UNSUPPORTED_BACKEND")
        self.assertIsNone(result.demote_result)
        self.assertEqual(demote_calls, [])

    def test_actual_cache_outcome_types_are_observable(self):
        result, _, _, _ = self.run_cache([base.Node(7)], [7])
        self.assertIsInstance(result, self.actual_session_outcome_type)
        self.assertIsInstance(result.nodes[0], self.actual_node_outcome_type)
        self.assertEqual(result.priority_release, "RELEASED")
        self.assertEqual(result.disposition, "ACCEPTED")
        self.assertEqual(result.nodes[0].freed_device_ids, (70,))

    def test_pending_first_safe_second_is_clipped_without_short_circuit(self):
        pending = base.Node(7, write_through_pending_id=4)
        result, _, core, _ = self.run_cache([pending, base.Node(8)], [7, 8])
        self.assertEqual(result.disposition, "CLIPPED")
        self.assertEqual(result.nodes[0].reason, "WRITE_THROUGH_PENDING")
        self.assertEqual(result.nodes[1].reason, "DEMOTED")
        self.assertEqual(core.demote_calls, [8])

    def test_safe_plus_dead_is_clipped(self):
        result, _, core, _ = self.run_cache([base.Node(7)], [7, 8])
        self.assertEqual(result.disposition, "CLIPPED")
        self.assertEqual(result.nodes[0].reason, "DEMOTED")
        self.assertEqual(result.nodes[1].reason, "NODE_NOT_LIVE")
        self.assertEqual(core.demote_calls, [7])

    def test_pending_plus_dead_is_rejected(self):
        pending = base.Node(7, write_through_pending_id=4)
        result, _, core, _ = self.run_cache([pending], [7, 8])
        self.assertEqual(result.disposition, "REJECTED")
        self.assertEqual(result.nodes[0].reason, "WRITE_THROUGH_PENDING")
        self.assertEqual(result.nodes[1].reason, "NODE_NOT_LIVE")
        self.assertEqual(core.demote_calls, [])

    def test_all_write_and_load_pending_is_deferred_with_release(self):
        write = base.Node(7, write_through_pending_id=4)
        load = base.Node(8, load_back_pending_id=5)
        result, cache, core, _ = self.run_cache([write, load], [7, 8])
        self.assertEqual(result.disposition, "DEFERRED")
        self.assertEqual(result.priority_release, "RELEASED")
        self.assertEqual(
            [node.reason for node in result.nodes],
            ["WRITE_THROUGH_PENDING", "LOAD_BACK_PENDING"],
        )
        self.assertEqual(core.demote_calls, [])
        self.assertEqual(cache.session_refs.release_count, 1)

    def test_load_only_reason_is_distinct(self):
        load = base.Node(7, load_back_pending_id=5)
        result, _, core, _ = self.run_cache([load], [7])
        self.assertEqual(result.disposition, "DEFERRED")
        self.assertEqual(result.nodes[0].reason, "LOAD_BACK_PENDING")
        self.assertEqual(core.demote_calls, [])

    def test_insert_and_eviction_walk_are_deferred(self):
        interface, core, _ = self.make_registered_probe([base.Node(7)])
        core_method, _ = self.compile_atomic_methods(interface)

        core.insert_ongoing = True
        before = list(core.demote_calls)
        inserted = core_method(core, 7)
        self.assertEqual(inserted.disposition, "DEFERRED")
        self.assertEqual(inserted.reason, "STRUCTURAL_OWNER_ACTIVE")
        self.assertIsNone(inserted.demote_result)
        self.assertEqual(core.demote_calls, before)

        core.insert_ongoing = False
        core.components_by_type[base.FULL].is_evict_device_ongoing = True
        before = list(core.demote_calls)
        evicting = core_method(core, 7)
        self.assertEqual(evicting.disposition, "DEFERRED")
        self.assertEqual(evicting.reason, "STRUCTURAL_OWNER_ACTIVE")
        self.assertIsNone(evicting.demote_result)
        self.assertEqual(core.demote_calls, before)

    def test_mutation_during_release_is_rechecked_before_fake_demote(self):
        node = base.Node(7)

        def mutate():
            node.children[8] = base.Node(8)

        result, cache, core, _ = self.run_cache([node], [7], mutate=mutate)
        self.assertEqual(result.disposition, "DEFERRED")
        self.assertEqual(result.nodes[0].reason, "NOT_CURRENT_DEVICE_LEAF")
        self.assertEqual(core.demote_calls, [])

        node.children[8].component_data[base.FULL].value = None
        later = core.demote_session_checked(7)
        self.assertEqual(later.disposition, "COMPLETED")
        self.assertEqual(later.reason, "DEMOTED")
        self.assertIsNotNone(later.demote_result)
        self.assertEqual(core.demote_calls, [7])
        cache._free_values(
            later.demote_result.device_frees,
            later.demote_result.host_frees,
        )
        self.assertEqual(core.device_resources[0].owner_count, 0)
        self.assertEqual(core.host_resources[0].owner_count, 0)

    def test_tracker_release_preserves_generation_and_omits_tombstone(self):
        self.require_surface()
        tracker = base._load_module("g0_atomic_tracker_v5", CHECKOUT / base.TRACKER_FILE)
        full = base.FakeComponent()
        refs = tracker.UnifiedSessionRefTracker(
            components=(full,),
            tree_core=object(),
            enable_session_radix_cache=True,
        )
        generation = refs.open_radix_session("session-a")
        frontiers = {base.FrontierNode(7), base.FrontierNode(2)}
        full._session_leaves["session-a"] = set(frontiers)

        stale = refs.release_session_priority("session-a", generation + 1)
        self.assertIsNone(stale)
        self.assertEqual(full.release_calls, [])
        self.assertEqual(full._session_leaves["session-a"], frontiers)

        result = refs.release_session_priority("session-a", generation)
        self.assertEqual(result.frontier_node_ids, (("FULL", (2, 7)),))
        self.assertEqual(result.released_component_leaves, 2)
        self.assertEqual(full.release_calls, ["session-a"])
        self.assertNotIn("session-a", full._session_leaves)
        self.assertEqual(refs.ensure_session_generation("session-a"), generation)
        self.assertNotIn("session-a", refs._closed_session_ids)

    def test_observation_failure_still_drains_device_and_host_once(self):
        interface, core, cache_method = self.make_registered_probe([base.Node(7)])

        def observation_failing_demote(backend, node_id):
            backend.demote_calls.append(node_id)
            device = ObservationFailResource((node_id * 10,))
            host = base.OwnedResource(block_ids=(node_id * 100,))
            backend.device_resources.append(device)
            backend.host_resources.append(host)
            backend.nodes[node_id].component_data[base.FULL].value = None
            return interface.DemoteResult(
                device_frees={base.FULL: [device]},
                host_frees={base.FULL: [host]},
                tracker={base.FULL: 1},
            )

        core.demote = types.MethodType(observation_failing_demote, core)
        release = base.PriorityRelease(
            "session-a", 3, (("FULL", (7,)),), 1
        )
        cache = base.FakeCache(core, release)
        with self.assertRaisesRegex(RuntimeError, "injected observation failure"):
            cache_method(cache, "session-a", 3)
        self.assertEqual(core.demote_calls, [7])
        self.assertEqual(core.device_resources[0].owner_count, 0)
        self.assertEqual(core.device_resources[0].drain_count, 1)
        self.assertEqual(core.host_resources[0].owner_count, 0)
        self.assertEqual(core.host_resources[0].drain_count, 1)
        self.assertEqual((cache.device_drains, cache.host_drains), (1, 1))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", required=True, type=Path)
    return parser.parse_known_args()


if __name__ == "__main__":
    ARGS, UNITTEST_ARGS = parse_args()
    CHECKOUT = ARGS.checkout.resolve()
    base.CHECKOUT = CHECKOUT
    unittest.main(argv=[sys.argv[0], *UNITTEST_ARGS], verbosity=2)
