#!/usr/bin/env bash
# Run source and installed-package controls; this command never starts a server.
set -Eeuo pipefail

SCRIPT_REPO_ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd)"
G0_RUN_DIR="${G0_RUN_DIR:-}"
if [[ -z "$G0_RUN_DIR" ]]; then
  echo "set G0_RUN_DIR to the directory emitted by command 20" >&2
  exit 64
fi
G0_RUN_DIR="$(cd "$G0_RUN_DIR" && pwd)"
readonly ADMITTED_RUN_DIR="$G0_RUN_DIR"
readonly FINALIZE="$SCRIPT_REPO_ROOT/experiments/g0/commands/g0_c_011_finalize.py"
readonly VERIFY_IDENTITY="$SCRIPT_REPO_ROOT/experiments/g0/commands/g0_c_008_verify_identity.py"
installed_work=""

write_invalid_scope() {
  local status="$1"
  local line="$2"
  trap - ERR HUP INT TERM
  if [[ -n "$installed_work" && -d "$installed_work" ]]; then
    rm -rf "$installed_work"
  fi
  python3 "$FINALIZE" failure --run-dir "$G0_RUN_DIR" \
    --attempt-status INVALID_SCOPE --phase contract-controls \
    --exit-code "$status" --line "$line" || true
  exit "$status"
}
trap 'write_invalid_scope "$?" "$LINENO"' ERR
trap 'write_invalid_scope 129 "$LINENO"' HUP
trap 'write_invalid_scope 130 "$LINENO"' INT
trap 'write_invalid_scope 143 "$LINENO"' TERM

test ! -e "$G0_RUN_DIR/execution-status.json"
test ! -e "$G0_RUN_DIR/artifact-index.json"
test ! -e "$G0_RUN_DIR/completion-receipt.json"
test ! -e "$G0_RUN_DIR/controls-passed.json"
python3 "$VERIFY_IDENTITY" --run-dir "$G0_RUN_DIR" \
  --repo-root "$SCRIPT_REPO_ROOT" \
  --require-receipt preflight-status.json --receipt-status ADMITTED_PRE_ARM
source "$G0_RUN_DIR/runtime.env"
test "$REPO_ROOT" = "$SCRIPT_REPO_ROOT"
test "$G0_RUN_DIR" = "$ADMITTED_RUN_DIR"

readonly SOURCE_ORACLE="$REPO_ROOT/experiments/g0/artifacts/test_atomic_checked_demote_contract_v6.py"
readonly INSTALLED_TEST="$REPO_ROOT/upstream/sglang/tests/test_g0_atomic_checked_demote_installed.py"
readonly INVENTORY="$REPO_ROOT/upstream/sglang/tests/inventory_checked_demote_calls.py"
for artifact in stock-oracle.txt treatment-oracle.txt installed-seam.txt static-inventory.json; do
  test ! -e "$G0_RUN_DIR/$artifact"
done

set +e
env -u PYTHONPATH "$G0_PYTHON" "$SOURCE_ORACLE" --checkout "$STOCK_CHECKOUT" \
  >"$G0_RUN_DIR/stock-oracle.txt" 2>&1
stock_status=$?
set -e
if [[ "$stock_status" != 1 ]] ||
  ! grep -q 'Ran 27 tests' "$G0_RUN_DIR/stock-oracle.txt" ||
  ! grep -q 'FAILED (failures=27)' "$G0_RUN_DIR/stock-oracle.txt"; then
  write_invalid_scope 65 "$LINENO"
fi
env -u PYTHONPATH "$G0_PYTHON" "$SOURCE_ORACLE" --checkout "$TREATMENT_CHECKOUT" \
  >"$G0_RUN_DIR/treatment-oracle.txt" 2>&1
grep -q 'Ran 27 tests' "$G0_RUN_DIR/treatment-oracle.txt"
grep -q '^OK$' "$G0_RUN_DIR/treatment-oracle.txt"

installed_work="$(mktemp -d)"
(
  cd "$installed_work"
  env -u PYTHONPATH "$TREATMENT_PYTHON" "$INSTALLED_TEST"
) >"$G0_RUN_DIR/installed-seam.txt" 2>&1
grep -q '^OK$' "$G0_RUN_DIR/installed-seam.txt"
rm -rf "$installed_work"
installed_work=""

env -u PYTHONPATH "$G0_PYTHON" "$INVENTORY" \
  --source-root "$TREATMENT_CHECKOUT" \
  --output "$G0_RUN_DIR/static-inventory.json"
python3 "$VERIFY_IDENTITY" --run-dir "$G0_RUN_DIR" \
  --repo-root "$SCRIPT_REPO_ROOT" \
  --require-receipt preflight-status.json --receipt-status ADMITTED_PRE_ARM
manifest_sha="$(sha256sum "$G0_RUN_DIR/manifest.json" | awk '{print $1}')"
"$G0_PYTHON" "$FINALIZE" receipt \
  --output "$G0_RUN_DIR/controls-passed.json" \
  --status CONTROLS_PASSED --manifest-sha256 "$manifest_sha"

trap - ERR HUP INT TERM
echo "CONTRACT_CONTROLS_PASSED: $G0_RUN_DIR"
