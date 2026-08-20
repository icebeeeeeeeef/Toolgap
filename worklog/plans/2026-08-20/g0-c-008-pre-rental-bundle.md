# G0-C-008 pre-rental execution bundle

> Status: completed — ready for a committed rental attempt; no CUDA run
>
> Claim state: `roadmap`
>
> Date: 2026-08-20

## Goal

Replace the frozen but unexecuted G0-C-007 protocol with one minimally repaired
G0-C-008 bundle that can be committed before renting the declared CUDA host.
The bundle must fail closed on source, package, phase-order, process-cleanup,
and evidence-sealing drift. It still asks only the successor G0 integration
question defined by `experiments/g0/SPEC.g0-c-008.md`.

## Scope

- preserve G0-C-007 unchanged as a frozen, never-run protocol;
- create a complete G0-C-008 SPEC, manifest template, four ordered entry
  commands, and revision-specific evidence helpers;
- retain the exact G0-C-006 patch, source oracle, installed seam test, static
  inventory, request body, SGLang pin, and G0/G1 ownership boundary;
- write generated attempts under the ignored `experiments/g0/raw/` tree;
- save both exact SGLang wheels and install reports inside the attempt;
- bind each phase to the ToolGap Git tree, admission manifest, runtime mapping,
  and predecessor receipt;
- seal every failed attempt as terminal plus artifact index, and seal a
  successful protocol as status plus index plus completion receipt;
- add a local structural/counterexample verifier that requires no GPU.

## Non-goals

- no physical demotion, allocator observation, output comparison, recovery,
  performance measurement, G1 execution, or production ToolGap runtime;
- no G0.5, generic experiment framework, container platform, cgroup manager,
  dynamic tracing, full dependency wheelhouse, signature service, or database.

## Counterexample matrix

Target: G0-C-008 pre-rental execution bundle

Confidence claim: after the local verifier passes, the committed bundle is
eligible for one rented-host runtime attempt; no CUDA or Gate result is claimed.

Basis: `docs/ROADMAP.md`, `docs/governance/EXPERIMENT_AND_EVIDENCE_SOP.md`,
`docs/DECISIONS.md` D021/D022, and `experiments/g0/SPEC.g0-c-008.md`.

| Behavior obligation | Credible wrong implementation | Distinguishing scenario and oracle | Evidence |
| --- | --- | --- | --- |
| Default attempt creation is usable and ignored | Reuse the absent/unignored 007 artifacts parent | Run preflight with an invalid interpreter and no `G0_RUN_DIR`; it must retain a blocked terminal and index under `raw/g0-c-008` | `scripts/verify-g0-c-008-bundle.sh` |
| Build uses the fixed pin's package root | Check repository-root `pyproject.toml` | Static contract requires `checkout/python/pyproject.toml`; pinned source evidence owns the path | bundle verifier plus fixed-source check |
| The pinned default wheel can actually build | Assume a Python-only wheel and discover missing Cargo after rental | Admission requires and records `cargo`/`rustc`; both arms build the default wheel without changing Rust-extension selection | fixed `setup.py` review plus bundle verifier |
| Rental admission cannot hang forever | Bound only HTTP serving and leave clone/build/model download unbounded | Every network/build admission command runs under a 1,800-second timeout and failures enter the preflight terminal | bundle verifier |
| Serving selects UnifiedRadixCache | Keep only `--enable-session-radix-cache` | Launch environment contains `SGLANG_ENABLE_UNIFIED_RADIX_TREE=1` | bundle verifier |
| Health and SSE cannot hang or accept a non-SSE body | Use connect timeout only, or parse any 200 body | Health has a total request timeout; non-`text/event-stream` response fails | bundle verifier and stream-helper test |
| Phases cannot be reordered | Let command 22 run before controls | Each command requires the predecessor receipt bound to the admitted manifest | receipt/identity helper tests |
| Tracked protocol and generated runtime identity cannot drift | Check manifest existence only | Mutating a tracked input or `runtime.env` makes identity verification fail | identity-helper counterexamples |
| An arm cannot silently use the other interpreter/package | Check only that imports are outside the checkout | Wrong expected interpreter or install root produces `passed=false` | provenance-helper counterexamples |
| The real launch cannot bypass the verified package | Clear `PYTHONPATH` for provenance but inherit it for `launch_server` | The executable launch clears `PYTHONPATH`; the bundle verifier rejects its removal | bundle verifier |
| Exact wheels survive work-root deletion | Store wheels only in `/tmp` | Both wheel paths are inside the attempt and remain hash-verifiable after work-root removal | manifest/final-seal tests |
| Cleanup covers descendants and attributable GPU work | Kill only the parent PID | Each arm has a process group and records before/during/after GPU PID sets; a surviving group or attributable PID fails | bundle verifier and final evidence verifier |
| A server crash cannot masquerade as normal cleanup | Ignore `wait` after two successful requests | Cleanup records the leader status and accepts only 0 or expected SIGTERM status 143 | final evidence counterexample |
| Operator disconnect cannot bypass failure cleanup | Trap only interactive `INT`/`TERM` | All four phases retain a failure terminal on `HUP`; a started arm first cleans its process group | bundle verifier |
| A success cannot exist without a complete seal | Write `COMPLETED` before indexing | Status is indexed first; only a receipt bound to the index and status carries `COMPLETED` | finalizer success counterexample |
| Failed attempts remain reviewable | Exit after writing a failure status | Failure finalization creates an index containing the terminal and no success receipt | finalizer failure counterexample |
| Off-host verification cannot accept a relabeled or incomplete seal | Verify only two hashes or complete an arbitrary directory | Finalizer requires attempt identity, manifest, phase receipts, planned artifacts, and exact `roadmap`/no-Gate receipt semantics; copied-path verification is exercised | finalizer counterexamples |
| Rental commands are directly runnable | Document non-executable scripts as bare commands or omit the run-dir handoff | SPEC uses `bash` for every phase and exports the exact default `G0_RUN_DIR` after admission | SPEC handoff review |

## Acceptance evidence

- the new verifier is observed failing before implementation and passing after;
- existing G0 evidence checks remain green;
- shell syntax, Python compilation, JSON parsing, Git diff checks, receipt
  ordering, identity drift, provenance drift, stream content type, and
  success/failure sealing counterexamples pass locally;
- fresh Luna Max reviewers independently inspect execution reachability,
  evidence causality, and Gate/minimality boundaries;
- final verification is rerun after all accepted review fixes.

## Canonical owners

- execution contract: `experiments/g0/SPEC.g0-c-008.md`;
- Gate order: `docs/ROADMAP.md`;
- revision decision: `docs/DECISIONS.md` D022;
- current documentation routing: `docs/README.md`.

## Completion evidence

- local counterexamples cover admission identity, bounded long operations,
  phase order, installed package identity, inherited `PYTHONPATH`, abnormal
  server exit, cleanup, SSE terminals, failure attribution, exact completion
  semantics, and off-host copied-path verification;
- execution, evidence, and Gate/minimality reviewers independently returned
  ready after their reproduced blockers were fixed and rerun;
- existing G0 evidence and frozen 007 checks remain regression inputs;
- no CUDA arm has run, so the project and this bundle remain `roadmap`.
