#!/usr/bin/env bash
# Direct development/replay checks for the frozen G1-C020 runtime contract.
set -euo pipefail

[[ "$#" == 0 ]] || {
  printf 'g1-c-020 verifier: arguments are forbidden\n' >&2
  exit 2
}

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/.." && pwd -P)"
PYTHON="/usr/bin/python3"
FROZEN_COMMIT="e43ad7aabb7a8c0e4a17855a4745d91ba5945d96"
RUNNER="$ROOT/experiments/g1/commands/20-g1-c-020.sh"
FINALIZER="$ROOT/experiments/g1/commands/g1_c_020_finalize.py"
BUILDER="$ROOT/experiments/g1/commands/g1_c_020_bundle_manifest.py"
LAUNCHER="$ROOT/experiments/g1/commands/g1_c_020_arm_launcher.py"
SAMPLER="$ROOT/experiments/g1/commands/g1_c_020_gpu_sampler.py"
export PYTHONPYCACHEPREFIX="/tmp/toolgap-g1-c020-pycache-$$"

git -C "$ROOT" cat-file -e "$FROZEN_COMMIT^{commit}"
git -C "$ROOT" diff --quiet "$FROZEN_COMMIT" -- \
  experiments/g1/SPEC.g1-c-020.md \
  experiments/g1/commands/20-g1-c-020.sh \
  upstream/sglang/patches/0001-atomic-checked-demote.patch \
  upstream/sglang/patches/0002-g1-scripted-forced-demote-c020.patch

bash -n "$RUNNER"
bash -n "$ROOT/scripts/anchor-g1-c-020-oss.sh"
"$PYTHON" -m py_compile "$BUILDER" "$FINALIZER" "$LAUNCHER" "$SAMPLER" \
  "$ROOT/experiments/g1/commands/test_g1_c_020_bundle_manifest.py" \
  "$ROOT/experiments/g1/commands/test_g1_c_020_finalize.py" \
  "$ROOT/experiments/g1/commands/test_g1_c_020_arm_launcher.py" \
  "$ROOT/experiments/g1/commands/test_g1_c_020_gpu_sampler.py" \
  "$ROOT/experiments/g1/commands/test_g1_c_020_ninja_binding.py" \
  "$ROOT/experiments/g1/commands/test_g1_c_020_request_admission.py" \
  "$ROOT/experiments/g1/commands/test_g1_c_020_shared_coverage.py"

"$PYTHON" "$ROOT/experiments/g1/commands/test_g1_c_020_bundle_manifest.py"
"$PYTHON" "$ROOT/experiments/g1/commands/test_g1_c_020_finalize.py"
"$PYTHON" "$ROOT/experiments/g1/commands/test_g1_c_020_arm_launcher.py"
"$PYTHON" "$ROOT/experiments/g1/commands/test_g1_c_020_gpu_sampler.py"
"$PYTHON" "$ROOT/experiments/g1/commands/test_g1_c_020_ninja_binding.py"
"$PYTHON" "$ROOT/experiments/g1/commands/test_g1_c_020_request_admission.py"
"$PYTHON" "$ROOT/experiments/g1/commands/test_g1_c_020_shared_coverage.py"
bash "$ROOT/experiments/g1/commands/test_g1_c_020_source_restore.sh"
bash "$ROOT/experiments/g1/commands/test_g1_c_020_runtime_wheel_name.sh"
bash "$ROOT/experiments/g1/commands/test_g1_c_020_arm_runner_spawn.sh"
bash "$ROOT/experiments/g1/commands/test_g1_c_020_anchor_offline.sh"
bash "$ROOT/experiments/g1/commands/test_g1_c_020_storage_preflight.sh"
bash "$ROOT/experiments/g1/commands/test_g1_c_020_failure_evidence.sh"
bash "$ROOT/experiments/g1/commands/test_g1_c_020_signal_cleanup.sh"
bash "$ROOT/experiments/g1/commands/test_g1_c_020_cleanup_failure.sh"
bash "$ROOT/experiments/g1/commands/test_g1_c_020_host_mismatch.sh"

printf 'G1-C-020 direct development/replay checks passed\n'
