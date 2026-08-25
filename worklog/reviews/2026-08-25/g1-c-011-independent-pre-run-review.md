# G1-C-011 independent pre-run review

Canonical owner: `experiments/g1/SPEC.g1-c-011.md`

## Decision

G1-C-011 is ready to freeze and execute on the admitted GPU host. Independent
code and counterexample-matrix reviews found no material issue after the full
local bundle verifier passed.

The nine-arm oracle now discriminates the two credible wrong implementations
that escaped G1-C-010:

- deleting or reordering the `LOAD_BACK_PENDING` guard falls through to the
  later device-lock reason and fails the exact-reason load-back row;
- deleting the settled Host-copy guard fails the row whose real target retains
  Device KV while Host KV is absent and pending work and locks are clear.

The Host-copy fixture uses the pinned Host pool's real `logical_size`,
`available_size`, `alloc`, and `free` APIs, records the full reservation and
restoration transition, and does not assign target/tree/KV state. The
finalizer requires both new rows to preserve Device IDs, make no physical
demote or cache-owned drain, and leave allocator capacity unchanged.

This decision authorizes only a new formal C-011 attempt. It is not a G1 Gate
result; all nine GPU arms, cleanup, sealing, off-host replay, and external OSS
anchoring remain required.
