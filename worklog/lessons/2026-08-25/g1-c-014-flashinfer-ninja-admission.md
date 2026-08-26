# FlashInfer JIT requires system Ninja admission

Canonical owner: `experiments/g1/SPEC.g1-c-015.md`

## Observation

Sealed C-014 attempt `g1-c-014-a2-20260825T144921Z` reached enabled-arm
startup, then FlashInfer JIT failed to execute bare `ninja` with
`FileNotFoundError`. Cleanup and offline verification were clean, so this is an
ordinary missing host prerequisite, not checked-demotion or CUDA evidence.

## Correction

Any executable launched by a runtime JIT belongs in host admission. C-015
therefore binds a self-verifying installer for Ubuntu `ninja-build`, requires
the exact `/usr/bin/ninja` path before the first arm, and seals both runtime and
dpkg versions for offline replay. It does not change the GPU substrate or Gate
oracle.
