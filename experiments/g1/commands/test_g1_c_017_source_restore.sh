#!/usr/bin/env bash
# Exercise C-003's patch restore and changed-path inventory in a clean Git fixture.
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd -P)"
RUNNER="$ROOT/experiments/g1/commands/20-g1-c-017.sh"
TEMPORARY="$(mktemp -d "${TMPDIR:-/tmp}/g1-c-017-source-restore.XXXXXX")"
trap 'python3 -c '\''import shutil, sys; shutil.rmtree(sys.argv[1], ignore_errors=True)'\'' "$TEMPORARY"' EXIT

sed -n '/BEGIN_FROZEN_PATCH_RESTORE_HELPER/,/END_FROZEN_PATCH_RESTORE_HELPER/p' "$RUNNER" >"$TEMPORARY/helper.sh"
sed -n '/BEGIN_CHANGED_PATH_INVENTORY_HELPER/,/END_CHANGED_PATH_INVENTORY_HELPER/p' "$RUNNER" >>"$TEMPORARY/helper.sh"
die() { printf 'fixture failure: %s\n' "$*" >&2; return 2; }
PYTHON="$(command -v python3)"
# shellcheck source=/dev/null
source "$TEMPORARY/helper.sh"

TREATMENT="$TEMPORARY/treatment"
PATCH_ROOT="$TEMPORARY/patches"
mkdir "$TREATMENT" "$PATCH_ROOT"
git -C "$TREATMENT" init -q
git -C "$TREATMENT" config user.name fixture
git -C "$TREATMENT" config user.email fixture@invalid
printf 'base\n' >"$TREATMENT/base.txt"
printf 'tracked two base\n' >"$TREATMENT/tracked-two.txt"
git -C "$TREATMENT" add base.txt tracked-two.txt
git -C "$TREATMENT" commit -qm base

PATCH_ONE="$PATCH_ROOT/0001-atomic-checked-demote.patch"
PATCH_TWO="$PATCH_ROOT/0002-g1-scripted-forced-demote-c017.patch"
PATCH_THREE="$PATCH_ROOT/0003-cuda12-compat-packaging.patch"
cat >"$PATCH_ONE" <<'PATCH'
diff --git a/base.txt b/base.txt
index df967b9..43dd47e 100644
--- a/base.txt
+++ b/base.txt
@@ -1 +1 @@
-base
+base one
PATCH
cat >"$PATCH_TWO" <<'PATCH'
diff --git a/tracked-two.txt b/tracked-two.txt
index 04e0d1e..bdf97f8 100644
--- a/tracked-two.txt
+++ b/tracked-two.txt
@@ -1 +1 @@
-tracked two base
+tracked two
PATCH
cat >"$PATCH_THREE" <<'PATCH'
diff --git a/test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py b/test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py
new file mode 100644
index 0000000..3f78685
--- /dev/null
+++ b/test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py
@@ -0,0 +1 @@
+def test_frozen_fixture(): pass
PATCH

apply_frozen_patches "$TREATMENT" "$PATCH_ONE" "$PATCH_TWO" "$PATCH_THREE" >"$TEMPORARY/restore.log"
CHANGED_OUTPUT="$(changed_regular_paths "$TREATMENT")"
CHANGED=()
while IFS= read -r changed_path; do
  [[ -n "$changed_path" ]] && CHANGED+=("$changed_path")
done <<<"$CHANGED_OUTPUT"
EXPECTED=(
  base.txt
  test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py
  tracked-two.txt
)
[[ "${CHANGED[*]}" == "${EXPECTED[*]}" ]]
[[ "$(git -C "$TREATMENT" ls-files --others --exclude-standard)" == 'test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py' ]]
for patch in "$PATCH_ONE" "$PATCH_TWO" "$PATCH_THREE"; do
  expected="$(sha256sum "$patch" | awk '{print $1}')"
  grep -Fq "$expected" "$TEMPORARY/restore.log"
done

# This must be checked before adding the patch-created test file to the index.
git -C "$TREATMENT" add -A
git -C "$TREATMENT" commit -qm patched
test -z "$(git -C "$TREATMENT" status --porcelain)"
printf 'G1-C-017 source restore inventory regression passed\n'
