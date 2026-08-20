# G0-C-009 rental attempt 002

Status: terminal retained — failure seal invalid

Canonical owner: `experiments/g0/SPEC.g0-c-009.md`.

## Executable scope

Run one new attempt, `g0-c-009-a10-attempt-002`, using the unchanged committed
G0-C-009 bundle at `1f59969afca994e09902221f27bc63f0c79fa85e`. Invoke command
20 with the existing provider path `/usr/local/cuda-13.0/bin` prepended to
`PATH`, then run commands 21–23 only if the preflight receipt admits the arm.

## Why this is in scope

Attempt 001 proved that the provider CUDA executable exists at this canonical
path, but command 20 checks bare `nvcc` before it establishes the same path in
its own environment. This attempt changes no source, pin, package, GPU
component, or timeout. `runtime.env` and the manifest retain the effective
`PATH`. See the decision-changing review
`worklog/reviews/2026-08-20/g0-c-009-path-discovery-review.md`.

## Boundaries

Attempt 001 remains sealed and is not reused. A missing receipt, any pre-arm
terminal, or later terminal stops this attempt; no phase is rerun in place.

## Observed terminal

The fixed SGLang clone ended with `curl 56`, `early EOF`, and
`invalid index-pack output`, yielding a `BLOCKED_BEFORE_EXECUTION` attempt.
The raw directory was copied off host. Both the remote original and off-host
copy then failed finalizer verification because finalization appended its own
summary to the indexed clone log. This attempt remains preserved but is not an
independently verifiable sealed failure; D024 creates the minimal successor.
