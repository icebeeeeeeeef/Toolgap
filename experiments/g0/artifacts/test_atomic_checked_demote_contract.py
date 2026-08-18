#!/usr/bin/env python3
"""Fixed-source oracle for the atomic session checked-demote seam."""

from __future__ import annotations

import argparse
import ast
import copy
import importlib.util
import sys
import types
import unittest
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace


CACHE_FILE = "python/sglang/srt/mem_cache/unified_radix_cache.py"
CORE_FILE = "python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py"
INTERFACE_FILE = (
    "python/sglang/srt/mem_cache/unified_cache/unified_tree_core_interface.py"
)
REGISTRY_FILE = (
    "python/sglang/srt/mem_cache/unified_cache/tree_core_registry.py"
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


def class_node(checkout: Path, relative: str, class_name: str):
    path = checkout / relative
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for item in tree.body:
        if isinstance(item, ast.ClassDef) and item.name == class_name:
            return item
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
    exec(compile(module, "<g0-atomic-extracted-method>", "exec"), namespace)
    return namespace[function.name]


class _FieldSpec:
    def __init__(self, default_factory):
        self.default_factory = default_factory


class _StubStruct:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()

        def init(self, *args, **values):
            names = []
            for owner in reversed(cls.mro()):
                names.extend(getattr(owner, "__annotations__", {}).keys())
            names = list(dict.fromkeys(names))
            if len(args) > len(names):
                raise TypeError("too many positional arguments")
            for name, value in zip(names, args):
                setattr(self, name, value)
            for name in names[len(args) :]:
                if name in values:
                    setattr(self, name, values.pop(name))
                    continue
                default = getattr(cls, name, None)
                if isinstance(default, _FieldSpec):
                    default = default.default_factory()
                setattr(self, name, default)
            if values:
                raise TypeError(f"unexpected arguments: {sorted(values)}")

        cls.__init__ = init


def _install_interface_stubs():
    msgspec = types.ModuleType("msgspec")
    msgspec.Struct = _StubStruct
    msgspec.field = lambda *, default_factory: _FieldSpec(default_factory)
    sys.modules["msgspec"] = msgspec

    package_names = [
        "sglang",
        "sglang.srt",
        "sglang.srt.mem_cache",
        "sglang.srt.mem_cache.unified_cache",
    ]
    for name in package_names:
        module = sys.modules.setdefault(name, types.ModuleType(name))
        module.__path__ = []
    events_name = "sglang.srt.mem_cache.events"
    events = types.ModuleType(events_name)
    events.KVCacheEventMixin = type("KVCacheEventMixin", (), {})
    sys.modules[events_name] = events


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class PriorityRelease:
    session_id: str
    generation: int
    frontier_node_ids: tuple[tuple[str, tuple[int, ...]], ...]
    released_component_leaves: int


@dataclass(frozen=True)
class NodeOutcome:
    node_id: int
    disposition: str
    reason: str
    freed_device_ids: tuple[int, ...]


@dataclass(frozen=True)
class SessionOutcome:
    session_id: str
    generation: int
    priority_release: str
    disposition: str
    released_component_leaves: int
    nodes: tuple[NodeOutcome, ...]
    reason: str


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


@dataclass(frozen=True)
class FrontierNode:
    id: int


class FakeComponent:
    def __init__(self, name: str = "FULL"):
        self.component_type = SimpleNamespace(name=name)
        self._session_leaves: dict[str, set[FrontierNode]] = {}
        self.release_calls: list[str] = []

    def reset_session_state(self):
        self._session_leaves = {}

    def release_session(self, session_id: str) -> int:
        self.release_calls.append(session_id)
        return len(self._session_leaves.pop(session_id, set()))


@dataclass
class OwnedResource:
    owner_count: int = 1
    drain_count: int = 0
    fail: bool = False
    block_ids: tuple[int, ...] = (1,)

    def numel(self) -> int:
        return len(self.block_ids)

    def tolist(self) -> list[int]:
        return list(self.block_ids)

    def drain(self) -> None:
        if self.fail:
            raise RuntimeError("injected drain failure")
        if self.owner_count != 1:
            raise AssertionError("resource lacks a unique cleanup owner")
        self.owner_count = 0
        self.drain_count += 1


class FakeSessionRefs:
    def __init__(self, release: PriorityRelease | None, after_release=None):
        self.release = release
        self.after_release = after_release
        self.calls: list[tuple[str, int]] = []
        self.release_count = 0

    def release_session_priority(self, session_id: str, generation: int):
        self.calls.append((session_id, generation))
        if self.release is None:
            return None
        self.release_count += 1
        if self.after_release is not None:
            self.after_release()
        return self.release


class FakeCache:
    def __init__(self, core, release, after_release=None):
        self.tree_components = (FULL,)
        self.tree_core = core
        self.session_refs = FakeSessionRefs(release, after_release)
        self.tracker = defaultdict(int)
        self.device_drains = 0
        self.host_drains = 0

    def _free_values(self, device_frees, host_frees):
        try:
            for component in list(device_frees):
                values = device_frees.pop(component)
                for value in values:
                    value.drain()
                    self.device_drains += 1
        finally:
            for component in list(host_frees):
                values = host_frees.pop(component)
                for value in values:
                    value.drain()
                    self.host_drains += 1

    def _accumulate_tracker(self, tracker, delta):
        for component, count in delta.items():
            tracker[component] += count


def _dummy_abstract(*args, **kwargs):
    return None


class AtomicCheckedDemoteContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cache_node = class_method_node(
            CHECKOUT, CACHE_FILE, "UnifiedRadixCache", "checked_demote_session"
        )
        cls.core_node = class_method_node(
            CHECKOUT, CORE_FILE, "UnifiedTreeCore", "demote_session_checked"
        )
        cls.interface_node = class_method_node(
            CHECKOUT,
            INTERFACE_FILE,
            "UnifiedTreeCoreInterface",
            "demote_session_checked",
        )
        cls.execution_node = class_node(
            CHECKOUT, INTERFACE_FILE, "SessionDemoteExecution"
        )
        cls.tracker_node = class_method_node(
            CHECKOUT,
            TRACKER_FILE,
            "UnifiedSessionRefTracker",
            "release_session_priority",
        )

    def require_surface(self):
        self.assertIsNotNone(
            self.cache_node, "fixed source lacks atomic checked_demote_session"
        )
        self.assertIsNotNone(
            self.core_node, "fixed source lacks atomic backend demote_session_checked"
        )
        self.assertIsNotNone(
            self.interface_node,
            "fixed source lacks maintained-interface demote_session_checked",
        )
        self.assertIsNotNone(
            self.execution_node, "fixed source lacks SessionDemoteExecution"
        )
        self.assertIsNotNone(
            self.tracker_node,
            "fixed source lacks generation-preserving priority release",
        )

    def load_actual_interface_and_registry(self):
        self.require_surface()
        _install_interface_stubs()
        interface_name = (
            "sglang.srt.mem_cache.unified_cache.unified_tree_core_interface"
        )
        interface = _load_module(interface_name, CHECKOUT / INTERFACE_FILE)
        registry_name = "sglang.srt.mem_cache.unified_cache.tree_core_registry"
        registry = _load_module(registry_name, CHECKOUT / REGISTRY_FILE)
        return interface, registry

    def concrete_backend_type(self, interface, name, overrides=None):
        attrs = {
            method: _dummy_abstract
            for method in interface.UnifiedTreeCoreInterface.__abstractmethods__
        }
        attrs.update(overrides or {})
        return type(name, (interface.UnifiedTreeCoreInterface,), attrs)

    def compile_atomic_methods(self, interface):
        core_method = compile_method(
            self.core_node,
            {
                "BASE_COMPONENT_TYPE": FULL,
                "SessionDemoteExecution": interface.SessionDemoteExecution,
            },
        )
        cache_method = compile_method(
            self.cache_node,
            {
                "BASE_COMPONENT_TYPE": FULL,
                "SessionNodeDemoteOutcome": NodeOutcome,
                "SessionCheckedDemoteOutcome": SessionOutcome,
            },
        )
        return core_method, cache_method

    def make_registered_probe(self, nodes: list[Node]):
        interface, registry = self.load_actual_interface_and_registry()
        core_method, cache_method = self.compile_atomic_methods(interface)

        def init(core):
            core.root_node = Node(0)
            core.nodes = {node.id: node for node in nodes}
            core.component_types = (FULL,)
            core.components_by_type = {
                FULL: SimpleNamespace(is_evict_device_ongoing=False)
            }
            core.insert_ongoing = False
            core.demote_calls = []
            core.device_resources = []
            core.host_resources = []
            core.fail_next_device_drain = False

        def has_ongoing_insert(core):
            return core.insert_ongoing

        def node_by_id(core, node_id):
            return core.nodes[node_id]

        def settled(core, node):
            data = node.component_data[FULL]
            return (
                node is not core.root_node
                and data.value is not None
                and data.host_value is not None
                and node.write_through_pending_id is None
                and node.load_back_pending_id is None
            )

        def device_leaf(core, node):
            return (
                node is not core.root_node
                and not node.evicted
                and node.component_data[FULL].value is not None
                and not any(data.lock_ref > 0 for data in node.component_data)
                and not any(
                    child.component_data[FULL].value is not None
                    for child in node.children.values()
                )
            )

        def demote(core, node_id):
            node = core.nodes[node_id]
            core.demote_calls.append(node_id)
            device = OwnedResource(
                fail=core.fail_next_device_drain, block_ids=(node_id * 10,)
            )
            host = OwnedResource(block_ids=(node_id * 100,))
            core.device_resources.append(device)
            core.host_resources.append(host)
            node.component_data[FULL].value = None
            return interface.DemoteResult(
                device_frees={FULL: [device]},
                host_frees={FULL: [host]},
                tracker={FULL: 1},
            )

        backend_type = self.concrete_backend_type(
            interface,
            "RegisteredAtomicProbe",
            {
                "__init__": init,
                "has_ongoing_insert": has_ongoing_insert,
                "node_by_id": node_by_id,
                "_is_settled_full_host_duplicate": settled,
                "_is_device_leaf": device_leaf,
                "demote": demote,
                "demote_session_checked": core_method,
            },
        )
        core = backend_type()
        holder = {"core": core}
        registry.register_tree_core_backend(
            "g0-atomic-probe", lambda params, components: holder["core"]
        )
        registered = registry.create_tree_core("g0-atomic-probe", None, {})
        self.assertIs(registered, core)
        return interface, registered, cache_method

    def run_cache(self, nodes, frontier_ids, mutate=None, release=True):
        interface, core, cache_method = self.make_registered_probe(nodes)
        release_value = (
            PriorityRelease(
                "session-a",
                3,
                (("FULL", tuple(frontier_ids)),),
                len(frontier_ids),
            )
            if release
            else None
        )
        cache = FakeCache(core, release_value, mutate)
        result = cache_method(cache, "session-a", 3)
        return result, cache, core, interface

    def test_stock_requires_all_vertical_surfaces(self):
        self.require_surface()

    def test_actual_interface_and_registry_keep_legacy_backend_fail_closed(self):
        interface, registry = self.load_actual_interface_and_registry()
        legacy_type = self.concrete_backend_type(interface, "RegisteredLegacy")
        legacy = legacy_type()
        registry.register_tree_core_backend(
            "g0-legacy", lambda params, components: legacy
        )
        registered = registry.create_tree_core("g0-legacy", None, {})
        result = registered.demote_session_checked(7)
        self.assertEqual(result.disposition, "REJECTED")
        self.assertEqual(result.reason, "UNSUPPORTED_BACKEND")
        self.assertIsNone(result.demote_result)

    def test_all_safe_frontiers_are_accepted_and_drained_once(self):
        result, cache, core, _ = self.run_cache([Node(7), Node(8)], [7, 8])
        self.assertEqual(result.disposition, "ACCEPTED")
        self.assertEqual(result.priority_release, "RELEASED")
        self.assertEqual(core.demote_calls, [7, 8])
        self.assertEqual(result.nodes[0].freed_device_ids, (70,))
        self.assertEqual(result.nodes[1].freed_device_ids, (80,))
        self.assertEqual(cache.session_refs.release_count, 1)
        self.assertEqual((cache.device_drains, cache.host_drains), (2, 2))
        self.assertTrue(all(resource.owner_count == 0 for resource in core.device_resources))
        self.assertTrue(all(resource.owner_count == 0 for resource in core.host_resources))

    def test_partial_safe_and_write_pending_is_clipped(self):
        pending = Node(8, write_through_pending_id=4)
        result, cache, core, _ = self.run_cache([Node(7), pending], [7, 8])
        self.assertEqual(result.disposition, "CLIPPED")
        self.assertEqual(core.demote_calls, [7])
        self.assertEqual(cache.session_refs.release_count, 1)
        self.assertEqual(result.nodes[1].reason, "WRITE_THROUGH_PENDING")

    def test_all_write_and_load_pending_is_deferred_with_release(self):
        write = Node(7, write_through_pending_id=4)
        load = Node(8, load_back_pending_id=5)
        result, cache, core, _ = self.run_cache([write, load], [7, 8])
        self.assertEqual(result.disposition, "DEFERRED")
        self.assertEqual(result.priority_release, "RELEASED")
        self.assertEqual(core.demote_calls, [])
        self.assertEqual(cache.session_refs.release_count, 1)

    def test_missing_host_copy_is_deferred(self):
        node = Node(7)
        node.component_data[FULL].host_value = None
        result, _, core, _ = self.run_cache([node], [7])
        self.assertEqual(result.disposition, "DEFERRED")
        self.assertEqual(result.nodes[0].reason, "HOST_COPY_NOT_COMMITTED")
        self.assertEqual(core.demote_calls, [])

    def test_dead_node_is_rejected_after_release(self):
        result, cache, core, _ = self.run_cache([], [7])
        self.assertEqual(result.disposition, "REJECTED")
        self.assertEqual(result.priority_release, "RELEASED")
        self.assertEqual(result.nodes[0].reason, "NODE_NOT_LIVE")
        self.assertEqual(cache.session_refs.release_count, 1)
        self.assertEqual(core.demote_calls, [])

    def test_empty_frontier_is_rejected_after_release(self):
        result, cache, core, _ = self.run_cache([], [])
        self.assertEqual(result.disposition, "REJECTED")
        self.assertEqual(result.reason, "EMPTY_TARGET_FRONTIER")
        self.assertEqual(cache.session_refs.release_count, 1)
        self.assertEqual(core.demote_calls, [])

    def test_device_absent_is_rejected(self):
        node = Node(7)
        node.component_data[FULL].value = None
        result, _, core, _ = self.run_cache([node], [7])
        self.assertEqual(result.disposition, "REJECTED")
        self.assertEqual(result.nodes[0].reason, "DEVICE_VALUE_ABSENT")
        self.assertEqual(core.demote_calls, [])

    def test_remaining_non_target_coverage_is_deferred(self):
        node = Node(7)
        node.component_data[FULL].session_ref = 1
        result, _, core, _ = self.run_cache([node], [7])
        self.assertEqual(result.disposition, "DEFERRED")
        self.assertEqual(result.nodes[0].reason, "NON_TARGET_SESSION_COVERAGE")
        self.assertEqual(core.demote_calls, [])

    def test_device_lock_is_deferred(self):
        node = Node(7)
        node.component_data[1].lock_ref = 1
        result, _, core, _ = self.run_cache([node], [7])
        self.assertEqual(result.disposition, "DEFERRED")
        self.assertEqual(result.nodes[0].reason, "DEVICE_LOCKED")
        self.assertEqual(core.demote_calls, [])

    def test_insert_and_eviction_walk_are_deferred(self):
        result, _, core, _ = self.run_cache([Node(7)], [7])
        core.insert_ongoing = True
        interface = sys.modules[
            "sglang.srt.mem_cache.unified_cache.unified_tree_core_interface"
        ]
        core_method = compile_method(
            self.core_node,
            {
                "BASE_COMPONENT_TYPE": FULL,
                "SessionDemoteExecution": interface.SessionDemoteExecution,
            },
        )
        inserted = core_method(core, 7)
        self.assertEqual(inserted.reason, "STRUCTURAL_OWNER_ACTIVE")

        core.insert_ongoing = False
        core.nodes[7].component_data[FULL].value = object()
        core.components_by_type[FULL].is_evict_device_ongoing = True
        evicting = core_method(core, 7)
        self.assertEqual(evicting.reason, "STRUCTURAL_OWNER_ACTIVE")

    def test_mutation_during_release_is_rechecked_before_fake_demote(self):
        node = Node(7)

        def mutate():
            node.children[8] = Node(8)

        result, _, core, _ = self.run_cache([node], [7], mutate=mutate)
        self.assertEqual(result.disposition, "REJECTED")
        self.assertEqual(result.nodes[0].reason, "NOT_CURRENT_DEVICE_LEAF")
        self.assertEqual(core.demote_calls, [])

    def test_auxiliary_scope_and_stale_generation_do_not_release(self):
        interface, core, cache_method = self.make_registered_probe([Node(7)])
        release = PriorityRelease("session-a", 3, (("FULL", (7,)),), 1)
        auxiliary = FakeCache(core, release)
        auxiliary.tree_components = (FULL, 1)
        result = cache_method(auxiliary, "session-a", 3)
        self.assertEqual(result.reason, "UNSUPPORTED_COMPONENT_SET")
        self.assertEqual(auxiliary.session_refs.release_count, 0)

        stale = FakeCache(core, None)
        result = cache_method(stale, "session-a", 99)
        self.assertEqual(result.reason, "STALE_GENERATION")
        self.assertEqual(stale.session_refs.release_count, 0)

    def test_tracker_release_preserves_generation_and_omits_tombstone(self):
        self.require_surface()
        tracker = _load_module("g0_atomic_tracker", CHECKOUT / TRACKER_FILE)
        full = FakeComponent()
        refs = tracker.UnifiedSessionRefTracker(
            components=(full,),
            tree_core=object(),
            enable_session_radix_cache=True,
        )
        generation = refs.open_radix_session("session-a")
        full._session_leaves["session-a"] = {FrontierNode(7), FrontierNode(2)}
        result = refs.release_session_priority("session-a", generation)
        self.assertEqual(result.frontier_node_ids, (("FULL", (2, 7)),))
        self.assertEqual(refs.ensure_session_generation("session-a"), generation)
        self.assertNotIn("session-a", refs._closed_session_ids)

    def test_cleanup_failure_returns_no_terminal_success(self):
        interface, core, cache_method = self.make_registered_probe([Node(7)])
        core.fail_next_device_drain = True
        release = PriorityRelease("session-a", 3, (("FULL", (7,)),), 1)
        cache = FakeCache(core, release)
        with self.assertRaisesRegex(RuntimeError, "injected drain failure"):
            cache_method(cache, "session-a", 3)
        self.assertEqual(core.demote_calls, [7])
        self.assertEqual(core.device_resources[0].owner_count, 1)
        self.assertEqual(core.device_resources[0].drain_count, 0)
        self.assertEqual(core.host_resources[0].owner_count, 0)
        self.assertEqual(core.host_resources[0].drain_count, 1)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", required=True, type=Path)
    return parser.parse_known_args()


if __name__ == "__main__":
    ARGS, UNITTEST_ARGS = parse_args()
    CHECKOUT = ARGS.checkout.resolve()
    unittest.main(argv=[sys.argv[0], *UNITTEST_ARGS], verbosity=2)
