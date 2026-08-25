#!/usr/bin/env bash
# Prove a spawn child can import and resolve a selected module's callable.
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd -P)"
RUNNER="$ROOT/experiments/g1/commands/20-g1-c-011.sh"
TEMPORARY="$(mktemp -d "${TMPDIR:-/tmp}/g1-c-011-arm-runner.XXXXXX")"
trap 'python3 -c '\''import shutil, sys; shutil.rmtree(sys.argv[1], ignore_errors=True)'\'' "$TEMPORARY"' EXIT
SCRIPTED_DIR="$TEMPORARY/scripted"
mkdir "$SCRIPTED_DIR"

awk '
  /^cat >"\$RUN_DIR\/arm-runner\.py" <<'"'"'PY'"'"'$/ { capture = 1; next }
  capture && /^PY$/ { exit }
  capture { print }
' "$RUNNER" >"$TEMPORARY/arm-runner.py"
test -s "$TEMPORARY/arm-runner.py"
cat >"$SCRIPTED_DIR/spawn_case.py" <<'PY'
import importlib
import multiprocessing
import pathlib
import unittest


def scripted_callable():
    return "resolved"


def child_resolve_callable(module_name, qualname):
    resolved = importlib.import_module(module_name)
    for part in qualname.split("."):
        resolved = getattr(resolved, part)
    if resolved.__module__ != module_name or resolved() != "resolved":
        raise RuntimeError("spawn child resolved the wrong callable")


class SpawnSafe(unittest.TestCase):
    def test_spawn_child_resolves_callable_module(self):
        module_name = scripted_callable.__module__
        child = multiprocessing.get_context("spawn").Process(
            target=child_resolve_callable,
            args=(module_name, scripted_callable.__qualname__),
        )
        child.start()
        child.join(20)
        self.assertEqual(child.exitcode, 0)
        self.assertEqual(module_name, pathlib.Path(__file__).stem)
PY

if ! python3 "$TEMPORARY/arm-runner.py" "$SCRIPTED_DIR/spawn_case.py" \
  'SpawnSafe.test_spawn_child_resolves_callable_module' >"$TEMPORARY/runner.log" 2>&1; then
  cat "$TEMPORARY/runner.log" >&2
  exit 1
fi
test "$(grep -c 'test_spawn_child_resolves_callable_module' "$TEMPORARY/runner.log")" = 1
grep -Fq 'OK' "$TEMPORARY/runner.log"
if grep -Fq '_check_not_importing_main' "$TEMPORARY/runner.log"; then
  printf 'spawn child re-executed arm runner main\n' >&2
  exit 1
fi
printf 'G1-C-011 arm runner spawn regression passed\n'
