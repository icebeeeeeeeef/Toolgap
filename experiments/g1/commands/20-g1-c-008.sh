#!/usr/bin/env bash
# Execute one sealed formal G1-C-008 runtime revision on the pinned A10/CUDA12 host.
set -Eeuo pipefail

readonly BUNDLE_ID="G1-C-008"
readonly LONG_TIMEOUT_SECONDS=2400
readonly BASE_COMMIT="92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2"
readonly BASE_TREE="25e9bf86d04c27fe380024d9c8c421c3b5b51f3c"
readonly EXPECTED_RUNTIME_WHEEL_FILENAME="sglang-0.0.0.dev2+g734a8e921-cp312-cp312-linux_x86_64.whl"
readonly PYPI_INDEX_URL="http://mirrors.cloud.aliyuncs.com/pypi/simple/"
readonly PYPI_TRUSTED_HOST="mirrors.cloud.aliyuncs.com"

REPO_ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd -P)"
ATTEMPT_ID="${G1_C_008_ATTEMPT_ID:-}"
PYTHON="${G1_C_008_PYTHON:-python3}"
RUN_DIR="${G1_C_008_RUN_DIR:-$REPO_ROOT/experiments/g1/raw/g1-c-008/$ATTEMPT_ID}"
WORK_ROOT="${G1_C_008_WORK_ROOT:-/tmp/toolgap-g1-c-008-$ATTEMPT_ID}"
SOURCE_SEED_ARCHIVE="${G1_C_008_SOURCE_SEED_ARCHIVE:-}"
MODEL_SEED_ARCHIVE="${G1_C_008_MODEL_SEED_ARCHIVE:-}"
RUNTIME_WHEEL="${G1_C_008_RUNTIME_WHEEL:-}"
RUNTIME_WHEEL_PROVENANCE="${G1_C_008_RUNTIME_WHEEL_PROVENANCE:-}"
CUDA_WHEELHOUSE_ARCHIVE="${G1_C_008_CUDA_WHEELHOUSE_ARCHIVE:-}"
INPUT_MANIFEST="${G1_C_008_INPUT_MANIFEST:-}"
INPUT_OSS_RECEIPT="${G1_C_008_INPUT_OSS_RECEIPT:-}"
BOOTSTRAP_RECEIPT="${G1_C_008_BOOTSTRAP_RECEIPT:-}"
CUDA_HOME="${G1_C_008_CUDA_HOME:-/usr/local/cuda-12.8}"

readonly FINALIZER="$REPO_ROOT/experiments/g1/commands/g1_c_008_finalize.py"
readonly EXTRACTOR="$REPO_ROOT/experiments/g1/commands/g1_c_008_extract_records.py"
readonly GPU_SAMPLER="$REPO_ROOT/experiments/g1/commands/g1_c_008_gpu_sampler.py"
readonly ARM_LAUNCHER="$REPO_ROOT/experiments/g1/commands/g1_c_008_arm_launcher.py"
readonly TEMPLATE="$REPO_ROOT/experiments/g1/manifest.g1-c-008.template.json"
readonly MODEL_HELPER="$REPO_ROOT/experiments/g0/commands/g0_c_016_model_seed.py"
readonly PROVENANCE="$REPO_ROOT/experiments/g0/commands/g0_c_008_package_provenance.py"
readonly INVENTORY="$REPO_ROOT/experiments/g1/artifacts/model-files.g1-preflight-001.json"

declare -a ARMS=(
  enabled
  bypass
  reject_write_through_pending
  reject_non_target_session_coverage
  reject_device_locked
  reject_stale_generation
  stock_eviction_liveness
)
selector_for() {
  case "$1" in
    enabled) printf '%s\n' 'TestG1EnabledArm.test_enabled_checked_demotion_records_allocator_visible_release' ;;
    bypass) printf '%s\n' 'TestG1BypassArm.test_bypass_releases_priority_without_physical_reclamation' ;;
    reject_write_through_pending) printf '%s\n' 'TestG1WriteThroughPending.test_uncommitted_host_copy_is_deferred_without_physical_free' ;;
    reject_non_target_session_coverage) printf '%s\n' 'TestG1NonTargetCoverage.test_shared_target_is_deferred_for_the_other_session' ;;
    reject_device_locked) printf '%s\n' 'TestG1DeviceLocked.test_active_request_is_deferred_at_the_device_lock_check' ;;
    reject_stale_generation) printf '%s\n' 'TestG1StaleGeneration.test_stale_generation_is_rejected_before_priority_release' ;;
    stock_eviction_liveness) printf '%s\n' 'TestG1StockEvictionLiveness.test_stock_eviction_remains_reachable_after_bypass' ;;
    *) return 1 ;;
  esac
}

CURRENT_ARM_PID=""
CURRENT_ARM_PGID=""
CURRENT_SAMPLER_PID=""

# BEGIN_SIGNAL_CLEANUP_HELPERS
valid_runtime_pid() {
  [[ "${1:-}" =~ ^[1-9][0-9]*$ ]]
}
stop_current_sampler() {
  local sampler_pid="${CURRENT_SAMPLER_PID:-}"
  if valid_runtime_pid "$sampler_pid"; then
    if kill -0 "$sampler_pid" 2>/dev/null; then
      kill -TERM "$sampler_pid" 2>/dev/null || true
      sleep 1
      if kill -0 "$sampler_pid" 2>/dev/null; then kill -KILL "$sampler_pid" 2>/dev/null || true; fi
    fi
    wait "$sampler_pid" 2>/dev/null || true
  fi
  CURRENT_SAMPLER_PID=""
}
wait_for_runtime_group_exit() {
  local pgid="$1" attempts=0
  while kill -0 -- "-$pgid" 2>/dev/null; do
    (( attempts += 1 ))
    (( attempts < 100 )) || return 1
    sleep 0.05
  done
}
stop_current_arm_group() {
  local arm_pid="${CURRENT_ARM_PID:-}" pgid="${CURRENT_ARM_PGID:-}"
  if valid_runtime_pid "$arm_pid" && [[ "$pgid" == "$arm_pid" ]] && kill -0 -- "-$pgid" 2>/dev/null; then
    kill -TERM -- "-$pgid" 2>/dev/null || true
    sleep 1
    if kill -0 -- "-$pgid" 2>/dev/null; then kill -KILL -- "-$pgid" 2>/dev/null || true; fi
  elif valid_runtime_pid "$arm_pid" && kill -0 "$arm_pid" 2>/dev/null; then
    kill -TERM "$arm_pid" 2>/dev/null || true
    sleep 1
    if kill -0 "$arm_pid" 2>/dev/null; then kill -KILL "$arm_pid" 2>/dev/null || true; fi
  fi
  if valid_runtime_pid "$arm_pid"; then wait "$arm_pid" 2>/dev/null || true; fi
  if valid_runtime_pid "$pgid" && [[ "$pgid" == "$arm_pid" ]]; then
    wait_for_runtime_group_exit "$pgid" || return 1
  fi
  CURRENT_ARM_PID=""
  CURRENT_ARM_PGID=""
}
wait_for_arm_handshake() {
  local handshake="$1" ack="$2"
  valid_runtime_pid "${CURRENT_ARM_PID:-}" || return 1
  "$PYTHON" - "$CURRENT_ARM_PID" "$handshake" <<'PY' || return 1
import json
import os
import pathlib
import sys
import time

pid = int(sys.argv[1])
path = pathlib.Path(sys.argv[2])
deadline = time.monotonic() + 10
while True:
    if path.is_symlink():
        raise SystemExit(1)
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        document = None
    except (UnicodeDecodeError, json.JSONDecodeError):
        document = None
    if document is not None:
        if (
            document != {"pgid": pid, "pid": pid, "schema_version": 1}
            or type(document.get("pid")) is not int
            or type(document.get("pgid")) is not int
            or type(document.get("schema_version")) is not int
            or path.stat().st_mode & 0o222
            or not path.is_file()
        ):
            raise SystemExit(1)
        try:
            if os.getpgid(pid) != pid:
                raise SystemExit(1)
        except ProcessLookupError:
            raise SystemExit(1)
        raise SystemExit(0)
    if time.monotonic() >= deadline:
        raise SystemExit(1)
    time.sleep(0.01)
PY
  CURRENT_ARM_PGID="$CURRENT_ARM_PID"
  "$PYTHON" - "$CURRENT_ARM_PID" "$ack" <<'PY' || return 1
import json
import os
import pathlib
import sys

pid = int(sys.argv[1])
path = pathlib.Path(sys.argv[2])
payload = (json.dumps({"pid": pid, "schema_version": 1}, sort_keys=True) + "\n").encode()
descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(descriptor, "wb") as output:
    output.write(payload)
    output.flush()
    os.fsync(output.fileno())
path.chmod(0o444)
PY
}
cleanup_active_processes() {
  stop_current_sampler
  stop_current_arm_group
}
# END_SIGNAL_CLEANUP_HELPERS

die() { printf 'g1-c-008: %s\n' "$*" >&2; exit 2; }
require() { command -v "$1" >/dev/null || die "missing command: $1"; }
# BEGIN_RUNTIME_WHEEL_COPY_HELPERS
copy_immutable() {
  "$PYTHON" - "$1" "$2" <<'PY'
import os, pathlib, shutil, sys
source, output = map(pathlib.Path, sys.argv[1:])
if output.exists() or source.is_symlink() or not source.is_file():
    raise ValueError("immutable copy input or destination differs")
fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with source.open("rb") as reader, os.fdopen(fd, "wb") as writer:
    shutil.copyfileobj(reader, writer, length=1024 * 1024)
os.chmod(output, 0o444)
PY
}
runtime_wheel_filename() {
  "$PYTHON" - "$1" <<'PY'
import json
import pathlib
import sys

manifest = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
archives = manifest.get("archives")
entry = archives.get("runtime_wheel") if isinstance(archives, dict) else None
name = entry.get("path") if isinstance(entry, dict) else None
if not isinstance(name, str) or not name.endswith(".whl"):
    raise ValueError("runtime wheel manifest filename differs")
pure = pathlib.PurePosixPath(name)
if pure.is_absolute() or not pure.parts or pure.name != name or ".." in pure.parts:
    raise ValueError("unsafe runtime wheel manifest filename")
print(name)
PY
}
# END_RUNTIME_WHEEL_COPY_HELPERS
# BEGIN_STORAGE_PREFLIGHT_HELPER
storage_preflight() {
  local output="$1" stage="$2" target="$3" manifest="$4"
  "$PYTHON" - "$output" "$stage" "$target" "$manifest" <<'PY'
import json
import os
import pathlib
import sys

output, stage, target, manifest_path = map(pathlib.Path, sys.argv[1:])
if stage.name not in {"source_restore", "resolver"}:
    raise ValueError("storage preflight stage differs")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
storage = manifest.get("storage_preflight")
minimum = storage.get("minimum_free_bytes") if isinstance(storage, dict) else None
if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum <= 0:
    raise ValueError("storage preflight manifest binding differs")
target = target.resolve()
stats = os.statvfs(target)
available = stats.f_bavail * stats.f_frsize
total = stats.f_blocks * stats.f_frsize
document = {
    "available_free_bytes": available,
    "minimum_free_bytes": minimum,
    "path": str(target),
    "schema_version": 1,
    "stage": stage.name,
    "total_bytes": total,
}
descriptor = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
    handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(output, 0o444)
if available < minimum:
    raise SystemExit(f"available disk {available} below manifest minimum {minimum}")
PY
}
# END_STORAGE_PREFLIGHT_HELPER
# BEGIN_FROZEN_PATCH_RESTORE_HELPER
apply_frozen_patches() {
  local treatment="$1" patch
  shift
  [[ "$#" == 3 ]] || die 'frozen SGLang patch count differs'
  for patch in "$@"; do
    [[ -f "$patch" && ! -L "$patch" ]] || die "missing frozen SGLang patch: $patch"
    sha256sum "$patch"
    git -C "$treatment" apply --check "$patch"
    git -C "$treatment" apply "$patch"
  done
}
# END_FROZEN_PATCH_RESTORE_HELPER
# BEGIN_CHANGED_PATH_INVENTORY_HELPER
changed_regular_paths() {
  "$PYTHON" - "$1" <<'PY'
import pathlib
import subprocess
import sys

root = pathlib.Path(sys.argv[1]).resolve()
commands = (
    ("diff", "--name-only"),
    ("ls-files", "--others", "--exclude-standard"),
)
paths = set()
for command in commands:
    names = subprocess.check_output(
        ["git", "-C", str(root), *command], text=True
    ).splitlines()
    for raw_name in names:
        relative = pathlib.PurePosixPath(raw_name)
        if (
            not raw_name
            or relative.is_absolute()
            or not relative.parts
            or ".." in relative.parts
        ):
            raise ValueError(f"unsafe changed path: {raw_name!r}")
        candidate = root.joinpath(*relative.parts)
        resolved = candidate.resolve(strict=True)
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"changed path escapes source root: {raw_name}") from exc
        if (
            candidate.is_symlink()
            or not candidate.is_file()
        ):
            raise ValueError(f"changed path is not a regular non-symlink file: {raw_name}")
        paths.add(relative.as_posix())
print("\n".join(sorted(paths)))
PY
}
# END_CHANGED_PATH_INVENTORY_HELPER
gpu_pids() {
  nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null |
    awk 'NF && $1 ~ /^[0-9]+$/ {print $1}' | LC_ALL=C sort -n -u
}
capture_environment() {
  {
    printf 'captured_at=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    uname -a || true
    cat /etc/os-release 2>/dev/null || true
    "$PYTHON" --version || true
    nvidia-smi -L 2>/dev/null || true
    nvidia-smi --query-gpu=name,uuid,memory.total,driver_version --format=csv,noheader 2>/dev/null || true
    "$CUDA_HOME/bin/nvcc" --version 2>/dev/null || true
  } >"$RUN_DIR/environment.txt" 2>&1
  chmod 0444 "$RUN_DIR/environment.txt"
}
# BEGIN_FAILURE_EVIDENCE_HELPER
record_failure_evidence() {
  local code="$1"
  local phase="$2"
  "$PYTHON" - "$RUN_DIR/pre-execution-failure.json" "$phase" "$code" <<'PY'
import json, os, pathlib, sys

output = pathlib.Path(sys.argv[1])
phase = sys.argv[2]
try:
    exit_code = int(sys.argv[3])
except ValueError as error:
    raise ValueError("runner failure exit code is invalid") from error
phases = {
    "bootstrap", "input_binding", "source_restore", "model",
    "resolver", "formal_arms", "scope", "render", "seal",
}
if phase not in phases or not 1 <= exit_code <= 255:
    raise ValueError("runner failure evidence differs")
document = {
    "exit_code": exit_code,
    "failure_phase": phase,
    "schema_version": 1,
}
descriptor = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
    handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(output, 0o444)
PY
}
# END_FAILURE_EVIDENCE_HELPER
# BEGIN_INVALID_SEAL_HELPER
seal_invalid() {
  local code="$1"
  trap - EXIT ERR
  trap '' HUP INT TERM
  if ! cleanup_active_processes; then
    printf 'g1-c-008: cleanup could not prove process-group exit; attempt remains unsealed\n' >&2
    exit "$code"
  fi
  if [[ -d "$RUN_DIR" && -f "$RUN_DIR/attempt-context.json" && -f "$RUN_DIR/environment.txt" && ! -e "$RUN_DIR/execution-status.json" ]]; then
    record_failure_evidence "$code" "${PHASE:-unclassified}" || true
    "$PYTHON" "$FINALIZER" invalid --run-dir "$RUN_DIR" --reason "runner failure at phase ${PHASE:-unclassified}, exit $code" || true
  fi
  exit "$code"
}
# END_INVALID_SEAL_HELPER
PHASE="bootstrap"
trap 'seal_invalid "$?"' EXIT
trap 'seal_invalid "$?"' ERR
trap 'seal_invalid 129' HUP
trap 'seal_invalid 130' INT
trap 'seal_invalid 143' TERM

[[ -n "$ATTEMPT_ID" && "$ATTEMPT_ID" =~ ^[A-Za-z0-9._-]+$ ]] || die 'set G1_C_008_ATTEMPT_ID'
for path in "$SOURCE_SEED_ARCHIVE" "$MODEL_SEED_ARCHIVE" "$RUNTIME_WHEEL" "$RUNTIME_WHEEL_PROVENANCE" "$CUDA_WHEELHOUSE_ARCHIVE" "$INPUT_MANIFEST" "$INPUT_OSS_RECEIPT" "$BOOTSTRAP_RECEIPT"; do
  [[ "$path" = /* && -f "$path" && ! -L "$path" ]] || die "staged input must be an absolute regular file: $path"
done
[[ ! -e "$RUN_DIR" && ! -e "$WORK_ROOT" ]] || die 'attempt destination already exists'
require git
command -v "$PYTHON" >/dev/null || die "Python is unavailable: $PYTHON"
PYTHON="$(command -v "$PYTHON")"
[[ -f "$FINALIZER" && ! -L "$FINALIZER" ]] || die 'finalizer is unavailable'
"$PYTHON" "$FINALIZER" --help >/dev/null || die 'finalizer cannot run under bootstrap Python'
[[ -z "$(git -C "$REPO_ROOT" status --porcelain --untracked-files=no)" ]] || die 'restored ToolGap checkout is tracked-dirty'

mkdir -p "$(dirname -- "$RUN_DIR")"
mkdir "$RUN_DIR" "$WORK_ROOT" "$RUN_DIR/arms"
RUN_DIR="$(cd "$RUN_DIR" && pwd -P)"
WORK_ROOT="$(cd "$WORK_ROOT" && pwd -P)"
"$PYTHON" - "$REPO_ROOT" "$RUN_DIR/attempt-context.json" "$ATTEMPT_ID" "$WORK_ROOT" <<'PY'
import hashlib, json, os, pathlib, subprocess, sys
from datetime import datetime, timezone
root = pathlib.Path(sys.argv[1])
output = pathlib.Path(sys.argv[2])
attempt = sys.argv[3]
work_root = pathlib.Path(sys.argv[4])
git = lambda *args: subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()
spec = root / "experiments/g1/SPEC.g1-c-008.md"
document = {
    "attempt_id": attempt, "bundle_id": "G1-C-008", "claim_state": "roadmap",
    "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "gate": "G1", "kind": "formal_checked_demote_runtime",
    "spec_path": "experiments/g1/SPEC.g1-c-008.md",
    "spec_sha256": hashlib.sha256(spec.read_bytes()).hexdigest(),
    "toolgap_commit": git("rev-parse", "HEAD"),
    "toolgap_tracked_clean": not bool(git("status", "--porcelain", "--untracked-files=no")),
    "toolgap_tree": git("rev-parse", "HEAD^{tree}"),
    "work_root": str(work_root),
}
fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle: handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(output, 0o444)
PY
capture_environment

for command in nvidia-smi sha256sum tar timeout ss; do require "$command"; done
"$PYTHON" -c 'import ensurepip, sys, venv; assert sys.version_info[:2] == (3, 12), sys.version'
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || die 'requires Linux x86_64'
grep -Eq '^ID=ubuntu$' /etc/os-release && grep -Eq '^VERSION_ID="?24\.04"?$' /etc/os-release || die 'requires Ubuntu 24.04'
[[ -x "$CUDA_HOME/bin/nvcc" ]] && "$CUDA_HOME/bin/nvcc" --version | grep -Eq 'release 12\.8([,.]|$)' || die 'requires CUDA 12.8'
[[ "$(nvidia-smi -L | wc -l | xargs)" == 1 ]] || die 'requires exactly one GPU'
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader | grep -Eq '^NVIDIA A10.*, *([2][2-5][0-9]{3}) MiB, *580\.126\.09$' || die 'requires one A10 with driver 580.126.09'

PHASE="input_binding"
"$PYTHON" - "$INPUT_MANIFEST" "$INPUT_OSS_RECEIPT" "$BOOTSTRAP_RECEIPT" "$REPO_ROOT" "$SOURCE_SEED_ARCHIVE" "$MODEL_SEED_ARCHIVE" "$RUNTIME_WHEEL" "$RUNTIME_WHEEL_PROVENANCE" "$CUDA_WHEELHOUSE_ARCHIVE" <<'PY' >"$RUN_DIR/input-manifest-verify.log"
import hashlib, json, pathlib, re, subprocess, sys
(
    manifest_path, receipt_path, bootstrap_path, root, source, model, wheel, provenance, wheelhouse,
) = map(pathlib.Path, sys.argv[1:])
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
required = {"archives", "identity", "model", "ordinary_dependency_transport", "patches", "schema_version", "static_inputs", "storage_preflight"}
if set(manifest) != required or manifest["schema_version"] != 1:
    raise ValueError("input manifest schema differs")
if manifest["storage_preflight"] != {"minimum_free_bytes": 24 * 1024 * 1024 * 1024}:
    raise ValueError("storage preflight manifest differs")
identity = manifest["identity"]
if identity.get("bundle_id") != "G1-C-008" or identity.get("kind") != "formal_checked_demote_runtime":
    raise ValueError("input manifest identity differs")
head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
tree = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD^{tree}"], text=True).strip()
if identity.get("toolgap_commit") != head or identity.get("toolgap_tree") != tree:
    raise ValueError("input manifest ToolGap identity differs")
files = {
    "sglang_source_seed": source, "model_snapshot": model, "runtime_wheel": wheel,
    "runtime_wheel_provenance": provenance, "cuda_wheelhouse": wheelhouse,
}
for label, path in files.items():
    entry = manifest["archives"][label]
    observed = hashlib.sha256(path.read_bytes()).hexdigest()
    if entry != {"path": path.name, "sha256": observed, "size_bytes": path.stat().st_size}:
        raise ValueError(f"staged archive differs: {label}")
for path, binding in manifest["static_inputs"].items():
    candidate = root / path
    if not candidate.is_file() or binding != {"sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(), "size_bytes": candidate.stat().st_size}:
        raise ValueError(f"static input differs: {path}")
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
if receipt.get("identity") != identity:
    raise ValueError("input OSS receipt identity differs")
bootstrap = json.loads(bootstrap_path.read_text(encoding="utf-8"))
if bootstrap.get("input_manifest_sha256") != hashlib.sha256(manifest_path.read_bytes()).hexdigest():
    raise ValueError("bootstrap receipt differs")
print("input_manifest=verified")
PY
chmod 0444 "$RUN_DIR/input-manifest-verify.log"
copy_immutable "$INPUT_MANIFEST" "$RUN_DIR/input-manifest.json"
copy_immutable "$INPUT_OSS_RECEIPT" "$RUN_DIR/input-oss-receipt.json"
copy_immutable "$BOOTSTRAP_RECEIPT" "$RUN_DIR/bootstrap-receipt.json"
RUNTIME_WHEEL_FILENAME="$(runtime_wheel_filename "$RUN_DIR/input-manifest.json")" || die 'runtime wheel filename differs'
[[ "$RUNTIME_WHEEL_FILENAME" == "$EXPECTED_RUNTIME_WHEEL_FILENAME" ]] || die 'runtime wheel filename is not frozen'
[[ "$RUNTIME_WHEEL_FILENAME" == "$(basename -- "$RUNTIME_WHEEL")" ]] || die 'runtime wheel basename differs from manifest'
copy_immutable "$RUNTIME_WHEEL" "$RUN_DIR/$RUNTIME_WHEEL_FILENAME"
copy_immutable "$RUNTIME_WHEEL_PROVENANCE" "$RUN_DIR/runtime-wheel-provenance.json"

PHASE="source_restore"
storage_preflight "$RUN_DIR/storage-preflight-source-restore.json" source_restore "$WORK_ROOT" "$RUN_DIR/input-manifest.json" || die 'available disk is below manifest bound before source restore'
"$PYTHON" - "$SOURCE_SEED_ARCHIVE" <<'PY'
import pathlib, sys, tarfile
archive = pathlib.Path(sys.argv[1]); names = set()
with tarfile.open(archive, "r:*") as bundle:
    for member in bundle.getmembers():
        pure, name = pathlib.PurePosixPath(member.name), member.name.rstrip("/")
        if pure.is_absolute() or ".." in pure.parts or not pure.parts or pure.parts[0] != "sglang-source.git" or name in names or not (member.isdir() or member.isfile()):
            raise ValueError(f"unsafe SGLang source member: {member.name}")
        names.add(name)
if not names: raise ValueError("empty SGLang seed")
PY
tar --no-same-owner -xzf "$SOURCE_SEED_ARCHIVE" -C "$WORK_ROOT"
BARE="$WORK_ROOT/sglang-source.git"
TREATMENT="$WORK_ROOT/sglang"
SCRIPTED_TEST="$TREATMENT/test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py"
git -C "$BARE" fsck --full
[[ "$(git -C "$BARE" rev-parse "$BASE_COMMIT^{tree}")" == "$BASE_TREE" ]]
git clone --no-local "$BARE" "$TREATMENT"
git -C "$TREATMENT" checkout --detach "$BASE_COMMIT"
PATCHES=(
  "$REPO_ROOT/upstream/sglang/patches/0001-atomic-checked-demote.patch"
  "$REPO_ROOT/upstream/sglang/patches/0002-g1-scripted-forced-demote.patch"
  "$REPO_ROOT/upstream/sglang/patches/0003-cuda12-compat-packaging.patch"
)
apply_frozen_patches "$TREATMENT" "${PATCHES[@]}" >"$RUN_DIR/source-restore.log" 2>&1
# The patch sequence creates its scripted test module as an untracked file.
# Inventory both modified tracked paths and safe untracked regular files before
# `git add -A`, then require the exact frozen set.
CHANGED_OUTPUT="$(changed_regular_paths "$TREATMENT")" || die 'unable to inventory patched SGLang paths'
CHANGED=()
while IFS= read -r changed_path; do
  [[ -n "$changed_path" ]] && CHANGED+=("$changed_path")
done <<<"$CHANGED_OUTPUT"
EXPECTED_CHANGED=(
  python/pyproject.toml
  python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py
  python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py
  python/sglang/srt/mem_cache/unified_cache/unified_tree_core_interface.py
  python/sglang/srt/mem_cache/unified_radix_cache.py
  test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py
)
[[ "${CHANGED[*]}" == "${EXPECTED_CHANGED[*]}" ]] || die 'patched SGLang changed paths differ'
git -C "$TREATMENT" -c user.name='G1-C-008' -c user.email='g1-c-008@invalid' add -A
git -C "$TREATMENT" -c user.name='G1-C-008' -c user.email='g1-c-008@invalid' commit -m 'g1-c-008 frozen patch sequence' >>"$RUN_DIR/source-restore.log" 2>&1
"$PYTHON" - "$TREATMENT" "$RUN_DIR/sglang-provenance.json" "${PATCHES[@]}" <<'PY'
import hashlib, json, os, pathlib, subprocess, sys
source, output = map(pathlib.Path, sys.argv[1:3])
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
git = lambda *args: subprocess.check_output(["git", "-C", str(source), *args], text=True).strip()
patches = []
for index, raw_path in enumerate(sys.argv[3:], start=1):
    path = pathlib.Path(raw_path)
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise ValueError(f"invalid frozen patch path: {path}")
    patches.append({"label": f"patch_{index}", "path": str(path.resolve()), "sha256": digest(path)})
if len(patches) != 3:
    raise ValueError("frozen patch set differs")
document = {"base_commit": "92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2", "base_tree": "25e9bf86d04c27fe380024d9c8c421c3b5b51f3c", "patched_commit": git("rev-parse", "HEAD"), "patched_tree": git("rev-parse", "HEAD^{tree}"), "patches": patches}
fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle: handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(output, 0o444)
PY

PHASE="model"
MODEL_ROOT="$WORK_ROOT/model-input/model-snapshot"
"$PYTHON" "$MODEL_HELPER" prepare --archive "$MODEL_SEED_ARCHIVE"   --archive-sha256 "$(sha256sum "$MODEL_SEED_ARCHIVE" | awk '{print $1}')"   --input-root "$WORK_ROOT/model-input" --inventory "$INVENTORY"   --receipt "$RUN_DIR/model-snapshot.json" >"$RUN_DIR/model-seed-prepare.log" 2>&1

PHASE="resolver"
storage_preflight "$RUN_DIR/storage-preflight-resolver.json" resolver "$WORK_ROOT" "$RUN_DIR/input-manifest.json" || die 'available disk is below manifest bound before dependency install'
RUNTIME_VENV="$WORK_ROOT/runtime-venv"
"$PYTHON" -m venv "$RUNTIME_VENV"
"$RUNTIME_VENV/bin/python" -m pip --version >"$RUN_DIR/resolver-install.log" 2>&1
WHEELHOUSE_ROOT="$WORK_ROOT/cuda-wheelhouse"
mkdir "$WHEELHOUSE_ROOT"
"$PYTHON" - "$CUDA_WHEELHOUSE_ARCHIVE" "$WHEELHOUSE_ROOT" "$RUN_DIR/cuda-wheelhouse-index.json" "$RUN_DIR/cuda-wheelhouse-validation.json" <<'PY'
import hashlib, json, os, pathlib, shutil, sys, tarfile
archive, root, index_output, validation_output = map(pathlib.Path, sys.argv[1:])
names = {}
with tarfile.open(archive, "r:*") as bundle:
    for member in bundle.getmembers():
        pure, name = pathlib.PurePosixPath(member.name), member.name.rstrip("/")
        if pure.is_absolute() or ".." in pure.parts or not pure.parts or pure.parts[0] != "cuda-wheelhouse" or name in names or not (member.isdir() or member.isfile()):
            raise ValueError(f"unsafe CUDA wheelhouse member: {member.name}")
        if member.isfile():
            if len(pure.parts) != 2: raise ValueError("nested CUDA wheelhouse member")
            source = bundle.extractfile(member)
            if source is None: raise ValueError("unreadable wheelhouse member")
            target = root / pure.name
            with source, target.open("xb") as output: shutil.copyfileobj(source, output)
            names[name] = target
index = json.loads((root / "wheelhouse-index.json").read_text(encoding="utf-8"))
required = {"sglang_kernel", "sgl_deep_ep", "sgl_deep_gemm", "torch", "torchvision", "torchaudio"}
if set(index) != {"schema_version", "wheels"} or index["schema_version"] != 1 or set(index["wheels"]) != required:
    raise ValueError("wheelhouse index differs")
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for label, entry in index["wheels"].items():
    path = root / entry["path"]
    if path.name != entry["path"] or not path.is_file() or digest(path) != entry["sha256"] or path.stat().st_size != entry["size_bytes"]:
        raise ValueError(f"wheelhouse binding differs: {label}")
for output, document in ((index_output, index), (validation_output, {
    "archive_sha256": digest(archive), "archive_size_bytes": archive.stat().st_size,
    "index_sha256": digest(root / "wheelhouse-index.json"), "wheels": index["wheels"],
})):
    fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    with os.fdopen(fd, "w", encoding="utf-8") as handle: handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
    os.chmod(output, 0o444)
PY
mapfile -t CUDA_WHEELS < <("$PYTHON" - "$RUN_DIR/cuda-wheelhouse-index.json" "$WHEELHOUSE_ROOT" <<'PY'
import json, pathlib, sys
index, root = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
for entry in json.loads(index.read_text(encoding="utf-8"))["wheels"].values():
    print(root / entry["path"])
PY
)
test "${#CUDA_WHEELS[@]}" = 6
"$RUNTIME_VENV/bin/python" -m pip install --only-binary=:all: --find-links "$WHEELHOUSE_ROOT" --index-url "$PYPI_INDEX_URL" --trusted-host "$PYPI_TRUSTED_HOST" --force-reinstall "${CUDA_WHEELS[@]}" >>"$RUN_DIR/resolver-install.log" 2>&1
"$RUNTIME_VENV/bin/python" -m pip install --no-deps --force-reinstall "$RUN_DIR/$RUNTIME_WHEEL_FILENAME" >>"$RUN_DIR/resolver-install.log" 2>&1
"$RUNTIME_VENV/bin/python" -m pip install --no-deps --only-binary=:all: --index-url "$PYPI_INDEX_URL" --trusted-host "$PYPI_TRUSTED_HOST" --force-reinstall "flashinfer_python[cu12]==0.6.17" >>"$RUN_DIR/resolver-install.log" 2>&1
"$PYTHON" - "$RUN_DIR/$RUNTIME_WHEEL_FILENAME" "$RUN_DIR/ordinary-requirements.txt" <<'PY'
from email.parser import BytesParser
import os, pathlib, re, sys, zipfile
wheel, output = map(pathlib.Path, sys.argv[1:])
special = {"cuda-tile", "flashinfer-python", "sglang-kernel", "sgl-deep-ep", "sgl-deep-gemm", "torch", "torchvision", "torchaudio"}
with zipfile.ZipFile(wheel) as archive:
    metadata = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
    if len(metadata) != 1: raise ValueError("runtime wheel metadata differs")
    requirements = BytesParser().parsebytes(archive.read(metadata[0])).get_all("Requires-Dist", [])
ordinary = []
for requirement in requirements:
    match = re.match(r"\s*([A-Za-z0-9_.-]+)", requirement)
    if not match: raise ValueError(f"unparseable requirement: {requirement!r}")
    if re.sub(r"[-_.]+", "-", match.group(1)).lower() not in special: ordinary.append(requirement)
fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle: handle.write("\n".join(ordinary) + "\n")
os.chmod(output, 0o444)
PY
"$RUNTIME_VENV/bin/python" -m pip install --only-binary=:all: --index-url "$PYPI_INDEX_URL" --trusted-host "$PYPI_TRUSTED_HOST" -r "$RUN_DIR/ordinary-requirements.txt" >>"$RUN_DIR/resolver-install.log" 2>&1
"$RUNTIME_VENV/bin/python" -m pip list --format=json >"$RUN_DIR/installed-distributions.json"
chmod 0444 "$RUN_DIR/installed-distributions.json"
"$PYTHON" - "$RUN_DIR/runtime-wheel-validation.json" "$RUN_DIR/$RUNTIME_WHEEL_FILENAME" "$RUN_DIR/runtime-wheel-provenance.json" <<'PY'
import hashlib, json, os, pathlib, sys
out, wheel, provenance = map(pathlib.Path, sys.argv[1:])
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
document = {"provenance_identity": json.loads(provenance.read_text(encoding="utf-8"))["identity"], "runtime_wheel_filename": wheel.name, "runtime_wheel_sha256": digest(wheel), "runtime_wheel_size_bytes": wheel.stat().st_size, "source_rebuild": False}
fd = os.open(out, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle: handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(out, 0o444)
PY
"$PYTHON" - "$RUN_DIR/omitted-dependency-exception.json" <<'PY'
import json, os, pathlib, sys
out = pathlib.Path(sys.argv[1])
document = {"allowed_uninstalled_requirement": "cuda-tile==1.6.0rc5", "installed_without_dependency_resolution": "flashinfer_python[cu12]==0.6.17", "reason": "CUDA12 wheel route must not source-build cuda-tile on ECS"}
fd = os.open(out, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle: handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(out, 0o444)
PY
env -u PYTHONPATH "$RUNTIME_VENV/bin/python" "$PROVENANCE" --source-root "$TREATMENT" --install-root "$RUNTIME_VENV" --expected-interpreter "$RUNTIME_VENV/bin/python" --output "$RUN_DIR/installed-source-provenance.json"
mv "$RUN_DIR/installed-source-provenance.json" "$RUN_DIR/sglang-package-provenance.json"

"$PYTHON" - "$RUN_DIR/arm-plan.json" "$SCRIPTED_TEST" <<'PY'
import json, os, pathlib, sys
out = pathlib.Path(sys.argv[1])
scripted_test = pathlib.Path(sys.argv[2])
if not scripted_test.is_file(): raise ValueError("scripted test module is absent")
arms = [
    ("enabled", "TestG1EnabledArm.test_enabled_checked_demotion_records_allocator_visible_release"),
    ("bypass", "TestG1BypassArm.test_bypass_releases_priority_without_physical_reclamation"),
    ("reject_write_through_pending", "TestG1WriteThroughPending.test_uncommitted_host_copy_is_deferred_without_physical_free"),
    ("reject_non_target_session_coverage", "TestG1NonTargetCoverage.test_shared_target_is_deferred_for_the_other_session"),
    ("reject_device_locked", "TestG1DeviceLocked.test_active_request_is_deferred_at_the_device_lock_check"),
    ("reject_stale_generation", "TestG1StaleGeneration.test_stale_generation_is_rejected_before_priority_release"),
    ("stock_eviction_liveness", "TestG1StockEvictionLiveness.test_stock_eviction_remains_reachable_after_bypass"),
]
fd = os.open(out, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle:
    handle.write(json.dumps({"arms": [{"arm": arm, "selector": selector} for arm, selector in arms], "fresh_process_per_arm": True, "selector_module": scripted_test.stem}, indent=2, sort_keys=True) + "\n")
os.chmod(out, 0o444)
PY
cat >"$RUN_DIR/arm-runner.py" <<'PY'
import importlib, pathlib, sys, unittest

def main() -> int:
    path = pathlib.Path(sys.argv[1]).resolve(); selector = sys.argv[2]
    if not path.is_file(): raise ValueError("scripted test module is absent")
    class_name, method_name = selector.rsplit(".", 1)
    sys.path.insert(0, str(path.parent))
    module = importlib.import_module(path.stem)
    module_file = getattr(module, "__file__", None)
    if module_file is None or pathlib.Path(module_file).resolve() != path:
        raise ValueError("scripted test module resolved from the wrong path")
    suite = unittest.defaultTestLoader.loadTestsFromName(f"{class_name}.{method_name}", module)
    if suite.countTestCases() != 1: raise ValueError("selector did not resolve exactly one test")
    return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1

if __name__ == "__main__":
    raise SystemExit(main())
PY
chmod 0444 "$RUN_DIR/arm-runner.py"
{
  printf 'HF_HUB_OFFLINE=1\nTRANSFORMERS_OFFLINE=1\nSGLANG_ENABLE_UNIFIED_RADIX_TREE=1\n'
  printf 'TOOLGAP_G1_MODEL_PATH=%q\nTREATMENT=%q\nRUNTIME_PYTHON=%q\n' "$MODEL_ROOT" "$TREATMENT" "$RUNTIME_VENV/bin/python"
  printf 'ORDINARY_PYPI_INDEX=%q\n' "$PYPI_INDEX_URL"
} >"$RUN_DIR/runtime.env"
chmod 0444 "$RUN_DIR/runtime.env"

PHASE="formal_arms"
run_arm() {
  local arm="$1" selector="$2" pid pgid sampler_pid status
  local arm_dir="$RUN_DIR/arms"
  printf '%s\n' "$selector" >"$arm_dir/$arm.command.txt"
  gpu_pids >"$arm_dir/$arm.gpu-before.txt"
  ss -ltnH | LC_ALL=C sort -u >"$arm_dir/$arm.listeners-before.txt"
  (
    cd "$TREATMENT"
    exec "$PYTHON" "$ARM_LAUNCHER" \
      --handshake "$arm_dir/$arm.launcher-handshake.json" \
      --ack "$arm_dir/$arm.launcher-ack.json" -- \
      timeout --signal=TERM --kill-after=30s "${LONG_TIMEOUT_SECONDS}s" \
      env -u PYTHONPATH HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 SGLANG_ENABLE_UNIFIED_RADIX_TREE=1 \
      TOOLGAP_G1_MODEL_PATH="$MODEL_ROOT" "$RUNTIME_VENV/bin/python" "$RUN_DIR/arm-runner.py" \
      "$SCRIPTED_TEST" "$selector"
  ) >"$arm_dir/$arm.log" 2>&1 &
  pid="$!"
  CURRENT_ARM_PID="$pid"
  CURRENT_ARM_PGID=""
  wait_for_arm_handshake "$arm_dir/$arm.launcher-handshake.json" "$arm_dir/$arm.launcher-ack.json" \
    || die "arm $arm launcher handshake failed"
  pgid="$CURRENT_ARM_PGID"
  printf '%s\n' "$pid" >"$arm_dir/$arm.pid"
  printf '%s\n' "$pgid" >"$arm_dir/$arm.pgid"
  "$PYTHON" "$GPU_SAMPLER" --arm-pid "$pid" --poll-seconds 0.25 \
    --samples "$arm_dir/$arm.gpu-samples.json" --union "$arm_dir/$arm.gpu-during.txt" &
  sampler_pid="$!"
  CURRENT_SAMPLER_PID="$sampler_pid"
  if wait "$pid"; then status=0; else status=$?; fi
  if ! wait "$sampler_pid"; then die "arm $arm GPU sampler failed"; fi
  CURRENT_SAMPLER_PID=""
  ps -eo pid=,pgid=,stat=,args= | awk -v group="$pgid" '$2 == group && $3 !~ /^Z/' >"$arm_dir/$arm.process-group-after.txt"
  gpu_pids >"$arm_dir/$arm.gpu-after.txt"
  ss -ltnH | LC_ALL=C sort -u >"$arm_dir/$arm.listeners-after.txt"
  comm -13 "$arm_dir/$arm.gpu-before.txt" "$arm_dir/$arm.gpu-during.txt" >"$arm_dir/$arm.gpu-attributable.txt"
  comm -12 "$arm_dir/$arm.gpu-attributable.txt" "$arm_dir/$arm.gpu-after.txt" >"$arm_dir/$arm.gpu-leaked.txt"
  comm -13 "$arm_dir/$arm.listeners-before.txt" "$arm_dir/$arm.listeners-after.txt" >"$arm_dir/$arm.listeners-leaked.txt"
  "$PYTHON" - "$arm_dir/$arm.cleanup.json" "$arm" "$pid" "$pgid" "$arm_dir/$arm.process-group-after.txt" "$arm_dir/$arm.gpu-leaked.txt" "$arm_dir/$arm.listeners-leaked.txt" <<'PY'
import json, os, pathlib, sys
out = pathlib.Path(sys.argv[1])
arm = sys.argv[2]
pid, pgid = map(int, sys.argv[3:5])
group, gpu, listeners = map(pathlib.Path, sys.argv[5:])
document = {"arm": arm, "pid": pid, "pgid": pgid, "listener_clean": not listeners.read_text(), "pgid_clean": not group.read_text(), "gpu_delta_clean": not gpu.read_text()}
fd = os.open(out, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle: handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(out, 0o444)
PY
  [[ ! -s "$arm_dir/$arm.process-group-after.txt" && ! -s "$arm_dir/$arm.gpu-leaked.txt" && ! -s "$arm_dir/$arm.listeners-leaked.txt" ]] || die "arm $arm cleanup evidence is not clean"
  [[ "$status" == 0 ]] || return "$status"
  "$PYTHON" "$EXTRACTOR" --expected-arm "$arm" --log "$arm_dir/$arm.log" --output "$arm_dir/$arm.record.json"
  CURRENT_ARM_PID=""
  CURRENT_ARM_PGID=""
}
for arm in "${ARMS[@]}"; do run_arm "$arm" "$(selector_for "$arm")"; done
"$PYTHON" - "$RUN_DIR/arm-records.json" "$RUN_DIR/cleanup.json" "$RUN_DIR" "${ARMS[@]}" <<'PY'
import json, os, pathlib, sys
records_out = pathlib.Path(sys.argv[1])
cleanup_out = pathlib.Path(sys.argv[2])
root = pathlib.Path(sys.argv[3])
arms = sys.argv[4:]
records = [json.loads((root / "arms" / f"{arm}.record.json").read_text()) for arm in arms]
cleanup = [json.loads((root / "arms" / f"{arm}.cleanup.json").read_text()) for arm in arms]
for out, document in ((records_out, records), (cleanup_out, {"all_clean": all(all(row[key] for key in ("listener_clean", "pgid_clean", "gpu_delta_clean")) for row in cleanup), "arms": cleanup})):
    fd = os.open(out, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    with os.fdopen(fd, "w", encoding="utf-8") as handle: handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
    os.chmod(out, 0o444)
PY

PHASE="scope"
"$PYTHON" - "$RUN_DIR/scope-scan.log" "$RUN_DIR/resolver-install.log" "$RUN_DIR/source-restore.log" "$RUN_DIR/arms" <<'PY'
import os, pathlib, re, sys
out, resolver, restore, arms_root = map(pathlib.Path, sys.argv[1:])
forbidden = {
    "unapproved_index": r"(pypi\.org|github\.com|download\.pytorch\.org|docs\.sglang\.ai)",
    "source_build": r"\b(cargo|rustc|maturin|building wheel|build backend)\b",
    "treatment_source_install": r"pip install .*sglang/python",
}
hits = []
arm_logs = sorted(arms_root.glob("*.log"))
if len(arm_logs) != 7:
    raise ValueError("scope scan requires every formal arm log")
for path in (resolver, restore, *arm_logs):
    text = path.read_text(encoding="utf-8", errors="replace")
    for label, pattern in forbidden.items():
        if re.search(pattern, text, re.IGNORECASE):
            hits.append(f"{path.name}:{label}")
fd = os.open(out, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle:
    handle.write("scope=clean\n" if not hits else "scope=invalid\n" + "\n".join(hits) + "\n")
os.chmod(out, 0o444)
if hits: raise SystemExit(1)
PY

PHASE="render"
TERMINAL="$("$PYTHON" - "$RUN_DIR/arm-records.json" "$FINALIZER" <<'PY'
import importlib.util, json, pathlib, sys
records, module = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("g1_c_008_finalize", module)
loaded = importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(loaded)
print(loaded.classify_records(json.loads(records.read_text()))[0])
PY
)"
"$PYTHON" "$FINALIZER" render --template "$TEMPLATE" --output "$RUN_DIR/manifest.json" --terminal "$TERMINAL"
(cd "$RUN_DIR" && sha256sum manifest.json >manifest.sha256)
chmod 0444 "$RUN_DIR/manifest.sha256"
PHASE="seal"
"$PYTHON" "$FINALIZER" finish --run-dir "$RUN_DIR"
printf 'G1_C_008_SEALED_ATTEMPT=%s\n' "$RUN_DIR"
