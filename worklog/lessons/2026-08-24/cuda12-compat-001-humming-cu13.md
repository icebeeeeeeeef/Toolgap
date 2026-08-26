# CUDA12-COMPAT-001 Humming CUDA extra correction

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

Observed: the initial CUDA 12 metadata rewrite left
`humming-kernels[cu13]==0.1.10` unchanged. Its CUDA 13 extra can resolve the
unqualified `nvidia-cuda-{runtime,cccl,nvcc,nvrtc}` packages at version 13,
which the earlier `-cu13` name-only cleanup did not detect.

Correction: patch the Humming extra to `cu12`, remove either CUDA 13 naming
form before the local CUDA wheelhouse install, and reject both forms in the
final dependency lock. The prior staged input set remains non-runnable history;
the replacement requires a new wheel, manifest, and OSS prefix.
