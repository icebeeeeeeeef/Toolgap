#!/usr/bin/env bash
# Prove pip accepts the manifest-preserved runtime wheel filename after copying.
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd -P)"
RUNNER="$ROOT/experiments/g1/commands/20-g1-c-009.sh"
TEMPORARY="$(mktemp -d "${TMPDIR:-/tmp}/g1-c-009-runtime-wheel.XXXXXX")"
trap 'python3 -c '\''import shutil, sys; shutil.rmtree(sys.argv[1], ignore_errors=True)'\'' "$TEMPORARY"' EXIT

sed -n '/BEGIN_RUNTIME_WHEEL_COPY_HELPERS/,/END_RUNTIME_WHEEL_COPY_HELPERS/p' "$RUNNER" >"$TEMPORARY/helper.sh"
die() { printf 'fixture failure: %s\n' "$*" >&2; return 2; }
PYTHON="$(command -v python3)"
# shellcheck source=/dev/null
source "$TEMPORARY/helper.sh"

WHEEL_FILENAME='fixture_runtime-0.0.0-py3-none-any.whl'
INPUT_DIR="$TEMPORARY/input"
RUN_DIR="$TEMPORARY/run"
mkdir "$INPUT_DIR" "$RUN_DIR"
INPUT_WHEEL="$INPUT_DIR/$WHEEL_FILENAME"
"$PYTHON" - "$INPUT_WHEEL" <<'PY'
import pathlib
import sys
import zipfile

wheel = pathlib.Path(sys.argv[1])
files = {
    "fixture_runtime/__init__.py": b"VALUE = 'installed'\n",
    "fixture_runtime-0.0.0.dist-info/METADATA": (
        b"Metadata-Version: 2.1\nName: fixture-runtime\nVersion: 0.0.0\n\n"
    ),
    "fixture_runtime-0.0.0.dist-info/WHEEL": (
        b"Wheel-Version: 1.0\nGenerator: g1-c-009-regression\n"
        b"Root-Is-Purelib: true\nTag: py3-none-any\n"
    ),
    "fixture_runtime-0.0.0.dist-info/RECORD": b"",
}
with zipfile.ZipFile(wheel, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for name, contents in files.items():
        archive.writestr(name, contents)
PY
MANIFEST="$TEMPORARY/input-manifest.json"
"$PYTHON" - "$MANIFEST" "$WHEEL_FILENAME" <<'PY'
import json
import pathlib
import sys

pathlib.Path(sys.argv[1]).write_text(
    json.dumps({"archives": {"runtime_wheel": {"path": sys.argv[2]}}}),
    encoding="utf-8",
)
PY

RUNTIME_WHEEL_FILENAME="$(runtime_wheel_filename "$MANIFEST")"
[[ "$RUNTIME_WHEEL_FILENAME" == "$WHEEL_FILENAME" ]]
copy_immutable "$INPUT_WHEEL" "$RUN_DIR/$RUNTIME_WHEEL_FILENAME"
COPIED_WHEEL="$RUN_DIR/$RUNTIME_WHEEL_FILENAME"
test -f "$COPIED_WHEEL" && test ! -L "$COPIED_WHEEL"

VENV="$TEMPORARY/venv"
"$PYTHON" -m venv "$VENV"
"$VENV/bin/python" -m pip install --no-deps --force-reinstall "$COPIED_WHEEL" >"$TEMPORARY/pip-valid.log" 2>&1
"$VENV/bin/python" -c "import fixture_runtime; assert fixture_runtime.VALUE == 'installed'"

# A generic filename is the sealed C-003 failure mode and must remain rejected.
cp "$INPUT_WHEEL" "$RUN_DIR/runtime-wheel.whl"
if "$VENV/bin/python" -m pip install --no-deps --force-reinstall "$RUN_DIR/runtime-wheel.whl" >"$TEMPORARY/pip-generic.log" 2>&1; then
  die 'pip accepted a generic runtime wheel filename'
fi
grep -Fq 'not a valid wheel filename' "$TEMPORARY/pip-generic.log"
printf 'G1-C-009 runtime wheel filename regression passed\n'
