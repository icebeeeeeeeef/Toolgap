# G0-C-ATOMIC-007 — CUDA package and ordinary-serving integration

> Gate: G0
>
> Specification state: frozen before runtime execution
>
> Claim state: `roadmap`
>
> Revision: G0-C-ATOMIC-007
>
> Run identity: `g0-c-atomic-runtime-integration-007`

## 1. Decision question and claim ceiling

Can the reviewed four-file atomic checked-demote patch be installed as an exact
SGLang package, exercise its real cache-to-registered-backend fail-closed seam,
and start ordinary HiCache serving on one frozen CUDA host?

This experiment does **not** invoke physical `demote`, read allocator capacity,
or establish output equivalence, lifecycle correctness, recovery, or
performance. A green run supports only `experimental integration` on the named
source, package lock, model, and host. It does not claim upstream acceptance and
does not authorize G1 until independent review accepts the Gate decision.

## 2. Authority, source, and treatment

`docs/ROADMAP.md` owns G0/G1 order; `docs/DEMOTION_CONTRACT.md` owns the
semantics; this file owns only this successor runtime protocol. It supersedes
no frozen G0-C-001 through G0-C-006 artifact.

Both arms start from the SGLang remote, base commit, tree, model, and fixed
configuration in [`upstream/sglang/pin.toml`](../../upstream/sglang/pin.toml).
The treatment applies only
`upstream/sglang/patches/0001-atomic-checked-demote.patch`, whose SHA-256 must
equal `e69776678909b4ee49b1c0fa4a8e208666893b659c0508387c83fcdf11e82a9a`.
It may change only these paths:

```text
python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py
python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py
python/sglang/srt/mem_cache/unified_cache/unified_tree_core_interface.py
python/sglang/srt/mem_cache/unified_radix_cache.py
```

The source runner creates complete stock and treatment checkouts. An audit-only
sparse checkout is invalid because the server entrypoint and packaging files
must be materialized. The treatment tree is recorded after applying the patch;
the patch hash and tree, not an upstream merge, establish reproducibility.

## 3. Environment admission

Before either arm, command `20-g0-c-007-preflight.sh` must record and enforce:

- Linux x86_64, exactly one NVIDIA A10 with 22–25 GiB reported memory, driver
  `580.65.06`, Python `3.12.11`, and Torch CUDA `13.0`;
- complete stock/treatment worktrees at the fixed source identity;
- one resolved dependency lock derived from the stock wheel, with the SGLang
  package line removed; separately built stock and treatment wheels; and clean,
  separate environments that install that shared lock plus their own wheel;
- package provenance: absolute interpreter, `sys.path`, package path, and
  hashes of all four treatment modules; and
- model/tokenizer snapshot identity before either server starts.

The command writes an immutable admission manifest with the SHA-256 of this
SPEC. Any mismatch or build/model failure before an arm starts is
`BLOCKED_BEFORE_EXECUTION`; it is retained and does not imply a Gate decision.

## 4. Controls and seam oracle

Command `21-g0-c-007-contract-controls.sh` runs these controls in order:

1. The retained v6 source oracle with its checkout argument set to the fresh
   stock checkout must exit 1 and report Ran 27 tests plus
   FAILED (failures=27).
2. The same oracle against the treatment checkout must exit 0 and report
   Ran 27 tests plus OK.
3. The treatment wheel runs
   `upstream/sglang/tests/test_g0_atomic_checked_demote_installed.py` from a
   temporary directory with `PYTHONPATH` unset. The test constructs the real
   `UnifiedRadixCache` through the real TreeCore registry, registers a legacy
   backend whose checked method returns the actual typed
   `UNSUPPORTED_BACKEND` result, calls the installed
   `checked_demote_session`, and asserts a zero physical-`demote` counter.
4. The AST inventory reports no production call expression to
   `checked_demote_session`, exactly one call expression to
   `demote_session_checked` inside that cache method, and no dynamic
   `getattr` route for either name.

The installed seam control is deliberately fail-closed: a real physical
`demote` call, a source-path import, a changed inventory count, or a missing
typed result makes the attempt `INVALID_SCOPE`.

## 5. Paired serving protocol

Command `22-g0-c-007-serving-arms.sh` runs stock first on port 30000 and
treatment second on port 30001. Apart from source/wheel/environment and port,
the launch flags are identical: Python TreeCore, `write_through`, bfloat16,
page size 16, context/max-total 4096, static fraction 0.70, HiCache ratio 2.0,
kernel/page-first I/O, TP=DP=1, FCFS, seed `20260817`, session radix enabled,
and no L3 backend.

For each arm, the runner captures pre/post GPU process readbacks and server
stdout/stderr, waits at most 900 seconds for `/health`, then sends this native
streaming `/generate` body twice serially:

```json
{
  "text": "ordinary cache integration prompt ordinary cache integration prompt ordinary cache integration prompt ordinary cache integration prompt ordinary cache integration prompt ordinary cache integration prompt ordinary cache integration prompt ordinary cache integration prompt ordinary cache integration prompt ordinary cache integration prompt ordinary cache integration prompt ordinary cache integration prompt ordinary cache integration prompt ordinary cache integration prompt ordinary cache integration prompt ordinary cache integration prompt",
  "sampling_params": {
    "temperature": 0.0,
    "max_new_tokens": 8,
    "ignore_eos": true
  },
  "stream": true
}
```

Before the first request, the selected tokenizer must report at least 32 input
tokens. Each request has a 10-second connection deadline and 180-second
terminal deadline. Its raw Server-Sent Events are retained; success requires
HTTP 200, at least one JSON `data:` event with `text` and `meta_info`, terminal
`[DONE]`, and no parse or timeout error. The server then receives `SIGTERM` and
must leave no listener or tracked process after 60 seconds.

A well-formed response is a startup/protocol observation only. The two model
outputs are not compared and do not support model-correctness claims.

## 6. Outcomes and decision

| Attempt condition | Status | Gate implication |
| --- | --- | --- |
| Host, source, build, model, or admission-manifest failure before an arm | `BLOCKED_BEFORE_EXECUTION` | none; prior G0 `RESHAPE` remains |
| Started arm lacks a required terminal, fails protocol, times out, crashes, or leaks | `EXECUTION_FAILED_AFTER_START` | none pending root-cause review |
| Patch scope, provenance, inventory, or seam no-demote invariant fails | `INVALID_SCOPE` | none; create a new revision |
| All predeclared checks hold | `COMPLETED` | independent review may select PASS/RESHAPE/STOP |

A failed preflight retains preflight-status.txt with
BLOCKED_BEFORE_EXECUTION. A contract-control failure retains
execution-status.json as INVALID_SCOPE; a started-serving failure records
EXECUTION_FAILED_AFTER_START. Command 23 writes COMPLETED only after every
required terminal holds, and records that independent review is still pending.

PASS requires all source controls, isolated package provenance, installed
fail-closed seam evidence, paired server protocol terminals, cleanup evidence,
and a review finding no widened ownership. It unlocks only a separate G1 plan
and SPEC. RESHAPE requires evidence that this narrow integration cannot run
without widening ownership; STOP requires a second physical data plane,
replacement tree/allocator, public pause API, worker, or candidate-owned
physical algorithm.

## 7. Commands and evidence bundle

```text
experiments/g0/commands/20-g0-c-007-preflight.sh
experiments/g0/commands/21-g0-c-007-contract-controls.sh
experiments/g0/commands/22-g0-c-007-serving-arms.sh
experiments/g0/commands/23-g0-c-007-verify.sh
```

Run these commands in numeric order from the repository root. Set one new,
stable G0_ATTEMPT_ID before command 20, then set G0_RUN_DIR to its emitted
attempt directory before commands 21 through 23. Never rerun an attempted
phase into the same directory: choose a new attempt ID so the prior raw
evidence remains untouched.

The preflight creates
`experiments/g0/artifacts/g0-c-007/<attempt-id>/manifest.json` before either
arm. It records only admitted identity and planned evidence; the post-run
verifier creates a separate artifact index rather than rewriting that manifest.
Raw outputs, lock, wheels, provenance, server logs, SSE captures, and failed
attempts remain in that attempt directory. `RESULTS.g0-c-007.md` is created
only after execution and independent review; it is not pre-created as a
placeholder.
