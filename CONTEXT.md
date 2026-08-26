# ToolGap

The bounded domain language for ToolGap's session-scoped checked-demotion
evidence work. Canonical contracts and Gate order remain in `docs/` and
`experiments/`; this file only fixes the terms used to discuss them.

## Language

**G1 Gate closure**:
A sealed, independently reviewable G1 terminal decision of `PASS` or `STOP`,
after its SPEC is accepted and execution is explicitly authorized. It is not
synonymous with code completion or a successful result.
_Avoid_: G1 done, implementation complete

**G1 quiescent slice**:
The test-only envelope of one current session generation and one operation over
a committed Host copy and private target tail, with no lifecycle or tree
interleavings. It proves only whether the active action makes upstream
allocator capacity available immediately; it is not a lifecycle, recovery, or
performance guarantee.
_Avoid_: paused-session support, G1 lifecycle runtime

**G1 positive trace**:
Evidence in which an ordinary SGLang request first creates the private target
tail, authoritative Host-copy completion is observed, and only then a
test-only in-process trigger invokes the checked-demotion seam. A hand-built
cache, tree, node, device value, or allocator state cannot stand in for this
positive path; it is limited to deterministic rejection tests.
_Avoid_: manually assembled positive cache state, unit-only physical proof

**Committed Host copy**:
The recovery materialization for exact KV content after authoritative Host-copy
completion and with its relevant pending markers clear. A `backuped` flag or
non-null Host value alone is not a committed Host copy.
_Avoid_: backed up, Host-present copy

**Allocator-visible headroom**:
GPU capacity observed in the upstream allocator after physical free drain, not
a logical session-state transition or merely requested bytes.
_Avoid_: logical reclaim, offered-token headroom

**Candidate bypass**:
Removing candidate intent admission, safe resolution, and immediate checked
execution together while retaining upstream Publication, priority release,
stock eviction, and evidence taps. It tests causal ownership, not disabled
instrumentation.
_Avoid_: tracing off, stock eviction off
