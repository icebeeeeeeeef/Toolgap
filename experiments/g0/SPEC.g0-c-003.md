# G0-C Atomic Checked-Demote Seam Specification

> Status: `roadmap`
>
> Specification state: `frozen`
>
> Revision: `G0-C-ATOMIC-003`
>
> Run identity: `g0-c-atomic-seam-003`
>
> Frozen at: `2026-08-17T16:01:18Z`
>
> Claim ceiling: fixed-source seam-contract evidence with a registered fake
> backend; no real physical demotion, allocator, lifecycle, correctness, CUDA,
> or performance result

## 1. Correction and authority

This immutable revision corrects the independent review blockers in
`G0-C-ADMISSION-002`:

1. returning eligible NodeIds before a later `demote` left a TOCTOU window;
2. the fake core neither inherited nor used the maintained TreeCore interface
   and registry, so deleting the interface hunk still passed;
3. all/partial/zero-eligible aggregation and the persistence of target priority
   release were not specified;
4. missing Host copy, dead NodeId, and device-absent branches were not tested.

Both earlier revisions, their manifests, tests, patches, and outputs are
preserved as invalid protocol attempts with informative evidence. Neither is
decisive Gate evidence.

The decisive question is:

> Can one atomic upstream session checked-demote seam validate and release the
> current target generation, then have the registered TreeCore backend perform
> the final live check and invoke its existing `demote` primitive in the same
> backend call, while the cache remains the unique free-drain owner?

The retained source patch may wrap the already-existing upstream `demote`
primitive. It may not add a physical demotion algorithm, allocator, movement
path, second index, candidate lifecycle executor, public API, retry loop, or
background work. The G0 oracle must never invoke the real upstream physical
primitive; a registered fake backend supplies deterministic results.

## 2. Fixed identities and configuration

| Field | Frozen value |
|---|---|
| Upstream | `https://github.com/sgl-project/sglang.git` |
| SGLang commit / tree | `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2` / `25e9bf86d04c27fe380024d9c8c421c3b5b51f3c` |
| Stock checkout | `/private/tmp/toolgap-kv-g0-sglang-92b1d382` |
| Patched checkout | `/private/tmp/toolgap-kv-g0-sglang-atomic-prototype` |
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

The complete resolved dependency lock is absent and the observed local host is
macOS arm64 without CUDA, `python3.12`, SGLang, Torch, or Transformers. The
unchanged exact stock command is `commands/10-stock-hicache-smoke.sh`; its new
003 attempt must remain `blocked before execution` on this host, not success.

## 3. One atomic vertical contract

The only cache caller surface is:

```python
UnifiedRadixCache.checked_demote_session(session_id, generation)
    -> SessionCheckedDemoteOutcome
```

Its internal implementation may span the existing tracker, maintained TreeCore
interface, Python TreeCore, and cache wrapper:

```text
validate Full-only scope and exact generation
-> snapshot existing target frontiers before mutation
-> non-terminally release exactly that target contribution
-> for each snapshot NodeId call TreeCoreInterface.demote_session_checked
-> backend performs every final live predicate and, only if all hold, calls its
   existing demote primitive before returning
-> cache copies observations and drains the returned frees exactly once
-> cache returns only terminal per-node outcomes; no eligible capability escapes
```

`demote_session_checked` must be a concrete fail-closed interface method for
legacy/external registered backends. The Python backend overrides it. This
avoids breaking backend construction while requiring an explicit implementation
before any external backend can demote.

Final backend predicates: Full-only components, live NodeId, device value,
settled Host duplicate, zero device component locks, zero write/load pending
IDs, no resumable insert, no active eviction walk, zero remaining Full
`session_ref`, and current D-leaf/cascade safety.

## 4. Release and aggregate semantics

For a current generation in Full-only scope, target priority release is a
one-way baseline action. It remains applied even when zero nodes are physically
demoted. The result records `priority_release=RELEASED`; there is no hidden
rollback or background retry. A stale generation or unsupported component set
does not release anything.

| Aggregate | Exact source-contract rule |
|---|---|
| `Accepted` | at least one fake physical demotion completed and every requested frontier completed |
| `Clipped` | at least one completed and at least one frontier was deferred/rejected; every exclusion is retained |
| `Deferred` | zero completed and at least one transient blocker exists, with no permanent reject |
| `Rejected` | stale/unsupported/empty target, or zero completed with any permanent reject |

Transient reasons: write pending, load pending, device lock, structural owner,
remaining non-target coverage, or Host copy not committed. Permanent reasons:
unsupported backend/components, dead NodeId, missing device value, or not a
current D-leaf. G2 may later define bounded retries; G0 does not.

## 5. Executable counterexample oracle

The test first runs on untouched stock and must fail specifically because the
single cache surface, atomic backend method, and generation-preserving tracker
sub-step are absent. On the patched checkout it must:

- load the actual patched TreeCore interface with dependency stubs;
- construct both legacy and overriding fake backends through the actual fixed-
  pin `tree_core_registry.py`;
- prove the legacy backend remains constructible and fails closed;
- bind the extracted Python atomic method to the overriding registered fake;
- bind the extracted cache method to fake cache state;
- never import or call the real physical TreeCore `demote` implementation.

Required cases:

1. stock cache/interface/tracker surfaces absent;
2. interface hunk required and legacy registered backend fails closed;
3. all-safe multi-frontier -> `Accepted`, one release, two fake demotes/drains;
4. partial safe plus write-pending -> `Clipped`, release persists;
5. all write/load pending -> `Deferred`, release persists;
6. dead/empty/device-absent target -> `Rejected`, release semantics explicit;
7. missing Host copy -> `Deferred`;
8. remaining non-target coverage, device lock, insert, and eviction walk ->
   `Deferred`;
9. mutation during tracker release adds a device child before the atomic backend
   call -> no demote and stable reject;
10. auxiliary component scope and stale generation -> reject before release;
11. generation remains open and no tombstone is added;
12. cleanup success -> one owner and one drain per returned resource;
13. injected cleanup failure -> no terminal success; independent Host cleanup
    is attempted and any undrained resource retains one owner.

## 6. Commands and retained artifacts

RED:

```bash
/opt/homebrew/bin/python3 \
  toolgap/experiments/g0/artifacts/test_atomic_checked_demote_contract.py \
  --checkout /private/tmp/toolgap-kv-g0-sglang-92b1d382
```

GREEN:

```bash
/opt/homebrew/bin/python3 \
  toolgap/experiments/g0/artifacts/test_atomic_checked_demote_contract.py \
  --checkout /private/tmp/toolgap-kv-g0-sglang-atomic-prototype
```

Required artifacts: finalized `manifest.g0-c-003.json`, immutable
`artifacts/g0-c-003-registration.json`, stock blocker readbacks, the test,
retained patch, RED/GREEN summaries, patched identity, updated matrices, and
independent review.

## 7. Decision boundary

- `PASS` is impossible on stock because the atomic contract is absent and no
  real physical/runtime result is produced.
- `RESHAPE` is allowed only if the patch exposes exactly one cache caller
  surface, final check and existing physical primitive are in the same backend
  method, real registry construction is tested, all aggregate/release branches
  pass, the patch adds no second ownership system, and independent review finds
  no blocker.
- `STOP` applies if those properties require a broad backend rewrite, mutation-
  version ownership system, second physical index/data plane, or candidate-
  owned physical demotion algorithm.

Any change to fixed source/configuration, contract fields, test cases, or branch
requires a new immutable revision. This file is frozen after its checksum enters
the raw registration snapshot.
