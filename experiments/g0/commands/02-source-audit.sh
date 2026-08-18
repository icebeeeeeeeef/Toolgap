#!/usr/bin/env bash
set -euo pipefail

SGLANG_G0_COMMIT="92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2"
SGLANG_G0_CHECKOUT="${SGLANG_G0_CHECKOUT:-/private/tmp/toolgap-kv-g0-sglang-92b1d382}"

test "$(git -C "${SGLANG_G0_CHECKOUT}" rev-parse HEAD)" = \
  "${SGLANG_G0_COMMIT}"
test -z "$(git -C "${SGLANG_G0_CHECKOUT}" status --porcelain)"

git -C "${SGLANG_G0_CHECKOUT}" grep -n -E \
  'release_radix_session|SessionRefTracker|session_ids|session_ref' \
  "${SGLANG_G0_COMMIT}" -- \
  python/sglang/srt/mem_cache \
  python/sglang/srt/managers \
  test/registered/unit/mem_cache

git -C "${SGLANG_G0_CHECKOUT}" grep -n -E \
  'def demote|backuped|host_value|host_lock_ref|lock_ref|evictable' \
  "${SGLANG_G0_COMMIT}" -- \
  python/sglang/srt/mem_cache \
  test/registered/unit/mem_cache

git -C "${SGLANG_G0_CHECKOUT}" grep -n -E \
  'write_back|write_through|writing|loading|pending|transfer|completion|event' \
  "${SGLANG_G0_COMMIT}" -- \
  python/sglang/srt/mem_cache \
  python/sglang/srt/managers \
  test/registered/unit/mem_cache \
  benchmark/hicache \
  docs/backend/hicache

git -C "${SGLANG_G0_CHECKOUT}" grep -n -E \
  'available_size|free.*page|free.*block|allocator|evict' \
  "${SGLANG_G0_COMMIT}" -- \
  python/sglang/srt/mem_cache \
  python/sglang/srt/managers \
  test/registered/unit/mem_cache
