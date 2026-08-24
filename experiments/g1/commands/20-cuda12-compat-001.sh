#!/usr/bin/env bash
# Run one sealed, no-action CUDA 12.8 compatibility attempt.
set -Eeuo pipefail

readonly BUNDLE_ID="CUDA12-COMPAT-001"
readonly LONG_COMMAND_TIMEOUT_SECONDS=1800
readonly RESTRICTED_SELECTOR="test.registered.scripted_runtime.test_toolgap_g1_forced_demote.TestG1PreflightStartup.test_local_model_starts_without_runtime_script"

REPO_ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd)"
ATTEMPT_ID="${CUDA12_COMPAT_ATTEMPT_ID:-}"
PYTHON="${CUDA12_COMPAT_PYTHON:-python3}"
RUN_DIR="${CUDA12_COMPAT_RUN_DIR:-$REPO_ROOT/experiments/g1/raw/cuda12-compat-001/$ATTEMPT_ID}"
WORK_ROOT="${CUDA12_COMPAT_WORK_ROOT:-/tmp/toolgap-cuda12-compat-001-$ATTEMPT_ID}"
SOURCE_SEED_ARCHIVE="${CUDA12_COMPAT_SOURCE_SEED_ARCHIVE:-}"
MODEL_SEED_ARCHIVE="${CUDA12_COMPAT_MODEL_SEED_ARCHIVE:-}"
TOOLGAP_SEED_ARCHIVE="${CUDA12_COMPAT_TOOLGAP_SEED_ARCHIVE:-}"
RUNTIME_WHEEL="${CUDA12_COMPAT_RUNTIME_WHEEL:-}"
RUNTIME_WHEEL_PROVENANCE="${CUDA12_COMPAT_RUNTIME_WHEEL_PROVENANCE:-}"
CUDA_WHEELHOUSE_ARCHIVE="${CUDA12_COMPAT_CUDA_WHEELHOUSE_ARCHIVE:-}"
INPUT_MANIFEST="${CUDA12_COMPAT_INPUT_MANIFEST:-}"
INPUT_OSS_RECEIPT="${CUDA12_COMPAT_INPUT_OSS_RECEIPT:-}"
BOOTSTRAP_RECEIPT="${CUDA12_COMPAT_BOOTSTRAP_RECEIPT:-}"
PYPI_INDEX_URL="${CUDA12_COMPAT_PYPI_INDEX_URL:-http://mirrors.cloud.aliyuncs.com/pypi/simple/}"
PHASE="host_identity"
current_pid=""
current_pgid=""
startup_port=""

readonly FINALIZE="$REPO_ROOT/experiments/g1/commands/cuda12_compat_001_finalize.py"
readonly BUNDLE_MANIFEST="$REPO_ROOT/experiments/g1/commands/cuda12_compat_001_bundle_manifest.py"
readonly MODEL_HELPER="$REPO_ROOT/experiments/g0/commands/g0_c_016_model_seed.py"
readonly PROVENANCE="$REPO_ROOT/experiments/g0/commands/g0_c_008_package_provenance.py"
readonly PIN="$REPO_ROOT/upstream/sglang/pin.cuda12-compat-001.toml"
readonly TEMPLATE="$REPO_ROOT/experiments/g1/manifest.cuda12-compat-001.template.json"
readonly SPEC="$REPO_ROOT/experiments/g1/SPEC.cuda12-compat-001.md"

require() {
  command -v "$1" >/dev/null || { echo "missing required command: $1" >&2; return 1; }
}

run_bounded() {
  timeout --signal=TERM --kill-after=30s "${LONG_COMMAND_TIMEOUT_SECONDS}s" "$@"
}

failure_terminal() {
  local exit_code="${1:-}"
  case "$PHASE" in
    host_identity|inputs|restore) printf '%s\n' BLOCKED_HOST_IDENTITY ;;
    resolver)
      if [[ -f "$RUN_DIR/resolver-install.log" ]] &&
          grep -Eiq '(connection (reset|refused|timed out)|connecttimeout|readtimeout|httpsconnectionpool|proxyerror|sslerror|temporary failure|name or service not known|network is unreachable|failed to establish a new connection|could not fetch url|http error [45][0-9]{2}|[45][0-9]{2} (client|server) error|timed out|timeout)' "$RUN_DIR/resolver-install.log"; then
        printf '%s\n' BLOCKED_DEPENDENCY_TRANSPORT
      else
        printf '%s\n' BLOCKED_DEPENDENCY_RESOLUTION
      fi
      ;;
    torch_cuda) printf '%s\n' RUNTIME_INCOMPATIBLE ;;
    compiler) printf '%s\n' TOOLKIT_COMPILER_FAILED ;;
    scope) printf '%s\n' INVALID_SCOPE ;;
    startup)
      if [[ -f "$RUN_DIR/restricted-startup.log" ]] &&
        grep -Eiq '(^|[^[:alpha:]])(jit|nvrtc|nvcc)([^[:alpha:]]|$)|cuda[^[:alpha:]]*(compile|compiler)' "$RUN_DIR/restricted-startup.log"; then
        printf '%s\n' SGLANG_STARTUP_JIT_FAILED
      else
        printf '%s\n' SGLANG_STARTUP_FAILED_OTHER
      fi
      ;;
    *) printf '%s\n' BLOCKED_HOST_IDENTITY ;;
  esac
}

capture_environment() {
  {
    printf 'captured_at=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    printf 'uname='; uname -a || true
    if [[ -f /etc/os-release ]]; then cat /etc/os-release || true; else printf 'os_release=absent\n'; fi
    printf 'python='; "$PYTHON" --version || true
    printf 'nvidia_smi_path='; command -v nvidia-smi || true
    nvidia-smi -L || true
    nvidia-smi --query-gpu=name,uuid,memory.total,driver_version --format=csv,noheader || true
    printf 'nvcc_path='; command -v nvcc || true
    nvcc --version || true
    if [[ -x /usr/local/cuda-12.8/bin/nvcc ]]; then /usr/local/cuda-12.8/bin/nvcc --version || true; fi
  } >"$RUN_DIR/environment.txt" 2>&1
}

gpu_pids() {
  nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null |
    awk 'NF && $1 ~ /^[0-9]+$/ {print $1}' | LC_ALL=C sort -n -u
}

target_listener_rows() {
  if [[ -n "$startup_port" ]]; then
    ss -ltnH | awk -v port="$startup_port" '$4 ~ (":" port "$") {print}'
  fi
}

process_group_members() {
  local pgid="$1"
  ps -eo pid=,pgid=,stat=,args= |
    awk -v target="$pgid" '$2 == target && $3 !~ /^Z/ {sub(/^[[:space:]]+/, ""); print}'
}

emergency_cleanup() {
  if [[ -n "$current_pgid" && "$current_pgid" = "$current_pid" ]]; then
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

seal_failure_or_error() {
  local terminal="$1"
  local phase="$2"
  local status="$3"
  if ! "$PYTHON" "$FINALIZE" fail --run-dir "$RUN_DIR" \
    --status "$terminal" --phase "$phase" --exit-code "$status"; then
    printf 'CUDA12-COMPAT-001 terminal sealing failed for %s\n' "$RUN_DIR" >&2
    return 70
  fi
}

fail() {
  local status="$1"
  local terminal
  trap - ERR HUP INT TERM
  emergency_cleanup
  if [[ -d "$RUN_DIR" && -f "$RUN_DIR/attempt-context.json" && -f "$RUN_DIR/environment.txt" && ! -e "$RUN_DIR/execution-status.json" ]]; then
    terminal="$(failure_terminal "$status")"
    if ! seal_failure_or_error "$terminal" "$PHASE" "$status"; then
      exit 70
    fi
  elif [[ -d "$RUN_DIR" && ! -e "$RUN_DIR/execution-status.json" ]]; then
    printf 'CUDA12-COMPAT-001 terminal sealing preconditions are missing for %s\n' "$RUN_DIR" >&2
    exit 70
  fi
  exit "$status"
}

wait_for_startup_pgid() {
  local deadline=$((SECONDS + 10))
  local observed
  while kill -0 "$current_pid" 2>/dev/null; do
    observed="$(ps -o pgid= -p "$current_pid" | xargs || true)"
    if [[ "$observed" = "$current_pid" ]]; then
      current_pgid="$observed"
      return 0
    fi
    if (( SECONDS >= deadline )); then return 1; fi
    sleep 1
  done
  return 1
}

wait_for_startup() {
  local deadline=$((SECONDS + LONG_COMMAND_TIMEOUT_SECONDS + 35))
  local state
  while kill -0 "$current_pid" 2>/dev/null; do
    state="$(ps -o stat= -p "$current_pid" | xargs || true)"
    if [[ "$state" == Z* ]]; then break; fi
    if (( SECONDS >= deadline )); then return 124; fi
    sleep 1
  done
  wait "$current_pid"
}

read_startup_listener_port() {
  local required="$1"
  "$PYTHON" - "$RUN_DIR/restricted-startup.log" "$required" <<'PY'
import json
import re
import sys

path = sys.argv[1]
required = sys.argv[2] == "required"
records = []
for line in open(path, encoding="utf-8", errors="replace"):
    try:
        record = json.loads(line)
    except json.JSONDecodeError:
        continue
    if isinstance(record, dict) and record.get("kind") == "G1_PREFLIGHT_SERVER_STARTED":
        records.append(record)
if len(records) > 1:
    raise ValueError("restricted startup emitted multiple listener records")
if not records:
    if required:
        raise ValueError("missing restricted startup listener record")
    raise SystemExit(0)
record = records[0]
if not isinstance(record.get("base_url"), str):
    raise ValueError("restricted startup listener record omits base_url")
match = re.fullmatch(r"http://127\.0\.0\.1:([1-9][0-9]{0,4})", record["base_url"])
if not match:
    raise ValueError("invalid restricted startup listener URL")
print(match.group(1))
PY
}

verify_startup_cleanup() {
  local process_status="$1"
  local passed=true
  local deadline=$((SECONDS + 60))
  gpu_pids >"$RUN_DIR/startup-gpu-pids-during.txt"
  comm -13 "$RUN_DIR/startup-gpu-pids-before.txt" "$RUN_DIR/startup-gpu-pids-during.txt" \
    >"$RUN_DIR/startup-gpu-pids-attributable.txt"
  if [[ "$process_status" != 0 ]]; then passed=false; fi
  if kill -0 "$current_pid" 2>/dev/null; then
    passed=false
    kill -TERM -- "-$current_pgid" 2>/dev/null || true
  fi
  while true; do
    process_group_members "$current_pgid" >"$RUN_DIR/startup-process-group-after.txt"
    target_listener_rows >"$RUN_DIR/startup-listeners-after.txt"
    gpu_pids >"$RUN_DIR/startup-gpu-pids-after.txt"
    comm -12 "$RUN_DIR/startup-gpu-pids-attributable.txt" "$RUN_DIR/startup-gpu-pids-after.txt" \
      >"$RUN_DIR/startup-gpu-pids-leaked.txt"
    if [[ ! -s "$RUN_DIR/startup-process-group-after.txt" &&
      ! -s "$RUN_DIR/startup-gpu-pids-leaked.txt" &&
      ! -s "$RUN_DIR/startup-listeners-after.txt" ]]; then
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
    printf 'startup_pid=%s\n' "$current_pid"
    printf 'startup_pgid=%s\n' "$current_pgid"
    printf 'startup_exit_status=%s\n' "$process_status"
  } >"$RUN_DIR/shutdown.log"
  current_pid=""
  current_pgid=""
  [[ "$passed" == true ]]
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
            pure.is_absolute() or ".." in pure.parts or not pure.parts
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
  echo "set CUDA12_COMPAT_ATTEMPT_ID to A-Z a-z 0-9 . _ -" >&2
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
trap 'fail "$?"' ERR
trap 'fail 129' HUP
trap 'fail 130' INT
trap 'fail 143' TERM

"$PYTHON" - "$REPO_ROOT" "$RUN_DIR/attempt-context.json" "$ATTEMPT_ID" <<'PY'
import hashlib, json, os, pathlib, subprocess, sys
from datetime import datetime, timezone

repo = pathlib.Path(sys.argv[1]).resolve()
spec = repo / "experiments/g1/SPEC.cuda12-compat-001.md"
git = lambda *args: subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()
document = {
    "attempt_id": sys.argv[3],
    "bundle_id": "CUDA12-COMPAT-001",
    "claim_state": "roadmap",
    "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "gate": "G1",
    "gate_decision": "N/A",
    "spec_path": "experiments/g1/SPEC.cuda12-compat-001.md",
    "spec_sha256": hashlib.sha256(spec.read_bytes()).hexdigest(),
    "toolgap_commit": git("rev-parse", "HEAD"),
    "toolgap_tracked_clean": not bool(git("status", "--porcelain", "--untracked-files=no")),
    "toolgap_tree": git("rev-parse", "HEAD^{tree}"),
}
fd = os.open(sys.argv[2], os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle:
    handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(sys.argv[2], 0o444)
PY

# Capture substrate readbacks before any identity assertion so every sealed
# terminal retains diagnostic host evidence, including a rejected image.
capture_environment

config="$("$PYTHON" - "$PIN" <<'PY'
import pathlib, re, shlex, sys, tomllib

pin = tomllib.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
if pin.get("bundle") != {
    "id": "CUDA12-COMPAT-001",
    "kind": "preformal_cuda12_compatibility_probe",
    "claim_state": "roadmap",
    "gate_decision": "N/A: this bundle cannot produce a G1 Gate result",
}:
    raise ValueError("wrong compatibility pin identity")
sglang = pin.get("sglang")
model = pin.get("model")
envelope = pin.get("capability_envelope")
packaging = pin.get("cuda12_packaging")
runtime_wheel = pin.get("runtime_wheel")
ordinary_transport = pin.get("ordinary_dependency_transport")
if not all(isinstance(value, dict) for value in (sglang, model, envelope, packaging, runtime_wheel, ordinary_transport)):
    raise ValueError("compatibility pin is incomplete")
assert isinstance(sglang, dict) and isinstance(model, dict)
assert isinstance(envelope, dict) and isinstance(packaging, dict) and isinstance(runtime_wheel, dict) and isinstance(ordinary_transport, dict)
for key, length in (("base_commit", 40), ("base_tree", 40), ("source_seed_sha256", 64)):
    if not isinstance(sglang.get(key), str) or not re.fullmatch(rf"[0-9a-f]{{{length}}}", sglang[key]):
        raise ValueError(f"invalid SGLang {key}")
patches = sglang.get("patches")
if not isinstance(patches, list) or len(patches) != 3:
    raise ValueError("compatibility pin must contain three patches")
for index, patch in enumerate(patches, start=1):
    if not isinstance(patch, dict) or set(patch) != {"path", "sha256", "changed_paths"}:
        raise ValueError(f"invalid patch entry {index}")
    if not isinstance(patch["path"], str) or pathlib.PurePosixPath(patch["path"]).is_absolute() or ".." in pathlib.PurePosixPath(patch["path"]).parts:
        raise ValueError(f"unsafe patch path {index}")
    if not isinstance(patch["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", patch["sha256"]):
        raise ValueError(f"invalid patch hash {index}")
    if not isinstance(patch["changed_paths"], list) or not patch["changed_paths"]:
        raise ValueError(f"invalid changed paths {index}")
required = {
    "os", "provider_image", "gpu", "nvidia_driver", "system_cuda", "cuda_home", "python", "runtime"
}
if set(envelope) != required or envelope["os"] != "Linux x86_64" or envelope["system_cuda"] != "12.8":
    raise ValueError("unexpected host envelope")
required_packaging = {
    "source_evidence", "metadata_patch", "torch_version", "torchvision_version", "torchaudio_version",
    "torch_index_url", "deep_ep_version", "deep_ep_index_url", "sglang_kernel_version",
    "sglang_kernel_wheel_template", "deep_gemm_version", "deep_gemm_wheel_template",
    "full_docker_reproduction",
}
if set(packaging) != required_packaging or packaging["full_docker_reproduction"] is not False:
    raise ValueError("unexpected CUDA 12 packaging pin")
if runtime_wheel != {
    "provenance_identity": "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite",
    "source_rebuild": False,
    "payload": "prebuilt G0 treatment runtime payload; only CUDA12 wheel METADATA and RECORD are rewritten",
    "base_wheel_attempt": "G0-C-011 attempt 005 treatment",
    "base_wheel_filename": "sglang-0.0.0.dev2+g734a8e921-cp312-cp312-linux_x86_64.whl",
    "base_wheel_sha256": "0874acca7b27e45ae39606eb12ee24a5f4cb17cd3791bb60fdccb95c332bf59e",
}:
    raise ValueError("unexpected runtime-wheel pin")
if ordinary_transport != {
    "index_url": "http://mirrors.cloud.aliyuncs.com/pypi/simple/",
    "trusted_host": "mirrors.cloud.aliyuncs.com",
    "evidence": "G0-C-011 attempt 005 resolved ordinary dependencies through this provider-internal mirror",
}:
    raise ValueError("unexpected ordinary-dependency transport pin")
if not isinstance(model.get("inventory"), str) or model.get("local_only") is not True:
    raise ValueError("model must be pinned local-only")
values = {
    "BASE_COMMIT": sglang["base_commit"],
    "BASE_TREE": sglang["base_tree"],
    "SGLANG_REMOTE": sglang["remote"],
    "SOURCE_SEED_SHA256": sglang["source_seed_sha256"],
    "MODEL_INVENTORY_REL": model["inventory"],
    "CUDA_HOME_EXPECTED": envelope["cuda_home"],
    "EXPECTED_DRIVER": envelope["nvidia_driver"],
    "TORCH_VERSION": packaging["torch_version"],
    "TORCHVISION_VERSION": packaging["torchvision_version"],
    "TORCHAUDIO_VERSION": packaging["torchaudio_version"],
    "DEEP_EP_VERSION": packaging["deep_ep_version"],
    "SGLANG_KERNEL_VERSION": packaging["sglang_kernel_version"],
    "DEEP_GEMM_VERSION": packaging["deep_gemm_version"],
    "RUNTIME_WHEEL_PROVENANCE_ID": runtime_wheel["provenance_identity"],
    "PYPI_INDEX_EXPECTED": ordinary_transport["index_url"],
    "PYPI_TRUSTED_HOST": ordinary_transport["trusted_host"],
}
for key, value in values.items():
    if not isinstance(value, str) or not value:
        raise ValueError(f"invalid pin value: {key}")
    print(f"{key}={shlex.quote(value)}")
for index, patch in enumerate(patches, start=1):
    print(f"PATCH_{index}_PATH={shlex.quote(patch['path'])}")
    print(f"PATCH_{index}_SHA256={shlex.quote(patch['sha256'])}")
print("EXPECTED_CHANGED_PATHS=" + shlex.quote("\n".join(sorted({path for patch in patches for path in patch["changed_paths"]}))))
PY
)"
eval "$config"
readonly BASE_COMMIT BASE_TREE SGLANG_REMOTE SOURCE_SEED_SHA256 MODEL_INVENTORY_REL
readonly CUDA_HOME_EXPECTED EXPECTED_DRIVER TORCH_VERSION TORCHVISION_VERSION TORCHAUDIO_VERSION
readonly DEEP_EP_VERSION SGLANG_KERNEL_VERSION DEEP_GEMM_VERSION
readonly RUNTIME_WHEEL_PROVENANCE_ID PYPI_INDEX_EXPECTED PYPI_TRUSTED_HOST
readonly PATCH_1_PATH PATCH_1_SHA256 PATCH_2_PATH PATCH_2_SHA256 PATCH_3_PATH PATCH_3_SHA256
readonly EXPECTED_CHANGED_PATHS
readonly CUDA_HOME="${CUDA12_COMPAT_CUDA_HOME:-$CUDA_HOME_EXPECTED}"
export CUDA_HOME
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
  echo "requires Linux x86_64" >&2
  exit 78
fi
if [[ ! -f /etc/os-release ]] || ! grep -Eq '^ID=ubuntu$' /etc/os-release ||
  ! grep -Eq '^VERSION_ID="?24\.04"?$' /etc/os-release; then
  echo "requires Alibaba Cloud Ubuntu 24.04 GPU image" >&2
  exit 78
fi
for command in curl git nvidia-smi nvcc sha256sum ss tar timeout; do require "$command"; done
[[ "$CUDA_HOME" = "$CUDA_HOME_EXPECTED" && -x "$CUDA_HOME/bin/nvcc" ]]
"$CUDA_HOME/bin/nvcc" --version | grep -Eq 'release 12\.8([,.]|$)'
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
gpu_driver="$(xargs <<<"$gpu_driver")"
readonly gpu_name gpu_memory gpu_driver
[[ "$gpu_driver" = "$EXPECTED_DRIVER" ]]
[[ "$gpu_name" = "NVIDIA A10" ]]
(( gpu_memory >= 22000 && gpu_memory <= 25000 ))

PHASE="inputs"
[[ "$SOURCE_SEED_ARCHIVE" = /* && "$MODEL_SEED_ARCHIVE" = /* && "$TOOLGAP_SEED_ARCHIVE" = /* && "$RUNTIME_WHEEL" = /* && "$RUNTIME_WHEEL_PROVENANCE" = /* && "$CUDA_WHEELHOUSE_ARCHIVE" = /* && "$INPUT_MANIFEST" = /* && "$INPUT_OSS_RECEIPT" = /* && "$BOOTSTRAP_RECEIPT" = /* ]]
[[ -f "$SOURCE_SEED_ARCHIVE" && -f "$MODEL_SEED_ARCHIVE" && -f "$TOOLGAP_SEED_ARCHIVE" && -f "$RUNTIME_WHEEL" && -f "$RUNTIME_WHEEL_PROVENANCE" && -f "$CUDA_WHEELHOUSE_ARCHIVE" && -f "$INPUT_MANIFEST" && -f "$INPUT_OSS_RECEIPT" && -f "$BOOTSTRAP_RECEIPT" ]]
[[ "$PYPI_INDEX_URL" = "$PYPI_INDEX_EXPECTED" ]]
"$PYTHON" "$BUNDLE_MANIFEST" verify --repo-root "$REPO_ROOT" \
  --manifest "$INPUT_MANIFEST" --toolgap-seed "$TOOLGAP_SEED_ARCHIVE" \
  --sglang-seed "$SOURCE_SEED_ARCHIVE" --model-snapshot "$MODEL_SEED_ARCHIVE" \
  --runtime-wheel "$RUNTIME_WHEEL" --runtime-wheel-provenance "$RUNTIME_WHEEL_PROVENANCE" \
  --cuda-wheelhouse "$CUDA_WHEELHOUSE_ARCHIVE" \
  >"$RUN_DIR/input-manifest-verify.log" 2>&1
"$PYTHON" - "$INPUT_OSS_RECEIPT" "$INPUT_MANIFEST" "$SOURCE_SEED_ARCHIVE" \
  "$MODEL_SEED_ARCHIVE" "$TOOLGAP_SEED_ARCHIVE" "$RUNTIME_WHEEL" \
  "$RUNTIME_WHEEL_PROVENANCE" "$CUDA_WHEELHOUSE_ARCHIVE" "$REPO_ROOT" <<'PY'
import hashlib
import json
import pathlib
import re
import sys

(
    receipt_path,
    manifest_path,
    source_seed,
    model_seed,
    toolgap_seed,
    runtime_wheel,
    runtime_provenance,
    cuda_wheelhouse,
    repo_root,
) = map(pathlib.Path, sys.argv[1:])
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
archives = manifest["archives"]
expected_local = {
    "input_manifest": manifest_path,
    "sglang_source_seed": source_seed,
    "model_snapshot": model_seed,
    "toolgap_source_seed": toolgap_seed,
    "runtime_wheel": runtime_wheel,
    "runtime_wheel_provenance": runtime_provenance,
    "cuda_wheelhouse": cuda_wheelhouse,
    "bootstrap": repo_root / "experiments/g1/commands/00-cuda12-compat-001-bootstrap.sh",
    "prereqs": repo_root / "experiments/g1/commands/19-cuda12-compat-001-project-prereqs.sh",
}
if set(receipt) != {"schema_version", "identity", "objects"}:
    raise ValueError("input OSS receipt fields differ")
if receipt["schema_version"] != 1 or receipt["identity"] != manifest["identity"]:
    raise ValueError("input OSS receipt identity differs")
objects = receipt["objects"]
if not isinstance(objects, dict) or set(objects) != set(expected_local):
    raise ValueError("input OSS receipt object set differs")

def file_binding(path):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size

prefixes = set()
for label, local_path in expected_local.items():
    object_record = objects[label]
    if not isinstance(object_record, dict) or set(object_record) != {
        "object_uri", "sha256", "size_bytes", "version_id"
    }:
        raise ValueError(f"invalid input OSS receipt object: {label}")
    uri = object_record["object_uri"]
    version = object_record["version_id"]
    if (
        not isinstance(uri, str)
        or not re.fullmatch(r"oss://[^/]+/.+", uri)
        or not isinstance(version, str)
        or not version
        or not isinstance(object_record["sha256"], str)
        or not re.fullmatch(r"[0-9a-f]{64}", object_record["sha256"])
        or not isinstance(object_record["size_bytes"], int)
        or object_record["size_bytes"] < 1
    ):
        raise ValueError(f"invalid input OSS receipt binding: {label}")
    if uri.rsplit("/", 1)[1] != local_path.name:
        raise ValueError(f"input OSS receipt filename differs: {label}")
    prefixes.add(uri.rsplit("/", 1)[0])
    actual_sha256, actual_size = file_binding(local_path)
    if (
        actual_sha256 != object_record["sha256"]
        or actual_size != object_record["size_bytes"]
    ):
        raise ValueError(f"input OSS receipt local binding differs: {label}")
if len(prefixes) != 1:
    raise ValueError("input OSS receipt objects do not share a prefix")
PY
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
copy_immutable "$INPUT_OSS_RECEIPT" "$RUN_DIR/input-oss-receipt.json"
copy_immutable "$BOOTSTRAP_RECEIPT" "$RUN_DIR/bootstrap-receipt.json"
copy_immutable "$RUNTIME_WHEEL" "$RUN_DIR/runtime-wheel.whl"
copy_immutable "$RUNTIME_WHEEL_PROVENANCE" "$RUN_DIR/runtime-wheel-provenance.json"
[[ "$(sha256sum "$SOURCE_SEED_ARCHIVE" | awk '{print $1}')" = "$SOURCE_SEED_SHA256" ]]
for index in 1 2 3; do
  patch_path_var="PATCH_${index}_PATH"
  patch_sha_var="PATCH_${index}_SHA256"
  patch_path="$REPO_ROOT/${!patch_path_var}"
  [[ -f "$patch_path" && "$(sha256sum "$patch_path" | awk '{print $1}')" = "${!patch_sha_var}" ]]
done

{
  date -u '+%Y-%m-%dT%H:%M:%SZ'
  printf 'alibaba_image_id=%s\n' "$IMAGE_ID"
  printf 'alibaba_instance_type=%s\n' "$INSTANCE_TYPE"
  printf 'alibaba_region_id=%s\n' "$REGION_ID"
  printf 'alibaba_zone_id=%s\n' "$ZONE_ID"
  "$CUDA_HOME/bin/nvcc" --version
  "$PYTHON" --version
  git --version
  printf 'ordinary_pypi_index=%s\n' "$PYPI_INDEX_URL"
} >>"$RUN_DIR/environment.txt"
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
readonly RUNTIME_VENV="$WORK_ROOT/runtime-venv"
readonly CUDA_WHEELHOUSE_ROOT="$WORK_ROOT/cuda-wheelhouse"
mkdir "$SOURCE_INPUT" "$TOOLGAP_INPUT"

# The staged G0 wheel is the only SGLang runtime build input. Its sidecar
# binds the unmodified Python payload to the three-patch tree and proves that
# only the four CUDA12 METADATA substitutions were made. The separate minimal
# wheelhouse keeps CUDA wheels off the known-unreliable GitHub/SGLang/PyTorch
# transport path; ordinary PyPI dependencies remain intentionally outside it.
"$PYTHON" - "$RUNTIME_WHEEL" "$RUNTIME_WHEEL_PROVENANCE" \
  "$INPUT_MANIFEST" "$PIN" "$CUDA_WHEELHOUSE_ARCHIVE" "$CUDA_WHEELHOUSE_ROOT" \
  "$RUN_DIR/runtime-wheel-validation.json" "$RUN_DIR/cuda-wheelhouse-validation.json" <<'PY'
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys
import tarfile
import zipfile

wheel_path, provenance_path, manifest_path, pin_path, wheelhouse_archive, wheelhouse_root, wheel_output, wheelhouse_output = map(pathlib.Path, sys.argv[1:])
top_level = "cuda-wheelhouse"
expected_rewrites = (
    ("cuda-python>=13.0", "cuda-python>=12,<13"),
    ("flashinfer_python[cu13]", "flashinfer_python[cu12]"),
    ("humming-kernels[cu13]==0.1.10", "humming-kernels[cu12]==0.1.10"),
    ("nvidia-cutlass-dsl[cu13]==4.6.2", "nvidia-cutlass-dsl==4.6.2"),
)

def digest_path(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()

def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()

def write_exclusive(path, value):
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.chmod(path, 0o444)

def normal(name):
    return re.sub(r"[-_.]+", "-", name).lower()

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
pin = __import__("tomllib").loads(pin_path.read_text(encoding="utf-8"))
archives = manifest.get("archives")
required = {
    "cuda_wheelhouse", "model_snapshot", "runtime_wheel",
    "runtime_wheel_provenance", "sglang_source_seed", "toolgap_source_seed",
}
if not isinstance(archives, dict) or set(archives) != required:
    raise ValueError("input manifest archive set differs")

def verify_staged(label, path):
    entry = archives[label]
    if (
        not isinstance(entry, dict)
        or path.name != entry.get("path")
        or path.stat().st_size != entry.get("size_bytes")
        or digest_path(path) != entry.get("sha256")
    ):
        raise ValueError(f"staged {label} differs from input manifest")

verify_staged("runtime_wheel", wheel_path)
verify_staged("runtime_wheel_provenance", provenance_path)
verify_staged("cuda_wheelhouse", wheelhouse_archive)
runtime_pin = pin.get("runtime_wheel")
if not isinstance(runtime_pin, dict):
    raise ValueError("runtime-wheel pin is absent")
provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
output = provenance.get("output_wheel")
if (
    provenance.get("identity") != runtime_pin.get("provenance_identity")
    or provenance.get("source_rebuild", {}).get("performed") is not False
    or not isinstance(output, dict)
    or output.get("sha256") != digest_path(wheel_path)
    or output.get("size_bytes") != wheel_path.stat().st_size
):
    raise ValueError("runtime-wheel provenance does not bind the staged wheel")
base = provenance.get("base_wheel")
if (
    not isinstance(base, dict)
    or base.get("filename") != runtime_pin.get("base_wheel_filename")
    or base.get("sha256") != runtime_pin.get("base_wheel_sha256")
):
    raise ValueError("runtime-wheel provenance does not bind the pinned G0 base wheel")
pinned_patches = pin.get("sglang", {}).get("patches")
observed_patches = provenance.get("patches")
if not isinstance(pinned_patches, list) or not isinstance(observed_patches, list) or len(pinned_patches) != 3 or len(observed_patches) != 3:
    raise ValueError("runtime-wheel provenance patch set differs")
for label, observed, expected in zip(("patch_one", "patch_two", "patch_three"), observed_patches, pinned_patches):
    if not isinstance(observed, dict) or observed.get("label") != label or observed.get("sha256") != expected.get("sha256"):
        raise ValueError("runtime-wheel provenance patch hash differs")
with zipfile.ZipFile(wheel_path) as archive:
    metadata_paths = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
    if len(metadata_paths) != 1:
        raise ValueError("runtime wheel must contain exactly one METADATA file")
    metadata = archive.read(metadata_paths[0])
for before, after in expected_rewrites:
    if metadata.count(before.encode("ascii")) != 0 or metadata.count(after.encode("ascii")) != 1:
        raise ValueError("runtime wheel does not contain exactly the four CUDA12 metadata rewrites")
rewrite = provenance.get("metadata_rewrite", {}).get("exact_substitutions")
if rewrite != [
    {"from": before, "to": after, "input_occurrences": 1, "output_occurrences": 1}
    for before, after in expected_rewrites
]:
    raise ValueError("runtime-wheel provenance metadata rewrite differs")
write_exclusive(wheel_output, {
    "metadata_path": metadata_paths[0],
    "metadata_sha256": digest_bytes(metadata),
    "runtime_wheel_sha256": digest_path(wheel_path),
    "runtime_wheel_size_bytes": wheel_path.stat().st_size,
    "source_rebuild": False,
    "provenance_identity": runtime_pin["provenance_identity"],
})

packaging = pin.get("cuda12_packaging")
if not isinstance(packaging, dict) or wheelhouse_root.exists():
    raise ValueError("unexpected CUDA wheelhouse destination or pin")
expected_wheels = {
    "sglang_kernel": ("sglang-kernel", f"{packaging['sglang_kernel_version']}+cu129"),
    "sgl_deep_ep": ("sgl-deep-ep", f"{packaging['deep_ep_version']}+cu129"),
    "sgl_deep_gemm": ("sgl-deep-gemm", f"{packaging['deep_gemm_version']}+cu129"),
    "torch": ("torch", f"{packaging['torch_version']}+cu129"),
    "torchvision": ("torchvision", f"{packaging['torchvision_version']}+cu129"),
    "torchaudio": ("torchaudio", f"{packaging['torchaudio_version']}+cu129"),
}
wheelhouse_root.mkdir(mode=0o755)
members = {}
seen = set()
with tarfile.open(wheelhouse_archive, "r:*") as archive:
    for member in archive.getmembers():
        pure = pathlib.PurePosixPath(member.name)
        member_name = member.name.rstrip("/")
        if (
            pure.is_absolute() or ".." in pure.parts or not pure.parts
            or pure.parts[0] != top_level or member_name in seen
            or not (member.isdir() or member.isfile())
        ):
            raise ValueError(f"unsafe CUDA wheelhouse member: {member.name}")
        seen.add(member_name)
        if member.isfile():
            if len(pure.parts) != 2:
                raise ValueError(f"nested CUDA wheelhouse member: {member.name}")
            reader = archive.extractfile(member)
            if reader is None:
                raise ValueError(f"unreadable CUDA wheelhouse member: {member.name}")
            destination = wheelhouse_root / pure.name
            with reader, destination.open("xb") as output:
                shutil.copyfileobj(reader, output, length=1024 * 1024)
            os.chmod(destination, 0o444)
            members[member.name] = destination
index_path = f"{top_level}/wheelhouse-index.json"
if index_path not in members:
    raise ValueError("CUDA wheelhouse omits wheelhouse-index.json")
index_bytes = members[index_path].read_bytes()
index = json.loads(index_bytes.decode("utf-8"))
if not isinstance(index, dict) or set(index) != {"schema_version", "wheels"} or index["schema_version"] != 1:
    raise ValueError("CUDA wheelhouse index schema differs")
wheels = index["wheels"]
if not isinstance(wheels, dict) or set(wheels) != set(expected_wheels):
    raise ValueError("CUDA wheelhouse package set differs")
expected_member_names = {index_path}
for label, (expected_name, expected_version) in expected_wheels.items():
    entry = wheels[label]
    if (
        not isinstance(entry, dict) or set(entry) != {"path", "sha256", "size_bytes"}
        or not isinstance(entry.get("path"), str)
        or pathlib.PurePosixPath(entry["path"]).name != entry["path"]
        or not entry["path"].endswith(".whl")
    ):
        raise ValueError(f"invalid CUDA wheelhouse entry: {label}")
    member_name = f"{top_level}/{entry['path']}"
    expected_member_names.add(member_name)
    payload = members.get(member_name)
    if (
        payload is None
        or payload.stat().st_size != entry.get("size_bytes")
        or digest_path(payload) != entry.get("sha256")
    ):
        raise ValueError(f"CUDA wheelhouse index does not bind {label}")
    with zipfile.ZipFile(payload) as archive:
        metadata_paths = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(metadata_paths) != 1:
            raise ValueError(f"CUDA wheelhouse {label} metadata differs")
        text = archive.read(metadata_paths[0]).decode("utf-8")
    headers = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            if key in {"Name", "Version"} and key not in headers:
                headers[key] = value.strip()
    if normal(headers.get("Name", "")) != normal(expected_name) or headers.get("Version") != expected_version:
        raise ValueError(f"CUDA wheelhouse package identity differs: {label}")
if set(members) != expected_member_names:
    raise ValueError("CUDA wheelhouse contains files outside its six-package boundary")
write_exclusive(wheelhouse_output, {
    "archive_path": str(wheelhouse_archive.resolve()),
    "archive_sha256": digest_path(wheelhouse_archive),
    "archive_size_bytes": wheelhouse_archive.stat().st_size,
    "index_sha256": digest_bytes(index_bytes),
    "wheels": wheels,
})
PY
copy_immutable "$CUDA_WHEELHOUSE_ROOT/wheelhouse-index.json" "$RUN_DIR/cuda-wheelhouse-index.json"

validate_seed_archive "$TOOLGAP_SEED_ARCHIVE" toolgap-source.git
tar --no-same-owner -xzf "$TOOLGAP_SEED_ARCHIVE" -C "$TOOLGAP_INPUT"
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

PHASE="restore"
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
  printf 'patch_1=%s\n' "$PATCH_1_PATH"
  printf 'patch_2=%s\n' "$PATCH_2_PATH"
  printf 'patch_3=%s\n' "$PATCH_3_PATH"
} >"$RUN_DIR/source-restore.log"
git clone --no-local "$SOURCE_REPOSITORY" "$TREATMENT"
git -C "$TREATMENT" checkout --detach "$BASE_COMMIT"
git -C "$TREATMENT" remote set-url origin "$SGLANG_REMOTE"
for index in 1 2 3; do
  patch_path_var="PATCH_${index}_PATH"
  patch_path="$REPO_ROOT/${!patch_path_var}"
  git -C "$TREATMENT" apply --check "$patch_path"
  git -C "$TREATMENT" apply "$patch_path"
done
actual_paths="$(
  {
    git -C "$TREATMENT" diff --name-only "$BASE_COMMIT"
    git -C "$TREATMENT" ls-files --others --exclude-standard
  } | LC_ALL=C sort
)"
test "$actual_paths" = "$EXPECTED_CHANGED_PATHS"
git -C "$TREATMENT" add -A
git -C "$TREATMENT" -c user.name=ToolGap-CUDA12 -c user.email=toolgap-cuda12@invalid \
  commit --no-gpg-sign -m "CUDA12-COMPAT-001 treatment" >>"$RUN_DIR/source-restore.log" 2>&1
test "$(git -C "$TREATMENT" rev-parse 'HEAD^')" = "$BASE_COMMIT"
test -z "$(git -C "$TREATMENT" status --porcelain)"

run_bounded "$PYTHON" "$MODEL_HELPER" prepare \
  --archive "$MODEL_SEED_ARCHIVE" --archive-sha256 "$MODEL_SEED_SHA256" \
  --input-root "$MODEL_INPUT" --inventory "$REPO_ROOT/$MODEL_INVENTORY_REL" \
  --receipt "$RUN_DIR/model-snapshot.json" >"$RUN_DIR/model-seed-prepare.log" 2>&1

PHASE="resolver"
"$PYTHON" -m venv "$RUNTIME_VENV"
run_bounded "$RUNTIME_VENV/bin/python" -m pip install --only-binary=:all: \
  --index-url "$PYPI_INDEX_URL" --trusted-host "$PYPI_TRUSTED_HOST" --upgrade pip >"$RUN_DIR/resolver-install.log" 2>&1
mapfile -t CUDA_WHEEL_FILES < <("$PYTHON" - "$RUN_DIR/cuda-wheelhouse-index.json" "$CUDA_WHEELHOUSE_ROOT" <<'PY'
import json
import pathlib
import sys

index, root = map(pathlib.Path, sys.argv[1:])
document = json.loads(index.read_text(encoding="utf-8"))
for label in ("sglang_kernel", "sgl_deep_ep", "sgl_deep_gemm", "torch", "torchvision", "torchaudio"):
    print(root / document["wheels"][label]["path"])
PY
)
test "${#CUDA_WHEEL_FILES[@]}" = 6
# CUDA-specific package artifacts are deliberately local-only. This command
# names no GitHub, SGLang, or PyTorch index; their runtime dependencies may
# resolve only through the G0-proven provider-internal ordinary-dependency mirror.
run_bounded "$RUNTIME_VENV/bin/python" -m pip install --only-binary=:all: \
  --find-links "$CUDA_WHEELHOUSE_ROOT" --index-url "$PYPI_INDEX_URL" --trusted-host "$PYPI_TRUSTED_HOST" --force-reinstall \
  --report "$RUN_DIR/cuda-wheelhouse-install-report.json" \
  "${CUDA_WHEEL_FILES[@]}" >>"$RUN_DIR/resolver-install.log" 2>&1
# The runtime wheel has a deliberately Docker-equivalent post-solve DeepGEMM
# identity. Install its fixed, already-validated payload without asking pip to
# solve that incompatible source-era metadata graph.
run_bounded "$RUNTIME_VENV/bin/python" -m pip install --no-index --no-deps --force-reinstall \
  --report "$RUN_DIR/runtime-install-report.json" "$RUNTIME_WHEEL" \
  >>"$RUN_DIR/resolver-install.log" 2>&1
"$PYTHON" - "$RUNTIME_WHEEL" "$RUN_DIR/ordinary-dependency-requirements.txt" <<'PY'
from email.parser import BytesParser
import os
import pathlib
import re
import sys
import zipfile

wheel, output = map(pathlib.Path, sys.argv[1:])
special = {"cuda-tile", "flashinfer-python", "sglang-kernel", "sgl-deep-ep", "sgl-deep-gemm", "torch", "torchvision", "torchaudio"}
with zipfile.ZipFile(wheel) as archive:
    paths = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
    if len(paths) != 1:
        raise ValueError("runtime wheel METADATA differs")
    metadata = BytesParser().parsebytes(archive.read(paths[0]))
requirements = []
for requirement in metadata.get_all("Requires-Dist", []):
    match = re.match(r"\s*([A-Za-z0-9_.-]+)", requirement)
    if not match:
        raise ValueError(f"unparseable runtime requirement: {requirement!r}")
    if re.sub(r"[-_.]+", "-", match.group(1)).lower() not in special:
        requirements.append(requirement)
descriptor = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
    handle.write("\n".join(requirements) + "\n")
os.chmod(output, 0o444)
PY
# FlashInfer declares cuda-tile transitively. Install the known cu12 FlashInfer
# wheel without resolving its CUDA 13.1+-only source dependency, then permit
# the regular resolver to fetch the remaining ordinary closure from the G0
# internal mirror. The no-action startup test is the compatibility oracle for
# this deliberately narrow exception.
run_bounded "$RUNTIME_VENV/bin/python" -m pip install --no-deps --only-binary=:all: \
  --index-url "$PYPI_INDEX_URL" --trusted-host "$PYPI_TRUSTED_HOST" --force-reinstall \
  --report "$RUN_DIR/flashinfer-exception-install-report.json" "flashinfer_python[cu12]==0.6.17" \
  >>"$RUN_DIR/resolver-install.log" 2>&1
"$PYTHON" - "$RUN_DIR/omitted-dependency-exception.json" <<'PY'
import json
import os
import pathlib
import sys

output = pathlib.Path(sys.argv[1])
document = {
    "allowed_uninstalled_requirement": "cuda-tile==1.6.0rc5",
    "installed_without_dependency_resolution": "flashinfer_python[cu12]==0.6.17",
    "reason": "G0-C-011 built this CUDA 13.1+-only source distribution; CUDA12-COMPAT-001 must not source-build on ECS",
    "success_scope": "restricted startup only; no claim that cuda-tile-dependent execution is compatible",
}
fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle:
    handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(output, 0o444)
PY
# Only ordinary requirements may use the Alibaba PyPI mirror. --only-binary
# makes any source-native compilation route an explicit resolver failure instead.
run_bounded "$RUNTIME_VENV/bin/python" -m pip install --only-binary=:all: \
  --index-url "$PYPI_INDEX_URL" --trusted-host "$PYPI_TRUSTED_HOST" --report "$RUN_DIR/ordinary-dependency-report.json" \
  -r "$RUN_DIR/ordinary-dependency-requirements.txt" >>"$RUN_DIR/resolver-install.log" 2>&1

# Match the pinned Docker cleanup, including the four CUDA 13 packages selected
# by Humming Kernels' unsuffixed CUDA 13 extra. Then make the local CUDA
# wheelhouse the final special-package state.
"$RUNTIME_VENV/bin/python" -m pip list --format=freeze | \
  awk -F'==' '($1 ~ /-cu13$/) || ($1 ~ /^nvidia-cuda-(cccl|nvcc|nvrtc|runtime)$/ && $2 ~ /^13([.]|$)/) {print $1}' >"$RUN_DIR/cu13-distributions-before-removal.txt"
if [[ -s "$RUN_DIR/cu13-distributions-before-removal.txt" ]]; then
  while IFS= read -r distribution; do
    run_bounded "$RUNTIME_VENV/bin/python" -m pip uninstall -y "$distribution" \
      >>"$RUN_DIR/resolver-install.log" 2>&1
  done <"$RUN_DIR/cu13-distributions-before-removal.txt"
fi
run_bounded "$RUNTIME_VENV/bin/python" -m pip install --only-binary=:all: \
  --find-links "$CUDA_WHEELHOUSE_ROOT" --index-url "$PYPI_INDEX_URL" --trusted-host "$PYPI_TRUSTED_HOST" --force-reinstall \
  "${CUDA_WHEEL_FILES[@]}" \
  >>"$RUN_DIR/resolver-install.log" 2>&1
"$RUNTIME_VENV/bin/python" -m pip list --format=freeze | \
  awk -F'==' '($1 ~ /-cu13$/) || ($1 ~ /^nvidia-cuda-(cccl|nvcc|nvrtc|runtime)$/ && $2 ~ /^13([.]|$)/) {print $1}' >"$RUN_DIR/cu13-distributions-after-removal.txt"
test ! -s "$RUN_DIR/cu13-distributions-after-removal.txt"
"$RUNTIME_VENV/bin/python" -m pip freeze | LC_ALL=C sort >"$RUN_DIR/dependency-lock.txt"
"$RUNTIME_VENV/bin/python" -m pip list --format=json >"$RUN_DIR/installed-distributions.json"
chmod 0444 "$RUN_DIR/installed-distributions.json"
"$PYTHON" - "$RUN_DIR/installed-distributions.json" \
  "$SGLANG_KERNEL_VERSION" "$DEEP_EP_VERSION" "$DEEP_GEMM_VERSION" \
  "$TORCH_VERSION" "$TORCHVISION_VERSION" "$TORCHAUDIO_VERSION" <<'PY'
import json
import re
import sys

versions = sys.argv[2:]
canonical = lambda value: re.sub(r"[-_.]+", "-", value).lower()
locked = {}
inventory = json.load(open(sys.argv[1], encoding="utf-8"))
if not isinstance(inventory, list):
    raise SystemExit("installed distribution inventory is not a list")
for entry in inventory:
    if not isinstance(entry, dict) or set(entry) != {"name", "version"}:
        raise SystemExit("installed distribution inventory entry differs")
    name = entry["name"]
    version = entry["version"]
    if not isinstance(name, str) or not isinstance(version, str) or not name or not version:
        raise SystemExit("installed distribution inventory entry is invalid")
    normalized = canonical(name)
    if normalized in locked:
        raise SystemExit(f"duplicate normalized distribution in installed inventory: {name}")
    locked[normalized] = version
for name, version in locked.items():
    if name.endswith("-cu13") or (
        name in {
            "nvidia-cuda-runtime",
            "nvidia-cuda-cccl",
            "nvidia-cuda-nvcc",
            "nvidia-cuda-nvrtc",
        }
        and re.fullmatch(r"13(?:[.].*)?", version)
    ):
        raise SystemExit(f"CUDA 13 distribution remains in installed inventory: {name}=={version}")
if "cuda-tile" in locked:
    raise SystemExit("installed inventory unexpectedly contains cuda-tile")
expected = {
    "flashinfer-python": "0.6.17",
    "sglang-kernel": f"{versions[0]}+cu129",
    "sgl-deep-ep": f"{versions[1]}+cu129",
    "sgl-deep-gemm": f"{versions[2]}+cu129",
    "torch": f"{versions[3]}+cu129",
    "torchvision": f"{versions[4]}+cu129",
    "torchaudio": f"{versions[5]}+cu129",
}
for name, expected_version in expected.items():
    actual_version = locked.get(name)
    if actual_version != expected_version:
        raise SystemExit(
            f"installed inventory differs for {name}: {actual_version!r} != {expected_version!r}"
        )
PY
"$RUNTIME_VENV/bin/python" -m pip show sglang-kernel sgl-deep-ep sgl-deep-gemm torch torchvision torchaudio \
  >>"$RUN_DIR/resolver-install.log" 2>&1

PHASE="torch_cuda"
TORCH_EXPECTED_VERSION="$TORCH_VERSION" TORCH_EXPECTED_CUDA="129" \
  "$RUNTIME_VENV/bin/python" - <<'PY' >"$RUN_DIR/torch-cuda-probe.log" 2>&1
import json
import os
import torch

assert torch.__version__.split("+")[0] == os.environ["TORCH_EXPECTED_VERSION"], torch.__version__
expected_cuda = f"{os.environ['TORCH_EXPECTED_CUDA'][0:2]}.{os.environ['TORCH_EXPECTED_CUDA'][2:]}"
assert torch.version.cuda == expected_cuda, torch.version.cuda
assert torch.cuda.is_available()
assert torch.cuda.device_count() == 1, torch.cuda.device_count()
assert "A10" in torch.cuda.get_device_name(0), torch.cuda.get_device_name(0)
value = torch.tensor([2, 3], device="cuda", dtype=torch.int32)
result = (value * value).sum()
torch.cuda.synchronize()
assert result.item() == 13, result.item()
print(json.dumps({"device": torch.cuda.get_device_name(0), "torch": torch.__version__, "torch_cuda": torch.version.cuda}))
PY

PHASE="compiler"
cat >"$RUN_DIR/cuda-sm86.cu" <<'CU'
#include <cuda_runtime.h>
#include <cstdio>

__global__ void write_value(int* output) { *output = 86; }

int main() {
  int* device = nullptr;
  int host = 0;
  if (cudaMalloc(&device, sizeof(int)) != cudaSuccess) return 2;
  write_value<<<1, 1>>>(device);
  if (cudaGetLastError() != cudaSuccess) return 3;
  if (cudaDeviceSynchronize() != cudaSuccess) return 4;
  if (cudaMemcpy(&host, device, sizeof(int), cudaMemcpyDeviceToHost) != cudaSuccess) return 5;
  cudaFree(device);
  if (host != 86) return 6;
  std::printf("sm_86_cuda_program=ok\n");
  return 0;
}
CU
chmod 0444 "$RUN_DIR/cuda-sm86.cu"
run_bounded "$CUDA_HOME/bin/nvcc" -arch=sm_86 "$RUN_DIR/cuda-sm86.cu" -o "$WORK_ROOT/cuda-sm86" \
  >"$RUN_DIR/cuda-sm86-build.log" 2>&1
run_bounded "$WORK_ROOT/cuda-sm86" >"$RUN_DIR/cuda-sm86-output.log" 2>&1
grep -Fx 'sm_86_cuda_program=ok' "$RUN_DIR/cuda-sm86-output.log"

env -u PYTHONPATH "$RUNTIME_VENV/bin/python" "$PROVENANCE" \
  --source-root "$TREATMENT" --install-root "$RUNTIME_VENV" \
  --expected-interpreter "$RUNTIME_VENV/bin/python" --output "$RUN_DIR/sglang-provenance.json"
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
  printf 'RUNTIME_WHEEL=%q\n' "$RUNTIME_WHEEL"
  printf 'RUNTIME_WHEEL_PROVENANCE=%q\n' "$RUN_DIR/runtime-wheel-provenance.json"
  printf 'CUDA_WHEELHOUSE_INDEX=%q\n' "$RUN_DIR/cuda-wheelhouse-index.json"
  printf 'ORDINARY_PYPI_INDEX=%q\n' "$PYPI_INDEX_URL"
} >"$RUN_DIR/runtime.env"
chmod 0444 "$RUN_DIR/runtime.env"
"$PYTHON" "$FINALIZE" render --template "$TEMPLATE" --repo-root "$REPO_ROOT" --output "$RUN_DIR/manifest.json"
(cd "$RUN_DIR" && sha256sum manifest.json >manifest.sha256)
chmod 0444 "$RUN_DIR/manifest.sha256"

printf 'selector=%s\noffline=true\nwarmup_disabled=true\n' "$RESTRICTED_SELECTOR" \
  >"$RUN_DIR/restricted-startup-command.txt"
chmod 0444 "$RUN_DIR/restricted-startup-command.txt"
PHASE="startup"
gpu_pids >"$RUN_DIR/startup-gpu-pids-before.txt"
(
  cd "$TREATMENT"
  exec setsid timeout --signal=TERM --kill-after=30s "${LONG_COMMAND_TIMEOUT_SECONDS}s" \
    env -u PYTHONPATH HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
    TOOLGAP_G1_MODEL_PATH="$MODEL_ROOT" "$RUNTIME_VENV/bin/python" -m unittest \
    "$RESTRICTED_SELECTOR"
) >"$RUN_DIR/restricted-startup.log" 2>&1 &
current_pid="$!"
wait_for_startup_pgid
printf '%s\n' "$current_pid" >"$RUN_DIR/startup.pid"
printf '%s\n' "$current_pgid" >"$RUN_DIR/startup.pgid"
if wait_for_startup; then startup_status=0; else startup_status=$?; fi
if [[ "$startup_status" = 0 ]]; then listener_requirement=required; else listener_requirement=optional; fi
# Read the listener record on both passing and failing startup. If a record is
# present, teardown must prove that exact listener is gone before sealing.
if startup_port="$(read_startup_listener_port "$listener_requirement")"; then
  listener_status=0
else
  listener_status=$?
  startup_port=""
fi
if verify_startup_cleanup "$startup_status"; then cleanup_status=0; else cleanup_status=$?; fi
if [[ "$listener_status" != 0 && "$startup_status" = 0 ]]; then startup_status="$listener_status"; fi

PHASE="scope"
if "$PYTHON" - "$RUN_DIR/restricted-startup-command.txt" "$RUN_DIR/restricted-startup.log" <<'PY' >"$RUN_DIR/scope-scan.log"; then
import pathlib, re, sys

patterns = {
    "http_generate": re.compile(r"/generate"),
    "script_action": re.compile(r"execute_script"),
    "checked_operation": re.compile(r"checked_demote_session"),
    "priority_operation": re.compile(r"release_session_priority"),
    "member_demotion": re.compile(r"\.demote"),
    "member_eviction": re.compile(r"\.evict"),
    "gate_result": re.compile(r"\bG1\s+(?:PASS|STOP|RESHAPE)\b"),
}
violations = []
for raw in sys.argv[1:]:
    path = pathlib.Path(raw)
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        for label, pattern in patterns.items():
            if pattern.search(line):
                violations.append(f"{path.name}:{line_number}:{label}")
if violations:
    print("scope=invalid")
    print("\n".join(violations))
    raise SystemExit(1)
print("scope=clean")
PY
  scope_status=0
else
  scope_status=$?
fi
if [[ "$scope_status" != 0 ]]; then
  if ! seal_failure_or_error INVALID_SCOPE scope "$scope_status"; then
    trap - ERR HUP INT TERM
    exit 70
  fi
  trap - ERR HUP INT TERM
  exit "$scope_status"
fi
if [[ "$startup_status" != 0 || "$cleanup_status" != 0 ]]; then
  PHASE="startup"
  terminal_status="$([[ "$startup_status" != 0 ]] && echo "$startup_status" || echo "$cleanup_status")"
  if ! seal_failure_or_error "$(failure_terminal "$terminal_status")" startup "$terminal_status"; then
    trap - ERR HUP INT TERM
    exit 70
  fi
  trap - ERR HUP INT TERM
  exit "$terminal_status"
fi
"$PYTHON" "$FINALIZE" finish --run-dir "$RUN_DIR"
"$PYTHON" "$FINALIZE" verify --run-dir "$RUN_DIR"
trap - ERR HUP INT TERM
echo "CUDA12_COMPAT_TERMINAL_SEALED: $RUN_DIR"
