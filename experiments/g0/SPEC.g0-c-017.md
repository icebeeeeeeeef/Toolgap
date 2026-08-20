# G0-C-ATOMIC-017 — staged-input CUDA package and serving integration

> Gate: G0
>
> Specification state: frozen before runtime execution
>
> Claim state: `roadmap`
>
> Revision: G0-C-ATOMIC-017
>
> Run identity: `g0-c-atomic-runtime-integration-017`

## 1. Revision reason

G0-C-ATOMIC-016 attempt 002 completed admission, every contract control, both
stock requests, and both treatment requests. Both arms received the runner's
SIGTERM, reaped with the attributed status 137, and left no process-group or GPU
PID survivor. Stock cleanup passed. During treatment cleanup the process group
disappeared before the kernel removed the unowned port-30001 listener entry;
the runner sampled that transient entry immediately, marked cleanup false, and
sealed `EXECUTION_FAILED_AFTER_START`. A later residual probe found no listener.

This revision preserves 016 and both attempts unchanged. It changes only the
existing 60-second cleanup convergence: the runner now waits for the process
group, target listener, and attributable GPU PID set to quiesce together before
taking the final snapshots. A listener that survives the same deadline still
fails closed. No oracle, input, server parameter, request, receipt schema,
claim boundary, or Gate result changes.

## 2. Decision question and claim ceiling

Can the reviewed four-file atomic checked-demote patch be installed as an exact
SGLang package, exercise its real cache-to-registered-backend fail-closed seam,
and coexist with ordinary HiCache serving on one frozen CUDA host?

This experiment does **not** invoke candidate physical `demote`, read allocator
capacity, compare model outputs, or establish lifecycle correctness, recovery,
or performance. A green protocol supports only an experimental integration on
the named source, wheels, dependency lock, model, and host. It remains
`roadmap` until independent review accepts a successor G0 Gate decision.

Physical completion and allocator-visible capacity remain G1 questions. A
successor G0 PASS may authorize a separate G1 plan and frozen SPEC; it does not
authorize G1 execution by itself.

## 3. Fixed source and ownership

Both arms use the SGLang remote, base commit, tree, model, and runtime target in
`upstream/sglang/pin.g0-c-016.toml`:

```text
base commit  92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2
base tree    25e9bf86d04c27fe380024d9c8c421c3b5b51f3c
patch SHA    e69776678909b4ee49b1c0fa4a8e208666893b659c0508387c83fcdf11e82a9a
seed SHA     2d40db92ff1a21cb78e95f4da98352f1fa17086e1a16a82e95070f05e1460400
model SHA    7831ff4149673415ff5adcb36630438b418d0c21092f230ed3b3176fc584edb8
```

The seed archive is a transport artifact, not a second source authority. It is
a portable archive of a shallow bare Git repository fetched from the named
remote at the fixed commit. Before either arm, command 20 requires its frozen
SHA-256, extracts it once, runs `git fsck`, proves the fixed commit and tree,
then makes independent stock and treatment clones. Each checkout resets its
`origin` readback to the canonical GitHub URL and must be clean at the fixed
identity. The runner never contacts GitHub for SGLang source.

The model archive is likewise a transport artifact, not a new model authority.
It contains the exact regular files downloaded from
`Qwen/Qwen2.5-0.5B-Instruct` revision
`c89bee90d9f811437d9735454613c35b4a3c4dc8`. Command 20 requires the frozen
archive SHA-256, rejects links and path escapes, extracts it once, and checks
the exact sorted file set, size, and SHA-256 of every file against
`experiments/g0/artifacts/model-files.g0-c-016.json`. Commands 21-23 rehash the
same files before their phase, and command 22 repeats that check before each
arm. Tokenizer and server loading use only this local path with Hugging Face and
Transformers offline modes enabled; the runner never contacts Hugging Face.

The treatment applies only
`upstream/sglang/patches/0001-atomic-checked-demote.patch` and may change only:

```text
python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py
python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py
python/sglang/srt/mem_cache/unified_cache/unified_tree_core_interface.py
python/sglang/srt/mem_cache/unified_radix_cache.py
```

ToolGap owns logical admissibility and the evidence protocol. SGLang continues
to own the physical KV tree, residency, allocator, movement, eviction, and model
execution. No second physical index, cache tree, allocator, worker, public pause
API, or dynamic tracing hook is admitted.

## 4. Environment admission and immutable identity

The experimental invariants are one physical NVIDIA A10 with 22–25 GiB, real
CUDA execution, the exact paired source/application stack, and identical
substrate for both arms. How the driver and CUDA toolkit were installed is not
part of the checked-demote question.

The admitted substrate is therefore Alibaba Cloud's official Ubuntu 24.04
NVIDIA GPU image on a `gn7i` instance. The recommended rental profile is
`ecs.gn7i-c16g1.4xlarge` (16 vCPU, 60 GiB, one 24 GiB A10), but CPU/RAM SKU is
recorded rather than treated as a causal invariant. On the purchase page,
select the preinstalled GPU image and do **not** also select the separate
automatic GPU-driver installation option.

Command `19-g0-c-016-project-prereqs.sh` may install only ordinary project build
tools absent from the image (`cargo`, `rustc`, C/C++ build tools, Git, curl,
Python venv support, and `ss`). It refuses to install or replace the NVIDIA
driver, CUDA, cuDNN, NCCL, Docker, or NVIDIA Container Toolkit. If the official
image lacks the required GPU substrate, stop this attempt rather than repairing
the host in place.

Command `20-g0-c-017-preflight.sh` runs before either arm and requires:

- Linux x86_64 and the official Alibaba Cloud Ubuntu 24.04 NVIDIA GPU image,
  proved through bounded IMDSv2 readback;
- exactly one NVIDIA A10 reporting 22–25 GiB, NVIDIA driver `>=580.65.06`,
  provider CUDA 13.0 at `/usr/local/cuda-13.0`, and Python `3.12.x`;
- installed Torch `2.13.0`, Torch CUDA `13.0`, Transformers `5.12.1`, one
  CUDA-visible A10, and a successful `torch.cuda.is_available()` readback in
  both isolated arm environments;
- GNU `timeout` plus Rust `>=1.92.0`, the minimum declared by the pinned
  SGLang dependency graph; exact `cargo` and `rustc` versions are retained;
- a committed ToolGap checkout with no tracked changes; its `HEAD` and
  `HEAD^{tree}` bind this SPEC, commands, helpers, pin, patch, oracle, installed
  test, inventory, and request;
- complete stock/treatment SGLang checkouts at the fixed base, with the exact
  patch applied without fuzz and no other changed path;
- the operator-staged source seed at the frozen SHA-256, with its path,
  expected/observed hashes, extraction log, Git integrity, and checkout
  identities retained;
- the operator-staged model seed at its frozen SHA-256, with a safe extraction
  log, canonical repository/revision receipt, and exact per-file inventory;
- package metadata at the fixed source location `python/pyproject.toml`;
- stock and treatment wheels built into the attempt directory, one resolved
  dependency lock, separate clean environments, and per-arm pip install reports;
- package provenance containing the absolute interpreter, expected environment
  root, package/module paths, and hashes of all four audited modules;
- the fixed local-only model/tokenizer snapshot and a tokenizer readback proving
  the request contains at least 32 input tokens.

The preflight establishes `/usr/local/cuda-13.0/bin` on its own `PATH` before
discovering required commands, then proves that same canonical path exists and
reports CUDA 13.0. It does not install, replace, or select a different CUDA
toolchain.

The sealed environment readback records the exact image ID, instance type,
region, zone, OS/kernel, GPU UUID/model/memory, driver, CUDA compiler, Python,
Rust, Docker/NVIDIA-container versions when present, and any visible KeenTune
unit state. It deliberately omits account identity, instance identity, and IP
addresses. A future provider image is admissible only if it still satisfies
the frozen capability envelope; its exact identity remains reviewable through
this readback.

Generated `runtime.env` is written before the manifest and hashed by it. The
manifest also hashes all generated admission inputs. Every later command first
rechecks the same ToolGap commit/tree with no tracked diff, manifest hash,
runtime mapping, source trees, retained wheels, lock, reports, model identity,
and predecessor receipt before sourcing the runtime mapping.

Every source/model restoration and pip resolution/build/install operation has
a 1,800-second command deadline. A deadline becomes a retained
`BLOCKED_BEFORE_EXECUTION` terminal rather than an unbounded rental operation.

Immediately after reserving a new attempt directory, preflight writes an
immutable `attempt-context.json` with the attempt ID, SPEC hash, ToolGap commit
and tree, and tracked-clean readback. If admission stops before `manifest.json`
exists, this file is the stage-aware identity retained by the failure index.

The default attempt location is:

```text
experiments/g0/raw/g0-c-017/<attempt-id>/
```

It is generated raw state and is ignored by Git. A failed admission is retained
as `BLOCKED_BEFORE_EXECUTION` with `execution-status.json` inside its artifact
index. It does not imply a Gate result.

## 5. Ordered controls

The phase order is enforced, not merely documented:

```text
preflight-status.json: ADMITTED_PRE_ARM
  -> controls-passed.json: CONTROLS_PASSED
  -> serving-passed.json: SERVING_PASSED
  -> final evidence seal
```

Each receipt is immutable and bound to the manifest SHA-256. A missing,
reordered, replaced, or differently bound receipt makes the attempt
`INVALID_SCOPE`.

Command `21-g0-c-017-contract-controls.sh` runs, in order:

1. The retained v6 oracle against stock must exit 1 and report `Ran 27 tests`
   plus `FAILED (failures=27)`.
2. The same oracle against treatment must exit 0 and report `Ran 27 tests` plus
   `OK`.
3. The installed treatment wheel executes the real
   `UnifiedRadixCache.checked_demote_session` seam through the registered legacy
   test backend, returns the package's typed `UNSUPPORTED_BACKEND`, and records
   zero calls to physical `demote`.
4. The fixed AST inventory reports zero production callers of
   `checked_demote_session`, exactly one cache-to-backend call to
   `demote_session_checked`, and no declared dynamic `getattr` route.

These controls prove a fixed source/installed seam only. They do not prove a
runtime dynamic bypass or physical mechanism.

## 6. Paired ordinary-serving protocol

Command `22-g0-c-017-serving-arms.sh` runs stock on port 30000, cleans it, then
runs treatment on port 30001. Before each launch, the actual arm interpreter
reruns package provenance and must resolve all four modules inside that arm's
environment with hashes matching its checkout. Both provenance and the real
server launch clear inherited `PYTHONPATH` so the launch cannot resolve a
different package than the one just verified. Both also force offline model
loading from the same per-file-verified local snapshot.

Apart from arm identity and port, both launches are identical: Python TreeCore,
`write_through`, bfloat16, page size 16, context/max-total 4096, static fraction
0.70, HiCache ratio 2.0, kernel/page-first I/O, TP=DP=1, FCFS, seed `20260817`,
session radix enabled, no L3 backend, and:

```text
SGLANG_ENABLE_UNIFIED_RADIX_TREE=1
```

Each server starts in its own Linux process group. The runner records the group
and GPU compute PID sets before, during, and after the arm. After the runner
sends `SIGTERM`, the existing 60-second deadline covers convergence of all
three cleanup observations: process-group members, the arm's listener, and GPU
PIDs attributable to that arm. The final immutable snapshots are taken from
the first jointly quiescent observation, or from the deadline observation.
Any survivor at the deadline fails cleanup. A runner `HUP`, `INT`, or `TERM`
also enters the same failure cleanup path. The server leader must be reaped
with exit status 0, the expected SIGTERM-derived 143, or this fixed SGLang
revision's attributed self-cleanup status 137; any other status is retained as
an execution failure, even if requests otherwise look green.

Readiness polls `/health` every five seconds for at most 900 seconds. Every
poll has both a five-second connection timeout and a ten-second total transfer
timeout. A connected endpoint that never returns cannot defeat the outer
deadline.

For each arm, the exact body in `request.g0-c-007.json` is sent twice serially.
Each request has a ten-second connection deadline and a 180-second terminal
deadline. Success requires HTTP 200, a response media type of
`text/event-stream` (parameters allowed), at least one JSON `data:` event with
`text` and `meta_info`, terminal `[DONE]`, and no parse/timeout error. Outputs
are retained but never compared for model correctness.

## 7. Attempt terminals and evidence seal

| Condition | Retained attempt status | Gate implication |
| --- | --- | --- |
| Host, source, build, model, or manifest admission fails before an arm | `BLOCKED_BEFORE_EXECUTION` | none; prior G0 `RESHAPE` remains |
| A started arm lacks a terminal, fails protocol, times out, crashes, or leaks attributable work | `EXECUTION_FAILED_AFTER_START` | none pending root-cause review |
| Patch scope, identity, phase order, inventory, or seam no-demote invariant fails | `INVALID_SCOPE` | none; preserve the attempt |
| All checks and the three-part seal hold | `COMPLETED` | independent review may select PASS/RESHAPE/STOP |

Every failure uses the same finalizer:

```text
execution-status.json -> artifact-index.json containing that terminal
```

After an artifact index is written, terminal sealing must not append bytes to
any indexed artifact. A failure receipt is therefore represented by the two
files above rather than a post-index summary line in a build log.

A successful protocol uses:

```text
execution-status.json: all checks passed, completion not yet claimed
  -> artifact-index.json containing execution-status.json
  -> completion-receipt.json: COMPLETED, binding index and status hashes
```

An `execution-status.json` without the matching completion receipt is never a
successful attempt. The completion receipt records that independent review is
still pending and carries no Gate decision.

## 8. Commands and rental-host handoff

From the committed repository root, prepare only missing project build tools.
This step is outside the attempt and may be rerun safely:

```bash
bash experiments/g0/commands/19-g0-c-016-project-prereqs.sh
```

Then choose one unused stable attempt ID and run the sealed attempt exactly
once in numeric order:

```bash
export G0_SOURCE_SEED_ARCHIVE=/root/g0-inputs/sglang-92b1d382-seed-portable.tar.gz
export G0_MODEL_SEED_ARCHIVE=/root/g0-inputs/qwen2.5-0.5b-c89bee90-model-seed.tar.gz
export G0_ATTEMPT_ID=g0-c-017-a10-attempt-001
bash experiments/g0/commands/20-g0-c-017-preflight.sh
export G0_RUN_DIR="$PWD/experiments/g0/raw/g0-c-017/$G0_ATTEMPT_ID"
bash experiments/g0/commands/21-g0-c-017-contract-controls.sh
bash experiments/g0/commands/22-g0-c-017-serving-arms.sh
bash experiments/g0/commands/23-g0-c-017-verify.sh
```

If `G0_RUN_DIR` is overridden before command 20, export that exact emitted path
instead of the default shown above. Never rerun a phase or overwrite a receipt
in the same attempt directory; create a new attempt identity.

Before releasing an ephemeral rental host, copy the complete attempt directory
off host and run:

```text
python3 experiments/g0/commands/g0_c_017_finalize.py verify \
  --run-dir <downloaded-attempt-directory>
```

Only after that verification may the host be released. Independent review then
chooses whether selected compact evidence belongs under tracked `artifacts/`
and whether the successor G0 decision is PASS, RESHAPE, STOP, or no decision.
