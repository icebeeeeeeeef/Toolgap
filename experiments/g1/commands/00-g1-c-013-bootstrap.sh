#!/usr/bin/env bash
# Restore exactly the ToolGap revision bound by a G1-C-013 input manifest.
set -Eeuo pipefail

INPUT_MANIFEST="${G1_C_013_INPUT_MANIFEST:-}"
TOOLGAP_SEED_ARCHIVE="${G1_C_013_TOOLGAP_SEED_ARCHIVE:-}"
BOOTSTRAP_ROOT="${G1_C_013_BOOTSTRAP_ROOT:-}"
PYTHON="${G1_C_013_PYTHON:-python3}"

die() { printf 'g1-c-013 bootstrap: %s\n' "$*" >&2; exit 2; }
[[ "$INPUT_MANIFEST" = /* && "$TOOLGAP_SEED_ARCHIVE" = /* && "$BOOTSTRAP_ROOT" = /* ]] || die 'all paths must be absolute'
[[ -f "$INPUT_MANIFEST" && -f "$TOOLGAP_SEED_ARCHIVE" && ! -e "$BOOTSTRAP_ROOT" ]] || die 'invalid input paths'
command -v "$PYTHON" >/dev/null || die 'Python is unavailable'
PYTHON="$(command -v "$PYTHON")"
SELF_PATH="$(cd -- "$(dirname -- "$0")" && pwd -P)/$(basename -- "$0")"
[[ -f "$SELF_PATH" && ! -L "$SELF_PATH" ]] || die 'bootstrap must be a regular file'

mapfile -t EXPECTED < <("$PYTHON" - "$SELF_PATH" "$INPUT_MANIFEST" <<'PY'
import hashlib, json, pathlib, re, sys

script, manifest_path = map(pathlib.Path, sys.argv[1:])
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
binding = manifest.get("static_inputs", {}).get(
    "experiments/g1/commands/00-g1-c-013-bootstrap.sh"
)
if not isinstance(binding, dict) or set(binding) != {"sha256", "size_bytes"}:
    raise ValueError("input manifest omits bootstrap binding")
if binding["sha256"] != hashlib.sha256(script.read_bytes()).hexdigest() or binding["size_bytes"] != script.stat().st_size:
    raise ValueError("bootstrap bytes differ from input manifest")
identity = manifest.get("identity")
archive = manifest.get("archives", {}).get("toolgap_source_seed")
if not isinstance(identity, dict) or not isinstance(archive, dict):
    raise ValueError("input manifest lacks identity or ToolGap seed")
for key, value in {"bundle_id": "G1-C-013", "claim_state": "roadmap", "gate": "G1"}.items():
    if identity.get(key) != value:
        raise ValueError("input manifest identity differs")
for key, length in (("toolgap_commit", 40), ("toolgap_tree", 40), ("sha256", 64)):
    value = identity.get(key) if key != "sha256" else archive.get(key)
    if not isinstance(value, str) or not re.fullmatch(rf"[0-9a-f]{{{length}}}", value):
        raise ValueError(f"invalid {key}")
if not isinstance(identity.get("toolgap_remote"), str):
    raise ValueError("ToolGap remote is invalid")
print(identity["toolgap_commit"])
print(identity["toolgap_tree"])
print(identity["toolgap_remote"])
print(archive["sha256"])
PY
)
readonly EXPECTED_COMMIT="${EXPECTED[0]}" EXPECTED_TREE="${EXPECTED[1]}" EXPECTED_REMOTE="${EXPECTED[2]}" EXPECTED_SEED_SHA256="${EXPECTED[3]}"
[[ "$(sha256sum "$TOOLGAP_SEED_ARCHIVE" | awk '{print $1}')" == "$EXPECTED_SEED_SHA256" ]] || die 'ToolGap seed hash differs'

"$PYTHON" - "$TOOLGAP_SEED_ARCHIVE" <<'PY'
import pathlib, sys, tarfile

archive = pathlib.Path(sys.argv[1])
names = set()
with tarfile.open(archive, "r:*") as bundle:
    for member in bundle.getmembers():
        pure, name = pathlib.PurePosixPath(member.name), member.name.rstrip("/")
        if (
            pure.is_absolute() or ".." in pure.parts or not pure.parts
            or pure.parts[0] != "toolgap-source.git" or name in names
            or not (member.isdir() or member.isfile())
        ):
            raise ValueError(f"unsafe ToolGap seed member: {member.name}")
        names.add(name)
if not names:
    raise ValueError("empty ToolGap seed")
PY

mkdir "$BOOTSTRAP_ROOT"
tar --no-same-owner -xzf "$TOOLGAP_SEED_ARCHIVE" -C "$BOOTSTRAP_ROOT"
BARE="$BOOTSTRAP_ROOT/toolgap-source.git"
CHECKOUT="$BOOTSTRAP_ROOT/toolgap"
git -C "$BARE" fsck --full
[[ "$(git -C "$BARE" rev-parse --is-bare-repository)" == true ]]
[[ "$(git -C "$BARE" cat-file -t "$EXPECTED_COMMIT")" == commit ]]
[[ "$(git -C "$BARE" rev-parse "$EXPECTED_COMMIT^{tree}")" == "$EXPECTED_TREE" ]]
git clone --no-local "$BARE" "$CHECKOUT"
git -C "$CHECKOUT" checkout --detach "$EXPECTED_COMMIT"
git -C "$CHECKOUT" remote set-url origin "$EXPECTED_REMOTE"
[[ "$(git -C "$CHECKOUT" rev-parse HEAD)" == "$EXPECTED_COMMIT" ]]
[[ "$(git -C "$CHECKOUT" rev-parse 'HEAD^{tree}')" == "$EXPECTED_TREE" ]]
[[ "$(git -C "$CHECKOUT" remote get-url origin)" == "$EXPECTED_REMOTE" ]]
test -z "$(git -C "$CHECKOUT" status --porcelain)"

"$PYTHON" - "$BOOTSTRAP_ROOT/bootstrap-receipt.json" "$INPUT_MANIFEST" "$TOOLGAP_SEED_ARCHIVE" "$CHECKOUT" "$EXPECTED_COMMIT" "$EXPECTED_TREE" "$EXPECTED_REMOTE" <<'PY'
import hashlib, json, os, pathlib, sys

out, manifest, seed, checkout = map(pathlib.Path, sys.argv[1:5])
commit, tree, remote = sys.argv[5:]
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
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
fd = os.open(out, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle:
    handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(out, 0o444)
PY
printf 'TOOLGAP_CHECKOUT=%s\nG1_C_013_BOOTSTRAP_RECEIPT=%s\n' "$CHECKOUT" "$BOOTSTRAP_ROOT/bootstrap-receipt.json"
