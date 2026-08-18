# Decision Log

> Status: `roadmap`
>
> D001-D019 are `accepted` design decisions. D020 records the owner's D0
> closure. D021 records the evidence-backed G0 `RESHAPE`; decision status
> remains distinct from project claim state.

## Decision Status

- `proposed`: under review;
- `accepted`: current design contract;
- `rejected`: considered and not selected;
- `superseded`: previously accepted and replaced, with history preserved.

Decision status is not a project claim state.

## Initial Decisions

| ID | Decision | Status | Reason | Reopen condition |
|---|---|---|---|---|
| D001 | Use a fixed SGLang HiCache source pin as the candidate engine | accepted | Select the substrate by whether one fixed revision offers the smallest maintainable seam for the owned contract, not by ecosystem maturity; the candidate pin still must pass G0 | G0 shows no maintainable session-scoped path, or a version-matched audit shows another substrate offers a materially narrower owned path |
| D002 | Make Host-tier checked demotion the unconditional mainline | accepted | It is the smallest path that can test physical reclamation and resume correctness | Host tier cannot provide a real recovery path |
| D003 | Candidate owns logical lifecycle and checked execution; SGLang owns the physical KV data plane | accepted | Preserves ownership without rebuilding tree, allocator, movement, or model execution | G0 proves a narrowly missing physical contract requires a patch |
| D004 | Treat Publication to a committed Host copy plus source-proven target session-priority release and stock eviction as the strongest simple baseline | accepted | It can capture most value without active reclamation; G0 must prove that priority release preserves the declared lifecycle rather than substituting terminal session close | A stronger fair baseline is found on the fixed pin, or no conforming priority-release seam exists |
| D005 | Keep proactive prefetch outside the project mainline | accepted | It has an independent signal, executor path, and success criterion | A separate review proves usable non-oracle slack and a non-duplicative mechanism |
| D006 | Defer dynamic policy until G5 | accepted | Correctness and measured action boundaries must precede selector design | G0-G4 complete and at least two regimes prefer different actions |
| D007 | Do not require Mooncake or another L3 tier | accepted | Host tier is sufficient for the core deletion test and avoids independent failure semantics | Host-only evidence exposes one precise L3-dependent question |
| D008 | Use joint resumed/foreground SLO rather than resumed TTFT alone | accepted | Capacity gains may hide active-request interference | Target deployment provides a different explicit service objective |
| D009 | Preserve old vLLM experiments as historical evidence, not proof of the new SGLang design | accepted | Negative and inconclusive work remains useful but is not transferable runtime evidence | A formally equivalent contract is demonstrated across engines |
| D010 | Archive the agentic-KV selection review as historical input, not a canonical fact source | accepted | The review preserves rationale and rejected alternatives, while its upstream and prior-art statements include claims later overturned or narrowed | The canonical documents or fixed-source audit change the historical boundary |
| D011 | Record conditional policy design now, but block implementation on G5 | accepted | The four-layer design, hazard form, information ladder, and action-regret protocol can be reviewed before coding; implementation still requires G0-G4 evidence and G5 admission | G5 shows no selector is needed, or a smaller policy contract supersedes this design |
| D012 | Keep proactive prefetch in a separate future admission review | accepted | Hint timing, usable slack, exact transfer segment, executor, and contention costs are independent of checked demotion | A separate review passes its non-oracle signal and deletion test |
| D013 | Supersede the historical P0-P9 roadmap with G0-G5 plus a separate prefetch review | accepted | The current gates separate source seam, mechanism, correctness, baseline, boundary, and policy admission without coupling prefetch to the mainline | The owner accepts a replacement Gate order and records its supersession here |
| D014 | Selectively adapt reusable methods from the previous Agentic-KV documentation; keep its runtime and market facts historical | accepted | Project-selection, evidence, and performance-diagnosis discipline transfer across questions, while old Mooncake/L3/C0/C1 facts, source pins, results, and dated hiring samples do not establish the new SGLang demotion design | A fixed-contract equivalence or refreshed evidence review proves that one specific historical fact is directly applicable |
| D015 | Keep the migration to four distinct documents: selection SOP, career-value hypothesis, evidence SOP, and performance-engineering method | accepted | They answer four non-overlapping questions without creating a second roadmap or result ledger | Two documents acquire the same authority or a future reader cannot identify the canonical owner of a decision |
| D016 | Do not migrate a second runtime failure matrix or create an empty RCA casebook | accepted | `DEMOTION_CONTRACT.md` already owns the failure/race contract, and a casebook has no evidence value before the first admitted anomaly | A real anomaly needs a durable RCA record that the minimal performance document cannot hold |

## Accepted Execution-Design Decisions

| ID | Decision | Status | Reason | Reopen condition |
|---|---|---|---|---|
| D017 | Keep `ROADMAP.md` as the only global Gate-order authority; allow a draft only for the next Gate under review, and freeze/execute detailed sequencing only after authorization in `experiments/<gate>/SPEC.md` | accepted | A non-authoritative global outline had already drifted from G2/G3 STOP branches; deleting the duplicate is simpler than synchronizing two roadmaps | A Gate-local SPEC cannot express a necessary cross-Gate dependency without changing the canonical roadmap |
| D018 | Restrict the first G1 real-engine slice to a quiescent, test-only, single-generation and single-operation path over a committed Host copy; defer lifecycle interleavings to G2 | accepted | This is the smallest safe way to observe physical demotion without prematurely implementing the full lifecycle runtime | G0 proves the physical primitive itself requires an asynchronous interaction that cannot be isolated inside this envelope |
| D019 | Require measured capacity and realized pressure before the G3 positive sentinel, judge G3 by sustainable load under the joint SLO, and keep workload-point expansion separate from pre-registered repetitions | accepted | Prevents allocator mediators, arbitrary offered-token grids, or post-hoc seed counts from becoming a false performance PASS | The accepted primary service objective or statistical contract changes |

## 2026-08-17 — D020: Accept and close the D0 documentation contract

Status: accepted

Context:

D001-D016 remained proposed until the project owner reviewed the canonical
contract and the adversarial findings. D017-D019 were already accepted and were
rechecked against the same documents.

Decision:

Accept D001-D016, retain D017-D019, and close D0. The accepted project is one
fixed-version, Host-tier-only, session-scoped checked-demotion question. It
keeps dynamic policy blocked on G5 and proactive prefetch in a separate future
review. This decision does not freeze or authorize execution of the G0 SPEC.

Alternatives considered:

- keep D0 open despite owner approval;
- couple L3, prefetch, or dynamic policy into the unconditional mainline;
- treat documentation completion as runtime or performance evidence.

Evidence:

The owner approved the reviewed D001-D016 packet on 2026-08-17. The review also
strengthened the baseline, committed-copy, removal-test, and G1/G2 boundaries
without changing the project question.

Consequences:

G0 is the next Gate, but its SPEC remains draft and not frozen. The project
claim state remains `roadmap`; no source attempt, runtime implementation, GPU
measurement, or performance result is accepted by this decision.

Reopen condition:

Reopen D0 when evidence changes the project question, ownership split,
unconditional dependencies, explicit exclusions, or global Gate order. A G0
PASS, RESHAPE, or STOP within the accepted branches does not by itself reopen
D0.

Affected documents and experiments:

`../README.md`, `README.md`, `PROJECT.md`, `ARCHITECTURE.md`,
`DEMOTION_CONTRACT.md`, `ROADMAP.md`, `EVALUATION.md`, `POLICY.md`,
`future/PREFETCH_ADMISSION.md`, and the draft `experiments/g0/SPEC.md`.

## 2026-08-17 — D021: Reshape G0 around one atomic checked-demote contract

Status: accepted

Context:

The frozen G0 source audit inspected SGLang
`92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`. The physical tree, Host transfer
completion, live device-leaf predicate, TreeCore demotion primitive, free
payload, allocator action, per-session frontier index, and Full coverage counts
all exist on that pin. Public `release_radix_session`, however, records a close
tombstone and removes the generation before releasing component contributions.

Decision:

Set G0 to `RESHAPE`. Select `write_through` as the only Host semantic branch.
Isolate one atomic cache-level upstream contract that validates generation,
snapshots and non-terminally releases target frontiers, asks the registered
TreeCore backend to combine final live checks with its existing `demote` in one
backend method, and keeps raw-result drain in the cache owner. Keep physical
ownership/data movement in upstream and lifecycle ownership in the later
candidate runtime. Block G1 until the contract is reviewed, included in an exact
pin, and G0 is rerun on the frozen CUDA-capable environment.

Alternatives considered:

- declare `PASS` from private component methods and a direct NodeId demote;
- use terminal session close as temporary priority release;
- maintain a candidate-owned session-to-physical-node index;
- declare `STOP` and replace the cache backend;
- broaden G0 into a real executor or lifecycle implementation.

Evidence:

The capability matrix maps all eight architecture questions and all nine
demotion predicates to immutable fixed-pin source. Independent review
invalidated both the tracker-only 001 attempt and preparation-only 002 attempt;
002 allowed mutation between admission and execution and did not test the
maintained interface or aggregate semantics. Later independent reviews also
invalidated 003 and 005 through credible wrong implementations; 004 was
invalidated after registration and before execution. Corrected G0-C-006 froze
the full successor configuration and executable dependency hashes, then failed
all 27 cases on stock and passed all 27 with a four-file, 216-insertion source
prototype. A fresh independent rerun reproduced both arms and found no remaining
Gate-blocking counterexample. The actual interface/registry/outcome types,
target-only multi-session release, exact caller/NodeId/freed-ID attribution,
mixed frontier order, Host-lock separation, legacy vertical release, and
cleanup boundaries are executable. No second index or physical algorithm is
added, and the real physical path is not invoked in G0.

Consequences:

The project remains `roadmap`. No stock SGLang run, GPU result, allocator
measurement, output-correctness proof, lifecycle result, or performance result
is accepted. The exact stock launch was frozen but blocked before execution by
the local non-CUDA environment. G1 has no execution authorization. The only
legal next action is vertical contract review/integration, exact repinning, and
a new G0 run on the declared CUDA-capable testbed.

Reopen condition:

Reopen D021 if a fixed upstream pin exposes an equivalent atomic operation, the
proposed contract cannot be integrated without broader ownership changes, final
checks and existing demote cannot remain in one backend call, or source evidence
invalidates the Full-only conservative resolver proof.

Affected documents and experiments:

`README.md`, `ROADMAP.md`, `DECISIONS.md`, `../experiments/g0/SPEC.md`,
`../experiments/g0/SPEC.g0-c-001.md`,
`../experiments/g0/SPEC.g0-c-002.md`,
`../experiments/g0/SPEC.g0-c-003.md`,
`../experiments/g0/SPEC.g0-c-004.md`,
`../experiments/g0/SPEC.g0-c-005.md`,
`../experiments/g0/SPEC.g0-c-006.md`, and
`../experiments/g0/RESULTS.md`.

## Decision Template

```text
## YYYY-MM-DD — Dxxx: Title

Status: proposed | accepted | rejected | superseded

Context:

Decision:

Alternatives considered:

Evidence:

Consequences:

Reopen condition:

Affected documents and experiments:
```

Create an ADR only when the accepted choice is costly to reverse, surprising
without history, and represents a genuine architectural trade-off. The decision
log links to that ADR rather than duplicating it.
