# G1 Results - Forced Host-Tier Mechanism

> Narrow G1 mechanism finding: `experimentally validated`
>
> Overall ToolGap project claim state: `roadmap`
>
> Accepted Gate decision: `PASS` through independently reviewed G1-C-010/A1
>
> ToolGap revision: `ac31ff2dae357943191ce49cc280c9dbbcca2172`
>
> SGLang base: `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`

## Decision

G1-C-010/A1 passed the frozen seven-arm oracle on one Alibaba Cloud NVIDIA A10
host with Ubuntu 24.04, CUDA 12.8, driver 580.126.09, and Qwen3-0.6B. Independent
review found no P0, P1, or P2 evidence blocker and selected `Ready: Yes`.

Within the frozen Full-only, single-generation, single-action, private-tail
envelope, the candidate checked-demotion path produced exact physical frees and
allocator-visible capacity. Bypassing candidate behavior preserved the same
prepared device tail and capacity while releasing only target-session priority.
The result therefore supports the G1 `PASS` branch rather than `STOP`.

This Gate result does not change the overall project claim state from
`roadmap`. G2 still owns asynchronous lifecycle correctness and recovery, and
G3 still owns comparison against the strongest simple baseline.

## Formal Attempt

| Field | Value |
| --- | --- |
| bundle | `G1-C-010` |
| attempt | `g1-c-010-a1-20260825T095119Z` |
| terminal | `PASS` |
| evidence scope | `formal_runtime` |
| ToolGap commit/tree | `ac31ff2dae357943191ce49cc280c9dbbcca2172` / `72aa686fc22822cd377f2bbc0c07fa672682f539` |
| SGLang base commit/tree | `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2` / `25e9bf86d04c27fe380024d9c8c421c3b5b51f3c` |
| external anchor SHA-256 | `09f2594d1162122591484b2ad034f9749821d0cfceb39303dc85bc425c922ac5` |
| external anchor version | `CAEQnAYYgYCAyd_b4YEaIiAyY2YyYmQwNTZjNmE0MzQ3YTNmNGYyZDg2NzkyZjgwZg--` |

External anchor:

`oss://agentic-kv-c0-evidence-20260812/g1/g1-c-010/ac31ff2/anchors/g1-c-010-a1-20260825T095119Z/external-anchor-09f2594d1162122591484b2ad034f9749821d0cfceb39303dc85bc425c922ac5.json`

## Decisive Evidence

| Arm | Frozen observation |
| --- | --- |
| `enabled` | `ACCEPTED`; target node 21 freed exact device IDs 257 through 264; allocator available size increased from 3832 to 3840; checked facade, checked backend, physical demote, and cache drain each executed once; stock eviction remained zero |
| `bypass` | `PRIORITY_RELEASE_ONLY`; allocator remained 3832; target device IDs remained 257 through 264; checked, physical-demote, drain, and stock-eviction counters remained zero |
| `reject_write_through_pending` | `DEFERRED/WRITE_THROUGH_PENDING`; no physical free or allocator increase |
| `reject_non_target_session_coverage` | `DEFERRED/NON_TARGET_SESSION_COVERAGE`; the other session reference remained and no physical free occurred |
| `reject_device_locked` | `DEFERRED/DEVICE_LOCKED`; the live device lock remained and no physical free occurred |
| `reject_stale_generation` | `REJECTED/STALE_GENERATION` before priority release; no backend or physical call occurred |
| `stock_eviction_liveness` | bypass remained priority-only and ordinary pressure reached one stock eviction with a real victim |

All seven selectors ran once in fresh process groups and reported `OK`. Every
arm sealed an exact PID/PGID handshake and empty process-group, listener-leak,
and attributable-GPU-leak observations.

## Evidence Closure

The off-host finalizer independently replayed the terminal classification from
the preserved sealed directory. Its artifact index contains 157 files; with
`artifact-index.json` and `completion-receipt.json`, the sealed closure contains
159 regular files and no symlinks.

Independent review recomputed every local SHA-256 and size, fetched all 159 OSS
objects by their exact version IDs, and recomputed every remote SHA-256 and
size. It also checked all seven frozen input object versions. All comparisons
matched. The review record is
[`worklog/reviews/2026-08-25/g1-c-010-independent-evidence-review.md`](../../worklog/reviews/2026-08-25/g1-c-010-independent-evidence-review.md).

## Preserved Invalid Attempts

Earlier revisions remain immutable and do not contribute to this PASS:

- G1-C-008/A1 sealed `pre_execution INVALID`; its partial arm evidence cannot
  contribute to a Gate decision.
- G1-C-009/A1 sealed `pre_execution INVALID` after the bypass request consumed
  its scheduler-step budget before HTTP/tokenizer admission. C010 fenced exact
  `/generate` and `/close_session` admission without changing the downstream
  400-step side-effect bounds or the seven-arm oracle.

## Limits

The result proves only the narrow physical mechanism under the frozen host,
model, source, and workload. It does not prove:

- output equivalence, restore, recompute, cancellation, or recovery;
- concurrent, repeated, or asynchronous lifecycle correctness;
- SWA, MAMBA, multi-node, other models, or general upstream compatibility;
- production API, public pause semantics, or dynamic policy;
- latency, throughput, sustainable load, time-to-headroom advantage, or any
  statistically repeated performance result.

## Next Gate

G1 is closed at `PASS`. The next Gate is G2 lifecycle correctness and recovery.
G1 PASS authorizes preparation and review of a separate G2 plan and frozen
execution contract; it does not itself prove or execute G2.
