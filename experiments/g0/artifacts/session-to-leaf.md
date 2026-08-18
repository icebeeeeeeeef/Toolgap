# Session intent to current device leaves

Status: conservative source-backed resolver design; not implemented on the real
engine in G0.

## Existing ownership facts

SGLang already owns the only physical tree and the only per-session frontier
index needed by the first slice:

- each `TreeComponent` stores `_session_leaves[session_id]` as the deepest
  registered reusable nodes at
  [`tree_component.py#L118-L120`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/components/tree_component.py#L118-L120);
- those nodes are explicitly frontiers, not necessarily physical leaves;
- registration moves the frontier index at
  [`tree_component.py#L167-L177`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/components/tree_component.py#L167-L177);
- Full increments/decrements `session_ref` on the frontier-to-root coverage path
  at
  [`full_component.py#L59-L99`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/components/full_component.py#L59-L99).

`session_ids` is only a frontier marker. It is not a complete ownership set on
an arbitrary prefix node. A resolver based on `node.session_ids == {target}` is
therefore rejected.

## First supported slice

The first G1 slice must use a dense Full-only tree and non-streaming sessions
covered by `--enable-session-radix-cache`. If SWA or Mamba components are
present, or if suspended non-target coverage can exist outside the tracker
(including an untracked streaming-session path), G0 does not infer safe cascade
or non-target coverage and the request is rejected. This trades breadth for an
auditable proof.

Inside one scheduler-thread cache-facade call:

1. validate `session_id` and the current upstream generation;
2. reject if a resumable insert or component eviction walk is active;
3. snapshot the target's Full frontier NodeIds from the existing index;
4. release only the target's session-priority contribution without closing the
   generation;
5. for each snapshotted NodeId, resolve it again from the live TreeCore and
   apply every final predicate below;
6. demote only the safe subset and emit an explicit reason for every clipped
   or rejected NodeId.

No candidate-maintained session-to-node table is allowed.

## Final per-node predicate

For a snapshotted Full frontier `n`, admission requires all of the following at
the immediate execution point:

| Check | Oracle | Failure disposition |
|---|---|---|
| current identity | tracker generation still equals request generation | rejected: stale generation |
| live identity | `node_by_id(id)` resolves the same live node | clipped: node disappeared/replaced |
| target provenance | `id` came from the target snapshot in this call | rejected: unowned target |
| non-target coverage | after target release, Full `session_ref(n) == 0` | clipped: protected non-target coverage |
| device leaf | live `_is_device_leaf(n)` is true | clipped: not current D-leaf/locked |
| committed Host copy | settled Full Host duplicate is true | deferred if pending, otherwise clipped |
| pending state | both node pending IDs are `None`; no live conflicting transfer owns it | deferred: transfer owner |
| structural state | no resumable insert or eviction walk is active | deferred: structural owner |
| cascade scope | Full-only component set | rejected: unsupported component cascade |
| cleanup | one cache wrapper owns and drains the returned frees | operation failure if terminal drain fails |

The live D-leaf predicate is
[`unified_tree_core.py#L1676-L1692`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L1676-L1692).
Direct `demote(node_id)` does not perform this complete check; it verifies only
device/Host presence before its cascade at
[`unified_tree_core.py#L1465-L1503`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L1465-L1503).

## Non-target proof boundary

For the Full-only slice, after the target contribution is removed:

```text
Full session_ref(n) == 0
```

is a conservative proof that no remaining indexed session frontier covers
`n`. This follows from Full's path increment/decrement implementation. A
positive value rejects the node. Active non-session requests are protected
separately by device `lock_ref`, which is part of the live D-leaf check.

This is not a theorem that demoting a shared prefix would change model output.
It enforces the project's stronger lifecycle non-interference rule: do not
directly demote coverage still protected by another session.

## Counterexamples that prevent broader claims

1. A target frontier later gains a device-resident child. It remains in the
   target frontier index but is no longer a D-leaf; final resolution clips it.
2. Two sessions share a prefix. The shared prefix may have no `session_ids`
   marker while `session_ref > 1`; the marker shortcut is wrong.
3. Host indices exist while D2H is pending. The node is `backuped` but not a
   committed recovery point; final resolution defers it.
4. A Full demote can cascade to auxiliary components. G0 has no target-aware
   auxiliary proof, so the first slice rejects those configurations.

The resolver is exact only for the declared conservative slice: it returns the
current safe subset of the target's own upstream frontiers, not every byte that
might be physically reclaimable under a more permissive policy.
