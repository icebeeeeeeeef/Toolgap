# Experiment and Evidence SOP

> Status: `roadmap`
>
> This is a cross-cutting evidence contract for the existing G0-G5 sequence. It
> is not a new Gate, an implementation plan, or a current result. Gate order and
> exit decisions remain owned by [ROADMAP.md](../ROADMAP.md).

## 1. Authority order

Keep two kinds of authority separate:

1. **What happened:** the fixed source/configuration named by a run manifest and
   its retained raw artifacts are the factual record. A summary, review, or
   decision cannot turn a missing artifact into an observation.
2. **What the project is allowed to ask or claim:** use the repository contract
   in this order:

   `PROJECT.md` → `ARCHITECTURE.md` → `DEMOTION_CONTRACT.md` →
   `ROADMAP.md` → `EVALUATION.md` + this SOP → `DECISIONS.md` →
   per-Gate experiment artifacts.

The documents have deliberately narrow ownership:

| Owner | Authority | Must not do |
|---|---|---|
| `PROJECT.md` | problem, causal chain, ownership, exclusions, and scope | inherit a result from a lower document |
| `ARCHITECTURE.md` | runtime boundaries and upstream/owned interfaces | state performance conclusions |
| `DEMOTION_CONTRACT.md` | safety, lifecycle, recovery, and cleanup invariants | authorize a policy or relax an invariant |
| `ROADMAP.md` | G0-G5 order and PASS/RESHAPE/STOP branches | duplicate experiment recipes |
| `EVALUATION.md` | baselines, workload, metrics, statistics, and evidence requirements | narrate actual results |
| this SOP | common provenance, preregistration, failure accounting, and claim-promotion rules | add a Gate or redefine a project metric |
| `DECISIONS.md` | rationale and decision history | act as runtime evidence or claim state |
| `experiments/<gate>/` | frozen `SPEC.md`, `RESULTS.md`, manifest, commands, and artifacts for one Gate | override a canonical contract |
| `reviews/` | historical input | serve as a current technical fact source |

If scope changes, change `PROJECT.md` first and record the rationale in
`DECISIONS.md`; then update the affected roadmap, evaluation contract, and new
experiment specification. A lower document cannot silently widen an earlier
boundary.

## 2. Preregister before execution

Every executable Gate has a frozen `SPEC.md` before its first treatment,
comparison, or evaluation result is observed. The SPEC is checksum-linked from
the run manifest. It must freeze, at minimum:

- the decision question, hypothesis, claim ceiling, and required PASS/RESHAPE/STOP
  evidence;
- fixed source, configuration, model/revision, and environment assumptions;
- actions and baselines, including controls where the mechanism is expected to
  lose or be irrelevant;
- workload source, preprocessing, seed/hash, arrival process, pressure inputs,
  tuning/evaluation split, and unit of replication;
- primary, causal, and guardrail metrics; SLOs; materiality/noise rules; and
  aggregation and interval methods;
- repetition count, pairing and order, warm-up/measurement/drain windows;
- failure, missing-terminal, invalid-attempt, right-censoring, and competing-
  outcome treatment;
- exact commands and the raw artifacts required to make the result reviewable.

Calibration/tuning data must be separate from evaluation data. A change to the
SPEC, workload, threshold, action set, order, or analysis rule after execution
creates a new SPEC revision and new run identity; it never overwrites the old
artifact or silently retries a losing result.

The existing Gates use the same contract with different evidence questions:

| Gate | SPEC must make observable |
|---|---|
| G0 | fixed-source capability, exact legal target mapping, counterexamples, extension boundary, and removal test |
| G1 | forced action, physical completion, allocator-visible effect, rejection cases, and default-path bypass |
| G2 | operation identity, stale-completion fencing, failure injection, fallback, output equivalence, and quiescent cleanup |
| G3 | the strongest simple baseline, paired action paths, joint SLO/guardrails, and losing controls |
| G4 | capacity-derived reachable regimes, sentinel selection, causal decomposition, and positive/losing/irrelevant regions |
| G5 | legal action set, tuned static/action-only baseline, separate tuning/evaluation traces, decision margin, and hot-path/tail overhead |

This table records evidence requirements only; it does not change the Gate
questions or add a sub-gate.

## 3. Minimum run manifest

Each attempt has one immutable `manifest.json` (or an explicitly equivalent
machine-readable manifest) with an artifact index. At minimum it records:

The manifest is stage-aware, not a ritual checklist. Every listed field must
either have a value or be written as `N/A` with a reason; a blank or silently
omitted field is invalid. Runtime-specific fields (device/runtime identity,
process readbacks, terminal events, and runtime artifacts) become required only
for runtime attempts. For source-only or design-only attempts, mark them
`N/A: source-only` (or the precise reason) and retain the source/configuration
identity that was actually inspected.

| Area | Required fields |
|---|---|
| Identity | experiment/cohort ID, Gate, SPEC revision and checksum, run/attempt/repeat ID, arm, and run status |
| Source | engine commit, local patch/worktree identity, dependency and model/tokenizer revisions, resolved flags, and hashes where available |
| Environment | testbed, host/device identity, runtime/driver versions, process/role mapping, and relevant capacity/configuration |
| Workload | source/release, preprocessing, seed and content hash, arrival process, session/gap shape, pressure inputs, and tuning/evaluation split |
| Protocol | baseline/action, assignment, order, warm-up/measurement/drain windows, clock domains, repetition unit, SLOs, thresholds, and denominator rules |
| Metrics | primary/causal/guardrail names, required terminal events, censoring and failure classification, and analysis revision |
| Execution | exact command references, start/end and exit information, environment readbacks, and raw artifact paths with size/checksum |
| Outcome | executed/blocked/inconclusive status, Gate decision only when that Gate actually ran, and the claim state of each promoted claim |

Do not infer a Gate outcome from a manifest that only proves setup. A blocked
admission is a retained blocker, not a failed mechanism run. Keep secrets and
unnecessary user content out of manifests and raw artifacts; hash sensitive
inputs when identity, not content, is needed.

## 4. Raw evidence and derived report

Use the existing per-Gate artifact contract:

```text
SPEC.md          frozen question, protocol, branches, and claim ceiling
RESULTS.md       actual execution, analysis, evidence links, and decision
manifest.json    identity, environment, protocol, outcome, and checksums
commands/        exact reproduction commands
artifacts/       raw logs, traces, readbacks, snapshots, and machine summaries
```

Raw evidence is immutable after an attempt is sealed: retain stdout/stderr,
traces, request/operation records, allocator and cleanup observations, command
outputs, environment readbacks, and failed or incomplete attempts. The manifest
index and checksums make the bundle reviewable.

`RESULTS.md` is a derived report. It may contain joins, aggregates, plots,
intervals, exclusions, failure counts, and a Gate decision, but every material
number must point to raw artifacts and the analysis revision that produced it.
Analysis may not delete failed rows, invent missing terminals, replace an
invalid attempt, mutate the SPEC, or write a more favorable Gate outcome. A
regenerated report must leave the raw bundle unchanged.

Source inspection, unit tests, mocks, and a completed SPEC can prove a local
contract or implementation fact; they do not prove a real engine result unless
the relevant runtime artifact is retained. `make check` or document review
checks repository consistency only; it is not a Gate result.

## 5. Failure denominators and censoring

Every rate, ratio, quantile, and success claim names its denominator in the
SPEC and reports numerator, denominator, failures, missing data, and exclusions.
Use the following default discipline unless the SPEC declares a more precise
project-specific definition:

| Measurement | Denominator discipline |
|---|---|
| success/SLO | all admitted or started attempts selected by the SPEC; request errors, timeouts, and failed fallbacks count against the declared success objective |
| latency quantiles | the declared population (for example, all terminal requests or successful terminals); report the full attempt and failure counts alongside the quantile, never silently filter failures |
| physical mechanism | keep requested, eligible, scheduled, and completed bytes distinct; a completion ratio cannot use requested bytes when eligibility is the question |
| lifecycle/hazard | use the declared at-risk set; report events, right-censored observations, cancellation/timeouts, and other competing terminal outcomes separately |
| ratios/effects | require a positive, predeclared denominator; a non-positive or missing denominator is undefined/inconclusive, not zero |

Classify failures before interpreting a result:

- **before execution:** environment or admission blocked; no treatment outcome
  is counted, and the Gate remains unresolved;
- **after execution starts:** request, mechanism, cleanup, or fallback failures
  count in the declared attempt denominator;
- **right-censored:** observation ended before the event was known; retain censor
  time/reason and do not convert it into a short success;
- **competing terminal:** cancellation, timeout, explicit termination, or process
  failure is reported separately and handled according to the preregistered
  analysis;
- **missing evidence:** missing terminal/core join/cleanup evidence invalidates
  the relevant claim or attempt; it is not evidence of success.

The statistical unit is the unit frozen in the SPEC (usually a paired run or
session), not the number of correlated requests emitted inside it. Invalid
attempts remain in the artifact index and cannot be replaced after the result is
known unless that replacement rule was preregistered.

## 6. Gate decisions and STOP discipline

Apply the existing decision vocabulary in `ROADMAP.md`:

- `PASS` unlocks only the next work that the roadmap allows;
- `RESHAPE` narrows or changes the supported mechanism, preserving the prior
  evidence and requiring a new SPEC before rerun;
- `STOP` ends the affected branch, records the exact failing condition and the
  last supported claim, and preserves the raw and derived artifacts;
- G5's `STOP POLICY` retains G0-G4 mechanism/boundary evidence and blocks a
  dynamic selector.

An `inconclusive` attempt or missing required artifact is not a PASS and does
not become a null result through more favorable wording. It remains unresolved
until an owner-approved, checksum-linked protocol revision addresses the missing
evidence. No later mechanism, policy, or broader workload can compensate for a
failed earlier correctness or ownership condition. This SOP adds no Gate and
does not alter the separate future-prefetch review.

## 7. Preserve negative results

Losing and irrelevant controls are required evidence, not noise. Keep the raw
and derived record when:

- the mechanism loses under low pressure, shared-prefix, already-sufficient
  stock, expensive-recovery, or other preregistered controls;
- a baseline is already timely or no measurable boundary is reached;
- a failure injector or terminal observation is unavailable;
- calibration and evaluation disagree, or the result is right-censored;
- G3/G4 show a narrow or negative boundary, or G5 stops policy admission.

Do not drop a workload because it makes demotion lose, increase pressure after
observing a loss without registering a new question, weaken a threshold after
the run, or turn a missing result into a pass. Superseded SPECs, results, and
decisions remain linked historical artifacts; they are never overwritten or
silently reused as current evidence.

## 8. Claim promotion

Claim state is orthogonal to Gate decision and decision-log status. Use exactly
the four states defined by the repository:

| State | Minimum meaning | Claim ceiling |
|---|---|---|
| `roadmap` | planned, proposed, source/design discussion, or unexecuted contract | no implementation, runtime, or performance claim |
| `shipped` | code exists and has been exercised in the stated system | implementation exists in that stated system; no measured benefit or broader generalization |
| `experimentally validated` | a declared environment/workload produced a retained, reproducible runtime result with the required baseline, guardrails, denominators, and raw evidence | only the measured scenario and mechanism claim supported by that artifact |
| `simulated` | trace, replay, model, or simulator result with its calibration boundary declared | no real-engine, lifecycle, or end-to-end performance claim |

Promotion rules:

1. Documentation completeness, an accepted decision, a source audit, a mock, a
   unit test, or an API shape never promotes a runtime claim by itself.
2. Promote to `shipped` only after the implementation is present and exercised;
   identify the exact source/configuration and test or run artifact.
3. Promote to `experimentally validated` only for the specific claim whose
   frozen SPEC, manifest, raw evidence, derived analysis, denominator accounting,
   baseline, and Gate decision all support it. A Gate PASS does not promote
   unrelated claims.
4. Keep replay/model results `simulated`, even when they agree with a runtime
   result; they do not replace the runtime causal comparison.
5. Preserve the narrowest supported environment, workload, failure coverage,
   and boundary in the wording. Do not convert one-node evidence into a general
   engine, production, or policy claim.

## 9. Review checklist

Before publishing a Gate result, a reviewer should be able to answer “yes” to
all of the following:

- Was the SPEC frozen and checksum-linked before the relevant result?
- Can the manifest reproduce the exact source, configuration, workload, and
  environment?
- Are raw artifacts, failed attempts, and checksums retained?
- Are derived numbers reproducible from raw evidence without hidden filtering?
- Are denominators, failure classes, censoring, and invalid attempts explicit?
- Are the strongest baseline and losing controls present?
- Does the recorded decision match the existing roadmap branch and claim ceiling?
- Does each promoted claim use the narrowest valid claim state?
