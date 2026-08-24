# CUDA12-COMPAT-001 UnifiedRadix startup correction

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

## Executable scope

Preserve sealed attempt `20260824T1726Z`: it completed CUDA graph capture,
allocated the hierarchical Host pool, then rejected
`enable_session_radix_cache=True` because
`SGLANG_ENABLE_UNIFIED_RADIX_TREE=1` was not declared. Its existing terminal
label is retained even though the old classifier matched successful earlier JIT
log lines. Its terminal receipt remains at
`/opt/toolgap-cuda12-compat-001-r10/runs/cuda12-compat-001-20260824T1726Z`
until external anchoring; do not recycle that run directory. Freeze a successor
that explicitly binds that feature flag to the
restricted startup command and classifies JIT failure only from the final
exception block.

No source patch, model, wheel, provider substrate, selector, request, cache
operation, or G1 claim is added. This remains a no-action startup probe.

## Completion

Run the static verifier, freeze a fresh source seed and input receipt, then run
one new restricted-startup attempt. Retain all earlier sealed attempts and do
not report this as a formal G1 Gate result.
