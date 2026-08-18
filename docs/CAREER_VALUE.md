# ToolGap Career Value

> Status: `roadmap`
>
> Project claim state: `roadmap`
>
> This is an **end-state hiring hypothesis**, not a current project result,
> job-description score, completion report, offer prediction, or novelty claim.

## 1. Positioning hypothesis

If the current ToolGap contract is implemented and evidenced, it could support
the following positioning:

> LLM Serving / Inference Infra engineer focused on safe KV-cache lifecycle,
> session-scoped resource reclamation, and measurable runtime boundaries.

The concrete project is a Host-tier, session-scoped checked-demotion executor
for one fixed SGLang HiCache version. Its value would come from owning a narrow
runtime contract and defending its causal evidence—not from inventing a new
cache algorithm or collecting more technology names.

Novelty has approximately zero weight in this hypothesis. Prior art determines
what must be attributed and which baseline is fair. It does not justify a claim
of “first”, universal superiority, or a higher hiring probability.

The direct role fit is serving runtime, cache lifecycle, and scheduler-adjacent
AI Infra. The project alone would not establish ownership of CUDA kernels,
compilers, NPU adaptation, RDMA, multi-node systems, or production operations.

## 2. Current state and claim boundary

The canonical project documents currently describe a `roadmap` design. They do
not, by themselves, establish `shipped` code, `experimentally validated`
performance, or `simulated` evidence. This file therefore makes no current
completion or performance claim.

The project must not claim that an upstream physical capability is absent. The
current source and ownership boundary is maintained by
[ARCHITECTURE.md](ARCHITECTURE.md), while the checked session contract is
maintained by [DEMOTION_CONTRACT.md](DEMOTION_CONTRACT.md). This document does
not repeat their source symbols or lifecycle contract.

The current project does not claim:

- an optimization gain, a capacity number, or a completed implementation;
- a market share, job frequency, interview probability, score, or offer uplift;
- that a public trace proves server residency, allocator pressure, or transfer
  cost;
- that a policy or predictor is implemented; policy remains conditional on G5;
- that proactive prefetch belongs to the mainline; it has a separate future
  admission contract;
- generalization beyond the fixed source, declared single-node environment,
  workload, and measured boundary;
- ownership of a remote/distributed storage layer or another physical KV data
  plane.

## 3. What an end-state project could prove

These are hiring hypotheses. Each row becomes a claim only when the listed
artifact exists and its state is recorded correctly.

| Potential signal | Required artifact | Permitted claim state when established |
|---|---|---|
| Source-level serving-runtime understanding | Fixed-version source audit artifact, source map, and upstream/candidate boundary | `roadmap` for the candidate project claim; an audit artifact alone does not become `shipped`, which requires implemented and exercised code/tests |
| Lifecycle ownership | Candidate executor and tests for identity, generation, idempotence, cancellation, stale completion, fallback, and cleanup | `shipped` |
| Physical causal reasoning | DecisionTrace plus allocator-visible completion and capacity accounting | `experimentally validated` only with a declared run and raw evidence |
| Fair performance judgment | Same workload/executor, release-priority-only plus stock eviction baseline, controls, and losing region | `experimentally validated` |
| Trace/model reasoning | Replayed or modeled client behavior with calibration boundary and no server inference | `simulated` |
| Scope and claim discipline | Removal/bypass test, negative result, reproducible manifest, and explicit stop rule | `shipped` for the test artifact; any measured conclusion is `experimentally validated` |

The table is not a promise that every row will pass. A negative or narrowed
result can still be useful evidence when its hypothesis, baseline, causal
measurement, and decision consequence are preserved.

## 4. Why the project could be interview-defensible

The defensible story is a sequence of ownership and evidence decisions:

```text
pause intent
  -> session generation / operation identity
  -> committed Host copy
  -> legal device-leaf resolution
  -> checked physical demotion
  -> allocator headroom
  -> resumed/foreground SLO effect
  -> losing boundary and cleanup proof
```

An interviewer should be able to inspect, or be pointed to, the following:

- the exact fixed source seam and which objects remain upstream-owned;
- the candidate lifecycle registry, eligibility recheck, completion fence,
  fallback, and cleanup ledger;
- the strongest simple baseline: Publication plus target session-priority
  release followed by stock eviction;
- a fair forced checked-reclamation comparison, not a hit-rate-only report;
- shared-prefix, running-lock, pending-transfer, cancellation, partial-success,
  and stale-completion tests;
- physical completion and allocator-visible headroom, then request-level and
  foreground effects;
- at least one losing, irrelevant, or stop region;
- the ownership deletion test showing that removing candidate code removes the
  checked behavior while ordinary stock behavior remains meaningful.

The project is not defensible merely because it uses SGLang, mentions agents,
or reproduces a public cache system.

## 5. Interview answer map

| Likely question | Evidence-backed answer shape |
|---|---|
| “What did you own?” | “The candidate-owned part was session identity, checked target resolution, lifecycle fencing, fallback, cleanup, and DecisionTrace; SGLang owned the tree, allocator, movement, eviction, and execution.” |
| “Why SGLang instead of vLLM?” | “The substrate was selected by whether one fixed source revision offered the smallest maintainable seam for this owned contract, not by ecosystem maturity alone. G0 must still prove that SGLang seam; D001 is reopened if it cannot, or if a version-matched audit demonstrates a materially narrower owned path elsewhere.” Do not turn historical vLLM observations into a current cross-engine claim. |
| “Why not just let stock eviction run?” | “That is the primary release-priority-only baseline. Checked reclamation must show earlier allocator-visible headroom and a joint-SLO benefit beyond it, or it is removed.” |
| “Is this only a wrapper?” | Show the deletion/bypass test and the behavior that disappears; a configuration or trace-only change is not enough. |
| “What happens with a shared prefix?” | Apply the version-matched non-target coverage contract; reject or clip when exact protection cannot be proven. Correct output equivalence and cache-interference protection are separate claims. |
| “What happens on cancel or stale completion?” | The authoritative operation identity fences publication; old work cannot mutate newer state, but all old jobs, buffers, locks, and reservations still reach cleanup. |
| “When does it lose?” | Name low pressure, small KV/expensive recovery, timely stock eviction, shared-prefix-heavy eligibility, or foreground-interference regimes from the measured boundary. |
| “Did you build a predictor or prefetcher?” | Not as a current claim. Dynamic selection requires G5; proactive prefetch is separately reviewed and cannot be used to inflate the mainline story. |
| “Can this generalize to production or other hardware?” | Only to the declared environment and workload until separate artifacts establish a broader boundary. |
| “Does slower restore than recompute stop the project?” | It establishes a local losing condition. The full early-reclaim, recovery, foreground, and joint-SLO chain decides whether any useful envelope remains. |

## 6. End-state resume language

The following is a template, not a sentence that may be used now:

> On fixed SGLang HiCache commit `[commit]`, implemented `[candidate-owned
> lifecycle/checked-demotion artifact]`; compared it with Publication plus
> session-priority release and stock eviction under `[manifest/workload]`, and
> measured `[physical-to-SLO result]` with `[correctness/cleanup evidence]`.
> The result lost or became neutral under `[registered boundary]`.

Fill the template only after the relevant artifacts have the matching claim
state. Do not insert invented percentages, scores, sample counts, job titles,
hardware claims, or completion verbs. If the result is `roadmap`, say it is
planned. If it is `shipped`, identify the code and test. If it is
`experimentally validated`, identify the environment and raw run. If it is
`simulated`, state the model/replay and what it cannot establish.

## 7. Role-fit use and limits

This project is intended to be one evidence packet for roles whose work is
close to:

- LLM serving and inference runtime;
- KV-cache lifecycle, memory pressure, and recovery;
- scheduler-adjacent resource decisions and SLO measurement;
- AI Infra backend work that requires source reading, failure handling, and
  reproducible performance diagnosis.

It is adjacent evidence—not direct proof—for broader AI platform or MaaS
backend roles. It is not a substitute for the fundamentals those roles may
test: programming, data structures, Linux, concurrency, networking, GPU
execution, and systems design.

It is not direct evidence for kernel/compiler/NPU/RDMA/multi-node roles. A
candidate may discuss transferable reasoning, but must not present this
single-node Host-tier project as experience that was not performed.

## 8. Historical hiring inputs and freshness

The earlier JD, interview, and public-team-action ledgers are dated evidence
snapshots. They are useful for shaping this verification method:

- job duties must be separated from hard or optional requirements;
- interview reports are examples of ownership, baseline, measurement, and
  boundary questions, not market probabilities;
- public technical actions establish a team's technical direction, not current
  headcount, hiring, or offer causality;
- private, user-provided planning notes are not public evidence.

Refresh those sources before using them in a current application or public
resume. This document intentionally carries no historical sample numbers,
scores, or company-ranking claims.

## 9. End-state acceptance checklist

Before upgrading the career story beyond `roadmap`, verify:

- fixed source commit and source-to-ownership map are recorded;
- lifecycle and physical boundaries are tested, not inferred from a wrapper;
- the deletion/bypass test passes;
- the strongest simple baseline and fair controls are run;
- output, stale, cancel, partial, fallback, and cleanup invariants are tested;
- client/server clocks, join keys, censoring, and tool-group rules are recorded;
- capacity and pressure are measured rather than represented by an arbitrary
  grid;
- the primary joint SLO, physical causal chain, raw artifacts, and losing
  region are available;
- every sentence in the resume or interview uses the artifact's claim state.

Until this checklist is satisfied, the honest description is a `roadmap`
project and hiring hypothesis, not a completed achievement.
