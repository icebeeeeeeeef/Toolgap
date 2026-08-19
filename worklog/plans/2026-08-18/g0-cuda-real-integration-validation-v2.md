# G0 CUDA real-integration validation plan v2

> Status: completed — pre-rental execution bundle landed; no rented-host run
>
> Claim state: `roadmap`
>
> Date: 2026-08-18
>
> Supersedes:
> [`g0-cuda-real-integration-validation.md`](g0-cuda-real-integration-validation.md)

> **For agentic workers:** execute this plan only after owner acceptance. Before
> either runtime arm, create a checksum-linked, frozen
> `experiments/g0/SPEC.g0-c-007.md` and manifest. Do not start G1 from an
> intermediate success.

## 1. Decision to make

Determine whether the reviewed four-file atomic checked-demote contract can be
installed, exercised at its cache-to-backend seam without physical demotion,
and coexist with ordinary SGLang HiCache serving on one frozen CUDA host.

This is a successor **G0 integration** experiment, not a G1 mechanism run. It
does not call a real physical demotion, observe GPU allocator reclamation,
measure latency/throughput/capacity, or test recovery, cancellation, resume,
or output after demotion.

The chosen reproducibility form is **experimental patch**. Waiting for a public
upstream merge would make this validation depend on an external review schedule
rather than improve its local causal evidence. The result must say
`experimental integration`, never `upstream accepted`.

## 2. Minimal evidence chain and acceptance contract

The experiment is intentionally a chain, not a single health check:

```text
exact full source + reviewed patch
  -> source-contract RED/GREEN control
  -> isolated installed wheels and provenance
  -> treatment cache/backend seam dry-run, zero physical demote
  -> stock/treatment HiCache start plus ordinary native request protocol smoke
```

### PASS — authorizes only G1 planning/specification

All of these hold in one checksum-linked run bundle:

1. Full stock and treatment worktrees derive from SGLang base commit
   `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`; the treatment applies only
   `sglang-session-atomic-checked-demote-v5.patch` with SHA-256
   `e69776678909b4ee49b1c0fa4a8e208666893b659c0508387c83fcdf11e82a9a` and
   records the resulting commit/tree.
2. The retained v6 oracle has the expected stock RED and treatment 27/27 GREEN
   terminals. This remains a source-contract control, not real physical-path
   evidence.
3. The two arms use independently built wheels and isolated environments that
   retain the package lock, wheel hashes, interpreter, `sys.path`, package
   `__file__` paths, and hashes of all four modified modules.
4. The installed treatment package executes the real
   `UnifiedRadixCache.checked_demote_session` cache method against a registered
   legacy test backend; it returns the real typed unsupported outcome and makes
   zero calls to physical `demote`.
5. A fixed static inventory of the treatment source finds no production caller
   of `checked_demote_session`, and only its declared cache-to-backend call to
   `demote_session_checked`. This supports the limited fixed-source claim that
   the ordinary serving smoke has no direct source caller into the candidate
   seam.
6. Stock and treatment each start the fixed HiCache server configuration and
   complete two identical ordinary native `/generate` request protocols. Each
   protocol satisfies the frozen HTTP/SSE schema and process-cleanup oracle.

The resulting claim ceiling is narrow: on this exact host, the audited seam is
an installed experimental SGLang integration and ordinary serving starts and
speaks the selected native protocol. It does **not** prove physical reclamation,
allocator headroom, request-path dynamic bypass, output equivalence, lifecycle
correctness, or performance. The project remains `roadmap` unless canonical
records later make a supported promotion.

### RESHAPE and STOP

- **RESHAPE:** only after review shows the contract cannot be made buildable or
  runnable without widening the audited ownership boundary.
- **STOP:** only after review shows that the smallest viable integration needs a
  second physical index/data plane, replacement cache tree or allocator,
  public pause API, background worker, or candidate-owned physical demotion.

Neither an unavailable GPU nor an install/server failure automatically reaches
either decision.

### Attempt status

| Situation | Recorded attempt status | Gate decision |
| --- | --- | --- |
| Required host/configuration, source admission, model, or build preflight fails before an arm starts | `BLOCKED_BEFORE_EXECUTION` | none; G0 remains at its prior `RESHAPE` result |
| A started arm lacks a terminal, times out, crashes, fails its HTTP/SSE oracle, or leaks a process | `EXECUTION_FAILED_AFTER_START` | none unless a later review establishes RESHAPE/STOP |
| Static inventory is non-zero/ambiguous, patch scope changes, or physical demote is called in the seam dry-run | `INVALID_SCOPE` | none; preserve artifacts and require a new plan/SPEC |
| Every preregistered requirement holds | `COMPLETED` | PASS, RESHAPE, or STOP only after independent review |

Incomplete and invalid attempts remain in the manifest index. They are not
silently retried, renamed as an inconclusive Gate result, or used to unlock G1.

## 3. Fixed scope boundary

### In scope

- Python TreeCore, `write_through` Host mode, one node, and the retained
  four-file patch: `session_ref_tracker.py`, `unified_tree_core.py`,
  `unified_tree_core_interface.py`, and `unified_radix_cache.py`.
- Stock versus patched **installed** SGLang package compatibility.
- A test-only registered backend that supplies typed execution results, with
  physical `demote` replaced by a fail-fast counter stub solely to prove it was
  not called.
- Native server startup, health, two ordinary requests, and shutdown.

### Explicit exclusions

- Any real `demote`, allocator query, GPU-memory result, cache eviction
  comparison, forced trigger, pressure workload, output-equivalence assertion,
  benchmark, recovery/cancel/resume test, or ToolGap runtime source.
- An upstream merge requirement, a second cache index, changing the physical
  cache tree/allocator, a public pause API, worker/retry subsystem, or a
  dynamic tracing hook.
- Reusing an audit-only sparse checkout to build or launch the server.

## 4. Execution order

### A. Source admission before renting a GPU

1. Create two **complete** SGLang worktrees from the fixed base: `stock` and
   `treatment`. Explicitly disable sparse checkout in both before any package
   build; the existing audit acquisition intentionally omits server entrypoint
   and packaging files.
2. Verify `git apply --check`, apply the exact patch without fuzz, and record
   base/treatment commit and tree IDs. Reject any diff outside the four named
   files or any change in patch hash.
3. Re-run the frozen v6 source oracle: stock must be RED and treatment must be
   27/27 GREEN. Retain both terminals unchanged.
4. Obtain independent review of the exact treatment diff. It must confirm one
   cache caller, final live checks plus existing `demote` in one backend method,
   cache-owned drain, fail-closed legacy behavior, and no added physical data
   structure or policy.
5. Prepare the smallest future execution bundle; do not add runtime production
   code:

   ```text
   upstream/sglang/
     pin.toml
     patches/0001-atomic-checked-demote.patch
     tests/test_g0_atomic_checked_demote_installed.py
   experiments/g0/
     SPEC.g0-c-007.md
     manifest.g0-c-007.template.json
     commands/20-g0-c-007-preflight.sh
     commands/21-g0-c-007-contract-controls.sh
     commands/22-g0-c-007-serving-arms.sh
     commands/23-g0-c-007-verify.sh
     artifacts/g0-c-007-*
     RESULTS.g0-c-007.md
   ```

No GPU is rented until source admission succeeds. A public upstream merge may
be recorded as additional evidence, but is not an admission condition.

### B. Freeze the successor specification before either arm

Freeze `G0-C-ATOMIC-007` with a checksum-linked manifest. The SPEC must copy
the decision and attempt rules above verbatim and additionally fix:

- target environment: Ubuntu 24.04.3 x86_64, exactly one NVIDIA A10 24 GB,
  driver `580.65.06`, CUDA `13.0`, Python `3.12.11`; if observed values differ,
  stop before any arm and create a new SPEC revision rather than substituting;
- full source identities, exact patch, model/tokenizer revision, launch flags,
  all timeouts, artifact names, command paths, and wheel-build recipe;
- the SGLang dependency inputs used for resolution. On the leased host,
  `20-g0-c-007-preflight.sh` produces the resolved lock and wheel hashes, then
  seals them into the manifest **before either arm starts**. Both arms reuse
  that one lock; no post-observation package substitution is permitted;
- fixed `write_through` configuration inherited from G0-C-006: page size 16,
  context/max tokens 4096, static memory fraction 0.70, HiCache ratio 2.0,
  kernel I/O, page-first layout, TP=DP=1, FCFS, seed `20260817`, session radix
  enabled, and no L3 backend. The actual launch command and model revision are
  recorded verbatim rather than reconstructed from this summary;
- readiness: poll `/health` every 5 seconds for at most 900 seconds; each HTTP
  connection has a 10-second connection deadline and 180-second terminal
  deadline; after each arm `SIGTERM` has 60 seconds to terminate the process.

The first preflight is environment admission, not a stock/treatment result. A
failed admission is retained as `BLOCKED_BEFORE_EXECUTION`.

### C. Build clean installed packages and prove provenance

For both source trees, build a wheel and resolve the shared dependency lock
during preflight, then seal their hashes into the manifest before either arm
starts. Install each wheel into a separate clean virtual environment with its
absolute interpreter; run tests from a temporary working directory with
`PYTHONPATH` unset. Retain:

- wheel filename, SHA-256, build command and lock;
- `sys.executable`, `sys.path`, `sglang.__file__`, package version, and the
  `__file__` plus SHA-256 of the four modified treatment modules;
- `uname -a`, GPU UUID/model/total memory, driver/CUDA readback, Python/pip
  versions, model/tokenizer identity/hash, disk capacity, port assignment, and
  complete stdout/stderr for build and install.

An import that resolves to either worktree, the other arm's environment, or an
ambient source path invalidates the arm. The manifest must identify the exact
process interpreter used for every command.

### D. Treatment installed-package seam dry-run

Create `test_g0_atomic_checked_demote_installed.py` as a treatment-wheel test.
It imports the real package objects and executes the real
`UnifiedRadixCache.checked_demote_session` method; it must not copy or extract
that method into the test.

The fixture is intentionally minimal:

1. Construct the smallest valid real cache/session state required to call the
   cache method, using a registered legacy test backend that returns the actual
   typed `UNSUPPORTED_BACKEND` execution result.
2. Make any physical `demote` implementation a counter/fail-fast stub. Assert
   zero calls at test end.
3. Assert the returned object is the package's real checked-demote outcome type
   with the expected unsupported reason. Retain method/type signatures and
   imported-module paths as readbacks.

This is neither a fake-resource success case nor a physical-demote simulation:
it only proves the installed cache-to-backend, typed fail-closed seam. On stock,
the interface absence is recorded as the expected baseline; the v6 RED control
is the cross-arm contract comparison.

### E. Fixed source inventory

Before launching a server, run a saved AST-based inventory on the full
treatment source. It must report, with file/line/function records:

- zero production call expressions to `checked_demote_session` under
  `python/sglang` (definitions and tests excluded); and
- exactly one production call expression to `demote_session_checked`, inside
  `UnifiedRadixCache.checked_demote_session`.

The command, source tree ID, and machine-readable result enter the artifact
index. This deliberately replaces a dynamic tripwire with a smaller claim:
the fixed source has no direct ordinary-request caller of the candidate seam.
Any reflection/dynamic route found during source review, a changed count, or an
ambiguous result is `INVALID_SCOPE`, not a reason to instrument the server.

### F. Paired native serving arms

Run stock first on port 30000 and treatment second on port 30001. Apart from
source/wheel/environment and port, every launch flag is identical. For each
arm:

1. Capture the pre-launch process/GPU readbacks and full server stdout/stderr.
2. Poll `/health` using the frozen deadline.
3. Use the selected source's native streaming `/generate` protocol. The frozen
   request body contains `stream: true`, deterministic sampling
   (`temperature: 0.0`, `max_new_tokens: 8`, `ignore_eos: true`), and one text
   prompt whose selected tokenizer count is recorded and is at least 32 tokens
   (at least two 16-token pages).
4. Send that exact body twice serially. For each request retain raw SSE bytes
   and a parsed record. Require HTTP 200, at least one valid data JSON object
   carrying `text` and `meta_info`, a terminal `[DONE]`, and no parse or timeout
   error.
5. Send `SIGTERM`; capture the exit terminal, verify the process and listener
   exit within 60 seconds, and retain post-shutdown process/GPU readbacks.

Do not compare the two model outputs or treat a well-formed response as model
correctness. These requests are protocol/startup observations only. A stock
internal `demote` reached through unrelated HiCache behavior is retained and
labelled; it is not itself a G1 candidate call. A call to the patched seam or a
physical demote in the installed seam dry-run is scope-invalidating as defined
above.

### G. Seal and review

`23-g0-c-007-verify.sh` must verify the SPEC checksum, source/patch trees,
wheel and module hashes, lock reuse, expected contract terminals, source
inventory, per-arm HTTP/SSE terminals, and cleanup terminals. It emits an
artifact index containing size and SHA-256 for every raw file.

An independent reviewer then determines whether the predeclared PASS,
RESHAPE, STOP, or no-decision condition holds. `RESULTS.g0-c-007.md` links to
the raw bundle and to the historical G0 `RESULTS.md`; it never rewrites the
previous `RESHAPE` record. Only an accepted PASS may start a separate G1 plan
and a new frozen G1 specification.

## 5. Why this is the smallest sufficient plan

Removing the source oracle loses the stock/treatment contract control. Removing
wheel provenance makes a local source import look like integration. Removing
the installed seam dry-run leaves the only new cache/backend boundary uncalled.
Removing the request pair leaves no actual server protocol observation.

Conversely, adding a real demote, allocator readback, response equality after
demotion, or a benchmark would not make this evidence stronger for its stated
question; it would create an unpreregistered G1-or-later question. This plan
therefore keeps the rented host meaningful without using it as an excuse to
broaden scope.

## 6. Implementation closure — 2026-08-19

The pre-rental execution bundle is now present in the repository:

- an exact SGLang pin, byte-identical four-file patch, installed-wheel seam
  test, and fixed-source AST inventory;
- the G0-C-ATOMIC-007 SPEC, template-only admission manifest, and fixed
  ordinary-request body;
- commands 20 through 23 for preflight/admission, contract controls, paired
  serving, and terminal verification; and
- a root-local structural verifier that checks syntax, patch identity,
  seal-once manifest behavior, and artifact indexing.

The local structural verifier passed on 2026-08-19. Its localhost streaming
subcheck was explicitly skipped because this sandbox denies socket bind; that
is not serving evidence. No CUDA host, wheel build, model download, SGLang
server, or Gate run has occurred. G1 remains blocked by
[docs/ROADMAP.md](../../../docs/ROADMAP.md).
