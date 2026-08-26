# G1-C-004 runtime-wheel filename revision

Canonical owners: `experiments/g1/SPEC.md`, `docs/ROADMAP.md`, and
`experiments/g1/SPEC.g1-c-004.md`.

## Executable scope

`G1-C-001` and `G1-C-002` sealed separate `pre_execution` `INVALID` attempts
during source restoration. `G1-C-003` sealed a separate `pre_execution`
`INVALID` at resolver after source restore, model preparation, CUDA wheelhouse,
and mirror dependencies succeeded: the runner copied the manifest-bound valid
runtime wheel to generic `runtime-wheel.whl`, and pip rejected that filename.
Preserve all three sealed attempts.

Freeze `G1-C-004` as a new formal runtime revision with the same mechanism,
host envelope, inputs, controls, and terminal oracle. Its sole repair preserves
the manifest-bound original wheel basename in the immutable evidence copy and
the local pip argument, and makes finalizer replay bind the same path and bytes.

## Boundaries

This repair does not reinterpret C-001/C-002/C-003, change the patches or
runtime payload bytes, add a G2/G3/public API/data-plane capability, or execute
ECS/OSS actions. C-004 has its own manifest, attempt identity, and
external-anchor namespace. Its local regression builds a minimal valid wheel,
copies it through the runner helper under its manifest basename, proves pip can
install it, and proves pip rejects the generic C-003 filename.
