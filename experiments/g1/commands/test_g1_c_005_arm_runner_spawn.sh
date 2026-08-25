#!/usr/bin/env bash
# Execute the generated arm runner while its selected test creates a spawn child.
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd -P)"
RUNNER="$ROOT/experiments/g1/commands/20-g1-c-005.sh"
TEMPORARY="$(mktemp -d "${TMPDIR:-/tmp}/g1-c-005-arm-runner.XXXXXX")"
trap 'rm -rf "$TEMPORARY"' EXIT

awk '
  /^cat >"\$RUN_DIR\/arm-runner\.py" <<'"'"'PY'"'"'$/ { capture = 1; next }
  capture && /^PY$/ { exit }
  capture { print }
' "$RUNNER" >"$TEMPORARY/arm-runner.py"
test -s "$TEMPORARY/arm-runner.py"
cat >"$TEMPORARY/spawn_case.py" <<'PY'
import multiprocessing
import os
import unittest


class SpawnSafe(unittest.TestCase):
    def test_spawn_child(self):
        child = multiprocessing.get_context("spawn").Process(target=os.getpid)
        child.start()
        child.join(20)
        self.assertEqual(child.exitcode, 0)
PY

python3 "$TEMPORARY/arm-runner.py" "$TEMPORARY/spawn_case.py" \
  'SpawnSafe.test_spawn_child' >"$TEMPORARY/runner.log" 2>&1
test "$(grep -c 'test_spawn_child' "$TEMPORARY/runner.log")" = 1
grep -Fq 'OK' "$TEMPORARY/runner.log"
if grep -Fq '_check_not_importing_main' "$TEMPORARY/runner.log"; then
  printf 'spawn child re-executed arm runner main\n' >&2
  exit 1
fi
printf 'G1-C-005 arm runner spawn regression passed\n'
