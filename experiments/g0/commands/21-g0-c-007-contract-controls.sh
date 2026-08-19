#!/usr/bin/env bash
# Run source and installed-package controls; this command never starts a server.
set -eo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd)"
G0_RUN_DIR="$G0_RUN_DIR"
if [[ -z "$G0_RUN_DIR" ]]; then
  echo "set G0_RUN_DIR to the directory emitted by command 20" >&2
  exit 64
fi
set -u
test -f "$G0_RUN_DIR/runtime.env"
source "$G0_RUN_DIR/runtime.env"
test -f "$G0_RUN_DIR/manifest.json"
sha256sum --check "$G0_RUN_DIR/manifest.sha256"

readonly SOURCE_ORACLE="$REPO_ROOT/experiments/g0/artifacts/test_atomic_checked_demote_contract_v6.py"
readonly INSTALLED_TEST="$REPO_ROOT/upstream/sglang/tests/test_g0_atomic_checked_demote_installed.py"
readonly INVENTORY="$REPO_ROOT/upstream/sglang/tests/inventory_checked_demote_calls.py"

write_invalid_scope() {
  local status="$1"
  local line="$2"
  trap - ERR
  if [[ -e "$G0_RUN_DIR/execution-status.json" ]]; then
    echo "refusing to replace existing terminal status" >&2
    exit "$status"
  fi
  {
    printf '{\n'
    printf '  "attempt_status": "INVALID_SCOPE",\n'
    printf '  "phase": "contract-controls",\n'
    printf '  "exit_code": %s,\n' "$status"
    printf '  "line": %s\n' "$line"
    printf '}\n'
  } >"$G0_RUN_DIR/execution-status.json"
  exit "$status"
}
trap 'write_invalid_scope "$?" "$LINENO"' ERR
for artifact in stock-oracle.txt treatment-oracle.txt installed-seam.txt static-inventory.json; do
  test ! -e "$G0_RUN_DIR/$artifact"
done
test ! -e "$G0_RUN_DIR/execution-status.json"

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
cleanup_installed_work() {
  local status="$1"
  rm -rf "$installed_work"
  exit "$status"
}
trap 'cleanup_installed_work "$?"' EXIT
(
  cd "$installed_work"
  env -u PYTHONPATH "$TREATMENT_PYTHON" "$INSTALLED_TEST"
) >"$G0_RUN_DIR/installed-seam.txt" 2>&1
grep -q '^OK$' "$G0_RUN_DIR/installed-seam.txt"

env -u PYTHONPATH "$G0_PYTHON" "$INVENTORY" \
  --source-root "$TREATMENT_CHECKOUT" \
  --output "$G0_RUN_DIR/static-inventory.json"
sha256sum --check "$G0_RUN_DIR/manifest.sha256"
trap - ERR
echo "CONTRACT_CONTROLS_PASSED: $G0_RUN_DIR"
