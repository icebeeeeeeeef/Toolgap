# G1-C-005 arm-runner spawn revision

Canonical owners: `experiments/g1/SPEC.md`, `docs/ROADMAP.md`, and
`experiments/g1/SPEC.g1-c-005.md`.

## Executable scope

`G1-C-001` through `G1-C-003` are sealed `pre_execution` `INVALID` attempts.
`G1-C-004` sealed a separate `pre_execution` `INVALID` at
`2026-08-25T01:32:28Z`. It reached the first real enabled arm, but its generated
arm runner ran unittest at import time. SGLang created a multiprocessing spawn
child, which reimported that main module and failed `_check_not_importing_main`.
The `formal_arms` phase exited `1`; enabled-arm PID/PGID, listener, and GPU
cleanup evidence was clean. Preserve that sealed attempt.

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
