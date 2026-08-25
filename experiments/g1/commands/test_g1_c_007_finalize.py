#!/usr/bin/env python3
"""Pure terminal-classification counterexamples for G1-C-007."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("g1_c_007_finalize.py")
SPEC = importlib.util.spec_from_file_location("g1_c_007_finalize", MODULE)
assert SPEC is not None and SPEC.loader is not None
FINALIZE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FINALIZE)


def record(arm: str) -> dict[str, object]:
    route = {
        "checked_facade": 1, "checked_backend": 1, "physical_demote": 0,
        "cache_owned_drain": 0, "stock_evict": 0, "physical_demote_node_ids": [],
    }
    observation = {
        "node_id": 7,
        "live": True,
        "host_committed": True,
        "write_through_pending": False,
        "load_back_pending": False,
        "lock_refs": [0],
        "session_ref": 1,
        "device_leaf": True,
        "device_ids": [42],
    }
    value: dict[str, object] = {
        "arm": arm,
        "operation": {"session_id": arm, "supplied_generation": 1},
        "component_qualification": {
            "components": ["FULL"], "supports_swa": False,
            "allocator_class": "TokenToKVPoolAllocator", "page_size": 1,
        },
        "priority_release": "RELEASED",
        "released_component_leaves": 1,
        "facade": {"disposition": "DEFERRED", "reason": "PLACEHOLDER"},
        "nodes": [],
        "freed_device_ids": [],
        "route_counters": route,
        "capacity": {
            "before": {"available_size": 1, "is_not_in_free_group": True},
            "after": {"available_size": 1, "is_not_in_free_group": True},
        },
        "target": {
            "requested_node_ids": [7], "eligible_node_ids": [7],
            "scheduled_node_ids": [], "completed_node_ids": [],
            "before": [copy.deepcopy(observation)],
            "after": [copy.deepcopy(observation)],
        },
    }
    if arm == "enabled":
        value["facade"] = {"disposition": "ACCEPTED", "reason": "ACCEPTED"}
        value["freed_device_ids"] = [42]
        value["route_counters"] = {
            **route, "physical_demote": 1, "cache_owned_drain": 1,
            "physical_demote_node_ids": [7],
        }
        value["capacity"]["after"]["available_size"] = 2
        value["target"]["completed_node_ids"] = [7]
        value["target"]["scheduled_node_ids"] = [7]
        value["target"]["after"][0]["device_ids"] = []
    elif arm == "bypass":
        value["facade"] = {"disposition": "BYPASSED", "reason": "PRIORITY_RELEASE_ONLY"}
        value["route_counters"] = {**route, "checked_facade": 0, "checked_backend": 0}
    elif arm == "stock_eviction_liveness":
        value["facade"] = {"disposition": "BYPASSED", "reason": "PRIORITY_RELEASE_ONLY"}
        value["route_counters"] = {**route, "checked_facade": 0, "checked_backend": 0, "stock_evict": 1}
        value["stock_eviction"] = {
            "candidate_ids_before": [7], "observed_calls": 1,
            "results": [{
                "num_tokens_evicted": 1, "swa_num_tokens_evicted": 0,
                "mamba_num_evicted": 0,
            }],
            "victims": [{
                "node_id": 7,
                "before": copy.deepcopy(observation),
                "after": {
                    **copy.deepcopy(observation), "device_ids": [], "device_leaf": False,
                },
                "capacity_before": {"available_size": 1, "is_not_in_free_group": True},
                "capacity_after": {"available_size": 2, "is_not_in_free_group": True},
            }],
        }
    else:
        reason = FINALIZE.REJECTION_REASONS[arm]
        value["facade"] = {"disposition": "DEFERRED", "reason": reason}
        if reason == "STALE_GENERATION":
            value["priority_release"] = "NOT_RELEASED"
            value["route_counters"] = {**route, "checked_backend": 0}
    return value


def records() -> list[dict[str, object]]:
    return [record(arm) for arm in FINALIZE.ARMS]


class G1C001TerminalTests(unittest.TestCase):
    def test_storage_preflight_minimum_is_manifest_bound(self) -> None:
        manifest = {
            "storage_preflight": {"minimum_free_bytes": FINALIZE.MINIMUM_FREE_BYTES},
        }
        self.assertEqual(FINALIZE.storage_minimum_free_bytes(manifest), FINALIZE.MINIMUM_FREE_BYTES)
        manifest["storage_preflight"]["minimum_free_bytes"] -= 1
        with self.assertRaises(ValueError):
            FINALIZE.storage_minimum_free_bytes(manifest)

    def test_runtime_wheel_filename_is_manifest_bound(self) -> None:
        manifest = {"archives": {"runtime_wheel": {"path": FINALIZE.RUNTIME_WHEEL_FILENAME}}}
        self.assertEqual(FINALIZE.runtime_wheel_filename(manifest), FINALIZE.RUNTIME_WHEEL_FILENAME)
        manifest["archives"]["runtime_wheel"]["path"] = "runtime-wheel.whl"
        with self.assertRaises(ValueError):
            FINALIZE.runtime_wheel_filename(manifest)

    def test_positive_records_pass(self) -> None:
        self.assertEqual(FINALIZE.classify_records(records())[0], "PASS")

    def test_enabled_missing_reclaim_stops(self) -> None:
        value = records()
        value[0]["freed_device_ids"] = []
        self.assertEqual(FINALIZE.classify_records(value)[0], "STOP")

    def test_bypass_physical_reclaim_stops(self) -> None:
        value = records()
        value[1]["route_counters"]["physical_demote"] = 1
        self.assertEqual(FINALIZE.classify_records(value)[0], "STOP")

    def test_bypass_priority_release_fault_is_invalid_not_stop(self) -> None:
        value = records()
        value[1]["priority_release"] = "NOT_RELEASED"
        self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_rejection_failure_is_invalid_not_stop(self) -> None:
        value = records()
        value[2]["facade"]["reason"] = "ACCEPTED"
        self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_malformed_record_is_invalid(self) -> None:
        value = copy.deepcopy(records())
        value[0].pop("capacity")
        self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_after_observation_missing_device_ids_is_invalid(self) -> None:
        value = records()
        value[0]["target"]["after"][0].pop("device_ids")
        self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_before_observation_with_noninteger_device_id_is_invalid(self) -> None:
        value = records()
        value[0]["target"]["before"][0]["device_ids"] = [42, "bad"]
        self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_minimal_stock_victim_is_invalid(self) -> None:
        value = records()
        value[-1]["stock_eviction"]["victims"] = [{}]
        self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_stock_tombstone_victim_after_is_valid(self) -> None:
        value = records()
        value[-1]["stock_eviction"]["victims"][0]["after"] = {
            "node_id": 7, "live": False,
        }
        self.assertEqual(FINALIZE.classify_records(value)[0], "PASS")


if __name__ == "__main__":
    unittest.main()
