# G1-C-010 final matrix review

Canonical owners: `experiments/g1/SPEC.md` and
`experiments/g1/SPEC.g1-c-010.md`

## Decision

G1-C-010 is not an accepted Gate `PASS`. Its sealed run, hashes, cleanup,
off-host replay, and OSS external anchor are valid, but the formal seven-arm
matrix is incomplete against the parent G1 acceptance contract.

## Counterexamples

1. Removing the `load_back_pending_id` guard while retaining the later device
   lock guard does not fail any selected C-010 arm. The existing pinned
   `TestG1LoadBackPending` fixture is executable but was not selected.
2. Removing `_is_settled_full_host_duplicate` while retaining the earlier
   `WRITE_THROUGH_PENDING` guard does not fail any selected C-010 arm. The
   selected pending-write row cannot distinguish these states.

Both omissions contradict `experiments/g1/SPEC.md` section 5, which makes
conflicting-transfer and uncommitted-Host-copy refusal G1 acceptance checks.
The smallest correction is a successor C-011 with the two missing real-runtime
rows; no mechanism or infrastructure redesign is justified.
