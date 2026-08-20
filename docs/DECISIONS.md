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

## 2026-08-20 — D022: Preserve G0-C-007 and repair the pre-run protocol as G0-C-008

Status: accepted

Context:

G0-C-007 was frozen as a successor package and ordinary-serving integration
protocol but was never executed. Pre-rental review found deterministic defects
in its default attempt path, fixed-pin package-root check, UnifiedRadixCache
selection, phase ordering, runtime identity, process cleanup, and evidence
sealing. These are protocol defects visible before either CUDA arm, not an
observed engine or mechanism result.

Decision:

Preserve G0-C-007 unchanged and record no Gate decision for it. Freeze
G0-C-008 as the smallest repaired successor G0 protocol. It retains the exact
SGLang pin, four-file patch, source controls, installed fail-closed seam,
ordinary HiCache serving question, and G0/G1 boundary. Generated attempts live
under `experiments/g0/raw/`; every phase is bound to the admitted Git/runtime
identity and predecessor receipt; exact wheels remain in the attempt; failures
receive a terminal plus artifact index; success requires a completion receipt
bound to the terminal-containing index.

Alternatives considered:

- modify the frozen 007 files in place;
- introduce a new G0.5 Gate or generic experiment-runner framework;
- widen the rerun to physical demotion, allocator evidence, or G1 execution;
- require cgroups, containers, a full dependency wheelhouse, or external
  signing before the first runtime attempt.

Evidence:

Three independent adversarial reviews agreed that the integration question is
still the narrowest useful successor G0 question while 007 is not executable as
frozen. Version-matched SGLang source places its build metadata at
`python/pyproject.toml` and requires
`SGLANG_ENABLE_UNIFIED_RADIX_TREE=1` for UnifiedRadixCache. Local probes also
reproduced the missing default parent and showed that the old structural check
did not distinguish several wrong execution/evidence implementations.

Consequences:

The project and all G0-C-008 implementation claims remain `roadmap`. Passing
the local G0-C-008 verifier authorizes only a rented runtime attempt. A complete
rented attempt still requires independent review before any successor G0 Gate
decision. An accepted successor PASS may authorize a separate G1 plan and
frozen SPEC; it does not itself authorize G1 execution.

Reopen condition:

Reopen this decision if a version-matched source check invalidates the fixed
package/cache assumptions, or if the repaired integration cannot run without
widening ownership into physical demotion, a replacement cache data plane, or
another explicitly excluded subsystem.

Affected documents and experiments:

`README.md`, `DECISIONS.md`, `../experiments/g0/SPEC.g0-c-007.md`,
`../experiments/g0/SPEC.g0-c-008.md`, and the G0-C-008 execution bundle.

## 2026-08-20 — D023: Reuse provider GPU infrastructure in G0-C-009

Status: accepted

Context:

G0-C-008 was frozen but never executed. While selecting the rental image, its
exact driver `580.65.06` and Python `3.12.11` requirements were traced back to
one planned host snapshot rather than the checked-demote decision question.
They would reject Alibaba Cloud's supported Ubuntu 24.04 NVIDIA GPU image even
though that image supplies a newer CUDA-13-compatible driver and Python 3.12,
and the pinned SGLang source does not require either exact patch version.

Decision:

Preserve G0-C-008 unchanged and freeze G0-C-009 as its infrastructure-corrected
successor. Require one physical A10, real CUDA, the exact SGLang/Torch/
Transformers source and application stack, and identical substrate for both
arms. Reuse Alibaba Cloud's official Ubuntu 24.04 NVIDIA GPU image on `gn7i`;
admit driver `>=580.65.06`, provider CUDA 13.0, and Python 3.12.x; seal the exact
image ID, instance type, region/zone, OS/kernel, GPU, driver, CUDA, Python, and
available tuning/runtime readbacks before either arm. The project may install
only ordinary SGLang build tools missing from the provider image. It may not
install or replace the GPU driver or accelerator runtime under this SPEC.

Alternatives considered:

- retain the exact 008 host snapshot as an experimental invariant;
- use a plain Ubuntu image plus Alibaba Cloud's automatic driver installation;
- add a project container despite no demonstrated virtual-environment conflict;
- manually install the NVIDIA driver and CUDA toolkit;
- modify frozen G0-C-008 in place.

Evidence:

Alibaba Cloud documents an official Ubuntu 24.04 GPU image for `gn7i` with
NVIDIA driver `580.126.09`, CUDA 12.8/13.0, cuDNN, NCCL, Docker, NVIDIA
Container Toolkit, and Python 3.12.3. Its instance-family table maps
`ecs.gn7i-c16g1.4xlarge` to one 24 GiB A10. NVIDIA documents `580.65.06` as the
minimum Linux driver for CUDA 13.0 GA, not a required exact driver. The pinned
SGLang `python/pyproject.toml` requires Python `>=3.10`, `cuda-python>=13.0`,
Torch `2.13.0`, and Transformers `5.12.1`. Primary references:

- https://help.aliyun.com/en/ecs/user-guide/ubuntu-pre-installed-nvidia-gpu-driver-image
- https://help.aliyun.com/en/ecs/user-guide/gpu-accelerated-compute-optimized-and-vgpu-accelerated-instance-families-1
- https://docs.nvidia.com/cuda/archive/13.0.0/cuda-toolkit-release-notes/index.html
- https://raw.githubusercontent.com/sgl-project/sglang/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/pyproject.toml

Consequences:

The purchase-page choice is the official preinstalled Ubuntu 24.04 NVIDIA GPU
image; the separate GPU-driver installation option remains unchecked. If that
image cannot satisfy the frozen capability checks, the attempt is retained as
`BLOCKED_BEFORE_EXECUTION`; the operator must not repair the GPU substrate in
place. A provider-managed installation fallback or manual installation requires
a new revision and explicit reason. The project remains `roadmap`; passing the
local 009 verifier authorizes only one rented G0 attempt, not a Gate result or
G1 execution.

Reopen condition:

Reopen D023 if Alibaba Cloud withdraws the supported image, its CUDA 13 path is
not usable by the pinned SGLang package, the provider image creates an observed
arm asymmetry, or a source/ABI defect proves an exact driver or Python patch is
causally required.

Affected documents and experiments:

`governance/EXPERIMENT_AND_EVIDENCE_SOP.md`, `DECISIONS.md`,
`../experiments/g0/SPEC.g0-c-008.md`,
`../experiments/g0/SPEC.g0-c-009.md`, and the G0-C-009 execution bundle.

## 2026-08-20 — D024: Preserve G0-C-009 and repair preflight discovery and failure sealing as G0-C-010

Status: accepted

Context:

The first provider-host G0-C-009 attempt stopped before an arm because the
official CUDA 13.0 executable existed at the required path but was not on the
initial non-login shell `PATH`. A second new attempt used that already-present
canonical path, then stopped during the fixed SGLang clone after a network
reset. Its raw log exposed a separate evidence defect: the failure finalizer
wrote a summary line after creating an index that included the redirected build
log, so the resulting failure terminal could not verify off host.

Decision:

Preserve G0-C-009 and both attempts unchanged. Freeze G0-C-010 with the same
source pin, patch, host capability envelope, model, controls, serving protocol,
and deadlines. It only establishes the canonical CUDA path before command
discovery and prevents failure finalization from writing post-index bytes to an
indexed artifact. Its verifier includes the redirected-log counterexample.

Alternatives considered:

- mutate 009 or overwrite either attempt;
- install or replace CUDA to satisfy bare-command discovery;
- treat the unverified 002 terminal as valid because SCP was successful;
- add retry logic, a mirror, a container, or a new infrastructure subsystem.

Evidence:

The provider `nvcc` executable reported CUDA 13.0 at
`/usr/local/cuda-13.0/bin/nvcc`; 009 itself later selected that same path. The
attempt-002 log contains the finalizer's `SEALED_FAILURE` line after the clone
error, whereas its artifact index records the pre-line hash. Both the remote
original and the off-host copy fail verification identically. A local
redirected-log regression test fails under 009 behavior and passes under 010.

Consequences:

G0 remains `roadmap`; neither pre-arm terminal is a Gate outcome or CUDA
integration result. A new 010 attempt must use a new ID and the unchanged
ordinary clone route. No driver, CUDA, source pin, dependency, model, patch,
control, serving, or G1 scope change is authorized.

Reopen condition:

Reopen if a new 010 attempt again cannot produce an independently verifiable
terminal without changes beyond the two listed corrections.

Affected documents and experiments:

`README.md`, `docs/README.md`, `DECISIONS.md`,
`../experiments/g0/SPEC.g0-c-009.md`,
`../experiments/g0/SPEC.g0-c-010.md`, and the G0-C-010 execution bundle.

## 2026-08-20 — D025: Preserve G0-C-010 and stage the fixed source as G0-C-011

Status: accepted

Context:

Two G0-C-010 rental attempts stopped before an arm on the live GitHub source
path. The first could not connect. The second received about 90 MB before a
connection reset caused `early EOF`. Its remote and off-host failure seals
verify. A GitHub web HEAD could succeed while a bounded `git ls-remote` timed
out, and GitHub's public Git Operations status was operational. Existing
evidence cannot attribute the reset to GitHub, Alibaba Cloud egress, or an
intermediary, but it does establish that the live source path is not a stable
experimental prerequisite on this host.

Decision:

Preserve 010 and both attempts unchanged. Freeze G0-C-011 with the same source
remote, commit, tree, patch, host, dependency/model pins, controls, serving
protocol, deadlines, seal, and claim ceiling. Replace only the two live SGLang
clones with two local clones restored from one operator-staged shallow bare Git
seed archive. Freeze that archive's SHA-256. Before admission, verify its hash,
Git object integrity, fixed commit/tree, canonical origin readback, and two
independent clean checkouts.

Alternatives considered:

- repeatedly spend rental time retrying full GitHub clones;
- use a source mirror, proxy, OSS subsystem, or a different SGLang pin;
- mutate 010 or place pre-staged files under its live-clone destination;
- accept a shallow Git bundle that cannot restore its missing parent boundary.

Evidence:

The 010/002 build log records the connection reset, remaining response bytes,
`early EOF`, and invalid index-pack output. Its sealed terminal verifies on and
off host. A locally fetched fixed snapshot produced the exact frozen commit and
tree. A first shallow Git bundle passed `git bundle verify` but failed a real
clone because its parent boundary was absent. The replacement portable shallow
bare Git seed restored clean checkouts on both macOS and the Ubuntu rental host;
the transferred archive SHA-256 matched exactly.

Consequences:

G0 remains `roadmap`. Source staging proves no SGLang mechanism and changes no
experiment arm. G0-C-011 may start only with the frozen seed SHA-256 and an
unused attempt ID. Success still requires commands 20 through 23 plus off-host
seal verification and independent Gate review. G1 remains blocked.

Reopen condition:

Reopen if the frozen seed cannot restore the exact commit/tree on the admitted
host, or if staging changes the resulting source, wheel, dependency, model,
control, or serving identities.

Affected documents and experiments:

`README.md`, `docs/README.md`, `DECISIONS.md`,
`../experiments/g0/RESULTS.md`, `../experiments/g0/SPEC.g0-c-010.md`,
`../experiments/g0/SPEC.g0-c-011.md`, and the G0-C-011 execution bundle.

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
