#!/usr/bin/env python3
"""Minimal terminal-classification checks for the G1-C020 record contract."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("g1_c_020_finalize.py")
SPEC = importlib.util.spec_from_file_location("g1_c_020_finalize", MODULE)
assert SPEC is not None and SPEC.loader is not None
FINALIZE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FINALIZE)


def record(arm: str) -> dict[str, object]:
    route = {
        "checked_facade": 1,
        "checked_backend": 1,
        "physical_demote": 0,
        "cache_owned_drain": 0,
        "stock_evict": 0,
        "physical_demote_node_ids": [],
    }
    observation = {
        "node_id": 7,
        "live": True,
        "host_committed": True,
        "host_value_present": True,
        "write_through_pending": False,
        "load_back_pending": False,
        "lock_refs": [0, 0, 0],
        "session_ref": 1,
        "device_leaf": True,
        "device_ids": [42],
    }
    value: dict[str, object] = {
        "arm": arm,
        "operation": {"session_id": arm, "supplied_generation": 1},
        "component_qualification": {
            "components": ["FULL"],
            "supports_swa": False,
            "allocator_class": "TokenToKVPoolAllocator",
            "page_size": 1,
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
        "host_pool": {},
        "target": {
            "requested_node_ids": [7],
            "eligible_node_ids": [7],
            "scheduled_node_ids": [],
            "completed_node_ids": [],
            "before": [copy.deepcopy(observation)],
            "after": [copy.deepcopy(observation)],
        },
    }
    if arm == "enabled":
        value.update(
            facade={"disposition": "ACCEPTED", "reason": "ACCEPTED"},
            freed_device_ids=[42],
            nodes=[{
                "node_id": 7,
                "disposition": "COMPLETED",
                "reason": "DEMOTED",
                "freed_device_ids": [42],
            }],
            route_counters={
                **route,
                "physical_demote": 1,
                "cache_owned_drain": 1,
                "physical_demote_node_ids": [7],
            },
        )
        value["capacity"]["after"]["available_size"] = 2
        value["target"]["scheduled_node_ids"] = [7]
        value["target"]["completed_node_ids"] = [7]
        value["target"]["after"][0].update(device_ids=[], device_leaf=False, session_ref=0)
    elif arm == "bypass":
        value.update(
            facade={"disposition": "BYPASSED", "reason": "PRIORITY_RELEASE_ONLY"},
            route_counters={**route, "checked_facade": 0, "checked_backend": 0},
        )
        value["target"]["after"][0]["session_ref"] = 0
    elif arm == "stock_eviction_liveness":
        value.update(
            facade={"disposition": "BYPASSED", "reason": "PRIORITY_RELEASE_ONLY"},
            route_counters={
                **route,
                "checked_facade": 0,
                "checked_backend": 0,
                "stock_evict": 1,
            },
            stock_eviction={
                "candidate_ids_before": [7],
                "observed_calls": 1,
                "results": [{
                    "num_tokens_evicted": 1,
                    "swa_num_tokens_evicted": 0,
                    "mamba_num_evicted": 0,
                }],
                "victims": [{
                    "node_id": 7,
                    "before": {**copy.deepcopy(observation), "session_ref": 0},
                    "after": {
                        **copy.deepcopy(observation),
                        "device_ids": [],
                        "device_leaf": False,
                        "session_ref": 0,
                    },
                    "capacity_before": {"available_size": 1, "is_not_in_free_group": True},
                    "capacity_after": {"available_size": 2, "is_not_in_free_group": True},
                }],
            },
        )
        value["target"]["after"][0]["session_ref"] = 0
    else:
        reason = FINALIZE.REJECTION_REASONS[arm]
        if reason == "STALE_GENERATION":
            value.update(
                facade={"disposition": "REJECTED", "reason": reason},
                priority_release="NOT_RELEASED",
                released_component_leaves=0,
                route_counters={**route, "checked_backend": 0},
                operation={"session_id": arm, "supplied_generation": 1, "current_generation": 2},
                target={
                    "requested_node_ids": [],
                    "eligible_node_ids": [],
                    "scheduled_node_ids": [],
                    "completed_node_ids": [],
                    "before": [],
                    "after": [],
                },
            )
        else:
            value["facade"] = {"disposition": "DEFERRED", "reason": "DEFERRED"}
            value["target"]["eligible_node_ids"] = []
            value["target"]["scheduled_node_ids"] = [7]
            before, after = value["target"]["before"][0], value["target"]["after"][0]
            after["session_ref"] = 0
            if reason == "WRITE_THROUGH_PENDING":
                for item in (before, after):
                    item.update(host_committed=False, write_through_pending=True, lock_refs=[1, 0, 0])
            elif reason == "NON_TARGET_SESSION_COVERAGE":
                before["session_ref"], after["session_ref"] = 2, 1
            elif reason == "DEVICE_LOCKED":
                before["lock_refs"] = after["lock_refs"] = [1, 0, 0]
            elif reason == "LOAD_BACK_PENDING":
                for item in (before, after):
                    item.update(
                        host_committed=False,
                        load_back_pending=True,
                        lock_refs=[1, 0, 0],
                        device_leaf=False,
                    )
            elif reason == "HOST_COPY_NOT_COMMITTED":
                for item in (before, after):
                    item.update(host_committed=False, host_value_present=False)
                value["host_pool"] = {
                    "logical_size": 2,
                    "available_before_reservation": 2,
                    "reserved_indices": [0, 1],
                    "available_while_reserved": 0,
                    "release_returned": 2,
                    "available_after_release": 2,
                }
            value["nodes"] = [{
                "node_id": 7,
                "disposition": "DEFERRED",
                "reason": reason,
                "freed_device_ids": [],
            }]
    return value


def records() -> list[dict[str, object]]:
    return [record(arm) for arm in FINALIZE.ARMS]


class G1C020TerminalTests(unittest.TestCase):
    def test_complete_nine_arm_record_set_passes(self) -> None:
        self.assertEqual(FINALIZE.classify_records(records())[0], "PASS")

    def test_enabled_missing_reclaim_stops(self) -> None:
        value = records()
        enabled = value[0]
        enabled["freed_device_ids"] = []
        enabled["nodes"][0]["freed_device_ids"] = []
        enabled["target"]["after"][0].update(device_ids=[42], device_leaf=True)
        enabled["capacity"]["after"]["available_size"] = 1
        self.assertEqual(FINALIZE.classify_records(value)[0], "STOP")

    def test_bypass_physical_reclaim_stops(self) -> None:
        value = records()
        bypass = value[1]
        bypass["route_counters"].update(
            physical_demote=1,
            physical_demote_node_ids=[7],
            cache_owned_drain=1,
        )
        bypass["target"]["after"][0].update(device_ids=[], device_leaf=False)
        bypass["capacity"]["after"]["available_size"] = 2
        self.assertEqual(FINALIZE.classify_records(value)[0], "STOP")

    def test_rejection_contract_fault_is_invalid(self) -> None:
        value = records()
        next(
            item for item in value if item["arm"] == "reject_write_through_pending"
        )["facade"]["reason"] = "ACCEPTED"
        self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_malformed_record_is_invalid(self) -> None:
        value = records()
        value[0].pop("facade")
        self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_invalid_precedes_causal_stop(self) -> None:
        value = records()
        enabled = value[0]
        enabled["freed_device_ids"] = []
        enabled["nodes"][0]["freed_device_ids"] = []
        enabled["target"]["after"][0].update(device_ids=[42], device_leaf=True)
        enabled["capacity"]["after"]["available_size"] = 1
        next(
            item for item in value if item["arm"] == "reject_write_through_pending"
        )["facade"]["reason"] = "ACCEPTED"
        self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")


if __name__ == "__main__":
    unittest.main()
