#!/usr/bin/env bash
# Upload one exact CUDA12-COMPAT-001 input set and emit its OSS version receipt.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/stage-cuda12-compat-001-inputs-oss.sh \
    --input-manifest /absolute/path/input-manifest.json \
    --input-dir /absolute/path/to/input-files \
    --bootstrap /absolute/path/00-cuda12-compat-001-bootstrap.sh \
    --prereqs /absolute/path/19-cuda12-compat-001-project-prereqs.sh \
    --bucket BUCKET --prefix PREFIX

Every listed local file is hash-checked against the generated manifest before
upload. The script uploads the manifest, its six archive inputs, and the two
external bootstrap scripts, then writes and uploads input-oss-receipt.json.
The receipt records the version ID, URI, SHA-256, and size of every input.
EOF
}

die() { printf 'stage-cuda12-compat-001-inputs-oss: %s\n' "$*" >&2; exit 2; }

MANIFEST=""
INPUT_DIR=""
BOOTSTRAP=""
PREREQS=""
BUCKET=""
PREFIX=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --input-manifest) MANIFEST="${2:-}"; shift 2 ;;
    --input-dir) INPUT_DIR="${2:-}"; shift 2 ;;
    --bootstrap) BOOTSTRAP="${2:-}"; shift 2 ;;
    --prereqs) PREREQS="${2:-}"; shift 2 ;;
    --bucket) BUCKET="${2:-}"; shift 2 ;;
    --prefix) PREFIX="${2:-}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[[ "$MANIFEST" = /* && "$INPUT_DIR" = /* && "$BOOTSTRAP" = /* && "$PREREQS" = /* ]] \
  || die "manifest, input-dir, bootstrap, and prereqs must be absolute paths"
[[ -f "$MANIFEST" && -d "$INPUT_DIR" && -f "$BOOTSTRAP" && -f "$PREREQS" ]] \
  || die "one or more input files do not exist"
[[ "$BUCKET" =~ ^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$ ]] || die "invalid OSS bucket name"
[[ "$PREFIX" =~ ^[A-Za-z0-9]([A-Za-z0-9._/-]*[A-Za-z0-9._-])?$ ]] \
  && [[ "$PREFIX" != *'//'* ]] && [[ "$PREFIX" != *'/./'* ]] && [[ "$PREFIX" != *'/../'* ]] \
  || die "invalid OSS prefix"
[[ "$(basename -- "$MANIFEST")" == "input-manifest.json" ]] || die "manifest filename must be input-manifest.json"
for command in ossutil python3 shasum stat; do command -v "$command" >/dev/null || die "missing $command"; done

MANIFEST="$(cd "$(dirname "$MANIFEST")" && pwd -P)/$(basename "$MANIFEST")"
INPUT_DIR="$(cd "$INPUT_DIR" && pwd -P)"
BOOTSTRAP="$(cd "$(dirname "$BOOTSTRAP")" && pwd -P)/$(basename "$BOOTSTRAP")"
PREREQS="$(cd "$(dirname "$PREREQS")" && pwd -P)/$(basename "$PREREQS")"
RECEIPT="$INPUT_DIR/input-oss-receipt.json"
[[ ! -e "$RECEIPT" ]] || die "refusing to overwrite existing receipt: $RECEIPT"

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/cuda12-compat-001-inputs.XXXXXXXX")"
trap 'rm -rf -- "$TMP_DIR"' EXIT
PLAN="$TMP_DIR/plan.tsv"
RECORDS="$TMP_DIR/records.tsv"

python3 - "$MANIFEST" "$INPUT_DIR" "$BOOTSTRAP" "$PREREQS" >"$PLAN" <<'PY'
import hashlib
import json
import pathlib
import re
import sys

manifest_path, input_dir, bootstrap, prereqs = map(pathlib.Path, sys.argv[1:])
document = json.loads(manifest_path.read_text(encoding="utf-8"))
if not isinstance(document, dict) or set(document) != {"archives", "identity", "model", "schema_version", "static_inputs"}:
    raise SystemExit("invalid input manifest schema")
if document.get("schema_version") != 1:
    raise SystemExit("unexpected input manifest version")
identity = document["identity"]
if not isinstance(identity, dict) or identity.get("bundle_id") != "CUDA12-COMPAT-001":
    raise SystemExit("wrong input manifest bundle")
archives = document["archives"]
required_archives = {
    "cuda_wheelhouse", "model_snapshot", "runtime_wheel", "runtime_wheel_provenance",
    "sglang_source_seed", "toolgap_source_seed",
}
if not isinstance(archives, dict) or set(archives) != required_archives:
    raise SystemExit("input manifest archive set differs")
static_inputs = document["static_inputs"]
paths = {
    "bootstrap": ("experiments/g1/commands/00-cuda12-compat-001-bootstrap.sh", bootstrap),
    "prereqs": ("experiments/g1/commands/19-cuda12-compat-001-project-prereqs.sh", prereqs),
}
if not isinstance(static_inputs, dict) or {value[0] for value in paths.values()} - set(static_inputs):
    raise SystemExit("input manifest omits external script bindings")

def entry(label, local, expected):
    if not isinstance(expected, dict) or set(expected) not in (
        {"sha256", "size_bytes"}, {"path", "sha256", "size_bytes"}
    ):
        raise SystemExit(f"invalid input binding: {label}")
    if not isinstance(expected["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", expected["sha256"]):
        raise SystemExit(f"invalid input hash: {label}")
    if not isinstance(expected["size_bytes"], int) or expected["size_bytes"] < 1:
        raise SystemExit(f"invalid input size: {label}")
    print("\t".join((label, str(local), local.name, expected["sha256"], str(expected["size_bytes"]))))

digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
print("\t".join(("input_manifest", str(manifest_path), manifest_path.name, digest, str(manifest_path.stat().st_size))))
for label in sorted(required_archives):
    expected = archives[label]
    if not isinstance(expected, dict) or set(expected) != {"path", "sha256", "size_bytes"}:
        raise SystemExit(f"invalid archive binding: {label}")
    path = input_dir / expected["path"]
    if path.name != expected["path"]:
        raise SystemExit(f"unsafe archive name: {label}")
    entry(label, path, expected)
for label, (manifest_key, path) in paths.items():
    entry(label, path, static_inputs[manifest_key])
PY

latest_version_id() {
  local object_uri="$1" listing version_id=""
  listing="$(mktemp "$TMP_DIR/ossutil-ls.XXXXXXXX")"
  ossutil ls --all-versions "$object_uri" >"$listing" || return 1
  version_id="$(python3 - "$listing" "$object_uri" <<'PY'
import sys
listing, expected = sys.argv[1:]
matches = []
for line in open(listing, encoding="utf-8", errors="replace"):
    fields = line.split()
    if len(fields) < 10:
        continue
    version_id, latest, delete_marker, uri = fields[-4:]
    if uri == expected and latest.lower() == "true" and delete_marker.lower() == "false":
        matches.append(version_id)
if len(matches) != 1 or not matches[0] or matches[0].lower() in {"null", "-"}:
    raise SystemExit("cannot identify exactly one latest live OSS object version")
print(matches[0])
PY
)"
  printf '%s' "$version_id"
}

: >"$RECORDS"
while IFS=$'\t' read -r label local filename expected_sha expected_size; do
  [[ -f "$local" && ! -L "$local" ]] || die "input is not a regular file: $label"
  [[ "$(shasum -a 256 "$local" | awk '{print $1}')" == "$expected_sha" ]] || die "input hash differs: $label"
  [[ "$(stat -f '%z' "$local")" == "$expected_size" ]] || die "input size differs: $label"
  object_uri="oss://$BUCKET/$PREFIX/$filename"
  ossutil -f cp "$local" "$object_uri" </dev/null
  version_id="$(latest_version_id "$object_uri")" || die "cannot read uploaded object version: $label"
  printf '%s\t%s\t%s\t%s\t%s\n' "$label" "$object_uri" "$version_id" "$expected_sha" "$expected_size" >>"$RECORDS"
done <"$PLAN"

python3 - "$MANIFEST" "$RECORDS" "$RECEIPT" <<'PY'
import json
import os
import pathlib
import sys

manifest_path, records_path, receipt_path = map(pathlib.Path, sys.argv[1:])
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
records = {}
for line in records_path.read_text(encoding="utf-8").splitlines():
    label, uri, version, digest, size = line.split("\t")
    if label in records:
        raise SystemExit("duplicate upload receipt label")
    records[label] = {"object_uri": uri, "sha256": digest, "size_bytes": int(size), "version_id": version}
expected = {"input_manifest", "bootstrap", "prereqs", *manifest["archives"]}
if set(records) != expected:
    raise SystemExit("upload receipt object set differs")
document = {"schema_version": 1, "identity": manifest["identity"], "objects": records}
fd = os.open(receipt_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle:
    handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(receipt_path, 0o444)
PY

receipt_uri="oss://$BUCKET/$PREFIX/input-oss-receipt.json"
ossutil -f cp "$RECEIPT" "$receipt_uri" </dev/null
receipt_version="$(latest_version_id "$receipt_uri")" || die "cannot read receipt object version"
printf 'CUDA12_COMPAT_001_INPUTS_STAGED receipt=%s version_id=%s\n' "$receipt_uri" "$receipt_version"
