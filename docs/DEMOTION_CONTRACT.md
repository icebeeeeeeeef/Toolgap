# Checked Demotion Contract

> Status: `roadmap`
>
> Document role: proposed core mechanism contract
>
> This is the core mechanism contract. It is intentionally independent of any
> dynamic policy or prefetch design.

## 1. Contract Goal

Given a pause intent for one current session generation, reclaim at most a
bounded number of GPU KV bytes whose lower-tier materialization is usable,
without violating active-request safety, non-target session protection,
asynchronous lifecycle semantics, or cleanup ownership.

## 2. Three Distinct Operations

### Publication

Establish that the exact KV materialization required for recovery has a committed
Host-tier copy. A submitted or pending copy is not committed. An upstream
`backuped` flag or non-null Host value is not sufficient project evidence until
the authoritative completion and pending-state semantics are proven. G0 bound
the selected `write_through` source seam to ack synchronization plus both
pending markers clear; `backuped` alone remains insufficient.

### Session-priority release

Remove only the target session's contribution to upstream session-aware eviction
priority. This does not by itself prove that a node was previously unevictable,
nor does it prove that device memory has been reclaimed. The operation must
preserve the declared pause/resume identity; a terminal close/tombstone API is
not automatically a conforming implementation. G0 accepted the narrow
generation-preserving target-only release in the reviewed atomic patch; the
stock terminal release remains non-conforming for this purpose.

### Checked reclamation

Immediately request physical device demotion for leaves that remain eligible at
execution time. This is the candidate-owned differentiating behavior.

These operations may be observed separately. The strongest simple baseline uses
Publication to a committed Host copy plus the G0-proven target session-priority
release and leaves reclamation to stock eviction.

## 3. Request and Outcome Semantics

### Accepted

All scheduled targets satisfied the current contract and at least one physical
demotion was admitted.

### Clipped

Only a safe subset of requested bytes was scheduled. The trace records every
excluded target and reason.

### Deferred

The request is currently unsafe or resource-infeasible but may become legal
without changing its logical intent. Deferral must be bounded or explicitly
cancelled; it cannot become an unowned background retry loop.

### Rejected

The identity is stale, the request is semantically invalid, no safe target can
be proven, or the integration cannot honor the requested contract.

Admission outcome and asynchronous completion outcome are distinct.

## 4. Eligibility Predicate

A target may be submitted for device demotion only when all required predicates
hold at the final execution check:

1. the session generation and pause sequence are current;
2. the requested operation is in a legal lifecycle state;
3. the exact Host-tier recovery materialization is committed;
4. the node still has device KV and is a legal current device leaf;
5. no relevant device-side request lock protects the target;
6. no conflicting store/load or structural operation owns the target;
7. removing the target session's contribution does not violate the declared
   non-target session protection contract;
8. component-level cascade effects have been computed and are safe;
9. every block and temporary resource has one cleanup owner.

`host_lock_ref` must not be treated as a blanket device-reclamation blocker
without a version-matched source proof. Host eviction safety and device eviction
safety are separate questions.

G0 resolved predicate 7 for the selected Full-only seam by combining the exact
session frontier/path bookkeeping with preserved non-target coverage.
`session_ids` alone remains frontier-only and must not be treated as a complete
arbitrary-node coverage set.

## 5. Non-Target Session Contract

The first implementation uses a deliberately conservative contract:

> Checked reclamation must not directly demote a target whose remaining upstream
> session coverage includes a protected non-target session.

This is a lifecycle non-interference rule, not an output-correctness theorem.
Demoting a shared prefix with a valid Host copy may preserve output correctness
while still harming another session's cache hit and tail latency. Those two
properties must remain separate in tests and reporting.

## 6. Linearization and Stale Completion

The design must identify exact linearization points for:

- accepting the pause operation;
- committing the Host copy;
- releasing the target session-priority contribution;
- submitting physical demotion;
- publishing allocator-visible reclamation;
- observing resume or cancellation;
- completing terminal cleanup.

A completion is current only when its full operation identity still matches the
authoritative lifecycle record. A stale completion:

- must not move a newer operation into a completed state;
- must not expose stale residency or recovery assumptions;
- must still release its jobs, buffers, locks, reservations, and ledger entries;
- must produce a terminal DecisionTrace event.

“Ignore stale completion” never means “skip cleanup.”

## 7. Fallback Contract

Fallback is an explicit observed outcome, not an exception hidden from the
requested action.

Allowed candidates, subject to G0 source proof, are:

- keep current device residency when admission is rejected or deferred;
- restore from the committed Host copy;
- invalidate unusable recovery materialization and recompute from authoritative
  tokens;
- fail the request explicitly when neither restore nor recompute is safe.

Every requested/observed disagreement must carry a finite reason code.

## 8. Failure and Race Matrix

The minimum matrix includes:

| Case | Required property |
|---|---|
| Resume before publication commit | No reclamation based on an uncommitted copy |
| Resume during demotion | Current identity determines restore, wait, or recompute; no double ownership |
| Duplicate pause/demote request | Idempotent result or explicit conflict |
| Cancel during publication | All operation-owned resources reach terminal cleanup |
| Cancel after device reclamation | No leaked session claim or retry |
| Late completion after newer pause | Newer state is unchanged; old resources are cleaned |
| Host-copy failure | No false committed state; safe fallback is attributable |
| Shared-prefix target | Reject or clip according to non-target coverage contract |
| Running device lock | Defer or reject; never force demotion |
| Tree changes after resolution | Final execution check catches stale eligibility |
| Partial physical success | Freed and retained targets are both accounted for |

## 9. Proof Obligations

The contract is not considered `shipped` until tests or real traces prove:

- output equivalence against a stock or recompute oracle in declared cases;
- no direct violation of the non-target coverage contract;
- allocator-visible capacity delta matches physical completion accounting;
- stale completions cannot mutate newer lifecycle state;
- quiescence returns all declared ledgers to baseline;
- removing or bypassing candidate intent, resolution, and execution removes the
  attributable immediate checked action and time-to-headroom effect while
  preserving ordinary requests and eventual stock eviction;
- disabling only candidate instrumentation does not change behavior.
