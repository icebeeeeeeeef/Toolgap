# Proactive Prefetch Admission Contract

> Status: `roadmap`
>
> Project claim state: `roadmap`
>
> Admission: separate future review; this is not G6 and is not part of the
> G0-G4 unconditional mainline.
>
> Implementation: not started. Experimental evidence: none.

## 1. Purpose and Boundary

This document specifies how to decide whether a non-oracle, proactive
storage-to-Host prefetch mechanism deserves a separate implementation review.
It does not authorize implementation, change the checked-demotion contract, or
turn prefetch into a prerequisite for the mainline project.

The question is narrow:

> Given a real hint before a resumed request reaches the engine, can the exact
> storage-to-Host transfer that the request would otherwise trigger be completed
> during usable slack, with lower joint serving cost than the fixed request-time
> reactive baseline and without unacceptable contention or reservation cost?

The answer must be measured on the fixed SGLang source pin selected by G0. The
mainline must remain correct and useful if this document, its implementation,
and its experiments are deleted.

## 2. What Is Being Admitted

The candidate future mechanism may submit a prefetch for a previously committed
lower-tier materialization. The first admission target is specifically:

```text
L3/storage -> Host
```

This is the exact segment that the future mechanism would attempt to move before
request arrival. The future review must verify on its adopted fixed pin whether
the reactive baseline starts this segment only after request arrival.
`Scheduler._prefetch_kvcache()` and the HiCache `prefetch_from_storage()` path
are candidate source locations, not accepted source facts or implementation
authorization. Their exact behavior and configuration must be frozen in that
future admission experiment's own manifest, not added as a G0 obligation.

The mechanism must not call this segment “restore time” in aggregate. Host to
device movement, request admission, scheduling delay, recompute prefill, and
first-token latency are separate segments. A prefetch result may report an
effect on those segments, but it may claim to hide only the transfer that was
actually issued before request arrival.

Prefetch does not establish a committed copy, repair stale lifecycle state, or
authorize device reclamation. Those responsibilities remain in
[`DEMOTION_CONTRACT.md`](../DEMOTION_CONTRACT.md).

## 3. Hint Models

The admission experiment must select one model before measurement. A hint is
non-oracle only when it is available from the deployed agent/runtime path and
does not inspect the future trace, future request, or measured answer time.

### H1 — Tool-start expected-duration hint

At tool invocation, the agent framework sends an expected return window or an
expected resume interval. The engine records the hint receipt time and may
schedule prefetch planning immediately. This model offers the largest possible
window but is exposed to prediction error, cancellation, and tool retries.

### H2 — Tool-completion, pre-request hint

When the tool result is available, the framework sends a resume-imminent hint
before assembling or submitting the next model request. The available window is
the actual framework, serialization, transport, and admission delay. This model
has less prediction error but often has little slack.

### H3 — Request-arrival hint

The hint is emitted only when the resumed request reaches the engine ingress.
Its pre-request slack is zero. It is therefore a control condition for showing
that a purported proactive path has merely reproduced the existing request-time
reactive prefetch behavior; it is not evidence of a new hiding opportunity.

The experiment must report hint age, duplicate and cancelled hints, the mapping
from hint to session generation/resume operation, and whether each hint arrived
before the corresponding request. A stale hint must be harmless and must not
change current lifecycle state.

## 4. Strict Clock and Slack Contract

All timestamps used for admission are monotonic timestamps from a declared
clock domain. If hint and request events cross processes, the experiment must
record synchronization/offset handling and its uncertainty; wall-clock labels
alone are not sufficient.

For one `(session_id, upstream_generation, pause_seq, resume_id)` pair define:

```text
t_hint       = engine-observed receipt of an accepted non-oracle hint
t_arrival    = corresponding resume request at the same engine ingress used by
               the reactive baseline, before its request-time prefetch starts
t_start      = actual start of the candidate storage-to-Host transfer
t_done       = completion and validation of that exact transfer
T_segment    = t_done - t_start
```

The offered prefetch slack is:

```text
offered_slack = max(0, t_arrival - t_hint)
```

The usable execution slack is:

```text
usable_slack = max(0, t_arrival - t_start)
```

The distinction matters: queueing or scheduling may consume the interval after
the hint. A transfer is fully hidden only when `t_done <= t_arrival` and its
completion is attributable to the same generation and resume operation. If a
transfer continues after arrival, only the overlap before arrival may be
reported as overlap; the remaining interval stays on the request's critical
path.

The contract must also record the baseline's corresponding
`t_reactive_start`, `t_reactive_done`, and `T_reactive_segment` under the same
engine and load. A claim that prefetch has positive slack is not enough: the
transfer must be the same materialization and must be usable by the subsequent
request without a duplicate storage read.

## 5. Admission Baselines and Fair Comparison

At minimum compare, with identical workload, committed lower-tier copies,
executor behavior, memory budget, and instrumentation:

1. **R0 — stock no-hint control:** no lifecycle hint and no candidate
   prefetching;
2. **R1 — stock reactive baseline:** the fixed SGLang request-time
   storage-to-Host prefetch path, triggered when the request reaches the
   waiting queue;
3. **R2 — candidate proactive path:** the selected H1 or H2 signal, with the
   same physical storage-to-Host executor and an explicit no-op result when the
   hint is stale or infeasible;
4. **R3 — optional timing reference:** an offline local oracle may supply an
   earlier admissible hint for analysis, but it cannot be used as the deployed
   PASS signal or as a claim about the runtime.

R1 is the minimum bar. A candidate that only invokes the same transfer at
request arrival has not demonstrated proactive value. R3 is an information
reference, not an implementation target or an upper bound on a global policy.

## 6. Costs and Failure Semantics

The admission record must include both benefits and costs:

- false-positive hints: wasted reads, duplicate work, and stale reservations;
- false-negative or late hints: request-time reactive fallback and exposed
  transfer time;
- storage, Host-memory, and DMA bandwidth contention with foreground traffic;
- temporary Host-memory reservation and its impact on other sessions;
- queue occupancy, cancellation, duplicate requests, and generation changes;
- validation, deduplication, and cleanup overhead;
- interference with active Host eviction, device admission, and recovery;
- storage miss, partial transfer, checksum/metadata failure, and recompute or
  reactive fallback.

The mechanism must obey the existing lifecycle identity and cleanup rules. A
prefetch completion for an old generation may not publish residency for a new
generation, but it must still release its buffers, jobs, locks, and
reservations. Prefetch failure is an observed fallback, not silent success.

## 7. Evidence and Decision Rules

The experiment must publish the hint model, clock definitions, segment timings,
noise/repetition protocol, raw traces, and the joint resumed/foreground SLO.
Client traces can calibrate hint and tool behavior; server traces must establish
residency, queueing, transfer, and allocator effects.

### PASS

Grant a future implementation review only if all of the following are shown in
reachable, pre-registered regimes:

- the selected non-oracle H1 or H2 signal creates a measurable distribution of
  positive usable slack for the exact storage-to-Host segment;
- R2 completes attributable work before request arrival often enough to change
  the measured critical path, rather than merely duplicating R1;
- the joint resumed/foreground SLO and cost accounting improve beyond observed
  measurement noise under the same executor and budget;
- stale, cancelled, duplicate, partial, and failed transfers preserve lifecycle
  correctness and cleanup invariants;
- the benefit and losing boundary are reproducible from raw artifacts.

No arbitrary percentage of slack, latency improvement, or oracle agreement is a
PASS threshold. The margin must be tied to measured noise and the declared SLO.

### DEFER

Defer implementation when positive slack exists but evidence is too sparse,
only an unusual deployment hint can provide it, the benefit is confined to an
unregistered regime, or the mechanism needs a separate storage/allocator
contract. Record the result and leave G0-G4 unchanged.

### REJECT

Reject the mechanism for the current project when every reachable non-oracle
hint has no usable slack for the exact segment, H3 is the only effective signal,
R2 is indistinguishable from or worse than R1 after costs, or safety/cleanup
cannot be owned at the selected seam. A REJECT is a valid engineering result;
it does not reject checked demotion or its measured boundary.

## 8. Deletion Test

Before any future implementation is accepted, perform a removal/bypass check:

1. remove this mechanism's code, flags, and traces;
2. run the G0-G4 mainline tests and the stock reactive baseline;
3. verify that checked demotion, resume/recompute fallback, DecisionTrace, and
   joint-SLO evaluation still have the same ownership and meaning;
4. verify that no mainline title, state machine, success condition, or resume
   claim requires proactive prefetch.

If deletion changes the unconditional mainline contract, the projects have been
coupled and prefetch admission must be rejected or redesigned. This document
must remain a future review artifact, never a hidden G6 or an implementation
authorization.
