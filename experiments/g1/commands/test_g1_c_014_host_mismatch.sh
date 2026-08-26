#!/usr/bin/env bash
# A host admission mismatch must seal an identifiable offline-verifiable attempt.
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd -P)"
TEMPORARY="$(mktemp -d "${TMPDIR:-/tmp}/g1-c-014-host-mismatch.XXXXXX")"
FIXTURE="$TEMPORARY/repo"
RUN_DIR="$TEMPORARY/run"
WORK_ROOT="$TEMPORARY/work"

cleanup() {
  local status="$?"
  trap - EXIT
  python3 -c 'import shutil, sys; shutil.rmtree(sys.argv[1], ignore_errors=True)' "$TEMPORARY"
  exit "$status"
}
trap cleanup EXIT

mkdir -p "$FIXTURE/experiments/g1/commands"
cp "$ROOT/experiments/g1/commands/20-g1-c-014.sh" "$FIXTURE/experiments/g1/commands/"
cp "$ROOT/experiments/g1/commands/g1_c_014_finalize.py" "$FIXTURE/experiments/g1/commands/"
cp "$ROOT/experiments/g1/SPEC.g1-c-014.md" "$FIXTURE/experiments/g1/"
(
  cd "$FIXTURE"
  git init -q
  git config user.name 'G1-C-014 Host Test'
  git config user.email 'g1-c-014-host-test@invalid'
  git add .
  git commit -q -m fixture
)

INPUTS=()
for name in source model runtime-wheel runtime-provenance wheelhouse manifest oss-receipt bootstrap-receipt; do
  path="$TEMPORARY/$name"
  printf 'fixture\n' >"$path"
  INPUTS+=("$path")
done

set +e
G1_C_014_ATTEMPT_ID=host-mismatch \
G1_C_014_PYTHON="$(command -v python3)" \
G1_C_014_RUN_DIR="$RUN_DIR" \
G1_C_014_WORK_ROOT="$WORK_ROOT" \
G1_C_014_SOURCE_SEED_ARCHIVE="${INPUTS[0]}" \
G1_C_014_MODEL_SEED_ARCHIVE="${INPUTS[1]}" \
G1_C_014_RUNTIME_WHEEL="${INPUTS[2]}" \
G1_C_014_RUNTIME_WHEEL_PROVENANCE="${INPUTS[3]}" \
G1_C_014_CUDA_WHEELHOUSE_ARCHIVE="${INPUTS[4]}" \
G1_C_014_INPUT_MANIFEST="${INPUTS[5]}" \
G1_C_014_INPUT_OSS_RECEIPT="${INPUTS[6]}" \
G1_C_014_BOOTSTRAP_RECEIPT="${INPUTS[7]}" \
G1_C_014_CUDA_HOME="$TEMPORARY/absent-cuda" \
bash "$FIXTURE/experiments/g1/commands/20-g1-c-014.sh" >"$TEMPORARY/runner.log" 2>&1
status=$?
set -e
[[ "$status" -ne 0 ]] || { printf 'host mismatch unexpectedly passed\n' >&2; exit 1; }
[[ -f "$RUN_DIR/execution-status.json" ]] || { cat "$TEMPORARY/runner.log" >&2; exit 1; }

python3 "$FIXTURE/experiments/g1/commands/g1_c_014_finalize.py" verify --run-dir "$RUN_DIR"
python3 - "$RUN_DIR" <<'PY'
import json
import pathlib
import sys

run = pathlib.Path(sys.argv[1])
status = json.loads((run / "execution-status.json").read_text(encoding="utf-8"))
failure = json.loads((run / "pre-execution-failure.json").read_text(encoding="utf-8"))
context = json.loads((run / "attempt-context.json").read_text(encoding="utf-8"))
assert status["attempt_status"] == "INVALID"
assert status["evidence_scope"] == "pre_execution"
assert failure["failure_phase"] == "bootstrap"
assert context["work_root"] == str((run.parent / "work").resolve())
PY
printf 'G1-C-014 host mismatch sealing regression passed\n'
