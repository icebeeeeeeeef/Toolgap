#!/usr/bin/env bash
# Admit one offline, no-action scripted-runtime G1 preflight attempt.
set -Eeuo pipefail

readonly BUNDLE_ID="G1-PREFLIGHT-001"
readonly BASE_COMMIT="92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2"
readonly BASE_TREE="25e9bf86d04c27fe380024d9c8c421c3b5b51f3c"
readonly SGLANG_REMOTE="https://github.com/sgl-project/sglang.git"
readonly SOURCE_SEED_SHA256="2d40db92ff1a21cb78e95f4da98352f1fa17086e1a16a82e95070f05e1460400"
readonly PATCH_0001_SHA256="e69776678909b4ee49b1c0fa4a8e208666893b659c0508387c83fcdf11e82a9a"
readonly PATCH_0002_SHA256="e4ca3377abab478c97a9a3c1296cf449e9c6a97a7bb288c76a04fae4406d24f7"
readonly LONG_COMMAND_TIMEOUT_SECONDS=1800

REPO_ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd)"
ATTEMPT_ID="${G1_PREFLIGHT_ATTEMPT_ID:-}"
PYTHON="${G1_PREFLIGHT_PYTHON:-python3}"
RUN_DIR="${G1_PREFLIGHT_RUN_DIR:-$REPO_ROOT/experiments/g1/raw/g1-preflight-001/$ATTEMPT_ID}"
WORK_ROOT="${G1_PREFLIGHT_WORK_ROOT:-/tmp/toolgap-g1-preflight-001-$ATTEMPT_ID}"
SOURCE_SEED_ARCHIVE="${G1_PREFLIGHT_SOURCE_SEED_ARCHIVE:-}"
MODEL_SEED_ARCHIVE="${G1_PREFLIGHT_MODEL_SEED_ARCHIVE:-}"
TOOLGAP_SEED_ARCHIVE="${G1_PREFLIGHT_TOOLGAP_SEED_ARCHIVE:-}"
INPUT_MANIFEST="${G1_PREFLIGHT_INPUT_MANIFEST:-}"
BOOTSTRAP_RECEIPT="${G1_PREFLIGHT_BOOTSTRAP_RECEIPT:-}"
PHASE="preflight"
current_pid=""
current_pgid=""
smoke_port=""

readonly FINALIZE="$REPO_ROOT/experiments/g1/commands/g1_preflight_001_finalize.py"
readonly BUNDLE_MANIFEST="$REPO_ROOT/experiments/g1/commands/g1_preflight_001_bundle_manifest.py"
readonly MODEL_HELPER="$REPO_ROOT/experiments/g0/commands/g0_c_016_model_seed.py"
readonly PROVENANCE="$REPO_ROOT/experiments/g0/commands/g0_c_008_package_provenance.py"
readonly MODEL_INVENTORY="$REPO_ROOT/experiments/g1/artifacts/model-files.g1-preflight-001.json"
readonly TEMPLATE="$REPO_ROOT/experiments/g1/manifest.g1-preflight-001.template.json"
readonly SPEC="$REPO_ROOT/experiments/g1/SPEC.g1-preflight-001.md"
readonly PATCH_0001="$REPO_ROOT/upstream/sglang/patches/0001-atomic-checked-demote.patch"
readonly PATCH_0002="$REPO_ROOT/upstream/sglang/patches/0002-g1-scripted-forced-demote.patch"

fail() {
  local status="$1"
  local line="$2"
  trap - ERR HUP INT TERM
  emergency_cleanup
  if [[ -d "$RUN_DIR" && ! -e "$RUN_DIR/execution-status.json" ]]; then
    "$PYTHON" "$FINALIZE" fail --run-dir "$RUN_DIR" \
      --status "$([[ "$PHASE" == runtime ]] && echo RUNTIME_FAILED || echo BLOCKED_BEFORE_RUNTIME)" \
      --phase "$PHASE" --exit-code "$status" || true
  fi
  exit "$status"
}

run_bounded() {
  timeout --signal=TERM --kill-after=30s "${LONG_COMMAND_TIMEOUT_SECONDS}s" "$@"
}

gpu_pids() {
  nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null |
    awk 'NF && $1 ~ /^[0-9]+$/ {print $1}' | LC_ALL=C sort -n -u
}

target_listener_rows() {
  ss -ltnH | awk -v port="$smoke_port" '$4 ~ (":" port "$") {print}'
}

process_group_members() {
  local pgid="$1"
  ps -eo pid=,pgid=,stat=,args= |
    awk -v target="$pgid" '$2 == target && $3 !~ /^Z/ {sub(/^[[:space:]]+/, ""); print}'
}

emergency_cleanup() {
  if [[ -n "$current_pgid" ]]; then
    kill -TERM -- "-$current_pgid" 2>/dev/null || true
    sleep 2
    kill -KILL -- "-$current_pgid" 2>/dev/null || true
  elif [[ -n "$current_pid" ]]; then
    kill -TERM "$current_pid" 2>/dev/null || true
    sleep 2
    kill -KILL "$current_pid" 2>/dev/null || true
  fi
  if [[ -n "$current_pid" ]]; then wait "$current_pid" 2>/dev/null || true; fi
  current_pid=""
  current_pgid=""
}

wait_for_smoke() {
  local deadline=$((SECONDS + LONG_COMMAND_TIMEOUT_SECONDS))
  local state
  while kill -0 "$current_pid" 2>/dev/null; do
    state="$(ps -o stat= -p "$current_pid" | xargs || true)"
    if [[ "$state" == Z* ]]; then break; fi
    if (( SECONDS >= deadline )); then return 124; fi
    sleep 1
  done
  wait "$current_pid"
}

verify_smoke_cleanup() {
  local process_status="$1"
  local passed=true
  local deadline=$((SECONDS + 60))
  gpu_pids >"$RUN_DIR/smoke-gpu-pids-during.txt"
  comm -13 "$RUN_DIR/smoke-gpu-pids-before.txt" "$RUN_DIR/smoke-gpu-pids-during.txt" \
    >"$RUN_DIR/smoke-gpu-pids-attributable.txt"
  if [[ "$process_status" != 0 ]]; then passed=false; fi
  if kill -0 "$current_pid" 2>/dev/null; then
    passed=false
    kill -TERM -- "-$current_pgid" 2>/dev/null || true
  fi
  while true; do
    process_group_members "$current_pgid" >"$RUN_DIR/smoke-process-group-after.txt"
    target_listener_rows >"$RUN_DIR/smoke-listeners-after.txt"
    gpu_pids >"$RUN_DIR/smoke-gpu-pids-after.txt"
    comm -12 "$RUN_DIR/smoke-gpu-pids-attributable.txt" "$RUN_DIR/smoke-gpu-pids-after.txt" \
      >"$RUN_DIR/smoke-gpu-pids-leaked.txt"
    if [[ ! -s "$RUN_DIR/smoke-process-group-after.txt" &&
      ! -s "$RUN_DIR/smoke-gpu-pids-leaked.txt" &&
      ! -s "$RUN_DIR/smoke-listeners-after.txt" ]]; then
      break
    fi
    if (( SECONDS >= deadline )); then
      passed=false
      kill -KILL -- "-$current_pgid" 2>/dev/null || true
      break
    fi
    sleep 1
  done
  {
    printf 'cleanup=%s\n' "$passed"
    printf 'smoke_pid=%s\n' "$current_pid"
    printf 'smoke_pgid=%s\n' "$current_pgid"
    printf 'smoke_exit_status=%s\n' "$process_status"
  } >"$RUN_DIR/shutdown.log"
  current_pid=""
  current_pgid=""
  [[ "$passed" == true ]]
}

require() {
  command -v "$1" >/dev/null || { echo "missing required command: $1" >&2; return 1; }
}

validate_seed_archive() {
  "$PYTHON" - "$1" "$2" <<'PY'
import pathlib, sys, tarfile

archive, top_level = map(pathlib.Path, sys.argv[1:])
names = set()
with tarfile.open(archive, "r:*") as bundle:
    members = bundle.getmembers()
    if not members:
        raise ValueError("seed archive is empty")
    for member in members:
        pure = pathlib.PurePosixPath(member.name)
        if (
            pure.is_absolute()
            or ".." in pure.parts
            or not pure.parts
            or pure.parts[0] != top_level.name
            or member.name.rstrip("/") in names
            or not (member.isdir() or member.isfile())
        ):
            raise ValueError(f"unsafe seed archive member: {member.name}")
        names.add(member.name.rstrip("/"))
PY
}

copy_immutable() {
  "$PYTHON" - "$1" "$2" <<'PY'
import os, pathlib, shutil, sys

source, output = map(pathlib.Path, sys.argv[1:])
fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with source.open("rb") as reader, os.fdopen(fd, "wb") as writer:
    shutil.copyfileobj(reader, writer, length=1024 * 1024)
os.chmod(output, 0o444)
PY
}

if [[ -z "$ATTEMPT_ID" || ! "$ATTEMPT_ID" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "set G1_PREFLIGHT_ATTEMPT_ID to A-Z a-z 0-9 . _ -" >&2
  exit 78
fi
if [[ -e "$RUN_DIR" || -e "$WORK_ROOT" ]]; then
  echo "attempt destination already exists" >&2
  exit 78
fi
if ! command -v "$PYTHON" >/dev/null; then
  echo "missing requested Python interpreter: $PYTHON" >&2
  exit 78
fi
PYTHON="$(command -v "$PYTHON")"
mkdir -p "$(dirname -- "$RUN_DIR")"
mkdir "$RUN_DIR"
RUN_DIR="$(cd "$RUN_DIR" && pwd)"
trap 'fail "$?" "$LINENO"' ERR
trap 'fail 129 "$LINENO"' HUP
trap 'fail 130 "$LINENO"' INT
trap 'fail 143 "$LINENO"' TERM

"$PYTHON" - "$REPO_ROOT" "$RUN_DIR/attempt-context.json" "$ATTEMPT_ID" <<'PY'
import hashlib, json, os, pathlib, subprocess, sys
from datetime import datetime, timezone

repo = pathlib.Path(sys.argv[1]).resolve()
spec = repo / "experiments/g1/SPEC.g1-preflight-001.md"
git = lambda *args: subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()
doc = {
    "attempt_id": sys.argv[3],
    "bundle_id": "G1-PREFLIGHT-001",
    "claim_state": "roadmap",
    "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "gate": "G1",
    "gate_decision": "N/A",
    "spec_path": "experiments/g1/SPEC.g1-preflight-001.md",
    "spec_sha256": hashlib.sha256(spec.read_bytes()).hexdigest(),
    "toolgap_commit": git("rev-parse", "HEAD"),
    "toolgap_tracked_clean": not bool(git("status", "--porcelain", "--untracked-files=no")),
    "toolgap_tree": git("rev-parse", "HEAD^{tree}"),
}
fd = os.open(sys.argv[2], os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle:
    handle.write(json.dumps(doc, indent=2, sort_keys=True) + "\n")
os.chmod(sys.argv[2], 0o444)
PY

if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
  echo "requires Linux x86_64" >&2
  exit 78
fi
if [[ ! -f /etc/os-release ]] || ! grep -Eq '^ID=ubuntu$' /etc/os-release ||
  ! grep -Eq '^VERSION_ID="?24\.04"?$' /etc/os-release; then
  echo "requires Alibaba Cloud Ubuntu 24.04 GPU image" >&2
  exit 78
fi
readonly CUDA_HOME="${G1_PREFLIGHT_CUDA_HOME:-/usr/local/cuda-13.0}"
export CUDA_HOME
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
for command in cargo curl git nvidia-smi ninja nvcc rustc sha256sum ss tar timeout; do require "$command"; done
[[ -x "$CUDA_HOME/bin/nvcc" ]]
"$CUDA_HOME/bin/nvcc" --version | grep -Eq 'release 13\.0([,.]|$)'
"$PYTHON" -c 'import ensurepip, venv; import sys; assert sys.version_info[:2] == (3, 12), sys.version'
[[ -z "$(git -C "$REPO_ROOT" status --porcelain --untracked-files=no)" ]]
metadata_token="$(curl --silent --show-error --fail --connect-timeout 2 --max-time 5 -X PUT \
  -H 'X-aliyun-ecs-metadata-token-ttl-seconds: 300' \
  http://100.100.100.200/latest/api/token)"
read_metadata() {
  curl --silent --show-error --fail --connect-timeout 2 --max-time 5 \
    -H "X-aliyun-ecs-metadata-token: $metadata_token" \
    "http://100.100.100.200/latest/meta-data/$1"
}
readonly IMAGE_ID="$(read_metadata image-id)"
readonly INSTANCE_TYPE="$(read_metadata instance/instance-type)"
readonly REGION_ID="$(read_metadata region-id)"
readonly ZONE_ID="$(read_metadata zone-id)"
[[ "$IMAGE_ID" =~ ^ubuntu_24_04_x64_100G_with_gpu_driver_and_cuda_alibase_.+\.vhd$ ]]
[[ "$INSTANCE_TYPE" =~ ^ecs\.gn7i- ]]
test "$(nvidia-smi -L | wc -l | tr -d ' ')" = 1
IFS=',' read -r gpu_name gpu_memory gpu_driver < <(
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits
)
gpu_name="$(xargs <<<"$gpu_name")"
gpu_memory="$(xargs <<<"$gpu_memory")"
readonly gpu_name gpu_memory gpu_driver
minimum_driver="580.65.06"
[[ "$(printf '%s\n%s\n' "$minimum_driver" "$gpu_driver" | sort -V | head -n 1)" = "$minimum_driver" ]]
[[ "$gpu_name" = "NVIDIA A10" ]]
(( gpu_memory >= 22000 && gpu_memory <= 25000 ))
[[ "$SOURCE_SEED_ARCHIVE" = /* && "$MODEL_SEED_ARCHIVE" = /* && "$TOOLGAP_SEED_ARCHIVE" = /* && "$INPUT_MANIFEST" = /* && "$BOOTSTRAP_RECEIPT" = /* ]]
[[ -f "$SOURCE_SEED_ARCHIVE" && -f "$MODEL_SEED_ARCHIVE" && -f "$TOOLGAP_SEED_ARCHIVE" && -f "$INPUT_MANIFEST" && -f "$BOOTSTRAP_RECEIPT" ]]
"$PYTHON" "$BUNDLE_MANIFEST" verify --repo-root "$REPO_ROOT" \
  --manifest "$INPUT_MANIFEST" --toolgap-seed "$TOOLGAP_SEED_ARCHIVE" \
  --sglang-seed "$SOURCE_SEED_ARCHIVE" --model-snapshot "$MODEL_SEED_ARCHIVE" \
  >"$RUN_DIR/input-manifest-verify.log" 2>&1
readonly MODEL_SEED_SHA256="$("$PYTHON" - "$INPUT_MANIFEST" <<'PY'
import json, pathlib, sys
value = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
print(value["archives"]["model_snapshot"]["sha256"])
PY
)"
"$PYTHON" - "$BOOTSTRAP_RECEIPT" "$INPUT_MANIFEST" "$TOOLGAP_SEED_ARCHIVE" "$REPO_ROOT" <<'PY'
import hashlib, json, pathlib, sys

receipt_path, manifest_path, seed_path, repo_root = map(pathlib.Path, sys.argv[1:])
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
expected = {
    "input_manifest_path", "input_manifest_sha256", "toolgap_checkout",
    "toolgap_commit", "toolgap_remote", "toolgap_seed_path",
    "toolgap_seed_sha256", "toolgap_tree",
}
if set(receipt) != expected:
    raise ValueError("bootstrap receipt fields differ")
def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()
if receipt["input_manifest_sha256"] != digest(manifest_path):
    raise ValueError("bootstrap receipt input manifest differs")
if receipt["toolgap_seed_sha256"] != digest(seed_path):
    raise ValueError("bootstrap receipt ToolGap seed differs")
if pathlib.Path(receipt["toolgap_checkout"]).resolve() != repo_root.resolve():
    raise ValueError("runner checkout was not restored by bootstrap")
identity = manifest["identity"]
for field in ("toolgap_commit", "toolgap_tree", "toolgap_remote"):
    if receipt[field] != identity[field]:
        raise ValueError(f"bootstrap receipt {field} differs from input manifest")
PY
copy_immutable "$INPUT_MANIFEST" "$RUN_DIR/input-manifest.json"
copy_immutable "$BOOTSTRAP_RECEIPT" "$RUN_DIR/bootstrap-receipt.json"
[[ "$(sha256sum "$SOURCE_SEED_ARCHIVE" | awk '{print $1}')" = "$SOURCE_SEED_SHA256" ]]
[[ "$(sha256sum "$PATCH_0001" | awk '{print $1}')" = "$PATCH_0001_SHA256" ]]
[[ "$(sha256sum "$PATCH_0002" | awk '{print $1}')" = "$PATCH_0002_SHA256" ]]

{
  date -u '+%Y-%m-%dT%H:%M:%SZ'
  cat /etc/os-release
  uname -a
  nvidia-smi --query-gpu=name,uuid,memory.total,driver_version --format=csv,noheader
  printf 'alibaba_image_id=%s\n' "$IMAGE_ID"
  printf 'alibaba_instance_type=%s\n' "$INSTANCE_TYPE"
  printf 'alibaba_region_id=%s\n' "$REGION_ID"
  printf 'alibaba_zone_id=%s\n' "$ZONE_ID"
  "$CUDA_HOME/bin/nvcc" --version
  "$PYTHON" --version
  git --version
  cargo --version
  rustc --version
  ninja --version
} >"$RUN_DIR/environment.txt"
{
  printf 'archive=%s\n' "$SOURCE_SEED_ARCHIVE"
  printf 'sha256=%s\n' "$SOURCE_SEED_SHA256"
} >"$RUN_DIR/source-seed.txt"

mkdir "$WORK_ROOT"
readonly SOURCE_INPUT="$WORK_ROOT/source-input"
readonly TOOLGAP_INPUT="$WORK_ROOT/toolgap-input"
readonly TREATMENT="$WORK_ROOT/treatment"
readonly MODEL_INPUT="$WORK_ROOT/model-input"
readonly MODEL_ROOT="$MODEL_INPUT/model-snapshot"
readonly RESOLVER_VENV="$WORK_ROOT/resolver-venv"
readonly RUNTIME_VENV="$WORK_ROOT/runtime-venv"
readonly WHEEL_ROOT="$RUN_DIR/wheels"
mkdir "$SOURCE_INPUT" "$TOOLGAP_INPUT" "$WHEEL_ROOT"
validate_seed_archive "$TOOLGAP_SEED_ARCHIVE" toolgap-source.git
tar -xzf "$TOOLGAP_SEED_ARCHIVE" -C "$TOOLGAP_INPUT"
readonly TOOLGAP_REPOSITORY="$TOOLGAP_INPUT/toolgap-source.git"
test "$(git -C "$TOOLGAP_REPOSITORY" rev-parse --is-bare-repository)" = true
git -C "$TOOLGAP_REPOSITORY" fsck --full >"$RUN_DIR/toolgap-seed-verify.log" 2>&1
{
  printf 'bare_repository=%s\n' "$TOOLGAP_REPOSITORY"
  printf 'fsck=passed\n'
  printf 'archive_sha256=%s\n' "$(sha256sum "$TOOLGAP_SEED_ARCHIVE" | awk '{print $1}')"
  printf 'archive_size_bytes=%s\n' "$(stat -c '%s' "$TOOLGAP_SEED_ARCHIVE")"
  printf 'commit=%s\n' "$(git -C "$REPO_ROOT" rev-parse HEAD)"
  printf 'tree=%s\n' "$(git -C "$REPO_ROOT" rev-parse 'HEAD^{tree}')"
} >>"$RUN_DIR/toolgap-seed-verify.log"
test "$(git -C "$TOOLGAP_REPOSITORY" cat-file -t "$(git -C "$REPO_ROOT" rev-parse HEAD)")" = commit
test "$(git -C "$TOOLGAP_REPOSITORY" rev-parse "$(git -C "$REPO_ROOT" rev-parse HEAD)^{tree}")" = \
  "$(git -C "$REPO_ROOT" rev-parse 'HEAD^{tree}')"
validate_seed_archive "$SOURCE_SEED_ARCHIVE" sglang-source.git
tar -xzf "$SOURCE_SEED_ARCHIVE" -C "$SOURCE_INPUT"
readonly SOURCE_REPOSITORY="$SOURCE_INPUT/sglang-source.git"
test "$(git -C "$SOURCE_REPOSITORY" rev-parse --is-bare-repository)" = true
git -C "$SOURCE_REPOSITORY" fsck --full
test "$(git -C "$SOURCE_REPOSITORY" cat-file -t "$BASE_COMMIT")" = commit
test "$(git -C "$SOURCE_REPOSITORY" rev-parse "$BASE_COMMIT^{tree}")" = "$BASE_TREE"
{
  printf 'bare_repository=%s\n' "$SOURCE_REPOSITORY"
  printf 'fsck=passed\n'
  printf 'base_commit=%s\n' "$BASE_COMMIT"
  printf 'base_tree=%s\n' "$BASE_TREE"
} >"$RUN_DIR/source-restore.log"
git clone --no-local "$SOURCE_REPOSITORY" "$TREATMENT"
git -C "$TREATMENT" checkout --detach "$BASE_COMMIT"
git -C "$TREATMENT" remote set-url origin "$SGLANG_REMOTE"
for patch in "$PATCH_0001" "$PATCH_0002"; do git -C "$TREATMENT" apply --check "$patch"; git -C "$TREATMENT" apply "$patch"; done
expected_paths="$(printf '%s\n' \
  python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py \
  python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py \
  python/sglang/srt/mem_cache/unified_cache/unified_tree_core_interface.py \
  python/sglang/srt/mem_cache/unified_radix_cache.py \
  test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py | LC_ALL=C sort)"
actual_paths="$(
  {
    git -C "$TREATMENT" diff --name-only "$BASE_COMMIT"
    git -C "$TREATMENT" ls-files --others --exclude-standard
  } | LC_ALL=C sort
)"
test "$actual_paths" = "$expected_paths"
git -C "$TREATMENT" add -A
git -C "$TREATMENT" -c user.name=ToolGap-G1 -c user.email=toolgap-g1@invalid \
  commit --no-gpg-sign -m "G1-PREFLIGHT-001 treatment" >>"$RUN_DIR/source-restore.log" 2>&1
test "$(git -C "$TREATMENT" rev-parse 'HEAD^')" = "$BASE_COMMIT"
test -z "$(git -C "$TREATMENT" status --porcelain)"

run_bounded "$PYTHON" "$MODEL_HELPER" prepare \
  --archive "$MODEL_SEED_ARCHIVE" \
  --archive-sha256 "$MODEL_SEED_SHA256" \
  --input-root "$MODEL_INPUT" --inventory "$MODEL_INVENTORY" \
  --receipt "$RUN_DIR/model-snapshot.json" >"$RUN_DIR/model-seed-prepare.log" 2>&1

"$PYTHON" -m venv "$RESOLVER_VENV"
run_bounded "$RESOLVER_VENV/bin/python" -m pip install --upgrade pip >"$RUN_DIR/build-install.log" 2>&1
run_bounded "$RESOLVER_VENV/bin/python" -m pip wheel --no-deps --wheel-dir "$WHEEL_ROOT" "$TREATMENT/python" >>"$RUN_DIR/build-install.log" 2>&1
wheels=("$WHEEL_ROOT"/sglang-*.whl)
test "${#wheels[@]}" = 1
readonly WHEEL="${wheels[0]}"
test -f "$WHEEL"
run_bounded "$RESOLVER_VENV/bin/python" -m pip install "$WHEEL" >>"$RUN_DIR/build-install.log" 2>&1
"$RESOLVER_VENV/bin/python" -m pip freeze | awk 'tolower($0) !~ /^sglang([ =@]|$)/' >"$RUN_DIR/dependency-lock.txt"
test -s "$RUN_DIR/dependency-lock.txt"
"$PYTHON" -m venv "$RUNTIME_VENV"
run_bounded "$RUNTIME_VENV/bin/python" -m pip install --upgrade pip >>"$RUN_DIR/build-install.log" 2>&1
run_bounded "$RUNTIME_VENV/bin/python" -m pip install --no-deps --report "$RUN_DIR/runtime-install-report.json" \
  -r "$RUN_DIR/dependency-lock.txt" "$WHEEL" >>"$RUN_DIR/build-install.log" 2>&1
"$RUNTIME_VENV/bin/python" -c '
import sys, torch, transformers
assert sys.version_info[:2] == (3, 12), sys.version
assert torch.__version__.split("+")[0] == "2.13.0", torch.__version__
assert torch.version.cuda == "13.0", torch.version.cuda
assert transformers.__version__ == "5.12.1", transformers.__version__
assert torch.cuda.is_available()
assert torch.cuda.device_count() == 1, torch.cuda.device_count()
assert "A10" in torch.cuda.get_device_name(0), torch.cuda.get_device_name(0)
' >>"$RUN_DIR/build-install.log" 2>&1
env -u PYTHONPATH "$RUNTIME_VENV/bin/python" "$PROVENANCE" \
  --source-root "$TREATMENT" --install-root "$RUNTIME_VENV" \
  --expected-interpreter "$RUNTIME_VENV/bin/python" \
  --output "$RUN_DIR/sglang-provenance.json"
"$PYTHON" - "$TREATMENT/test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py" "$RUN_DIR/test-module-provenance.json" <<'PY'
import hashlib, json, os, pathlib, sys
source, output = map(pathlib.Path, sys.argv[1:])
digest = hashlib.sha256(source.read_bytes()).hexdigest()
fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle:
    handle.write(json.dumps({"path": str(source.resolve()), "sha256": digest}, indent=2, sort_keys=True) + "\n")
os.chmod(output, 0o444)
PY
{
  printf 'HF_HUB_OFFLINE=1\n'
  printf 'TRANSFORMERS_OFFLINE=1\n'
  printf 'TOOLGAP_G1_MODEL_PATH=%q\n' "$MODEL_ROOT"
  printf 'TREATMENT=%q\n' "$TREATMENT"
  printf 'RUNTIME_PYTHON=%q\n' "$RUNTIME_VENV/bin/python"
} >"$RUN_DIR/runtime.env"
chmod 0444 "$RUN_DIR/runtime.env"
"$PYTHON" "$FINALIZE" render --template "$TEMPLATE" --repo-root "$REPO_ROOT" --output "$RUN_DIR/manifest.json"
(cd "$RUN_DIR" && sha256sum manifest.json >manifest.sha256)
chmod 0444 "$RUN_DIR/manifest.sha256"

PHASE="runtime"
run_bounded bash -c 'cd "$1" && env -u PYTHONPATH HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  TOOLGAP_G1_MODEL_PATH="$2" "$3" -m unittest \
  test.registered.scripted_runtime.test_toolgap_g1_forced_demote.TestG1RecordSchema' \
  _ "$TREATMENT" "$MODEL_ROOT" "$RUNTIME_VENV/bin/python" >"$RUN_DIR/schema.log" 2>&1
gpu_pids >"$RUN_DIR/smoke-gpu-pids-before.txt"
(
  cd "$TREATMENT"
  exec setsid env -u PYTHONPATH HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
    TOOLGAP_G1_MODEL_PATH="$MODEL_ROOT" "$RUNTIME_VENV/bin/python" -m unittest \
    test.registered.scripted_runtime.test_toolgap_g1_forced_demote.TestG1PreflightStartup.test_local_model_starts_without_runtime_script
) >"$RUN_DIR/smoke.log" 2>&1 &
current_pid="$!"
current_pgid="$(ps -o pgid= -p "$current_pid" | xargs)"
test -n "$current_pgid"
test "$current_pgid" = "$current_pid"
printf '%s\n' "$current_pid" >"$RUN_DIR/smoke.pid"
printf '%s\n' "$current_pgid" >"$RUN_DIR/smoke.pgid"
if wait_for_smoke; then smoke_status=0; else smoke_status=$?; fi
smoke_port="$($PYTHON - "$RUN_DIR/smoke.log" <<'PY'
import json, re, sys

records = []
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    try:
        record = json.loads(line)
    except json.JSONDecodeError:
        continue
    if isinstance(record, dict) and record.get("kind") == "G1_PREFLIGHT_SERVER_STARTED":
        records.append(record)
if len(records) != 1 or not isinstance(records[0].get("base_url"), str):
    raise ValueError("missing unique G1 preflight listener record")
match = re.fullmatch(r"http://127\.0\.0\.1:([1-9][0-9]{0,4})", records[0]["base_url"])
if not match:
    raise ValueError("invalid G1 preflight listener URL")
print(match.group(1))
PY
)"
verify_smoke_cleanup "$smoke_status"
"$PYTHON" "$FINALIZE" finish --run-dir "$RUN_DIR"
"$PYTHON" "$FINALIZE" verify --run-dir "$RUN_DIR"
trap - ERR HUP INT TERM
echo "PREFORMAL_RUNTIME_ADMISSION_COMPLETE: $RUN_DIR"
