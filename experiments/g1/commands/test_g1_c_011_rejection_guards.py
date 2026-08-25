#!/usr/bin/env python3
"""Mutation checks for the two C011 rejection-oracle completion guards."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PATCH_ONE = ROOT / "upstream/sglang/patches/0001-atomic-checked-demote.patch"
PATCH_TWO = ROOT / "upstream/sglang/patches/0002-g1-scripted-forced-demote-c011.patch"

GUARDS = {
    "load_back_pending": (
        "+        if node.load_back_pending_id is not None:\n"
        "+            return SessionDemoteExecution(\n"
        "+                node_id, \"DEFERRED\", \"LOAD_BACK_PENDING\"\n"
        "+            )\n"
    ),
    "host_copy_not_committed": (
        "+        if not self._is_settled_full_host_duplicate(node):\n"
        "+            return SessionDemoteExecution(\n"
        "+                node_id, \"DEFERRED\", \"HOST_COPY_NOT_COMMITTED\"\n"
        "+            )\n"
    ),
}


def guard_contract_errors(source: str) -> list[str]:
    return [name for name, guard in GUARDS.items() if source.count(guard) != 1]


class G1C011RejectionGuardMutationTests(unittest.TestCase):
    def test_frozen_implementation_contains_each_guard_once(self) -> None:
        self.assertEqual(guard_contract_errors(PATCH_ONE.read_text(encoding="utf-8")), [])

    def test_deleting_either_guard_is_red(self) -> None:
        source = PATCH_ONE.read_text(encoding="utf-8")
        for name, guard in GUARDS.items():
            with self.subTest(name=name):
                mutant = source.replace(guard, "", 1)
                self.assertEqual(guard_contract_errors(mutant), [name])

    def test_runtime_rows_bind_the_corresponding_specific_reasons(self) -> None:
        source = PATCH_TWO.read_text(encoding="utf-8")
        expectations = {
            "TestG1LoadBackPending": "LOAD_BACK_PENDING",
            "TestG1HostCopyNotCommitted": "HOST_COPY_NOT_COMMITTED",
        }
        for class_name, reason in expectations.items():
            with self.subTest(class_name=class_name):
                body = source.split(f"+class {class_name}", 1)[1].split("\n+class ", 1)[0]
                self.assertIn(f'_assert_deferred_node_reason(outcome, "{reason}")', body)


if __name__ == "__main__":
    unittest.main()
