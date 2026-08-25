# G1-C-005 arm-runner spawn revision

Canonical owners: `experiments/g1/SPEC.md`, `docs/ROADMAP.md`, and
`experiments/g1/SPEC.g1-c-005.md`.

## Executable scope

`G1-C-001` through `G1-C-003` are sealed `pre_execution` `INVALID` attempts.
`G1-C-004` is a separate in-flight frozen attempt. It reached the first real
enabled arm, but its generated arm runner runs unittest at import time. SGLang
creates a multiprocessing spawn child, which reimports that main module and
fails `_check_not_importing_main`. The C-004 parent remains within its frozen
2400-second timeout; do not alter or interrupt it.

Freeze C-005 with the same inputs, mechanism, controls, and terminal oracle.
The sole repair puts generated arm-runner selector loading and unittest
execution in `main()`, invoked only from a `__main__` guard.

## Boundaries

This repair does not reinterpret C-001 through C-004, change patches, runtime
payload bytes, selector scope, or evidence requirements, add G2/G3/public
API/data-plane capability, or execute ECS/OSS actions. C-005 has a new manifest
identity and anchor namespace. Its local regression extracts the actual
generated arm runner, runs one selected test that creates a Python spawn child,
and proves the child exits without bootstrap error while the selector appears
once in parent output.
