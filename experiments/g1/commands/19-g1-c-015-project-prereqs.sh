#!/usr/bin/env bash
# Install only the ordinary Ninja host prerequisite required by G1-C-015.
set -Eeuo pipefail

INPUT_MANIFEST="${G1_C_015_INPUT_MANIFEST:-}"
PYTHON="${G1_C_015_PYTHON:-python3}"
readonly NINJA_PATH="/usr/bin/ninja"

die() { printf 'g1-c-015 prerequisites: %s\n' "$*" >&2; exit 2; }
[[ "$INPUT_MANIFEST" = /* && -f "$INPUT_MANIFEST" && ! -L "$INPUT_MANIFEST" ]] || die 'input manifest must be an absolute regular file'
command -v "$PYTHON" >/dev/null || die 'Python is unavailable'
PYTHON="$(command -v "$PYTHON")"
SELF_PATH="$(cd -- "$(dirname -- "$0")" && pwd -P)/$(basename -- "$0")"
[[ -f "$SELF_PATH" && ! -L "$SELF_PATH" ]] || die 'prerequisite command must be a regular file'

# Bind the downloaded command before any apt invocation.
"$PYTHON" - "$SELF_PATH" "$INPUT_MANIFEST" <<'PY'
import hashlib
import json
import pathlib
import sys

script, manifest_path = map(pathlib.Path, sys.argv[1:])
expected_path = "experiments/g1/commands/19-g1-c-015-project-prereqs.sh"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
identity = manifest.get("identity")
if not isinstance(identity, dict) or identity.get("bundle_id") != "G1-C-015":
    raise ValueError("input manifest identity differs")
entry = manifest.get("static_inputs", {}).get(expected_path)
if not isinstance(entry, dict) or set(entry) != {"sha256", "size_bytes"}:
    raise ValueError("input manifest omits the prerequisite command binding")
if entry["sha256"] != hashlib.sha256(script.read_bytes()).hexdigest():
    raise ValueError("prerequisite command hash differs from the input manifest")
if entry["size_bytes"] != script.stat().st_size:
    raise ValueError("prerequisite command size differs from the input manifest")
PY

[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || die 'requires Linux x86_64'
grep -Eq '^ID=ubuntu$' /etc/os-release && grep -Eq '^VERSION_ID="?24\.04"?$' /etc/os-release || die 'requires Ubuntu 24.04'

run_privileged() {
  if [[ "${EUID:-$(id -u)}" == 0 ]]; then
    "$@"
  else
    command -v sudo >/dev/null || die 'sudo is required to install ninja-build'
    sudo "$@"
  fi
}

if [[ ! -x "$NINJA_PATH" ]]; then
  command -v apt-get >/dev/null || die 'apt-get is unavailable'
  run_privileged apt-get update
  run_privileged apt-get install -y --no-install-recommends ninja-build
fi

[[ -x "$NINJA_PATH" ]] || die 'ninja-build did not provide executable /usr/bin/ninja'
command -v dpkg-query >/dev/null || die 'dpkg-query is unavailable'
NINJA_VERSION="$("$NINJA_PATH" --version)"
PACKAGE_VERSION="$(dpkg-query -W -f='${Version}\n' ninja-build)"
[[ -n "$NINJA_VERSION" && -n "$PACKAGE_VERSION" ]] || die 'ninja version evidence is unavailable'
printf 'NINJA_PATH=%s\nNINJA_VERSION=%s\nNINJA_BUILD_PACKAGE_VERSION=%s\n' \
  "$NINJA_PATH" "$NINJA_VERSION" "$PACKAGE_VERSION"
