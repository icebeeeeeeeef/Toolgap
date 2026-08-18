# Target-only priority release

Status: source-backed sub-contract inside the corrected atomic vertical
checked-demote prototype; project claim state remains `roadmap`.

## Decision

The stock public `release_radix_session(session_id)` is not a conforming pause
baseline. It is a terminal close operation:

1. it records the session ID in the closed-session tombstone LRU;
2. it removes the current upstream generation;
3. it then releases each component's session contribution.

The fixed-source behavior is visible at
[`session_ref_tracker.py#L99-L118`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py#L99-L118).
Registration rejects a closed or stale request at
[`session_ref_tracker.py#L54-L79`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py#L54-L79).
Therefore reusing public close for pause would destroy the identity needed by a
same-generation resume.

The component operation at
[`tree_component.py#L246-L251`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/components/tree_component.py#L246-L251)
has the desired narrow state mutation: it removes only one session's indexed
frontiers and coverage contribution. It is private and has no generation check
or atomic frontier snapshot.

## Required tracker sub-contract

The proposed internal tracker operation is:

```python
release_session_priority(session_id, generation)
    -> SessionPriorityRelease | None
```

It validates the current upstream generation, snapshots the target's existing
per-component frontier node IDs, calls `component.release_session(session_id)`,
and deliberately does not add a close tombstone or remove the generation. The
snapshot must be consumed by the cache-level checked resolver synchronously;
it is not an external node-selection API.

The first retained one-file patch is
[`sglang-session-priority-release.patch`](sglang-session-priority-release.patch).
Its frozen contract test produced the following informative evidence:

| Arm | Oracle | Observed |
|---|---|---|
| untouched fixed pin | method must exist | expected RED, 5 failures naming the missing method |
| same pin plus retained patch | snapshot/release/generation/stale/disabled oracles | GREEN, 5 tests passed |

Raw summaries are in [`g0-c-red.txt`](g0-c-red.txt) and
[`g0-c-green.txt`](g0-c-green.txt). Fresh review found that this tracker-only
attempt did not establish the maintained backend admission boundary and did not
satisfy the parent successor-runtime fields. It is therefore retained as an
invalid protocol attempt, not decisive Gate evidence.

The decisive corrected evidence is the four-file atomic patch
[`sglang-session-atomic-checked-demote-v5.patch`](sglang-session-atomic-checked-demote-v5.patch)
and 27-case
[`test_atomic_checked_demote_contract_v6.py`](test_atomic_checked_demote_contract_v6.py).
That patch keeps `release_session_priority` as the tracker-owned sub-step behind
one `UnifiedRadixCache.checked_demote_session` caller surface. Valid-generation
release remains applied for accepted, clipped, deferred, and rejected terminal
results; stale/unsupported requests do not release. The actual tracker oracle
observes exactly one current-generation component release and frontier removal,
then separately proves that a stale generation makes zero release calls and
leaves the frontier unchanged. A second session shares one coverage node and
retains its complete frontier and coverage after the target release.

## Safety properties and limits

Source-backed facts:

- every component already owns its target frontier index; no candidate index is
  introduced;
- Full coverage decrement walks only the released frontier's ancestor path at
  [`full_component.py#L59-L65`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/components/full_component.py#L59-L65);
- the generation remains the upstream generation rather than a candidate copy.

Bounded inference:

- preserving the generation and omitting the tombstone preserves the identity
  needed for a later same-generation registration; full resume correctness is
  not proven until G2;
- after target release, a positive Full `session_ref` on a candidate means at
  least one remaining session contribution and must reject target-only checked
  reclamation.

Not proven in G0:

- asynchronous pause/resume/cancel behavior;
- idempotence across concurrent operations;
- physical device reclamation;
- output equivalence or allocator-visible capacity.

The operation must stay behind the internal scheduler-thread cache facade. A
public endpoint returning frontier NodeIds would reintroduce the stale-resolution
race and is explicitly rejected.
