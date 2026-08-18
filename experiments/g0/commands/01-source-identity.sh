#!/usr/bin/env bash
set -euo pipefail

SGLANG_G0_COMMIT="92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2"
SGLANG_G0_CHECKOUT="${SGLANG_G0_CHECKOUT:-/private/tmp/toolgap-kv-g0-sglang-92b1d382}"

git -C "${SGLANG_G0_CHECKOUT}" remote get-url origin
git -C "${SGLANG_G0_CHECKOUT}" show -s \
  --format='%H%n%T%n%P%n%an%n%aI%n%s' "${SGLANG_G0_COMMIT}"
git -C "${SGLANG_G0_CHECKOUT}" sparse-checkout list
git -C "${SGLANG_G0_CHECKOUT}" status --short --branch
git -C "${SGLANG_G0_CHECKOUT}" diff --exit-code "${SGLANG_G0_COMMIT}"
