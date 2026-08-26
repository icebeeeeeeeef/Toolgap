# G2 fixed-pin lifecycle source audit

> Status: completed research for [G2: audit fixed-pin lifecycle ingress and authoritative completion events](https://github.com/icebeeeeeeeef/Toolgap/issues/21)
>
> Claim state: `roadmap`
>
> Canonical owners: [`docs/ROADMAP.md`](../../../docs/ROADMAP.md) and
> [`docs/DEMOTION_CONTRACT.md`](../../../docs/DEMOTION_CONTRACT.md)

## Question

On the exact G1-C-020 SGLang lineage, which source-owned events are
authoritative for request/session progression, cancellation, Host-copy
commitment, checked demotion, load-back, structural mutation, and cleanup? What
is the smallest candidate-facing boundary that does not duplicate SGLang's KV
ownership?

## Scope and evidence ceiling

The audited base is SGLang
[`92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`](https://github.com/sgl-project/sglang/tree/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2).
G1-C-020 binds its patched tree to
`7e80d29117b7b3e4b84f6023cfb888ac7c12de35`; its physical mechanism result is
`experimentally validated`, while the project remains `roadmap`
([G1 results](../../../experiments/g1/RESULTS.md)). The G1 result explicitly
excludes output equivalence, restore/recompute, cancellation, recovery, and
asynchronous lifecycle correctness. This audit does not promote any of them.

`0001-atomic-checked-demote.patch` is part of that fixed lineage, not a claim
about stock SGLang. The C-020 scripted patch is test-only; it invokes the cache
from `server.execute_script` after ordinary traffic and adds neither a production
dispatcher message nor a public endpoint
([C-020 scope](../../../experiments/g1/SPEC.g1-c-020.md#L138-L153)).

## Source-backed event map

| Concern | Authoritative source fact | G2 consequence |
| --- | --- | --- |
| Session generation and ordinary request admission | The scheduler gives a radix-native request a source-owned generation with `ensure_session_generation`; opening and terminally closing a session are separate scheduler messages. Closing calls `release_radix_session`, which releases leaves and removes that generation. [Scheduler request path](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/managers/scheduler.py#L2370-L2443) · [open/close](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/managers/scheduler.py#L4833-L4848) · [tracker](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py#L54-L118) | `(session_id, generation)` is valid upstream identity, but it is not a G2 operation identity. Terminal close is not a pause or recovery action. |
| Request execution and cancellation | The scheduler dispatches `AbortReq` with normal requests and session controls, owns its event loop and batch-result processing, and cancels by request `rid`. A queued request is removed; a running request is only marked `to_finish` and completes via the existing batch path. [dispatcher/event loop](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/managers/scheduler.py#L1530-L1543) · [event loop](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/managers/scheduler.py#L1727-L1744) · [abort](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/managers/scheduler.py#L4442-L4576) | A cancellation observation is source-owned but is keyed by `rid`, not by session generation or a demote operation. G2 must bind those identities in its own logical record; it must not infer cancellation from a missing cache node. |
| Session-frontier publication | A finished non-aborted request is what registers its reusable session frontier; a stale request generation is rejected at that registration point. [cache completion hook](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_radix_cache.py#L734-L740) · [stale guard](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py#L54-L80) | The frontier and its `NodeId`s remain upstream-owned. G2 may name the source session/generation, but must never reconstruct or retain its own physical-node index. |
| Host-copy commitment | Write-through completion is the acknowledgment path: it removes the ongoing item, clears `write_through_pending_id`, updates duplicate tracking, and then unlocks the path. The tree's settled-host predicate also requires a device value, a host value, and both pending IDs clear. [ack owner](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_radix_cache.py#L1007-L1018) · [settled predicate](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L1163-L1173) · [tree ack](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L2004-L2018) | A Host value alone is not a publish-complete event. The final G2 eligibility check must continue to defer to SGLang's live check. |
| Checked demotion and physical completion | The G1 patch first snapshots and releases the target session priority, then calls one backend final-check/demote operation per Full frontier and always drains returned frees before producing its typed outcome. The backend owns checks for structural activity, node liveness, two pending markers, locks, residual session coverage, settled Host copy, and device-leaf status. [priority release](../../../upstream/sglang/patches/0001-atomic-checked-demote.patch#L24-L53) · [backend final check](../../../upstream/sglang/patches/0001-atomic-checked-demote.patch#L74-L125) · [cache facade and drain](../../../upstream/sglang/patches/0001-atomic-checked-demote.patch#L207-L291) | The one authoritative completion for the G1 action is the returned typed outcome after cache-owned draining, not admission, a queue action, or an allocator sample. ToolGap must not call `tree_core.demote` or drain allocations itself. |
| Load-back | Load-back locks the source path, commits a transfer, marks `load_back_pending_id`, then at load acknowledgment drops locks, clears the marker, and updates duplicate tracking. [load submission](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_radix_cache.py#L1020-L1123) · [tree commit/ack](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L1950-L2002) | G2 must treat a live load-back as physical state owned by SGLang. Its logical state may decide wait/recompute/fail, but must neither finish nor clear that transfer. |
| Structural mutation and physical cleanup | Tree insertion can start a backup action; device demotion returns frees while retaining the host-only tree node. Cache `_free_values` drains device and host values with a `finally`, and node deletion clears session-leaf and duplicate bookkeeping. [insert](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L1036-L1049) · [demote](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L1465-L1503) · [drain](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_radix_cache.py#L474-L484) · [deletion](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L1572-L1581) | Tree/allocator cleanup remains source-owned. G2 needs only a logical job/trace cleanup ledger, reconciled against the typed source result; it may not substitute a second cleanup path for the physical one. |

## Boundary and missing seam

The smallest correct boundary is a **scheduler-local work item**: ToolGap owns
the logical lifecycle operation, its operation token, cancellation intent, and
trace; the scheduler owns the call into the live cache; SGLang returns the
existing typed outcome and retains all physical state. The C-020 test hook
shows that a scheduler-owner invocation is possible, but it is not a production
ingress or lifecycle contract.

Three absent bindings must be resolved before implementation:

1. There is no production scheduler message that carries a ToolGap operation
   token to one `checked_demote_session` invocation and returns that result.
2. There is no source event joining request `rid`, session generation,
   write-through/load-back acknowledgment, and the demote outcome. The pending
   IDs are physical-transfer markers, not G2 operation IDs.
3. A `DEFERRED` or `CLIPPED` checked-demote outcome occurs **after** priority
   release. The patch does not roll that release back
   ([facade ordering](../../../upstream/sglang/patches/0001-atomic-checked-demote.patch#L222-L291)).
   Therefore “no physical free” cannot be interpreted as “no lifecycle effect,”
   and a same-generation retry/cancel rule cannot be assumed.

This is not G2 `STOP` yet: the source has a one-owner scheduler loop, a
fail-closed cache facade, typed outcomes, and source-owned physical cleanup. It
does require a narrow ingress/result seam or a correspondingly narrowed G2
envelope. Direct background access to `tree_cache`, a ToolGap `NodeId` map, a
second KV cleanup system, or a public pause endpoint would cross the established
ownership boundary and is rejected.

## What G1 did and did not establish

G1-C-020 observed a Full-only, single-generation, single-action private-tail
mechanism with a committed Host copy; the enabled path reached the checked
facade, backend, physical demote, and cache drain once, while unsafe source
states were deferred or rejected ([frozen results](../../../experiments/g1/RESULTS.md#L56-L72)).
Those are source/mechanism observations, not proof that a later lifecycle
operation can be cancelled, retried, restored, recomputed, or cleaned after a
stale completion.

## Decision for the map

Proceed to **[G2: decide lifecycle intent, operation identity, and state model](https://github.com/icebeeeeeeeef/Toolgap/issues/23)** as the next blocked human decision. It must decide the smallest logical operation identity and whether the scheduler-local ingress/result seam can make every required G2 event attributable. It must not choose physical node ownership, a new cache layer, or an implementation yet.
