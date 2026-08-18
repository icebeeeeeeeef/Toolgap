#!/usr/bin/env bash
set -euo pipefail

SGLANG_G0_CHECKOUT="/private/tmp/toolgap-kv-g0-sglang-92b1d382"
SGLANG_G0_COMMIT="92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2"
SGLANG_G0_TREE="25e9bf86d04c27fe380024d9c8c421c3b5b51f3c"

if test "$(uname -s)" != "Linux" || test "$(uname -m)" != "x86_64"; then
  echo "BLOCKED_BEFORE_EXECUTION: requires frozen Ubuntu x86_64 CUDA testbed"
  exit 78
fi
if ! command -v nvidia-smi >/dev/null || ! command -v python3.12 >/dev/null; then
  echo "BLOCKED_BEFORE_EXECUTION: requires nvidia-smi and python3.12"
  exit 78
fi
test "$(git -C "${SGLANG_G0_CHECKOUT}" rev-parse HEAD)" = "${SGLANG_G0_COMMIT}"
test "$(git -C "${SGLANG_G0_CHECKOUT}" rev-parse 'HEAD^{tree}')" = "${SGLANG_G0_TREE}"

uname -a
nvidia-smi --query-gpu=name,uuid,driver_version,memory.total --format=csv,noheader
python3.12 --version
python3.12 -c 'import sglang, torch, transformers; print("sglang", sglang.__version__); print("torch", torch.__version__, "cuda", torch.version.cuda); print("transformers", transformers.__version__)'
python3.12 -m pip freeze

cd "${SGLANG_G0_CHECKOUT}"
exec env \
  CUDA_VISIBLE_DEVICES=0 \
  SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python \
  python3.12 -m sglang.launch_server \
    --model-path Qwen/Qwen2.5-0.5B-Instruct \
    --revision c89bee90d9f811437d9735454613c35b4a3c4dc8 \
    --tokenizer-path Qwen/Qwen2.5-0.5B-Instruct \
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
    --port 30000
