#!/usr/bin/env bash
# Exercise the C-002 runner's exact explicit-patch restore helper in a clean Git fixture.
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd -P)"
RUNNER="$ROOT/experiments/g1/commands/20-g1-c-002.sh"
TEMPORARY="$(mktemp -d "${TMPDIR:-/tmp}/g1-c-002-source-restore.XXXXXX")"
trap 'rm -rf "$TEMPORARY"' EXIT

sed -n '/BEGIN_FROZEN_PATCH_RESTORE_HELPER/,/END_FROZEN_PATCH_RESTORE_HELPER/p' "$RUNNER" >"$TEMPORARY/helper.sh"
die() { printf 'fixture failure: %s\n' "$*" >&2; return 2; }
# shellcheck source=/dev/null
source "$TEMPORARY/helper.sh"

TREATMENT="$TEMPORARY/treatment"
PATCH_ROOT="$TEMPORARY/patches"
mkdir "$TREATMENT" "$PATCH_ROOT"
git -C "$TREATMENT" init -q
git -C "$TREATMENT" config user.name fixture
git -C "$TREATMENT" config user.email fixture@invalid
printf 'base\n' >"$TREATMENT/base.txt"
git -C "$TREATMENT" add base.txt
git -C "$TREATMENT" commit -qm base

write_patch() {
  local number="$1" filename="$2" payload="$3"
  printf '%s\n' "diff --git a/$filename b/$filename" >"$PATCH_ROOT/$number"
  printf '%s\n' 'new file mode 100644' >>"$PATCH_ROOT/$number"
  printf '%s\n' '--- /dev/null' >>"$PATCH_ROOT/$number"
  printf '%s\n' "+++ b/$filename" >>"$PATCH_ROOT/$number"
  printf '%s\n' '@@ -0,0 +1 @@' >>"$PATCH_ROOT/$number"
  printf '+%s\n' "$payload" >>"$PATCH_ROOT/$number"
}

PATCH_ONE="$PATCH_ROOT/0001-atomic-checked-demote.patch"
PATCH_TWO="$PATCH_ROOT/0002-g1-scripted-forced-demote.patch"
PATCH_THREE="$PATCH_ROOT/0003-cuda12-compat-packaging.patch"
write_patch "$(basename "$PATCH_ONE")" one.txt one
write_patch "$(basename "$PATCH_TWO")" two.txt two
write_patch "$(basename "$PATCH_THREE")" three.txt three

apply_frozen_patches "$TREATMENT" "$PATCH_ONE" "$PATCH_TWO" "$PATCH_THREE" >"$TEMPORARY/restore.log"
for file in one.txt two.txt three.txt; do test "$(cat "$TREATMENT/$file")" == "${file%.txt}"; done
test "$(git -C "$TREATMENT" ls-files --others --exclude-standard | LC_ALL=C sort)" == $'one.txt\nthree.txt\ntwo.txt'
for patch in "$PATCH_ONE" "$PATCH_TWO" "$PATCH_THREE"; do
  expected="$(sha256sum "$patch" | awk '{print $1}')"
  grep -Fq "$expected" "$TEMPORARY/restore.log"
done
printf 'G1-C-002 explicit source restore regression passed\n'
