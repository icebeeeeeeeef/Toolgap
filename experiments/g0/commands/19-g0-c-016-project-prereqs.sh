#!/usr/bin/env bash
# Install only project build tools that the provider GPU image does not promise.
set -Eeuo pipefail

if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]] ||
  [[ ! -f /etc/os-release ]] ||
  ! grep -Eq '^ID=ubuntu$' /etc/os-release ||
  ! grep -Eq '^VERSION_ID="?24\.04"?$' /etc/os-release; then
  echo "expected Ubuntu 24.04 x86_64" >&2
  exit 78
fi

if ! command -v nvidia-smi >/dev/null ||
  [[ ! -x /usr/local/cuda-13.0/bin/nvcc ]]; then
  echo "GPU driver/CUDA substrate is absent; select Alibaba Cloud's official Ubuntu 24.04 NVIDIA GPU image instead of installing it here" >&2
  exit 78
fi

missing=()
for command in cargo curl git ninja rustc ss; do
  command -v "$command" >/dev/null || missing+=("$command")
done
if ! command -v python3 >/dev/null ||
  ! python3 -c 'import ensurepip, venv' >/dev/null 2>&1; then
  missing+=("python3-venv")
fi

if ((${#missing[@]} == 0)); then
  echo "PROJECT_PREREQUISITES_PRESENT"
  exit 0
fi

sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  build-essential cargo curl git iproute2 ninja-build python3-venv rustc

for command in cargo curl git ninja rustc ss python3; do
  command -v "$command" >/dev/null
done
python3 -c 'import ensurepip, venv'
echo "PROJECT_PREREQUISITES_READY"
