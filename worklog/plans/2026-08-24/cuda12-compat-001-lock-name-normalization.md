# CUDA12-COMPAT-001 dependency-lock name normalization

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

The sealed attempt `cuda12-compat-001-20260824T1401Z` completed the local
wheelhouse and ordinary-dependency installs, but stopped at its post-install
lock assertions. `pip freeze` retained the wheel metadata spellings
`sglang_kernel`, `sgl_deep_ep`, and `sgl_deep_gemm`, while the Bash assertions
matched only their normalized hyphen forms.

Replace those textual `grep` assertions with one Python check that canonicalizes
`-`, `_`, and `.` in distribution names before comparing the same pinned
versions. It must retain the explicit absent-`cuda-tile` check and exact
FlashInfer/Torch-stack versions. This changes neither the resolver route nor
the restricted-startup success scope. The failed sealed attempt remains
evidence; the correction requires a new immutable seed, input receipt, and
attempt.
