# G1-C-002 source-restore revision

Canonical owners: `experiments/g1/SPEC.md`, `docs/ROADMAP.md`, and the new
`experiments/g1/SPEC.g1-c-002.md`.

## Executable scope

`G1-C-001` sealed a `pre_execution` `INVALID` during source restoration when
the runner passed the literal malformed glob `000{1-3}-*.patch` to
`sha256sum`. Preserve that sealed attempt. Freeze `G1-C-002` as a new formal
runtime revision with the same mechanism, host envelope, inputs, controls, and
terminal oracle, changing only source restoration to enumerate the three
manifest-bound patch paths explicitly.

## Boundaries

This repair does not reinterpret C-001, change the patches or runtime inputs,
add a G2/G3/public API/data-plane capability, or execute ECS/OSS actions. A
future C-002 attempt has a new input manifest, attempt identity, and external
anchor namespace.
