#!/usr/bin/env bash
# Local counterexample check for the G0-C-ATOMIC-011 pre-rental bundle.
# It never starts SGLang and requires no CUDA device.
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/.." && pwd)"
readonly REPO_ROOT

readonly SPEC="$REPO_ROOT/experiments/g0/SPEC.g0-c-011.md"
readonly TEMPLATE="$REPO_ROOT/experiments/g0/manifest.g0-c-011.template.json"
readonly PIN="$REPO_ROOT/upstream/sglang/pin.g0-c-011.toml"
readonly COMMAND_ROOT="$REPO_ROOT/experiments/g0/commands"
readonly PREREQS="$COMMAND_ROOT/19-g0-c-011-project-prereqs.sh"
readonly PREFLIGHT="$COMMAND_ROOT/20-g0-c-011-preflight.sh"
readonly CONTROLS="$COMMAND_ROOT/21-g0-c-011-contract-controls.sh"
readonly SERVING="$COMMAND_ROOT/22-g0-c-011-serving-arms.sh"
readonly VERIFY="$COMMAND_ROOT/23-g0-c-011-verify.sh"
readonly SEAL_MANIFEST="$COMMAND_ROOT/g0_c_008_seal_manifest.py"
readonly VERIFY_IDENTITY="$COMMAND_ROOT/g0_c_008_verify_identity.py"
readonly PROVENANCE="$COMMAND_ROOT/g0_c_008_package_provenance.py"
readonly STREAM_REQUEST="$COMMAND_ROOT/g0_c_008_stream_request.py"
readonly VERIFY_EVIDENCE="$COMMAND_ROOT/g0_c_008_verify_evidence.py"
readonly FINALIZE="$COMMAND_ROOT/g0_c_011_finalize.py"
readonly PREPARE_SOURCE="$COMMAND_ROOT/g0_c_011_prepare_source.sh"

for path in \
  "$SPEC" "$TEMPLATE" "$PIN" \
  "$PREREQS" "$PREFLIGHT" "$CONTROLS" "$SERVING" "$VERIFY" \
  "$SEAL_MANIFEST" "$VERIFY_IDENTITY" "$PROVENANCE" \
  "$STREAM_REQUEST" "$VERIFY_EVIDENCE" "$FINALIZE" "$PREPARE_SOURCE"; do
  test -f "$path"
done

bash -n \
  "$PREREQS" "$PREFLIGHT" "$CONTROLS" "$SERVING" "$VERIFY" \
  "$PREPARE_SOURCE"
work="$(mktemp -d)"
default_attempt="local-preflight-rejection-$$"
default_run="$REPO_ROOT/experiments/g0/raw/g0-c-011/$default_attempt"
cleanup() {
  local status="$?"
  rm -rf "$work"
  rm -rf "$default_run"
  rmdir "$REPO_ROOT/experiments/g0/raw/g0-c-011" 2>/dev/null || true
  rmdir "$REPO_ROOT/experiments/g0/raw" 2>/dev/null || true
  exit "$status"
}
trap cleanup EXIT

PYTHONPYCACHEPREFIX="$work/pycache" python3 -m py_compile \
  "$SEAL_MANIFEST" "$VERIFY_IDENTITY" "$PROVENANCE" \
  "$STREAM_REQUEST" "$VERIFY_EVIDENCE" "$FINALIZE"
python3 -m json.tool "$TEMPLATE" >/dev/null

# Fixed-version and bounded-execution contracts must remain visible in the
# executable entry scripts.
grep -Fq 'experiments/g0/raw/g0-c-011' "$PREFLIGHT"
grep -Fq 'latest/api/token' "$PREFLIGHT"
grep -Fq 'latest/meta-data/$1' "$PREFLIGHT"
grep -Fq -- '--connect-timeout 2 --max-time 5' "$PREFLIGHT"
grep -Fq 'ubuntu_24_04_x64_100G_with_gpu_driver_and_cuda_alibase_' "$PREFLIGHT"
grep -Fq 'minimum_driver="580.65.06"' "$PREFLIGHT"
grep -Fq 'expected provider Python 3.12.x' "$PREFLIGHT"
grep -Fq 'G0_CUDA_HOME="${G0_CUDA_HOME:-/usr/local/cuda-13.0}"' "$PREFLIGHT"
grep -Fq "release 13\\.0" "$PREFLIGHT"
python3 - "$PREFLIGHT" <<'PY'
import pathlib
import sys

script = pathlib.Path(sys.argv[1]).read_text()
assert script.index('export PATH="$CUDA_HOME/bin:$PATH"') < script.index(
    'for command in nvidia-smi nvcc'
)
PY
grep -Fq 'assert torch.cuda.is_available()' "$PREFLIGHT"
grep -Fq 'alibaba_image_id=' "$PREFLIGHT"
grep -Fq 'GPU driver/CUDA substrate is absent' "$PREREQS"
grep -Fq 'apt-get install -y --no-install-recommends' "$PREREQS"
if grep -Eq '^[[:space:]]+(nvidia|cuda|cudnn|nccl|docker)[[:alnum:]_.+-]*([[:space:]]|$)' "$PREREQS"; then
  echo "project prerequisite installer must not install GPU infrastructure" >&2
  exit 1
fi
grep -Fq 'python/pyproject.toml' "$PREFLIGHT"
grep -Fq '`upstream/sglang/pin.g0-c-011.toml`' "$SPEC"
grep -Fq 'driver = ">=580.65.06' "$PIN"
grep -Fq 'python = "3.12.x' "$PIN"
grep -Fq 'cargo --version' "$PREFLIGHT"
grep -Fq 'rustc --version' "$PREFLIGHT"
grep -Fq 'readonly G0_LONG_COMMAND_TIMEOUT_SECONDS=1800' "$PREFLIGHT"
grep -Fq 'timeout --signal=TERM --kill-after=30s' "$PREFLIGHT"
test "$(grep -c 'run_bounded ' "$PREFLIGHT")" -ge 9
grep -Fq 'G0_SOURCE_SEED_ARCHIVE' "$PREFLIGHT"
grep -Fq 'G0_SOURCE_SEED_SHA256' "$PREFLIGHT"
grep -Fq 'g0_c_011_prepare_source.sh' "$PREFLIGHT"
grep -Fq '2d40db92ff1a21cb78e95f4da98352f1fa17086e1a16a82e95070f05e1460400' "$PIN"
if grep -Fq 'git clone "$G0_REMOTE"' "$PREFLIGHT"; then
  echo "011 preflight must not depend on live GitHub clones" >&2
  exit 1
fi
grep -Fq 'SGLANG_ENABLE_UNIFIED_RADIX_TREE=1' "$SERVING"
grep -Fq -- '--max-time "$request_timeout"' "$SERVING"
grep -Fq 'local request_timeout=10' "$SERVING"
grep -Fq 'setsid' "$SERVING"
grep -Fq 'exec setsid env -u PYTHONPATH' "$SERVING"
grep -Fq 'server_wait_status' "$SERVING"
grep -Fq "trap 'preflight_failure 129 \"\$LINENO\"' HUP" "$PREFLIGHT"
grep -Fq "trap 'write_invalid_scope 129 \"\$LINENO\"' HUP" "$CONTROLS"
grep -Fq "trap 'write_serving_failure 129 \"\$LINENO\"' HUP" "$SERVING"
grep -Fq "trap 'write_verify_failure 129 \"\$LINENO\"' HUP" "$VERIFY"
grep -Fq 'controls-passed.json' "$SERVING"
grep -Fq 'serving-passed.json' "$VERIFY"
for artifact in \
  source-seed.txt source-seed-prepare.log \
  stock-install-report.json treatment-install-report.json \
  stock-serving-provenance.json treatment-serving-provenance.json \
  stock-process-group-after.txt treatment-process-group-after.txt \
  stock-gpu-pids-leaked.txt treatment-gpu-pids-leaked.txt \
  controls-passed.json serving-passed.json; do
  grep -Fq "\"$artifact\"" "$TEMPLATE"
done

# The real source-preparation helper must restore two independent clean
# checkouts from one archive, retain the canonical remote identity, and reject
# an archive whose observed SHA-256 differs from the operator-bound value.
mkdir "$work/seed-fixture" "$work/seed-payload"
git init -q "$work/seed-fixture"
git -C "$work/seed-fixture" config user.name 'G0 verifier'
git -C "$work/seed-fixture" config user.email 'g0-verifier@example.invalid'
printf 'fixed source fixture\n' >"$work/seed-fixture/source.txt"
git -C "$work/seed-fixture" add source.txt
git -C "$work/seed-fixture" commit -q -m 'fixture source'
fixture_commit="$(git -C "$work/seed-fixture" rev-parse HEAD)"
fixture_tree="$(git -C "$work/seed-fixture" rev-parse 'HEAD^{tree}')"
git clone -q --bare --no-local \
  "$work/seed-fixture" "$work/seed-payload/sglang-source.git"
tar -czf "$work/source-seed.tar.gz" -C "$work/seed-payload" sglang-source.git
fixture_sha256="$(sha256sum "$work/source-seed.tar.gz" | awk '{print $1}')"
fixture_remote='https://example.invalid/sglang.git'
"$PREPARE_SOURCE" \
  "$work/source-seed.tar.gz" "$fixture_sha256" \
  "$work/source-input" "$work/stock-checkout" "$work/treatment-checkout" \
  "$fixture_remote" "$fixture_commit" "$fixture_tree"
for checkout in "$work/stock-checkout" "$work/treatment-checkout"; do
  test "$(git -C "$checkout" remote get-url origin)" = "$fixture_remote"
  test "$(git -C "$checkout" rev-parse HEAD)" = "$fixture_commit"
  test "$(git -C "$checkout" rev-parse 'HEAD^{tree}')" = "$fixture_tree"
  test -z "$(git -C "$checkout" status --porcelain)"
done
if "$PREPARE_SOURCE" \
  "$work/source-seed.tar.gz" "$(printf '0%.0s' {1..64})" \
  "$work/wrong-source-input" "$work/wrong-stock" "$work/wrong-treatment" \
  "$fixture_remote" "$fixture_commit" "$fixture_tree" >/dev/null 2>&1; then
  echo "source helper accepted a mismatched archive SHA-256" >&2
  exit 1
fi
test ! -e "$work/wrong-stock"
test ! -e "$work/wrong-treatment"

# A default-path admission failure must still be retained and indexed. The
# current non-CUDA workstation intentionally reaches a blocked terminal.
test ! -e "$default_run"
set +e
G0_ATTEMPT_ID="$default_attempt" \
  G0_WORK_ROOT="$work/preflight-work" \
  G0_PYTHON=toolgap-missing-python \
  bash "$PREFLIGHT" >"$work/preflight.stdout" 2>"$work/preflight.stderr"
preflight_status=$?
set -e
test "$preflight_status" = 78
test -f "$default_run/attempt-context.json"
test -f "$default_run/execution-status.json"
test -f "$default_run/artifact-index.json"
test ! -e "$default_run/completion-receipt.json"
python3 "$FINALIZE" verify --run-dir "$default_run"
python3 - "$default_run/attempt-context.json" "$default_attempt" <<'PY'
import json
import sys
document = json.load(open(sys.argv[1]))
assert document["experiment_id"] == "G0-C-ATOMIC-011"
assert document["attempt_id"] == sys.argv[2]
assert len(document["spec_sha256"]) == 64
assert len(document["toolgap_commit"]) == 40
assert len(document["toolgap_tree"]) == 40
assert document["admission_manifest"].startswith("N/A:")
PY

# The finalizer must reject terminals without an attributable attempt and must
# distinguish a complete failure from a complete success. Only the completion
# receipt is allowed to carry attempt_status=COMPLETED.
mkdir "$work/failure-incomplete" "$work/failure-seal" \
  "$work/success-incomplete" "$work/success-seal"
printf 'unattributed failure\n' >"$work/failure-incomplete/evidence.txt"
if python3 "$FINALIZE" failure \
  --run-dir "$work/failure-incomplete" \
  --attempt-status BLOCKED_BEFORE_EXECUTION \
  --phase preflight --exit-code 78 --line 42 >/dev/null 2>&1; then
  echo "failure without attempt identity was unexpectedly sealable" >&2
  exit 1
fi
printf 'failure evidence\n' >"$work/failure-seal/evidence.txt"
python3 - "$work/failure-seal/attempt-context.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
path.write_text(json.dumps({
    "admission_manifest": "N/A: admission not completed",
    "attempt_id": "failure-fixture",
    "created_at": "2026-08-20T00:00:00Z",
    "experiment_id": "G0-C-ATOMIC-011",
    "spec_path": "experiments/g0/SPEC.g0-c-011.md",
    "spec_sha256": "a" * 64,
    "toolgap_commit": "b" * 40,
    "toolgap_tracked_clean": True,
    "toolgap_tree": "c" * 40,
}, indent=2, sort_keys=True) + "\n")
PY
python3 "$FINALIZE" failure \
  --run-dir "$work/failure-seal" \
  --attempt-status BLOCKED_BEFORE_EXECUTION \
  --phase preflight --exit-code 78 --line 42
python3 "$FINALIZE" verify --run-dir "$work/failure-seal"
python3 - "$work/failure-seal" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
status = json.loads((root / "execution-status.json").read_text())
index = json.loads((root / "artifact-index.json").read_text())
assert status["attempt_status"] == "BLOCKED_BEFORE_EXECUTION"
assert "execution-status.json" in {item["path"] for item in index["files"]}
assert "attempt-context.json" in {item["path"] for item in index["files"]}
assert not (root / "completion-receipt.json").exists()
PY
if python3 "$FINALIZE" failure \
  --run-dir "$work/failure-seal" \
  --attempt-status BLOCKED_BEFORE_EXECUTION \
  --phase preflight --exit-code 78 --line 42 >/dev/null 2>&1; then
  echo "failure terminal was unexpectedly replaceable" >&2
  exit 1
fi

# A preflight command may fail while its stdout and stderr are redirected into
# a retained build log. Sealing the resulting terminal must not append a
# post-index status line to that indexed log.
mkdir "$work/failure-redirected"
cp "$work/failure-seal/attempt-context.json" \
  "$work/failure-redirected/attempt-context.json"
write_redirected_failure() {
  printf 'upstream clone failure\n'
  python3 "$FINALIZE" failure \
    --run-dir "$work/failure-redirected" \
    --attempt-status BLOCKED_BEFORE_EXECUTION \
    --phase preflight --exit-code 128 --line 58
}
write_redirected_failure >"$work/failure-redirected/stock-build-install.log" 2>&1
python3 "$FINALIZE" verify --run-dir "$work/failure-redirected"

printf 'incomplete success evidence\n' >"$work/success-incomplete/evidence.txt"
if python3 "$FINALIZE" success \
  --run-dir "$work/success-incomplete" --phase final-verification \
  >/dev/null 2>&1; then
  echo "success without manifest and phase receipts was unexpectedly sealable" >&2
  exit 1
fi

printf 'success evidence\n' >"$work/success-seal/evidence.txt"
python3 - "$work/success-seal" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
context = {
    "admission_manifest": "manifest.json",
    "attempt_id": "success-fixture",
    "created_at": "2026-08-20T00:00:00Z",
    "experiment_id": "G0-C-ATOMIC-011",
    "spec_path": "experiments/g0/SPEC.g0-c-011.md",
    "spec_sha256": "a" * 64,
    "toolgap_commit": "b" * 40,
    "toolgap_tracked_clean": True,
    "toolgap_tree": "c" * 40,
}
(root / "attempt-context.json").write_text(
    json.dumps(context, indent=2, sort_keys=True) + "\n"
)
planned = [
    "attempt-context.json",
    "controls-passed.json",
    "evidence.txt",
    "manifest.json",
    "manifest.sha256",
    "preflight-status.json",
    "serving-passed.json",
]
manifest = {
    "identity": {
        "attempt_id": context["attempt_id"],
        "experiment_id": context["experiment_id"],
        "gate": "G0",
        "spec_path": context["spec_path"],
        "spec_sha256": context["spec_sha256"],
        "toolgap_commit": context["toolgap_commit"],
        "toolgap_tracked_clean": True,
        "toolgap_tree": context["toolgap_tree"],
    },
    "outcome": {
        "claim_state": "roadmap",
        "gate_decision": "N/A: manifest sealed before runtime arms",
    },
    "planned_success_artifacts": planned,
}
manifest_path = root / "manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
(root / "manifest.sha256").write_text(f"{digest}  manifest.json\n")
PY
success_manifest_sha="$(shasum -a 256 "$work/success-seal/manifest.json" | awk '{print $1}')"
python3 "$FINALIZE" receipt --output "$work/success-seal/preflight-status.json" \
  --status ADMITTED_PRE_ARM --manifest-sha256 "$success_manifest_sha"
python3 "$FINALIZE" receipt --output "$work/success-seal/controls-passed.json" \
  --status CONTROLS_PASSED --manifest-sha256 "$success_manifest_sha"
python3 "$FINALIZE" receipt --output "$work/success-seal/serving-passed.json" \
  --status SERVING_PASSED --manifest-sha256 "$success_manifest_sha"
python3 "$FINALIZE" success \
  --run-dir "$work/success-seal" --phase final-verification
python3 "$FINALIZE" verify --run-dir "$work/success-seal"
python3 - "$work/success-seal" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
status_path = root / "execution-status.json"
index_path = root / "artifact-index.json"
receipt = json.loads((root / "completion-receipt.json").read_text())
status = json.loads(status_path.read_text())
index = json.loads(index_path.read_text())
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert status["attempt_status"].startswith("N/A:")
assert receipt["attempt_status"] == "COMPLETED"
assert receipt["artifact_index_sha256"] == digest(index_path)
assert receipt["execution_status_sha256"] == digest(status_path)
assert "execution-status.json" in {item["path"] for item in index["files"]}
PY

cp "$work/success-seal/completion-receipt.json" "$work/completion-receipt.saved"
chmod u+w "$work/success-seal/completion-receipt.json"
python3 - "$work/success-seal/completion-receipt.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
document = json.loads(path.read_text())
document["gate_decision"] = "PASS"
path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
PY
if python3 "$FINALIZE" verify --run-dir "$work/success-seal" >/dev/null 2>&1; then
  echo "mutated completion Gate decision was unexpectedly accepted" >&2
  exit 1
fi
cp "$work/completion-receipt.saved" "$work/success-seal/completion-receipt.json"
chmod 0444 "$work/success-seal/completion-receipt.json"
cp -R "$work/success-seal" "$work/off-host-success-copy"
rm -rf "$work/success-seal"
python3 "$FINALIZE" verify --run-dir "$work/off-host-success-copy"

# Build small Git fixtures for manifest and identity tests. They exercise real
# Git identity and retained files without pretending to be the pinned SGLang.
fixture_repo="$work/toolgap-fixture"
stock="$work/stock"
treatment="$work/treatment"
run="$work/attempt"
mkdir "$fixture_repo" "$stock" "$run"
for repo in "$fixture_repo" "$stock"; do
  git -C "$repo" init --quiet
  git -C "$repo" config user.name verifier
  git -C "$repo" config user.email verifier@invalid
done
mkdir -p "$stock/python"
printf '[build-system]\nrequires=[]\n' >"$stock/python/pyproject.toml"
printf 'base\n' >"$stock/source.txt"
git -C "$stock" add .
git -C "$stock" commit --quiet -m base
git clone --quiet "$stock" "$treatment"
git -C "$treatment" config user.name verifier
git -C "$treatment" config user.email verifier@invalid
printf 'treatment\n' >>"$treatment/source.txt"
git -C "$treatment" add source.txt
git -C "$treatment" commit --quiet -m treatment

printf 'fixture spec\n' >"$fixture_repo/spec.md"
printf 'fixture patch\n' >"$fixture_repo/patch.diff"
printf '{"stream":true,"text":"fixture"}\n' >"$fixture_repo/request.json"
cp "$TEMPLATE" "$fixture_repo/template.json"
stock_commit="$(git -C "$stock" rev-parse HEAD)"
stock_tree="$(git -C "$stock" rev-parse 'HEAD^{tree}')"
patch_sha="$(shasum -a 256 "$fixture_repo/patch.diff" | awk '{print $1}')"
python3 - "$fixture_repo/template.json" "$stock_commit" "$stock_tree" "$patch_sha" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
doc = json.loads(path.read_text())
doc["identity"]["spec_path"] = "spec.md"
doc["source"]["base_commit"] = sys.argv[2]
doc["source"]["base_tree"] = sys.argv[3]
doc["source"]["patch_sha256"] = sys.argv[4]
doc["source"]["patch_path"] = "patch.diff"
doc["runtime"]["request_path"] = "request.json"
path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
PY
git -C "$fixture_repo" add .
git -C "$fixture_repo" commit --quiet -m fixture

mkdir -p "$run/wheels/stock" "$run/wheels/treatment" "$run/bin"
printf 'stock wheel\n' >"$run/wheels/stock/sglang-stock.whl"
printf 'treatment wheel\n' >"$run/wheels/treatment/sglang-treatment.whl"
printf 'dependency==1\n' >"$run/dependency-lock.txt"
printf 'environment\n' >"$run/environment.txt"
printf 'runtime mapping\n' >"$run/runtime.env"
printf '{"install": "stock"}\n' >"$run/stock-install-report.json"
printf '{"install": "treatment"}\n' >"$run/treatment-install-report.json"
printf '{"model": "fixture"}\n' >"$run/model-snapshot.json"
printf '{"passed": true}\n' >"$run/stock-provenance.json"
printf '{"passed": true}\n' >"$run/treatment-provenance.json"
ln -s "$(command -v python3)" "$run/bin/stock-python"
ln -s "$(command -v python3)" "$run/bin/treatment-python"

python3 "$SEAL_MANIFEST" \
  --template "$fixture_repo/template.json" \
  --spec "$fixture_repo/spec.md" \
  --repo-root "$fixture_repo" \
  --output "$run/manifest.json" \
  --attempt-id local-identity-fixture \
  --stock-checkout "$stock" --treatment-checkout "$treatment" \
  --patch "$fixture_repo/patch.diff" \
  --stock-wheel "$run/wheels/stock/sglang-stock.whl" \
  --treatment-wheel "$run/wheels/treatment/sglang-treatment.whl" \
  --dependency-lock "$run/dependency-lock.txt" \
  --environment-readback "$run/environment.txt" \
  --runtime-env "$run/runtime.env" \
  --request "$fixture_repo/request.json" \
  --model-snapshot "$run/model-snapshot.json" \
  --stock-install-report "$run/stock-install-report.json" \
  --treatment-install-report "$run/treatment-install-report.json" \
  --stock-provenance "$run/stock-provenance.json" \
  --treatment-provenance "$run/treatment-provenance.json" \
  --stock-interpreter "$run/bin/stock-python" \
  --treatment-interpreter "$run/bin/treatment-python"
(cd "$run" && shasum -a 256 manifest.json >manifest.sha256)
manifest_sha="$(shasum -a 256 "$run/manifest.json" | awk '{print $1}')"
python3 "$FINALIZE" receipt --output "$run/preflight-status.json" \
  --status ADMITTED_PRE_ARM --manifest-sha256 "$manifest_sha"
python3 "$VERIFY_IDENTITY" --run-dir "$run" --repo-root "$fixture_repo" \
  --require-receipt preflight-status.json --receipt-status ADMITTED_PRE_ARM

cp "$run/runtime.env" "$work/runtime.env.saved"
chmod u+w "$run/runtime.env"
printf 'drift\n' >>"$run/runtime.env"
if python3 "$VERIFY_IDENTITY" --run-dir "$run" --repo-root "$fixture_repo" \
  >/dev/null 2>&1; then
  echo "runtime.env drift was not rejected" >&2
  exit 1
fi
cp "$work/runtime.env.saved" "$run/runtime.env"

printf 'tracked drift\n' >>"$fixture_repo/spec.md"
if python3 "$VERIFY_IDENTITY" --run-dir "$run" --repo-root "$fixture_repo" \
  >/dev/null 2>&1; then
  echo "tracked protocol drift was not rejected" >&2
  exit 1
fi
git -C "$fixture_repo" checkout -- spec.md
python3 "$VERIFY_IDENTITY" --run-dir "$run" --repo-root "$fixture_repo"

if python3 "$VERIFY_IDENTITY" --run-dir "$run" --repo-root "$fixture_repo" \
  --require-receipt controls-passed.json --receipt-status CONTROLS_PASSED \
  >/dev/null 2>&1; then
  echo "missing predecessor receipt was not rejected" >&2
  exit 1
fi
python3 "$FINALIZE" receipt --output "$run/controls-passed.json" \
  --status CONTROLS_PASSED --manifest-sha256 "$manifest_sha"
python3 "$VERIFY_IDENTITY" --run-dir "$run" --repo-root "$fixture_repo" \
  --require-receipt controls-passed.json --receipt-status CONTROLS_PASSED

# Provenance must bind both the actual interpreter and installed module root.
source_root="$work/source-root"
install_root="$work/install-root"
for relative in \
  sglang/__init__.py \
  sglang/srt/__init__.py \
  sglang/srt/mem_cache/__init__.py \
  sglang/srt/mem_cache/unified_cache/__init__.py \
  sglang/srt/mem_cache/unified_cache/session_ref_tracker.py \
  sglang/srt/mem_cache/unified_cache/unified_tree_core.py \
  sglang/srt/mem_cache/unified_cache/unified_tree_core_interface.py \
  sglang/srt/mem_cache/unified_radix_cache.py; do
  mkdir -p "$install_root/$(dirname "$relative")"
  mkdir -p "$source_root/python/$(dirname "$relative")"
  printf '# %s\n' "$relative" >"$install_root/$relative"
  cp "$install_root/$relative" "$source_root/python/$relative"
done
actual_python="$(python3 -c 'import os,sys; print(os.path.abspath(sys.executable))')"
PYTHONPATH="$install_root" python3 "$PROVENANCE" \
  --source-root "$source_root" --install-root "$install_root" \
  --expected-interpreter "$actual_python" \
  --output "$work/provenance-pass.json"
if PYTHONPATH="$install_root" python3 "$PROVENANCE" \
  --source-root "$source_root" --install-root "$install_root" \
  --expected-interpreter "$work/wrong-python" \
  --output "$work/provenance-fail.json" >/dev/null 2>&1; then
  echo "interpreter swap was not rejected" >&2
  exit 1
fi
python3 - "$work/provenance-fail.json" <<'PY'
import json
import sys
doc = json.load(open(sys.argv[1]))
assert doc["passed"] is False
assert doc["interpreter_matches"] is False
PY

# The final evidence verifier must parse, rather than merely find, provenance,
# pip reports, SSE bytes, and cleanup terminals.
evidence_run="$work/evidence-success"
mkdir "$evidence_run"
python3 - \
  "$evidence_run" "$work/provenance-pass.json" "$actual_python" <<'PY'
import hashlib
import json
import pathlib
import shutil
import sys

root = pathlib.Path(sys.argv[1])
provenance = pathlib.Path(sys.argv[2])
interpreter = sys.argv[3]
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

for arm in ("stock", "treatment"):
    wheel = root / f"{arm}.whl"
    wheel.write_text(f"{arm} wheel\n")
    report = {
        "install": [
            {
                "metadata": {"name": "dependency", "version": "1"},
                "download_info": {
                    "url": "https://example.invalid/dependency.whl",
                    "archive_info": {"hashes": {"sha256": "d" * 64}},
                },
            },
            {
                "metadata": {"name": "sglang", "version": "0"},
                "download_info": {
                    "url": wheel.as_uri(),
                    "archive_info": {"hashes": {"sha256": digest(wheel)}},
                },
            },
        ]
    }
    (root / f"{arm}-install-report.json").write_text(json.dumps(report) + "\n")
    shutil.copy(provenance, root / f"{arm}-provenance.json")
    shutil.copy(provenance, root / f"{arm}-serving-provenance.json")
    (root / f"{arm}-server.pid").write_text("99999999\n")
    (root / f"{arm}-process-group-after.txt").write_text("")
    (root / f"{arm}-gpu-pids-leaked.txt").write_text("")
    (root / f"{arm}-listeners-after-term.txt").write_text("")
    (root / f"{arm}-cleanup-status.json").write_text(json.dumps({
        "passed": True,
        "process_group_survivors": [],
        "attributable_gpu_pid_survivors": [],
        "server_wait_status": 143,
    }) + "\n")
    for number in (1, 2):
        (root / f"{arm}-request-{number}.sse").write_bytes(
            b'data: {"text":"ok","meta_info":{}}\n\ndata: [DONE]\n\n'
        )
        (root / f"{arm}-request-{number}.json").write_text(json.dumps({
            "passed": True,
            "content_type": "text/event-stream; charset=utf-8",
        }) + "\n")

(root / "stock-oracle.txt").write_text("Ran 27 tests\nFAILED (failures=27)\n")
(root / "treatment-oracle.txt").write_text("Ran 27 tests\n\nOK\n")
(root / "installed-seam.txt").write_text("\nOK\n")
(root / "static-inventory.json").write_text('{"passed": true}\n')
(root / "request-input-token-count.txt").write_text("32\n")
(root / "request.json").write_text('{"stream": true}\n')
(root / "model-snapshot.json").write_text('{"model": "fixture"}\n')

planned = [path.name for path in root.iterdir() if path.is_file()]
planned += ["manifest.json", "preflight-status.json", "controls-passed.json", "serving-passed.json"]
manifest = {
    "environment": {
        "stock_interpreter": interpreter,
        "treatment_interpreter": interpreter,
    },
    "source": {
        "stock_wheel_path": "stock.whl",
        "stock_wheel_sha256": digest(root / "stock.whl"),
        "treatment_wheel_path": "treatment.whl",
        "treatment_wheel_sha256": digest(root / "treatment.whl"),
    },
    "runtime": {
        "model_snapshot_path": "model-snapshot.json",
        "request_sha256": digest(root / "request.json"),
        "stock_install_report_path": "stock-install-report.json",
        "treatment_install_report_path": "treatment-install-report.json",
    },
    "planned_success_artifacts": sorted(set(planned)),
}
(root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
manifest_sha = digest(root / "manifest.json")
for name, status in (
    ("preflight-status.json", "ADMITTED_PRE_ARM"),
    ("controls-passed.json", "CONTROLS_PASSED"),
    ("serving-passed.json", "SERVING_PASSED"),
):
    (root / name).write_text(json.dumps({
        "status": status,
        "manifest_sha256": manifest_sha,
    }) + "\n")
PY
python3 "$VERIFY_EVIDENCE" --run-dir "$evidence_run"
cp "$evidence_run/treatment-serving-provenance.json" "$work/serving-provenance.saved"
cp "$evidence_run/stock-cleanup-status.json" "$work/cleanup-status.saved"
python3 - "$evidence_run/stock-cleanup-status.json" <<'PY'
import json
import pathlib
import sys
path = pathlib.Path(sys.argv[1])
doc = json.loads(path.read_text())
doc["server_wait_status"] = 7
path.write_text(json.dumps(doc) + "\n")
PY
if python3 "$VERIFY_EVIDENCE" --run-dir "$evidence_run" >/dev/null 2>&1; then
  echo "crashed server exit status was not rejected" >&2
  exit 1
fi
cp "$work/cleanup-status.saved" "$evidence_run/stock-cleanup-status.json"
chmod u+w "$evidence_run/treatment-serving-provenance.json"
python3 - "$evidence_run/treatment-serving-provenance.json" <<'PY'
import json
import pathlib
import sys
path = pathlib.Path(sys.argv[1])
doc = json.loads(path.read_text())
doc["passed"] = False
path.write_text(json.dumps(doc) + "\n")
PY
if python3 "$VERIFY_EVIDENCE" --run-dir "$evidence_run" >/dev/null 2>&1; then
  echo "false serving provenance was not rejected" >&2
  exit 1
fi
cp "$work/serving-provenance.saved" "$evidence_run/treatment-serving-provenance.json"
printf 'data: [DONE]\n\n' >"$evidence_run/stock-request-1.sse"
if python3 "$VERIFY_EVIDENCE" --run-dir "$evidence_run" >/dev/null 2>&1; then
  echo "SSE without a data JSON event was not rejected" >&2
  exit 1
fi

python3 - "$STREAM_REQUEST" <<'PY'
import importlib.util
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("g0_stream", path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
assert module.is_event_stream("text/event-stream")
assert module.is_event_stream("text/event-stream; charset=utf-8")
assert not module.is_event_stream("application/json")
assert not module.is_event_stream(None)
PY

# Retained wheels live under the attempt, never only in the disposable work
# root. Identity verification above must still pass after unrelated work dies.
mkdir "$work/disposable-work"
printf 'temporary\n' >"$work/disposable-work/value"
rm -rf "$work/disposable-work"
test -f "$run/wheels/stock/sglang-stock.whl"
test -f "$run/wheels/treatment/sglang-treatment.whl"
python3 "$VERIFY_IDENTITY" --run-dir "$run" --repo-root "$fixture_repo"

echo "G0-C-ATOMIC-011 bundle: local counterexamples passed (no CUDA run)."
