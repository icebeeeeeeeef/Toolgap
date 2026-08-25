#!/usr/bin/env bash
# Publish a sealed formal G1-C-010 attempt from an operator machine.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/anchor-g1-c-010-oss.sh     --attempt-dir /absolute/path/to/sealed-attempt     --attempt-id ATTEMPT_ID     --bucket BUCKET     --raw-prefix PREFIX     --anchor-prefix PREFIX
EOF
}
die() { printf 'anchor-g1-c-010: %s\n' "$*" >&2; exit 2; }
value() { [[ -n "${2:-}" ]] || die "missing value for $1"; printf '%s' "$2"; }
valid_bucket() { [[ "$1" =~ ^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$ ]]; }
valid_id() { [[ "$1" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$ ]]; }
valid_prefix() {
  [[ "$1" =~ ^[A-Za-z0-9]([A-Za-z0-9._/-]*[A-Za-z0-9._-])?$ ]] &&
    [[ "$1" != *'//'* && "$1" != *'/./'* && "$1" != *'/../'* ]]
}
overlap() { [[ "$1" == "$2" || "$1" == "$2"/* || "$2" == "$1"/* ]]; }

ATTEMPT_DIR=""; ATTEMPT_ID=""; BUCKET=""; RAW_PREFIX=""; ANCHOR_PREFIX=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --attempt-dir) ATTEMPT_DIR="$(value "$1" "${2:-}")"; shift 2 ;;
    --attempt-id) ATTEMPT_ID="$(value "$1" "${2:-}")"; shift 2 ;;
    --bucket) BUCKET="$(value "$1" "${2:-}")"; shift 2 ;;
    --raw-prefix) RAW_PREFIX="$(value "$1" "${2:-}")"; shift 2 ;;
    --anchor-prefix) ANCHOR_PREFIX="$(value "$1" "${2:-}")"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done
[[ -n "$ATTEMPT_DIR" && -n "$ATTEMPT_ID" && -n "$BUCKET" && -n "$RAW_PREFIX" && -n "$ANCHOR_PREFIX" ]] || die 'all arguments are required'
valid_id "$ATTEMPT_ID" && valid_bucket "$BUCKET" && valid_prefix "$RAW_PREFIX" && valid_prefix "$ANCHOR_PREFIX" || die 'invalid argument'
! overlap "$RAW_PREFIX" "$ANCHOR_PREFIX" || die 'raw and anchor prefixes must not overlap'
command -v ossutil >/dev/null || die 'ossutil is required'
command -v python3 >/dev/null || die 'python3 is required'
SCRIPT_DIR="$(cd -- "$(dirname -- "$BASH_SOURCE")" && pwd -P)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
FINALIZER="$ROOT/experiments/g1/commands/g1_c_010_finalize.py"
[[ -f "$FINALIZER" && -d "$ATTEMPT_DIR" ]] || die 'missing finalizer or attempt directory'
ATTEMPT_DIR="$(cd "$ATTEMPT_DIR" && pwd -P)"
python3 "$FINALIZER" verify --run-dir "$ATTEMPT_DIR"

read -r CONTEXT_ATTEMPT_ID CONTEXT_SHA256 < <(python3 - "$ATTEMPT_DIR/attempt-context.json" <<'PY'
import hashlib, json, sys
path = sys.argv[1]
document = json.load(open(path, encoding="utf-8"))
attempt_id = document.get("attempt_id")
if not isinstance(attempt_id, str) or not attempt_id:
    raise SystemExit("sealed attempt context lacks an attempt ID")
print(attempt_id, hashlib.sha256(open(path, "rb").read()).hexdigest())
PY
)
[[ "$CONTEXT_ATTEMPT_ID" == "$ATTEMPT_ID" ]] || die '--attempt-id does not match sealed attempt context'

read -r STATUS CLAIM GATE < <(python3 - "$ATTEMPT_DIR/execution-status.json" <<'PY'
import json, sys
document = json.load(open(sys.argv[1], encoding="utf-8"))
if document.get("attempt_status") not in ("PASS", "STOP", "INVALID"):
    raise SystemExit("not a G1-C-010 terminal")
if document.get("claim_state") != "roadmap" or document.get("gate") != "G1":
    raise SystemExit("attempt exceeds formal G1 scope")
print(document["attempt_status"], document["claim_state"], document["gate"])
PY
)
[[ "$CLAIM" == roadmap && "$GATE" == G1 ]] || die 'sealed attempt identity differs'

TMP="$(mktemp -d "${TMPDIR:-/tmp}/g1-c-010-anchor.XXXXXXXX")"
trap 'rm -rf -- "$TMP"' EXIT
RAW_ROOT="oss://$BUCKET/$RAW_PREFIX/$CONTEXT_ATTEMPT_ID"
PLAN="$TMP/plan.tsv"
RECORDS="$TMP/records.tsv"
python3 - "$ATTEMPT_DIR" "$RAW_ROOT" >"$PLAN" <<'PY'
import hashlib, json, re, sys
from pathlib import Path
root, raw = Path(sys.argv[1]).resolve(), sys.argv[2]
index = json.loads((root / "artifact-index.json").read_text(encoding="utf-8"))
seen = set()
for item in index.get("files", []):
    path, digest, size = item.get("path"), item.get("sha256"), item.get("size_bytes")
    candidate = Path(path) if isinstance(path, str) else Path()
    if (
        not isinstance(path, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+/-]*", path)
        or "//" in path or ".." in candidate.parts or path in seen
        or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
        or not isinstance(size, int) or size < 0
    ):
        raise SystemExit("unsafe artifact index entry")
    seen.add(path)
    local = root / path
    if local.is_symlink() or not local.is_file():
        raise SystemExit("indexed artifact is not a regular file")
    if local.resolve().parent != root.resolve() and root.resolve() not in local.resolve().parents:
        raise SystemExit("indexed artifact escapes attempt")
    actual = hashlib.sha256(local.read_bytes()).hexdigest()
    if actual != digest or local.stat().st_size != size:
        raise SystemExit("indexed artifact changed after verification")
    print(f"{path}\t{digest}\t{size}\t{raw}/{path}")
if not seen:
    raise SystemExit("artifact index is empty")
PY

latest_version() {
  local uri="$1" listing version
  listing="$(mktemp "$TMP/versions.XXXXXXXX")"
  ossutil ls --all-versions "$uri" >"$listing"
  version="$(python3 - "$listing" "$uri" <<'PY'
import sys
rows = []
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    fields = line.rstrip("\n").rsplit(None, 4)
    if len(fields) != 5: continue
    _, version, latest, deleted, uri = fields
    if uri == sys.argv[2] and latest.lower() == "true" and deleted.lower() == "false":
        rows.append(version)
if len(rows) != 1 or not rows[0] or rows[0].lower() in {"null", "-"}:
    raise SystemExit("expected exactly one latest non-delete object version")
print(rows[0])
PY
)"
  printf '%s' "$version"
}
metadata() {
  python3 - "$1" <<'PY'
import hashlib, sys
from pathlib import Path
path = Path(sys.argv[1])
if path.is_symlink() or not path.is_file(): raise SystemExit("not a regular file")
print(hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_size)
PY
}
while IFS=$'\t' read -r path expected_sha expected_size uri; do
  local_path="$ATTEMPT_DIR/$path"
  read -r actual_sha actual_size <<<"$(metadata "$local_path")"
  [[ "$actual_sha" == "$expected_sha" && "$actual_size" == "$expected_size" ]] || die "artifact changed: $path"
  ossutil -f cp "$local_path" "$uri" </dev/null
  printf '%s\t%s\t%s\t%s\t%s\n' "$path" "$expected_sha" "$expected_size" "$uri" "$(latest_version "$uri")" >>"$RECORDS"
done <"$PLAN"

for terminal in artifact-index.json completion-receipt.json; do
  read -r digest size <<<"$(metadata "$ATTEMPT_DIR/$terminal")"
  uri="$RAW_ROOT/$terminal"
  ossutil -f cp "$ATTEMPT_DIR/$terminal" "$uri" </dev/null
  printf '%s\t%s\t%s\t%s\t%s\n' "$terminal" "$digest" "$size" "$uri" "$(latest_version "$uri")" >>"$RECORDS"
done

ANCHOR="$TMP/external-anchor.json"
python3 - "$ANCHOR" "$ATTEMPT_DIR" "$CONTEXT_ATTEMPT_ID" "$CONTEXT_SHA256" "$RAW_ROOT" "$STATUS" "$RECORDS" <<'PY'
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path
out = Path(sys.argv[1])
attempt_dir = Path(sys.argv[2])
attempt_id = sys.argv[3]
context_sha256 = sys.argv[4]
raw = sys.argv[5]
terminal = sys.argv[6]
records_file = Path(sys.argv[7])
index = json.loads((attempt_dir / "artifact-index.json").read_text(encoding="utf-8"))
records = {}
for line in records_file.read_text(encoding="utf-8").splitlines():
    path, digest, size, uri, version = line.split("\t")
    if path in records or not version: raise SystemExit("invalid uploaded-object record")
    records[path] = {"path": path, "sha256": digest, "size_bytes": int(size), "object_uri": uri, "version_id": version}
indexed = [records[item["path"]] for item in index["files"]]
if len(indexed) != len(index["files"]): raise SystemExit("missing indexed upload")
document = {
    "anchor_kind": "G1_C_010_EXTERNAL_OSS_ANCHOR",
    "attempt": {"attempt_id": attempt_id, "context_sha256": context_sha256, "raw_object_prefix": raw},
    "claim_state": "roadmap", "gate": "G1", "gate_decision": terminal,
    "indexed_artifacts": indexed,
    "terminal_objects": {"artifact_index": records["artifact-index.json"], "completion_receipt": records["completion-receipt.json"], "execution_status": records["execution-status.json"]},
    "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "schema_version": 1,
}
fd = os.open(out, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
with os.fdopen(fd, "w", encoding="utf-8") as handle: handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
os.chmod(out, 0o444)
PY
ANCHOR_SHA="$(metadata "$ANCHOR" | awk '{print $1}')"
ANCHOR_URI="oss://$BUCKET/$ANCHOR_PREFIX/$CONTEXT_ATTEMPT_ID/external-anchor-$ANCHOR_SHA.json"
ossutil -f cp "$ANCHOR" "$ANCHOR_URI" </dev/null
printf 'OSS_EXTERNAL_ANCHOR_URI=%s\nOSS_EXTERNAL_ANCHOR_VERSION_ID=%s\nOSS_EXTERNAL_ANCHOR_SHA256=%s\n' "$ANCHOR_URI" "$(latest_version "$ANCHOR_URI")" "$ANCHOR_SHA"
