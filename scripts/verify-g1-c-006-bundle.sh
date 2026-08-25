#!/usr/bin/env bash
# Static contract checks for the independent formal G1-C-006 source bundle.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/.." && pwd -P)"
PYTHON="${PYTHON:-python3}"
SPEC="$ROOT/experiments/g1/SPEC.g1-c-006.md"
TEMPLATE="$ROOT/experiments/g1/manifest.g1-c-006.template.json"
BOOTSTRAP="$ROOT/experiments/g1/commands/00-g1-c-006-bootstrap.sh"
RUNNER="$ROOT/experiments/g1/commands/20-g1-c-006.sh"
BUILDER="$ROOT/experiments/g1/commands/g1_c_006_bundle_manifest.py"
EXTRACTOR="$ROOT/experiments/g1/commands/g1_c_006_extract_records.py"
FINALIZER="$ROOT/experiments/g1/commands/g1_c_006_finalize.py"
TESTS="$ROOT/experiments/g1/commands/test_g1_c_006_finalize.py"
GPU_SAMPLER="$ROOT/experiments/g1/commands/g1_c_006_gpu_sampler.py"
GPU_SAMPLER_TESTS="$ROOT/experiments/g1/commands/test_g1_c_006_gpu_sampler.py"
SIGNAL_CLEANUP_TESTS="$ROOT/experiments/g1/commands/test_g1_c_006_signal_cleanup.sh"
SOURCE_RESTORE_TESTS="$ROOT/experiments/g1/commands/test_g1_c_006_source_restore.sh"
RUNTIME_WHEEL_NAME_TESTS="$ROOT/experiments/g1/commands/test_g1_c_006_runtime_wheel_name.sh"
ARM_RUNNER_SPAWN_TESTS="$ROOT/experiments/g1/commands/test_g1_c_006_arm_runner_spawn.sh"
STORAGE_PREFLIGHT_TESTS="$ROOT/experiments/g1/commands/test_g1_c_006_storage_preflight.sh"
ANCHOR="$ROOT/scripts/anchor-g1-c-006-oss.sh"

for path in "$SPEC" "$TEMPLATE" "$BOOTSTRAP" "$RUNNER" "$BUILDER" "$EXTRACTOR" "$FINALIZER" "$TESTS" "$GPU_SAMPLER" "$GPU_SAMPLER_TESTS" "$SIGNAL_CLEANUP_TESTS" "$SOURCE_RESTORE_TESTS" "$RUNTIME_WHEEL_NAME_TESTS" "$ARM_RUNNER_SPAWN_TESTS" "$STORAGE_PREFLIGHT_TESTS" "$ANCHOR"; do
  test -f "$path"
done
bash -n "$BOOTSTRAP"
bash -n "$RUNNER"
bash -n "$ANCHOR"
"$PYTHON" -m py_compile "$BUILDER" "$EXTRACTOR" "$FINALIZER" "$TESTS" "$GPU_SAMPLER" "$GPU_SAMPLER_TESTS"
"$PYTHON" "$TESTS"
"$PYTHON" "$GPU_SAMPLER_TESTS"
bash "$SIGNAL_CLEANUP_TESTS"
bash "$SOURCE_RESTORE_TESTS"
bash "$RUNTIME_WHEEL_NAME_TESTS"
bash "$ARM_RUNNER_SPAWN_TESTS"
bash "$STORAGE_PREFLIGHT_TESTS"
git -C "$ROOT" diff --check

# G1-C-006 must not change predecessor evidence. This is intentionally a
# working-tree check, not a claim about unrelated concurrent additions.
FROZEN=(
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
)
git -C "$ROOT" diff --quiet -- "${FROZEN[@]}"

"$PYTHON" - "$ROOT" "$SPEC" "$TEMPLATE" "$RUNNER" "$BUILDER" "$FINALIZER" "$ANCHOR" <<'PY'
import hashlib
import importlib.util
import json
import pathlib
import re
import sys

root, spec_path, template_path, runner_path, builder_path, finalizer_path, anchor_path = map(pathlib.Path, sys.argv[1:])
spec = spec_path.read_text(encoding="utf-8")
runner = runner_path.read_text(encoding="utf-8")
builder = builder_path.read_text(encoding="utf-8")
finalizer = finalizer_path.read_text(encoding="utf-8")
anchor = anchor_path.read_text(encoding="utf-8")
template = json.loads(template_path.read_text(encoding="utf-8"))

assert template["identity"] == {
    "attempt_id": "__GENERATED__", "bundle_id": "G1-C-006",
    "claim_state": "roadmap", "gate": "G1", "gate_decision": "__GENERATED__",
    "kind": "formal_checked_demote_runtime",
    "spec_path": "experiments/g1/SPEC.g1-c-006.md",
    "spec_sha256": "__GENERATED__", "toolgap_commit": "__GENERATED__",
    "toolgap_tree": "__GENERATED__",
}
assert template["outcome"] == {"claim_state": "roadmap", "terminals": ["PASS", "STOP", "INVALID"]}
for fragment in (
    "private Full KV tail", "committed host copy", "G2/G3",
    "public pause/cancel/resume API", "second physical KV data plane",
    "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite",
    "current-tree wheel build", "six special wheels", "fresh SGLang",
    "four rejection cases", "is permitted only", "external anchor",
    "2026-08-25T01:32:28Z", "formal_arms", "_check_not_importing_main",
    "cleanup evidence was clean", "ENOSPC", "68719476736",
    "storage_preflight.minimum_free_bytes",
):
    assert fragment in spec, fragment
assert "in-flight frozen attempt" not in spec
assert "parent remains under the frozen 2400-second timeout" not in spec

module_spec = importlib.util.spec_from_file_location("g1_c_006_finalize", finalizer_path)
assert module_spec and module_spec.loader
module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)
assert tuple(module.ARMS) == (
    "enabled", "bypass", "reject_write_through_pending",
    "reject_non_target_session_coverage", "reject_device_locked",
    "reject_stale_generation", "stock_eviction_liveness",
)
assert set(module.SELECTORS) == set(module.ARMS)
for arm, selector in module.SELECTORS.items():
    assert f'[{arm}]="{selector}"' in runner
assert "fresh_process_per_arm" in runner
assert "exec setsid timeout" in runner
assert "G1_C_006_INPUT_OSS_RECEIPT" in runner
assert "--find-links" in runner and "mirrors.cloud.aliyuncs.com" in runner
assert "pip install --upgrade pip" not in runner
assert "g1_c_006_gpu_sampler.py" in runner
assert "--poll-seconds 0.25" in runner
assert "gpu-samples.json" in runner and "gpu-during.txt" in runner and "gpu-attributable.txt" in runner
assert "cleanup_active_processes" in runner and "CURRENT_ARM_PGID" in runner
assert "trap 'seal_invalid \"$?\"' EXIT" in runner
assert "PATCHES=(" in runner
assert "apply_frozen_patches" in runner
assert "000{1-3}" not in runner
assert "storage_preflight" in runner
assert "64 * 1024 * 1024 * 1024" in runner
assert "storage-preflight-source-restore.json" in runner
assert "storage-preflight-resolver.json" in runner
assert "available disk is below manifest bound before source restore" in runner
assert "available disk is below manifest bound before dependency install" in runner
assert runner.index('storage-preflight-source-restore.json') < runner.index('tar --no-same-owner')
assert runner.index('storage-preflight-resolver.json') < runner.index('"$PYTHON" -m venv')
assert "def main() -> int:" in runner
assert 'if __name__ == "__main__":' in runner
assert "raise SystemExit(main())" in runner
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
    "0002-g1-scripted-forced-demote.patch",
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
assert "G1_C_006_EXTERNAL_OSS_ANCHOR" in anchor
assert "ossutil ls --all-versions" in anchor
assert "python3 \"$FINALIZER\" verify" in anchor
assert "CONTEXT_ATTEMPT_ID" in anchor and "CONTEXT_SHA256" in anchor

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
    "experiments/g1/SPEC.g1-c-006.md",
    "experiments/g1/commands/20-g1-c-006.sh",
    "experiments/g1/commands/g1_c_006_finalize.py",
    "experiments/g1/commands/g1_c_006_gpu_sampler.py",
    "experiments/g1/commands/test_g1_c_006_runtime_wheel_name.sh",
    "experiments/g1/commands/test_g1_c_006_arm_runner_spawn.sh",
    "experiments/g1/commands/test_g1_c_006_storage_preflight.sh",
    "scripts/anchor-g1-c-006-oss.sh",
):
    assert relative in builder
for patch in (
    root / "upstream/sglang/patches/0001-atomic-checked-demote.patch",
    root / "upstream/sglang/patches/0002-g1-scripted-forced-demote.patch",
    root / "upstream/sglang/patches/0003-cuda12-compat-packaging.patch",
):
    assert re.fullmatch(r"[0-9a-f]{64}", hashlib.sha256(patch.read_bytes()).hexdigest())

# The terminal classifier validates formal arm context before evaluating only
# the two causal STOP predicates; malformed/rejection/liveness faults are INVALID.
assert "return \"STOP\", causal_stop" in finalizer
assert "return \"INVALID\", structural" in finalizer
assert "enabled_context_errors" in finalizer and "bypass_context_errors" in finalizer
assert "validate_full_evidence" in finalizer and "sglang-package-provenance.json" in finalizer
assert "RUNTIME_WHEEL_FILENAME" in finalizer and "runtime_wheel_filename" in finalizer
assert "MINIMUM_FREE_BYTES" in builder and "storage_preflight" in builder
assert "validate_storage_preflight" in finalizer and "storage-preflight-resolver.json" in finalizer
assert "rejection contract" in finalizer and "stock eviction liveness" in finalizer
assert "arm record aggregate differs from individual evidence" in finalizer
assert "observation_errors" in finalizer and "LIVE_OBSERVATION_FIELDS" in finalizer
assert "validate_gpu_samples" in finalizer and "GPU sampler union differs" in finalizer
assert "stock_eviction_errors" in finalizer and "no_allocator_reclaim" in finalizer
print("G1-C-006 static contract checks passed")
PY
