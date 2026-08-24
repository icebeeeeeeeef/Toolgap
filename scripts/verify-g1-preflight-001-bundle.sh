#!/usr/bin/env bash
# Static contract checks for the G1-PREFLIGHT-001 source bundle.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/.." && pwd)"
PATCH_0001="$ROOT/upstream/sglang/patches/0001-atomic-checked-demote.patch"
PATCH_0002="$ROOT/upstream/sglang/patches/0002-g1-scripted-forced-demote.patch"

test "$(sha256sum "$PATCH_0001" | awk '{print $1}')" = \
  e69776678909b4ee49b1c0fa4a8e208666893b659c0508387c83fcdf11e82a9a
test "$(sha256sum "$PATCH_0002" | awk '{print $1}')" = \
  2a1715555c7adac71f368a9a8210f219f3869ac038ca4fb07fb18255fa9007d1
bash -n "$ROOT/experiments/g1/commands/20-g1-preflight-001.sh"
bash -n "$ROOT/experiments/g1/commands/00-g1-preflight-001-bootstrap.sh"
python3 -m py_compile \
  "$ROOT/experiments/g1/commands/g1_preflight_001_finalize.py" \
  "$ROOT/experiments/g1/commands/g1_preflight_001_bundle_manifest.py"

python3 - "$ROOT" "$PATCH_0002" <<'PY'
import json, pathlib, re, sys

root, patch = map(pathlib.Path, sys.argv[1:])
inventory = json.loads((root / "experiments/g1/artifacts/model-files.g1-preflight-001.json").read_text())
pin = (root / "upstream/sglang/pin.g1-preflight-001.toml").read_text()
template = json.loads((root / "experiments/g1/manifest.g1-preflight-001.template.json").read_text())
assert inventory["schema_version"] == 1
assert f'repository = "{inventory["repository"]}"' in pin
assert f'revision = "{inventory["revision"]}"' in pin
assert inventory["revision"] == "c1899de289a04d12100db370d81485cdf75e47ca"
assert len(inventory["files"]) == 10
assert [item["path"] for item in inventory["files"]] == sorted(item["path"] for item in inventory["files"])
assert re.search(r'^gate_decision = "N/A: this bundle cannot produce a G1 PASS or STOP"$', pin, re.M)
assert template["identity"]["kind"] == "preformal_runtime_validation"
assert "input-manifest-verify.log" in template["planned_success_artifacts"]
text = patch.read_text()
assert '"model_path": "Qwen/Qwen3-0.6B"' not in text
assert '_LOCAL_MODEL_PATH_ENV = "TOOLGAP_G1_MODEL_PATH"' in text
start = text.index("+class TestG1PreflightStartup")
end = text.index("+class TestG1EnabledArm", start)
smoke = text[start:end]
for forbidden in ("execute_script", "generate", "checked_demote_session", "release_session_priority", ".demote", ".evict"):
    assert forbidden not in smoke, forbidden
assert '"skip_server_warmup": True' in smoke
assert "G1_PREFLIGHT_SERVER_STARTED" in smoke
PY

for disallowed in TestG1EnabledArm TestG1BypassArm TestG1WriteThroughPending TestG1LoadBackPending TestG1NonTargetCoverage TestG1DeviceLocked TestG1StaleGeneration TestG1StockEvictionLiveness; do
  ! rg -F "$disallowed" "$ROOT/experiments/g1/commands/20-g1-preflight-001.sh"
done
rg -F 'HF_HUB_OFFLINE=1' "$ROOT/experiments/g1/commands/20-g1-preflight-001.sh" >/dev/null
rg -F 'TRANSFORMERS_OFFLINE=1' "$ROOT/experiments/g1/commands/20-g1-preflight-001.sh" >/dev/null
rg -F 'TestG1PreflightStartup.test_local_model_starts_without_runtime_script' \
  "$ROOT/experiments/g1/commands/20-g1-preflight-001.sh" >/dev/null

if [[ -n "${G1_PREFLIGHT_SGLANG_CHECKOUT:-}" ]]; then
  test -e "$G1_PREFLIGHT_SGLANG_CHECKOUT/.git"
  test "$(git -C "$G1_PREFLIGHT_SGLANG_CHECKOUT" rev-parse HEAD)" = \
    92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2
  git -C "$G1_PREFLIGHT_SGLANG_CHECKOUT" apply --check "$PATCH_0001"
  git -C "$G1_PREFLIGHT_SGLANG_CHECKOUT" apply "$PATCH_0001"
  git -C "$G1_PREFLIGHT_SGLANG_CHECKOUT" apply --check "$PATCH_0002"
  git -C "$G1_PREFLIGHT_SGLANG_CHECKOUT" apply "$PATCH_0002"
  python3 -m py_compile \
    "$G1_PREFLIGHT_SGLANG_CHECKOUT/test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py"
fi

echo "VERIFIED_G1_PREFLIGHT_001_STATIC_BUNDLE"
