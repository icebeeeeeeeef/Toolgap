# Proposed atomic checked-demote boundary

Status: `roadmap`; absent from stock SGLang
`92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`.

## Why preparation alone is unsafe

`G0-C-ADMISSION-002` returned immutable eligible NodeIds and required G1 to call
`demote` later. That is not an execution-time check: the tree can change between
calls while all preparation tests still pass. An admission token without an
upstream mutation epoch/CAS would only rename the race and add ownership state.

The smaller correct boundary is one cache caller surface whose registered
backend combines the final check with the already-existing physical primitive:

```python
UnifiedRadixCache.checked_demote_session(session_id, generation)
    -> SessionCheckedDemoteOutcome

UnifiedTreeCoreInterface.demote_session_checked(node_id)
    -> SessionDemoteExecution
```

The first is the single caller contract. The second is its maintained backend
sub-step. It has a concrete `UNSUPPORTED_BACKEND` default so an old external
backend remains constructible but can never silently demote.
The 006 oracle gives that legacy backend a recording/raising `demote` method,
proves the default returns no result with zero physical calls, and proves the
vertical cache path performs its one-way release before that permanent reject.

## Linearization

```text
cache rejects non-Full scope
-> tracker validates exact generation
-> tracker snapshots target frontier NodeIds before mutation
-> tracker removes target contributions without close/tombstone
-> cache calls the registered backend for each snapshot
-> backend checks structural owners, live/device state, both pending IDs, every
   device lock, remaining Full session coverage, settled Host duplicate, and
   current device-leaf state
-> in that same backend method, only the eligible branch calls existing demote
-> cache attempts to copy freed device IDs
-> a `finally` path pops/drains raw device and Host frees exactly once even if
   observation fails
-> cache returns actual typed terminal per-node and aggregate outcomes
```

No `ELIGIBLE` capability is returned to a caller. The source prototype wraps the
existing upstream `demote`; it adds no allocator, movement algorithm, physical
index, worker, public pause API, or lifecycle executor. G0 calls only a registered
fake backend, never the real physical method.

## Aggregate and release semantics

For a valid generation and Full-only scope, target priority release persists
even if physical completion count is zero. That is the conforming release-only
baseline, not a rollbackable reservation.

| Outcome | Rule |
|---|---|
| `ACCEPTED` | every requested frontier completed and at least one completed |
| `CLIPPED` | at least one completed and at least one did not |
| `DEFERRED` | none completed; every blocker is transient |
| `REJECTED` | stale/unsupported/empty, or none completed with a permanent reject |

Every node retains its terminal reason and copied device block IDs. Raw
`DemoteResult` never escapes cache cleanup ownership. Not-current-D-leaf is
transient because removal of a device-resident child can make the same NodeId
intent legal without changing that intent.

## Ownership

| Concern | Owner |
|---|---|
| generation/frontier/contribution facts | upstream tracker/components |
| final private tree predicates and existing physical primitive | registered upstream TreeCore backend |
| caller surface, aggregate result, raw-result drain | upstream `UnifiedRadixCache` |
| pause intent, sequence, operation identity, fallback, DecisionTrace | candidate logical runtime in later Gates |
| allocator, residency, movement, eviction, model execution | upstream unchanged |

## Retained proof and limits

The decisive source-contract artifacts are
[`test_atomic_checked_demote_contract_v6.py`](test_atomic_checked_demote_contract_v6.py)
and
[`sglang-session-atomic-checked-demote-v5.patch`](sglang-session-atomic-checked-demote-v5.patch).
The test loads the actual patched interface with dependency stubs, constructs
legacy and overriding fake backends through the actual fixed-pin registry, and
executes extracted cache/Python-backend methods plus the actual cache outcome
class definitions with fake values. Its 27 cases also observe target-only
multi-session release, exact caller and per-node identity, all frontier orders,
Host-lock non-blocking, legacy release semantics, multi-index freed-ID copying,
structural zero-demote, transient D-leaf retry, and cleanup after observation
failure. Both inherited executable dependencies are hash-checked at startup.

This can support only `RESHAPE`: stock lacks the contract. It does not prove the
patch imports in a real SGLang environment, physical demotion succeeds,
allocator headroom changes, a session resumes, cleanup failure is orchestrated
in production, or performance improves.
