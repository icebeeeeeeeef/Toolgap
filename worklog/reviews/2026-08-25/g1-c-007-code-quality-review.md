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

## Secondary review correction

Secondary review rejected PGID polling because a leader could create a
descendant and exit before the probe. C-007 now uses a pre-workload
`setsid` handshake/ack launcher and seals both records per arm; the regression
kills a surviving descendant group after its leader exits. It also adds a
post-scope `render` failure phase, so classification/render/checksum failures
replay clean scope without falsely requiring a manifest; `seal` still requires
the completed manifest checksum.

Final review found that the group-exit deadline was still ignored after forced
cleanup. C-007 now propagates that timeout, retains PID/PGID state, and refuses
all terminal sealing when process-group exit is unproven. An injected timeout
counterexample verifies nonzero exit with no finalizer call or terminal files;
the real leader-gone descendant cleanup remains the success control.
