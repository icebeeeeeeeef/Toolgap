# ToolGap Project Selection SOP

> Status: `roadmap`
>
> Project claim state: `roadmap`
>
> Scope: a reusable method for evaluating project direction, engineering
> ownership, evidence quality, and interview defensibility. ToolGap's current
> safe session-demotion/SGLang HiCache work is the application example; this
> document is not its implementation contract or execution plan.

## 1. Authority and boundary

For the current ToolGap instance, the project contract is
[PROJECT.md](../PROJECT.md), runtime boundary is [ARCHITECTURE.md](../ARCHITECTURE.md),
safety contract is [DEMOTION_CONTRACT.md](../DEMOTION_CONTRACT.md), execution
order is [ROADMAP.md](../ROADMAP.md), and evidence rules are
[EVALUATION.md](../EVALUATION.md). Those documents own the current technical
claims. This SOP does not restate their source facts, state machine, causal
chain, or execution gates.

Future mechanisms and dynamic policy must remain separate when applying this
method; see [POLICY.md](../POLICY.md) and
[future/PREFETCH_ADMISSION.md](../future/PREFETCH_ADMISSION.md).

Every material project claim in this document set uses one of four states:
`roadmap`, `shipped`, `experimentally validated`, or `simulated`. A complete
design document remains `roadmap` until the corresponding source, test,
manifest, trace, or measured experiment exists.

## 2. Selection objective

Select a project that produces defensible LLM Serving / AI Infra evidence. The
working model is:

```text
hiring evidence
  = role marginal value
  × owned execution path
  × judgment density
  × evidence/runtime completeness
  × claim honesty
```

Novelty has approximately zero weight in this decision. It may affect prior-art
attribution and the baseline, but it does not compensate for missing ownership,
correctness, measurement, or an honest losing boundary. This is not a scoring
system and must not be converted into fabricated points.

For ToolGap, the target role family is serving runtime, cache lifecycle, and
scheduler-adjacent AI Infra. The project is not evidence of CUDA-kernel,
compiler, NPU, RDMA, multi-node, or production ownership unless separate
artifacts establish those claims.

## 3. Selection tests (not execution gates)

The following Hard Tests A-E are reusable selection tests. They decide whether
a project is worth selecting, narrowing, or stopping; they do not authorize
implementation and they are deliberately not named G0-G5. Once a project is
selected, its execution gates belong to the relevant project roadmap (for
ToolGap, [ROADMAP.md](../ROADMAP.md)). A failed selection test is not repaired
by adding another feature.

### Hard Test A — Role marginal value and real problem

The project must remove a role-relevant engineering uncertainty, name a primary
metric, connect it to a causal proxy, and state a losing condition. “The topic
is important” or “the workload is novel” is motivation, not evidence. For the
ToolGap instance, the role target is serving runtime, cache lifecycle, and
scheduler-adjacent AI Infra; the current contract for that instance remains in
[PROJECT.md](../PROJECT.md).

### Hard Test B — Falsifiable path and feasible scope

The source and runtime audit must identify the smallest path that can answer the
question, its fixed-version boundary, observable state, and a controlled way to
force both a candidate case and a counterexample. The project must distinguish
an upstream capability from a missing candidate-owned contract. If the proposed
answer needs a broad replacement data plane or untestable production context,
narrow or stop it.

### Hard Test C — Ownership and deletion

Candidate ownership must be behaviorally necessary, not only a wrapper,
configuration file, benchmark script, or trace exporter. Name what the
candidate changes or owns, what remains an upstream dependency, and which test
proves the difference. A useful ownership claim may be a runtime mechanism,
failure/lifecycle logic, or a measurement decision, but it must have a causal
effect that can be removed and observed.

The ownership deletion test is mandatory:

1. remove or bypass the candidate-owned behavior and its required state;
2. run the same ordinary, baseline, and recovery controls;
3. verify that the claimed candidate behavior disappears while the dependency
   path still has an interpretable meaning;
4. disable only the candidate instrumentation and verify that behavior does
   not change;
5. delete any generator or policy feature and verify that the core mechanism
   and its tests still have a causal question.

If removal leaves the claimed behavior unchanged, the project is an integration
exercise and must be reshaped. If removal breaks ordinary dependency behavior
(ordinary SGLang behavior in the ToolGap instance), the patch boundary is too
invasive.

### Hard Test D — Strongest simple baseline and judgment density

The project must compare against the strongest simple behavior that shares the
same workload, executor environment, and instrumentation. For the ToolGap
instance this is **Publication to the same committed Host copy plus the
G0-proven target session-priority release, then stock eviction**, as defined by
the canonical project documents; this SOP does not redefine that contract.

The selection record should contain at least:

1. the strongest simple baseline;
2. the candidate action or mechanism;
3. a no-pressure or no-benefit control;
4. a fair alternative such as restore/recompute, when relevant.

The candidate must state what each alternative solves, what it risks, which
measurement distinguishes it, and what result would reverse the choice. A
policy or predictor is not a substitute for an unmeasured mechanism.

### Hard Test E — Evidence completeness and claim honesty

The project must have a reviewable evidence path from implementation or
measurement to the stated outcome. A performance statement requires a declared
environment, workload, raw artifact, repetition protocol, primary metric, and
at least one losing or no-benefit region. A runtime statement requires the
relevant correctness, failure, fallback, and cleanup evidence for that scope.

Use the claim states precisely and independently of selection-test results:

- `roadmap`: design, hypothesis, or planned gate;
- `shipped`: candidate code and tests run in the declared system;
- `experimentally validated`: measured behavior with manifest and raw evidence;
- `simulated`: trace/model/replay evidence with its calibration boundary.

Do not upgrade a claim because a document is detailed, a source audit is
interesting, or a public project uses the same vocabulary. Source understanding
is not implemented behavior, and a planned experiment is not a result.

## 4. Judgment density and evidence discipline

Before implementation, write at least two plausible actions and a test that can
separate them. For the ToolGap application, examples include release-only
versus checked reclamation, retain versus release, restore versus recompute,
and a no-pressure control. The question is not which action sounds clever; it
is whether the action changes the declared primary outcome beyond the baseline.

Use the same executor, legal action set, QoS constraints, and measurement
definition whenever policy is the independent variable. QoS is a decision and
evaluation constraint; it is not a correctness invariant. An offline local
action oracle can select the best observed feasible action for one state, but it
is only a local regret reference, never permission to bypass safety or a global
sequential-policy upper bound. Report out-of-sample action regret and joint-SLO
effect, not a gap-prediction score.

The workload and evidence boundary must be explicit:

- client and server events use explicit join keys and declared monotonic clocks;
- right-censored returns, cancellation, timeout, and terminal outcomes are
  retained with their treatment stated;
- blocking and parallel tool groups record membership and the join rule;
- a public trace calibrates client behavior only; it does not prove server
  residency, allocator pressure, transfer cost, or admission time;
- capacity points and sentinels come from measured pool size and realized
  pressure, not an arbitrary Cartesian grid or fixed percentage gate.

## 5. Selection workflow and branches

The selection workflow is: write the role/problem claim, run Hard Tests A-E,
record proceed/narrow/stop, and only then hand the selected scope to the
project's execution roadmap. Each execution gate must have its own frozen
question and artifacts; this SOP does not create or rename those gates.

If the selected project later evaluates a policy, use the canonical policy
document's information ladder, legal-action constraints, and local action
oracle. Do not promote a selector from a selection test alone.

## 6. Failure, reshape, and stop rules

Stop or narrow the selected project when:

- the selected mechanism has no attributable outcome beyond its baseline;
- the runtime safety, recovery, or cleanup evidence cannot be owned at the
  selected seam;
- deletion leaves the claimed behavior intact: call it integration evidence,
  not candidate-owned runtime work;
- the candidate does not beat the strongest simple baseline beyond measured
  noise, or the primary metric regresses: remove the optimization claim and
  preserve the diagnosis or negative result;
- the positive region disappears under fair workload, executor, or QoS controls:
  stop the broader claim;
- a feature needs a new storage tier, router, workflow scheduler, or unrelated
  physical data plane: open a separate review rather than expanding scope.

One losing regime is a boundary, not automatically a project-wide STOP. Evaluate
the full declared causal chain and joint objective before deciding whether any
useful envelope remains. If no regime distinguishes the candidate action from
the baseline, stop the optimization rather than inventing a more complex policy.

## 7. Interview defense contract

An end-state defense should follow one chain:

```text
problem -> exact upstream path -> candidate-owned seam -> strongest baseline
  -> causal measurement -> losing condition -> deletion test -> claim state
```

The owner must be able to answer, with artifacts:

- which exact lifecycle and physical objects are upstream versus candidate;
- why release-priority-only plus stock eviction is the strongest simple baseline;
- how shared-prefix, cancel, stale completion, partial success, and cleanup are
  handled;
- which workload and pressure regime loses and what would reverse the decision;
- what is shipped, experimentally validated, simulated, or still roadmap;
- what the project deliberately did not build.

The answer must never replace a missing trace, test, manifest, or source audit
with a keyword, a market statistic, or a novelty claim.

## 8. Historical input and freshness

The earlier selection reports and evidence ledgers were useful for method, not
for current project authority. Their durable lessons are: separate job duties
from hard requirements; treat interview reports as verification examples rather
than market probabilities; use public team actions to establish technical
direction, not hiring or offer causality; and preserve provenance and dates.

The job, interview, and public-action ledgers are dated snapshots. Refresh them
before using them in a resume or a current hiring decision. The private source
note is user-provided planning material and is not public evidence. No sample
count, score, or historical project verdict is copied into this SOP.

## 9. Minimum selection checklist

Do not call the project ready for an end-state hiring claim until the owner can
point to:

- the fixed source/version audit and exact ownership map;
- the candidate/upstream ownership map;
- the deletion/bypass test;
- the strongest-simple baseline and fair action controls;
- lifecycle, recovery, failure, and cleanup tests;
- a client/server trace join and capacity-derived workload protocol;
- physical-to-SLO causal evidence and at least one losing region;
- a claim state that matches the artifact, with no broader role claim than the
  evidence supports.

Until then, the project and this SOP remain `roadmap`.
