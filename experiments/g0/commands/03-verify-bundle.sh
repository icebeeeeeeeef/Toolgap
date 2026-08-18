#!/usr/bin/env bash
set -euo pipefail

G0_ROOT="toolgap/experiments/g0"
SPEC_SHA="$(shasum -a 256 "${G0_ROOT}/SPEC.md" | awk '{print $1}')"
MANIFEST_SHA="$(jq -r '.identity.spec_sha256' "${G0_ROOT}/manifest.json")"

python3 -m json.tool "${G0_ROOT}/manifest.json" >/dev/null
test "${SPEC_SHA}" = "${MANIFEST_SHA}"
test -z "$(jq -r 'paths(scalars) as $p | select(getpath($p) == "" or getpath($p) == null) | $p | join(".")' "${G0_ROOT}/manifest.json")"
test -z "$(rg -n '[[:blank:]]+$' "${G0_ROOT}" --glob '!*.patch' || true)"
rg -l 'github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/' \
  "${G0_ROOT}/artifacts/capability-matrix.md" \
  "${G0_ROOT}/artifacts/source-index.md" >/dev/null
