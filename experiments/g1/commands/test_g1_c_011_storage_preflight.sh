#!/usr/bin/env bash
# Exercise both pass and insufficient-space outcomes from the runner's real gate.
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd -P)"
RUNNER="$ROOT/experiments/g1/commands/20-g1-c-011.sh"
TEMPORARY="$(mktemp -d "${TMPDIR:-/tmp}/g1-c-011-storage-preflight.XXXXXX")"
trap 'python3 -c '\''import shutil, sys; shutil.rmtree(sys.argv[1], ignore_errors=True)'\'' "$TEMPORARY"' EXIT

sed -n '/BEGIN_STORAGE_PREFLIGHT_HELPER/,/END_STORAGE_PREFLIGHT_HELPER/p' "$RUNNER" >"$TEMPORARY/helper.sh"
PYTHON="$(command -v python3)"
# shellcheck source=/dev/null
source "$TEMPORARY/helper.sh"

TARGET="$TEMPORARY/work"
mkdir "$TARGET"
PASS_MANIFEST="$TEMPORARY/pass-manifest.json"
printf '%s\n' '{"storage_preflight":{"minimum_free_bytes":1}}' >"$PASS_MANIFEST"
PASS_OUTPUT="$TEMPORARY/pass.json"
storage_preflight "$PASS_OUTPUT" source_restore "$TARGET" "$PASS_MANIFEST"

AVAILABLE="$($PYTHON - "$PASS_OUTPUT" <<'PY'
import json, pathlib, stat, sys
document = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert document["schema_version"] == 1
assert document["stage"] == "source_restore"
assert document["minimum_free_bytes"] == 1
assert document["available_free_bytes"] >= 1
assert document["total_bytes"] >= document["available_free_bytes"]
assert pathlib.Path(document["path"]).is_absolute()
assert stat.S_IMODE(pathlib.Path(sys.argv[1]).stat().st_mode) == 0o444
print(document["available_free_bytes"])
PY
)"

FAIL_MANIFEST="$TEMPORARY/fail-manifest.json"
printf '{"storage_preflight":{"minimum_free_bytes":%s}}\n' "$((AVAILABLE + 1))" >"$FAIL_MANIFEST"
FAIL_OUTPUT="$TEMPORARY/fail.json"
if storage_preflight "$FAIL_OUTPUT" resolver "$TARGET" "$FAIL_MANIFEST" >"$TEMPORARY/fail.log" 2>&1; then
  printf 'storage preflight accepted an impossible free-space bound\n' >&2
  exit 1
fi
"$PYTHON" - "$FAIL_OUTPUT" "$AVAILABLE" <<'PY'
import json, pathlib, sys
document = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert document["stage"] == "resolver"
assert document["minimum_free_bytes"] == int(sys.argv[2]) + 1
assert document["available_free_bytes"] < document["minimum_free_bytes"]
PY
grep -Fq 'below manifest minimum' "$TEMPORARY/fail.log"
printf 'G1-C-011 storage preflight regression passed\n'
