#!/usr/bin/env bash
# Prepare and seal one exact G0-C-ATOMIC-007 attempt before any server starts.
set -eo pipefail

readonly G0_BASE_COMMIT="92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2"
readonly G0_BASE_TREE="25e9bf86d04c27fe380024d9c8c421c3b5b51f3c"
readonly G0_REMOTE="https://github.com/sgl-project/sglang.git"
readonly G0_PATCH_SHA256="e69776678909b4ee49b1c0fa4a8e208666893b659c0508387c83fcdf11e82a9a"

REPO_ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd)"
G0_ATTEMPT_ID="$G0_ATTEMPT_ID"
if [[ -z "$G0_ATTEMPT_ID" ]]; then
  echo "BLOCKED_BEFORE_EXECUTION: set a stable G0_ATTEMPT_ID" >&2
  exit 78
fi
if [[ ! "$G0_ATTEMPT_ID" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "BLOCKED_BEFORE_EXECUTION: attempt id may use only A-Z a-z 0-9 . _ -" >&2
  exit 78
fi
if [[ -z "$G0_PYTHON" ]]; then G0_PYTHON=python3.12; fi
if [[ -z "$G0_RUN_DIR" ]]; then
  G0_RUN_DIR="$REPO_ROOT/experiments/g0/artifacts/g0-c-007/$G0_ATTEMPT_ID"
fi
if [[ -z "$G0_WORK_ROOT" ]]; then
  G0_WORK_ROOT="/tmp/toolgap-g0-c-007-$G0_ATTEMPT_ID"
fi
set -u

if [[ -e "$G0_RUN_DIR" || -e "$G0_WORK_ROOT" ]]; then
  echo "BLOCKED_BEFORE_EXECUTION: attempt destination already exists" >&2
  exit 78
fi
mkdir "$G0_RUN_DIR"

preflight_failure() {
  local status="$1"
  local line="$2"
  {
    printf 'status=BLOCKED_BEFORE_EXECUTION\n'
    printf 'exit_code=%s\n' "$status"
    printf 'line=%s\n' "$line"
    date -u '+%Y-%m-%dT%H:%M:%SZ'
  } >"$G0_RUN_DIR/preflight-status.txt"
  exit "$status"
}
fail_preflight() {
  echo "BLOCKED_BEFORE_EXECUTION: $1" >&2
  preflight_failure 78 "$LINENO"
}
trap 'preflight_failure "$?" "$LINENO"' ERR

if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
  fail_preflight "G0 requires Linux x86_64"
fi
if ! command -v nvidia-smi >/dev/null || ! command -v "$G0_PYTHON" >/dev/null ||
  ! command -v curl >/dev/null || ! command -v ss >/dev/null; then
  fail_preflight "requires nvidia-smi, curl, ss, and $G0_PYTHON"
fi
if [[ "$(nvidia-smi -L | wc -l | tr -d ' ')" != 1 ]]; then
  fail_preflight "requires exactly one visible GPU"
fi

IFS=',' read -r gpu_name gpu_memory gpu_driver < <(
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits
)
gpu_name="$(xargs <<<"$gpu_name")"
gpu_memory="$(xargs <<<"$gpu_memory")"
gpu_driver="$(xargs <<<"$gpu_driver")"
if [[ "$gpu_name" != "NVIDIA A10" || "$gpu_driver" != 580.65.06 ]] ||
  (( gpu_memory < 22000 || gpu_memory > 25000 )); then
  fail_preflight "expected one NVIDIA A10 (22-25 GiB), driver 580.65.06; got $gpu_name, $gpu_memory MiB, $gpu_driver"
fi
if [[ "$("$G0_PYTHON" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')" != 3.12.11 ]]; then
  fail_preflight "expected Python 3.12.11"
fi

mkdir "$G0_WORK_ROOT"
readonly STOCK_CHECKOUT="$G0_WORK_ROOT/stock"
readonly TREATMENT_CHECKOUT="$G0_WORK_ROOT/treatment"
readonly WHEEL_ROOT="$G0_WORK_ROOT/wheels"
readonly RESOLVER_VENV="$G0_WORK_ROOT/resolver-venv"
readonly STOCK_VENV="$G0_WORK_ROOT/stock-venv"
readonly TREATMENT_VENV="$G0_WORK_ROOT/treatment-venv"
readonly PATCH="$REPO_ROOT/upstream/sglang/patches/0001-atomic-checked-demote.patch"
readonly FROZEN_PATCH="$REPO_ROOT/experiments/g0/artifacts/sglang-session-atomic-checked-demote-v5.patch"

{
  date -u '+%Y-%m-%dT%H:%M:%SZ'
  uname -a
  nvidia-smi --query-gpu=name,uuid,memory.total,driver_version --format=csv,noheader
  "$G0_PYTHON" --version
  git --version
} >"$G0_RUN_DIR/environment.txt"

test "$(sha256sum "$PATCH" | awk '{print $1}')" = "$G0_PATCH_SHA256"
cmp --silent "$PATCH" "$FROZEN_PATCH"

git clone "$G0_REMOTE" "$STOCK_CHECKOUT"
git -C "$STOCK_CHECKOUT" checkout --detach "$G0_BASE_COMMIT"
test "$(git -C "$STOCK_CHECKOUT" remote get-url origin)" = "$G0_REMOTE"
test "$(git -C "$STOCK_CHECKOUT" rev-parse HEAD)" = "$G0_BASE_COMMIT"
test "$(git -C "$STOCK_CHECKOUT" rev-parse 'HEAD^{tree}')" = "$G0_BASE_TREE"
test -z "$(git -C "$STOCK_CHECKOUT" status --porcelain)"

git clone "$G0_REMOTE" "$TREATMENT_CHECKOUT"
git -C "$TREATMENT_CHECKOUT" checkout --detach "$G0_BASE_COMMIT"
git -C "$TREATMENT_CHECKOUT" apply --check "$PATCH"
git -C "$TREATMENT_CHECKOUT" apply "$PATCH"
expected_paths="$(
  printf '%s\n' \
    python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py \
    python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py \
    python/sglang/srt/mem_cache/unified_cache/unified_tree_core_interface.py \
    python/sglang/srt/mem_cache/unified_radix_cache.py | LC_ALL=C sort
)"
actual_paths="$(git -C "$TREATMENT_CHECKOUT" diff --name-only "$G0_BASE_COMMIT" | LC_ALL=C sort)"
test "$actual_paths" = "$expected_paths"
git -C "$TREATMENT_CHECKOUT" -c user.name=ToolGap-G0 \
  -c user.email=toolgap-g0@invalid commit --no-gpg-sign -am \
  "G0-C-ATOMIC-007 experimental treatment"
test "$(git -C "$TREATMENT_CHECKOUT" rev-parse 'HEAD^')" = "$G0_BASE_COMMIT"
for checkout in "$STOCK_CHECKOUT" "$TREATMENT_CHECKOUT"; do
  test -f "$checkout/pyproject.toml"
  test -f "$checkout/python/sglang/launch_server.py"
  test -f "$checkout/python/sglang/srt/entrypoints/http_server.py"
done

"$G0_PYTHON" -m venv "$RESOLVER_VENV"
"$RESOLVER_VENV/bin/python" -m pip install --upgrade pip
mkdir -p "$WHEEL_ROOT/stock" "$WHEEL_ROOT/treatment"
"$RESOLVER_VENV/bin/python" -m pip wheel --no-deps \
  --wheel-dir "$WHEEL_ROOT/stock" "$STOCK_CHECKOUT/python"
readonly STOCK_WHEEL="$(find "$WHEEL_ROOT/stock" -maxdepth 1 -name 'sglang-*.whl' -print -quit)"
test -f "$STOCK_WHEEL"
"$RESOLVER_VENV/bin/python" -m pip install "$STOCK_WHEEL"
"$RESOLVER_VENV/bin/python" -m pip freeze |
  awk 'tolower($0) !~ /^sglang([ =@]|$)/' >"$G0_RUN_DIR/dependency-lock.txt"
test -s "$G0_RUN_DIR/dependency-lock.txt"
"$RESOLVER_VENV/bin/python" -m pip wheel --no-deps \
  --wheel-dir "$WHEEL_ROOT/treatment" "$TREATMENT_CHECKOUT/python"
readonly TREATMENT_WHEEL="$(find "$WHEEL_ROOT/treatment" -maxdepth 1 -name 'sglang-*.whl' -print -quit)"
test -f "$TREATMENT_WHEEL"
{
  sha256sum "$STOCK_WHEEL"
  sha256sum "$TREATMENT_WHEEL"
} >"$G0_RUN_DIR/wheels.txt"

for arm in stock treatment; do
  if [[ "$arm" == stock ]]; then
    venv="$STOCK_VENV"; wheel="$STOCK_WHEEL"
  else
    venv="$TREATMENT_VENV"; wheel="$TREATMENT_WHEEL"
  fi
  "$G0_PYTHON" -m venv "$venv"
  "$venv/bin/python" -m pip install --upgrade pip
  "$venv/bin/python" -m pip install -r "$G0_RUN_DIR/dependency-lock.txt"
  "$venv/bin/python" -m pip install --no-deps "$wheel"
  "$venv/bin/python" -c '
import sys, torch, transformers
assert ".".join(map(str, sys.version_info[:3])) == "3.12.11"
assert torch.__version__.split("+")[0] == "2.13.0", torch.__version__
assert torch.version.cuda == "13.0", torch.version.cuda
assert transformers.__version__ == "5.12.1", transformers.__version__
'
done

env -u PYTHONPATH "$STOCK_VENV/bin/python" \
  "$REPO_ROOT/experiments/g0/commands/g0_c_007_package_provenance.py" \
  --source-root "$STOCK_CHECKOUT" --output "$G0_RUN_DIR/stock-provenance.json"
env -u PYTHONPATH "$TREATMENT_VENV/bin/python" \
  "$REPO_ROOT/experiments/g0/commands/g0_c_007_package_provenance.py" \
  --source-root "$TREATMENT_CHECKOUT" --output "$G0_RUN_DIR/treatment-provenance.json"
env -u PYTHONPATH "$STOCK_VENV/bin/python" -c '
import json
from huggingface_hub import snapshot_download
print(json.dumps({
    "repository": "Qwen/Qwen2.5-0.5B-Instruct",
    "revision": "c89bee90d9f811437d9735454613c35b4a3c4dc8",
    "snapshot_path": snapshot_download(
        "Qwen/Qwen2.5-0.5B-Instruct",
        revision="c89bee90d9f811437d9735454613c35b4a3c4dc8",
    ),
}, sort_keys=True))
' >"$G0_RUN_DIR/model-snapshot.json"
env -u PYTHONPATH "$STOCK_VENV/bin/python" -c '
import json
from transformers import AutoTokenizer
request = json.load(open("'"$REPO_ROOT"'/experiments/g0/request.g0-c-007.json"))
tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen2.5-0.5B-Instruct",
    revision="c89bee90d9f811437d9735454613c35b4a3c4dc8",
)
count = len(tokenizer.encode(request["text"], add_special_tokens=True))
assert count >= 32, count
print(count)
' >"$G0_RUN_DIR/request-input-token-count.txt"

"$G0_PYTHON" "$REPO_ROOT/experiments/g0/commands/g0_c_007_seal_manifest.py" \
  --template "$REPO_ROOT/experiments/g0/manifest.g0-c-007.template.json" \
  --spec "$REPO_ROOT/experiments/g0/SPEC.g0-c-007.md" \
  --output "$G0_RUN_DIR/manifest.json" \
  --attempt-id "$G0_ATTEMPT_ID" \
  --stock-checkout "$STOCK_CHECKOUT" \
  --treatment-checkout "$TREATMENT_CHECKOUT" \
  --stock-wheel "$STOCK_WHEEL" \
  --treatment-wheel "$TREATMENT_WHEEL" \
  --dependency-lock "$G0_RUN_DIR/dependency-lock.txt" \
  --environment-readback "$G0_RUN_DIR/environment.txt" \
  --stock-interpreter "$STOCK_VENV/bin/python" \
  --treatment-interpreter "$TREATMENT_VENV/bin/python"
sha256sum "$G0_RUN_DIR/manifest.json" >"$G0_RUN_DIR/manifest.sha256"
chmod 0444 "$G0_RUN_DIR/manifest.json" "$G0_RUN_DIR/manifest.sha256"

{
  printf 'REPO_ROOT=%q\n' "$REPO_ROOT"
  printf 'G0_ATTEMPT_ID=%q\n' "$G0_ATTEMPT_ID"
  printf 'G0_PYTHON=%q\n' "$G0_PYTHON"
  printf 'G0_RUN_DIR=%q\n' "$G0_RUN_DIR"
  printf 'STOCK_CHECKOUT=%q\n' "$STOCK_CHECKOUT"
  printf 'TREATMENT_CHECKOUT=%q\n' "$TREATMENT_CHECKOUT"
  printf 'STOCK_PYTHON=%q\n' "$STOCK_VENV/bin/python"
  printf 'TREATMENT_PYTHON=%q\n' "$TREATMENT_VENV/bin/python"
  printf 'STOCK_WHEEL=%q\n' "$STOCK_WHEEL"
  printf 'TREATMENT_WHEEL=%q\n' "$TREATMENT_WHEEL"
  printf 'DEPENDENCY_LOCK=%q\n' "$G0_RUN_DIR/dependency-lock.txt"
  printf 'PATCH=%q\n' "$PATCH"
} >"$G0_RUN_DIR/runtime.env"
chmod 0444 "$G0_RUN_DIR/runtime.env"
{
  printf 'status=ADMITTED_PRE_ARM\n'
  printf 'manifest=%s\n' "$G0_RUN_DIR/manifest.json"
} >"$G0_RUN_DIR/preflight-status.txt"
trap - ERR
echo "ADMITTED_PRE_ARM: $G0_RUN_DIR"
