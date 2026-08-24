# G1 allocator and bypass evidence oracle — source audit

> Status: completed source audit; no G1 implementation or GPU execution
>
> Claim state: `roadmap`
>
> Tracker: [G1: define the allocator and bypass evidence oracle](https://github.com/icebeeeeeeeef/Toolgap/issues/10)
>
> Canonical owners: [`docs/ROADMAP.md`](../../../docs/ROADMAP.md),
> [`docs/DEMOTION_CONTRACT.md`](../../../docs/DEMOTION_CONTRACT.md), and a future
> accepted `experiments/g1/SPEC.md`.

## Question and answer

**Question.** What small, pre-registered observation can distinguish “the
forced checked-demote route made capacity available now” from “we only changed
logical priority, observed the Host backup, or happened to see stock eviction
later”?

**Answer.** On the fixed source, the capacity oracle is the Full KV allocator's
`cache.token_to_kv_pool_allocator.available_size()` sampled immediately before
the trigger and immediately after `checked_demote_session(...)` returns. It is
valid only when the candidate result contains non-empty `freed_device_ids`, its
cache-owned drain has returned, the allocator is not inside a deferred
free-group, and no stock-eviction path ran in the measured interval. This is an
allocator-pool capacity reading in **allocatable KV token slots**, not a claim
about driver-wide free bytes reported by CUDA.

The enabled and bypass arms must both finish the same write-through Host
publication and perform the same target-priority release. The enabled arm then
calls the checked facade once; the bypass arm deliberately stops after the
same release and makes **no** checked-resolution or physical-demote call. The
two arms therefore differ only by the candidate physical route.

## Fixed source basis

- SGLang base commit:
  [`92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`](https://github.com/sgl-project/sglang/tree/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2).
- Reviewed, non-stock four-file treatment patch:
  [`sglang-session-atomic-checked-demote-v5.patch`](https://github.com/icebeeeeeeeef/Toolgap/blob/1ccaa9e7730711939f06befaf06cbce387c56d49/experiments/g0/artifacts/sglang-session-atomic-checked-demote-v5.patch)
  (pinned SHA-256
  `e69776678909b4ee49b1c0fa4a8e208666893b659c0508387c83fcdf11e82a9a`).
- The source links below are immutable upstream permalinks. Statements about
  `checked_demote_session`, `release_session_priority`, and
  `demote_session_checked` come from the reviewed patch, not stock SGLang.

## 1. What counts as genuine allocator-visible capacity

For G1's Full-only scope, read the exact allocator owned by the cache:

```python
cache.token_to_kv_pool_allocator.available_size()
```

That is the same capacity query the fixed cache uses before a Full KV
load-back, rather than a ToolGap-owned estimate
([`unified_radix_cache.py#L1084-L1090`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_radix_cache.py#L1084-L1090)).

The physical route is also source-visible:

1. The patched facade retains each `DemoteResult.device_frees`, copies its
   exact indices to `SessionNodeDemoteOutcome.freed_device_ids`, then calls
   `_free_values(...)` in a `finally` before it can return
   ([patch, `checked_demote_session`, lines 207-291](https://github.com/icebeeeeeeeef/Toolgap/blob/1ccaa9e7730711939f06befaf06cbce387c56d49/experiments/g0/artifacts/sglang-session-atomic-checked-demote-v5.patch#L207-L291)).
2. `_free_values` drains device frees before host frees
   ([`unified_radix_cache.py#L474-L484`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_radix_cache.py#L474-L484)).
3. That device drain converts the returned Full values to
   `FreeComponentDeviceSlot`
   ([`unified_radix_cache.py#L899-L906`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_radix_cache.py#L899-L906)); `FullComponent` invokes the actual
   `token_to_kv_pool_allocator.free(indices)` for each value
   ([`full_component.py#L433-L441`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/components/full_component.py#L433-L441)).

### Unit and scope of the reading

For the normal `TokenToKVPoolAllocator`, `available_size()` returns the count
of free and released KV indices; its `free()` appends the released indices to
one of those counted collections
([`allocator/token.py#L42-L76`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/allocator/token.py#L42-L76)).
For a page allocator, the shared base reports page count multiplied by
`page_size`, again in logical KV-token slots
([`allocator/base.py#L38-L59`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/allocator/base.py#L38-L59)).

Therefore each raw run must record the runtime allocator class and `page_size`.
The G1 result may say “`Δ` allocatable Full-KV token slots”; it must **not**
translate that number into CUDA-driver free bytes or overall process HBM
without a separately defined measurement.

`tree_core.component_evictable_size(FULL)` is not this oracle. Fixed SGLang
explicitly presents it as capacity *in addition to* already available allocator
slots ([`unified_radix_cache.py#L2182-L2207`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_radix_cache.py#L2182-L2207)); it can change without a slot becoming immediately allocatable.

### Valid post-drain boundary

The valid `C_after` sample is taken only after the checked-facade call has
returned normally. A returned outcome means the patch has already reached the
`finally` drain above. A thrown drain error has no returned completion and is
not a G1 pass.

One non-obvious guard is mandatory: the base allocator can defer frees inside
`free_group_begin()` / `free_group_end()`; `available_size()` does not include
the temporary `free_group` list until the group ends
([`allocator/base.py#L57-L70`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/allocator/base.py#L57-L70)).
Thus G1 must record and require the read-only condition
`allocator.is_not_in_free_group is True` both before the trigger and at
`C_after`. Otherwise “no capacity delta” is an indeterminate sampling point,
not evidence that demotion did not free anything.

## 2. Completion is not merely a Host backup or accepted request

Write-through D→H publication first marks the node pending
([`unified_radix_cache.py#L971-L979`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_radix_cache.py#L971-L979)).
`writing_check` waits for the finished transfer event and then finishes the
ack ([`unified_radix_cache.py#L1880-L1920`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_radix_cache.py#L1880-L1920)).
Finishing clears the write-through pending mark and records the CPU-side store
([`unified_tree_core.py#L2004-L2018`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L2004-L2018)).

Only after that does the patched backend admit the target: it checks the live
device value, both pending markers, locks, non-target session coverage, a
settled Host duplicate, and current device-leaf status immediately before its
existing `demote(node_id)` call ([patch,
`demote_session_checked`, lines 74-125](https://github.com/icebeeeeeeeef/Toolgap/blob/1ccaa9e7730711939f06befaf06cbce387c56d49/experiments/g0/artifacts/sglang-session-atomic-checked-demote-v5.patch#L74-L125)).
The upstream physical operation removes the device component, accumulates the
device frees, tombstones the device value, and records a GPU remove event
([`unified_tree_core.py#L1465-L1503`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L1465-L1503)).

So G1's completion evidence is the conjunction:

```text
settled write-through Host copy
+ checked outcome: priority_release=RELEASED
+ every intended node: disposition=COMPLETED, reason=DEMOTED
+ non-empty exact freed_device_ids
+ normal return after the drain
+ C_after > C_before in the upstream Full allocator
```

Neither `backuped`, a CPU store event, released session priority, nor the
facade-level `ACCEPTED` string alone is sufficient.

## 3. The precise enabled/bypass pair

Use independent fresh-process/cache runs. In both arms keep the fixed commit,
patch, model, `write_through` setting, session/generation, private-tail
workload, Host-ack waiting, allocator observation, and ordinary SGLang eviction
configuration unchanged. Stock eviction stays enabled; the G1 window simply
contains no ordinary request or other scheduled cache work.

| Shared prefix | Enabled arm | Bypass arm |
| --- | --- | --- |
| wait for the same authoritative write-through ack; record Host commitment; snapshot `C_before`; record the same `(session_id, generation)` | call `cache.checked_demote_session(session_id, generation)` exactly once | call only `cache.session_refs.release_session_priority(session_id, generation)` exactly once; retain its release record, then discard its frontier IDs |
| both release the target's priority once | patched facade resolves the captured Full frontier and calls `tree_core.demote_session_checked(node_id)` once per target node | do **not** call `checked_demote_session`, `demote_session_checked`, `tree_core.demote`, or any ToolGap replacement mover |

This is not a fabricated comparison: the enabled facade itself performs that
priority release before frontier resolution ([patch,
`checked_demote_session`, lines 222-250](https://github.com/icebeeeeeeeef/Toolgap/blob/1ccaa9e7730711939f06befaf06cbce387c56d49/experiments/g0/artifacts/sglang-session-atomic-checked-demote-v5.patch#L222-L250)); the patch defines the separate
release method as snapshot-then-`component.release_session(...)`, preserving
the generation ([patch, `release_session_priority`, lines 24-53](https://github.com/icebeeeeeeeef/Toolgap/blob/1ccaa9e7730711939f06befaf06cbce387c56d49/experiments/g0/artifacts/sglang-session-atomic-checked-demote-v5.patch#L24-L53)).
The original component release reduces coverage from the recorded session
leaves and unmarks them ([`tree_component.py#L246-L251`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/components/tree_component.py#L246-L251)).

The bypass must discard NodeIds: it is a same-logical-release control, not a
second resolver or an external tree owner. It records only the release's
generation, component-leaf count, and Full frontier count for comparison.

## 4. Required raw observations and the stock-eviction trap

For each arm, the frozen raw record needs at least:

- source commit, patch SHA, allocator class, `page_size`, configuration
  fingerprint, run/arm ID, session ID and generation;
- same-workload proof: private-tail token length and the one write-through ack
  boundary; no request starts, resumes, cancellations, inserts, or load-backs
  after that boundary and before `C_after`;
- `C_before`, trigger monotonic timestamp, return timestamp, `C_after`, and
  `ΔC = C_after - C_before`; capture the allocator free-group condition at both
  samples;
- enabled only: full typed `SessionCheckedDemoteOutcome`, each node's
  disposition/reason, exact `freed_device_ids`, and the count of distinct
  Full-KV slots; bypass only: the same priority-release record plus explicit
  zero candidate-call counters;
- source-specific test-only trace counters for the interval: facade,
  `demote_session_checked`, `UnifiedTreeCore.demote`, `UnifiedRadixCache.evict`,
  `evict_device_start`/`evict_device_leaf`, and `UnifiedRadixCache._demote`.
  The enabled trace has the expected checked-route entries; both arms must show
  zero stock-eviction entries in the immediate observation window.

Those counters are an observation requirement, not a new production control
plane. The fixed source has no single operation ID that labels every allocator
free by origin. Its KV event queue cannot fill that gap: a GPU `BlockRemoved`
is emitted for the checked demote *and* for other removal routes, and the event
payload has no candidate-operation identity
([`events.py#L140-L186`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/events.py#L140-L186)).

This matters because ordinary eviction can physically demote a backed-up node
through a different path ([`unified_tree_core.py#L1222-L1249`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L1222-L1249)), while write-back eviction can invoke the cache's ordinary
`_demote` path ([`unified_radix_cache.py#L529-L570`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_radix_cache.py#L529-L570)). A before/after capacity number without
these exclusion observations is not causal evidence for the candidate.

### Post-classification stock-liveness control — separate from the candidate metric

The zero stock-eviction trace in the immediate window proves only that stock
did not contaminate the candidate observation. It does **not** by itself prove
that stock eviction remained live. Add one separate liveness control, but only
after the immediate raw record above has been sealed:

1. Start a new, matched **bypass** run: same source/configuration,
   `write_through` publication, Host-ack boundary, target-priority release,
   and zero candidate-call counters. Do not reuse the immediate-run cache.
2. After that bypass record is sealed, submit one ordinary pressure request
   whose pre-registered allocation demand exceeds the then-available Full-KV
   slots while the released private target remains a backed-up, evictable Full
   tail; record the actual stock victim. It must use the normal scheduler
   allocation route, not a test's direct
   `cache.evict(...)` call.
3. In a read-only test trace, capture `C_stock_before_evict` at the entry to
   the stock `tree_cache.evict(...)` reached by that request,
   `C_stock_after_evict` on its normal return, and the later post-allocation
   value separately. Record the normal-path and stock-eviction counters plus
   `ΔC_stock_evict = C_stock_after_evict - C_stock_before_evict`. The final
   post-request capacity can fall again because the request consumes the slots;
   it is not the liveness delta.

The fixed source supports—and therefore requires for this stronger liveness
claim—the normal request route. `ScheduleBatch.prepare_for_extend` calls
`alloc_for_extend` ([`schedule_batch.py#L2356-L2403`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/managers/schedule_batch.py#L2356-L2403)); its ordinary Full-KV allocation calls
`evict_from_tree_cache` before allocation
([`allocation.py#L152-L172`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/allocation.py#L152-L172)). For a standard allocator, that helper calls
`tree_cache.evict(...)` only for the actual shortfall
([`common.py#L112-L136`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/common.py#L112-L136)). A direct `cache.evict(...)` can test the primitive, but it bypasses
the scheduler/admission route and is therefore insufficient as the retained
stock-policy liveness control.

This later positive stock delta proves only that ordinary SGLang eviction was
still enabled and usable under pressure. It never enters `C_after - C_before`,
`time_to_headroom`, the enabled/bypass comparison, or the G1 PASS decision.
If this liveness control fails, preserve it as a separate stock-path failure;
it cannot rescue or invalidate an already-sealed immediate candidate result.

## 5. Small pre-registered sequence and result shapes

```text
0. Fresh run; fixed source/config; stock eviction remains enabled.
1. Make one private Full tail; wait for its write-through ack to clear pending.
2. Verify the quiescent G1 preconditions; read C_before and free-group state.
3. At t0, do exactly one arm action:
   enabled: checked_demote_session(session_id, generation)
   bypass: release_session_priority(session_id, generation), then stop.
4. On normal return at t1, read C_after and all trace/outcome records.
5. Freeze the raw sequence; do not run another request before classifying it.
```

`time_to_headroom = t1 - t0`: it is the time from the forced trigger to the
first valid post-drain allocator sample, not the write-through-copy duration.

| Shape | G1 interpretation |
| --- | --- |
| Enabled has the full completion conjunction above; `ΔC > 0`; immediate bypass has no candidate route, no physical-free trace, and `ΔC = 0`; neither immediate window has stock-eviction trace entries | **PASS shape** for the narrow mechanism claim: the candidate made allocator capacity available earlier on this exact quiescent path. |
| Both arms show only priority release / Host commitment and no non-empty candidate frees or no `ΔC > 0` | **STOP shape:** logical bookkeeping or publication was observed, not allocator-visible physical completion. |
| Bypass has the same immediate physical removal or positive `ΔC` | **STOP shape:** the observed capacity cannot be attributed to the checked candidate. |
| A stock-eviction trace entry, allocator free-group active, other request/tree mutation, a drain exception, or mismatched source/config/workload appears between samples | **Invalid causal attempt, not PASS.** Preserve it and rerun only under the pre-registered quiescent boundary; do not reinterpret it as a positive or a null mechanism result. |

## Source limits left explicit

1. This audit proves the source route and the proposed oracle, not a real CUDA
   allocation delta, correctness under concurrent resume, recovery, or a
   performance result. Those remain outside G1.
2. The fixed source does not expose a production operation ID that joins the
   checked call to every allocator free. The listed test-only trace is therefore
   required evidence; a plain KV event log is insufficient.
3. The allocator reading describes SGLang's reserved KV pool. It is deliberately
   not a proxy for unrelated PyTorch allocations, CUDA caching-allocator state,
   or process-wide HBM availability.
4. A G1 SPEC must choose the actual runtime allocator class and record it. If
   it is not compatible with the `available_size()` semantics above, this audit
   is not authorization to substitute a different metric silently.
