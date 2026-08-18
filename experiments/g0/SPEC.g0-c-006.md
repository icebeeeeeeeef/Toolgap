# G0-C Atomic Checked-Demote Seam Specification

> Status: `roadmap`
>
> Specification state: `frozen`
>
> Revision: `G0-C-ATOMIC-006`
>
> Run identity: `g0-c-atomic-seam-006`
>
> Frozen at: `2026-08-17T16:50:27Z`
>
> Claim ceiling: fixed-source seam-contract evidence with registered fake
> backends; no real physical demotion, allocator, lifecycle, correctness, CUDA,
> or performance result

## 1. Correction and authority

This immutable revision corrects the complete independent-review report against
`G0-C-ATOMIC-005`. Revision 005 closed all eight blockers reported against 003,
but its oracle still did not distinguish seven credible wrong implementations:

1. release could clear non-target session contributions;
2. the cache caller could ignore/replace requested session identity;
3. a permanent-reject-first loop could skip later safe targets;
4. `host_lock_ref` could be used as an unsupported blanket device blocker;
5. per-node outcomes could carry the wrong target NodeId;
6. a legacy backend could be rejected before the required one-way release;
7. freed-ID observation could copy only the first ID of each returned value.

The 005 executable also inherited an initially unindexed test dependency. This
revision freezes both inherited dependency hashes before the new oracle exists:

| Executable dependency | Size | SHA-256 |
|---|---:|---|
| `artifacts/test_atomic_checked_demote_contract.py` | 23455 | `90a3aeb69f8ca9a23b8f77f0dafa8d04e2698116d79947fe4dac91dd9906fd95` |
| `artifacts/test_atomic_checked_demote_contract_v5.py` | 12654 | `f3ec1863a58d7e8cde1f68945cbaee7fb8d220dc88a4f0eadc5673528edf3cec` |

Revisions 001 through 005 remain preserved with `N/A` Gate decisions. The v5
source treatment itself needs no code change for these seven oracle gaps, so 006
reuses the exact retained four-file patch at
`artifacts/sglang-session-atomic-checked-demote-v5.patch`, size 11857, SHA-256
`e69776678909b4ee49b1c0fa4a8e208666893b659c0508387c83fcdf11e82a9a`.
The new oracle must still observe stock RED before the patch is applied to the
new 006 worktree.

The decisive question remains:

> Can one atomic upstream session checked-demote seam validate and release only
> the requested current generation, then have the registered TreeCore backend
> perform final live checks and invoke its existing `demote` primitive in the
> same backend call, while the cache remains the unique free-drain owner?

The source patch may wrap the existing upstream `demote` primitive. It may not
add a physical algorithm, allocator, movement path, second index, candidate
lifecycle executor, public API, retry loop, or background work. The oracle never
imports or invokes the real upstream physical implementation.

## 2. Fixed identities and configuration

| Field | Frozen value |
|---|---|
| Upstream | `https://github.com/sgl-project/sglang.git` |
| SGLang commit / tree | `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2` / `25e9bf86d04c27fe380024d9c8c421c3b5b51f3c` |
| Stock checkout | `/private/tmp/toolgap-kv-g0-sglang-92b1d382` |
| Patched checkout | `/private/tmp/toolgap-kv-g0-sglang-atomic-prototype-006` |
| Treatment patch | v5 retained patch, exact size/hash frozen above |
| Model / revision | `Qwen/Qwen2.5-0.5B-Instruct` / `c89bee90d9f811437d9735454613c35b4a3c4dc8` |
| Tokenizer | same repository and revision as model |
| Dependency source | fixed `python/pyproject.toml`, SHA-256 `c4d204a1d24f7ba87a150e0d563d8b946fd94c989c4e92985d488e088d424446` |
| Declared critical versions | Python `3.12.11`; Torch `2.13.0`; Transformers `5.12.1`; CUDA family `13.x` |
| Target testbed | Ubuntu `24.04.3` x86_64; one NVIDIA A10 24 GB; driver `580.65.06`; CUDA `13.0` |
| TreeCore / Host mode | `python` / `write_through` |
| Dtype / KV dtype | `bfloat16` / `bfloat16` |
| Context / page / max KV | `4096` / `16` / `4096` tokens |
| Memory / Host ratio | `0.70` / `2.0` |
| HiCache I/O / layout | `kernel` / `page_first` |
| TP / DP / scheduler / seed | `1` / `1` / `fcfs` / `20260817` |
| Session mode | session radix enabled; streaming disabled |
| L3/storage | disabled |

The resolved dependency lock is absent. The observed local host is macOS arm64
without CUDA, `python3.12`, SGLang, Torch, or Transformers. The unchanged stock
command is `commands/10-stock-hicache-smoke.sh`; it must remain `blocked before
execution` on this host, never success.

## 3. Atomic vertical contract

The only cache caller surface is:

```python
UnifiedRadixCache.checked_demote_session(session_id, generation)
    -> SessionCheckedDemoteOutcome
```

It validates Full-only scope and exact caller identity, snapshots the target
frontier, releases only that target contribution without close/tombstone, and
calls `TreeCoreInterface.demote_session_checked` for every snapshot NodeId. The
registered Python backend performs all final checks and calls its existing
`demote` only on success in that same synchronous method. The cache attempts
exact freed-ID observation, always enters its unique cleanup path, and returns
actual typed outcomes using keyword construction. No eligible capability or raw
`DemoteResult` escapes.

The interface default remains constructible and fail-closed: no physical call,
no result. For a valid Full-only current request, its permanent per-node reject
occurs after the one-way target release, like every other backend node outcome.
Only stale identity and unsupported component scope reject before release.

Final Python-backend predicates are: Full-only components, live NodeId, device
value, settled Host duplicate, zero device `lock_ref`, zero write/load pending
IDs, no resumable insert, no active eviction walk, zero remaining Full
`session_ref`, and current D-leaf/cascade safety. `host_lock_ref` alone is not a
device-demotion blocker.

## 4. Release and aggregate semantics

Current target release must mutate only the requested session contribution. A
non-target session's frontier and path coverage remain unchanged. The requested
session and generation must be forwarded unchanged to the tracker and echoed in
the typed result.

| Aggregate | Exact source-contract rule |
|---|---|
| `Accepted` | every frontier completed and at least one completed |
| `Clipped` | at least one completed and at least one deferred/rejected, independent of frontier order |
| `Deferred` | zero completed, at least one transient blocker, and no permanent reject |
| `Rejected` | stale/unsupported/empty, or zero completed with any permanent reject |

Transient reasons are write/load pending, device lock, structural owner,
remaining non-target coverage, Host copy not committed, and not-current-D-leaf.
Permanent reasons are unsupported backend/components, dead NodeId, and absent
device value. Every node outcome retains the exact requested NodeId and reason.

## 5. Executable counterexample oracle

`artifacts/test_atomic_checked_demote_contract_v6.py` verifies the two inherited
dependency hashes at process start, then inherits the 22 v5 cases. It overrides
accepted/mixed/dead/tracker cases to strengthen attribution and adds five new
cases, for exactly 27 unittest cases.

Required added or strengthened checks:

1. seed session-a and session-b on a shared coverage node; stale a changes
   nothing; current a removes only a while b frontier and coverage remain;
2. invoke the vertical cache caller with a non-default session, generation, and
   NodeId; assert exact tracker call and every observable outcome field;
3. dead-first plus safe-second still visits/demotes safe, records both exact
   NodeIds, and returns `CLIPPED`;
4. a positive Host lock with zero device lock and otherwise safe state completes;
5. accepted, reversed mixed, and dead outcomes record requested NodeIds;
6. a current request through a registered legacy backend releases once, then
   returns typed `REJECTED/UNSUPPORTED_BACKEND`, with no result or physical call;
7. one returned fake device value contains `(70, 71, 72)`; the typed outcome
   preserves every ID and the value is drained exactly once.

All inherited obligations remain required: actual interface/registry/outcome
types, legacy direct zero-side-effect default, stale/current tracker semantics,
mixed aggregate priorities, write/load distinction, Host commitment, non-target
coverage, device locks, structural zero-demote, transient D-leaf retry,
auxiliary-scope exclusion, dead/empty/device-absent branches, and cleanup after
success, observation failure, and drain failure.

## 6. Commands and retained artifacts

RED:

```bash
/opt/homebrew/bin/python3 \
  toolgap/experiments/g0/artifacts/test_atomic_checked_demote_contract_v6.py \
  --checkout /private/tmp/toolgap-kv-g0-sglang-92b1d382
```

GREEN:

```bash
/opt/homebrew/bin/python3 \
  toolgap/experiments/g0/artifacts/test_atomic_checked_demote_contract_v6.py \
  --checkout /private/tmp/toolgap-kv-g0-sglang-atomic-prototype-006
```

Required artifacts: finalized `manifest.g0-c-006.json`, immutable
`artifacts/g0-c-006-registration.json`, runtime blocker readbacks, v6 test plus
both hashed dependencies, reused exact patch, RED/GREEN summaries, patched
identity, updated matrices, independent review, and final verification.

## 7. Decision boundary

- `PASS` is impossible on stock because the contract is absent and no real
  physical/runtime result is produced.
- `RESHAPE` is allowed only if all 27 cases pass on the patched checkout, the
  exact patch adds no second ownership system, and a fresh independent review
  finds no blocker.
- `STOP` applies if correctness requires a broad backend rewrite, mutation-
  version ownership system, second physical index/data plane, or candidate-
  owned physical demotion algorithm.

Any change to fixed source/configuration, dependency hashes, test cases, or
branch requires a new immutable revision. This file is frozen after its checksum
enters the raw registration snapshot.
