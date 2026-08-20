# G0-C-009 `nvcc` PATH admission counterexample

Canonical owner: `experiments/g0/SPEC.g0-c-009.md`.

The Alibaba Cloud Ubuntu 24.04 GPU image satisfied the recorded CUDA substrate:
`/usr/local/cuda-13.0/bin/nvcc` reported CUDA 13.0 and the A10 driver was
available. Nevertheless, attempt `g0-c-009-a10-attempt-001` stopped before
either arm because command 20 requires the bare `nvcc` command before it adds
that provider CUDA directory to `PATH`.

Lesson: an admission check must not demand a shell discovery condition before
establishing the canonical location it later treats as sufficient evidence. The
sealed raw attempt is the authoritative observation. G0-C-009 remains frozen;
do not rewrite it or reuse the attempt ID to hide this counterexample.
