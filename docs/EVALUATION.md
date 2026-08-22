# Evaluation Contract

> Status: `roadmap`
>
> Project claim state: `roadmap`
>
> This document defines acceptable evidence. It contains no current performance
> result. Experimental evidence: none.

## 1. Evaluation Objective

Determine whether checked session demotion is mechanically real, lifecycle-safe,
and measurably useful beyond the strongest simple upstream behavior on one
declared single-node testbed.

## 2. Pre-Registered Hypotheses

### H0 — Safe target resolution exists

The fixed source exposes enough information to resolve exact legal targets
without replacing the cache backend or duplicating physical ownership.

### H1 — Physical reclamation is attributable

Forced checked demotion produces physical device-block release and
allocator-visible headroom, not only a logical session-state change.

### H2 — Lifecycle races are fenced

Resume, cancellation, failure, and stale completion preserve output semantics
and return all declared resources to baseline.

### H3 — Immediate reclamation adds value

In at least one reachable pressure regime, checked reclamation creates useful
headroom earlier than the `write_through` same-Publication reference with the
G0-proven target session-priority release and stock eviction.

### H4 — The mechanism has a measurable boundary

Positive, losing, and irrelevant regimes can be explained using physical and
request-level measurements rather than post-hoc labels.

### H5 — Dynamic selection is conditionally useful

Only after H0-H4: at least two reachable regimes prefer different actions and a
small selector can outperform a tuned static/action-only baseline beyond noise.

## 3. Required Baselines

1. stock SGLang HiCache with no ToolGap lifecycle trigger;
2. stock session-radix behavior where applicable;
3. `write_through` Publication plus a source-proven target session-priority
   release that preserves the declared pause/resume lifecycle, with stock
   eviction;
4. forced checked reclamation over the same `write_through` committed Host
   copy and Publication history;
5. for any end-to-end optimization claim on the declared single-node testbed,
   tuned stock `write_through_selective` and `write_back` under the same
   workload and joint SLO;
6. forced restore and forced recompute when each is a fair, attributable path;
7. no-pressure and already-timely-stock controls where demotion should lose or
   be irrelevant;
8. for policy studies, B0/B1/B2 and an optional local action oracle.

G1 and G2 use `write_through` as the qualification/reference mode while proving
mechanism and correctness; they do not perform the release-only versus checked-
reclamation causal performance comparison. That comparison begins with the
first G3 run: both arms share `write_through` Publication, the committed Host
copy, workload, instrumentation, and stock eviction. G0 must prove that the
release operation is not terminal session close under another name.
`write_through` is not presumed end-to-end-optimal on the declared testbed.

An end-to-end optimization claim on the declared single-node testbed adds the
second comparison against the best measured tuned stock policy from
`write_through_selective` and `write_back`, with identical source/build, model,
capacity, workload, arrival process, SLO, and observation rules. If the
candidate wins the same-Publication comparison but not this stock-policy
challenge, report only a mechanism result. This stronger testbed comparison
does not establish production readiness. Tool-gap-triggered on-demand
Publication is excluded unless an independent accepted contract is opened
after eager Publication is measured as the decisive cost.

All policy baselines must share the same physical executor and legal action set
when policy is the independent variable. A local action oracle may choose the
best observed QoS-feasible action at one state, but it is a local regret
reference, not a global sequential-policy upper bound.

## 4. Primary Metric

Report maximum sustainable arrival rate `lambda` subject to all declared
constraints:

```text
resumed_TTFT_p95 <= S_resume
foreground_ITL_p95 <= S_itl
success_rate >= S_success
correctness and cleanup invariants pass
```

Thresholds are fixed before the comparison run. A result that improves resumed
TTFT while violating foreground ITL is not a win.

## 5. Causal Metrics

### Publication

- Host-write policy and Publication trigger;
- HBM-to-Host D2H submission, completion, and Host commit timing;
- committed Host bytes and Host occupancy before the tool gap.

### Checked reclamation

- requested, eligible, scheduled, and completed bytes;
- allocator free pages before and after completion;
- release-only versus checked-reclamation action identity;
- time from demotion admission to allocator-visible capacity;
- device/Host residency and stock eviction activity;
- final-check, release, free-drain, queue, and completion timing.

Checked reclamation reuses the committed Host copy. Do not attribute the
earlier Publication D2H to the checked-reclamation action or assume that the
existing demote performs another D2H.

### Recovery

- Host-to-HBM restore queue, transfer, and completion timing;
- recompute prefill and fallback timing;
- restored or recomputed bytes and first-token dependency.

### Request-level effect

- resumed queue wait, Host restore, recompute prefill, and first token;
- foreground queue wait and ITL/TPOT p50, p95, and p99;
- completed sessions and success rate;
- repeated prefill tokens;
- fallback and failure denominators.

### Workload reality

- unique resident device pages divided by device pool pages;
- allocator headroom and allocation failures;
- unique versus shared prefix bytes;
- current active and paused session counts;
- lifecycle-gap definition and censoring;
- blocking and parallel tool groups.

Offered context tokens alone are not a measure of realized GPU pressure.

Every performance comparison must close action -> mediator -> request endpoint
on the same workload. memcpy bandwidth, release speed, or another
microbenchmark cannot independently establish a win. A substrate patch that
affects both arms must be shared by both and cannot count as a ToolGap
differential.

Pressure must be evidenced by realized KV-pool occupancy, allocator headroom,
and stock-eviction activity. A reduced pool is admissible for controlled
pressure, but reduced capacity or offered tokens alone do not establish that
the regime is reachable; any claim must state its workload reachability basis.

## 6. Initial Sentinel Scenarios

Run a small counterexample set before any broad sweep:

Gate ownership remains strict: G1 may run only its quiescent positive and static
eligibility controls; resume, cancellation, newer-pause, late-completion,
failure, partial-completion, and full cleanup interleavings belong to G2. G3 and
G4 own the performance losing and boundary controls below.

1. private tail, low pressure — demotion should be irrelevant or lose;
2. private tail, high pressure — earliest plausible positive case;
3. shared prefix with remaining protected non-target coverage — reject or clip;
4. running request lock — defer or reject;
5. publication pending, followed by resume — no uncommitted recovery assumption;
6. cancel or newer pause followed by late completion — state fenced and cleanup
   complete;
7. Host-copy failure — safe attributable fallback;
8. release-priority-only stock eviction already timely — active reclamation
   should show no additional value;
9. restore slower than recompute in a small-KV regime — report the losing path
   without treating it as a project-wide stop.

Only measured sentinel results may justify a larger parameter sweep.

## 7. Workload Sources

### Controlled harness

The controlled harness establishes internal validity and exact concurrency,
pressure, prefix-sharing, gap, and fault conditions.

The first G1 mechanism slice is deliberately narrower than the later lifecycle
matrix: one current session generation, one operation, a committed Host copy,
a private target tail, no concurrent resume/cancel/new pause, no tree mutation,
and no conflicting pending work. The harness waits for the physical terminal
and verifies that the limited resources owned by this slice are released before
leaving it. This restriction supports a real mechanism observation; it does
not establish the full G2 lifecycle or cleanup contract.

A synthetic or parameterized gap distribution must record its provenance and
calibration boundary. It can establish controlled internal validity, but it
does not by itself prove that a positive pressure/gap regime is reachable in an
agent workload. A G3 positive sentinel therefore needs an explicit reachability
basis, such as measured tool latency, a declared public-trace observation, or a
separately justified deployment envelope. It does not require a hazard model or
TraceLab-driven replay.

### Public agent traces

Public traces may calibrate client-side tool sequences, parallelism, censoring,
and gap distributions. They cannot establish server-side KV residency,
allocator pressure, transfer cost, or admission time. Client and server traces
must be joined through explicit identifiers and clock definitions.

### 7.1 Client-side gap event schema

Each gap event should expose, or explicitly mark unavailable:

| Field | Meaning |
|---|---|
| trace_id | workload/run identifier shared with server records |
| session_id | logical session identifier |
| session_generation | upstream session incarnation, when available |
| gap_id | unique pause/tool-gap identifier |
| gap_start_time | timestamp plus source clock domain |
| next_request_admit_time | corresponding next-request ingress/admission time |
| censor_time and censor_reason | observation end when return is not observed |
| terminal_outcome | cancellation, timeout, termination, or other competing outcome |
| tool_group | tool class used for conditioning |
| blocking_group | group whose completion gates the next request |
| parallel_group | concurrent group; members are not summed as a serial gap |
| workflow_prefix | bounded observable trajectory prefix, if used by B2 |
| prefix_tokens / append_tokens | client workload shape |
| returned | whether the next request was observed |

Source timestamps must carry their clock domain and uncertainty. A trace's wall
time must not silently be treated as engine admission time.

### 7.2 Server-side lifecycle and residency schema

The server trace should expose:

| Field | Meaning |
|---|---|
| trace_id, session_id, session_generation, gap_id | join identity |
| operation_id, resume_id | lifecycle operation identity |
| event_time and clock domain | server monotonic event time |
| requested, eligible, scheduled, completed bytes | action accounting |
| unique_reclaimable_bytes / shared_bytes | target composition |
| device/Host residency | mainline materialization at each event; storage is recorded only in a separately admitted future experiment |
| lock_ref, host_lock_ref, session_ref, session_ids | version-matched eligibility evidence |
| allocator_headroom / free_pages | physical capacity observation |
| pressure, queue_depth, bandwidth | realized load and contention |
| restore, recompute, first_token timings | recovery and request effects |
| action, outcome, reason_code | requested versus observed result |
| cleanup_ledger_delta | terminal resource accounting |

The exact fields depend on the fixed source seam. Missing fields are an
unresolved evidence boundary, not permission to infer residency or ownership.
In particular, session_ids is a frontier marker rather than an arbitrary-node
coverage set, and session_ref is an eviction-priority signal rather than a hard
device pin. host_lock_ref must be interpreted from the fixed source rather than
treated as a universal device-reclaim blocker. No field alone authorizes
reclamation.

### 7.3 Join, clocks, and evidence boundary

Join on the explicit tuple
trace_id, session_id, session_generation, and gap_id; where present, also join
operation_id and resume_id. A server may emit many events for one client gap,
so the one-to-many relationship and event order must be preserved.

Use a declared monotonic clock in each process. If client and server clocks are
separate, record synchronization/offset calibration and its uncertainty. Prefer
an engine ingress event emitted by the server over reconstructing admission time
from a client log.

The joined trace can establish client-side gap/return behavior from client
events and server-side physical residency, allocator, transfer, and cleanup
from server events. Causal alignment is valid only where the join key, clock
mapping, and event ordering are evidenced. A client trace alone cannot prove
GPU residency, exact reclaimable bytes, eviction cause, transfer bandwidth, or
restore cost; a server trace alone cannot prove the workload's tool-return
distribution.

### 7.4 Right censoring, terminal outcomes, and tool groups

A gap is right-censored when observation ends while the session remains at risk
of returning and the eventual return time is unknown. Retain `censor_time` and
`censor_reason`; do not convert the event to a short gap or silently discard it.
Cancellation, timeout, explicit session termination, or process failure may be
terminal outcomes or competing risks rather than non-informative censoring.
Record them separately and justify whether a particular analysis treats them as
events, competing outcomes, or censoring. Hazard estimates must report the risk
set, terminal-outcome counts, censoring rate, and the censoring assumption.

For blocking tools, the next request is gated by the blocking group's
completion. For parallel tools, the group return follows its declared join rule
(such as all, any, quorum, or a framework-specific aggregation). Do not sum
parallel member wall times or label each member as a serial agent gap. The
harness must log group membership, start/end events, join rule, and the event
that admitted the next request.

Cancellation and timeout are lifecycle outcomes even when a specific estimator
also treats them as censored observations under a declared assumption. A server
operation may complete after client observation ends or after a terminal client
outcome; both traces must retain that distinction and test stale-completion
cleanup.

### 7.5 TraceLab boundary

[TraceLab](https://github.com/uw-syfi/TraceLab) may calibrate client-side
agent/tool behavior, tool-group structure, token-shape features, and censoring
assumptions. It is not a source of this project's server-side residency,
allocator pressure, transfer cost, or admission-time truth. It must be joined
with a controlled server harness or treated as client-only calibration.

The manifest must record the public trace release, fields, preprocessing, and
timestamp semantics. If a field is absent or anonymized, mark it unavailable
rather than manufacturing a server measurement.

## 8. Capacity-Derived Experiment Program

Do not begin with an arbitrary context-by-concurrency grid. Derive valid
sentinels and any later sweep from measured engine capacity.

Steps 1-4 are the minimum calibration required before G3 can register a
reachable low-pressure control and near-capacity candidate sentinel. Steps 5-6
belong to G4 boundary expansion and are not permission to pre-build a broad
grid before the G3 comparison.

1. Freeze model, revision, dtype, page size, context limit, cache flags, and
   memory fraction on the fixed source pin.
2. Measure actual device KV-pool bytes and bytes-per-token under that
   configuration. Record weight, activation, allocator, and non-KV
   reservations.
3. Derive the capacity anchor pool_tokens from measured pool bytes and measured
   bytes-per-token; do not treat it as a pressure result.
4. Run a harness that records realized unique resident device bytes, shared
   bytes, allocator headroom, allocation failures, and stock-eviction response.
   G3 requires a low-pressure control and a near-capacity candidate sentinel;
   an oversubscribed family is added in G4 only when it answers a measured
   boundary question. All families must fit the model context limit.
5. Select sentinels from observed pressure and recovery distributions: private
   tails and shared prefixes, short and long observed gaps, and relevant
   Host-tier transfer/recovery conditions. Another storage medium requires its
   own admitted experiment. Add a point only when it is a measured reachable
   combination.
6. Expand the sweep only after sentinel data identifies an axis that changes
   the causal result. Derive each new context/concurrency point from the same
   measured pool and record why it was added.

The number of points is an output of this program, not a fixed promise such as
36. Report realized pressure (unique resident bytes divided by device-pool
bytes), not merely offered tokens or a preselected Cartesian count. Preserve
low-pressure, small-KV, fast-stock, expensive-recovery, and shared-prefix-heavy
losing regions.

Workload-point count and statistical repetition are different decisions. A new
point is added only for a measured causal reason; the repetition count, pairing,
aggregation, and interval method for that point are frozen in its SPEC before
the primary result is observed.

## 9. Statistical Protocol

- freeze environment, model revision, tokenizer/template, engine commit, flags,
  workload seeds, arrival process, and warm-up policy;
- use paired comparisons where the same arrival trace can drive both paths;
- declare repetition count and aggregation before reading the primary result;
- report raw samples, median, p95/p99 where relevant, confidence interval, and
  failure count;
- require the claimed effect to exceed measurement noise and run-to-run drift;
- separate calibration/tuning traces from final evaluation traces.

Arbitrary fixed percentages for improvement, slack, or oracle proximity are not
Gate thresholds until tied to observed noise, a declared SLO, or a practical
capacity margin.

## 10. Hindsight Reference and Action Regret

An optional empirical one-step action oracle may replay the same local decision
with the same legal action set, QoS constraints, and physical executor, then
select the best observed feasible action. It must not use a future request to
change the legal set or bypass lifecycle checks.

For each decision state, local action regret is the observed cost or joint-SLO
loss of the selected action minus the best observed feasible action in that
same state/action set. Report the regret distribution, infeasible-action
reasons, selected action, observed outcome, and fallback reason on held-out
traces or sessions. Compare B0/B1/B2 and O* with separate calibration/tuning
and evaluation data.

The oracle is a local regret reference, not a global sequential-policy upper
bound: actions change later cache state, pressure, arrivals, and available
actions.

## 11. Experiment Artifact Contract

Each Gate experiment directory contains:

```text
SPEC.md          frozen question, hypothesis, protocol, and branches
RESULTS.md       actual execution, raw links, analysis, and decision
manifest.json    source, model, hardware, flags, workload, and hashes
commands/        exact reproduction commands
artifacts/       raw traces, logs, plots, and machine-readable summaries
```

The result report must distinguish:

- implemented behavior: `shipped`;
- real measured behavior: `experimentally validated`;
- trace/model-only evidence: `simulated`;
- remaining work: `roadmap`.

## 12. Negative-Result Rules

- Do not drop a workload because it makes demotion lose.
- Do not increase context size after observing a loss unless the new workload is
  registered as a separate question.
- Do not call slower restore a project-wide failure if early reclaim plus later
  recompute could still improve the joint SLO; measure the full chain.
- Do not convert an inconclusive result into a pass by weakening a threshold
  after the run.
