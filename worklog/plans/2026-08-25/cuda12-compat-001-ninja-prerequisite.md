# CUDA12-COMPAT-001 Ninja prerequisite correction

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

## Executable scope

Preserve sealed CUDA12-COMPAT-001 attempt `20260824T1656Z`: its startup log
reaches FlashInfer JIT and fails only because the ordinary Ubuntu `ninja`
command is absent. Its terminal receipt is retained at
`/opt/toolgap-cuda12-compat-001-r9/runs/cuda12-compat-001-20260824T1656Z`
until the indexed evidence is externally anchored. Freeze a successor input revision that adds Ubuntu
`ninja-build` to the existing prerequisite installer, requires `ninja` before
the runner starts, and records `ninja --version` in the sealed environment.
Do not change the provider GPU/CUDA substrate, model, source patches, wheel
inputs, SGLang options, test selector, or claim boundary.

## Completion

Run the static bundle verifier, create a new immutable source seed and OSS input
receipt, then execute one fresh restricted-startup attempt. Treat success only
as `COMPATIBLE_FOR_RESTRICTED_STARTUP_ONLY`; it remains neither formal G1
evidence nor a Gate decision.
