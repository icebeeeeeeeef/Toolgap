#!/usr/bin/env bash
# Restore one exact ToolGap checkout from the G1-PREFLIGHT-001 bare seed.
set -Eeuo pipefail

INPUT_MANIFEST="${G1_PREFLIGHT_INPUT_MANIFEST:-}"
TOOLGAP_SEED_ARCHIVE="${G1_PREFLIGHT_TOOLGAP_SEED_ARCHIVE:-}"
BOOTSTRAP_ROOT="${G1_PREFLIGHT_BOOTSTRAP_ROOT:-}"
PYTHON="${G1_PREFLIGHT_PYTHON:-python3}"

[[ "$INPUT_MANIFEST" = /* && "$TOOLGAP_SEED_ARCHIVE" = /* && "$BOOTSTRAP_ROOT" = /* ]]
[[ -f "$INPUT_MANIFEST" && -f "$TOOLGAP_SEED_ARCHIVE" && ! -e "$BOOTSTRAP_ROOT" ]]
command -v "$PYTHON" >/dev/null
PYTHON="$(command -v "$PYTHON")"

expected="$($PYTHON - "$INPUT_MANIFEST" <<'PY'
import json, pathlib, re, sys

manifest = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
identity = manifest["identity"]
archive = manifest["archives"]["toolgap_source_seed"]
for value, length in ((identity["toolgap_commit"], 40), (identity["toolgap_tree"], 40), (archive["sha256"], 64)):
    if not isinstance(value, str) or not re.fullmatch(rf"[0-9a-f]{{{length}}}", value):
        raise ValueError("input manifest has an invalid ToolGap identity")
if identity["bundle_id"] != "G1-PREFLIGHT-001" or identity["gate_decision"] != "N/A: preformal runtime validation only":
    raise ValueError("input manifest has the wrong preflight identity")
print(identity["toolgap_commit"])
print(identity["toolgap_tree"])
print(identity["toolgap_remote"])
print(archive["sha256"])
PY
)"
values=()
while IFS= read -r value; do
  values+=("$value")
done <<<"$expected"
readonly EXPECTED_COMMIT="${values[0]}"
readonly EXPECTED_TREE="${values[1]}"
readonly EXPECTED_REMOTE="${values[2]}"
readonly EXPECTED_SEED_SHA256="${values[3]}"
test "$(sha256sum "$TOOLGAP_SEED_ARCHIVE" | awk '{print $1}')" = "$EXPECTED_SEED_SHA256"

"$PYTHON" - "$TOOLGAP_SEED_ARCHIVE" <<'PY'
import pathlib, sys, tarfile

archive = pathlib.Path(sys.argv[1])
names = set()
with tarfile.open(archive, "r:*") as bundle:
    for member in bundle.getmembers():
        pure = pathlib.PurePosixPath(member.name)
        if (
            pure.is_absolute() or ".." in pure.parts or not pure.parts
            or pure.parts[0] != "toolgap-source.git"
            or member.name.rstrip("/") in names
            or not (member.isdir() or member.isfile())
        ):
            raise ValueError(f"unsafe ToolGap seed member: {member.name}")
        names.add(member.name.rstrip("/"))
if not names:
    raise ValueError("empty ToolGap seed")
PY

mkdir "$BOOTSTRAP_ROOT"
tar -xzf "$TOOLGAP_SEED_ARCHIVE" -C "$BOOTSTRAP_ROOT"
readonly BARE="$BOOTSTRAP_ROOT/toolgap-source.git"
readonly CHECKOUT="$BOOTSTRAP_ROOT/toolgap"
git -C "$BARE" fsck --full
test "$(git -C "$BARE" rev-parse --is-bare-repository)" = true
test "$(git -C "$BARE" cat-file -t "$EXPECTED_COMMIT")" = commit
test "$(git -C "$BARE" rev-parse "$EXPECTED_COMMIT^{tree}")" = "$EXPECTED_TREE"
git clone --no-local "$BARE" "$CHECKOUT"
git -C "$CHECKOUT" checkout --detach "$EXPECTED_COMMIT"
git -C "$CHECKOUT" remote set-url origin "$EXPECTED_REMOTE"
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = "$EXPECTED_COMMIT"
test "$(git -C "$CHECKOUT" rev-parse 'HEAD^{tree}')" = "$EXPECTED_TREE"
test "$(git -C "$CHECKOUT" remote get-url origin)" = "$EXPECTED_REMOTE"
test -z "$(git -C "$CHECKOUT" status --porcelain)"

"$PYTHON" - "$BOOTSTRAP_ROOT/bootstrap-receipt.json" "$INPUT_MANIFEST" "$TOOLGAP_SEED_ARCHIVE" "$CHECKOUT" "$EXPECTED_COMMIT" "$EXPECTED_TREE" "$EXPECTED_REMOTE" <<'PY'
import hashlib, json, os, pathlib, sys

output, manifest, seed, checkout = map(pathlib.Path, sys.argv[1:5])
commit, tree, remote = sys.argv[5:]
def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()
document = {
    "input_manifest_path": str(manifest.resolve()),
    "input_manifest_sha256": digest(manifest),
    "toolgap_checkout": str(checkout.resolve()),
    "toolgap_commit": commit,
    "toolgap_remote": remote,
    "toolgap_seed_path": str(seed.resolve()),
    "toolgap_seed_sha256": digest(seed),
    "toolgap_tree": tree,
}
fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle:
    handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(output, 0o444)
PY
printf 'TOOLGAP_CHECKOUT=%s\n' "$CHECKOUT"
printf 'G1_PREFLIGHT_BOOTSTRAP_RECEIPT=%s\n' "$BOOTSTRAP_ROOT/bootstrap-receipt.json"
