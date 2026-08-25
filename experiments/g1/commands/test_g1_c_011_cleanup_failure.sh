#!/usr/bin/env bash
# A group-exit timeout must remain unsealed and preserve cleanup identity.
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd -P)"
RUNNER="$ROOT/experiments/g1/commands/20-g1-c-011.sh"
TEMPORARY="$(mktemp -d "${TMPDIR:-/tmp}/g1-c-011-cleanup-failure.XXXXXX")"
ARM_PID=""

cleanup() {
  local status="$?"
  trap - EXIT
  if [[ "$ARM_PID" =~ ^[1-9][0-9]*$ ]]; then
    kill -KILL -- "-$ARM_PID" 2>/dev/null || true
    kill -KILL "$ARM_PID" 2>/dev/null || true
    wait "$ARM_PID" 2>/dev/null || true
  fi
  python3 -c 'import shutil, sys; shutil.rmtree(sys.argv[1], ignore_errors=True)' "$TEMPORARY"
  exit "$status"
}
trap cleanup EXIT

sed -n '/BEGIN_SIGNAL_CLEANUP_HELPERS/,/END_SIGNAL_CLEANUP_HELPERS/p' "$RUNNER" >"$TEMPORARY/helpers.sh"
sed -n '/BEGIN_FAILURE_EVIDENCE_HELPER/,/END_FAILURE_EVIDENCE_HELPER/p' "$RUNNER" >>"$TEMPORARY/helpers.sh"
sed -n '/BEGIN_INVALID_SEAL_HELPER/,/END_INVALID_SEAL_HELPER/p' "$RUNNER" >>"$TEMPORARY/helpers.sh"
# shellcheck source=/dev/null
source "$TEMPORARY/helpers.sh"

python3 - "$TEMPORARY/ready" <<'PY' &
import os
import pathlib
import signal
import sys
import time

os.setsid()
def stop(signum, frame):
    raise SystemExit(0)
signal.signal(signal.SIGTERM, stop)
pathlib.Path(sys.argv[1]).write_text(f"{os.getpid()}\n", encoding="utf-8")
time.sleep(60)
PY
ARM_PID="$!"
for _ in $(seq 1 100); do
  [[ -f "$TEMPORARY/ready" ]] && break
  sleep 0.01
done
[[ "$(cat "$TEMPORARY/ready")" == "$ARM_PID" ]]

CURRENT_ARM_PID="$ARM_PID"
CURRENT_ARM_PGID="$ARM_PID"
CURRENT_SAMPLER_PID=""
wait_for_runtime_group_exit() { return 1; }
if stop_current_arm_group; then
  printf 'group-exit timeout was swallowed\n' >&2
  exit 1
fi
[[ "$CURRENT_ARM_PID" == "$ARM_PID" && "$CURRENT_ARM_PGID" == "$ARM_PID" ]]

RUN_DIR="$TEMPORARY/run"
mkdir "$RUN_DIR"
: >"$RUN_DIR/attempt-context.json"
: >"$RUN_DIR/environment.txt"
CALLED="$TEMPORARY/finalizer-called"
export CALLED
printf '%s\n' '#!/usr/bin/env bash' ': >"$CALLED"' 'exit 0' >"$TEMPORARY/fake-python"
chmod +x "$TEMPORARY/fake-python"
PYTHON="$TEMPORARY/fake-python"
FINALIZER="$TEMPORARY/finalizer"
PHASE="formal_arms"

set +e
( seal_invalid 77 )
status=$?
set -e
[[ "$status" == 77 ]]
[[ ! -e "$CALLED" ]]
[[ ! -e "$RUN_DIR/pre-execution-failure.json" ]]
[[ ! -e "$RUN_DIR/execution-status.json" ]]
[[ ! -e "$RUN_DIR/artifact-index.json" ]]
[[ ! -e "$RUN_DIR/completion-receipt.json" ]]
printf 'G1-C-011 cleanup failure remains unsealed\n'
