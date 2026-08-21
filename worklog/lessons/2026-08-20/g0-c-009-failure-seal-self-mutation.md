# G0-C-009 failure seal self-mutation

Canonical owner: `experiments/g0/SPEC.g0-c-010.md`.

An immutable index is insufficient if the sealing command itself can inherit a
redirected file descriptor and append a human summary after it computes hashes.
The off-host verifier correctly rejected that situation. Treat an unverified
terminal as evidence of a protocol defect, not as a valid negative result or a
transport problem.
