# G1 real checked-demote path audit

> Status: completed
>
> Claim state: `roadmap`
>
> Tracker: [#7 G1: audit the real checked-demote path](https://github.com/icebeeeeeeeef/Toolgap/issues/7)
>
> Canonical owners: [`docs/ROADMAP.md`](../../../docs/ROADMAP.md),
> [`docs/PROJECT.md`](../../../docs/PROJECT.md),
> [`docs/DEMOTION_CONTRACT.md`](../../../docs/DEMOTION_CONTRACT.md), and the
> future accepted `experiments/g1/SPEC.md`.

## Decision question

On the fixed SGLang source, what is the smallest real-engine route from one
private, committed-Host Full-only target tail to physical demotion and
allocator-visible capacity, without introducing a second KV ownership system?

## Evidence

The frozen source is SGLang
[`92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`](https://github.com/sgl-project/sglang/tree/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2),
with the reviewed four-file patch SHA
`e69776678909b4ee49b1c0fa4a8e208666893b659c0508387c83fcdf11e82a9a` as
recorded in [`upstream/sglang/pin.g0-c-016.toml`](../../../upstream/sglang/pin.g0-c-016.toml).

| Stage | Source-proven owner and seam | G1 implication |
| --- | --- | --- |
| target identity | `UnifiedSessionRefTracker.release_session_priority(session_id, generation)` snapshots the Full frontier before target-only release and preserves the generation | a test-only caller supplies only `(session_id, generation)`; it must not reconstruct NodeIds |
| final eligibility + physical action | `UnifiedRadixCache.checked_demote_session` calls exactly one `tree_core.demote_session_checked(node_id)` per resolved Full frontier; the Python TreeCore checks live value, both pending IDs, device locks, residual non-target coverage, settled Host duplicate, and current device-leaf status immediately before its existing `demote` | no candidate check outside this backend call is authoritative |
| physical free | existing `UnifiedTreeCore.demote` returns `DemoteResult.device_frees`; the cache observes every free ID before its `finally` invokes `_free_values` | completion means typed physical output plus an entered drain, not an accepted request alone |
| allocator mutation | cache `_drain_device_frees` routes `FreeComponentDeviceSlot` to `FullComponent.apply_component_action`, which calls the upstream Full allocator's `free` | sample the allocator only after the checked call has returned and the drain has completed |

The patch is the source proof for the first three rows:
[`sglang-session-atomic-checked-demote-v5.patch`](../../../experiments/g0/artifacts/sglang-session-atomic-checked-demote-v5.patch).
The exact G0 source findings and their evidence ceiling are retained in
[`experiments/g0/RESULTS.md`](../../../experiments/g0/RESULTS.md): G0 installed
and served the seam, but deliberately did not invoke physical demotion or take
an allocator sample.

## Decision

Use the reviewed SGLang façade as the single G1 real-engine route:

```text
authoritative write-through completion and cleared pending state
-> test-only candidate trigger with (session_id, generation)
-> UnifiedRadixCache.checked_demote_session(...)
-> backend-owned final checks + existing demote
-> cache-owned exactly-once free drain
-> upstream allocator available-size observation
```

The minimal candidate-owned executor is therefore an **in-process, test-only
G1 harness**. In its enabled arm it invokes the façade once after Host
commitment. In its bypass arm it preserves the same source-proven target
priority release but omits checked resolution and physical invocation. It may
observe typed outcomes and allocator state, but may not receive or manipulate
NodeIds, tree nodes, device tensors, free lists, or allocator internals.

No new production package, cache backend, physical index, allocator adapter, or
public pause API is justified. The exact future filesystem placement is a
frozen-SPEC detail; the boundary above is the constraint. The current repository
has no production executor tree, so choosing one now would be premature rather
than a source-derived need.

## Rejected alternatives

- **Call `UnifiedTreeCore.demote` from ToolGap.** Rejected: it bypasses final
  liveness, Host-commit, lock, coverage, and leaf checks, and forces the caller
  to own NodeId resolution.
- **Maintain a ToolGap session-to-node map.** Rejected: it duplicates upstream
  frontier/path ownership and becomes stale exactly at the final-check boundary.
- **Use terminal `release_radix_session` as the baseline.** Rejected: it closes
  and tombstones identity, contrary to the accepted generation-preserving
  priority-release contract.
- **Add a public pause endpoint now.** Rejected: G1 explicitly confines the
  mechanism to an internal forced trigger; lifecycle/public API choices belong
  to later work.

## G1 admission and stop condition

The future G1 SPEC must freeze a private Full-only target tail, the
write-through commit observation, the enabled/bypass causal pair, the actual
typed frees, and allocator samples before and after the drained call. Its
linearized order is already specified by
[`g1-removal-test.md`](../../../experiments/g0/artifacts/g1-removal-test.md).

This audit is a source-level **GO for G1 SPEC review**, not G1 execution or a
Gate result. Stop G1 if the exact pinned physical run shows only logical
priority release, no completed physical free/drain, no attributable allocator
delta, or an unchanged immediate action/headroom time in the bypass arm. Do not
widen the design to compensate.
