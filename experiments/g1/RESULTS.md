# G1 Results - Forced Host-Tier Mechanism

> Narrow G1 mechanism finding: `experimentally validated`
>
> Overall ToolGap project claim state: `roadmap`
>
> Accepted Gate decision: `PASS`; latest formal confirmation is G1-C-020/A1
>
> Frozen ToolGap revision: `e43ad7aabb7a8c0e4a17855a4745d91ba5945d96`
>
> SGLang base: `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`

## Decision

G1 remains closed at `PASS`. G1-C-020/A1 passed its frozen nine-arm oracle on
one Alibaba Cloud NVIDIA A10 host with Ubuntu 24.04.4, CUDA 12.8, driver
580.126.09, Python 3.12.3, and Qwen3-0.6B. The sealed attempt was replayed by
the same frozen finalizer after a permission-preserving off-host transfer, and
its raw artifacts and terminal closure were uploaded to versioned OSS objects.

Within the frozen Full-only, single-generation, single-action, private-tail
envelope, the candidate checked-demotion path produced exact physical frees and
allocator-visible capacity. Bypassing candidate behavior preserved the same
prepared device tail and capacity while releasing only target-session priority.
Seven safety/liveness controls rejected unsafe states or preserved stock eviction
as required. The result supports the G1 `PASS` branch rather than `STOP`.

This result strengthens the independently reviewed G1-C-010/A1 seven-arm PASS
with real `LOAD_BACK_PENDING` and `HOST_COPY_NOT_COMMITTED` controls. It does
not rewrite that earlier review or the preserved invalid attempts. The overall
project remains `roadmap`; G2 still owns asynchronous lifecycle correctness and
recovery, and G3 still owns comparison against the strongest simple baseline.

## Formal Attempt

| Field | Value |
| --- | --- |
| bundle | `G1-C-020` |
| attempt | `g1-c-020-a1-20260825T190159Z` |
| terminal | `PASS` |
| evidence scope | `formal_runtime` |
| ToolGap commit/tree | `e43ad7aabb7a8c0e4a17855a4745d91ba5945d96` / `47cc669e0c6f0a7c557d91eb61f4f8220dbb1a30` |
| SGLang base commit/tree | `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2` / `25e9bf86d04c27fe380024d9c8c421c3b5b51f3c` |
| patched SGLang commit/tree | `63df132ee1ca7db615976d5993a97d4a2b199c6d` / `7e80d29117b7b3e4b84f6023cfb888ac7c12de35` |
| external anchor SHA-256 | `7c82337eca8b98170296c2f867829c2f5ae5656f1958b5b22850349a514de440` |
| external anchor version | `CAEQnAYYgYCA6abn6YEaIiA5NjM3NjEzZGI4MDQ0NzEyODEwMWQwOWU3YjIxNjY3OQ--` |

External anchor:

`oss://agentic-kv-c0-evidence-20260812/g1/g1-c-020/e43ad7a/anchors/g1-c-020-a1-20260825T190159Z/external-anchor-7c82337eca8b98170296c2f867829c2f5ae5656f1958b5b22850349a514de440.json`

The anchor was downloaded after publication. Its SHA-256 and sole latest
non-delete OSS version matched the values above. It binds 194 unique indexed
artifact versions plus the terminal artifact index and completion receipt.

## Decisive Evidence

| Arm | Frozen observation |
| --- | --- |
| `enabled` | `ACCEPTED`; node 21 freed exact device IDs 257 through 264; allocator availability increased from 3832 to 3840; checked facade, checked backend, physical demote, and cache drain each executed once; stock eviction remained zero |
| `bypass` | `PRIORITY_RELEASE_ONLY`; allocator remained 3832; device IDs 257 through 264 remained resident; checked, physical-demote, drain, and stock-eviction counters remained zero |
| `reject_write_through_pending` | `DEFERRED/WRITE_THROUGH_PENDING`; capacity and physical residency did not change |
| `reject_non_target_session_coverage` | `DEFERRED/NON_TARGET_SESSION_COVERAGE`; the other session reference remained and no physical free occurred |
| `reject_device_locked` | `DEFERRED/DEVICE_LOCKED`; the live device lock remained and no physical free occurred |
| `reject_stale_generation` | `REJECTED/STALE_GENERATION` before priority release; no backend or physical call occurred |
| `stock_eviction_liveness` | candidate behavior remained bypassed while ordinary pressure reached one stock eviction and reclaimed 8 tokens from a real victim |
| `reject_load_back_pending` | `DEFERRED/LOAD_BACK_PENDING`; the real in-flight load-back had positive lock refs and `device_leaf=false`; capacity and physical residency did not change |
| `reject_host_copy_not_committed` | `DEFERRED/HOST_COPY_NOT_COMMITTED`; device IDs remained resident, capacity was unchanged, and all 8193 reserved host indices were returned |

All nine selectors reported `OK` in fresh process groups. The sealed cleanup
summary reports `listener_clean`, `pgid_clean`, and `gpu_delta_clean` for every
arm. A post-service check also found no GPU process or experiment listener.

## Frozen Source and Input Storage

The exact C020 ToolGap commit and tree above are present in local Git history.
The operator mirror keeps the permission-preserving sealed attempts under
`experiments/g1/raw/`, which is intentionally ignored by Git. OSS is the
off-host source of truth for frozen inputs and raw evidence.

The C020 input manifest SHA-256 is
`20f647309b3c23ec85b39441da23cbec5ec6befa3a77fc49b19c662853875802`.
The ToolGap portable source seed is:

`oss://agentic-kv-c0-evidence-20260812/g1/g1-c-020/e43ad7a/inputs/toolgap-g1-c-020-e43ad7a-portable-seed.tar.gz`

Its SHA-256 is
`ac7186dc8378053a1d06e0d467c18c20672d96e964d59c40de9f0a67ebc2453e`
and its OSS version ID is
`CAEQnAYYgYCA9bqT6YEaIiA4ZWMyNmI4ZmJlZTM0MzdkOWE5ZGJiYWM1ZTYwYmRmMQ--`.
The input receipt itself has SHA-256
`d046e3589c03fbf32e3d92cb8a9f4afc7413083a1c63411a56147086d90f00e4`
and OSS version ID
`CAEQnAYYgYCAw5KW6YEaIiBhMDhlMzM2MmUxNTQ0ZWFmYTc5NmY5ZmRlZTI3ODJmMw--`.
It binds the exact versions and hashes of the model, runtime wheel, SGLang
source seed, CUDA wheelhouse, provenance, bootstrap, and ToolGap source seed.

## Preserved Invalid Attempt

G1-C-019/A1 is retained as `pre_execution INVALID`. Its formal runner reached
the first arm but a marker placed inside a continued `timeout` command left
`timeout` without an executable and returned 125. It contributes no arm result
to the C020 PASS.

| Field | Value |
| --- | --- |
| bundle/attempt | `G1-C-019` / `g1-c-019-a1-20260825T170549Z` |
| terminal | `INVALID` at `pre_execution/formal_arms` |
| ToolGap commit | `8461d7bedab1a4a9bc3455eb9098757948bc3944` |
| external anchor SHA-256 | `398da39de1027fc918d9df82d547bd8d6ecd8ea96783e844d93fac273a5c0d9f` |
| external anchor version | `CAEQnAYYgYCA2bn16YEaIiA2YTBiYTE5MDQ4NzE0YmUwYTBhYTczZmU1MGI1YjI4MA--` |

External anchor:

`oss://agentic-kv-c0-evidence-20260812/g1/g1-c-019/8461d7b/anchors/g1-c-019-a1-20260825T170549Z/external-anchor-398da39de1027fc918d9df82d547bd8d6ecd8ea96783e844d93fac273a5c0d9f.json`

Earlier C008 and C009 invalid attempts and the independently reviewed C010 PASS
remain preserved under their original identities. No evidence was relabeled or
combined across attempts. The C010 review record remains
[`worklog/reviews/2026-08-25/g1-c-010-independent-evidence-review.md`](../../worklog/reviews/2026-08-25/g1-c-010-independent-evidence-review.md).

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
