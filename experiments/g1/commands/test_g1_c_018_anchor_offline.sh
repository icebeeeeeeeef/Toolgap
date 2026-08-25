#!/usr/bin/env bash
# Execute the real anchor prefix through local plan generation without OSS I/O.
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd -P)"
ANCHOR="$ROOT/scripts/anchor-g1-c-018-oss.sh"
TEMPORARY="$(mktemp -d "${TMPDIR:-/tmp}/g1-c-018-anchor-offline.XXXXXX")"
trap 'python3 -c '\''import shutil, sys; shutil.rmtree(sys.argv[1], ignore_errors=True)'\'' "$TEMPORARY"' EXIT
ATTEMPT_DIR="$TEMPORARY/attempt"
FAKE_BIN="$TEMPORARY/bin"
ANCHOR_TMP="$TEMPORARY/anchor-tmp"
mkdir "$ATTEMPT_DIR" "$FAKE_BIN" "$ANCHOR_TMP"

python3 - "$ROOT" "$ATTEMPT_DIR" <<'PY'
import argparse
import importlib.util
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
run_dir = pathlib.Path(sys.argv[2])
fixture_path = root / "experiments/g1/commands/test_g1_c_018_pre_execution.py"
spec = importlib.util.spec_from_file_location("g1_c_018_pre_execution_fixture", fixture_path)
assert spec is not None and spec.loader is not None
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
fixture.prepare_run(str(run_dir))
fixture.write_failure(run_dir, "source_restore")
fixture.write_preflight(
    run_dir,
    "storage-preflight-source-restore.json",
    "source_restore",
    passed=True,
)
fixture.write_input_binding_milestone(run_dir)
assert fixture.FINALIZE.invalid(argparse.Namespace(
    run_dir=run_dir,
    reason=fixture.failure_reason("source_restore"),
)) == 0
PY

cat >"$FAKE_BIN/ossutil" <<'SH'
#!/usr/bin/env bash
exit 97
SH
chmod 0755 "$FAKE_BIN/ossutil"

# Preserve the actual process substitutions and plan heredoc. Only remove the
# temporary-directory rm trap and stop before the first OSS helper/call.
awk -v script_dir="$ROOT/scripts" -v root="$ROOT" '
  /^trap .*rm -rf/ { next }
  /^SCRIPT_DIR=/ { print "SCRIPT_DIR=\"" script_dir "\""; next }
  /^ROOT=/ { print "ROOT=\"" root "\""; next }
  /^latest_version\(\)/ { exit }
  { print }
' "$ANCHOR" >"$TEMPORARY/anchor-plan-only.sh"
chmod 0555 "$TEMPORARY/anchor-plan-only.sh"

PATH="$FAKE_BIN:$PATH" TMPDIR="$ANCHOR_TMP" \
  bash "$TEMPORARY/anchor-plan-only.sh" \
    --attempt-dir "$ATTEMPT_DIR" \
    --attempt-id attempt-001 \
    --bucket abc \
    --raw-prefix raw \
    --anchor-prefix anchors \
    >"$TEMPORARY/anchor.log" 2>&1 || {
      cat "$TEMPORARY/anchor.log" >&2
      exit 1
    }

PLAN="$(find "$ANCHOR_TMP" -type f -name plan.tsv -print)"
[[ -f "$PLAN" ]]
[[ "$(find "$ANCHOR_TMP" -type f -name plan.tsv -print | wc -l | tr -d ' ')" == 1 ]]
grep -Fq $'sglang-0.0.0.dev2+g734a8e921-cp312-cp312-linux_x86_64.whl\t' "$PLAN"
printf 'G1-C-018 offline anchor plan regression passed\n'
