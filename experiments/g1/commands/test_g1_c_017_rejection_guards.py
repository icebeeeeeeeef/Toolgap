#!/usr/bin/env python3
"""Mutation checks for the two C017 rejection-oracle completion guards."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PATCH_ONE = ROOT / "upstream/sglang/patches/0001-atomic-checked-demote.patch"
PATCH_TWO = ROOT / "upstream/sglang/patches/0002-g1-scripted-forced-demote-c017.patch"
PATCH_BASIS = ROOT / "upstream/sglang/patches/0002-g1-scripted-forced-demote-c012.patch"

PRIVATE_SESSION_HELPER = (
    "    @staticmethod\n"
    "    def _complete_private_session(\n"
    "        t: Any,\n"
    "        session_id: str,\n"
    "        rid: str,\n"
    "        *,\n"
    "        max_new_tokens: int = _MAX_NEW_TOKENS,\n"
    "    ) -> Generator[None, None, tuple[Any, int, tuple[int, ...]]]:\n"
    "        handle = _session_request(t, session_id, rid, max_new_tokens=max_new_tokens)\n"
)
PRIVATE_SESSION_HELPER_BASIS = (
    "    @staticmethod\n"
    "    def _complete_private_session(\n"
    "        t: Any, session_id: str, rid: str\n"
    "    ) -> Generator[None, None, tuple[Any, int, tuple[int, ...]]]:\n"
    "        handle = _session_request(t, session_id, rid, max_new_tokens=_MAX_NEW_TOKENS)\n"
)
LOAD_BACK_THRESHOLD_CALL = (
    "            yield from TestG1LoadBackPending._complete_private_session(\n"
    "                t,\n"
    "                session_id,\n"
    '                "g1-load-back-pending-first",\n'
    "                max_new_tokens=t.scheduler.tree_cache.load_back_threshold + 2,\n"
    "            )\n"
)
LOAD_BACK_THRESHOLD_CALL_BASIS = (
    "            yield from TestG1LoadBackPending._complete_private_session(\n"
    '                t, session_id, "g1-load-back-pending-first"\n'
    "            )\n"
)

LOAD_BACK_SUFFIX = "+            input_ids=target_input_ids + [7],\n"
LOAD_BACK_THRESHOLD_GENERATION = (
    "+                max_new_tokens=t.scheduler.tree_cache.load_back_threshold + 2,\n"
)
LOAD_BACK_THRESHOLD_QUALIFICATION = (
    "+        target_node = cache.tree_core.node_by_id(target_nodes[0])\n"
    "+        target_full_data = target_node.component_data[cache.tree_components[0]]\n"
    "+        target_host_value = target_full_data.host_value\n"
    "+        assert target_host_value is not None, target_nodes\n"
    "+        target_host_tokens = len(target_host_value)\n"
    "+        assert target_host_tokens >= cache.load_back_threshold, (\n"
    "+            target_host_tokens,\n"
    "+            cache.load_back_threshold,\n"
    "+        )\n"
)
EXACT_LOAD_BACK_ANCHOR = (
    "+                node.load_back_pending_id == node.id\n"
    "+                and node.id in cache.ongoing_load_back\n"
    "+                and cache.ongoing_load_back[node.id].node_id == node.id\n"
)

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


def applied_module_source(patch_source: str) -> str:
    lines = patch_source.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("@@ "))
    payload = lines[start + 1 :]
    if not payload or any(not line.startswith("+") for line in payload):
        raise ValueError("patch is not one complete added module")
    return "\n".join(line[1:] for line in payload) + "\n"


def added_block_source(block: str) -> str:
    lines = block.splitlines(keepends=True)
    if not lines or any(not line.startswith("+") for line in lines):
        raise ValueError("expected an added patch block")
    return "".join(line[1:] for line in lines)


def threshold_basis_errors(source: str, basis_source: str) -> list[str]:
    module = applied_module_source(source)
    replacements = (
        (PRIVATE_SESSION_HELPER, PRIVATE_SESSION_HELPER_BASIS, "private_session_helper"),
        (LOAD_BACK_THRESHOLD_CALL, LOAD_BACK_THRESHOLD_CALL_BASIS, "threshold_call"),
        (added_block_source(LOAD_BACK_THRESHOLD_QUALIFICATION), "", "qualification"),
    )
    errors = []
    for current, predecessor, label in replacements:
        if module.count(current) != 1:
            errors.append(label)
        else:
            module = module.replace(current, predecessor, 1)
    if not errors and module != applied_module_source(basis_source):
        errors.append("basis_delta")
    return errors


def load_back_fixture_contract_errors(source: str) -> list[str]:
    body = source.split("+class TestG1LoadBackPending", 1)[1].split(
        "\n+class TestG1HostCopyNotCommitted", 1
    )[0]
    errors = []
    if body.count(LOAD_BACK_SUFFIX) != 1:
        errors.append("frontier_suffix")
    if body.count(LOAD_BACK_THRESHOLD_GENERATION) != 1:
        errors.append("threshold_generation")
    if body.count(LOAD_BACK_THRESHOLD_QUALIFICATION) != 1:
        errors.append("threshold_qualification")
    if body.count(EXACT_LOAD_BACK_ANCHOR) != 1:
        errors.append("exact_anchor")
    if "+            input_ids=target_input_ids,\n" in body:
        errors.append("exact_frontier_replay")
    if "+        cache.load_back(" in body:
        errors.append("direct_load_back")
    assigns_ongoing = any(
        re.search(r"\]\s*=(?!=)", line)
        for line in body.splitlines()
        if "ongoing_load_back[" in line
    )
    assigns_pending_id = any(
        re.search(r"\.load_back_pending_id\s*=(?!=)", line)
        for line in body.splitlines()
    )
    if assigns_pending_id or assigns_ongoing:
        errors.append("manufactured_pending_state")
    return errors


class G1C017RejectionGuardMutationTests(unittest.TestCase):
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

    def test_load_back_fixture_extends_past_the_exact_frontier(self) -> None:
        source = PATCH_TWO.read_text(encoding="utf-8")
        self.assertEqual(load_back_fixture_contract_errors(source), [])

    def test_threshold_revision_has_exact_c012_basis(self) -> None:
        self.assertEqual(
            threshold_basis_errors(
                PATCH_TWO.read_text(encoding="utf-8"),
                PATCH_BASIS.read_text(encoding="utf-8"),
            ),
            [],
        )

    def test_indirect_pending_id_fabrication_is_red(self) -> None:
        source = PATCH_TWO.read_text(encoding="utf-8")
        mutant = source.replace(
            "+        loader = _session_request(\n",
            '+        setattr(target_node, "load_back_pending_id", target_node.id)\n'
            "+        loader = _session_request(\n",
            1,
        )
        self.assertEqual(load_back_fixture_contract_errors(mutant), [])
        self.assertEqual(
            threshold_basis_errors(
                mutant, PATCH_BASIS.read_text(encoding="utf-8")
            ),
            ["basis_delta"],
        )

    def test_mapping_update_pending_fabrication_is_red(self) -> None:
        source = PATCH_TWO.read_text(encoding="utf-8")
        mutant = source.replace(
            "+        loader = _session_request(\n",
            "+        cache.ongoing_load_back.update({target_node.id: object()})\n"
            "+        loader = _session_request(\n",
            1,
        )
        self.assertEqual(load_back_fixture_contract_errors(mutant), [])
        self.assertEqual(
            threshold_basis_errors(
                mutant, PATCH_BASIS.read_text(encoding="utf-8")
            ),
            ["basis_delta"],
        )

    def test_deleting_the_suffix_restores_the_c011_split_parent_counterexample(
        self,
    ) -> None:
        source = PATCH_TWO.read_text(encoding="utf-8")
        mutant = source.replace(LOAD_BACK_SUFFIX, "+            input_ids=target_input_ids,\n", 1)
        self.assertEqual(
            load_back_fixture_contract_errors(mutant),
            ["frontier_suffix", "exact_frontier_replay"],
        )

    def test_lowering_the_specialized_tail_to_eight_tokens_is_red(self) -> None:
        source = PATCH_TWO.read_text(encoding="utf-8")
        mutant = source.replace(
            LOAD_BACK_THRESHOLD_GENERATION,
            "+                max_new_tokens=_MAX_NEW_TOKENS,\n",
            1,
        )
        self.assertEqual(
            load_back_fixture_contract_errors(mutant),
            ["threshold_generation"],
        )

    def test_deleting_threshold_qualification_is_red(self) -> None:
        source = PATCH_TWO.read_text(encoding="utf-8")
        mutant = source.replace(LOAD_BACK_THRESHOLD_QUALIFICATION, "", 1)
        self.assertEqual(
            load_back_fixture_contract_errors(mutant),
            ["threshold_qualification"],
        )


if __name__ == "__main__":
    unittest.main()
