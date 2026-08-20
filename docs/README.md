# ToolGap Documentation

> Status: `roadmap`
>
> Document set: D0 contract accepted; project claim state remains `roadmap`

## Current Boundary

The unconditional mainline is a fixed-version, Host-tier-only, session-scoped
checked demotion executor for SGLang HiCache.

The following are not part of the unconditional mainline:

- Mooncake or another L3 backend;
- proactive prefetch;
- a runtime hazard predictor;
- workflow-graph scheduling;
- cross-session future-hit valuation;
- a general cache-policy platform.

Dynamic policy is conditional on the mechanism, correctness, strongest-simple-
baseline, and measured-boundary gates. Prefetch requires a separate project
review because it has an independent signal, implementation path, and success
criterion; it is documented under `future/` and is not a G6 or a mainline
dependency.

## Reading Order

1. [governance/PROJECT_SELECTION_SOP.md](governance/PROJECT_SELECTION_SOP.md) —
   stable project-value and direction-selection method; its hard tests are not
   execution Gates.
2. [PROJECT.md](PROJECT.md) — canonical project contract: problem, causal chain,
   ownership, scope, success, and stop conditions.
3. [ARCHITECTURE.md](ARCHITECTURE.md) — proposed runtime boundary, components,
   API, identity, and upstream integration.
4. [DEMOTION_CONTRACT.md](DEMOTION_CONTRACT.md) — checked-demotion eligibility,
   linearization, outcomes, recovery, and removal-test contract.
5. [ROADMAP.md](ROADMAP.md) — decision gates and the artifacts required to move
   between them.
6. [EVALUATION.md](EVALUATION.md) — shared baseline, workload, metric,
   statistical, and evidence rules.
7. [governance/EXPERIMENT_AND_EVIDENCE_SOP.md](governance/EXPERIMENT_AND_EVIDENCE_SOP.md)
   — preregistration, provenance, failure accounting, artifact, and claim-
   promotion discipline for the existing Gates.
8. [engineering/PERFORMANCE_ENGINEERING.md](engineering/PERFORMANCE_ENGINEERING.md)
   — post-correctness performance diagnosis and minimal-optimization method.
9. [DECISIONS.md](DECISIONS.md) — proposed, accepted, rejected, and superseded
   design decisions.
10. [RELATED_WORK.md](RELATED_WORK.md) — upstream and prior-art attribution.
11. [CAREER_VALUE.md](CAREER_VALUE.md) — end-state hiring-value hypothesis and
    interview-defense boundary; it is not a current achievement claim.
12. [POLICY.md](POLICY.md) — conditional Gate G5 policy admission and design
   boundary; it is not implementation authorization.
13. [PERFORMANCE_BOUNDARY.md](PERFORMANCE_BOUNDARY.md) — post-G4 result template;
   it contains no current performance conclusion.
14. [future/PREFETCH_ADMISSION.md](future/PREFETCH_ADMISSION.md) — separate
    proactive-prefetch admission contract; it is not G6 or part of G0-G4.
15. [reviews/2026-08-17-agentic-kv-selection-review.md](reviews/2026-08-17-agentic-kv-selection-review.md)
    — historical review input; it is not a canonical technical fact source.
16. [reviews/2026-08-17-gist-planning-source-notes.md](reviews/2026-08-17-gist-planning-source-notes.md)
    — condensed planning provenance and absorption audit; it is not a second
    roadmap or a current technical fact source.

## Document Responsibilities

| Document | Owns | Must not own |
|---|---|---|
| `governance/PROJECT_SELECTION_SOP.md` | Stable project-value and selection method | G0-G5 order, current source facts, or implementation status |
| `PROJECT.md` | Project-level truth and scope | Detailed state transitions or experiment recipes |
| `ARCHITECTURE.md` | Runtime boundaries and component interactions | Performance conclusions |
| `DEMOTION_CONTRACT.md` | Safety and recovery semantics | Dynamic policy quality |
| `ROADMAP.md` | Gate order and exit decisions | Duplicated experiment procedures |
| `EVALUATION.md` | Fair measurement and evidence rules | Actual result narratives |
| `governance/EXPERIMENT_AND_EVIDENCE_SOP.md` | Preregistration, provenance, failure accounting, and claim promotion | New Gates, project metrics, or current results |
| `engineering/PERFORMANCE_ENGINEERING.md` | Performance diagnosis, RCA, and minimal optimization method | A second roadmap, result claims, or scope expansion |
| `DECISIONS.md` | Historical rationale | Repeated architecture specification |
| `RELATED_WORK.md` | Attribution and comparison boundaries | Novelty claims from absence searches |
| `CAREER_VALUE.md` | End-state hiring hypothesis and defense boundary | Current achievement, market probability, or resume metric claims |
| `POLICY.md` | Conditional selector design after G5 | Permission to start policy work |
| `PERFORMANCE_BOUNDARY.md` | Durable synthesis after G4 | Prospective performance promises |
| `future/PREFETCH_ADMISSION.md` | Independent prefetch signal/slack admission contract | G0-G4 scope or a G6 gate |
| `experiments/<gate>/` | The authorized Gate's frozen SPEC, manifest, commands, raw artifacts, results, and decision evidence | A second global roadmap or authority over Gate order |
| `reviews/` | Historical rationale and rejected alternatives | Current technical facts or claim state |

## Current Gate Artifact

The [G0 source specification](../experiments/g0/SPEC.md) and independently
reviewed [G0-C atomic seam revision](../experiments/g0/SPEC.g0-c-006.md) were
frozen and executed. Revisions
[001](../experiments/g0/SPEC.g0-c-001.md) through
[005](../experiments/g0/SPEC.g0-c-005.md) are retained as invalid protocol
attempts. [G0 ended at `RESHAPE`](../experiments/g0/RESULTS.md),
recorded by
[D021](DECISIONS.md#2026-08-17--d021-reshape-g0-around-one-atomic-checked-demote-contract):
the fixed stock pin lacks one atomic cache-level contract composing non-terminal
frontier release, backend-owned final check plus existing demote, and cache-owned
drain. G1 remains blocked; no runtime or performance claim was promoted. Later
Gates are not expanded into a second project-wide execution outline.

The frozen [G0-C-ATOMIC-007](../experiments/g0/SPEC.g0-c-007.md) pre-rental
protocol was never executed and is retained after deterministic pre-run review
found execution and evidence defects. [D022](DECISIONS.md#2026-08-20--d022-preserve-g0-c-007-and-repair-the-pre-run-protocol-as-g0-c-008)
preserves it and freezes the minimally repaired
[G0-C-ATOMIC-008](../experiments/g0/SPEC.g0-c-008.md) bundle. Purchase-page
review then found that 008 had mistaken one planned host snapshot for a causal
environment requirement. [D023](DECISIONS.md#2026-08-20--d023-reuse-provider-gpu-infrastructure-in-g0-c-009)
preserves 008 and freezes the provider-reused
[G0-C-ATOMIC-009](../experiments/g0/SPEC.g0-c-009.md) successor. Its first two
pre-arm rental attempts are retained: one exposed canonical CUDA-path discovery
ordering; one exposed an unverifiable failure seal after a fixed-source clone
network reset. [D024](DECISIONS.md#2026-08-20--d024-preserve-g0-c-009-and-repair-preflight-discovery-and-failure-sealing-as-g0-c-010)
preserves 009 and freezes the minimally repaired
[G0-C-ATOMIC-010](../experiments/g0/SPEC.g0-c-010.md) successor. Its first
rental attempt could not connect to the fixed SGLang remote; its second
received about 90 MB before the Git data connection reset. Both produced
independently verifiable pre-arm terminals and neither started an arm.
[D025](DECISIONS.md#2026-08-20--d025-preserve-g0-c-010-and-stage-the-fixed-source-as-g0-c-011)
preserves them and freezes
[G0-C-ATOMIC-011](../experiments/g0/SPEC.g0-c-011.md), which replaces only live
source transport with a SHA-256-bound Git seed. Its fifth attempt built both
wheels, installed both same-lock environments, and passed both CUDA self-checks
before the host's Hugging Face route failed with `Network is unreachable`; no
arm started. [D026](DECISIONS.md#2026-08-20--d026-preserve-g0-c-011-and-stage-the-fixed-model-as-g0-c-012)
preserves all five attempts and freezes
[G0-C-ATOMIC-012](../experiments/g0/SPEC.g0-c-012.md), which replaces only live
model transport with one archive bound by an archive hash and exact per-file
inventory. Its first attempt completed admission and produced the exact stock
27/27 RED, but Bash's active `ERR` trap intercepted that expected exit 1 before
status inspection; no treatment control or arm started.
[D027](DECISIONS.md#2026-08-20--d027-preserve-g0-c-012-and-capture-expected-red-in-g0-c-013)
preserves it and freezes
[G0-C-ATOMIC-013](../experiments/g0/SPEC.g0-c-013.md), changing only that status
capture to a Bash `if` condition. Its first attempt completed admission, the
exact stock 27/27 RED, treatment 27/27 GREEN, and the installed seam before the
full-tree inventory rejected a legal UTF-8 BOM; no server started.
[D028](DECISIONS.md#2026-08-20--d028-preserve-g0-c-013-and-read-python-source-boms-in-g0-c-014)
preserves it and freezes
[G0-C-ATOMIC-014](../experiments/g0/SPEC.g0-c-014.md), changing only the frozen
inventory decoder to `utf-8-sig`. Its first attempt completed all controls and
started stock, but FlashInfer's first CUDA JIT failed before health because the
ordinary `ninja` tool was absent; no request or treatment arm ran.
[D029](DECISIONS.md#2026-08-20--d029-preserve-g0-c-014-and-admit-ninja-in-g0-c-015)
preserves it and freezes
[G0-C-ATOMIC-015](../experiments/g0/SPEC.g0-c-015.md), adding only Ubuntu
`ninja-build` to project prerequisites and admitting/version-recording the
executable. Its first stock arm then passed JIT, health, and both requests, but
the active Bash `ERR` trap intercepted the expected signaled `wait` before a
cleanup receipt was written; no treatment arm ran.
[D030](DECISIONS.md#2026-08-21--d030-preserve-g0-c-015-and-capture-attributed-shutdown-in-g0-c-016)
preserves it and freezes
[G0-C-ATOMIC-016](../experiments/g0/SPEC.g0-c-016.md), changing only shutdown
status capture and attribution while retaining all no-survivor checks. G0
remains `roadmap`; only a completed paired runtime protocol plus off-host
verification and independent review can change the Gate decision.
[D031](DECISIONS.md#2026-08-21--d031-preserve-g0-c-016-and-wait-for-joint-cleanup-quiescence-in-g0-c-017)
preserves both 016 attempts and freezes
[G0-C-ATOMIC-017](../experiments/g0/SPEC.g0-c-017.md). It keeps the same
60-second deadline but waits for process-group, target-listener, and
attributable-GPU evidence to quiesce together before the final cleanup
snapshot. G0 remains `roadmap` pending a completed fresh attempt, off-host
verification, and independent review. Attempt 017/001 has completed the first
two requirements; independent Gate review remains pending.

## Claim States

Every material project claim uses exactly one state:

- `roadmap`: planned or proposed;
- `shipped`: implemented and exercised in the stated system;
- `experimentally validated`: measured under a declared environment and
  workload;
- `simulated`: supported only by a trace, model, replay, or simulator, with its
  calibration boundary stated.

Document completeness never upgrades a claim state.

## Maintenance Rules

1. Change `PROJECT.md` before changing downstream story or roadmap scope.
2. Record a major scope or engine decision in `DECISIONS.md`; use an ADR only
   when the choice is costly to reverse, surprising, and based on a real
   trade-off.
3. Put each executable Gate under `experiments/` with a frozen `SPEC.md`, a
   `RESULTS.md`, an environment manifest, commands, and raw artifacts.
4. Preserve negative and inconclusive results.
5. Do not copy source facts between documents; link to their canonical owner.
6. Do not turn placeholders into resume claims by changing verb tense.
7. Previous Agentic-KV documents are historical inputs. Migrate reusable
   reasoning methods only; do not import their runtime facts, source pins,
   Gate outcomes, or claim vocabulary into this project.
8. Do not maintain a second global execution outline beside `ROADMAP.md`.
   Gate-local sequencing belongs to the currently authorized Gate's SPEC.
