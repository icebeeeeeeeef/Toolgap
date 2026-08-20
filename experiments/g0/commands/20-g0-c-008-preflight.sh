#!/usr/bin/env bash
# Prepare and seal one exact G0-C-ATOMIC-008 attempt before any server starts.
set -Eeuo pipefail

readonly G0_BASE_COMMIT="92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2"
readonly G0_BASE_TREE="25e9bf86d04c27fe380024d9c8c421c3b5b51f3c"
readonly G0_REMOTE="https://github.com/sgl-project/sglang.git"
readonly G0_PATCH_SHA256="e69776678909b4ee49b1c0fa4a8e208666893b659c0508387c83fcdf11e82a9a"
readonly G0_LONG_COMMAND_TIMEOUT_SECONDS=1800

REPO_ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd)"
G0_ATTEMPT_ID="${G0_ATTEMPT_ID:-}"
if [[ -z "$G0_ATTEMPT_ID" ]]; then
  echo "BLOCKED_BEFORE_EXECUTION: set a stable G0_ATTEMPT_ID" >&2
  exit 78
fi
if [[ ! "$G0_ATTEMPT_ID" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "BLOCKED_BEFORE_EXECUTION: attempt id may use only A-Z a-z 0-9 . _ -" >&2
  exit 78
fi
G0_PYTHON="${G0_PYTHON:-python3.12}"
G0_RUN_DIR="${G0_RUN_DIR:-$REPO_ROOT/experiments/g0/raw/g0-c-008/$G0_ATTEMPT_ID}"
G0_WORK_ROOT="${G0_WORK_ROOT:-/tmp/toolgap-g0-c-008-$G0_ATTEMPT_ID}"
readonly FINALIZE="$REPO_ROOT/experiments/g0/commands/g0_c_008_finalize.py"
HELPER_PYTHON="$(command -v python3 || true)"
if [[ -z "$HELPER_PYTHON" ]]; then
  echo "BLOCKED_BEFORE_EXECUTION: python3 is required for evidence finalization" >&2
  exit 78
fi
if [[ -e "$G0_RUN_DIR" || -e "$G0_WORK_ROOT" ]]; then
  echo "BLOCKED_BEFORE_EXECUTION: attempt destination already exists" >&2
  exit 78
fi
mkdir -p "$(dirname -- "$G0_RUN_DIR")"
mkdir "$G0_RUN_DIR"
G0_RUN_DIR="$(cd "$G0_RUN_DIR" && pwd)"

preflight_failure() {
  local status="$1"
  local line="$2"
  trap - ERR HUP INT TERM
  {
    printf 'phase=preflight\n'
    printf 'exit_code=%s\n' "$status"
    printf 'line=%s\n' "$line"
  } >"$G0_RUN_DIR/preflight-failure.txt"
  "$HELPER_PYTHON" "$FINALIZE" failure \
    --run-dir "$G0_RUN_DIR" \
    --attempt-status BLOCKED_BEFORE_EXECUTION \
    --phase preflight --exit-code "$status" --line "$line" || true
  exit "$status"
}
fail_preflight() {
  echo "BLOCKED_BEFORE_EXECUTION: $1" >&2
  preflight_failure 78 "$LINENO"
}
run_bounded() {
  timeout --signal=TERM --kill-after=30s \
    "${G0_LONG_COMMAND_TIMEOUT_SECONDS}s" "$@"
}
trap 'preflight_failure "$?" "$LINENO"' ERR
trap 'preflight_failure 129 "$LINENO"' HUP
trap 'preflight_failure 130 "$LINENO"' INT
trap 'preflight_failure 143 "$LINENO"' TERM

"$HELPER_PYTHON" - \
  "$REPO_ROOT" "$G0_RUN_DIR/attempt-context.json" "$G0_ATTEMPT_ID" <<'PY'
import hashlib
import json
import os
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

repo = pathlib.Path(sys.argv[1]).resolve()
output = pathlib.Path(sys.argv[2])
spec = repo / "experiments/g0/SPEC.g0-c-008.md"
digest = hashlib.sha256(spec.read_bytes()).hexdigest()
git = lambda *args: subprocess.check_output(
    ["git", "-C", str(repo), *args], text=True
).strip()
document = {
    "admission_manifest": "N/A: admission not completed",
    "attempt_id": sys.argv[3],
    "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "experiment_id": "G0-C-ATOMIC-008",
    "spec_path": "experiments/g0/SPEC.g0-c-008.md",
    "spec_sha256": digest,
    "toolgap_commit": git("rev-parse", "HEAD"),
    "toolgap_tracked_clean": not bool(
        git("status", "--porcelain", "--untracked-files=no")
    ),
    "toolgap_tree": git("rev-parse", "HEAD^{tree}"),
}
descriptor = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode=0o444)
with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
    handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(output, 0o444)
PY

if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
  fail_preflight "G0 requires Linux x86_64"
fi
if [[ ! -f /etc/os-release ]] ||
  ! grep -Eq '^PRETTY_NAME="Ubuntu 24\.04\.3 LTS"$' /etc/os-release; then
  fail_preflight "expected Ubuntu 24.04.3 LTS"
fi
for command in nvidia-smi curl ss git setsid ps comm sha256sum timeout cargo rustc; do
  command -v "$command" >/dev/null || fail_preflight "missing required command: $command"
done
if ! command -v "$G0_PYTHON" >/dev/null; then
  fail_preflight "missing required interpreter: $G0_PYTHON"
fi
G0_PYTHON="$(command -v "$G0_PYTHON")"
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
if [[ -n "$(git -C "$REPO_ROOT" status --porcelain --untracked-files=no)" ]]; then
  fail_preflight "ToolGap tracked files must be clean and committed"
fi

mkdir "$G0_WORK_ROOT"
G0_WORK_ROOT="$(cd "$G0_WORK_ROOT" && pwd)"
readonly STOCK_CHECKOUT="$G0_WORK_ROOT/stock"
readonly TREATMENT_CHECKOUT="$G0_WORK_ROOT/treatment"
readonly RESOLVER_VENV="$G0_WORK_ROOT/resolver-venv"
readonly STOCK_VENV="$G0_WORK_ROOT/stock-venv"
readonly TREATMENT_VENV="$G0_WORK_ROOT/treatment-venv"
readonly WHEEL_ROOT="$G0_RUN_DIR/wheels"
readonly PATCH="$REPO_ROOT/upstream/sglang/patches/0001-atomic-checked-demote.patch"
readonly FROZEN_PATCH="$REPO_ROOT/experiments/g0/artifacts/sglang-session-atomic-checked-demote-v5.patch"
readonly PROVENANCE="$REPO_ROOT/experiments/g0/commands/g0_c_008_package_provenance.py"
mkdir -p "$WHEEL_ROOT/stock" "$WHEEL_ROOT/treatment"

{
  date -u '+%Y-%m-%dT%H:%M:%SZ'
  cat /etc/os-release
  uname -a
  nvidia-smi --query-gpu=name,uuid,memory.total,driver_version --format=csv,noheader
  "$G0_PYTHON" --version
  git --version
  cargo --version
  rustc --version
  printf 'long_command_timeout_seconds=%s\n' "$G0_LONG_COMMAND_TIMEOUT_SECONDS"
  printf 'toolgap_commit=%s\n' "$(git -C "$REPO_ROOT" rev-parse HEAD)"
  printf 'toolgap_tree=%s\n' "$(git -C "$REPO_ROOT" rev-parse 'HEAD^{tree}')"
} >"$G0_RUN_DIR/environment.txt"

test "$(sha256sum "$PATCH" | awk '{print $1}')" = "$G0_PATCH_SHA256"
cmp --silent "$PATCH" "$FROZEN_PATCH"

run_bounded git clone "$G0_REMOTE" "$STOCK_CHECKOUT" \
  >"$G0_RUN_DIR/stock-build-install.log" 2>&1
git -C "$STOCK_CHECKOUT" checkout --detach "$G0_BASE_COMMIT" \
  >>"$G0_RUN_DIR/stock-build-install.log" 2>&1
test "$(git -C "$STOCK_CHECKOUT" remote get-url origin)" = "$G0_REMOTE"
test "$(git -C "$STOCK_CHECKOUT" rev-parse HEAD)" = "$G0_BASE_COMMIT"
test "$(git -C "$STOCK_CHECKOUT" rev-parse 'HEAD^{tree}')" = "$G0_BASE_TREE"
test -z "$(git -C "$STOCK_CHECKOUT" status --porcelain)"

run_bounded git clone "$G0_REMOTE" "$TREATMENT_CHECKOUT" \
  >"$G0_RUN_DIR/treatment-build-install.log" 2>&1
git -C "$TREATMENT_CHECKOUT" checkout --detach "$G0_BASE_COMMIT" \
  >>"$G0_RUN_DIR/treatment-build-install.log" 2>&1
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
  "G0-C-ATOMIC-008 experimental treatment" \
  >>"$G0_RUN_DIR/treatment-build-install.log" 2>&1
test "$(git -C "$TREATMENT_CHECKOUT" rev-parse 'HEAD^')" = "$G0_BASE_COMMIT"
for checkout in "$STOCK_CHECKOUT" "$TREATMENT_CHECKOUT"; do
  test -f "$checkout/python/pyproject.toml"
  test -f "$checkout/python/sglang/launch_server.py"
  test -f "$checkout/python/sglang/srt/entrypoints/http_server.py"
  test -z "$(git -C "$checkout" status --porcelain)"
done

"$G0_PYTHON" -m venv "$RESOLVER_VENV"
run_bounded "$RESOLVER_VENV/bin/python" -m pip install --upgrade pip \
  >"$G0_RUN_DIR/resolver-install.log" 2>&1
run_bounded "$RESOLVER_VENV/bin/python" -m pip wheel --no-deps \
  --wheel-dir "$WHEEL_ROOT/stock" "$STOCK_CHECKOUT/python" \
  >>"$G0_RUN_DIR/stock-build-install.log" 2>&1
mapfile -t stock_wheels < <(find "$WHEEL_ROOT/stock" -maxdepth 1 -name 'sglang-*.whl' -print)
test "${#stock_wheels[@]}" = 1
readonly STOCK_WHEEL="${stock_wheels[0]}"
run_bounded "$RESOLVER_VENV/bin/python" -m pip install "$STOCK_WHEEL" \
  >>"$G0_RUN_DIR/resolver-install.log" 2>&1
"$RESOLVER_VENV/bin/python" -m pip freeze |
  awk 'tolower($0) !~ /^sglang([ =@]|$)/' >"$G0_RUN_DIR/dependency-lock.txt"
test -s "$G0_RUN_DIR/dependency-lock.txt"
run_bounded "$RESOLVER_VENV/bin/python" -m pip wheel --no-deps \
  --wheel-dir "$WHEEL_ROOT/treatment" "$TREATMENT_CHECKOUT/python" \
  >>"$G0_RUN_DIR/treatment-build-install.log" 2>&1
mapfile -t treatment_wheels < <(find "$WHEEL_ROOT/treatment" -maxdepth 1 -name 'sglang-*.whl' -print)
test "${#treatment_wheels[@]}" = 1
readonly TREATMENT_WHEEL="${treatment_wheels[0]}"
{
  sha256sum "$STOCK_WHEEL"
  sha256sum "$TREATMENT_WHEEL"
} >"$G0_RUN_DIR/wheels.txt"

for arm in stock treatment; do
  if [[ "$arm" == stock ]]; then
    venv="$STOCK_VENV"; wheel="$STOCK_WHEEL"; log="$G0_RUN_DIR/stock-build-install.log"
  else
    venv="$TREATMENT_VENV"; wheel="$TREATMENT_WHEEL"; log="$G0_RUN_DIR/treatment-build-install.log"
  fi
  "$G0_PYTHON" -m venv "$venv"
  run_bounded "$venv/bin/python" -m pip install --upgrade pip >>"$log" 2>&1
  run_bounded "$venv/bin/python" -m pip install --no-deps \
    --report "$G0_RUN_DIR/$arm-install-report.json" \
    -r "$G0_RUN_DIR/dependency-lock.txt" "$wheel" >>"$log" 2>&1
  "$venv/bin/python" -c '
import sys, torch, transformers
assert ".".join(map(str, sys.version_info[:3])) == "3.12.11"
assert torch.__version__.split("+")[0] == "2.13.0", torch.__version__
assert torch.version.cuda == "13.0", torch.version.cuda
assert transformers.__version__ == "5.12.1", transformers.__version__
' >>"$log" 2>&1
done

env -u PYTHONPATH "$STOCK_VENV/bin/python" "$PROVENANCE" \
  --source-root "$STOCK_CHECKOUT" --install-root "$STOCK_VENV" \
  --expected-interpreter "$STOCK_VENV/bin/python" \
  --output "$G0_RUN_DIR/stock-provenance.json"
env -u PYTHONPATH "$TREATMENT_VENV/bin/python" "$PROVENANCE" \
  --source-root "$TREATMENT_CHECKOUT" --install-root "$TREATMENT_VENV" \
  --expected-interpreter "$TREATMENT_VENV/bin/python" \
  --output "$G0_RUN_DIR/treatment-provenance.json"

run_bounded env -u PYTHONPATH "$STOCK_VENV/bin/python" -c '
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
run_bounded env -u PYTHONPATH "$STOCK_VENV/bin/python" -c '
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

{
  printf 'REPO_ROOT=%q\n' "$REPO_ROOT"
  printf 'G0_ATTEMPT_ID=%q\n' "$G0_ATTEMPT_ID"
  printf 'G0_PYTHON=%q\n' "$G0_PYTHON"
  printf 'G0_RUN_DIR=%q\n' "$G0_RUN_DIR"
  printf 'G0_WORK_ROOT=%q\n' "$G0_WORK_ROOT"
  printf 'STOCK_CHECKOUT=%q\n' "$STOCK_CHECKOUT"
  printf 'TREATMENT_CHECKOUT=%q\n' "$TREATMENT_CHECKOUT"
  printf 'STOCK_PYTHON=%q\n' "$STOCK_VENV/bin/python"
  printf 'TREATMENT_PYTHON=%q\n' "$TREATMENT_VENV/bin/python"
  printf 'STOCK_VENV=%q\n' "$STOCK_VENV"
  printf 'TREATMENT_VENV=%q\n' "$TREATMENT_VENV"
  printf 'STOCK_WHEEL=%q\n' "$STOCK_WHEEL"
  printf 'TREATMENT_WHEEL=%q\n' "$TREATMENT_WHEEL"
  printf 'DEPENDENCY_LOCK=%q\n' "$G0_RUN_DIR/dependency-lock.txt"
  printf 'PATCH=%q\n' "$PATCH"
} >"$G0_RUN_DIR/runtime.env"
chmod 0444 "$G0_RUN_DIR/runtime.env"

"$G0_PYTHON" "$REPO_ROOT/experiments/g0/commands/g0_c_008_seal_manifest.py" \
  --template "$REPO_ROOT/experiments/g0/manifest.g0-c-008.template.json" \
  --spec "$REPO_ROOT/experiments/g0/SPEC.g0-c-008.md" \
  --repo-root "$REPO_ROOT" --output "$G0_RUN_DIR/manifest.json" \
  --attempt-id "$G0_ATTEMPT_ID" \
  --stock-checkout "$STOCK_CHECKOUT" --treatment-checkout "$TREATMENT_CHECKOUT" \
  --patch "$PATCH" \
  --stock-wheel "$STOCK_WHEEL" --treatment-wheel "$TREATMENT_WHEEL" \
  --dependency-lock "$G0_RUN_DIR/dependency-lock.txt" \
  --environment-readback "$G0_RUN_DIR/environment.txt" \
  --runtime-env "$G0_RUN_DIR/runtime.env" \
  --request "$REPO_ROOT/experiments/g0/request.g0-c-007.json" \
  --model-snapshot "$G0_RUN_DIR/model-snapshot.json" \
  --stock-install-report "$G0_RUN_DIR/stock-install-report.json" \
  --treatment-install-report "$G0_RUN_DIR/treatment-install-report.json" \
  --stock-provenance "$G0_RUN_DIR/stock-provenance.json" \
  --treatment-provenance "$G0_RUN_DIR/treatment-provenance.json" \
  --stock-interpreter "$STOCK_VENV/bin/python" \
  --treatment-interpreter "$TREATMENT_VENV/bin/python"
(cd "$G0_RUN_DIR" && sha256sum manifest.json >manifest.sha256)
chmod 0444 "$G0_RUN_DIR/manifest.sha256"
manifest_sha="$(sha256sum "$G0_RUN_DIR/manifest.json" | awk '{print $1}')"
"$G0_PYTHON" "$FINALIZE" receipt \
  --output "$G0_RUN_DIR/preflight-status.json" \
  --status ADMITTED_PRE_ARM --manifest-sha256 "$manifest_sha"

trap - ERR HUP INT TERM
echo "ADMITTED_PRE_ARM: $G0_RUN_DIR"
