# G1 implementation cross-review

> Status: implementation reviewed; local runtime validation blocked
>
> Tracker: [G1: implement the accepted mechanism protocol](https://github.com/icebeeeeeeeef/Toolgap/issues/12)
>
> Canonical owners: [`experiments/g1/SPEC.md`](../../../experiments/g1/SPEC.md),
> [`experiments/g1/IMPLEMENTATION_DESIGN.md`](../../../experiments/g1/IMPLEMENTATION_DESIGN.md),
> and [`docs/DEMOTION_CONTRACT.md`](../../../docs/DEMOTION_CONTRACT.md)

## Decision

The final treatment is limited to the authorized test-only scripted-runtime
module in `upstream/sglang/patches/0002-g1-scripted-forced-demote.patch`; it
replays after the existing four-file checked-demote seam on fixed source
`92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`. It adds no production route,
ToolGap runtime module, direct test demotion/eviction call, or physical KV data
plane.

Three independent final reviews of the clean replay found no remaining P1/P2.
Their review repaired target-key attribution before clearing: both the H2D
pending loader and device-lock active request reconstruct the completed target
frontier, rather than resending only its prompt prefix. The test also pins
`page_size=1`, requires a live `ongoing_load_back` entry and positive lock for
the H2D pending case, and observes the same target at the checked facade.

## Verified local evidence

- `0001` then `0002` apply cleanly to a fresh detached worktree at the fixed
  source commit; the replay has only the four frozen runtime paths plus the new
  scripted test path.
- `git diff --check`, Python syntax compilation, SGLang CI marker parsing, and
  the prohibited-call/route scan pass after the last edit.
- The retained G0 source inventory passes: there is no direct
  `checked_demote_session` call and its sole `demote_session_checked` call is
  inside `UnifiedRadixCache.checked_demote_session`; no dynamic route exists.
- Independent code, mechanism-protocol, and evidence reviews each report no
  remaining P1/P2 for the final replay.

## Blocking evidence

The retained G0 installed-contract command and the new test's import/schema
command both stop before test execution because the pinned SGLang import reaches
`python/sglang/srt/utils/common.py:88` and raises `ModuleNotFoundError: No
module named 'triton'`. This macOS environment cannot supply the required CUDA
runtime path. Do not claim that section 7 completed, that a GPU behavior was
observed, or that G1 selected `PASS` or `STOP`.

## Required next action

Run the two blocked import-dependent checks, then the frozen scripted GPU
protocol, in the later owner-approved Linux CUDA/Triton environment. Preserve
the resulting raw artifacts under `experiments/g1/`; only that evidence can
advance the issue or Gate decision.
