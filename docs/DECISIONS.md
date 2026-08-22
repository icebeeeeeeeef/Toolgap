# Decision Log

> Status: `roadmap`
>
> D001-D019 are `accepted` design decisions. D020 records the owner's D0
> closure. D021 preserves the historical evidence-backed G0 `RESHAPE`; D032
> records the accepted successor G0 `PASS`. D033-D035 keep later scope and
> optimization choices conditional on evidence. Decision status remains
> distinct from project claim state.

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

## 2026-08-20 — D026: Preserve G0-C-011 and stage the fixed model as G0-C-012

Status: accepted

Context:

G0-C-011 attempts 001-004 preserved ordinary Rust/build-cache prerequisites.
Attempt 005 then built distinct stock and treatment wheels, resolved and
installed the same dependency lock into two isolated environments, and passed
the fixed CUDA/Torch self-check in both. Before any arm, its fixed Hugging Face
snapshot request failed with `Network is unreachable`; the connection never
left TCP `SYN-SENT`, and no model bytes entered the host cache.

Decision:

Preserve G0-C-011 and all five attempts unchanged. Freeze G0-C-012 with the same
source seed, commit/tree, patch, host, dependency resolution, model repository
and revision, controls, serving protocol, deadlines, seal, and claim ceiling.
Replace only the live Hugging Face download with one operator-staged archive.
Bind the archive SHA-256 and an exact per-file inventory; reject links/path
escapes and rehash the extracted model before every phase and serving arm.

Alternatives considered:

- retry the unreachable Hugging Face route during paid rental time;
- add a proxy, model mirror service, OSS dependency, or another cloud product;
- change the model, revision, format, source pin, or dependency lock;
- mutate attempt 005 or populate its cache after the sealed failure.

Evidence:

The attempt-005 logs and install reports retain successful paired wheel builds,
paired dependency-identical installs, and CUDA self-checks. Its traceback ends
in `httpcore.ConnectError: [Errno 101] Network is unreachable` while listing the
fixed revision. The remote and off-host failure seals verify.

Consequences:

G0 remains `roadmap`. Model staging proves no runtime mechanism. G0-C-012 may
start only from its committed runner, frozen archive/inventory hashes, and a new
attempt ID. Success still requires controls, paired serving, final sealing,
off-host verification, and independent Gate review. G1 remains blocked.

Reopen condition:

Reopen if the staged archive cannot reproduce the exact fixed snapshot, if any
phase can use network/model bytes outside it, or if transport changes the
paired-serving protocol.

Affected documents and experiments:

`DECISIONS.md`, `../experiments/g0/RESULTS.md`,
`../experiments/g0/SPEC.g0-c-011.md`, `../experiments/g0/SPEC.g0-c-012.md`, and
the G0-C-012 execution bundle.

## 2026-08-20 — D027: Preserve G0-C-012 and capture expected RED in G0-C-013

Status: accepted

Context:

G0-C-012 attempt 001 completed admission and entered command 21. Identity and
model revalidation passed. The stock oracle then produced exactly the required
exit 1, 27 tests, and 27 failures, but the inherited Bash `ERR` trap fired at
the oracle command before `stock_status=$?` ran. `set +e` disables `errexit`; it
does not disable an `ERR` trap. No treatment control or server started.

Decision:

Preserve 012 and attempt 001 unchanged. Freeze G0-C-013 with every experimental
input and check unchanged. Replace only the stock-oracle status capture with an
`if` condition, where Bash suppresses `ERR` for the expected nonzero command,
and retain the exact exit/output assertions afterward. All unexpected command
failures keep the existing trap.

Alternatives considered:

- remove or globally disable the `ERR` trap during all controls;
- accept 012/001 manually or resume its sealed phase directory;
- change the oracle to return zero on stock or ignore its status;
- add a generic command runner abstraction for one expected failure.

Evidence:

The sealed 012/001 status records `INVALID_SCOPE` at command 21 line 57. Its
`stock-oracle.txt` ends with `Ran 27 tests` and `FAILED (failures=27)`; treatment
and installed-seam artifacts are absent. A local counterexample requires the
stock command to be an `if` condition and rejects the former `set +e` pattern.

Consequences:

G0 remains `roadmap`; 012/001 is not a Gate result. G0-C-013 requires a fresh
attempt and the full unchanged admission/controls/serving/final sequence. G1
remains blocked.

Reopen condition:

Reopen if the conditional capture suppresses any non-stock failure, changes the
expected RED assertions, or command 21 cannot reach treatment controls.

Affected documents and experiments:

`DECISIONS.md`, `../experiments/g0/RESULTS.md`,
`../experiments/g0/SPEC.g0-c-012.md`, `../experiments/g0/SPEC.g0-c-013.md`, and
the G0-C-013 execution bundle.

## 2026-08-20 — D028: Preserve G0-C-013 and read Python source BOMs in G0-C-014

Status: accepted

Context:

G0-C-013 attempt 001 completed admission and entered command 21. The stock
oracle produced the required 27/27 RED, the treatment oracle produced 27/27
GREEN, and the installed seam passed. The following full-tree AST inventory
decoded every Python file as plain `utf-8`; an unrelated upstream source file
begins with a legal UTF-8 BOM, so `ast.parse` rejected the retained U+FEFF. The
attempt sealed `INVALID_SCOPE` before either server started.

Decision:

Preserve 013 and attempt 001 unchanged. Freeze G0-C-014 with every experimental
input and check unchanged except for a successor-specific inventory reader
using `utf-8-sig`. Retain parsing of every Python file and the exact zero
production caller, one backend call, and zero dynamic-route assertions.

Alternatives considered:

- skip the BOM-bearing file or ignore inventory parse errors;
- normalize or rewrite the fixed upstream source archive;
- mutate the shared 013 inventory helper and rerun the sealed attempt;
- add generic encoding detection or fallback logic.

Evidence:

The sealed 013/001 artifacts include the exact stock/treatment oracle and
installed-seam terminals, followed by `INVALID_SCOPE` at command 21 line 81.
The failing path begins with bytes `EF BB BF`. A local counterexample reproduces
the failure with plain `utf-8` and passes with the one-line `utf-8-sig` change
while retaining the exact call-site assertions.

Consequences:

G0 remains `roadmap`; 013/001 is not a Gate result. G0-C-014 requires a fresh
attempt and the full unchanged admission/controls/serving/final sequence. G1
remains blocked.

Reopen condition:

Reopen if `utf-8-sig` changes non-BOM UTF-8 parsing, any source file is skipped,
an AST failure is suppressed, or the inventory call-site assertions change.

Affected documents and experiments:

`DECISIONS.md`, `../experiments/g0/RESULTS.md`,
`../experiments/g0/SPEC.g0-c-013.md`, `../experiments/g0/SPEC.g0-c-014.md`, and
the G0-C-014 execution bundle.

## 2026-08-20 — D029: Preserve G0-C-014 and admit Ninja in G0-C-015

Status: accepted

Context:

G0-C-014 attempt 001 completed admission and every command 21 control. Command
22 started stock, loaded the fixed model, and allocated the fixed KV cache.
FlashInfer's first CUDA JIT then tried to execute `ninja`, which command 19 had
not installed and command 20 had not admitted. The scheduler failed before
health; cleanup left no process-group or attributable GPU PID survivor. No
request or treatment arm ran.

Decision:

Preserve 014 and attempt 001 unchanged. Freeze G0-C-015 with every experimental
input, control, and server parameter unchanged. Add Ubuntu `ninja-build` only
to the existing ordinary project-prerequisite installer, require `ninja` in
preflight, and retain `ninja --version` in the sealed environment readback.

Alternatives considered:

- change the attention backend or disable prefill CUDA graphs;
- install Ninja manually without a frozen admission requirement;
- reuse the sealed 014 environments or resume command 22;
- treat the supervisor's cleanup SIGKILL status as a GPU OOM.

Evidence:

The sealed 014/001 stock log shows model load and KV-cache allocation followed
by `FileNotFoundError: ninja` inside FlashInfer JIT. The server never reached
health. Kernel logs contain no OOM event, and cleanup records no surviving
listener, process-group member, or attributable GPU PID. The local successor
verifier requires install, admission, and version readback of Ninja.

Consequences:

G0 remains `roadmap`; 014/001 is not a Gate result. G0-C-015 requires a fresh
attempt and the full unchanged admission/controls/serving/final sequence. The
provider GPU driver/CUDA image remains reused and G1 remains blocked.

Reopen condition:

Reopen if Ninja is not sufficient for the fixed FlashInfer JIT path, installing
it changes dependency resolution, or a server/backend parameter must change.

Affected documents and experiments:

`DECISIONS.md`, `../experiments/g0/RESULTS.md`,
`../experiments/g0/SPEC.g0-c-014.md`, `../experiments/g0/SPEC.g0-c-015.md`, and
the G0-C-015 execution bundle.

## 2026-08-21 — D030: Preserve G0-C-015 and capture attributed shutdown in G0-C-016

Status: accepted

Context:

G0-C-015 attempt 001 completed admission and every control. Stock passed its
FlashInfer CUDA JIT, reached health, and completed both frozen streaming
requests. The runner then sent SIGTERM. This fixed SGLang revision terminated a
child, entered logged SIGQUIT cleanup, and self-killed with wait status 137.
No process-group member, listener, or attributable GPU PID survived. The active
Bash `ERR` trap intercepted the old `set +e; wait` before cleanup receipt
creation, so treatment never ran.

Decision:

Preserve 015 and attempt 001 unchanged. Freeze G0-C-016 with all experimental
inputs, controls, server parameters, requests, and cleanup invariants unchanged.
Before TERM, require the server PID to be alive; require process-group TERM to
succeed; capture `wait` as an `if` condition; accept the fixed runtime's
observed 137 alongside 0/143 only when every no-survivor check passes, both
when writing the cleanup receipt and during final evidence verification.

Alternatives considered:

- accept every 137 without proving signal attribution or cleanup;
- require only 0/143 despite the fixed runtime's observed self-kill path;
- patch SGLang's shutdown behavior or add a server wrapper;
- resume the sealed 015 attempt at treatment.

Evidence:

Both 015/001 stock request JSON files record `passed: true`. The log records
health 200, both generate 200 responses, runner-timed SIGTERM, child -15,
SIGQUIT cleanup, and `kill_process_tree`; the seal records line 200 and exit
137. Process-group, listener, and attributable GPU survivor files are empty.
A local counterexample rejects `set +e; wait` and requires conditional capture,
live-PID/TERM ordering, status 137, and all inherited cleanup evidence.

Consequences:

G0 remains `roadmap`; 015/001 is not a Gate result. G0-C-016 requires a fresh
full attempt. No physical demotion, allocator, correctness, or performance
claim is promoted, and G1 remains blocked.

Reopen condition:

Reopen if 137 occurs without successful runner-issued TERM, any cleanup
survivor remains, the fixed runtime changes its shutdown behavior, or another
server/request parameter must change.

Affected documents and experiments:

`DECISIONS.md`, `../experiments/g0/RESULTS.md`,
`../experiments/g0/SPEC.g0-c-015.md`, `../experiments/g0/SPEC.g0-c-016.md`, and
the G0-C-016 execution bundle.

## 2026-08-21 — D031: Preserve G0-C-016 and wait for joint cleanup quiescence in G0-C-017

Status: accepted

Context:

G0-C-016 attempt 001 was deliberately interrupted and sealed without residue.
Attempt 002 completed admission, every control, and both requests in both arms.
Both server groups received runner-issued TERM and reaped with the attributed
status 137. Stock cleanup passed. For treatment, the group and attributable GPU
PID were gone while the immediately sampled `ss` output still contained an
unowned port-30001 listener; a later residual probe found no listener. The 016
runner waited only for the process group before sampling all cleanup evidence.

Decision:

Preserve 016 and both attempts unchanged. Freeze G0-C-017 with the same source,
model, dependencies, controls, server parameters, requests, receipt schema,
and 60-second cleanup deadline. Inside that deadline, resample process-group,
target-listener, and attributable-GPU state until all three are jointly
quiescent, then retain the final snapshots. Any survivor at the deadline still
fails closed. Reuse the immutable 016 pin, input inventories, helpers,
prerequisite installer, and evidence verifier instead of duplicating them.

Alternatives considered:

- accept 016/002 from the later ad hoc residual probe;
- ignore listener evidence when the process group is gone;
- add a fixed sleep before the existing one-shot snapshot;
- add a generic retry/supervisor framework or patch SGLang shutdown;
- resume or rewrite the sealed 016 attempt.

Evidence:

Both treatment request JSON files record `passed: true`, including 48 cached
tokens on the second request. The cleanup receipt records no process-group or
GPU survivor and status 137, while the same-timestamp listener snapshot alone
contains port 30001 without a process owner. The remote failure seal and
off-host copy both verify. The 017 bundle executes the production cleanup
function against transient-listener and permanent-listener counterexamples.

Consequences:

G0 remains `roadmap`; 016/002 is not a Gate result. G0-C-017 requires a fresh
full attempt and off-host verification. No physical demotion, allocator,
correctness, recovery, or performance claim is promoted, and G1 remains
blocked.

Reopen condition:

Reopen if joint quiescence exceeds the existing deadline, a final snapshot
retains any process/listener/GPU survivor, the new counterexamples admit a
permanent listener, or another experimental input must change.

Affected documents and experiments:

`DECISIONS.md`, `../experiments/g0/RESULTS.md`,
`../experiments/g0/SPEC.g0-c-016.md`, `../experiments/g0/SPEC.g0-c-017.md`, and
the G0-C-017 execution bundle.

## 2026-08-21 — D032: Accept G0-C-017 successor PASS and authorize G1 planning only

Status: accepted

Context:

G0-C-017 attempt 001 completed the frozen protocol on the admitted Alibaba
Cloud A10 host. Remote and off-host semantic verification and seal verification
passed. A fresh independent review checked attempt identity, immutable
protocol inputs, wheel provenance, source oracles, installed seam behavior,
static inventory, both CUDA serving arms, and cleanup evidence, then selected
`PASS` with no Gate blocker.

Decision:

Accept G0-C-017/001 as the successor G0 `PASS`, replacing the historical
accepted `RESHAPE` while preserving all earlier specifications and attempts.
Classify only the fixed package and ordinary-serving integration finding as
`experimentally validated`; keep the overall ToolGap project `roadmap`.
Authorize preparation and review of a separate G1 plan and frozen SPEC. Do not
authorize G1 execution through this decision.

Alternatives considered:

- retain `RESHAPE` despite the completed independently reviewed successor;
- promote G0 to proof of physical demotion or allocator-visible reclamation;
- start G1 execution directly from the G0 result;
- rewrite the immutable completion receipt after independent review;
- add a new Gate or generalized experiment framework.

Evidence:

The exact frozen source oracle produced 27/27 stock RED and 27/27 treatment
GREEN. The installed treatment cache surface returned `UNSUPPORTED_BACKEND`,
released target priority, and made zero physical `demote` calls. Both stock and
treatment wheels completed health plus two native streaming requests on the
A10; all four requests returned HTTP 200 and each second request reported 48
device-cached tokens. Both attributed shutdowns left no process-group, target
listener, or GPU survivor. The two prescribed off-host verifiers exited zero,
and the independent reviewer recomputed the completion bindings.

Consequences:

G0 is closed. The allowed narrow claim is limited to the exact frozen source,
patch, wheels, dependency lock, model, and host. No physical demotion,
allocator-visible headroom, output equality, lifecycle/recovery behavior,
latency/throughput/capacity gain, upstream acceptance, or general compatibility
is proven. G1 may now be specified but remains unauthorized for execution.

Reopen condition:

Reopen G0 if the fixed package identity cannot be reproduced, the registered
seam ceases to fail closed, an accepted source-contract mapping is falsified,
or the G0 integration claim requires a changed causal input.

Affected documents and experiments:

`DECISIONS.md`, `ROADMAP.md`, `README.md`,
`../experiments/g0/RESULTS.md`, `../experiments/g0/SPEC.g0-c-017.md`, and
`../experiments/g0/artifacts/g0-c-017-independent-review.md`.

## 2026-08-21 — D033: Reject mainline data-plane expansion; admit PD transfer slice as future review and checksum round-trip as an instrument option

Status: accepted

Context:

A job-description-driven capability review asked whether ToolGap should absorb
distributed KV-store data-plane features — automatic large-value slicing with
concurrent multi-node reads and writes, full-path zero-copy with GPUDirect,
small-object coalescing for prefill-to-decode KV transfer, and end-to-end
iterative CRC verification. These features match an existing mature
distributed KV cache store's feature set. At review time G0 had just closed
with a successor PASS (D032); G1 is specified for planning only, so the
project holds no physical demotion, allocator, recovery, or performance
evidence yet, and a limited rented-machine budget (at most five hosts) is
available.

Decision:

Reject adding any of these data-plane capabilities to the G0-G4 mainline;
`PROJECT.md` non-goals (no new KV storage or transfer engine; no distributed,
multi-node, or RDMA claims) remain unchanged. Admit
`docs/future/PD_TRANSFER_SLICE.md` as a future review artifact for a narrow
prefill-to-decode transfer lifecycle slice on a reused transport, gated on a
real G1 physical-demotion PASS and expected to live outside the mainline
repository. Record page-level checksum round-trip verification
(demote-time per-page checksum, restore-time per-page self-check plus
whole-payload check) as one admissible instrument choice for the G1/G2 SPEC
authors when they design output-equivalence and corruption evidence; this is
an instrument option, not a new Gate requirement and not a data plane. Direct
the rented-machine budget first to G1-G4 real-GPU execution.

Alternatives considered:

- absorb value slicing, zero-copy/GPUDirect, and a distributed CRC-verified
  store into the mainline: rejected as rebuilding a mature data plane,
  violating the ownership boundary and diluting the narrow contract;
- start the PD transfer extension now, before G1: rejected because the
  mainline's real-CUDA evidence gap is the scarcer risk and shares the same
  budget;
- claim RDMA/GDR capability from commodity rented hosts: rejected; claim
  language must name the actually measured transport;
- make the checksum round-trip a mandatory new G2 artifact: rejected to keep
  Gate requirements owned by their own frozen SPECs.

Evidence:

`PROJECT.md` Section 6 already excludes new transfer engines and distributed,
multi-node, RDMA, and production-scale claims. D032 fixes the current state:
G0 closed, G1 unexecuted, no physical or performance evidence. The referenced
feature list is the published capability set of an existing mature store, so
re-implementation would duplicate a dependency-owned data plane rather than
close a demonstrated contract gap. No experimental evidence is created or
promoted by this decision; every affected claim remains `roadmap`.

Consequences:

The mainline scope is unchanged. `ROADMAP.md` gains a future-review pointer
for the PD transfer slice parallel to the prefetch pointer. G1/G2 SPEC
authors may adopt or decline the checksum instrument without reopening this
decision. Any future PD transfer claim must satisfy the admission,
hardware-honesty, and deletion tests in `future/PD_TRANSFER_SLICE.md`.

Reopen condition:

Reopen if G1-G4 evidence shows the mainline itself needs a transfer-path
mechanism to close its contract, if the upstream dependency's ownership of
the physical data plane changes, or if the future review's admission
preconditions are shown to be unsatisfiable on obtainable hardware.

Affected documents and experiments:

`DECISIONS.md`, `ROADMAP.md`, `future/PD_TRANSFER_SLICE.md`, and
`../worklog/reviews/2026-08-21/data-plane-scope-review.md`.

## 2026-08-22 — D034: Qualify `write_through` as a causal reference and require a stock-policy challenge

Status: accepted

Context:

G0 selected `write_through` because its settled Full Host duplicate provides an
auditable committed-copy predicate. That source-semantic choice isolates later
release-only and checked-reclamation actions, but it does not establish the
best production Host-write policy. The fixed substrate also exposes
`write_through_selective` and `write_back`, whose Publication timing and cost
can change the end-to-end result.

Decision:

Use `write_through` only as the qualification/reference mode for G1, G2, and
the first G3 causal comparison. In that comparison, release-only and checked
reclamation reuse the same committed Host copy; the checked-reclamation action
must not receive a different Publication history. Before making a
production-grade optimization claim, challenge the candidate on the same
workload and joint SLO against tuned stock `write_through_selective` and
`write_back`. If checked reclamation wins only against the same-Publication
reference but not the best stock policy, retain only the mechanism result.

ToolGap-triggered on-demand Publication may be reviewed only after measurement
shows that eager Publication is the decisive cost and an independent accepted
contract defines its behavior. This decision does not authorize that mechanism.

Alternatives considered:

- treat the G0 `write_through` choice as a production-optimal policy;
- compare release-only and checked reclamation with different Host-copy
  histories;
- claim end-to-end value after beating only the same-Publication reference;
- add on-demand Publication now to make the candidate look stronger.

Evidence:

`experiments/g0/artifacts/host-mode-selection.md` supports only the committed
Host-copy source semantics and explicitly rejects a runtime conclusion. D004
and `EVALUATION.md` already require a same-copy release-only causal baseline.
There is no ToolGap runtime, Publication-cost, or performance evidence.

Consequences:

`EVALUATION.md` owns the two-level baseline protocol. G1/G2 mechanism and
correctness work remains isolated from production-policy tuning, while any
later production claim must survive the strongest measured stock policy. The
project claim remains `roadmap`.

Reopen condition:

Reopen if fixed-pin source or runtime evidence invalidates the committed-copy
semantics, shows that a named stock policy cannot be configured fairly, or
measures eager Publication as a decisive cost worthy of a separate contract
review.

Affected documents and experiments:

`DECISIONS.md`, `EVALUATION.md`,
`../worklog/plans/2026-08-22/write-policy-scope-decision.md`, and
`../worklog/reviews/2026-08-22/write-policy-scope-steelman-review.md`.

## 2026-08-22 — D035: Reject general Demote Pacing as the default; admit one measurement-driven conditional optimization series

Status: accepted

Context:

Fixed pin plus `write_through` spans three distinct costs that a generic
"Demote Pacing" label would conflate: earlier Publication, tool-gap-triggered
checked reclamation, and later Recovery. G0 provides only source/package and
ordinary-serving integration evidence; no current artifact identifies any of
these stages as a performance bottleneck.

Decision:

Keep the stages explicit:

1. **Publication:** the earlier HBM-to-Host D2H and Host commit;
2. **checked reclamation:** after the tool gap, reuse that committed Host copy
   and call the existing checked demote path to release the device value/HBM;
   do not presume this stage performs D2H;
3. **Recovery:** on resume, restore Host-to-HBM or recompute.

The G1-G4 mainline question remains whether tool-gap-triggered immediate checked
reclamation creates allocator headroom earlier than target session-priority
release plus stock eviction and thereby increases maximum sustainable arrival
rate under the joint SLO. G1 and G2 establish mechanism and correctness, not a
performance win.

Reject general Demote Pacing as a default implementation. Do not add a
`PacingController`, public pacing parameters, a Gate, or a module. During G3 or
G4, only a reproducible stage-attributed symptom may occupy one conditional
optimization slot, and only one series may be active:

- if per-node final checks, release, or free-drain in checked reclamation is
  measured as scheduler, CPU, or allocator interference, a later SPEC revision
  may consider candidate-owned **Checked Reclamation Chunking**. It may apply a
  node/byte budget per scheduler cycle and stop after the required headroom is
  reached. Resume may cancel only chunks not yet started; already released
  content follows normal restore/recompute. Admission requires an ablation,
  deletion test, and losing workload. This is not a current implementation;
- if eager Publication D2H or Host occupancy is decisive, only an independent
  review may admit **Tool-gap-triggered On-demand Publication with Pacing**;
  D035 does not authorize it;
- if Recovery/H2D is decisive, verify the fixed-pin restore path first. A
  profile-justified narrow upstream layer-wise/substrate patch must be shared
  by baseline and candidate arms and is not a ToolGap differential;
- event-driven completion regains candidate status only if polling wait is
  measured on the critical path;
- slicing, coalescing, concurrent channels, and PD transfer remain in
  `future/PD_TRANSFER_SLICE.md`; L3 and prefetch remain outside the mainline;
- a dynamic selector remains blocked until G5 admission.

If there is no reproducible bottleneck, implement no additional optimization
patch. No memcpy bandwidth, release-rate, or microbenchmark result can win by
itself: the same workload must close action -> mediator -> joint endpoint, with
realized KV-pool pressure and fair sharing of any two-arm substrate patch.

Alternatives considered:

- implement a general pacing framework before a measured symptom;
- pace all three stages under one controller;
- run multiple optimization series in parallel;
- treat chunking, on-demand Publication, layer-wise restore, event completion,
  PD transfer, L3, prefetch, or policy as one bundled optimization;
- infer a performance win from bandwidth or reclamation microbenchmarks.

Evidence:

The fixed G0 patch defines a call to existing demote only after checking a
committed Host duplicate; it does not establish a new D2H in checked
reclamation. The accepted evaluation contract already requires
allocator-visible headroom and a joint-SLO endpoint. The PR5 PD-transfer and
restore reviews preserve separate-scope and preflight conclusions, but no prior
accepted decision authorizes general Demote Pacing. All performance claims
remain `roadmap`.

Consequences:

`ROADMAP.md` keeps the existing conditional diagnosis outside Gate order;
`engineering/PERFORMANCE_ENGINEERING.md` owns stage attribution and one-series
admission; `EVALUATION.md` owns fairness, pressure, reachability, and endpoint
proof. No runtime work is authorized.

Reopen condition:

Reopen only from a reproducible G3/G4 symptom with stage attribution and a
small discriminating experiment, or after G5 independently admits a selector.
The reopen record must identify the one selected series, SPEC revision,
ablation, deletion test, losing workload, and fair arm treatment.

Affected documents and experiments:

`DECISIONS.md`, `ROADMAP.md`, `EVALUATION.md`,
`engineering/PERFORMANCE_ENGINEERING.md`,
`../worklog/plans/2026-08-22/bottom-optimization-route-landing.md`, and
`../worklog/reviews/2026-08-22/bottom-optimization-route-reshape.md`.

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
