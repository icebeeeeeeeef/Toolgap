# G1-C-013 pending-state basis review

Canonical owners: `experiments/g1/SPEC.g1-c-013.md` and
`experiments/g1/SPEC.g1-c-014.md`.

## Decision change

Frozen commit `6347aae14a98b5a2eda68d6fcf7bb92c1c3baada` is not approved for GPU
execution. Its load-back fixture contains no pending-state fabrication, but
the mutation oracle only rejects direct assignments. Equivalent `setattr` or
mapping-update fabrication survives that check, so the oracle does not prove
the stated boundary.

## Accepted repair

G1-C-014 must enforce the positive basis instead of extending a blacklist:
after removing only the threshold-derived generation argument and explicit
Host-tail qualification, its load-back class must equal frozen C-012 exactly.
Any third change, including helper calls or indirect state mutation, is then
rejected. C-013 remains unexecuted and has no Gate conclusion.
