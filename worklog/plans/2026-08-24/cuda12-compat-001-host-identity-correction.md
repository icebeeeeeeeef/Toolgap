# CUDA12-COMPAT-001 host-identity correction

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

## Observed evidence

The first sealed real-host attempt, `cuda12-compat-001-20260824T2057Z`, ended
at `BLOCKED_HOST_IDENTITY`. The provider image, A10, CUDA 12.8 compiler, and
driver were present. The runner instead compared the untrimmed third field of
`nvidia-smi` CSV output to the pinned driver value.

Bootstrap also restored a macOS-created bare Git seed as its archived UID,
which made Git reject the extracted repository under the safe-directory
ownership check. The archived bytes and failed attempt remain retained; they
are not overwritten.

## Executable scope

1. Normalize `gpu_driver` after CSV parsing, exactly as the existing G0
   preflight runner does.
2. Extract the checked ToolGap bare seed with GNU tar's `--no-same-owner` in
   both bootstrap and inner runner so the host running as root owns the
   restored repository.
3. Add focused static assertions, commit the new frozen revision, then create
   a new manifest, seed, OSS prefix, and receipt before another attempt.

This changes no G1 mechanism, no host substrate, and no Gate conclusion. Any
subsequent terminal still has `claim_state: roadmap` and `gate_decision: N/A`.
