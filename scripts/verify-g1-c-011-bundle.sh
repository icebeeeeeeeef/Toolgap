#!/usr/bin/env bash
# Static contract checks for the independent formal G1-C-011 source bundle.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/.." && pwd -P)"
PYTHON="${PYTHON:-python3}"
SPEC="$ROOT/experiments/g1/SPEC.g1-c-011.md"
TEMPLATE="$ROOT/experiments/g1/manifest.g1-c-011.template.json"
BOOTSTRAP="$ROOT/experiments/g1/commands/00-g1-c-011-bootstrap.sh"
RUNNER="$ROOT/experiments/g1/commands/20-g1-c-011.sh"
BUILDER="$ROOT/experiments/g1/commands/g1_c_011_bundle_manifest.py"
ARM_LAUNCHER="$ROOT/experiments/g1/commands/g1_c_011_arm_launcher.py"
EXTRACTOR="$ROOT/experiments/g1/commands/g1_c_011_extract_records.py"
FINALIZER="$ROOT/experiments/g1/commands/g1_c_011_finalize.py"
TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_finalize.py"
ARM_LAUNCHER_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_arm_launcher.py"
GPU_SAMPLER="$ROOT/experiments/g1/commands/g1_c_011_gpu_sampler.py"
GPU_SAMPLER_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_gpu_sampler.py"
SIGNAL_CLEANUP_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_signal_cleanup.sh"
SOURCE_RESTORE_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_source_restore.sh"
RUNTIME_WHEEL_NAME_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_runtime_wheel_name.sh"
ARM_RUNNER_SPAWN_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_arm_runner_spawn.sh"
ANCHOR_OFFLINE_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_anchor_offline.sh"
REQUEST_ADMISSION_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_request_admission.py"
SHARED_COVERAGE_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_shared_coverage.py"
REJECTION_GUARD_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_rejection_guards.py"
STORAGE_PREFLIGHT_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_storage_preflight.sh"
BUILDER_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_bundle_manifest.py"
PRE_EXECUTION_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_pre_execution.py"
FAILURE_EVIDENCE_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_failure_evidence.sh"
CLEANUP_FAILURE_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_cleanup_failure.sh"
HOST_MISMATCH_TESTS="$ROOT/experiments/g1/commands/test_g1_c_011_host_mismatch.sh"
PLAN="$ROOT/worklog/plans/2026-08-25/g1-c-011-rejection-oracle-completion.md"
LESSON="$ROOT/worklog/lessons/2026-08-25/g1-c-009-request-admission-race.md"
CONTROL_REVIEW="$ROOT/worklog/reviews/2026-08-25/g1-c-010-final-matrix-review.md"
ANCHOR="$ROOT/scripts/anchor-g1-c-011-oss.sh"

for path in "$SPEC" "$TEMPLATE" "$BOOTSTRAP" "$RUNNER" "$BUILDER" "$ARM_LAUNCHER" "$EXTRACTOR" "$FINALIZER" "$TESTS" "$ARM_LAUNCHER_TESTS" "$GPU_SAMPLER" "$GPU_SAMPLER_TESTS" "$SIGNAL_CLEANUP_TESTS" "$SOURCE_RESTORE_TESTS" "$RUNTIME_WHEEL_NAME_TESTS" "$ARM_RUNNER_SPAWN_TESTS" "$ANCHOR_OFFLINE_TESTS" "$REQUEST_ADMISSION_TESTS" "$SHARED_COVERAGE_TESTS" "$REJECTION_GUARD_TESTS" "$STORAGE_PREFLIGHT_TESTS" "$BUILDER_TESTS" "$PRE_EXECUTION_TESTS" "$FAILURE_EVIDENCE_TESTS" "$CLEANUP_FAILURE_TESTS" "$HOST_MISMATCH_TESTS" "$PLAN" "$LESSON" "$CONTROL_REVIEW" "$ANCHOR"; do
  test -f "$path"
done
bash -n "$BOOTSTRAP"
bash -n "$RUNNER"
bash -n "$ANCHOR"
"$PYTHON" -m py_compile "$BUILDER" "$ARM_LAUNCHER" "$EXTRACTOR" "$FINALIZER" "$TESTS" "$ARM_LAUNCHER_TESTS" "$GPU_SAMPLER" "$GPU_SAMPLER_TESTS" "$BUILDER_TESTS" "$PRE_EXECUTION_TESTS" "$REQUEST_ADMISSION_TESTS" "$SHARED_COVERAGE_TESTS" "$REJECTION_GUARD_TESTS"
"$PYTHON" "$BUILDER_TESTS"
"$PYTHON" "$PRE_EXECUTION_TESTS"
"$PYTHON" "$TESTS"
"$PYTHON" "$ARM_LAUNCHER_TESTS"
"$PYTHON" "$GPU_SAMPLER_TESTS"
bash "$SIGNAL_CLEANUP_TESTS"
bash "$SOURCE_RESTORE_TESTS"
bash "$RUNTIME_WHEEL_NAME_TESTS"
bash "$ARM_RUNNER_SPAWN_TESTS"
bash "$ANCHOR_OFFLINE_TESTS"
"$PYTHON" "$REQUEST_ADMISSION_TESTS"
"$PYTHON" "$SHARED_COVERAGE_TESTS"
"$PYTHON" "$REJECTION_GUARD_TESTS"
bash "$STORAGE_PREFLIGHT_TESTS"
bash "$FAILURE_EVIDENCE_TESTS"
bash "$CLEANUP_FAILURE_TESTS"
bash "$HOST_MISMATCH_TESTS"
PREDECESSOR="8b19400e4ea8dedeec9aba60b5d3a56a9d12dcfa"
git -C "$ROOT" diff --check "$PREDECESSOR"

# G1-C-011 must match every listed frozen predecessor path to the explicit
# C-009 predecessor commit, not merely to the current index.
FROZEN=(
  experiments/g1/artifacts/model-files.g1-preflight-001.json
  upstream/sglang/patches/0001-atomic-checked-demote.patch
  upstream/sglang/patches/0002-g1-scripted-forced-demote.patch
  upstream/sglang/patches/0003-cuda12-compat-packaging.patch
  experiments/g1/SPEC.g1-preflight-001.md
  experiments/g1/manifest.g1-preflight-001.template.json
  experiments/g1/commands/00-g1-preflight-001-bootstrap.sh
  experiments/g1/commands/20-g1-preflight-001.sh
  experiments/g1/commands/g1_preflight_001_bundle_manifest.py
  experiments/g1/commands/g1_preflight_001_finalize.py
  experiments/g1/SPEC.cuda12-compat-001.md
  experiments/g1/manifest.cuda12-compat-001.template.json
  experiments/g1/commands/00-cuda12-compat-001-bootstrap.sh
  experiments/g1/commands/20-cuda12-compat-001.sh
  experiments/g1/commands/cuda12_compat_001_bundle_manifest.py
  experiments/g1/commands/cuda12_compat_001_finalize.py
  experiments/g1/SPEC.g1-c-001.md
  experiments/g1/manifest.g1-c-001.template.json
  experiments/g1/commands/00-g1-c-001-bootstrap.sh
  experiments/g1/commands/20-g1-c-001.sh
  experiments/g1/commands/g1_c_001_bundle_manifest.py
  experiments/g1/commands/g1_c_001_finalize.py
  experiments/g1/commands/g1_c_001_extract_records.py
  experiments/g1/commands/g1_c_001_gpu_sampler.py
  experiments/g1/commands/test_g1_c_001_finalize.py
  experiments/g1/commands/test_g1_c_001_gpu_sampler.py
  experiments/g1/commands/test_g1_c_001_signal_cleanup.sh
  scripts/verify-g1-c-001-bundle.sh
  scripts/anchor-g1-c-001-oss.sh
  experiments/g1/SPEC.g1-c-002.md
  experiments/g1/manifest.g1-c-002.template.json
  experiments/g1/commands/00-g1-c-002-bootstrap.sh
  experiments/g1/commands/20-g1-c-002.sh
  experiments/g1/commands/g1_c_002_bundle_manifest.py
  experiments/g1/commands/g1_c_002_finalize.py
  experiments/g1/commands/g1_c_002_extract_records.py
  experiments/g1/commands/g1_c_002_gpu_sampler.py
  experiments/g1/commands/test_g1_c_002_finalize.py
  experiments/g1/commands/test_g1_c_002_gpu_sampler.py
  experiments/g1/commands/test_g1_c_002_signal_cleanup.sh
  experiments/g1/commands/test_g1_c_002_source_restore.sh
  scripts/verify-g1-c-002-bundle.sh
  scripts/anchor-g1-c-002-oss.sh
  experiments/g1/SPEC.g1-c-003.md
  experiments/g1/manifest.g1-c-003.template.json
  experiments/g1/commands/00-g1-c-003-bootstrap.sh
  experiments/g1/commands/20-g1-c-003.sh
  experiments/g1/commands/g1_c_003_bundle_manifest.py
  experiments/g1/commands/g1_c_003_finalize.py
  experiments/g1/commands/g1_c_003_extract_records.py
  experiments/g1/commands/g1_c_003_gpu_sampler.py
  experiments/g1/commands/test_g1_c_003_finalize.py
  experiments/g1/commands/test_g1_c_003_gpu_sampler.py
  experiments/g1/commands/test_g1_c_003_signal_cleanup.sh
  experiments/g1/commands/test_g1_c_003_source_restore.sh
  scripts/verify-g1-c-003-bundle.sh
  scripts/anchor-g1-c-003-oss.sh
  experiments/g1/SPEC.g1-c-004.md
  experiments/g1/manifest.g1-c-004.template.json
  experiments/g1/commands/00-g1-c-004-bootstrap.sh
  experiments/g1/commands/20-g1-c-004.sh
  experiments/g1/commands/g1_c_004_bundle_manifest.py
  experiments/g1/commands/g1_c_004_finalize.py
  experiments/g1/commands/g1_c_004_extract_records.py
  experiments/g1/commands/g1_c_004_gpu_sampler.py
  experiments/g1/commands/test_g1_c_004_finalize.py
  experiments/g1/commands/test_g1_c_004_gpu_sampler.py
  experiments/g1/commands/test_g1_c_004_runtime_wheel_name.sh
  experiments/g1/commands/test_g1_c_004_signal_cleanup.sh
  experiments/g1/commands/test_g1_c_004_source_restore.sh
  scripts/verify-g1-c-004-bundle.sh
  scripts/anchor-g1-c-004-oss.sh
  experiments/g1/SPEC.g1-c-005.md
  experiments/g1/manifest.g1-c-005.template.json
  experiments/g1/commands/00-g1-c-005-bootstrap.sh
  experiments/g1/commands/20-g1-c-005.sh
  experiments/g1/commands/g1_c_005_bundle_manifest.py
  experiments/g1/commands/g1_c_005_finalize.py
  experiments/g1/commands/g1_c_005_extract_records.py
  experiments/g1/commands/g1_c_005_gpu_sampler.py
  experiments/g1/commands/test_g1_c_005_finalize.py
  experiments/g1/commands/test_g1_c_005_gpu_sampler.py
  experiments/g1/commands/test_g1_c_005_runtime_wheel_name.sh
  experiments/g1/commands/test_g1_c_005_signal_cleanup.sh
  experiments/g1/commands/test_g1_c_005_source_restore.sh
  experiments/g1/commands/test_g1_c_005_arm_runner_spawn.sh
  scripts/verify-g1-c-005-bundle.sh
  scripts/anchor-g1-c-005-oss.sh
  experiments/g1/SPEC.g1-c-006.md
  experiments/g1/manifest.g1-c-006.template.json
  experiments/g1/commands/00-g1-c-006-bootstrap.sh
  experiments/g1/commands/20-g1-c-006.sh
  experiments/g1/commands/g1_c_006_bundle_manifest.py
  experiments/g1/commands/g1_c_006_finalize.py
  experiments/g1/commands/g1_c_006_extract_records.py
  experiments/g1/commands/g1_c_006_gpu_sampler.py
  experiments/g1/commands/test_g1_c_006_finalize.py
  experiments/g1/commands/test_g1_c_006_gpu_sampler.py
  experiments/g1/commands/test_g1_c_006_runtime_wheel_name.sh
  experiments/g1/commands/test_g1_c_006_signal_cleanup.sh
  experiments/g1/commands/test_g1_c_006_source_restore.sh
  experiments/g1/commands/test_g1_c_006_arm_runner_spawn.sh
  experiments/g1/commands/test_g1_c_006_storage_preflight.sh
  scripts/verify-g1-c-006-bundle.sh
  scripts/anchor-g1-c-006-oss.sh
  experiments/g1/SPEC.g1-c-007.md
  experiments/g1/manifest.g1-c-007.template.json
  experiments/g1/commands/00-g1-c-007-bootstrap.sh
  experiments/g1/commands/20-g1-c-007.sh
  experiments/g1/commands/g1_c_007_arm_launcher.py
  experiments/g1/commands/g1_c_007_bundle_manifest.py
  experiments/g1/commands/g1_c_007_extract_records.py
  experiments/g1/commands/g1_c_007_finalize.py
  experiments/g1/commands/g1_c_007_gpu_sampler.py
  experiments/g1/commands/test_g1_c_007_arm_launcher.py
  experiments/g1/commands/test_g1_c_007_arm_runner_spawn.sh
  experiments/g1/commands/test_g1_c_007_bundle_manifest.py
  experiments/g1/commands/test_g1_c_007_cleanup_failure.sh
  experiments/g1/commands/test_g1_c_007_failure_evidence.sh
  experiments/g1/commands/test_g1_c_007_finalize.py
  experiments/g1/commands/test_g1_c_007_gpu_sampler.py
  experiments/g1/commands/test_g1_c_007_host_mismatch.sh
  experiments/g1/commands/test_g1_c_007_pre_execution.py
  experiments/g1/commands/test_g1_c_007_runtime_wheel_name.sh
  experiments/g1/commands/test_g1_c_007_signal_cleanup.sh
  experiments/g1/commands/test_g1_c_007_source_restore.sh
  experiments/g1/commands/test_g1_c_007_storage_preflight.sh
  scripts/verify-g1-c-007-bundle.sh
  scripts/anchor-g1-c-007-oss.sh
  worklog/plans/2026-08-25/g1-c-007-pre-run-review-repairs.md
  worklog/reviews/2026-08-25/g1-c-007-code-quality-review.md
  experiments/g1/SPEC.g1-c-008.md
  experiments/g1/manifest.g1-c-008.template.json
  experiments/g1/commands/00-g1-c-008-bootstrap.sh
  experiments/g1/commands/20-g1-c-008.sh
  experiments/g1/commands/g1_c_008_arm_launcher.py
  experiments/g1/commands/g1_c_008_bundle_manifest.py
  experiments/g1/commands/g1_c_008_extract_records.py
  experiments/g1/commands/g1_c_008_finalize.py
  experiments/g1/commands/g1_c_008_gpu_sampler.py
  experiments/g1/commands/test_g1_c_008_anchor_offline.sh
  experiments/g1/commands/test_g1_c_008_arm_launcher.py
  experiments/g1/commands/test_g1_c_008_arm_runner_spawn.sh
  experiments/g1/commands/test_g1_c_008_bundle_manifest.py
  experiments/g1/commands/test_g1_c_008_cleanup_failure.sh
  experiments/g1/commands/test_g1_c_008_failure_evidence.sh
  experiments/g1/commands/test_g1_c_008_finalize.py
  experiments/g1/commands/test_g1_c_008_gpu_sampler.py
  experiments/g1/commands/test_g1_c_008_host_mismatch.sh
  experiments/g1/commands/test_g1_c_008_pre_execution.py
  experiments/g1/commands/test_g1_c_008_runtime_wheel_name.sh
  experiments/g1/commands/test_g1_c_008_signal_cleanup.sh
  experiments/g1/commands/test_g1_c_008_source_restore.sh
  experiments/g1/commands/test_g1_c_008_storage_preflight.sh
  scripts/verify-g1-c-008-bundle.sh
  scripts/anchor-g1-c-008-oss.sh
  worklog/lessons/2026-08-25/g1-c-007-scripted-module-identity.md
  worklog/lessons/2026-08-25/g1-c-008-anchor-portability.md
  worklog/plans/2026-08-25/g1-c-008-importable-arm-module.md
  experiments/g1/SPEC.g1-c-009.md
  experiments/g1/manifest.g1-c-009.template.json
  experiments/g1/commands/00-g1-c-009-bootstrap.sh
  experiments/g1/commands/20-g1-c-009.sh
  experiments/g1/commands/g1_c_009_arm_launcher.py
  experiments/g1/commands/g1_c_009_bundle_manifest.py
  experiments/g1/commands/g1_c_009_extract_records.py
  experiments/g1/commands/g1_c_009_finalize.py
  experiments/g1/commands/g1_c_009_gpu_sampler.py
  experiments/g1/commands/test_g1_c_009_anchor_offline.sh
  experiments/g1/commands/test_g1_c_009_arm_launcher.py
  experiments/g1/commands/test_g1_c_009_arm_runner_spawn.sh
  experiments/g1/commands/test_g1_c_009_bundle_manifest.py
  experiments/g1/commands/test_g1_c_009_cleanup_failure.sh
  experiments/g1/commands/test_g1_c_009_failure_evidence.sh
  experiments/g1/commands/test_g1_c_009_finalize.py
  experiments/g1/commands/test_g1_c_009_gpu_sampler.py
  experiments/g1/commands/test_g1_c_009_host_mismatch.sh
  experiments/g1/commands/test_g1_c_009_pre_execution.py
  experiments/g1/commands/test_g1_c_009_runtime_wheel_name.sh
  experiments/g1/commands/test_g1_c_009_shared_coverage.py
  experiments/g1/commands/test_g1_c_009_signal_cleanup.sh
  experiments/g1/commands/test_g1_c_009_source_restore.sh
  experiments/g1/commands/test_g1_c_009_storage_preflight.sh
  scripts/verify-g1-c-009-bundle.sh
  scripts/anchor-g1-c-009-oss.sh
  upstream/sglang/patches/0002-g1-scripted-forced-demote-c009.patch
  worklog/plans/2026-08-25/g1-c-009-shared-coverage-fixture.md
  worklog/lessons/2026-08-25/g1-c-009-shared-coverage-fixture.md
  worklog/lessons/2026-08-25/g1-c-009-request-admission-race.md
  experiments/g1/SPEC.g1-c-010.md
  experiments/g1/manifest.g1-c-010.template.json
  experiments/g1/commands/00-g1-c-010-bootstrap.sh
  experiments/g1/commands/20-g1-c-010.sh
  experiments/g1/commands/g1_c_010_arm_launcher.py
  experiments/g1/commands/g1_c_010_bundle_manifest.py
  experiments/g1/commands/g1_c_010_extract_records.py
  experiments/g1/commands/g1_c_010_finalize.py
  experiments/g1/commands/g1_c_010_gpu_sampler.py
  experiments/g1/commands/test_g1_c_010_anchor_offline.sh
  experiments/g1/commands/test_g1_c_010_arm_launcher.py
  experiments/g1/commands/test_g1_c_010_arm_runner_spawn.sh
  experiments/g1/commands/test_g1_c_010_bundle_manifest.py
  experiments/g1/commands/test_g1_c_010_cleanup_failure.sh
  experiments/g1/commands/test_g1_c_010_failure_evidence.sh
  experiments/g1/commands/test_g1_c_010_finalize.py
  experiments/g1/commands/test_g1_c_010_gpu_sampler.py
  experiments/g1/commands/test_g1_c_010_host_mismatch.sh
  experiments/g1/commands/test_g1_c_010_pre_execution.py
  experiments/g1/commands/test_g1_c_010_request_admission.py
  experiments/g1/commands/test_g1_c_010_runtime_wheel_name.sh
  experiments/g1/commands/test_g1_c_010_shared_coverage.py
  experiments/g1/commands/test_g1_c_010_signal_cleanup.sh
  experiments/g1/commands/test_g1_c_010_source_restore.sh
  experiments/g1/commands/test_g1_c_010_storage_preflight.sh
  scripts/verify-g1-c-010-bundle.sh
  scripts/anchor-g1-c-010-oss.sh
  upstream/sglang/patches/0002-g1-scripted-forced-demote-c010.patch
  worklog/plans/2026-08-25/g1-c-010-request-admission-fence.md
  worklog/reviews/2026-08-25/g1-c-010-control-admission-review.md
)
git -C "$ROOT" cat-file -e "$PREDECESSOR^{commit}"
for path in "${FROZEN[@]}"; do
  git -C "$ROOT" cat-file -e "$PREDECESSOR:$path"
done
git -C "$ROOT" diff --quiet "$PREDECESSOR" -- "${FROZEN[@]}"
git -C "$ROOT" apply --check \
  "$ROOT/upstream/sglang/patches/0002-g1-scripted-forced-demote-c011.patch"

"$PYTHON" - "$ROOT" "$SPEC" "$TEMPLATE" "$RUNNER" "$BUILDER" "$ARM_LAUNCHER" "$FINALIZER" "$ANCHOR" <<'PY'
import hashlib
import importlib.util
import json
import pathlib
import re
import sys

root, spec_path, template_path, runner_path, builder_path, launcher_path, finalizer_path, anchor_path = map(pathlib.Path, sys.argv[1:])
spec = spec_path.read_text(encoding="utf-8")
runner = runner_path.read_text(encoding="utf-8")
builder = builder_path.read_text(encoding="utf-8")
launcher = launcher_path.read_text(encoding="utf-8")
finalizer = finalizer_path.read_text(encoding="utf-8")
anchor = anchor_path.read_text(encoding="utf-8")
shared_tests = (root / "experiments/g1/commands/test_g1_c_011_shared_coverage.py").read_text(encoding="utf-8")
request_tests = (root / "experiments/g1/commands/test_g1_c_011_request_admission.py").read_text(encoding="utf-8")
template = json.loads(template_path.read_text(encoding="utf-8"))

assert template["identity"] == {
    "attempt_id": "__GENERATED__", "bundle_id": "G1-C-011",
    "claim_state": "roadmap", "gate": "G1", "gate_decision": "__GENERATED__",
    "kind": "formal_checked_demote_runtime",
    "spec_path": "experiments/g1/SPEC.g1-c-011.md",
    "spec_sha256": "__GENERATED__", "toolgap_commit": "__GENERATED__",
    "toolgap_tree": "__GENERATED__",
}
assert template["outcome"] == {"claim_state": "roadmap", "terminals": ["PASS", "STOP", "INVALID"]}
for fragment in (
    "private Full KV tail", "committed host copy", "G2/G3",
    "public pause/cancel/resume API", "second physical KV data plane",
    "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite",
    "current-tree wheel build", "six special wheels", "fresh SGLang",
    "six rejection cases", "is permitted only", "external anchor",
    "2026-08-25T01:32:28Z", "formal_arms", "_check_not_importing_main",
    "cleanup evidence was clean", "ENOSPC", "25769803776",
    "storage_preflight.minimum_free_bytes", "14922854400",
    "33479200768", "0ad49f1afdf5c59285a2828afbfe36d3409caa68",
    "529866d7fb10c88fbbfd174a320089b5ca0f8ab8",
    "g1-c-007-a1-20260825T042407Z", "2026-08-25 12:30:51 CST",
    "ModuleNotFoundError: No module named 'g1_c_007_scripted'",
    "frozen 2400-second timeout", "premature C-007 terminal state or receipt",
    "g1-c-008-a1-20260825T053604Z", "sealed `pre_execution INVALID`",
    "after three complete arm records", "((21,), (24,))",
    "DEFERRED/DEFERRED", "WRITE_THROUGH_PENDING",
    "REJECTED/STALE_GENERATION", "source-backed rejection-oracle mapping",
    "same nonempty unique sequence", "eligible and completed IDs must be empty",
    "non-boolean supplied and current generations differ", "empty target",
    "fixed `FULL`, `SWA`, and `MAMBA` slots", "exactly three",
    "Enabled binds requested, eligible", "scheduled, completed", "globally",
    "flatten exactly to the aggregate freed indices",
    "Within each before or after snapshot", "recomputed from before observations",
    "demote count, ID count, and cache-drain count agree",
    "does not assert the PASS-side", "before causal `STOP` is considered",
    "exact unchanged prepared device shape", "demoted host-only shape",
    "tombstones, host loss, and", "`checked_backend` to equal",
    "stock-victim record whose `after`", "frees cannot be reassigned across nodes",
    "all-unchanged", "capacity is unchanged",
    "reason must also be replayable", "all locks are zero", "from `1` to `0`",
    "Allocator device indices are", "Malformed or contradictory IDs are `INVALID`",
    "causal missing-reclaim `STOP` case",
    "pre-execution-failure.json", "real filename stem", "inherits this `sys.path`",
    "28a094182905fb4b8a8bc52182fb0314490baf08",
    "g1-c-009-a1-20260825T082527Z", "400 scheduler steps",
    "eventual HTTP 200", "_http_post_and_await_recv_msg", "exact request `rid`",
    "close-session control admission fences", "CloseSessionReqInput",
    "exact `session_id`", "No bare", "`_submit_post` remains",
    "g1-c-010-a1-20260825T095119Z", "seven-arm", "final independent matrix review",
    "LOAD_BACK_PENDING", "settled Host-copy guards", "all nine exactly once",
    "host_value_present == false", "available_before_reservation == logical_size",
    "available_after_release == logical_size", "no scheduler yield",
):
    assert fragment in spec, fragment

module_spec = importlib.util.spec_from_file_location("g1_c_011_finalize", finalizer_path)
assert module_spec and module_spec.loader
module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)
selected_test_path = pathlib.PurePosixPath(
    "test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py"
)
assert module.SCRIPTED_TEST_PATH == str(selected_test_path)
assert module.SELECTOR_MODULE == selected_test_path.stem
assert f'SCRIPTED_TEST="$TREATMENT/{selected_test_path}"' in runner
assert '"selector_module": scripted_test.stem' in runner
assert tuple(module.ARMS) == (
    "enabled", "bypass", "reject_write_through_pending",
    "reject_non_target_session_coverage", "reject_device_locked",
    "reject_stale_generation", "stock_eviction_liveness",
    "reject_load_back_pending", "reject_host_copy_not_committed",
)
assert set(module.SELECTORS) == set(module.ARMS)
for arm, selector in module.SELECTORS.items():
    assert selector in runner
assert "fresh_process_per_arm" in runner
assert 'exec "$PYTHON" "$ARM_LAUNCHER"' in runner
assert "wait_for_arm_handshake" in runner and "launcher-handshake.json" in runner
assert "os.setsid()" in launcher and "os.O_EXCL" in launcher and "wait_for_ack" in launcher
assert "G1_C_011_INPUT_OSS_RECEIPT" in runner
assert "--find-links" in runner and "mirrors.cloud.aliyuncs.com" in runner
assert "pip install --upgrade pip" not in runner
assert "g1_c_011_gpu_sampler.py" in runner
assert "--poll-seconds 0.25" in runner
assert "gpu-samples.json" in runner and "gpu-during.txt" in runner and "gpu-attributable.txt" in runner
assert "cleanup_active_processes" in runner and "CURRENT_ARM_PGID" in runner
assert "cleanup could not prove process-group exit; attempt remains unsealed" in runner
assert 'wait_for_runtime_group_exit "$pgid" || return 1' in runner
assert "os.getpgid(pid)" in runner and "launcher-ack.json" in runner
assert "trap 'seal_invalid \"$?\"' EXIT" in runner
assert "PATCHES=(" in runner
assert "apply_frozen_patches" in runner
assert "000{1-3}" not in runner
assert "storage_preflight" in runner
assert "24 * 1024 * 1024 * 1024" in runner
assert "storage-preflight-source-restore.json" in runner
assert "storage-preflight-resolver.json" in runner
assert "available disk is below manifest bound before source restore" in runner
assert "available disk is below manifest bound before dependency install" in runner
assert runner.index('storage-preflight-source-restore.json') < runner.index('tar --no-same-owner')
assert runner.index('storage-preflight-resolver.json') < runner.index('"$PYTHON" -m venv')
assert runner.index('record_failure_evidence "$code"') < runner.index('"$PYTHON" "$FINALIZER" invalid')
assert '"work_root": str(work_root)' in runner
assert runner.index("capture_environment") < runner.index("requires Linux x86_64")
assert runner.rindex('PHASE="seal"') > runner.index('sha256sum manifest.json')
assert runner.rindex('PHASE="render"') > runner.index('scope=clean')
assert runner.rindex('PHASE="render"') < runner.index('sha256sum manifest.json')
assert "def main() -> int:" in runner
assert 'if __name__ == "__main__":' in runner
assert "raise SystemExit(main())" in runner
assert "sys.path.insert(0, str(path.parent))" in runner
assert "importlib.import_module(path.stem)" in runner
assert 'getattr(module, "__file__", None)' in runner
assert 'pathlib.Path(module_file).resolve() != path' in runner
assert "g1_c_011_scripted" not in runner
assert "importlib.util, pathlib, sys, unittest" not in runner
assert "runtime_wheel_filename" in runner
assert "EXPECTED_RUNTIME_WHEEL_FILENAME" in runner
assert '"$RUNTIME_WHEEL_FILENAME" == "$EXPECTED_RUNTIME_WHEEL_FILENAME"' in runner
assert '"$RUN_DIR/$RUNTIME_WHEEL_FILENAME"' in runner
assert '"runtime-wheel.whl"' not in runner
assert "changed_regular_paths" in runner
assert '"diff", "--name-only"' in runner
assert '"ls-files", "--others", "--exclude-standard"' in runner
assert "candidate.is_symlink()" in runner
assert "candidate.is_file()" in runner
assert "resolved.relative_to(root)" in runner
assert "CHANGED_OUTPUT" in runner
assert "test_toolgap_g1_forced_demote.py" in runner
for patch_name in (
    "0001-atomic-checked-demote.patch",
    "0002-g1-scripted-forced-demote-c011.patch",
    "0003-cuda12-compat-packaging.patch",
):
    assert patch_name in runner
assert "scope scan requires every formal arm log" in runner
assert "unapproved_index" in runner and "source_build" in runner
for forbidden in (
    "cargo ", "rustc ", "maturin ", "pip install \"$TREATMENT/python\"",
    "download.pytorch.org", "docs.sglang.ai", "github.com/sgl-project",
):
    assert forbidden not in runner, forbidden
assert "G1_C_011_EXTERNAL_OSS_ANCHOR" in anchor
assert "ossutil ls --all-versions" in anchor
assert "python3 \"$FINALIZER\" verify" in anchor
assert "CONTEXT_ATTEMPT_ID" in anchor and "CONTEXT_SHA256" in anchor
assert 'not in ("PASS", "STOP", "INVALID")' in anchor
assert 'r"[A-Za-z0-9][A-Za-z0-9._+/-]*"' in anchor
assert 'not in {"PASS", "STOP", "INVALID"}' not in anchor

# Builder independently binds patch bytes, immutable runtime provenance, the
# six-wheel index, and every static formal script.
for required in (
    "RUNTIME_PROVENANCE", "validate_runtime_provenance", "validate_wheelhouse",
    "safe_seed", "STATIC_PATHS", "tracked ToolGap files must be clean",
):
    assert required in builder, required
for label in ("patch_one", "patch_two", "patch_three"):
    assert label in builder and label in finalizer
for relative in (
    "experiments/g1/SPEC.g1-c-011.md",
    "experiments/g1/commands/20-g1-c-011.sh",
    "experiments/g1/commands/g1_c_011_arm_launcher.py",
    "experiments/g1/commands/g1_c_011_finalize.py",
    "experiments/g1/commands/g1_c_011_gpu_sampler.py",
    "experiments/g1/commands/test_g1_c_011_runtime_wheel_name.sh",
    "experiments/g1/commands/test_g1_c_011_arm_launcher.py",
    "experiments/g1/commands/test_g1_c_011_arm_runner_spawn.sh",
    "experiments/g1/commands/test_g1_c_011_anchor_offline.sh",
    "experiments/g1/commands/test_g1_c_011_request_admission.py",
    "experiments/g1/commands/test_g1_c_011_shared_coverage.py",
    "experiments/g1/commands/test_g1_c_011_rejection_guards.py",
    "experiments/g1/commands/test_g1_c_011_storage_preflight.sh",
    "experiments/g1/commands/test_g1_c_011_bundle_manifest.py",
    "experiments/g1/commands/test_g1_c_011_pre_execution.py",
    "experiments/g1/commands/test_g1_c_011_failure_evidence.sh",
    "experiments/g1/commands/test_g1_c_011_cleanup_failure.sh",
    "experiments/g1/commands/test_g1_c_011_host_mismatch.sh",
    "scripts/anchor-g1-c-011-oss.sh",
):
    assert relative in builder
for patch in (
    root / "upstream/sglang/patches/0001-atomic-checked-demote.patch",
    root / "upstream/sglang/patches/0002-g1-scripted-forced-demote-c011.patch",
    root / "upstream/sglang/patches/0003-cuda12-compat-packaging.patch",
):
    assert re.fullmatch(r"[0-9a-f]{64}", hashlib.sha256(patch.read_bytes()).hexdigest())

patch_one = (root / "upstream/sglang/patches/0001-atomic-checked-demote.patch").read_text(encoding="utf-8")
patch_two = (root / "upstream/sglang/patches/0002-g1-scripted-forced-demote-c011.patch").read_text(encoding="utf-8")
assert 'reason="STALE_GENERATION"' in patch_one
assert 'reason=disposition' in patch_one
session_request = patch_two.split("+def _session_request(", 1)[1].split(
    "+def _session_frontier", 1
)[0]
assert "_http_post_and_await_recv_msg" in session_request
assert 'predicate=lambda obj: getattr(obj, "rid", None) == rid' in session_request
assert 'description=f"request with rid {rid!r}"' in session_request
assert "_submit_post" not in session_request
assert "_MAX_STEPS = 400" in patch_two
stale_script = patch_two.split("+    def _script_stale_generation", 1)[1].split(
    "+class TestG1StockEvictionLiveness", 1
)[0]
assert "CloseSessionReqInput" in stale_script
assert "_http_post_and_await_recv_msg" in stale_script
assert 'path="/close_session"' in stale_script
assert "isinstance(obj, CloseSessionReqInput)" in stale_script
assert "obj.session_id == session_id" in stale_script
assert 'description=f"close session {session_id!r}"' in stale_script
assert "_submit_post" not in patch_two
for regression in (
    "test_delayed_admission_blocks_helper_before_scheduler_budget_starts",
    "test_wrong_rid_does_not_satisfy_admission_fence",
    "test_request_arrival_timeout_propagates_before_handle_or_budget",
    "test_delayed_close_admission_precedes_side_effect_budget",
    "test_close_predicate_rejects_wrong_type_and_session",
    "test_close_arrival_timeout_propagates_before_side_effect_budget",
    "test_completion_steps_begin_after_arrival_and_reach_frontier",
    "test_source_forbids_fire_and_forget_submission_anywhere",
):
    assert regression in request_tests
assert "equal_but_distinct" in request_tests
assert "actual is not value" in request_tests
assert "def _register_non_target_session_coverage(" in patch_two
assert "ensure_session_generation(session_id)" in patch_two
assert "component.register_session_leaf(session_id, node)" in patch_two
assert "assert target_nodes == other_nodes" not in patch_two
assert 'assert outcome.reason == "DEFERRED"' in patch_two
for reason in (
    "WRITE_THROUGH_PENDING", "NON_TARGET_SESSION_COVERAGE", "DEVICE_LOCKED",
    "LOAD_BACK_PENDING", "HOST_COPY_NOT_COMMITTED",
):
    assert f'_assert_deferred_node_reason(outcome, "{reason}")' in patch_two

enabled_script = patch_two.split("+    def _script_enabled", 1)[1].split(
    "+class TestG1BypassArm", 1
)[0]
bypass_script = patch_two.split("+    def _script_bypass", 1)[1].split(
    "+class TestG1WriteThroughPending", 1
)[0]
for arm_script in (enabled_script, bypass_script):
    assert "record = _new_record(" in arm_script
    assert "print(json.dumps(record, sort_keys=True))" in arm_script
for forbidden in (
    "assert _freed_ids(outcome)", "assert counters.cache_owned_drain",
    'assert after["available_size"]', "expected_freed_ids",
):
    assert forbidden not in enabled_script
for forbidden in (
    "assert counters.physical_demote == 0", "assert counters.cache_owned_drain == 0",
    'assert after["available_size"] == before["available_size"]',
    'assert [observation["device_ids"] for observation in target_after]',
):
    assert forbidden not in bypass_script
assert 'and observation["host_committed"]' in patch_two
assert 'and observation["device_leaf"]' in patch_two
assert 'and not any(observation["lock_refs"])' in patch_two
assert 'and observation["session_ref"] == 1' in patch_two

# The terminal classifier validates formal arm context before evaluating only
# the two causal STOP predicates; malformed/rejection/liveness faults are INVALID.
assert "return \"STOP\", causal_stop" in finalizer
assert "return \"INVALID\", structural" in finalizer
assert finalizer.index("if failures:") < finalizer.index("causal_stop =")
assert "enabled_context_errors" in finalizer and "bypass_context_errors" in finalizer
assert "validate_full_evidence" in finalizer and "sglang-package-provenance.json" in finalizer
assert "RUNTIME_WHEEL_FILENAME" in finalizer and "runtime_wheel_filename" in finalizer
assert "MINIMUM_FREE_BYTES" in builder and "storage_preflight" in builder
assert "validate_storage_preflight" in finalizer and "storage-preflight-resolver.json" in finalizer
assert "validate_pre_execution_evidence" in finalizer and "pre_execution_failure_reason" in finalizer
assert "PHASE_REQUIRED_MILESTONES" in finalizer and '"work_root"' in finalizer
assert '"render"' in finalizer and "launcher handshake differs" in finalizer
assert "artifact index does not equal the sealed regular-file set" in finalizer
assert "rejection contract" in finalizer and "stock eviction liveness" in finalizer
assert "rejection_nodes_pass" in finalizer
assert "rejection_observations_pass" in finalizer
assert "stale_rejection_context_pass" in finalizer
assert 'set(operation) != {"session_id", "supplied_generation"}' in finalizer
assert 'target["scheduled_node_ids"] != requested' in finalizer
assert 'target["eligible_node_ids"] != []' in finalizer
assert 'target["completed_node_ids"] != []' in finalizer
assert 'record["released_component_leaves"] > 0' in finalizer
assert 'not isinstance(record["priority_release"], str)' in finalizer
assert 'operation["supplied_generation"] != operation["current_generation"]' in finalizer
assert 'before[node_id]["write_through_pending"] is False' in finalizer
assert 'before[node_id]["load_back_pending"] is False' in finalizer
assert 'all(value == 0 for value in before[node_id]["lock_refs"])' in finalizer
assert 'before[node_id]["session_ref"] == 1' in finalizer
assert 'after[node_id]["session_ref"] == 0' in finalizer
assert '{"disposition": "DEFERRED", "reason": "DEFERRED"}' in finalizer
assert '{"disposition": "REJECTED", "reason": reason}' in finalizer
assert "release_session_priority" in shared_tests
assert "session_ids" in shared_tests and "ancestor" in shared_tests
assert 'self.assertEqual(target.component_data["FULL"].session_ref, 1)' in shared_tests
assert 'self.assertEqual(ancestor.component_data["FULL"].session_ref, 1)' in shared_tests
assert 'self.assertEqual(component._session_leaves[second_session], {target})' in shared_tests
assert "arm record aggregate differs from individual evidence" in finalizer
assert "observation_errors" in finalizer and "LIVE_OBSERVATION_FIELDS" in finalizer
assert 'len(lock_refs) != 3' in finalizer
assert 'observation["session_ref"] < 0' in finalizer
assert 'observation["node_id"] < 0' in finalizer
assert 'len(device_ids) != len(set(device_ids))' in finalizer
assert 'len(phase_device_ids) != len(set(phase_device_ids))' in finalizer
assert 'observation_is_eligible(observation)' in finalizer
assert 'def observation_is_prepared(' in finalizer
assert 'observation_is_prepared(item)' in finalizer
assert 'positive_after_shape(before[index], item)' in finalizer
assert 'len(target[key]) != len(set(target[key]))' in finalizer
assert 'target["eligible_node_ids"] != requested' in finalizer
assert 'target["completed_node_ids"] != requested' in finalizer
assert 'counters["physical_demote_node_ids"] != requested' in finalizer
assert 'counters["physical_demote"] != len(requested)' in finalizer
assert 'counters["cache_owned_drain"] != len(requested)' in finalizer
assert 'counters["physical_demote"] != len(physical_ids)' in finalizer
assert 'counters["cache_owned_drain"] != counters["physical_demote"]' in finalizer
assert 'physical_ids != demoted_ids' in finalizer
assert 'counters["checked_backend"] != len(requested)' in finalizer
assert '== (0 if stale else len(record["target"]["requested_node_ids"]))' in finalizer
assert 'node["disposition"] != "COMPLETED" or node["reason"] != "DEMOTED"' in finalizer
assert 'len(original_device_ids) != len(set(original_device_ids))' in finalizer
assert 'node_freed_device_ids != record["freed_device_ids"]' in finalizer
assert 'expected_node_frees' in finalizer and 'expected_freed_device_ids' in finalizer
assert 'all(shape == "unchanged" for shape in after_shapes)' in finalizer
assert 'def liveness_target_after_passes(' in finalizer
assert 'victim_after.get(after["node_id"]) != after' in finalizer
assert 'any(type(node_id) is not int or node_id < 0 for node_id in candidates)' in finalizer
assert '[data.lock_ref for data in node.component_data]' in patch_two
assert '[1, 0, 0]' in (root / "experiments/g1/commands/test_g1_c_011_finalize.py").read_text(encoding="utf-8")
tests = (root / "experiments/g1/commands/test_g1_c_011_finalize.py").read_text(encoding="utf-8")
assert "test_patch_records_causal_outcomes_before_final_classification" in tests
assert "test_noncausal_failure_precedes_enabled_causal_stop" in tests
assert "test_target_phase_device_ids_are_globally_unique" in tests
assert "test_enabled_after_requires_a_coherent_live_source_shape" in tests
assert "test_bypass_after_requires_unchanged_or_instrumented_demoted_shape" in tests
assert "test_liveness_before_requires_a_prepared_device_tail" in tests
assert "test_enabled_tombstone_preparation_is_invalid_without_exception" in tests
assert "test_checked_backend_count_matches_requested_nodes" in tests
assert "test_enabled_after_shape_binds_frees_and_capacity" in tests
assert "test_enabled_frees_cannot_be_attributed_to_another_node" in tests
assert "test_liveness_after_requires_preserved_state_or_matching_victim" in tests
assert "test_liveness_target_eviction_is_replayed_from_matching_victim" in tests
assert "test_priority_release_unhashable_json_is_invalid_without_exception" in tests
assert "validate_gpu_samples" in finalizer and "GPU sampler union differs" in finalizer
assert "stock_eviction_errors" in finalizer and "no_allocator_reclaim" in finalizer
print("G1-C-011 static contract checks passed")
PY
