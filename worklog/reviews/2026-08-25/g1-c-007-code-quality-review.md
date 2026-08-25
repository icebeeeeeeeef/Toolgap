# G1-C-007 code-quality review

Canonical owner: [`experiments/g1/SPEC.g1-c-007.md`](../../../experiments/g1/SPEC.g1-c-007.md)

The candidate was rejected before execution. Review counterexamples showed
that a claimed late failure could omit completed-stage evidence, Python booleans
could satisfy integer fields, immediate PGID sampling raced `setsid`, host
admission could fail before an attempt existed, and the verifier allowed
non-canonical sealed directories.

The minimum repair binds preflight paths to context `work_root`, validates only
the milestones preceding each failure phase, rejects boolean integer values,
polls the real arm PGID with a deadline, creates attempt evidence before host
admission, and requires the sorted index to equal the sealed regular-file set.
Focused counterexamples cover forged late phases, mismatched paths, delayed
`setsid`, host mismatch sealing, unindexed files/symlinks, and reordered indexes.
