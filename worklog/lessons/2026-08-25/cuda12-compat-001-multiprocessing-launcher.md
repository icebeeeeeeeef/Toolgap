# CUDA12-COMPAT-001 multiprocessing launcher

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

The sealed r7 attempt `cuda12-compat-001-20260824T1609Z` passed its exact
package inventory, Torch CUDA, and `sm_86` compiler checks, then failed before
a valid SGLang startup because the direct test loader ran through `python -`.
Its multiprocessing child tried to re-open `<stdin>`. The attempt was stopped
after confirming no model GPU process and sealed as `SGLANG_STARTUP_FAILED_OTHER`;
it is not a SGLang compatibility result. A test launcher that may spawn must
be a real immutable file with a main guard, and a successor uses new seed,
receipt, and attempt ID.
