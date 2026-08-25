#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd -P)"
RUNNER="$ROOT/experiments/g1/commands/20-g1-c-007.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

sed -n '/# BEGIN_FAILURE_EVIDENCE_HELPER/,/# END_FAILURE_EVIDENCE_HELPER/p' "$RUNNER" >"$TMP/helper.sh"
# shellcheck source=/dev/null
source "$TMP/helper.sh"

PYTHON="${PYTHON:-python3}"
RUN_DIR="$TMP/run"
mkdir "$RUN_DIR"
record_failure_evidence 23 resolver

"$PYTHON" - "$RUN_DIR/pre-execution-failure.json" <<'PY'
import json, pathlib, sys

path = pathlib.Path(sys.argv[1])
assert json.loads(path.read_text(encoding="utf-8")) == {
    "exit_code": 23,
    "failure_phase": "resolver",
    "schema_version": 1,
}
assert path.stat().st_mode & 0o777 == 0o444
PY

if record_failure_evidence 24 resolver 2>/dev/null; then
  echo "failure evidence was replaceable" >&2
  exit 1
fi

printf 'G1-C-007 failure evidence helper checks passed\n'
