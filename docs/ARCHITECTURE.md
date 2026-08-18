# Runtime Architecture

> Status: `roadmap`
>
> Document role: proposed runtime boundary
>
> No runtime component described here is currently implemented in `toolgap/`.

## 1. Candidate Upstream Pin

The current source-audit candidate is SGLang commit:

```text
92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2
```

Before implementation, Gate G0 must either adopt this commit or replace it with
another exact pin and rerun the contract audit. No unpinned `main` claim is
allowed.

Version-matched source facts already used by this draft:

- `UnifiedTreeCore.demote(node_id)` is an existing physical primitive whose
  upstream precondition includes a `backuped` node; that flag alone does not
  prove the project's stronger committed, pending-free Host-copy contract;
- upstream session tracking already has session generations and closed-session
  tombstones;
- `release_radix_session()` removes the current generation and records a closed
  session; it is not by itself proof of a temporary priority release that
  preserves the declared pause/resume lifecycle;
- `session_ref` participates in eviction priority rather than acting as a hard
  device pin;
- `session_ids` marks session frontier leaves and is not by itself an arbitrary
  node's exact coverage set;
- device-leaf eligibility is a dynamic tree property and must be revalidated at
  execution time.

Primary source links:

- [tree demotion](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L1465-L1501)
- [device-leaf predicate](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L1676-L1690)
- [session generations and terminal release](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py#L42-L119)
- [session frontier markers](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/components/tree_component.py#L171-L178)
- [session-aware eviction priority](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/components/full_component.py#L186-L188)

## 2. Design Principles

1. Safety filters authorize actions; policy never authorizes an unsafe action.
2. Upstream owns physical allocation, tree structure, movement, and eviction.
3. Candidate code owns session-scoped intent, checked resolution, lifecycle
   fencing, fallback, cleanup, and evidence.
4. The first implementation is Host-tier only.
5. Ordinary requests preserve the stock path.
6. A direct node-level primitive is never exposed to an external orchestrator.
7. Every accepted request records what was requested, resolved, executed, and
   cleaned up.

## 3. System Context

```text
Agent/orchestrator
  -> pause intent(session_id, generation, pause_seq, target_bytes)
  -> SessionDemotionService
       -> LifecycleRegistry
       -> TargetResolver
       -> EligibilityChecker
       -> DemotionExecutor
       -> CompletionFence / CleanupLedger
       -> DecisionTrace
  -> audited SGLang HiCache interfaces
       -> unified radix tree
       -> Host/device KV data plane
       -> allocator and scheduler
```

The orchestrator supplies logical intent. It does not select physical nodes or
override engine safety.

## 4. Proposed External Contract

```text
demote(
  session_id,
  upstream_generation,
  pause_seq,
  target_bytes,
  reason
) -> DemotionDecision

DemotionDecision:
  operation_id
  outcome: accepted | clipped | deferred | rejected
  requested_bytes
  eligible_bytes
  scheduled_bytes
  reason_code
```

The result describes admission, not final completion. Completion is a separate
event tied to the same operation identity.

This proposed external shape is not selected by the first forced-mechanism
experiment. G1 may use an internal test trigger inside its declared quiescent
envelope. The dedicated-API versus request-carried-hint decision remains open
until G0 proves the narrowest supported seam; a successful internal trace does
not by itself authorize a public orchestrator API.

## 5. Identity Model

The logical operation identity is:

```text
(session_id, upstream_generation, pause_seq, operation_id)
```

- `upstream_generation` is authoritative for session incarnation.
- `pause_seq` distinguishes multiple pauses in one session generation.
- `operation_id` distinguishes retries and asynchronous work within one pause.

Candidate code must not create an independent session generation that can
silently disagree with upstream.

## 6. Minimal Lifecycle

```text
ACTIVE
  -> PAUSE_OBSERVED
  -> DEMOTION_ADMITTED | DEMOTION_DEFERRED | DEMOTION_REJECTED
  -> DEMOTION_IN_FLIGHT
  -> DEMOTED | DEMOTION_FAILED
  -> RESUMING
  -> ACTIVE

Any non-terminal state -> CANCELLED -> CLEANED
```

The persisted state should be no richer than required to fence completion,
perform cleanup, and explain observed behavior.

## 7. Proposed Components

### SessionDemotionService

Owns the public logical operation, idempotence, and result semantics.

### LifecycleRegistry

Maps the operation identity to current state, pending work, and cleanup
ownership. It composes with upstream generation rather than replacing it.

### TargetResolver

Resolves session intent to candidate frontier/path nodes. Its central Gate G0
obligation is proving non-target session coverage without inventing a broad
parallel ownership system.

### EligibilityChecker

Revalidates Host commitment, current device-leaf status, relevant locks,
pending-transfer state, generation, non-target coverage, and cascade safety.

### DemotionExecutor

Invokes the smallest audited upstream physical path. It does not implement a
second allocator, radix tree, or tensor-transfer engine.

### CompletionFence and CleanupLedger

Suppresses stale state publication while still releasing every temporary
resource owned by an operation.

### DecisionTrace

Records intent, identity, resolved targets, filter failures, physical results,
allocator delta, fallback, timings, and terminal cleanup.

## 8. Integration Boundary to Prove in G0

G0 must answer all of the following before implementation architecture is
treated as selected:

1. How are exact candidate leaves derived from upstream session bookkeeping?
2. Which object establishes a committed Host copy?
3. Which source-proven operation removes only the target session's priority
   contribution while preserving the declared resume lifecycle?
4. Which lock and pending-transfer fields are relevant to device reclamation?
5. How is device-leaf and cascade safety checked immediately before execution?
6. Which supported or narrowly patched seam invokes physical demotion?
7. Which event reports final freed block IDs or bytes?
8. How does allocator-visible capacity prove a physical rather than logical win?

If these answers require replacing the cache backend or maintaining a second
physical ownership system, the design must be narrowed or stopped.
