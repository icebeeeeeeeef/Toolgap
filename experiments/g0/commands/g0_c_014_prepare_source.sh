#!/usr/bin/env bash
# Restore the two fixed G0-C-014 SGLang checkouts from one operator-staged seed.
set -euo pipefail

if [[ "$#" != 8 ]]; then
  echo "usage: $0 ARCHIVE SHA256 INPUT_ROOT STOCK TREATMENT REMOTE COMMIT TREE" >&2
  exit 64
fi

readonly ARCHIVE="$1"
readonly EXPECTED_SHA256="$2"
readonly INPUT_ROOT="$3"
readonly STOCK_CHECKOUT="$4"
readonly TREATMENT_CHECKOUT="$5"
readonly CANONICAL_REMOTE="$6"
readonly BASE_COMMIT="$7"
readonly BASE_TREE="$8"

[[ -f "$ARCHIVE" ]]
[[ "$EXPECTED_SHA256" =~ ^[0-9a-f]{64}$ ]]
[[ "$BASE_COMMIT" =~ ^[0-9a-f]{40}$ ]]
[[ "$BASE_TREE" =~ ^[0-9a-f]{40}$ ]]
[[ ! -e "$INPUT_ROOT" && ! -e "$STOCK_CHECKOUT" && ! -e "$TREATMENT_CHECKOUT" ]]
test "$(sha256sum "$ARCHIVE" | awk '{print $1}')" = "$EXPECTED_SHA256"

mkdir "$INPUT_ROOT"
tar -xzf "$ARCHIVE" -C "$INPUT_ROOT"
readonly SEED_REPOSITORY="$INPUT_ROOT/sglang-source.git"
test "$(git -C "$SEED_REPOSITORY" rev-parse --is-bare-repository)" = true
git -C "$SEED_REPOSITORY" fsck --full
test "$(git -C "$SEED_REPOSITORY" cat-file -t "$BASE_COMMIT")" = commit
test "$(git -C "$SEED_REPOSITORY" rev-parse "$BASE_COMMIT^{tree}")" = "$BASE_TREE"

for checkout in "$STOCK_CHECKOUT" "$TREATMENT_CHECKOUT"; do
  git clone --no-local "$SEED_REPOSITORY" "$checkout"
  git -C "$checkout" checkout --detach "$BASE_COMMIT"
  git -C "$checkout" remote set-url origin "$CANONICAL_REMOTE"
  test "$(git -C "$checkout" remote get-url origin)" = "$CANONICAL_REMOTE"
  test "$(git -C "$checkout" rev-parse HEAD)" = "$BASE_COMMIT"
  test "$(git -C "$checkout" rev-parse 'HEAD^{tree}')" = "$BASE_TREE"
  test -z "$(git -C "$checkout" status --porcelain)"
done
