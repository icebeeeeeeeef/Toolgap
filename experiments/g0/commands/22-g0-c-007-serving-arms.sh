#!/usr/bin/env bash
# Run the fixed ordinary-serving protocol. It never calls the checked-demote API.
set -eo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd)"
G0_RUN_DIR="$G0_RUN_DIR"
if [[ -z "$G0_RUN_DIR" ]]; then
  echo "set G0_RUN_DIR to the directory emitted by command 20" >&2
  exit 64
fi
set -u
source "$G0_RUN_DIR/runtime.env"
sha256sum --check "$G0_RUN_DIR/manifest.sha256"
serving_started=false
write_serving_failure() {
  local status="$1"
  local line="$2"
  local attempt_status=INVALID_SCOPE
  trap - ERR
  if [[ "$serving_started" == true ]]; then
    attempt_status=EXECUTION_FAILED_AFTER_START
  fi
  if [[ -e "$G0_RUN_DIR/execution-status.json" ]]; then
    echo "refusing to replace existing terminal status" >&2
    exit "$status"
  fi
  {
    printf '{\n'
    printf '  "attempt_status": "%s",\n' "$attempt_status"
    printf '  "phase": "serving-arms",\n'
    printf '  "exit_code": %s,\n' "$status"
    printf '  "line": %s\n' "$line"
    printf '}\n'
  } >"$G0_RUN_DIR/execution-status.json"
  exit "$status"
}
trap 'write_serving_failure "$?" "$LINENO"' ERR
test "$(cat "$G0_RUN_DIR/request-input-token-count.txt")" -ge 32
test ! -e "$G0_RUN_DIR/request.json"
test ! -e "$G0_RUN_DIR/execution-status.json"
for artifact in stock-server.log treatment-server.log stock-server.pid treatment-server.pid; do
  test ! -e "$G0_RUN_DIR/$artifact"
done
cp "$REPO_ROOT/experiments/g0/request.g0-c-007.json" "$G0_RUN_DIR/request.json"

readonly REQUEST_RUNNER="$REPO_ROOT/experiments/g0/commands/g0_c_007_stream_request.py"
readonly MODEL="Qwen/Qwen2.5-0.5B-Instruct"
readonly REVISION="c89bee90d9f811437d9735454613c35b4a3c4dc8"

stop_server() {
  local arm="$1"
  local port="$2"
  local pid="$3"
  local deadline
  local process_gone=false
  kill -TERM "$pid" 2>/dev/null || true
  deadline=$((SECONDS + 60))
  while kill -0 "$pid" 2>/dev/null; do
    if (( SECONDS >= deadline )); then
      break
    fi
    sleep 1
  done
  if ! kill -0 "$pid" 2>/dev/null; then
    process_gone=true
  fi
  ss -ltnp >"$G0_RUN_DIR/$arm-listeners-after-term.txt" 2>&1 || true
  if [[ "$process_gone" != true ]] ||
    grep -Eq ":$port([^0-9]|$)" "$G0_RUN_DIR/$arm-listeners-after-term.txt"; then
    {
      printf 'passed=false\n'
      printf 'pid=%s\n' "$pid"
      printf 'port=%s\n' "$port"
      printf 'reason=process-or-listener-survived-60-second-SIGTERM-window\n'
    } >"$G0_RUN_DIR/$arm-cleanup-status.txt"
    kill -KILL "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
    return 1
  fi
  wait "$pid" 2>/dev/null || true
  {
    printf 'passed=true\n'
    printf 'pid=%s\n' "$pid"
    printf 'port=%s\n' "$port"
    printf 'reason=SIGTERM-cleanup-complete\n'
  } >"$G0_RUN_DIR/$arm-cleanup-status.txt"
}

wait_for_health() {
  local arm="$1"
  local port="$2"
  local pid="$3"
  local deadline=$((SECONDS + 900))
  while true; do
    if curl --silent --show-error --fail --connect-timeout 5 \
      "http://127.0.0.1:$port/health" >"$G0_RUN_DIR/$arm-health.json"; then
      return 0
    fi
    if ! kill -0 "$pid" 2>/dev/null; then
      echo "server exited before /health" >>"$G0_RUN_DIR/$arm-server.log"
      return 1
    fi
    if (( SECONDS >= deadline )); then
      echo "900-second /health deadline exceeded" >>"$G0_RUN_DIR/$arm-server.log"
      return 1
    fi
    sleep 5
  done
}

run_arm() {
  local arm="$1"
  local port="$2"
  local interpreter="$3"
  local server_work="$G0_RUN_DIR/$arm-server-workdir"
  local pid
  mkdir "$server_work"
  nvidia-smi >"$G0_RUN_DIR/$arm-gpu-before.txt"
  (
    cd "$server_work"
    exec env CUDA_VISIBLE_DEVICES=0 \
      SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python \
      "$interpreter" -m sglang.launch_server \
        --model-path "$MODEL" \
        --revision "$REVISION" \
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
  if ! wait_for_health "$arm" "$port" "$pid"; then
    stop_server "$arm" "$port" "$pid" || true
    nvidia-smi >"$G0_RUN_DIR/$arm-gpu-after.txt" || true
    return 1
  fi
  if ! "$interpreter" "$REQUEST_RUNNER" \
    --base-url "http://127.0.0.1:$port" \
    --request-json "$G0_RUN_DIR/request.json" \
    --raw-output "$G0_RUN_DIR/$arm-request-1.sse" \
    --parsed-output "$G0_RUN_DIR/$arm-request-1.json"; then
    stop_server "$arm" "$port" "$pid" || true
    nvidia-smi >"$G0_RUN_DIR/$arm-gpu-after.txt" || true
    return 1
  fi
  if ! "$interpreter" "$REQUEST_RUNNER" \
    --base-url "http://127.0.0.1:$port" \
    --request-json "$G0_RUN_DIR/request.json" \
    --raw-output "$G0_RUN_DIR/$arm-request-2.sse" \
    --parsed-output "$G0_RUN_DIR/$arm-request-2.json"; then
    stop_server "$arm" "$port" "$pid" || true
    nvidia-smi >"$G0_RUN_DIR/$arm-gpu-after.txt" || true
    return 1
  fi
  if ! stop_server "$arm" "$port" "$pid"; then
    nvidia-smi >"$G0_RUN_DIR/$arm-gpu-after.txt" || true
    return 1
  fi
  nvidia-smi >"$G0_RUN_DIR/$arm-gpu-after.txt"
}

serving_started=true
run_arm stock 30000 "$STOCK_PYTHON"
run_arm treatment 30001 "$TREATMENT_PYTHON"
sha256sum --check "$G0_RUN_DIR/manifest.sha256"
trap - ERR
echo "SERVING_ARMS_PASSED: $G0_RUN_DIR"
