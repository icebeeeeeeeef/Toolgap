#!/usr/bin/env python3
"""Exercise the installed G0 checked-demote seam without physical demotion.

This is intentionally outside the SGLang checkout so the G0 runner can execute
it from a temporary directory using the treatment virtual environment.  It uses
real installed cache, registry, component, and outcome classes; only the
registered backend is a fail-closed test double.
"""

from __future__ import annotations

import inspect
import unittest
from array import array
from types import SimpleNamespace
from uuid import uuid4

import torch

from sglang.srt.environ import envs
from sglang.srt.mem_cache.allocator import TokenToKVPoolAllocator
from sglang.srt.mem_cache.base_prefix_cache import InsertParams, MatchPrefixParams
from sglang.srt.mem_cache.cache_init_params import CacheInitParams
from sglang.srt.mem_cache.memory_pool import MHATokenToKVPool, ReqToTokenPool
from sglang.srt.mem_cache.radix_cache import RadixKey
from sglang.srt.mem_cache.unified_cache.component_type import ComponentType
from sglang.srt.mem_cache.unified_cache.tree_core_registry import (
    _TREE_CORE_REGISTRY,
    register_tree_core_backend,
)
from sglang.srt.mem_cache.unified_cache.unified_tree_core import UnifiedTreeCore
from sglang.srt.mem_cache.unified_cache.unified_tree_core_interface import (
    SessionDemoteExecution,
    UnifiedTreeCoreInterface,
)
from sglang.srt.mem_cache.unified_radix_cache import (
    SessionCheckedDemoteOutcome,
    UnifiedRadixCache,
)


def make_params() -> CacheInitParams:
    """Build the same real CPU cache shape used by pinned SGLang unit tests."""
    dtype = torch.float16
    kv_pool = MHATokenToKVPool(
        size=64,
        page_size=1,
        dtype=dtype,
        head_num=2,
        head_dim=8,
        layer_num=1,
        device="cpu",
        enable_memory_saver=False,
    )
    allocator = TokenToKVPoolAllocator(
        size=64,
        dtype=dtype,
        device="cpu",
        kvcache=kv_pool,
        need_sort=False,
    )
    return CacheInitParams(
        disable=False,
        req_to_token_pool=ReqToTokenPool(
            size=8,
            max_context_len=128,
            device="cpu",
            enable_memory_saver=False,
        ),
        token_to_kv_pool_allocator=allocator,
        page_size=1,
        eviction_policy="lru",
        enable_session_radix_cache=True,
        tree_components=(ComponentType.FULL,),
    )


def insert_and_register(cache: UnifiedRadixCache, session_id: str) -> int:
    token_ids = [11, 12, 13, 14]
    indices = cache.token_to_kv_pool_allocator.alloc(len(token_ids))
    cache.insert(
        InsertParams(
            key=RadixKey(array("q", token_ids)),
            value=indices.to(torch.int64),
        )
    )
    generation = cache.ensure_session_generation(session_id)
    last_node = cache.match_prefix(
        MatchPrefixParams(key=RadixKey(array("q", token_ids)))
    ).last_device_node
    cache.session_refs.register_session_ref(
        SimpleNamespace(
            session_id=session_id,
            session_generation=generation,
            session=None,
            last_node=last_node,
            origin_input_ids=array("q", token_ids),
            output_ids=array("q"),
            kv_committed_len=len(token_ids),
            extra_key=None,
        )
    )
    return generation


class LegacyFailClosedTreeCore(UnifiedTreeCore):
    """A registered backend with the interface's real fail-closed behavior."""

    def __init__(self, params: CacheInitParams, components) -> None:
        super().__init__(params, components)
        self.checked_calls = 0
        self.physical_demote_calls = 0

    def demote_session_checked(self, node_id) -> SessionDemoteExecution:
        self.checked_calls += 1
        return UnifiedTreeCoreInterface.demote_session_checked(self, node_id)

    def demote(self, node_id):  # pragma: no cover - its call is the failure oracle
        self.physical_demote_calls += 1
        raise AssertionError(f"physical demote must not run for {node_id!r}")


class InstalledCheckedDemoteSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self.registry_before = dict(_TREE_CORE_REGISTRY)
        self.backend_name = f"g0_legacy_fail_closed_{uuid4().hex}"
        register_tree_core_backend(self.backend_name, LegacyFailClosedTreeCore)
        with envs.SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND.override(self.backend_name):
            self.cache = UnifiedRadixCache(make_params())
        self.assertIsInstance(self.cache.tree_core, LegacyFailClosedTreeCore)

    def tearDown(self) -> None:
        _TREE_CORE_REGISTRY.clear()
        _TREE_CORE_REGISTRY.update(self.registry_before)

    def test_real_cache_routes_to_registered_fail_closed_backend(self) -> None:
        self.assertEqual(
            tuple(inspect.signature(UnifiedRadixCache.checked_demote_session).parameters),
            ("self", "session_id", "generation"),
        )
        self.assertEqual(
            tuple(inspect.signature(UnifiedTreeCoreInterface.demote_session_checked).parameters),
            ("self", "node_id"),
        )

        generation = insert_and_register(self.cache, "g0-installed-seam")
        result = self.cache.checked_demote_session("g0-installed-seam", generation)

        self.assertIsInstance(result, SessionCheckedDemoteOutcome)
        self.assertEqual(result.session_id, "g0-installed-seam")
        self.assertEqual(result.generation, generation)
        self.assertEqual(result.priority_release, "RELEASED")
        self.assertEqual(result.disposition, "REJECTED")
        self.assertEqual(result.reason, "REJECTED")
        self.assertEqual(len(result.nodes), 1)
        self.assertEqual(result.nodes[0].reason, "UNSUPPORTED_BACKEND")
        self.assertEqual(self.cache.tree_core.checked_calls, 1)
        self.assertEqual(self.cache.tree_core.physical_demote_calls, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
