#!/usr/bin/env bash
# Local structural check for the pre-rental execution bundle; no CUDA run occurs.
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/.." && pwd)"
readonly REPO_ROOT

bash -n \
  "$REPO_ROOT/experiments/g0/commands/20-g0-c-007-preflight.sh" \
  "$REPO_ROOT/experiments/g0/commands/21-g0-c-007-contract-controls.sh" \
  "$REPO_ROOT/experiments/g0/commands/22-g0-c-007-serving-arms.sh" \
  "$REPO_ROOT/experiments/g0/commands/23-g0-c-007-verify.sh"
python3 -m py_compile \
  "$REPO_ROOT/experiments/g0/commands/g0_c_007_seal_manifest.py" \
  "$REPO_ROOT/experiments/g0/commands/g0_c_007_package_provenance.py" \
  "$REPO_ROOT/experiments/g0/commands/g0_c_007_stream_request.py" \
  "$REPO_ROOT/experiments/g0/commands/g0_c_007_artifact_index.py" \
  "$REPO_ROOT/upstream/sglang/tests/test_g0_atomic_checked_demote_installed.py" \
  "$REPO_ROOT/upstream/sglang/tests/inventory_checked_demote_calls.py"
python3 -m json.tool "$REPO_ROOT/experiments/g0/manifest.g0-c-007.template.json" >/dev/null
test "$(shasum -a 256 "$REPO_ROOT/upstream/sglang/patches/0001-atomic-checked-demote.patch" | awk '{print $1}')" = \
  "$(shasum -a 256 "$REPO_ROOT/experiments/g0/artifacts/sglang-session-atomic-checked-demote-v5.patch" | awk '{print $1}')"
grep -Fx 'base_commit = "92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2"' \
  "$REPO_ROOT/upstream/sglang/pin.toml"
grep -Fx 'base_tree = "25e9bf86d04c27fe380024d9c8c421c3b5b51f3c"' \
  "$REPO_ROOT/upstream/sglang/pin.toml"
grep -Fx 'patch_sha256 = "e69776678909b4ee49b1c0fa4a8e208666893b659c0508387c83fcdf11e82a9a"' \
  "$REPO_ROOT/upstream/sglang/pin.toml"

work="$(mktemp -d)"
server_pid=
cleanup() {
  local status="$1"
  if [[ -n "$server_pid" ]]; then
    kill -TERM "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
  fi
  rm -rf "$work"
  exit "$status"
}
trap 'cleanup "$?"' EXIT
for arm in stock treatment; do
  checkout="$work/$arm"
  mkdir "$checkout"
  git -C "$checkout" init --quiet
  git -C "$checkout" config user.name verifier
  git -C "$checkout" config user.email verifier@invalid
  printf '%s\n' "$arm" >"$checkout/identity.txt"
  git -C "$checkout" add identity.txt
  git -C "$checkout" commit --quiet -m fixture
done
printf 'wheel\n' >"$work/stock.whl"
printf 'wheel\n' >"$work/treatment.whl"
printf 'dependency==1\n' >"$work/dependency-lock.txt"
printf 'environment\n' >"$work/environment.txt"
python3 "$REPO_ROOT/experiments/g0/commands/g0_c_007_seal_manifest.py" \
  --template "$REPO_ROOT/experiments/g0/manifest.g0-c-007.template.json" \
  --spec "$REPO_ROOT/experiments/g0/SPEC.g0-c-007.md" \
  --output "$work/manifest.json" \
  --attempt-id local-structural-check \
  --stock-checkout "$work/stock" \
  --treatment-checkout "$work/treatment" \
  --stock-wheel "$work/stock.whl" \
  --treatment-wheel "$work/treatment.whl" \
  --dependency-lock "$work/dependency-lock.txt" \
  --environment-readback "$work/environment.txt" \
  --stock-interpreter "$(command -v python3)" \
  --treatment-interpreter "$(command -v python3)"
python3 -c '
import json, sys
manifest = json.load(open(sys.argv[1]))
assert manifest["identity"]["run_status"] == "ADMITTED_PRE_ARM"
assert "__" not in json.dumps(manifest)
' "$work/manifest.json"
if python3 "$REPO_ROOT/experiments/g0/commands/g0_c_007_seal_manifest.py" \
  --template "$REPO_ROOT/experiments/g0/manifest.g0-c-007.template.json" \
  --spec "$REPO_ROOT/experiments/g0/SPEC.g0-c-007.md" \
  --output "$work/manifest.json" \
  --attempt-id local-structural-check \
  --stock-checkout "$work/stock" \
  --treatment-checkout "$work/treatment" \
  --stock-wheel "$work/stock.whl" \
  --treatment-wheel "$work/treatment.whl" \
  --dependency-lock "$work/dependency-lock.txt" \
  --environment-readback "$work/environment.txt" \
  --stock-interpreter "$(command -v python3)" \
  --treatment-interpreter "$(command -v python3)" >/dev/null 2>&1; then
  echo "sealed manifest was unexpectedly replaceable" >&2
  exit 1
fi
mkdir "$work/evidence"
printf 'preserved failure-or-success evidence\n' >"$work/evidence/evidence.txt"
python3 "$REPO_ROOT/experiments/g0/commands/g0_c_007_artifact_index.py" \
  --artifact-dir "$work/evidence" --output "$work/evidence/artifact-index.json"
python3 -c '
import json, sys
index = json.load(open(sys.argv[1]))
assert index["files"][0]["path"] == "evidence.txt"
' "$work/evidence/artifact-index.json"

set +e
G0_ATTEMPT_ID=local-preflight-rejection \
  G0_RUN_DIR="$work/preflight-rejection" \
  G0_WORK_ROOT="$work/preflight-work" \
  G0_PYTHON=toolgap-missing-python \
  bash "$REPO_ROOT/experiments/g0/commands/20-g0-c-007-preflight.sh" \
  >"$work/preflight.stdout" 2>"$work/preflight.stderr"
preflight_status=$?
set -e
test "$preflight_status" = 78
grep -q '^status=BLOCKED_BEFORE_EXECUTION$' \
  "$work/preflight-rejection/preflight-status.txt"

python3 -c '
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        self.wfile.write(
            b"data: "
            + json.dumps({"text": "ok", "meta_info": {}}).encode()
            + b"\n\ndata: [DONE]\n\n"
        )
    def log_message(self, format, *args):
        pass
server = HTTPServer(("127.0.0.1", 0), Handler)
print(server.server_port, flush=True)
server.serve_forever()
' >"$work/stream-port.txt" 2>"$work/stream-server.log" &
server_pid=$!
for _ in 1 2 3 4 5; do
  if [[ -s "$work/stream-port.txt" ]]; then break; fi
  sleep 1
done
if [[ -s "$work/stream-port.txt" ]]; then
  printf '%s\n' '{"text":"fixture","sampling_params":{"temperature":0.0},"stream":true}' \
    >"$work/stream-request.json"
  python3 "$REPO_ROOT/experiments/g0/commands/g0_c_007_stream_request.py" \
    --base-url "http://127.0.0.1:$(cat "$work/stream-port.txt")" \
    --request-json "$work/stream-request.json" \
    --raw-output "$work/stream.sse" \
    --parsed-output "$work/stream.json"
  kill -TERM "$server_pid"
  wait "$server_pid" 2>/dev/null || true
  server_pid=
  python3 -c '
import json, sys
result = json.load(open(sys.argv[1]))
assert result["passed"] is True, result
' "$work/stream.json"
elif grep -q 'Operation not permitted' "$work/stream-server.log"; then
  echo "stream-runner integration check skipped: local socket bind is sandbox-denied."
  server_pid=
else
  cat "$work/stream-server.log" >&2
  exit 1
fi

echo "G0-C-ATOMIC-007 execution bundle: structural checks passed (no CUDA run)."
