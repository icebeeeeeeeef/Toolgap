#!/usr/bin/env bash
# Verify the successful protocol evidence and create its three-part seal.
set -Eeuo pipefail

SCRIPT_REPO_ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd)"
G0_RUN_DIR="${G0_RUN_DIR:-}"
if [[ -z "$G0_RUN_DIR" ]]; then
  echo "set G0_RUN_DIR to the directory emitted by command 20" >&2
  exit 64
fi
G0_RUN_DIR="$(cd "$G0_RUN_DIR" && pwd)"
readonly ADMITTED_RUN_DIR="$G0_RUN_DIR"
readonly FINALIZE="$SCRIPT_REPO_ROOT/experiments/g0/commands/g0_c_013_finalize.py"
readonly VERIFY_IDENTITY="$SCRIPT_REPO_ROOT/experiments/g0/commands/g0_c_008_verify_identity.py"
readonly VERIFY_EVIDENCE="$SCRIPT_REPO_ROOT/experiments/g0/commands/g0_c_008_verify_evidence.py"
readonly MODEL_HELPER="$SCRIPT_REPO_ROOT/experiments/g0/commands/g0_c_013_model_seed.py"

write_verify_failure() {
  local status="$1"
  local line="$2"
  trap - ERR HUP INT TERM
  python3 "$FINALIZE" failure --run-dir "$G0_RUN_DIR" \
    --attempt-status INVALID_SCOPE --phase final-verification \
    --exit-code "$status" --line "$line" || true
  exit "$status"
}
trap 'write_verify_failure "$?" "$LINENO"' ERR
trap 'write_verify_failure 129 "$LINENO"' HUP
trap 'write_verify_failure 130 "$LINENO"' INT
trap 'write_verify_failure 143 "$LINENO"' TERM

test ! -e "$G0_RUN_DIR/execution-status.json"
test ! -e "$G0_RUN_DIR/artifact-index.json"
test ! -e "$G0_RUN_DIR/completion-receipt.json"
python3 "$VERIFY_IDENTITY" --run-dir "$G0_RUN_DIR" \
  --repo-root "$SCRIPT_REPO_ROOT" \
  --require-receipt serving-passed.json --receipt-status SERVING_PASSED
source "$G0_RUN_DIR/runtime.env"
test "$REPO_ROOT" = "$SCRIPT_REPO_ROOT"
test "$G0_RUN_DIR" = "$ADMITTED_RUN_DIR"
"$G0_PYTHON" "$MODEL_HELPER" verify \
  --model-root "$MODEL_SNAPSHOT" --inventory "$MODEL_INVENTORY" \
  --receipt "$MODEL_RECEIPT"
"$G0_PYTHON" "$VERIFY_EVIDENCE" --run-dir "$G0_RUN_DIR"
"$G0_PYTHON" "$MODEL_HELPER" verify \
  --model-root "$MODEL_SNAPSHOT" --inventory "$MODEL_INVENTORY" \
  --receipt "$MODEL_RECEIPT"
python3 "$VERIFY_IDENTITY" --run-dir "$G0_RUN_DIR" \
  --repo-root "$SCRIPT_REPO_ROOT" \
  --require-receipt serving-passed.json --receipt-status SERVING_PASSED

trap - ERR HUP INT TERM
"$G0_PYTHON" "$FINALIZE" success \
  --run-dir "$G0_RUN_DIR" --phase final-verification
"$G0_PYTHON" "$FINALIZE" verify --run-dir "$G0_RUN_DIR"
echo "COMPLETED_PROTOCOL_AWAITING_INDEPENDENT_REVIEW: $G0_RUN_DIR"
