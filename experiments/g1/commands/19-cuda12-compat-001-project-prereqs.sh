#!/usr/bin/env bash
# Install only the ordinary host commands needed by CUDA12-COMPAT-001.
set -Eeuo pipefail

INPUT_MANIFEST="${CUDA12_COMPAT_INPUT_MANIFEST:-}"
PYTHON="${CUDA12_COMPAT_PYTHON:-python3}"

if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]] ||
  [[ ! -f /etc/os-release ]] ||
  ! grep -Eq '^ID=ubuntu$' /etc/os-release ||
  ! grep -Eq '^VERSION_ID="?24\.04"?$' /etc/os-release; then
  echo "expected Ubuntu 24.04 x86_64" >&2
  exit 78
fi

if ! command -v nvidia-smi >/dev/null ||
  [[ ! -x /usr/local/cuda-12.8/bin/nvcc ]]; then
  echo "GPU driver/CUDA substrate is absent; select the declared provider image instead of installing it here" >&2
  exit 78
fi

[[ "$INPUT_MANIFEST" = /* && -f "$INPUT_MANIFEST" ]]
command -v "$PYTHON" >/dev/null
PYTHON="$(command -v "$PYTHON")"
SELF_PATH="$(cd -- "$(dirname -- "$0")" && pwd -P)/$(basename -- "$0")"
[[ -f "$SELF_PATH" && ! -L "$SELF_PATH" ]]

# This script runs before the ToolGap checkout exists. Bind its own downloaded
# bytes before the first privileged command.
"$PYTHON" - "$SELF_PATH" "$INPUT_MANIFEST" <<'PY'
import hashlib
import json
import pathlib
import sys

script, manifest_path = map(pathlib.Path, sys.argv[1:])
expected_path = "experiments/g1/commands/19-cuda12-compat-001-project-prereqs.sh"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
entry = manifest.get("static_inputs", {}).get(expected_path)
if not isinstance(entry, dict) or set(entry) != {"sha256", "size_bytes"}:
    raise ValueError("input manifest omits the prerequisite script binding")
digest = hashlib.sha256(script.read_bytes()).hexdigest()
if entry["sha256"] != digest or entry["size_bytes"] != script.stat().st_size:
    raise ValueError("prerequisite script differs from the sealed input manifest")
archives = manifest.get("archives")
required = {
    "model_snapshot", "cuda_wheelhouse", "runtime_wheel",
    "runtime_wheel_provenance", "sglang_source_seed", "toolgap_source_seed",
}
if not isinstance(archives, dict) or set(archives) != required:
    raise ValueError("input manifest archive set differs")
PY

needs_apt=false
for command in curl git ninja python3 ss; do
  command -v "$command" >/dev/null || needs_apt=true
done
if ! python3 -c 'import ensurepip, venv' >/dev/null 2>&1; then
  needs_apt=true
fi

if [[ "$needs_apt" == true ]]; then
  sudo apt-get update
  sudo apt-get install -y --no-install-recommends \
    curl git iproute2 ninja-build python3-venv
fi

for command in curl git ninja python3 ss; do
  command -v "$command" >/dev/null
done
python3 -c 'import ensurepip, venv'
echo "PROJECT_PREREQUISITES_READY"
