#!/usr/bin/env python3
"""Source-extracted oracle for the fixed-pin checked-admission seam."""

from __future__ import annotations

import argparse
import ast
import copy
import dataclasses
import importlib.util
import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace


CACHE_FILE = "python/sglang/srt/mem_cache/unified_radix_cache.py"
CORE_FILE = (
    "python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py"
)
TRACKER_FILE = (
    "python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py"
)
FULL = 0


def class_method_node(checkout: Path, relative: str, class_name: str, method: str):
    path = checkout / relative
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for item in tree.body:
        if isinstance(item, ast.ClassDef) and item.name == class_name:
            for member in item.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if member.name == method:
                        return member
    return None


def compile_method(node, globals_map: dict):
    function = copy.deepcopy(node)
    function.decorator_list = []
    function.returns = None
    for argument in (
        function.args.posonlyargs
        + function.args.args
        + function.args.kwonlyargs
    ):
        argument.annotation = None
    if function.args.vararg is not None:
        function.args.vararg.annotation = None
    if function.args.kwarg is not None:
        function.args.kwarg.annotation = None
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    namespace = dict(globals_map)
    exec(compile(module, "<g0-extracted-method>", "exec"), namespace)
    return namespace[function.name]


def load_tracker_module(checkout: Path):
    path = checkout / TRACKER_FILE
    spec = importlib.util.spec_from_file_location("g0_v2_tracker", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class Admission:
    node_id: int
    eligible: bool
    reason: str


@dataclass(frozen=True)
class CheckedAdmission:
    session_id: str
    generation: int
    released_component_leaves: int
    nodes: tuple[Admission, ...]
    reason: str


@dataclass(frozen=True)
class PriorityRelease:
    session_id: str
    generation: int
    frontier_node_ids: tuple[tuple[str, tuple[int, ...]], ...]
    released_component_leaves: int


@dataclass(frozen=True)
class FrontierNode:
    id: int


@dataclass
class ComponentData:
    value: object | None = field(default_factory=object)
    host_value: object | None = field(default_factory=object)
    lock_ref: int = 0
    session_ref: int = 0


@dataclass
class Node:
    id: int
    component_data: list[ComponentData] = field(
        default_factory=lambda: [ComponentData(), ComponentData(), ComponentData()]
    )
    children: dict[int, "Node"] = field(default_factory=dict)
    write_through_pending_id: int | None = None
    load_back_pending_id: int | None = None
    evicted: bool = False


class FakeComponent:
    def __init__(self, name: str = "FULL"):
        self.component_type = SimpleNamespace(name=name)
        self.is_evict_device_ongoing = False
        self._session_leaves: dict[str, set[SimpleNamespace]] = {}
        self.release_calls: list[str] = []

    def reset_session_state(self) -> None:
        self._session_leaves = {}

    def release_session(self, session_id: str) -> int:
        self.release_calls.append(session_id)
        return len(self._session_leaves.pop(session_id, set()))


class FakeCore:
    def __init__(self, node: Node):
        self.root_node = Node(0)
        self.nodes = {node.id: node}
        self.component_types = (FULL,)
        self.components_by_type = {FULL: SimpleNamespace(is_evict_device_ongoing=False)}
        self.insert_ongoing = False

    def has_ongoing_insert(self) -> bool:
        return self.insert_ongoing

    def node_by_id(self, node_id: int) -> Node:
        return self.nodes[node_id]

    def _is_settled_full_host_duplicate(self, node: Node) -> bool:
        data = node.component_data[FULL]
        return (
            node is not self.root_node
            and data.value is not None
            and data.host_value is not None
            and node.write_through_pending_id is None
            and node.load_back_pending_id is None
        )

    def _is_device_leaf(self, node: Node) -> bool:
        return (
            node is not self.root_node
            and not node.evicted
            and not any(data.lock_ref > 0 for data in node.component_data)
            and not any(
                child.component_data[FULL].value is not None
                for child in node.children.values()
            )
        )


class FakeSessionRefs:
    def __init__(self, release: PriorityRelease | None):
        self.release = release
        self.calls: list[tuple[str, int]] = []
        self.mutations = 0

    def release_session_priority(self, session_id: str, generation: int):
        self.calls.append((session_id, generation))
        if self.release is not None:
            self.mutations += 1
        return self.release


class FakeCache:
    def __init__(self, core: FakeCore, release: PriorityRelease | None):
        self.tree_components = (FULL,)
        self.tree_core = core
        self.session_refs = FakeSessionRefs(release)


@dataclass
class OwnedResource:
    owner_count: int = 1
    drain_count: int = 0

    def drain(self, fail: bool = False) -> None:
        if fail:
            raise RuntimeError("injected drain failure")
        if self.owner_count != 1:
            raise AssertionError("resource has no unique cleanup owner")
        self.owner_count = 0
        self.drain_count += 1


def cleanup_oracle(device: OwnedResource, host: OwnedResource, *, fail_device=False):
    success = False
    try:
        device.drain(fail=fail_device)
    finally:
        host.drain()
    success = True
    return success


class CheckedAdmissionContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cache_node = class_method_node(
            CHECKOUT,
            CACHE_FILE,
            "UnifiedRadixCache",
            "prepare_session_checked_demote",
        )
        cls.core_node = class_method_node(
            CHECKOUT,
            CORE_FILE,
            "UnifiedTreeCore",
            "check_session_demote_admission",
        )
        cls.tracker_node = class_method_node(
            CHECKOUT,
            TRACKER_FILE,
            "UnifiedSessionRefTracker",
            "release_session_priority",
        )

    def require_surface(self) -> None:
        self.assertIsNotNone(
            self.cache_node,
            "fixed source lacks prepare_session_checked_demote",
        )
        self.assertIsNotNone(
            self.core_node,
            "fixed source lacks TreeCore checked-admission interface implementation",
        )
        self.assertIsNotNone(
            self.tracker_node,
            "fixed source lacks generation-preserving priority release",
        )

    def extracted_methods(self):
        self.require_surface()
        core_method = compile_method(
            self.core_node,
            {
                "BASE_COMPONENT_TYPE": FULL,
                "SessionDemoteAdmission": Admission,
            },
        )
        cache_method = compile_method(
            self.cache_node,
            {
                "BASE_COMPONENT_TYPE": FULL,
                "SessionDemoteAdmission": Admission,
                "SessionCheckedAdmission": CheckedAdmission,
            },
        )
        return core_method, cache_method

    def make_safe(self):
        node = Node(7)
        core = FakeCore(node)
        release = PriorityRelease("session-a", 3, (("FULL", (7,)),), 1)
        return node, core, FakeCache(core, release)

    def run_admission(self, mutate=None):
        core_method, cache_method = self.extracted_methods()
        node, core, cache = self.make_safe()
        if mutate is not None:
            mutate(node, core, cache)
        core.check_session_demote_admission = core_method.__get__(core, FakeCore)
        result = cache_method(cache, "session-a", 3)
        return result, node, core, cache

    def test_stock_exposes_one_cache_level_contract(self) -> None:
        self.require_surface()

    def test_settled_full_only_target_is_admitted(self) -> None:
        result, _, _, _ = self.run_admission()
        self.assertEqual(result.reason, "ADMITTED")
        self.assertEqual(result.nodes, (Admission(7, True, "ELIGIBLE"),))

    def test_write_through_pending_is_rejected(self) -> None:
        result, *_ = self.run_admission(
            lambda node, core, cache: setattr(node, "write_through_pending_id", 7)
        )
        self.assertEqual(result.nodes[0].reason, "WRITE_THROUGH_PENDING")

    def test_load_back_pending_is_rejected(self) -> None:
        result, *_ = self.run_admission(
            lambda node, core, cache: setattr(node, "load_back_pending_id", 7)
        )
        self.assertEqual(result.nodes[0].reason, "LOAD_BACK_PENDING")

    def test_remaining_non_target_session_coverage_is_rejected(self) -> None:
        result, *_ = self.run_admission(
            lambda node, core, cache: setattr(
                node.component_data[FULL], "session_ref", 1
            )
        )
        self.assertEqual(result.nodes[0].reason, "NON_TARGET_SESSION_COVERAGE")

    def test_tree_mutation_invalidates_device_leaf(self) -> None:
        def add_child(node, core, cache):
            node.children[8] = Node(8)

        result, *_ = self.run_admission(add_child)
        self.assertEqual(result.nodes[0].reason, "NOT_CURRENT_DEVICE_LEAF")

    def test_device_component_lock_is_rejected(self) -> None:
        result, *_ = self.run_admission(
            lambda node, core, cache: setattr(
                node.component_data[1], "lock_ref", 1
            )
        )
        self.assertEqual(result.nodes[0].reason, "DEVICE_LOCKED")

    def test_resumable_insert_owner_is_rejected(self) -> None:
        result, *_ = self.run_admission(
            lambda node, core, cache: setattr(core, "insert_ongoing", True)
        )
        self.assertEqual(result.nodes[0].reason, "STRUCTURAL_OWNER_ACTIVE")

    def test_eviction_walk_owner_is_rejected(self) -> None:
        def start_evict(node, core, cache):
            core.components_by_type[FULL].is_evict_device_ongoing = True

        result, *_ = self.run_admission(start_evict)
        self.assertEqual(result.nodes[0].reason, "STRUCTURAL_OWNER_ACTIVE")

    def test_auxiliary_component_scope_is_rejected_before_release(self) -> None:
        _, cache_method = self.extracted_methods()
        node, core, cache = self.make_safe()
        cache.tree_components = (FULL, 1)

        result = cache_method(cache, "session-a", 3)

        self.assertEqual(result.reason, "UNSUPPORTED_COMPONENT_SET")
        self.assertEqual(cache.session_refs.calls, [])
        self.assertEqual(cache.session_refs.mutations, 0)

    def test_stale_generation_is_rejected_without_release(self) -> None:
        _, cache_method = self.extracted_methods()
        node = Node(7)
        core = FakeCore(node)
        cache = FakeCache(core, None)

        result = cache_method(cache, "session-a", 99)

        self.assertEqual(result.reason, "STALE_GENERATION")
        self.assertEqual(cache.session_refs.mutations, 0)

    def test_tracker_release_keeps_generation_and_snapshots_before_mutation(self) -> None:
        self.require_surface()
        module = load_tracker_module(CHECKOUT)
        full = FakeComponent("FULL")
        tracker = module.UnifiedSessionRefTracker(
            components=(full,),
            tree_core=object(),
            enable_session_radix_cache=True,
        )
        generation = tracker.open_radix_session("session-a")
        full._session_leaves["session-a"] = {
            FrontierNode(7),
            FrontierNode(2),
        }

        result = tracker.release_session_priority("session-a", generation)

        self.assertEqual(result.frontier_node_ids, (("FULL", (2, 7)),))
        self.assertEqual(tracker.ensure_session_generation("session-a"), generation)
        self.assertNotIn("session-a", tracker._closed_session_ids)
        self.assertNotIn("session-a", full._session_leaves)

    def test_cleanup_success_has_exactly_one_owner_and_one_drain(self) -> None:
        self.require_surface()
        device = OwnedResource()
        host = OwnedResource()
        self.assertTrue(cleanup_oracle(device, host))
        self.assertEqual((device.owner_count, device.drain_count), (0, 1))
        self.assertEqual((host.owner_count, host.drain_count), (0, 1))

    def test_cleanup_failure_emits_no_success_and_preserves_unique_owner(self) -> None:
        self.require_surface()
        device = OwnedResource()
        host = OwnedResource()
        with self.assertRaisesRegex(RuntimeError, "injected drain failure"):
            cleanup_oracle(device, host, fail_device=True)
        self.assertEqual((device.owner_count, device.drain_count), (1, 0))
        self.assertEqual((host.owner_count, host.drain_count), (0, 1))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", required=True, type=Path)
    return parser.parse_known_args()


if __name__ == "__main__":
    ARGS, UNITTEST_ARGS = parse_args()
    CHECKOUT = ARGS.checkout.resolve()
    unittest.main(argv=[sys.argv[0], *UNITTEST_ARGS], verbosity=2)
