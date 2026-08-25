#!/usr/bin/env python3
"""Pure terminal-classification counterexamples for G1-C-009."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("g1_c_009_finalize.py")
SPEC = importlib.util.spec_from_file_location("g1_c_009_finalize", MODULE)
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
        if reason == "STALE_GENERATION":
            value["facade"] = {"disposition": "REJECTED", "reason": reason}
            value["priority_release"] = "NOT_RELEASED"
            value["released_component_leaves"] = 0
            value["route_counters"] = {**route, "checked_backend": 0}
            value["operation"] = {
                "session_id": arm,
                "supplied_generation": 1,
                "current_generation": 2,
            }
            value["target"] = {
                "requested_node_ids": [], "eligible_node_ids": [],
                "scheduled_node_ids": [], "completed_node_ids": [],
                "before": [], "after": [],
            }
        else:
            value["facade"] = {"disposition": "DEFERRED", "reason": "DEFERRED"}
            value["target"]["eligible_node_ids"] = []
            value["target"]["scheduled_node_ids"] = [7]
            before = value["target"]["before"][0]
            after = value["target"]["after"][0]
            after["session_ref"] = 0
            if reason == "WRITE_THROUGH_PENDING":
                for observation in (before, after):
                    observation["host_committed"] = False
                    observation["write_through_pending"] = True
            elif reason == "NON_TARGET_SESSION_COVERAGE":
                before["session_ref"] = 2
                after["session_ref"] = 1
            elif reason == "DEVICE_LOCKED":
                for observation in (before, after):
                    observation["lock_refs"] = [1]
            value["nodes"] = [{
                "node_id": 7,
                "disposition": "DEFERRED",
                "reason": reason,
                "freed_device_ids": [],
            }]
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

    def test_deferred_rejections_keep_specific_reason_on_nodes(self) -> None:
        for arm in (
            "reject_write_through_pending",
            "reject_non_target_session_coverage",
            "reject_device_locked",
        ):
            with self.subTest(arm=arm):
                value = record(arm)
                self.assertEqual(
                    value["facade"],
                    {"disposition": "DEFERRED", "reason": "DEFERRED"},
                )
                self.assertEqual(
                    FINALIZE.classify_records(
                        [value if item["arm"] == arm else item for item in records()]
                    )[0],
                    "PASS",
                )

    def test_specific_node_reason_cannot_replace_facade_aggregate(self) -> None:
        value = records()
        value[2]["facade"]["reason"] = FINALIZE.REJECTION_REASONS[value[2]["arm"]]
        self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_deferred_node_reason_is_required(self) -> None:
        value = records()
        value[2]["nodes"][0]["reason"] = "DEVICE_LOCKED"
        self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_malformed_deferred_node_is_invalid(self) -> None:
        value = records()
        value[2]["nodes"] = [{}]
        self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_stale_generation_is_rejected_before_backend(self) -> None:
        stale = record("reject_stale_generation")
        self.assertEqual(
            stale["facade"],
            {"disposition": "REJECTED", "reason": "STALE_GENERATION"},
        )
        self.assertEqual(FINALIZE.classify_records(records())[0], "PASS")

    def test_deferred_rejection_target_forgery_is_invalid(self) -> None:
        mutators = {
            "eligible": lambda item: item["target"].__setitem__("eligible_node_ids", [7]),
            "missing_scheduled": lambda item: item["target"].__setitem__("scheduled_node_ids", []),
            "completed": lambda item: item["target"].__setitem__("completed_node_ids", [7]),
            "missing_before": lambda item: item["target"].__setitem__("before", []),
            "missing_after": lambda item: item["target"].__setitem__("after", []),
            "device_removed": lambda item: item["target"]["after"][0].__setitem__("device_ids", []),
            "zero_released_leaves": lambda item: item.__setitem__("released_component_leaves", 0),
            "fake_physical_ids": lambda item: item["route_counters"].__setitem__("physical_demote_node_ids", [7]),
            "extra_operation_target": lambda item: item["operation"].__setitem__("node_id", 7),
        }
        for label, mutate in mutators.items():
            with self.subTest(label=label):
                value = records()
                mutate(value[2])
                self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_deferred_duplicate_ids_are_invalid_even_when_sets_align(self) -> None:
        value = records()
        deferred = value[2]
        for field in ("requested_node_ids", "scheduled_node_ids"):
            deferred["target"][field] = [7, 7]
        for field in ("before", "after"):
            deferred["target"][field] = [
                copy.deepcopy(deferred["target"][field][0]),
                copy.deepcopy(deferred["target"][field][0]),
            ]
        deferred["nodes"] = [
            copy.deepcopy(deferred["nodes"][0]),
            copy.deepcopy(deferred["nodes"][0]),
        ]
        self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_write_through_reason_requires_persistent_pending_state(self) -> None:
        mutators = {
            "before_not_pending": lambda item: item["target"]["before"][0].__setitem__("write_through_pending", False),
            "after_not_pending": lambda item: item["target"]["after"][0].__setitem__("write_through_pending", False),
            "before_claims_committed": lambda item: item["target"]["before"][0].__setitem__("host_committed", True),
            "after_claims_committed": lambda item: item["target"]["after"][0].__setitem__("host_committed", True),
        }
        for label, mutate in mutators.items():
            with self.subTest(label=label):
                value = records()
                mutate(value[2])
                self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_non_target_reason_requires_shared_coverage_transition(self) -> None:
        mutators = {
            "before_not_shared": lambda item: item["target"]["before"][0].__setitem__("session_ref", 1),
            "after_not_remaining": lambda item: item["target"]["after"][0].__setitem__("session_ref", 0),
            "host_not_committed": lambda item: item["target"]["before"][0].__setitem__("host_committed", False),
            "not_device_leaf": lambda item: item["target"]["after"][0].__setitem__("device_leaf", False),
        }
        for label, mutate in mutators.items():
            with self.subTest(label=label):
                value = records()
                mutate(value[3])
                self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_device_locked_reason_requires_live_lock(self) -> None:
        for phase in ("before", "after"):
            with self.subTest(phase=phase):
                value = records()
                value[4]["target"][phase][0]["lock_refs"] = [0]
                self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_each_deferred_reason_preserves_nonempty_device_ids(self) -> None:
        for arm_index in (2, 3, 4):
            for phase in ("before", "after"):
                with self.subTest(arm=FINALIZE.ARMS[arm_index], phase=phase):
                    value = records()
                    value[arm_index]["target"][phase][0]["device_ids"] = []
                    self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_stale_generation_contract_forgery_is_invalid(self) -> None:
        mutators = {
            "missing_current_generation": lambda item: item["operation"].pop("current_generation"),
            "same_generation": lambda item: item["operation"].__setitem__("current_generation", 1),
            "bool_supplied_generation": lambda item: item["operation"].__setitem__("supplied_generation", True),
            "bool_current_generation": lambda item: item["operation"].__setitem__("current_generation", True),
            "extra_operation_field": lambda item: item["operation"].__setitem__("extra", 3),
            "released_leaves": lambda item: item.__setitem__("released_component_leaves", 1),
            "node_outcome": lambda item: item.__setitem__("nodes", [{
                "node_id": 7, "disposition": "DEFERRED",
                "reason": "DEVICE_LOCKED", "freed_device_ids": [],
            }]),
        }
        for label, mutate in mutators.items():
            with self.subTest(label=label):
                value = records()
                mutate(value[5])
                self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_stale_generation_target_must_be_completely_empty(self) -> None:
        for field in (
            "requested_node_ids", "eligible_node_ids", "scheduled_node_ids",
            "completed_node_ids", "before", "after",
        ):
            with self.subTest(field=field):
                value = records()
                stale = value[5]
                if field in {"before", "after"}:
                    stale["target"][field] = [copy.deepcopy(record("enabled")["target"]["before"][0])]
                else:
                    stale["target"][field] = [7]
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

    def test_enabled_bool_as_int_combination_is_invalid(self) -> None:
        value = records()
        enabled = value[0]
        enabled["component_qualification"]["page_size"] = True
        enabled["operation"]["supplied_generation"] = True
        enabled["released_component_leaves"] = True
        enabled["route_counters"]["checked_facade"] = True
        enabled["route_counters"]["checked_backend"] = True
        enabled["route_counters"]["physical_demote"] = True
        enabled["route_counters"]["cache_owned_drain"] = True
        enabled["capacity"]["before"]["available_size"] = True
        self.assertEqual(FINALIZE.classify_records(value)[0], "INVALID")

    def test_record_integer_fields_reject_bool(self) -> None:
        mutators = (
            lambda item: item["component_qualification"].__setitem__("page_size", True),
            lambda item: item["operation"].__setitem__("supplied_generation", True),
            lambda item: item.__setitem__("released_component_leaves", True),
            lambda item: item["route_counters"].__setitem__("checked_facade", True),
            lambda item: item["route_counters"].__setitem__("physical_demote_node_ids", [True]),
            lambda item: item.__setitem__("freed_device_ids", [True]),
            lambda item: item["target"].__setitem__("requested_node_ids", [True]),
            lambda item: item["capacity"]["before"].__setitem__("available_size", True),
        )
        for mutate in mutators:
            with self.subTest(mutate=mutate):
                enabled = record("enabled")
                mutate(enabled)
                self.assertTrue(FINALIZE.record_errors(enabled, "enabled"))

    def test_gpu_sample_arm_pid_rejects_bool(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "samples.json"
            path.write_text(json.dumps({
                "arm_pid": True,
                "poll_seconds": 0.25,
                "samples": [{"captured_at": "2026-08-25T00:00:00Z", "pids": [1]}],
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                FINALIZE.validate_gpu_samples(path, 1, [1], "enabled")


if __name__ == "__main__":
    unittest.main()
