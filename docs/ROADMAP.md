# Gate-Driven Roadmap

> Status: `roadmap`
>
> Gate order is authoritative. Calendar estimates remain secondary to Gate
> evidence and are added only when they serve the currently authorized work.

## 1. Roadmap Rules

1. Each Gate answers one decision question.
2. Each Gate has a frozen experiment `SPEC.md` before execution.
3. PASS, RESHAPE, and STOP branches are written before results are observed.
4. A later mechanism cannot compensate for a failed earlier correctness or
   ownership Gate.
5. `ROADMAP.md` is the only global Gate-order authority. Do not maintain a
   second project-wide execution outline that copies future Gate questions or
   decision branches.
6. Detailed implementation and experiment sequencing lives in
   `experiments/<gate>/SPEC.md`. A draft may be prepared for the next Gate under
   review, but only an authorized Gate's SPEC may be frozen or executed; later
   Gates are not expanded in advance.
7. Negative and inconclusive results remain first-class artifacts.

## D0 — Documentation Contract

### Question

Do the project contract, ownership boundary, exclusions, and Gate order express
one causal question without coupling independent projects?

### Required output

- accepted `PROJECT.md`;
- accepted ownership boundary in `ARCHITECTURE.md`;
- accepted core invariants in `DEMOTION_CONTRACT.md`;
- reviewed conditional design in `POLICY.md` (implementation remains blocked by
  G5);
- separate `future/PREFETCH_ADMISSION.md` review contract;
- decision entries for Host-only mainline, policy deferral, and prefetch
  separation.

### Exit

The documents contain no contradictory default dependency on Mooncake,
prefetch, dynamic prediction, or a full cache-backend replacement.

D0 was accepted by the project owner on 2026-08-17 through
[D020](DECISIONS.md#2026-08-17--d020-accept-and-close-the-d0-documentation-contract).
This accepts the documentation contract but does not by itself upgrade the
project claim state beyond `roadmap`. G0 was subsequently executed and recorded
under D021 below.

## G0 — Fixed Source and Safe Seam

The [G0 source SPEC](../experiments/g0/SPEC.md) was frozen and executed against
SGLang `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`. Its historical decision was
`RESHAPE`: stock lacks one atomic cache-level checked-demote contract composing
generation-preserving frontier release, backend-owned final checks and the
existing physical primitive, then cache-owned drain. Independently reviewed
G0-C-006 represents that missing seam as a four-file, 216-insertion vertical
source prototype with one caller surface, exact target/caller attribution,
fail-closed legacy behavior, and no second index.

Independently reviewed [G0-C-017/001](../experiments/g0/RESULTS.md) is the
accepted successor `PASS`. Its fixed oracle reproduced 27/27 stock RED and
27/27 treatment GREEN; the exact treatment wheel installed, the registered
cache seam failed closed without a physical call, and both stock and treatment
completed ordinary HiCache CUDA serving and cleanup on the frozen A10 host.
This is a narrow `experimentally validated` package/serving-integration result.
It does not prove physical demotion, allocator-visible reclamation, lifecycle
or output correctness, recovery, performance, upstream acceptance, or general
compatibility. The overall project claim state remains `roadmap`.

### Decision question

Can the fixed SGLang version map a session-scoped intent to exact, currently
eligible device leaves, establish the target-only priority-release baseline,
and invoke physical demotion through maintainable seams?

### Work

- freeze the SGLang commit and configuration;
- audit session generation, frontier/path bookkeeping, session priority,
  device-leaf membership, transfer state, cascade behavior, and completion;
- prove a target-only priority-release operation that preserves the declared
  pause/resume lifecycle, or retain its absence as a RESHAPE/STOP input;
- construct counterexamples for shared prefixes, tree mutation, and pending
  work;
- prototype the narrowest checked resolver without building a replacement cache
  backend.

### Required artifacts

- source capability matrix with exact links;
- source-backed priority-release mapping or failing counterexample;
- proposed checked-demote interface;
- session-to-leaf ownership proof or failing counterexample;
- minimal extension/patch boundary;
- removal-test design.

### Decision

- **PASS:** exact safe mapping, a conforming priority-release baseline, and
  maintainable invocation/completion seams are demonstrated.
- **RESHAPE:** one narrowly missing upstream contract is isolated and can be
  represented by an auditable patch plus failing test.
- **STOP:** correctness requires broad cache-backend replacement or a second
  physical ownership system.

## G1 — Forced Host-Tier Mechanism

G0 PASS authorizes preparation and review of a separate G1 plan and frozen
SPEC. It does not authorize G1 execution; that requires an explicit later
decision after the G1 contract and evidence protocol are accepted.

### Decision question

Does checked demotion of a committed Host-backed target create observable and
allocator-visible GPU capacity on the real engine path?

### Work

- implement only the G0-proven target session-priority release and forced
  checked reclamation;
- begin with a test-only quiescent slice: one current session generation, one
  operation, a committed Host copy, a private target tail, no concurrent
  resume/cancel/new pause, no tree mutation, and no conflicting pending work;
- use an internal forced trigger; G1 does not select or expose the final public
  pause/hint API;
- record Host commitment, operation identity, requested, eligible, scheduled,
  and completed targets, plus allocator pages before/after and time to
  allocator-visible headroom;
- exercise a private-tail positive case and rejection cases;
- prove the default request path bypasses candidate logic.

G1 proves only the narrow physical mechanism inside this envelope. G2 owns
resume, cancellation, repeated pauses, stale completion, failure, partial
completion, and other asynchronous lifecycle interleavings.

### Required artifacts

- minimal candidate-owned executor;
- deterministic tests around acceptance and filtering;
- one real forced-demotion trace;
- one removal/bypass test showing that the candidate immediate action and
  time-to-headroom effect disappear while eventual stock eviction remains;
- exact environment manifest and reproduction command.

### Decision

- **PASS:** physical completion and allocator-visible capacity are attributable.
- **STOP:** only logical bookkeeping changes, or the candidate's immediate
  action and time-to-headroom are unchanged after bypassing candidate behavior.

## G2 — Lifecycle Correctness and Recovery

### Decision question

Is the mechanism safe across resume, cancel, stale completion, failure, shared
prefixes, and partial completion?

### Work

- implement the minimal lifecycle registry and operation identity;
- implement final eligibility revalidation;
- fence stale completion while preserving cleanup;
- implement one safe restore/recompute fallback;
- run the failure and race matrix from `DEMOTION_CONTRACT.md`.

### Required artifacts

- state-transition tests;
- deterministic failure injection;
- output-equivalence evidence;
- block/job/lock/buffer cleanup ledger;
- DecisionTrace examples for every requested/observed disagreement.

### Decision

- **PASS:** declared invariants hold and quiescence restores capacity accounting.
- **RESHAPE:** narrow the supported lifecycle cases and state the boundary.
- **STOP:** safe recovery or cleanup cannot be owned at the selected seam.

## G3 — Strongest Simple Baseline

### Decision question

Does immediate checked reclamation add measurable value over Publication to the
same committed Host copy plus the G0-proven target session-priority release
followed by stock eviction?

### Work

- use identical Host copies, workload, arrival process, and instrumentation;
- compare release-only and checked-reclamation paths;
- measure actual KV-pool capacity and realized pressure before registering the
  candidate positive sentinel; offered tokens alone do not establish a
  reachable pressure regime;
- measure time-to-headroom, scheduler effects, resumed latency, foreground tail,
  and recovery cost;
- use maximum sustainable arrival rate under the pre-registered joint SLO as
  the primary endpoint; physical and request-stage measurements are causal
  mediators, not independent PASS criteria;
- include no-pressure and already-sufficient-stock losing controls.

### Decision

- **PASS:** the mechanism wins beyond declared noise in at least one reachable
  pre-registered regime without violating guardrails.
- **RESHAPE:** remove active reclamation and retain the source diagnosis,
  release-only integration, or upstream test contribution.
- **STOP:** no attributable behavior remains after simplification.

## G4 — Measured Performance Boundary

### Decision question

Where does checked demotion win, lose, or become irrelevant under realistic
memory pressure and recovery cost?

### Work

- calibrate a small set of sentinel regimes before any broad sweep;
- vary realized device pressure, unique reclaimable bytes, shared-prefix ratio,
  gap/resume behavior, and foreground load;
- report sustainable arrival rate under the joint SLO;
- preserve negative and interference-heavy regimes.

The number of workload points may grow only from measured sentinel evidence.
The repetition count, pairing, aggregation, and interval method for each
comparison are frozen in its SPEC before the primary result is observed.

### Required output

- `PERFORMANCE_BOUNDARY.md` populated from real results;
- raw results, manifest, repetitions, confidence intervals, and exact commands;
- a causal decomposition from physical reclamation to request-level effects.

### Exit

G4 completes with either a defensible positive boundary or a defensible negative
result. It does not require dynamic policy.

### Conditional performance diagnosis (not a Gate)

After G0-G2, a reproducible symptom encountered during G3 or G4 may invoke the
method in [`engineering/PERFORMANCE_ENGINEERING.md`](engineering/PERFORMANCE_ENGINEERING.md).
No diagnosis report or optimization patch is required when no symptom exists.
A behavior-changing fix requires an updated SPEC revision and new run identity;
it cannot retroactively turn an earlier result into PASS.

## G5 — Dynamic Policy Admission

### Decision question

Do at least two reachable, reproducible regimes prefer different actions, such
that a runtime selector can add value over a tuned static/action-only baseline?

### Preconditions

- G0-G4 complete;
- identical executors across policy baselines;
- separate tuning and evaluation traces;
- decision margin larger than measurement and model error;
- bounded hot-path and tail overhead.

The design to be evaluated is in [`POLICY.md`](POLICY.md). Its existence is
roadmap documentation only; no selector implementation starts before G5
passes.

### Decision

- **PASS:** authorize the smallest transparent selector described in
  `POLICY.md`.
- **STOP POLICY:** keep the mechanism and boundary evidence; do not implement a
  dynamic selector.

## Future Project Review — Proactive Prefetch (not G6)

See [`future/PREFETCH_ADMISSION.md`](future/PREFETCH_ADMISSION.md). Prefetch
requires a separate review that proves a non-oracle `resume_imminent` signal,
positive usable slack for the exact transfer segment, an independent executor
path, and a baseline beyond request-time reactive restore. Failure or success of
prefetch must not change G0-G4 conclusions.
