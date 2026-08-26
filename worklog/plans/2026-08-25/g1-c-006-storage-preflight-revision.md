# G1-C-006 storage-preflight revision

Canonical owners: `experiments/g1/SPEC.md`, `docs/ROADMAP.md`, and
`experiments/g1/SPEC.g1-c-006.md`.

## Executable scope

`G1-C-001` through `G1-C-004` are sealed `pre_execution` `INVALID` attempts.
`G1-C-005` sealed a separate `pre_execution` `INVALID` at resolver when the
host reported `ENOSPC`. Preserve all five attempts.

Freeze C-006 with identical source, runtime wheel, CUDA wheelhouse, model,
patches, selectors, controls, and terminal oracle. Its sole repair adds the
manifest-bound `68719476736` byte free-disk preflight before source restore and
again before dependency installation. The runner records both filesystem
observations. A value below the bound seals `pre_execution INVALID` before any
formal arm.

## Boundaries

This repair does not reinterpret C-001 through C-005, change runtime payload
bytes, selector scope, mechanism, G1 acceptance oracle, or cleanup contract,
add G2/G3/public API/data-plane capability, or execute ECS/OSS actions. C-006
has a new manifest identity and anchor namespace. Its local regression invokes
the actual runner helper with an attainable bound and an impossible bound, and
proves the latter records evidence then rejects before work starts.
