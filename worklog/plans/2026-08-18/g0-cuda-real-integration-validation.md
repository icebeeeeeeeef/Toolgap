# G0 CUDA real-integration validation plan

> Status: superseded by
> [`g0-cuda-real-integration-validation-v2.md`](g0-cuda-real-integration-validation-v2.md)
> after Steelman review on 2026-08-18. Do not freeze or execute this revision.
>
> Claim state: `roadmap`
>
> Date: 2026-08-18

> **For agentic workers:** REQUIRED SUB-SKILL: use `executing-plans` after the
> owner accepts this plan. Execute the tasks in order; do not start G1 from an
> intermediate success.

**Goal:** Decide whether the reviewed atomic checked-demote contract can exist
as a reproducible, real SGLang integration on one frozen CUDA host, while
keeping physical reclamation and allocator measurements out of G0.

**Architecture:** Start with an exact source state and the retained four-file
atomic patch. Run the existing source-contract oracle in both stock and
treatment arms, then prove that the treatment can build, import, start HiCache,
and serve one ordinary request on the declared CUDA host. The test never invokes
`checked_demote_session`; G1 alone owns an actual physical-demotion invocation.

**Tech stack:** SGLang HiCache `UnifiedRadixCache`, Python TreeCore,
`write_through` Host mode, Python 3.12, PyTorch/CUDA, Qwen2.5-0.5B-Instruct,
Ubuntu x86_64 with one NVIDIA GPU.

---

## 1. Why this is a successor G0 rather than G1

The sealed `G0-C-ATOMIC-006` run proves a narrow source contract with 27
registered fake-resource counterexamples. It does not import the real physical
path or run a real engine. The new run therefore asks only:

> Does an exact SGLang source state containing the reviewed atomic contract
> build and expose the intended cache/backend seam on the frozen CUDA host,
> without changing the ordinary serving path?

It must not measure allocator pages, time-to-headroom, resumed latency,
throughput, output equivalence after demotion, cancellation, or recovery. Those
are G1 or later work.

## 2. Decision contract

### PASS — unlocks only G1 planning

All of the following hold in the same frozen treatment source state:

1. base commit, applied patch or merge commit, resulting tree, dependency
   resolution, model revision, flags, and testbed identity are recorded;
2. the stock checkout produces the registered contract RED result and the
   treatment produces 27/27 GREEN with the retained oracle;
3. the installed treatment package imports the four changed surfaces and the
   fixed `launch_server` configuration reaches the version-matched `/health`
   endpoint;
4. one native `/generate` request with a frozen text payload and deterministic
   sampling completes in both stock and treatment arms; and
5. a treatment-source call-site inventory shows no production request-path
   caller of `checked_demote_session`; therefore the serving smoke cannot enter
   its sole backend sub-step, `demote_session_checked`.

The supported conclusion is only: the reviewed seam is a real, buildable
SGLang integration on this exact single-node environment. The project remains
`roadmap`; no physical-reclamation or performance claim is promoted.

### RESHAPE

Take `RESHAPE` if the source-level oracle remains valid but the contract cannot
be built, imported, registered, or launched without widening ownership beyond
the four audited files. Preserve the failing source state and logs. A change to
the pin, patch, flags, oracle, or configuration requires a new immutable G0
revision.

### STOP

Take `STOP` if the real integration requires a second physical index/data plane,
replacement allocator or cache tree, public pause API, background retry worker,
or candidate-owned physical demotion implementation.

### Invalid or blocked attempt

Treat an unavailable host, missing model artifact, dependency/build failure
before either arm begins, or incomplete raw evidence as `BLOCKED_BEFORE_EXECUTION`
or invalid evidence. Do not call it a PASS, a null result, or a G1 authorization.
If a serving smoke unexpectedly invokes `checked_demote_session`, terminate the
run, retain the logs, and mark the attempt invalid for this G0 contract because
it crossed into G1 without an authorized physical-mechanism specification. A
stock-owned `demote` call by an unrelated HiCache/eviction path is not such a
violation; it must be retained and labelled separately.

## 3. Required files when the plan is authorized

These files are not created by this planning record. They are the smallest
future execution bundle:

```text
upstream/sglang/
  pin.toml
  patches/0001-atomic-checked-demote.patch     # only if no upstream commit
  tests/test_g0_atomic_checked_demote.py

experiments/g0/
  SPEC.g0-c-007.md
  manifest.g0-c-007.json
  commands/20-g0-c-007-preflight.sh
  commands/21-g0-c-007-contract-arms.sh
  commands/22-g0-c-007-serving-smoke.sh
  commands/23-g0-c-007-verify.sh
  artifacts/g0-c-007-*.txt|json|log
  RESULTS.g0-c-007.md
```

`RESULTS.md` remains the index of the original `RESHAPE` evidence. The successor
result is a new file and links back to it; historical G0-C-001 through 006
artifacts are never rewritten.

## 4. Task 1 — admit one exact treatment source state before renting a GPU

**Files:**

- Read: `experiments/g0/artifacts/sglang-session-atomic-checked-demote-v5.patch`
- Read: `experiments/g0/artifacts/test_atomic_checked_demote_contract_v6.py`
- Create after admission: `upstream/sglang/pin.toml`
- Create after admission: `upstream/sglang/patches/0001-atomic-checked-demote.patch`

- [ ] Create two clean SGLang worktrees from base commit
  `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`: `stock` is unmodified and
  `treatment` receives the retained patch with SHA-256
  `e69776678909b4ee49b1c0fa4a8e208666893b659c0508387c83fcdf11e82a9a`.
- [ ] Run `git apply --check` before applying the patch, then record the base
  commit/tree and treatment commit/tree. Reject a patch that applies with fuzz
  or requires edits outside `session_ref_tracker.py`, `unified_tree_core.py`,
  `unified_tree_core_interface.py`, and `unified_radix_cache.py`.
- [ ] Run the existing v6 source-contract oracle against both worktrees. The
  stock arm must retain RED; the treatment arm must retain all 27 GREEN cases.
- [ ] Have an independent reviewer check the final treatment diff against the
  ownership boundary: one cache caller; final live checks and existing
  `demote` in one backend call; cache-owned free drain; no second index, public
  API, worker, physical algorithm, allocator, or movement path.
- [ ] Choose exactly one reproducibility form:

  - **Merged form:** record an upstream commit hash and tree containing the
    reviewed contract.
  - **Experimental-patch form:** record the fixed base commit/tree, exact patch
    SHA-256, resulting treatment commit/tree, and reviewer decision. Label the
    outcome `experimental integration`; do not claim upstream acceptance.

Do not rent a GPU until one form is selected and its review passes. An upstream
public merge is valuable evidence but is not required unless the successor G0
SPEC explicitly makes it a prerequisite.

## 5. Task 2 — preregister G0-C-ATOMIC-007 before any CUDA treatment runs

**Files:**

- Create: `experiments/g0/SPEC.g0-c-007.md`
- Create: `experiments/g0/manifest.g0-c-007.json`
- Create: `experiments/g0/commands/20-g0-c-007-preflight.sh`
- Create: `experiments/g0/commands/21-g0-c-007-contract-arms.sh`
- Create: `experiments/g0/commands/22-g0-c-007-serving-smoke.sh`
- Create: `experiments/g0/commands/23-g0-c-007-verify.sh`

- [ ] Copy the decision contract in section 2 verbatim into the successor SPEC,
  including the explicit G1 exclusion and invalid-attempt rule.
- [ ] Freeze the following exact treatment and stock identities in the manifest:
  base commit/tree; treatment commit/tree; patch hash or merged commit; Python,
  SGLang, PyTorch, Transformers, CUDA and driver versions; resolved package
  lock or full `pip freeze`; model/tokenizer revision; all launch flags; and
  every command/artifact path.
- [ ] Freeze the existing configuration unless an owner-approved source change
  requires a new choice: Python TreeCore, `write_through`, bfloat16 model/KV,
  page size 16, context and max tokens 4096, static memory fraction 0.70,
  HiCache ratio 2.0, kernel I/O, page-first layout, TP=DP=1, FCFS, seed
  `20260817`, session radix enabled, streaming disabled, and no L3 backend.
- [ ] Freeze one serving-smoke request for both arms:

  ```json
  {
    "text": "Reply with exactly: ok",
    "sampling_params": {"temperature": 0.0, "max_new_tokens": 4}
  }
  ```

  The request validates ordinary `/generate` serving only. Its response must
  have a successful terminal response and must not be interpreted as a
  demotion, correctness-after-restore, or performance result.
- [ ] Make `upstream/sglang/tests/test_g0_atomic_checked_demote.py` an
  installed-package test, not another extracted-method oracle. It imports
  `SessionPriorityRelease`, `SessionDemoteExecution`,
  `SessionCheckedDemoteOutcome`, and `UnifiedRadixCache.checked_demote_session`
  from the selected treatment checkout, asserts their declared constructor or
  method signatures, and performs no physical-demote call. Its fixed execution
  command is:

  ```bash
  PYTHONPATH="$TREATMENT/python" python3.12 -m pytest \
    upstream/sglang/tests/test_g0_atomic_checked_demote.py -q
  ```

  The expected treatment terminal is PASS. This separates package/import
  compatibility from the retained fake-resource contract oracle.
- [ ] Checksum-link the SPEC into the manifest before executing the stock or
  treatment CUDA arm. Seal each generated artifact with size and SHA-256.

## 6. Task 3 — prepare the leased host without consuming treatment evidence

**Files:**

- Generate: `experiments/g0/artifacts/g0-c-007-environment.txt`
- Generate: `experiments/g0/artifacts/g0-c-007-package-lock.txt`
- Generate: `experiments/g0/artifacts/g0-c-007-model-identity.txt`

- [ ] Use one Ubuntu x86_64 NVIDIA host. The initial target is one A10 24 GB
  GPU, matching G0-C-006; a different host requires a new frozen environment
  entry before either arm runs.
- [ ] Before starting either arm, capture `uname -a`, `nvidia-smi` GPU UUID,
  driver, total memory, Python version, compiler/build readbacks, package lock,
  available disk, and the model/tokenizer revision. The manifest records the
  observed values, not only planned values.
- [ ] Acquire the model and dependencies before the paired arms begin. If this
  fails, retain the output as a blocked preflight; do not switch versions or
  flags inside the same run identity.
- [ ] Verify that `curl http://127.0.0.1:<port>/health` and the native
  `/generate` request shape are defined by the selected SGLang source. The
  fixed source exposes both endpoints; repeat this check against the selected
  exact treatment source.

The cost-control rule is simple: do source review, patch hashing, and artifact
layout before allocating the GPU; once the host is leased, run the frozen paired
arms and stop the host after logs and artifacts are copied out. No exploratory
parameter sweep is permitted.

## 7. Task 4 — execute the paired G0 runtime-integration arms

**Files:**

- Generate: `experiments/g0/artifacts/g0-c-007-stock-contract.txt`
- Generate: `experiments/g0/artifacts/g0-c-007-treatment-contract.txt`
- Generate: `experiments/g0/artifacts/g0-c-007-stock-server.log`
- Generate: `experiments/g0/artifacts/g0-c-007-treatment-server.log`
- Generate: `experiments/g0/artifacts/g0-c-007-stock-smoke.json`
- Generate: `experiments/g0/artifacts/g0-c-007-treatment-smoke.json`
- Generate: `experiments/g0/artifacts/g0-c-007-source-identity.txt`

- [ ] Run the registered v6 oracle in the installed stock environment. Record
  its expected RED terminal separately from the server smoke; a failing oracle
  is the stock contract baseline, not a failed GPU environment.
- [ ] Launch stock HiCache on port 30000 with the frozen configuration. Poll
  `/health`, submit the frozen native `/generate` payload, capture the terminal
  JSON and full server log, then shut down cleanly.
- [ ] Run the same v6 oracle in the installed treatment environment. It must
  produce 27/27 GREEN before the treatment server is launched.
- [ ] Run the frozen installed-package test command from Task 2 against the
  treatment checkout and retain its terminal. A pass proves the selected
  runtime environment imports the four changed surfaces without the oracle's
  dependency stubs; it does not prove physical reclamation.
- [ ] Launch treatment HiCache on port 30001 with every non-port flag identical
  to stock. Poll `/health`, submit the identical payload, capture terminal JSON
  and full log, then shut down cleanly.
- [ ] Before either server starts, retain a treatment-source call-site inventory
  proving that `checked_demote_session` has no production request-path caller
  and that its only backend sub-step is `demote_session_checked`. Do not infer
  the absence of all `demote` calls from server logs: ordinary stock HiCache or
  eviction paths may legitimately use that existing primitive. Record any such
  stock-owned event separately; only a candidate checked-session invocation is
  a G0 scope violation.
- [ ] Record every arm's start/end time, exit status, process ID, port, failure
  class, and artifact checksums. A server startup failure after its arm begins
  remains a recorded arm failure; it may not be silently retried with changed
  dependencies or flags.

## 8. Task 5 — seal evidence and make the Gate decision

**Files:**

- Create: `experiments/g0/RESULTS.g0-c-007.md`
- Modify after decision: `experiments/g0/RESULTS.md` only to append a link to
  the successor result and preserve the prior `RESHAPE` record unchanged
- Modify after decision: `docs/DECISIONS.md` only if the Gate state or accepted
  source boundary changes

- [ ] Run the successor verifier. It checks the SPEC checksum, every manifest
  identity, source/patch tree hashes, command references, artifact size/hash,
  stock RED, treatment 27/27 GREEN, both endpoint terminals, and the static
  no-production-caller inventory for the candidate checked-session method.
- [ ] Perform a fresh review using only the sealed SPEC, source identities,
  treatment diff, commands, and artifacts. The reviewer decides whether each
  PASS condition actually holds; it does not rewrite the run.
- [ ] Publish `PASS`, `RESHAPE`, `STOP`, `BLOCKED_BEFORE_EXECUTION`, or invalid
  attempt exactly as the recorded evidence supports. Preserve every failed or
  blocked artifact.
- [ ] If and only if G0 passes, create a separate G1 plan and then a separate,
  frozen G1 SPEC for the quiescent private-tail physical-demotion experiment.
  Its primary terminal sequence begins at Host commit and ends at exact free
  drain plus allocator sample; it is not part of this run.

## 9. Completion checklist

This plan is complete only when a future executor can answer all of these
without inventing a configuration or widening scope:

- Which exact source state is stock, which is treatment, and how can each be
  reproduced?
- What does the successor G0 prove, and which tempting claims remain forbidden?
- Which paired runtime observations distinguish a buildable integration from a
  source-only fake-backend test?
- Which artifact makes a blocked or failed GPU attempt reviewable?
- What exact PASS result, and only that result, authorizes the separate G1
  physical-mechanism experiment?

## Canonical references

- [`docs/ROADMAP.md`](../../../docs/ROADMAP.md) — Gate order and G1 block;
- [`docs/DEMOTION_CONTRACT.md`](../../../docs/DEMOTION_CONTRACT.md) — safety and
  lifecycle invariants;
- [`docs/governance/EXPERIMENT_AND_EVIDENCE_SOP.md`](../../../docs/governance/EXPERIMENT_AND_EVIDENCE_SOP.md)
  — preregistration and evidence retention;
- [`experiments/g0/RESULTS.md`](../../../experiments/g0/RESULTS.md) — current
  G0 `RESHAPE` evidence;
- [`experiments/g0/SPEC.g0-c-006.md`](../../../experiments/g0/SPEC.g0-c-006.md)
  — frozen predecessor, retained without modification.
