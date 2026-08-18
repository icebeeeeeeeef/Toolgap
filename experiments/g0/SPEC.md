# G0 Source Audit Specification — Fixed Source and Safe Seam

> Status: `roadmap`
>
> Specification state: `frozen`
>
> Revision: `G0-SOURCE-001`
>
> Run identity: `g0-source-audit-001`
>
> Frozen at: `2026-08-17T15:01:06Z`
>
> Claim ceiling: source/design evidence for G0 only; no `shipped`, real-engine,
> allocator-visible, lifecycle-correctness, or performance claim

## 1. Authority and decision question

This is the frozen source-only specification for G0-A and G0-B. It is governed
by the following authority order:

```text
PROJECT.md
-> ARCHITECTURE.md
-> DEMOTION_CONTRACT.md
-> ROADMAP.md
-> EVALUATION.md + EXPERIMENT_AND_EVIDENCE_SOP.md
-> DECISIONS.md
-> this G0 artifact bundle
```

`toolgap/docs/reviews/` and the repository's historical vLLM work are excluded
as current technical evidence.

Decision question:

> Can SGLang commit `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`
> map a session-scoped intent to exact, currently eligible device leaves,
> establish a target-only priority-release baseline that preserves the declared
> pause/resume identity, and expose maintainable physical-demotion invocation
> and completion-observation seams?

Hypothesis:

> The fixed source exposes enough session, tree, residency, transfer, and
> completion state to resolve a conservative legal target set and call the
> upstream physical path without replacing the cache backend or maintaining a
> second physical ownership system.

## 2. Frozen source and workspace identity

| Field | Frozen value |
|---|---|
| Upstream | `https://github.com/sgl-project/sglang.git` |
| Commit | `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2` |
| Commit tree | `25e9bf86d04c27fe380024d9c8c421c3b5b51f3c` |
| Commit parent | `b6d7602914d1d54253e79b1cc5b8f9017152b6e0` |
| Commit subject | `[Fix] Correct dense FP8 Marlin bias ordering (#35020)` |
| Local audit checkout | `/private/tmp/toolgap-kv-g0-sglang-92b1d382` |
| Checkout state | detached `HEAD` at the frozen commit; sparse worktree; no local patch |
| Candidate repository HEAD | `db0b4fa` |
| Candidate branch | `codex/ai-infra-interview-map` |
| Candidate worktree | dirty before G0; all pre-existing changes are out of scope; `toolgap/` was already untracked |
| G0 patch identity | `N/A: source-only audit; no upstream or candidate runtime patch is authorized` |

The sparse checkout includes only the fixed revision's source surfaces needed
for this audit:

- `python/sglang/srt/mem_cache/`;
- `python/sglang/srt/managers/`;
- `test/registered/unit/mem_cache/`;
- `benchmark/hicache/`;
- `docs/backend/hicache/`.

If evidence requires another path from the same commit, it may be added to the
sparse checkout and recorded in the manifest. The commit may not change inside
this run identity.

## 3. Frozen configuration boundary

This run is source-only. It audits the single-node SGLang HiCache unified radix
path with a device tier and Host tier, no Mooncake/L3 dependency, and no public
pause/hint API.

| Runtime/config field | Frozen value |
|---|---|
| Host write mode | `N/A: source-only; selecting exactly one mode is an output of G0-B` |
| Model and revision | `N/A: source-only; no model is loaded` |
| Tokenizer/template revision | `N/A: source-only; no request is run` |
| Dtype | `N/A: source-only; no KV allocation is measured` |
| Page size | `N/A: source-only; no allocator run occurs` |
| Context limit | `N/A: source-only; no request is run` |
| Cache flags | `N/A: source-only; exact G0-C flags require the selected Host mode` |
| Memory fraction | `N/A: source-only; no device pool is created` |
| Hardware/device | `N/A: source-only; no GPU result is attempted` |
| Driver/runtime versions | `N/A: source-only; no CUDA/ROCm runtime is invoked` |
| Python/dependency environment | `N/A: source-only; upstream modules are not imported or installed` |
| Workload/arrival process/seeds | `N/A: source-only; no workload is executed` |
| SLO/statistical protocol | `N/A: source-only; no treatment comparison or metric is produced` |

The source audit may compare upstream write modes only to determine which one
has auditable committed-copy and completion semantics. It may not prototype or
run both modes as a hedge.

## 4. Included work and forbidden work

Included:

1. map all eight questions in `ARCHITECTURE.md` section 8;
2. map every current predicate in `DEMOTION_CONTRACT.md` section 4;
3. separate `fact`, `inference`, and `unresolved` claims;
4. identify candidate-owned and upstream-owned responsibility;
5. construct decision-relevant counterexamples for shared/non-target coverage,
   post-resolution tree/leaf mutation, and pending/conflicting structural or
   transfer work including cascade/completion effects;
6. prove a pause/resume-preserving target-only priority release, or retain a
   precise failing counterexample;
7. propose the narrowest checked-demote boundary and G1 removal/bypass test;
8. choose one Host write mode only if source establishes committed-copy,
   authoritative completion, and a maintainable patch surface.

Forbidden in this revision:

- any stock runtime or model download;
- any candidate physical executor or forced demotion;
- any performance or allocator-visible claim;
- public pause/hint API design;
- resume, cancel, stale-completion, failure orchestration, or the full G2 race
  matrix;
- a second cache backend, allocator, ownership index, or physical data plane;
- L3/Mooncake, dynamic policy, TraceLab hazard, workflow automaton, or prefetch;
- an upstream patch without one isolated missing contract and a test that fails
  without that patch.

## 5. Evidence protocol

Primary evidence is the frozen upstream source or tests at the exact commit.
Every material capability entry must include:

- an immutable GitHub blob URL containing the full commit;
- a local file path and line range from the detached checkout;
- the observed behavior, not an API-name inference;
- classification as `fact`, `inference`, or `unresolved`;
- owner as `candidate` or `upstream`;
- effect on the G0 branch;
- a source-level or executable counterexample when the claim could change the
  branch.

Search snippets, current `main`, README statements without code confirmation,
old vLLM results, and historical review notes cannot decide G0.

The capability matrix basis is:

```text
Target: fixed-pin SGLang session-scoped checked-demotion seam
Confidence claim: source evidence excludes the known credible unsafe mappings
Basis: PROJECT.md, ARCHITECTURE.md section 8, DEMOTION_CONTRACT.md section 4,
       ROADMAP.md G0, and this frozen specification
Current evidence: frozen upstream source plus retained command outputs
```

The smallest mandatory counterexample obligations are:

| Behavior obligation | Credible wrong implementation | Distinguishing oracle |
|---|---|---|
| Do not demote protected non-target coverage | Treat frontier `session_ids` as complete arbitrary-node ownership | Shared/private-prefix construction must expose missing or non-target coverage; unresolved coverage cannot authorize demotion |
| Revalidate at execution | Resolve once and retain stale node/leaf identity | Mutation between resolution and submission makes the final predicate fail or remain unresolved |
| Reject/defer conflicting work | Check only Host value or `backuped` | Pending store/load/structural/cascade/completion state prevents a committed, pending-free authorization |

These rows define G0 evidence only. G2 owns resume/cancel/newer-pause/late-
completion orchestration.

## 6. Commands and artifacts

Frozen command entrypoints:

- `commands/00-acquire-source.sh` — acquire and detach the exact source;
- `commands/01-source-identity.sh` — reproduce source/worktree identity;
- `commands/02-source-audit.sh` — collect the initial version-matched symbol and
  call-site inventory;
- `commands/03-verify-bundle.sh` — verify JSON, checksums, source links, and
  repository formatting after the run is sealed.

Required artifact paths:

- `artifacts/preflight.md`;
- `artifacts/source-identity.txt`;
- `artifacts/source-audit.txt`;
- `artifacts/source-index.md`;
- `artifacts/capability-matrix.md`;
- `artifacts/counterexample-matrix.md`;
- `artifacts/priority-release.md`;
- `artifacts/session-to-leaf.md`;
- `artifacts/checked-demote-interface.md`;
- `artifacts/g1-removal-test.md`;
- `RESULTS.md`;
- `manifest.json`.

If G0-B cannot support a Host-mode choice or isolates a decisive blocker, the
corresponding missing G0-C artifacts are recorded as `N/A` with reasons rather
than fabricated.

## 7. Outcome branches

Apply `ROADMAP.md` verbatim:

- **PASS:** exact safe mapping, a conforming target-only priority-release
  baseline, and maintainable invocation/completion seams are demonstrated.
- **RESHAPE:** exactly one narrowly missing upstream contract is isolated and
  can be represented by an auditable minimal patch plus a failing test.
- **STOP:** correctness requires broad cache-backend replacement or a second
  physical ownership system.

Missing evidence, inaccessible source, an unselected/unauditable Host mode,
environment blockage, or uncertain runtime behavior is not PASS. It remains
`unresolved` unless the evidence cleanly meets RESHAPE or STOP.

No Gate decision upgrades the project claim state beyond `roadmap` in this
source-only run.

## 8. G0-C revision rule

No stock runtime or prototype is authorized by `G0-SOURCE-001`. If G0-B selects
one Host mode and source evidence justifies continuing, create both:

- a new immutable `SPEC.g0-c-001.md` with exact model, revision, dtype, page
  size, flags, memory fraction, environment, command, failure accounting, and
  artifact paths; and
- a new `manifest.g0-c-001.json` with a distinct run identity.

The source-only SPEC, manifest, raw outputs, and decision record remain
unchanged and linked from the G0-C revision.

## 9. Freeze and checksum procedure

From the repository root:

```bash
shasum -a 256 toolgap/experiments/g0/SPEC.md
```

Record the exact digest in `manifest.json` before running
`commands/02-source-audit.sh`. After that point this file is immutable. Any
change to the question, source, configuration boundary, evidence oracle, or
branching rule requires a new SPEC revision and run identity; it may not be
edited into this historical revision.
