# Runtime JIT tools belong in admission

Canonical owner: `experiments/g0/SPEC.g0-c-015.md`.

Wheel installation alone did not prove the runtime toolchain was complete:
FlashInfer generated a CUDA extension during server startup and invoked
`ninja`. If a fixed runtime path can launch a build tool after installation,
that executable must be installed by project prerequisites, checked before the
attempt, and versioned in the sealed environment readback.
