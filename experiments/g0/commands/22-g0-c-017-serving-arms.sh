#!/usr/bin/env bash
# Run the fixed ordinary-serving protocol. It never calls checked demotion.
set -Eeuo pipefail

SCRIPT_REPO_ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd)"
G0_RUN_DIR="${G0_RUN_DIR:-}"
if [[ -z "$G0_RUN_DIR" ]]; then
  echo "set G0_RUN_DIR to the directory emitted by command 20" >&2
  exit 64
fi
G0_RUN_DIR="$(cd "$G0_RUN_DIR" && pwd)"
readonly ADMITTED_RUN_DIR="$G0_RUN_DIR"
readonly FINALIZE="$SCRIPT_REPO_ROOT/experiments/g0/commands/g0_c_017_finalize.py"
readonly VERIFY_IDENTITY="$SCRIPT_REPO_ROOT/experiments/g0/commands/g0_c_008_verify_identity.py"
readonly MODEL_HELPER="$SCRIPT_REPO_ROOT/experiments/g0/commands/g0_c_016_model_seed.py"
any_arm_started=false
current_pid=""
current_pgid=""

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
  if [[ -n "$current_pid" ]]; then
    wait "$current_pid" 2>/dev/null || true
  fi
  current_pid=""
  current_pgid=""
}

write_serving_failure() {
  local status="$1"
  local line="$2"
  local attempt_status=INVALID_SCOPE
  trap - ERR HUP INT TERM
  emergency_cleanup
  if [[ "$any_arm_started" == true ]]; then
    attempt_status=EXECUTION_FAILED_AFTER_START
  fi
  python3 "$FINALIZE" failure --run-dir "$G0_RUN_DIR" \
    --attempt-status "$attempt_status" --phase serving-arms \
    --exit-code "$status" --line "$line" || true
  exit "$status"
}
trap 'write_serving_failure "$?" "$LINENO"' ERR
trap 'write_serving_failure 129 "$LINENO"' HUP
trap 'write_serving_failure 130 "$LINENO"' INT
trap 'write_serving_failure 143 "$LINENO"' TERM

test ! -e "$G0_RUN_DIR/execution-status.json"
test ! -e "$G0_RUN_DIR/artifact-index.json"
test ! -e "$G0_RUN_DIR/completion-receipt.json"
test ! -e "$G0_RUN_DIR/serving-passed.json"
python3 "$VERIFY_IDENTITY" --run-dir "$G0_RUN_DIR" \
  --repo-root "$SCRIPT_REPO_ROOT" \
  --require-receipt controls-passed.json --receipt-status CONTROLS_PASSED
source "$G0_RUN_DIR/runtime.env"
test "$REPO_ROOT" = "$SCRIPT_REPO_ROOT"
test "$G0_RUN_DIR" = "$ADMITTED_RUN_DIR"
test "$(cat "$G0_RUN_DIR/request-input-token-count.txt")" -ge 32
test ! -e "$G0_RUN_DIR/request.json"
cp "$REPO_ROOT/experiments/g0/request.g0-c-007.json" "$G0_RUN_DIR/request.json"

readonly REQUEST_RUNNER="$REPO_ROOT/experiments/g0/commands/g0_c_008_stream_request.py"
readonly PROVENANCE="$REPO_ROOT/experiments/g0/commands/g0_c_008_package_provenance.py"
readonly MODEL="$MODEL_SNAPSHOT"

gpu_pids() {
  nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null |
    awk 'NF && $1 ~ /^[0-9]+$/ {print $1}' | LC_ALL=C sort -n -u
}

process_group_members() {
  local pgid="$1"
  ps -eo pid=,pgid=,stat=,args= |
    awk -v target="$pgid" '$2 == target && $3 !~ /^Z/ {sub(/^[[:space:]]+/, ""); print}'
}

wait_for_health() {
  local arm="$1"
  local port="$2"
  local pid="$3"
  local deadline=$((SECONDS + 900))
  local remaining
  local request_timeout=10
  while true; do
    remaining=$((deadline - SECONDS))
    if (( remaining <= 0 )); then
      echo "900-second /health deadline exceeded" >>"$G0_RUN_DIR/$arm-server.log"
      return 1
    fi
    request_timeout=10
    if (( remaining < request_timeout )); then request_timeout="$remaining"; fi
    if curl --silent --show-error --fail --connect-timeout 5 \
      --max-time "$request_timeout" \
      "http://127.0.0.1:$port/health" >"$G0_RUN_DIR/$arm-health.txt"; then
      return 0
    fi
    if ! kill -0 "$pid" 2>/dev/null; then
      echo "server exited before /health" >>"$G0_RUN_DIR/$arm-server.log"
      return 1
    fi
    remaining=$((deadline - SECONDS))
    if (( remaining <= 0 )); then continue; fi
    if (( remaining < 5 )); then sleep "$remaining"; else sleep 5; fi
  done
}

write_cleanup_status() {
  local arm="$1"
  local port="$2"
  local pid="$3"
  local pgid="$4"
  local passed="$5"
  local server_wait_status="$6"
  "$G0_PYTHON" - \
    "$G0_RUN_DIR/$arm-cleanup-status.json" "$arm" "$port" "$pid" "$pgid" \
    "$passed" "$server_wait_status" \
    "$G0_RUN_DIR/$arm-process-group-after.txt" \
    "$G0_RUN_DIR/$arm-gpu-pids-attributable.txt" \
    "$G0_RUN_DIR/$arm-gpu-pids-leaked.txt" <<'PY'
import json
import os
import pathlib
import sys

(
    output,
    arm,
    port,
    pid,
    pgid,
    passed,
    server_wait_status,
    group_path,
    attributable_path,
    leaked_path,
) = sys.argv[1:]
group = pathlib.Path(group_path).read_text().splitlines()
attributable = pathlib.Path(attributable_path).read_text().splitlines()
leaked = pathlib.Path(leaked_path).read_text().splitlines()
document = {
    "arm": arm,
    "attributable_gpu_pids": [int(item) for item in attributable],
    "attributable_gpu_pid_survivors": [int(item) for item in leaked],
    "passed": passed == "true",
    "pgid": int(pgid),
    "pid": int(pid),
    "port": int(port),
    "process_group_survivors": group,
    "server_wait_status": int(server_wait_status),
}
descriptor = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode=0o444)
with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
    handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(output, 0o444)
PY
}

stop_arm() {
  local arm="$1"
  local port="$2"
  local pid="$3"
  local pgid="$4"
  local deadline
  local passed=true
  local server_wait_status

  gpu_pids >"$G0_RUN_DIR/$arm-gpu-pids-during.txt"
  comm -13 \
    "$G0_RUN_DIR/$arm-gpu-pids-before.txt" \
    "$G0_RUN_DIR/$arm-gpu-pids-during.txt" \
    >"$G0_RUN_DIR/$arm-gpu-pids-attributable.txt"
  if ! kill -0 "$pid" 2>/dev/null; then
    passed=false
  elif ! kill -TERM -- "-$pgid" 2>/dev/null; then
    passed=false
  fi
  deadline=$((SECONDS + 60))
  while true; do
    process_group_members "$pgid" >"$G0_RUN_DIR/$arm-process-group-after.txt"
    ss -ltnp >"$G0_RUN_DIR/$arm-listeners-after-term.txt" 2>&1 || true
    gpu_pids >"$G0_RUN_DIR/$arm-gpu-pids-after.txt"
    comm -12 \
      "$G0_RUN_DIR/$arm-gpu-pids-attributable.txt" \
      "$G0_RUN_DIR/$arm-gpu-pids-after.txt" \
      >"$G0_RUN_DIR/$arm-gpu-pids-leaked.txt"
    if [[ ! -s "$G0_RUN_DIR/$arm-process-group-after.txt" ]] &&
      [[ ! -s "$G0_RUN_DIR/$arm-gpu-pids-leaked.txt" ]] &&
      ! grep -Eq ":$port([^0-9]|$)" "$G0_RUN_DIR/$arm-listeners-after-term.txt"; then
      break
    fi
    if (( SECONDS >= deadline )); then break; fi
    sleep 1
  done
  if [[ -s "$G0_RUN_DIR/$arm-process-group-after.txt" ]] ||
    [[ -s "$G0_RUN_DIR/$arm-gpu-pids-leaked.txt" ]] ||
    grep -Eq ":$port([^0-9]|$)" "$G0_RUN_DIR/$arm-listeners-after-term.txt"; then
    passed=false
    kill -KILL -- "-$pgid" 2>/dev/null || true
  fi
  if wait "$pid" 2>/dev/null; then
    server_wait_status=0
  else
    server_wait_status=$?
  fi
  if [[ "$server_wait_status" != 0 && "$server_wait_status" != 137 &&
    "$server_wait_status" != 143 ]]; then
    passed=false
  fi
  write_cleanup_status \
    "$arm" "$port" "$pid" "$pgid" "$passed" "$server_wait_status"
  current_pid=""
  current_pgid=""
  [[ "$passed" == true ]]
}

run_arm() {
  local arm="$1"
  local port="$2"
  local interpreter="$3"
  local install_root="$4"
  local checkout="$5"
  local server_work="$G0_WORK_ROOT/$arm-server-workdir"
  local pid
  local pgid
  for artifact in \
    "$arm-server.log" "$arm-server.pid" "$arm-server.pgid" \
    "$arm-cleanup-status.json" "$arm-serving-provenance.json"; do
    test ! -e "$G0_RUN_DIR/$artifact"
  done
  "$G0_PYTHON" "$MODEL_HELPER" verify \
    --model-root "$MODEL_SNAPSHOT" --inventory "$MODEL_INVENTORY" \
    --receipt "$MODEL_RECEIPT"
  env -u PYTHONPATH "$interpreter" "$PROVENANCE" \
    --source-root "$checkout" --install-root "$install_root" \
    --expected-interpreter "$interpreter" \
    --output "$G0_RUN_DIR/$arm-serving-provenance.json"
  mkdir "$server_work"
  gpu_pids >"$G0_RUN_DIR/$arm-gpu-pids-before.txt"
  (
    cd "$server_work"
    exec setsid env -u PYTHONPATH CUDA_VISIBLE_DEVICES=0 \
      HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
      SGLANG_ENABLE_UNIFIED_RADIX_TREE=1 \
      SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python \
      "$interpreter" -m sglang.launch_server \
        --model-path "$MODEL" \
        --tokenizer-path "$MODEL" \
        --dtype bfloat16 \
        --kv-cache-dtype bfloat16 \
        --context-length 4096 \
        --page-size 16 \
        --max-total-tokens 4096 \
        --mem-fraction-static 0.70 \
        --tp-size 1 \
        --dp-size 1 \
        --schedule-policy fcfs \
        --random-seed 20260817 \
        --enable-hierarchical-cache \
        --hicache-ratio 2.0 \
        --hicache-write-policy write_through \
        --hicache-io-backend kernel \
        --hicache-mem-layout page_first \
        --enable-session-radix-cache \
        --host 127.0.0.1 \
        --port "$port"
  ) >"$G0_RUN_DIR/$arm-server.log" 2>&1 &
  pid=$!
  printf '%s\n' "$pid" >"$G0_RUN_DIR/$arm-server.pid"
  current_pid="$pid"
  any_arm_started=true
  pgid="$(ps -o pgid= -p "$pid" | xargs)"
  test -n "$pgid"
  test "$pgid" = "$pid"
  printf '%s\n' "$pgid" >"$G0_RUN_DIR/$arm-server.pgid"
  current_pgid="$pgid"

  if ! wait_for_health "$arm" "$port" "$pid"; then
    stop_arm "$arm" "$port" "$pid" "$pgid" || true
    return 1
  fi
  for request_number in 1 2; do
    if ! "$interpreter" "$REQUEST_RUNNER" \
      --base-url "http://127.0.0.1:$port" \
      --request-json "$G0_RUN_DIR/request.json" \
      --raw-output "$G0_RUN_DIR/$arm-request-$request_number.sse" \
      --parsed-output "$G0_RUN_DIR/$arm-request-$request_number.json" \
      --connect-timeout 10 --terminal-timeout 180; then
      stop_arm "$arm" "$port" "$pid" "$pgid" || true
      return 1
    fi
  done
  stop_arm "$arm" "$port" "$pid" "$pgid"
}

run_arm stock 30000 "$STOCK_PYTHON" "$STOCK_VENV" "$STOCK_CHECKOUT"
run_arm treatment 30001 "$TREATMENT_PYTHON" "$TREATMENT_VENV" "$TREATMENT_CHECKOUT"
python3 "$VERIFY_IDENTITY" --run-dir "$G0_RUN_DIR" \
  --repo-root "$SCRIPT_REPO_ROOT" \
  --require-receipt controls-passed.json --receipt-status CONTROLS_PASSED
manifest_sha="$(sha256sum "$G0_RUN_DIR/manifest.json" | awk '{print $1}')"
"$G0_PYTHON" "$FINALIZE" receipt \
  --output "$G0_RUN_DIR/serving-passed.json" \
  --status SERVING_PASSED --manifest-sha256 "$manifest_sha"

trap - ERR HUP INT TERM
echo "SERVING_ARMS_PASSED: $G0_RUN_DIR"
