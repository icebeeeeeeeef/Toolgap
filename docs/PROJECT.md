# Project Contract

> Status: `roadmap`
>
> Working title: **Safe Session Demotion Executor for SGLang HiCache**
>
> Repository codename: **ToolGap**

## 1. Purpose

Tool-using LLM agents alternate between model execution and external work. While
a tool is running, a session's KV materialization may be idle in GPU memory even
though it could be needed again. Retaining every paused session consumes scarce
HBM; reclaiming too aggressively increases later restore or recompute cost and
can interfere with active requests.

This project is an LLM Serving / AI Infra engineering work sample. Its value is
the ownership and proof of one narrow engine lifecycle contract, not novelty or
the number of storage tiers and policies combined in one system.

## 2. Falsifiable Question

> On one fixed SGLang HiCache version, can a candidate-owned session-scoped
> checked demotion executor, after a committed Host-tier copy exists, safely
> produce allocator-visible GPU headroom earlier than releasing the target
> session's eviction-priority contribution and waiting for stock eviction, and
> improve sustainable load under a joint resumed/foreground SLO?

This question has two independent parts:

1. **Mechanism and correctness:** can the executor identify and reclaim only
   currently legal device leaves, fence asynchronous lifecycle changes, and
   recover or recompute safely?
2. **Measured value:** does immediate checked reclamation add value over the
   strongest simpler upstream behavior?

Failure of either part narrows or stops the project. A policy cannot repair a
missing safe mechanism or a mechanism with no measured value.

## 3. Hypothesis and Causal Chain

The candidate hypothesis is:

> Under reachable GPU-memory pressure, a pause signal can be mapped to a bounded
> set of safely reclaimable device leaves whose Host copies are committed; early
> reclamation makes capacity available before stock eviction would, allowing
> more useful work without unacceptable resumed-request or foreground-request
> tail regression.

The full causal chain that evidence must close is:

```text
pause intent
  -> current session generation and operation identity
  -> committed Host copy
  -> exact legal device-leaf resolution
  -> checked physical demotion
  -> allocator-visible free pages
  -> scheduler or admission headroom
  -> higher sustainable load under joint SLO
  -> bounded restore/recompute and interference cost on resume
```

Freeing bytes alone does not establish the project claim.

## 4. Ownership Boundary

### Candidate-owned

- pause-operation identity over the upstream session generation;
- legal lifecycle transitions and idempotence;
- mapping a session-scoped intent to a checked set of candidate leaves;
- accept, clip, defer, and reject semantics;
- stale-completion fencing;
- cancellation, terminal cleanup, and safe fallback orchestration;
- DecisionTrace connecting intent, resolved targets, physical outcomes, cleanup,
  and request-level effects;
- tests, failure injection, baselines, and measured boundaries.

### SGLang-owned dependency

- radix-tree structure and shared-prefix representation;
- physical KV residency and component data;
- device and Host allocation;
- existing eviction ordering and cascade behavior;
- tensor movement, model execution, and request scheduling;
- upstream session generation and session-reference bookkeeping.

The project must not duplicate the physical KV data plane merely to increase the
amount of candidate-written code.

## 5. Unconditional Mainline

The unconditional project ends at:

1. a fixed SGLang source contract;
2. one Host-tier checked-demotion path;
3. lifecycle identity and asynchronous correctness;
4. recovery, cancellation, and resource cleanup;
5. a removal/bypass test proving candidate ownership;
6. comparison with Publication plus source-proven target session-priority
   release and stock eviction;
7. a measured positive and losing boundary, or an honest negative conclusion.

## 6. Explicit Non-Goals

- building a new KV storage or transfer engine;
- replacing SGLang eviction globally;
- direct orchestrator manipulation of physical KV nodes;
- making Mooncake or another L3 tier a prerequisite;
- proactive prefetch in the unconditional mainline;
- workflow-graph or learned prediction;
- cross-session future-hit valuation;
- distributed, multi-node, RDMA, or production-scale claims;
- CUDA kernel or PagedAttention changes;
- claiming that the mechanism is the first agentic KV-management system.

## 7. Success Conditions

The mainline succeeds as an engineering work sample when all of the following
are true:

These are end-to-end mainline conditions. They are not all G1 exit criteria;
the G1 quiescent mechanism and G2 asynchronous lifecycle split remains owned by
`ROADMAP.md`.

1. the fixed-version source seam and exact ownership mapping are auditable;
2. a real Host-tier checked demotion frees allocator-visible GPU pages;
3. ordinary requests bypass candidate lifecycle behavior;
4. shared-prefix, running-lock, pending-transfer, resume, cancellation, stale
   completion, and fallback cases satisfy the declared contract;
5. quiescence returns block, lock, job, buffer, and reservation accounting to
   baseline;
6. requested and observed physical outcomes are attributable in DecisionTrace;
7. the mechanism is compared fairly with Publication plus source-proven target
   session-priority release and stock eviction;
8. the report preserves at least one losing or no-benefit condition.

A performance win is desirable but is not required to preserve a valuable
negative engineering result. It is required before making an optimization claim.

## 8. Stop and Narrow Conditions

- If exact target-session coverage cannot be proven through a maintainable seam,
  stop active reclamation or propose only one narrow auditable upstream patch.
- If checked demotion cannot create allocator-visible headroom, stop.
- If removing candidate intent, checked resolution, and execution leaves the
  same immediate action and time-to-headroom, the project has become a wrapper
  and must be reshaped. Eventual stock demotion may remain and ordinary stock
  requests must continue to work.
- If active reclamation does not beat Publication plus source-proven target
  session-priority release and stock eviction beyond noise under pre-registered
  workloads, remove active reclamation and retain the diagnosis or upstream
  regression contribution.
- If a safe Host-tier recovery path cannot be exercised, do not add L3 or
  prefetch complexity.
- If reachable regimes do not prefer different actions, retire dynamic policy.

## 9. Open Decisions for Review

1. What exact pause signal is admitted: a dedicated API or a request-carried
   lifecycle hint?
2. Can upstream frontier/path bookkeeping prove non-target session coverage
   without maintaining a second ownership index?
3. What is the smallest supported point that can invoke checked demotion without
   registering an entire custom cache backend?
4. Which upstream completion event is the authoritative observation for
   reclamation and cleanup?
5. What single-node joint SLO and workload envelope should be pre-registered?
