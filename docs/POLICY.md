# Conditional Policy Design

> Status: `roadmap`
>
> Project claim state: `roadmap`
>
> Admission: blocked by Gate G5. Implementation: not started. Experimental
> evidence: none.

This document records the strategy design that can be evaluated after the
mechanism and its boundary are known. It is not implementation authorization,
and it does not turn a proposed policy into a project claim. G0-G4 must first
establish a checked executor, lifecycle correctness, a fair strongest-simple
baseline, and reachable regimes with a measured boundary.

## 1. Policy Question

If multiple reachable regimes prefer different legal actions, can a small,
transparent selector reduce out-of-sample local action regret and improve the
joint resumed/foreground SLO over a tuned static or action-only baseline,
without unacceptable hot-path or tail overhead?

The selector is optional. A useful mechanism with no useful selector remains a
valid G0-G4 result. The policy layer must never be used to compensate for an
unproven target resolver, unsafe physical operation, or missing cleanup.

## 2. Four-Layer Architecture

The layers are ordered by authority:

~~~text
Correctness / execution layer
  -> resolves and executes only legal actions
Prediction layer
  -> supplies conditional information about return timing or demand
Cost layer
  -> measures transfer, recovery, recompute, and interference costs
Decision layer
  -> chooses among the remaining actions under declared constraints
~~~

### 2.1 Correctness and execution

The executor and its safety filters produce the legal action set. The policy
may rank or decline those actions; it cannot authorize an action that the
contract rejects. The complete eligibility, shared-prefix, lock, generation,
completion, fallback, and cleanup rules are owned by
[DEMOTION_CONTRACT.md](DEMOTION_CONTRACT.md). They are deliberately not
duplicated here.

The policy must consume an execution result that identifies requested,
eligible, scheduled, completed, clipped, deferred, rejected, and cleaned-up
work. A score is never a safety proof.

### 2.2 Prediction

Prediction is optional information about when a session or tool group returns.
The first prediction-bearing candidate is an interpretable discrete hazard
table, not a learned workflow controller. It may be removed without changing
the executor. B0 remains the first policy baseline and contains no return-time
predictor.

### 2.3 Cost

Cost is measured from the declared engine and workload, including transfer
queueing, effective bandwidth, Host/device contention, restore, recompute,
foreground interference, allocator headroom, and cleanup overhead. Costs are
reported with units and uncertainty; they are not guessed from a symbolic
rent or a fixed bandwidth constant.

### 2.4 Decision

The decision layer uses a lexicographic order: lifecycle safety, resource
feasibility, foreground-QoS feasibility, then the returning request's measured
or predicted recovery-completion cost. QoS is a decision constraint and an
evaluation objective, not a correctness invariant. Violating a QoS budget can
make a policy result fail; it cannot make an otherwise unsafe demotion legal.
The first selector must not sum recovery, interference, and collateral effects
into one weighted score unless a later review establishes a common unit and a
measured need that the lexicographic rule cannot express.

## 3. Admission and Information Ladder

All levels use the same workload split, executor, legal action resolver, and
joint-SLO definition:

~~~text
B0: runtime pressure and current KV state only
  -> strongest information-free/action-only baseline
B1: B0 plus tool-group return hazard
B2: B1 plus bounded current-trajectory prefix features
O*: offline local action oracle over the same executor, legal actions, and QoS
    constraints
~~~

The levels are nested. The oracle is a local one-step action reference, not a
global sequential-policy upper bound: an action changes later cache state,
pressure, arrivals, and available actions.

The measured comparison is out-of-sample action regret plus joint-SLO result,
not gap-prediction RMSE. For a decision state `s`, regret is the observed cost
or SLO loss of the selected action relative to the best QoS-feasible action in
the same local action set and executor. The trace must retain infeasible
actions and their reasons so that an oracle cannot win by bypassing safety.

Use separate calibration/tuning and evaluation traces. A feature is admitted
only when its evaluation-set action regret and joint-SLO effect exceed observed
measurement/model uncertainty and the added runtime cost is attributable.

### Decision rules

- If B0 is sufficient, stop at B0 and do not deploy a hazard table.
- If B1 does not improve out-of-sample action regret and joint-SLO outcomes,
  remove the hazard table from the runtime.
- If B2 adds no measured value, do not build a workflow-prefix predictor.
- A large `O* - B2` gap records an information gap; it does not authorize an
  unbounded model or a new lifecycle mechanism.
- If no reachable regimes prefer different actions, retire dynamic policy and
  keep the mechanism/action-only evidence.

## 4. Discrete Return Hazard

Return observations are right-censored only when observation ends while the
session is still at risk of returning and the eventual return time is unknown.
A trace boundary can have that meaning. Cancellation, timeout, or session
termination may instead be terminal outcomes or competing risks and may be
informative; they must not be silently treated as non-informative censoring.
Record the outcome and justify the selected statistical treatment rather than
converting it to a short or missing gap.

For a tool group `g`, elapsed waiting bucket `t`, and observable feature vector
`x`, the prediction consumed by a policy is:

~~~text
P(return <= h | already waited t, tool_group = g, features = x)
~~~

`h` is a concrete horizon such as the measured storage/Host transfer,
Host/device restore, or recompute interval under the current load. It is not a
generic percentile and is not a denominator in a value-density score.

The v1 upper bound is a per-tool-group, elapsed-time-bucket discrete hazard or
survival table with explicit event, competing-outcome, and right-censoring
treatment. A Kaplan–Meier-style risk set is allowed only when its censoring
assumption is stated and defended for the selected data. The design must state
bucket boundaries, minimum-support handling, terminal outcomes, censoring
rules, update cadence, and cold-start fallback. Do not introduce a parameterized
survival model before the table's incremental value is established.

The split is by trace/session, not by randomly mixing events from the same
session across training and evaluation. The evaluation report must disclose
tool-group support, censoring rate, horizon calibration, and cold-start
coverage. Client-side traces calibrate return behavior; server-side traces
calibrate the costs and effects consumed by a decision.

## 5. Candidate Actions and Ordering

The first policy may choose only among actions with independent G0-G4 evidence,
for example retain, session-priority release with stock eviction, checked
reclamation, or recompute/restore fallback where the executor supports them.
Prefetch is a separate future admission in
[future/PREFETCH_ADMISSION.md](future/PREFETCH_ADMISSION.md), not a hidden
policy action.

The decision sequence is:

1. ask the correctness/execution layer for the current legal action set;
2. discard actions that violate declared resource or foreground-QoS feasibility;
3. among the remaining actions, compare the returning request's measured,
   unit-bearing recovery-completion cost without adding the preceding
   constraints into that cost;
4. choose a deterministic action when the predicted advantage exceeds the
   declared uncertainty margin;
5. otherwise use the stock/action-only fallback and record the reason.

The expression
`expected recovery/interference/collateral penalty ÷ unique reclaimable bytes`
is a possible experiment for ordering already legal candidates, not an
accepted algorithm or project commitment. In particular, `penalty/bytes` does
not authorize reclamation, trade correctness for QoS, or replace the shared
prefix and leaf checks. A composite weighted score is not admitted merely to
combine incomparable constraints.

Block-level ranking is not required initially. Walk legal targets in a
deterministic auditable order until the byte budget is reached; add ranking only
after a measured counterexample shows that target choice changes outcomes.

## 6. Required Evidence

Policy evaluation extends [EVALUATION.md](EVALUATION.md) with:

- identical executor and legal-action semantics for B0/B1/B2/O*;
- separate tuning and out-of-sample evaluation traces;
- action-level decisions, feasible-set membership, predicted uncertainty,
  selected action, observed outcome, and fallback reason;
- local action regret, joint resumed/foreground SLO, and policy hot-path/tail
  overhead;
- hazard calibration, right-censored counts, cold-start usage, and feature
  provenance;
- positive, losing, and no-information regimes.

Every policy result remains one of the repository claim states. A table or
selector in a document is `roadmap`; a running implementation requires
`shipped`; measured behavior requires `experimentally validated`; trace-only
replay requires `simulated` with its boundary.

## 7. Stop, Narrow, and Fallback Rules

Stop policy work and keep B0 when:

- one action dominates across all reachable registered regimes;
- B0 is within measurement noise of B1/B2/O* on joint SLO and action regret;
- return-time information does not transfer out of sample;
- target choices cannot be attributed to the same executor;
- policy overhead or foreground tail cost erases the measured margin;
- the mechanism's positive boundary disappears under a fair baseline.

Narrow to B1 only when the hazard table adds reproducible value and no
trajectory feature is needed. Narrow to B2 only when the bounded trajectory
features add value beyond B1. If any layer requires a new physical data plane,
workflow scheduler, cross-session future-hit valuation, or prefetch dependency,
stop and open a separate design review instead.

Stopping policy work does not invalidate a safe mechanism, a negative result,
or a measured G0-G4 boundary. It simply records that the simplest transparent
action policy is the final selected policy for the reachable envelope.

## 8. G5 Admission Checklist

G5 may authorize implementation only after:

1. G0-G4 are complete with raw traces and manifests;
2. at least two reachable regimes prefer different legal actions;
3. all policy baselines use the same executor and QoS constraints;
4. the action-regret and joint-SLO effect survives an out-of-sample split;
5. hot-path, tail, memory, and cleanup overhead are within the pre-registered
   envelope;
6. the smallest selector and its fallback are documented before coding.

Until every item is evidenced, this file remains a conditional roadmap design,
not a runtime plan.
