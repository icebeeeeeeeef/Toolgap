# G1 ECS development-loop decision

Canonical owners: `experiments/g1/SPEC.md` for the G1 contract and
`experiments/g1/SPEC.g1-c-019.md` for the consumed C-019 revision.

## Decision change

Formal C-019 attempt `g1-c-019-a1-20260825T170549Z` sealed `INVALID` at
`formal_arms`, exit `125`. The runtime-venv Ninja binding succeeded, but a
marker placed after a continued `timeout` line made the shell comment out the
formal command. Cleanup proved no surviving process group, listener, or GPU
process. Preserve that attempt; do not rewrite or retry it as C-019.

Move runtime development to a separate ECS checkout. Reuse the admitted GPU
host and immutable runtime inputs, but keep all development runs outside the
formal evidence tree and label them `simulated`. Development may iterate until
the exact nine-arm protocol can execute cleanly; it must not iterate on the
mechanism or oracle until the Gate outcome becomes `PASS`.

## Freeze boundary

Do not create an experiment revision for intermediate development fixes. After
the remote enabled-arm smoke and all nine arms are green, commit the smallest
runtime repair, create one clean successor C-020 bundle, and freeze its
commit/tree, input SHA-256 values, and OSS versions before the formal attempt.
The formal terminal remains authoritative whether it is `PASS`, `STOP`, or
`INVALID`; sync the selected commit and sealed evidence back locally after the
terminal rather than after every development iteration.

No verifier self-protection, new threat model, mechanism change, Gate-oracle
change, public API, or second KV data plane is authorized by this decision.

