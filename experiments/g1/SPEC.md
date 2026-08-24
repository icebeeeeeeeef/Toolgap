# G1 Mechanism Protocol Specification — Forced Host-Tier Reclamation

> Gate: G1
>
> Claim state: `roadmap`
>
> Specification state: frozen protocol; not an executable runtime revision
>
> Revision: `G1-PROTOCOL-001`
>
> Formal GPU execution: not authorized

## 1. Authority and purpose

This specification fixes what G1 must prove and how that claim is judged. It
does not invent an implementation, authorize a GPU run, or pretend that code
which has not yet been written is already frozen.

Authority remains:

```text
docs/PROJECT.md
-> docs/ARCHITECTURE.md
-> docs/DEMOTION_CONTRACT.md
-> docs/ROADMAP.md
-> docs/EVALUATION.md + docs/governance/EXPERIMENT_AND_EVIDENCE_SOP.md
-> docs/DECISIONS.md
-> this protocol and its future runtime revision
```

G1's single question is:

> After a normal request has created a private KV tail and an authoritative
> Host copy is complete, does the proposed active action make real SGLang
> Full-KV allocator capacity available immediately, beyond the same preparation
> without that action?

This is a physical-mechanism question only. It does not establish a production
> policy, latency/throughput benefit, output equivalence, restore correctness,
> cancellation, resume, repeated operations, stale completion, partial
> completion, or general cleanup correctness.

## 2. Fixed protocol boundary

The protocol starts from the source decision already accepted for G1 planning:

| Field | Fixed protocol value |
| --- | --- |
| SGLang base | `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2` |
| Existing checked-demote seam | `e69776678909b4ee49b1c0fa4a8e208666893b659c0508387c83fcdf11e82a9a` (`experiments/g0/artifacts/sglang-session-atomic-checked-demote-v5.patch`) |
| Candidate call | `UnifiedRadixCache.checked_demote_session(session_id, generation)` |
| Physical owner | SGLang's existing tree, movement, free drain, and Full-KV allocator |
| Test trigger | in-process and test-only; no public pause API |
| Scope | one current session generation, one operation, one private Full-only target tail, and a committed Host copy |

The existing seam is the starting point, not a line-count limit. G1 may change
SGLang and/or ToolGap when that is necessary to implement or observe the
protocol. Every behavior-changing source change must be identified in the
future runtime revision and appear in both the implementation review and the
formal-run manifest. ToolGap must not replace SGLang's tree, allocator,
movement, or model execution with a second physical data plane.

## 3. Required positive path

The G1 positive case must use a normal SGLang request to create the target
tail. A test may not manufacture the positive state by directly constructing
or mutating a cache tree, node, device value, or allocator state.

The required order is:

```text
ordinary request creates a private Full-KV tail
-> authoritative write-through Host completion and pending clear
-> record available Full-KV allocator capacity (C_before)
-> one test-only action
   enabled: checked_demote_session(session_id, generation)
   bypass:  release the same target's priority, then stop
-> normal return from the action
-> record available Full-KV allocator capacity (C_after)
```

The two arms use fresh processes and identical source, configuration, model,
workload, target shape, Host-copy completion rule, and stock-eviction setting.
The enabled arm executes the active path exactly once. The bypass arm preserves
the same Host publication and target-priority release but does not call the
checked-demote facade, backend checked method, underlying physical demote, or a
ToolGap replacement mover.

The immediate observation window starts at the arm action and ends at
`C_after`. No ordinary request, resume, cancellation, insertion, load-back, or
other tree mutation may occur in that interval. Ordinary stock eviction stays
enabled overall; a separate, later normal request-pressure control must show
that it can still run. That later control is not part of the immediate G1
metric.

## 4. What counts as a valid positive result

The capacity reading is SGLang Full-KV allocator capacity in allocatable token
slots, read through `cache.token_to_kv_pool_allocator.available_size()`. It is
not a CUDA-driver-wide or process-wide free-memory claim.

An enabled arm supports the G1 mechanism claim only when all of the following
are retained as raw evidence:

1. the Host copy is committed and relevant pending work is clear;
2. the checked result reports target-priority release and a completed physical
   demotion for every intended target;
3. its exact freed device IDs are non-empty, and the cache-owned free drain has
   returned normally;
4. the allocator is outside a deferred free group at both samples and
   `C_after > C_before`;
5. test-only trace evidence shows the enabled checked path and no stock
   eviction in the immediate window; and
6. the matched bypass arm has no candidate physical call, no physical-free
   trace, and no immediate capacity increase.

The implementation must record the runtime allocator class and page size. If
the selected allocator cannot make `available_size()` mean allocatable
Full-KV token slots, the formal runtime revision is blocked until it defines a
source-verified replacement metric before execution.

## 5. Required rejection cases

G1 must prove that the action refuses to free a target when any of these facts
is true:

1. the Host copy is not yet committed;
2. a protected non-target session still shares the target;
3. an active request or conflicting transfer owns the target; or
4. the supplied session identity is no longer current.

Each deterministic rejection test must retain the reason, show no physical
free, and show no allocator-capacity increase. These are G1 acceptance checks,
not an attempt to implement G2 lifecycle behavior.

## 6. Branches and invalid attempts

### PASS evidence shape

The full conjunction in section 4 holds for the enabled arm, while the matched
bypass arm shows none of the immediate active-path physical effect. The
separate normal-pressure control shows stock eviction remains usable. A `PASS`
supports only the narrow G1 mechanism statement in section 1; project claim
state remains `roadmap`.

### STOP evidence shape

Stop active reclamation for this project path if either:

- the enabled arm produces only Host publication or priority bookkeeping, not
  completed physical free plus allocator-capacity increase; or
- the bypass arm has the same immediate physical result or capacity increase,
  so the proposed active action cannot be credited.

The raw evidence remains a valid negative result. Do not widen the design to
hide either outcome.

### Invalid or unresolved attempt

A source/configuration mismatch, missing required record, deferred allocator
free group, unexpected stock eviction, other request/tree mutation in the
immediate window, drain error, crash, timeout, or failed cleanup does not
produce PASS or STOP evidence. Preserve the attempt and resolve the cause with
a new runtime revision before another formal run.

## 7. From protocol to a formal GPU runtime revision

Implementation and local iteration may begin only after the project owner
explicitly authorizes that work. They are not formal G1 runtime attempts.

Before the first formal GPU attempt, the owner must approve a new immutable
runtime revision (for example, `SPEC.g1-c-001.md`). That revision must freeze:

- the complete SGLang and ToolGap source changes, exact commits/patches and
  changed-path inventory;
- model and configuration, workload construction, target size, and all test
  code and commands;
- a capability-compatible GPU environment, with exact observed host/software
  identity recorded in the run manifest;
- the exact enabled, bypass, rejection, and stock-liveness controls;
- repeat count, arm order, timeout and cleanup rules, raw-artifact inventory,
  manifest/checksum procedure, and independent-review handoff.

It must bind the source and protocol identity in an immutable manifest before
either formal arm starts. Any later change to source, workload, action,
threshold, or analysis creates another runtime revision and run identity. No
formal result may be combined across revisions.

## 8. Non-goals

This protocol does not authorize or define:

- a public pause or lifecycle API;
- G2 resume, cancellation, stale completion, failure, partial completion, or
  cleanup interleavings;
- G3/G4 performance or production-write-policy comparisons;
- dynamic policy, L3/Mooncake, prefetch, a replacement cache backend, a second
  physical KV data plane, or an upstream merge campaign.

## 9. Review and progression

This protocol is a planning artifact. It is not G1 execution authorization,
implementation evidence, a frozen runtime configuration, or a Gate decision.
The next work is to obtain a narrow owner authorization for implementation,
then review and freeze the exact runnable source and formal runtime protocol
before any GPU experiment. A sealed runtime bundle requires independent review
before G1 can be marked `PASS` or `STOP`.
