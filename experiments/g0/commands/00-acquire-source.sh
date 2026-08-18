#!/usr/bin/env bash
set -euo pipefail

SGLANG_G0_COMMIT="92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2"
SGLANG_G0_REMOTE="https://github.com/sgl-project/sglang.git"
SGLANG_G0_CHECKOUT="${SGLANG_G0_CHECKOUT:-/private/tmp/toolgap-kv-g0-sglang-92b1d382}"

if [[ ! -e "${SGLANG_G0_CHECKOUT}" ]]; then
  git clone --filter=blob:none --no-checkout \
    "${SGLANG_G0_REMOTE}" "${SGLANG_G0_CHECKOUT}"
fi

test "$(git -C "${SGLANG_G0_CHECKOUT}" remote get-url origin)" = \
  "${SGLANG_G0_REMOTE}"
git -C "${SGLANG_G0_CHECKOUT}" cat-file -e "${SGLANG_G0_COMMIT}^{commit}"
git -C "${SGLANG_G0_CHECKOUT}" sparse-checkout init --cone
git -C "${SGLANG_G0_CHECKOUT}" sparse-checkout set \
  python/sglang/srt/mem_cache \
  python/sglang/srt/managers \
  test/registered/unit/mem_cache \
  benchmark/hicache \
  docs/backend/hicache
git -C "${SGLANG_G0_CHECKOUT}" checkout --detach "${SGLANG_G0_COMMIT}"
test "$(git -C "${SGLANG_G0_CHECKOUT}" rev-parse HEAD)" = \
  "${SGLANG_G0_COMMIT}"
test -z "$(git -C "${SGLANG_G0_CHECKOUT}" status --porcelain)"
