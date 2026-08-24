#!/usr/bin/env bash
# Publish a sealed CUDA12-COMPAT-001 attempt from an operator machine.
# The ECS role remains read-only; this script is deliberately not an ECS step.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/anchor-cuda12-compat-001-oss.sh \
    --attempt-dir /absolute/path/to/sealed-attempt \
    --attempt-id ATTEMPT_ID \
    --bucket BUCKET \
    --raw-prefix PREFIX \
    --anchor-prefix PREFIX

The script does not modify the attempt directory. It verifies the sealed
attempt locally, uploads every artifact-index entry plus its index and receipt,
and publishes one external JSON anchor. The raw and anchor prefixes must be
different, non-overlapping OSS key prefixes.
EOF
}

die() {
  printf 'anchor-cuda12-compat-001-oss: %s\n' "$*" >&2
  exit 2
}

require_value() {
  local flag="$1"
  local value="${2:-}"
  [[ -n "$value" ]] || die "missing value for $flag"
  printf '%s' "$value"
}

valid_bucket() {
  [[ "$1" =~ ^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$ ]]
}

valid_attempt_id() {
  [[ "$1" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$ ]]
}

valid_prefix() {
  local value="$1"
  [[ "$value" =~ ^[A-Za-z0-9]([A-Za-z0-9._/-]*[A-Za-z0-9._-])?$ ]] \
    && [[ "$value" != *'//'* ]] \
    && [[ "$value" != *'/./'* ]] \
    && [[ "$value" != *'/../'* ]] \
    && [[ "$value" != . && "$value" != .. ]]
}

prefixes_overlap() {
  local first="$1"
  local second="$2"
  [[ "$first" == "$second" || "$first" == "$second"/* || "$second" == "$first"/* ]]
}

ATTEMPT_DIR=""
ATTEMPT_ID=""
BUCKET=""
RAW_PREFIX=""
ANCHOR_PREFIX=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --attempt-dir)
      ATTEMPT_DIR="$(require_value "$1" "${2:-}")"
      shift 2
      ;;
    --attempt-id)
      ATTEMPT_ID="$(require_value "$1" "${2:-}")"
      shift 2
      ;;
    --bucket)
      BUCKET="$(require_value "$1" "${2:-}")"
      shift 2
      ;;
    --raw-prefix)
      RAW_PREFIX="$(require_value "$1" "${2:-}")"
      shift 2
      ;;
    --anchor-prefix)
      ANCHOR_PREFIX="$(require_value "$1" "${2:-}")"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

[[ -n "$ATTEMPT_DIR" && -n "$ATTEMPT_ID" && -n "$BUCKET" && -n "$RAW_PREFIX" && -n "$ANCHOR_PREFIX" ]] \
  || die "all five arguments are required"
valid_attempt_id "$ATTEMPT_ID" || die "invalid attempt ID"
valid_bucket "$BUCKET" || die "invalid OSS bucket name"
valid_prefix "$RAW_PREFIX" || die "invalid raw prefix"
valid_prefix "$ANCHOR_PREFIX" || die "invalid anchor prefix"
! prefixes_overlap "$RAW_PREFIX" "$ANCHOR_PREFIX" \
  || die "raw and anchor prefixes must not overlap"

for command in ossutil python3; do
  command -v "$command" >/dev/null 2>&1 || die "required command not found: $command"
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
FINALIZER="$REPO_ROOT/experiments/g1/commands/cuda12_compat_001_finalize.py"
[[ -f "$FINALIZER" ]] || die "CUDA12-COMPAT-001 finalizer is missing from this checkout"
[[ -d "$ATTEMPT_DIR" ]] || die "attempt directory does not exist: $ATTEMPT_DIR"
ATTEMPT_DIR="$(cd "$ATTEMPT_DIR" && pwd -P)"

# Validate all internal bindings before any external object is created.
python3 "$FINALIZER" verify --run-dir "$ATTEMPT_DIR"

CONTEXT_IDENTITY="$(
  python3 - "$ATTEMPT_DIR/attempt-context.json" <<'PY'
import json
import sys

context = json.load(open(sys.argv[1], encoding="utf-8"))
expected = {"attempt_id", "claim_state", "gate", "gate_decision"}
if not expected.issubset(context):
    raise SystemExit("attempt context does not contain anchor identity fields")
values = [context[name] for name in ("attempt_id", "claim_state", "gate", "gate_decision")]
if not all(isinstance(value, str) and value for value in values):
    raise SystemExit("attempt context has invalid anchor identity fields")
print(*values)
PY
)"
read -r CONTEXT_ATTEMPT_ID CLAIM_STATE GATE GATE_DECISION <<<"$CONTEXT_IDENTITY"
[[ "$CONTEXT_ATTEMPT_ID" == "$ATTEMPT_ID" ]] \
  || die "--attempt-id does not match sealed attempt context"
[[ "$CLAIM_STATE" == "roadmap" && "$GATE" == "G1" && "$GATE_DECISION" == "N/A" ]] \
  || die "sealed attempt context exceeds CUDA12-COMPAT-001 scope"

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/cuda12-compat-001-anchor.XXXXXXXX")"
trap 'rm -rf -- "$TMP_DIR"' EXIT
PLAN="$TMP_DIR/indexed-artifacts.tsv"
RECORDS="$TMP_DIR/uploaded-indexed-artifacts.tsv"
RAW_ROOT="oss://$BUCKET/$RAW_PREFIX/$ATTEMPT_ID"

# Recheck each indexed item before transfer. The finalizer has already checked
# the complete terminal; this makes the transfer plan itself fail closed on a
# symlink, path escape, or post-verification local mutation.
python3 - "$ATTEMPT_DIR" "$RAW_ROOT" >"$PLAN" <<'PY'
import hashlib
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
raw_root = sys.argv[2]
index = json.loads((root / "artifact-index.json").read_text(encoding="utf-8"))
entries = index.get("files")
if not isinstance(entries, list):
    raise SystemExit("artifact index lacks files list")

safe_path = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]*")
seen = set()
for entry in entries:
    if not isinstance(entry, dict):
        raise SystemExit("invalid artifact index entry")
    path = entry.get("path")
    digest = entry.get("sha256")
    size = entry.get("size_bytes")
    if (
        not isinstance(path, str)
        or not safe_path.fullmatch(path)
        or "//" in path
        or any(part in {".", ".."} for part in Path(path).parts)
        or path in seen
        or not isinstance(digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", digest)
        or not isinstance(size, int)
        or size < 0
    ):
        raise SystemExit("unsafe artifact index entry")
    seen.add(path)
    local = root / path
    if local.is_symlink() or not local.is_file():
        raise SystemExit(f"indexed artifact is not a regular file: {path}")
    try:
        local.resolve().relative_to(root)
    except ValueError as exc:
        raise SystemExit(f"indexed artifact escapes attempt: {path}") from exc
    actual = hashlib.sha256(local.read_bytes()).hexdigest()
    if local.stat().st_size != size or actual != digest:
        raise SystemExit(f"indexed artifact changed after finalizer verification: {path}")
    print(f"{path}\t{digest}\t{size}\t{raw_root}/{path}")
PY

latest_version_id() {
  local object_uri="$1"
  local listing
  local version_id=""
  local attempt

  for attempt in 1 2 3; do
    listing="$(mktemp "$TMP_DIR/ossutil-ls.XXXXXXXX")"
    if ossutil ls --all-versions "$object_uri" >"$listing"; then
      if version_id="$(python3 - "$listing" "$object_uri" <<'PY'
import sys

listing, expected_uri = sys.argv[1:]
matches = []
for line in open(listing, encoding="utf-8", errors="replace"):
    fields = line.rstrip("\n").rsplit(None, 4)
    if len(fields) != 5:
        continue
    _, version_id, is_latest, delete_marker, object_uri = fields
    if object_uri != expected_uri:
        continue
    if is_latest.lower() == "true" and delete_marker.lower() == "false":
        matches.append(version_id)
if len(matches) != 1 or not matches[0] or matches[0].lower() in {"null", "-"}:
    raise SystemExit(
        "expected exactly one non-delete latest version from ossutil ls --all-versions"
    )
print(matches[0])
PY
      )"; then
        printf '%s' "$version_id"
        return 0
      fi
    fi
    sleep "$attempt"
  done
  die "could not read a non-delete latest object version for $object_uri"
}

file_metadata() {
  python3 - "$1" <<'PY'
import hashlib
import sys
from pathlib import Path

path = Path(sys.argv[1])
if path.is_symlink() or not path.is_file():
    raise SystemExit("artifact is not a regular file")
digest = hashlib.sha256(path.read_bytes()).hexdigest()
print(digest, path.stat().st_size)
PY
}

upload_one() {
  local relative_path="$1"
  local expected_sha256="$2"
  local expected_size="$3"
  local object_uri="$4"
  local version_id
  local local_path="$ATTEMPT_DIR/$relative_path"
  local actual_sha256
  local actual_size

  [[ -f "$local_path" && ! -L "$local_path" ]] || die "refusing non-regular upload input: $relative_path"
  read -r actual_sha256 actual_size <<<"$(file_metadata "$local_path")"
  [[ "$actual_sha256" == "$expected_sha256" && "$actual_size" == "$expected_size" ]] \
    || die "artifact changed before upload: $relative_path"
  ossutil -f cp "$local_path" "$object_uri" </dev/null
  version_id="$(latest_version_id "$object_uri")"
  printf '%s\t%s\t%s\t%s\t%s\n' \
    "$relative_path" "$expected_sha256" "$expected_size" "$object_uri" "$version_id" >>"$RECORDS"
}

while IFS=$'\t' read -r relative_path expected_sha256 expected_size object_uri; do
  [[ -n "$relative_path" && -n "$expected_sha256" && -n "$expected_size" && -n "$object_uri" ]] \
    || die "invalid generated artifact upload plan"
  upload_one "$relative_path" "$expected_sha256" "$expected_size" "$object_uri"
done <"$PLAN"

read -r INDEX_SHA256 INDEX_SIZE <<<"$(file_metadata "$ATTEMPT_DIR/artifact-index.json")"
read -r RECEIPT_SHA256 RECEIPT_SIZE <<<"$(file_metadata "$ATTEMPT_DIR/completion-receipt.json")"
INDEX_URI="$RAW_ROOT/artifact-index.json"
RECEIPT_URI="$RAW_ROOT/completion-receipt.json"
ossutil -f cp "$ATTEMPT_DIR/artifact-index.json" "$INDEX_URI" </dev/null
INDEX_VERSION_ID="$(latest_version_id "$INDEX_URI")"
ossutil -f cp "$ATTEMPT_DIR/completion-receipt.json" "$RECEIPT_URI" </dev/null
RECEIPT_VERSION_ID="$(latest_version_id "$RECEIPT_URI")"

ANCHOR_FILE="$TMP_DIR/external-anchor.json"
python3 - \
  "$ANCHOR_FILE" "$ATTEMPT_DIR" "$ATTEMPT_ID" "$RAW_ROOT" "$RECORDS" \
  "$INDEX_SHA256" "$INDEX_SIZE" "$INDEX_URI" "$INDEX_VERSION_ID" \
  "$RECEIPT_SHA256" "$RECEIPT_SIZE" "$RECEIPT_URI" "$RECEIPT_VERSION_ID" <<'PY'
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

(
    output,
    attempt_dir,
    attempt_id,
    raw_root,
    records_path,
    index_sha256,
    index_size,
    index_uri,
    index_version_id,
    receipt_sha256,
    receipt_size,
    receipt_uri,
    receipt_version_id,
) = sys.argv[1:]
root = Path(attempt_dir)
index = json.loads((root / "artifact-index.json").read_text(encoding="utf-8"))
entries = index["files"]
records = {}
for line in Path(records_path).read_text(encoding="utf-8").splitlines():
    fields = line.split("\t")
    if len(fields) != 5:
        raise SystemExit("malformed uploaded-artifact record")
    path, digest, size, uri, version_id = fields
    if path in records:
        raise SystemExit("duplicate uploaded-artifact record")
    records[path] = {
        "path": path,
        "sha256": digest,
        "size_bytes": int(size),
        "object_uri": uri,
        "version_id": version_id,
    }

anchored = []
for entry in entries:
    path = entry["path"]
    record = records.get(path)
    if record is None:
        raise SystemExit(f"missing uploaded-artifact record: {path}")
    if (
        record["sha256"] != entry["sha256"]
        or record["size_bytes"] != entry["size_bytes"]
        or record["object_uri"] != f"{raw_root}/{path}"
        or not record["version_id"]
    ):
        raise SystemExit(f"uploaded-artifact binding differs: {path}")
    anchored.append(record)
if len(records) != len(anchored):
    raise SystemExit("uploaded-artifact set differs from artifact index")
status = records.get("execution-status.json")
if status is None:
    raise SystemExit("artifact index lacks execution-status.json")

document = {
    "anchor_kind": "CUDA12_COMPAT_001_EXTERNAL_OSS_ANCHOR",
    "attempt": {
        "attempt_id": attempt_id,
        "raw_object_prefix": raw_root,
    },
    "claim_state": "roadmap",
    "gate": "G1",
    "gate_decision": "N/A",
    "indexed_artifacts": anchored,
    "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "schema_version": 1,
    "terminal_objects": {
        "artifact_index": {
            "path": "artifact-index.json",
            "sha256": index_sha256,
            "size_bytes": int(index_size),
            "object_uri": index_uri,
            "version_id": index_version_id,
        },
        "completion_receipt": {
            "path": "completion-receipt.json",
            "sha256": receipt_sha256,
            "size_bytes": int(receipt_size),
            "object_uri": receipt_uri,
            "version_id": receipt_version_id,
        },
        "execution_status": status,
    },
}
encoded = json.dumps(document, indent=2, sort_keys=True) + "\n"
descriptor = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
    handle.write(encoded)
os.chmod(output, 0o444)
PY
ANCHOR_SHA256="$(python3 - "$ANCHOR_FILE" <<'PY'
import hashlib
import sys
from pathlib import Path

print(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())
PY
)"
ANCHOR_URI="oss://$BUCKET/$ANCHOR_PREFIX/$ATTEMPT_ID/external-anchor-$ANCHOR_SHA256.json"
ossutil -f cp "$ANCHOR_FILE" "$ANCHOR_URI" </dev/null
ANCHOR_VERSION_ID="$(latest_version_id "$ANCHOR_URI")"

printf 'OSS_EXTERNAL_ANCHOR_URI=%s\n' "$ANCHOR_URI"
printf 'OSS_EXTERNAL_ANCHOR_VERSION_ID=%s\n' "$ANCHOR_VERSION_ID"
printf 'OSS_EXTERNAL_ANCHOR_SHA256=%s\n' "$ANCHOR_SHA256"
