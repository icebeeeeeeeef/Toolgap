#!/usr/bin/env bash
# Check that the sealed attempt has every required terminal, then emit its evidence index.
set -eo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd)"
G0_RUN_DIR="$G0_RUN_DIR"
if [[ -z "$G0_RUN_DIR" ]]; then
  echo "set G0_RUN_DIR to the directory emitted by command 20" >&2
  exit 64
fi
set -u
source "$G0_RUN_DIR/runtime.env"
sha256sum --check "$G0_RUN_DIR/manifest.sha256"
write_verify_failure() {
  local status="$1"
  local line="$2"
  local attempt_status="$3"
  trap - ERR
  if [[ -e "$G0_RUN_DIR/execution-status.json" ]]; then
    echo "refusing to replace existing terminal status" >&2
    exit "$status"
  fi
  {
    printf '{\n'
    printf '  "attempt_status": "%s",\n' "$attempt_status"
    printf '  "phase": "final-verification",\n'
    printf '  "exit_code": %s,\n' "$status"
    printf '  "line": %s\n' "$line"
    printf '}\n'
  } >"$G0_RUN_DIR/execution-status.json"
  exit "$status"
}
trap 'write_verify_failure "$?" "$LINENO" INVALID_SCOPE' ERR
test ! -e "$G0_RUN_DIR/execution-status.json"
test ! -e "$G0_RUN_DIR/artifact-index.json"
"$G0_PYTHON" -c '
import hashlib, json, pathlib, subprocess, sys

manifest_path, spec_path, stock, treatment, patch, stock_wheel, treatment_wheel, lock = map(
    pathlib.Path, sys.argv[1:]
)
manifest = json.loads(manifest_path.read_text())
source = manifest["source"]
identity = manifest["identity"]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(checkout, *args):
    return subprocess.check_output(["git", "-C", str(checkout), *args], text=True).strip()

assert digest(spec_path) == identity["spec_sha256"]
assert digest(patch) == source["patch_sha256"]
assert digest(stock_wheel) == source["stock_wheel_sha256"]
assert digest(treatment_wheel) == source["treatment_wheel_sha256"]
assert digest(lock) == source["dependency_lock_sha256"]
assert git(stock, "rev-parse", "HEAD") == source["stock_commit"]
assert git(stock, "rev-parse", "HEAD^{tree}") == source["stock_tree"]
assert git(treatment, "rev-parse", "HEAD") == source["treatment_commit"]
assert git(treatment, "rev-parse", "HEAD^{tree}") == source["treatment_tree"]
assert not git(stock, "status", "--porcelain")
assert not git(treatment, "status", "--porcelain")
' \
  "$G0_RUN_DIR/manifest.json" \
  "$REPO_ROOT/experiments/g0/SPEC.g0-c-007.md" \
  "$STOCK_CHECKOUT" "$TREATMENT_CHECKOUT" "$PATCH" \
  "$STOCK_WHEEL" "$TREATMENT_WHEEL" "$DEPENDENCY_LOCK"

for artifact in \
  stock-oracle.txt treatment-oracle.txt installed-seam.txt static-inventory.json \
  stock-provenance.json treatment-provenance.json \
  stock-server.log treatment-server.log \
  stock-request-1.sse stock-request-2.sse \
  treatment-request-1.sse treatment-request-2.sse \
  stock-request-1.json stock-request-2.json \
  treatment-request-1.json treatment-request-2.json \
  stock-cleanup-status.txt treatment-cleanup-status.txt \
  stock-gpu-before.txt stock-gpu-after.txt treatment-gpu-before.txt treatment-gpu-after.txt; do
  test -s "$G0_RUN_DIR/$artifact"
done
grep -q 'Ran 27 tests' "$G0_RUN_DIR/stock-oracle.txt"
grep -q 'FAILED (failures=27)' "$G0_RUN_DIR/stock-oracle.txt"
grep -q 'Ran 27 tests' "$G0_RUN_DIR/treatment-oracle.txt"
grep -q '^OK$' "$G0_RUN_DIR/treatment-oracle.txt"
grep -q '^OK$' "$G0_RUN_DIR/installed-seam.txt"
grep -q '"passed": true' "$G0_RUN_DIR/static-inventory.json"
grep -q '^passed=true$' "$G0_RUN_DIR/stock-cleanup-status.txt"
grep -q '^passed=true$' "$G0_RUN_DIR/treatment-cleanup-status.txt"

for arm in stock treatment; do
  for request in 1 2; do
    python3 -c '
import json, sys
result = json.load(open(sys.argv[1]))
assert result["passed"] is True, result
' "$G0_RUN_DIR/$arm-request-$request.json"
  done
  pid="$(cat "$G0_RUN_DIR/$arm-server.pid")"
  if kill -0 "$pid" 2>/dev/null; then
    echo "EXECUTION_FAILED_AFTER_START: server still alive: $arm pid $pid" >&2
    write_verify_failure 1 "$LINENO" EXECUTION_FAILED_AFTER_START
  fi
done

sha256sum --check "$G0_RUN_DIR/manifest.sha256"
python3 "$REPO_ROOT/experiments/g0/commands/g0_c_007_artifact_index.py" \
  --artifact-dir "$G0_RUN_DIR" --output "$G0_RUN_DIR/artifact-index.json"
trap - ERR
python3 -c '
import json, pathlib, sys
target = pathlib.Path(sys.argv[1])
target.write_text(json.dumps({
    "attempt_status": "COMPLETED",
    "status": "PROTOCOL_COMPLETE_AWAITING_INDEPENDENT_REVIEW",
    "gate_decision": "N/A",
    "claim_state": "roadmap",
}, indent=2, sort_keys=True) + "\n")
' "$G0_RUN_DIR/execution-status.json"
echo "COMPLETED_PROTOCOL_AWAITING_INDEPENDENT_REVIEW: $G0_RUN_DIR"
