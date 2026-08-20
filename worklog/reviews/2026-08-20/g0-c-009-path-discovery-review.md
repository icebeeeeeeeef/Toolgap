# G0-C-009 CUDA path discovery review

Canonical owner: `experiments/g0/SPEC.g0-c-009.md`.

## Decision

Use a new attempt with `/usr/local/cuda-13.0/bin` prepended to `PATH`; do not
create a successor SPEC and do not modify the frozen bundle.

## Evidence and adversarial check

The 001 terminal proves only that the bare command was absent from the initial
shell `PATH`. It does not show missing CUDA: the same host reported a working
CUDA 13.0 executable at the canonical location that command 20 itself later
adds to `PATH`. That path is then sealed in `runtime.env` and the manifest.

The strongest contrary view is that any post-failure environmental change
invalidates the frozen run. It would be correct for installing/replacing CUDA
or selecting another toolchain. It is not correct for discovering the exact
provider executable already required by the frozen capability contract. A new
attempt ID preserves the counterexample and makes the effective environment
reviewable.
