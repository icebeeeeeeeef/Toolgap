# G0-C Atomic Checked-Demote Seam Specification

> Status: `roadmap`
>
> Specification state: `frozen`
>
> Revision: `G0-C-ATOMIC-005`
>
> Run identity: `g0-c-atomic-seam-005`
>
> Frozen at: `2026-08-17T16:29:20Z`
>
> Claim ceiling: fixed-source seam-contract evidence with a registered fake
> backend; no real physical demotion, allocator, lifecycle, correctness, CUDA,
> or performance result

## 1. Correction and authority

This immutable revision closes the complete independent-review report against
frozen `G0-C-ATOMIC-003`. It carries forward the seven corrections registered
in 004 and adds the eighth: execute the actual cache outcome class definitions,
not surrogate dataclasses. Revision 004 was invalidated after its registration
receipt and before any preflight, test, patch, or prototype execution because
that eighth requirement was missing.

The eight corrected counterexamples are:

1. actual target release must be observed;
2. actual stale-generation release must have zero side effects;
3. mixed aggregate priorities and frontier order must be distinguished;
4. not-current-D-leaf is transient when the same intent can later become legal;
5. structural blockers must prove zero physical calls and no result;
6. legacy fail-closed must prove zero physical calls and no result;
7. observation failure must still enter the unique cleanup path;
8. actual cache outcome definitions must be executed and observed.

Revisions 001 through 004, their manifests, tests, patches, and outputs are
preserved as invalid protocol attempts with informative evidence. None is
decisive Gate evidence.

The decisive question is:

> Can one atomic upstream session checked-demote seam validate and release the
> current target generation, then have the registered TreeCore backend perform
> the final live check and invoke its existing `demote` primitive in the same
> backend call, while the cache remains the unique free-drain owner?

The retained source patch may wrap the already-existing upstream `demote`
primitive. It may not add a physical demotion algorithm, allocator, movement
path, second index, candidate lifecycle executor, public API, retry loop, or
background work. The oracle never imports or invokes the real upstream physical
implementation; a registered fake backend supplies deterministic resources.

## 2. Fixed identities and configuration

| Field | Frozen value |
|---|---|
| Upstream | `https://github.com/sgl-project/sglang.git` |
| SGLang commit / tree | `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2` / `25e9bf86d04c27fe380024d9c8c421c3b5b51f3c` |
| Stock checkout | `/private/tmp/toolgap-kv-g0-sglang-92b1d382` |
| Patched checkout | `/private/tmp/toolgap-kv-g0-sglang-atomic-prototype-005` |
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

The complete resolved dependency lock is absent. The observed local host is
macOS arm64 without CUDA, `python3.12`, SGLang, Torch, or Transformers. The
unchanged exact stock command is `commands/10-stock-hicache-smoke.sh`; its 005
attempt must remain `blocked before execution` on this host, never success.

## 3. One atomic vertical contract

The only cache caller surface is:

```python
UnifiedRadixCache.checked_demote_session(session_id, generation)
    -> SessionCheckedDemoteOutcome
```

Its implementation may span the existing tracker, maintained TreeCore
interface, Python TreeCore, and cache wrapper:

```text
validate Full-only scope and exact generation
-> snapshot existing target frontiers before mutation
-> non-terminally release exactly that target contribution
-> for each snapshot NodeId call TreeCoreInterface.demote_session_checked
-> backend performs every final live predicate and, only if all hold, calls its
   existing demote primitive before returning
-> cache attempts observation and always enters the unique free-drain path
-> cache returns actual typed outcomes; no eligible capability escapes
```

`demote_session_checked` is a concrete fail-closed interface method for legacy
or external registered backends. The Python backend overrides it. The default
must never call `demote` and must return no `demote_result`.

The Python backend performs the final predicates: Full-only components, live
NodeId, device value, settled Host duplicate, zero device component locks, zero
write/load pending IDs, no resumable insert, no active eviction walk, zero
remaining Full `session_ref`, and current D-leaf/cascade safety. The current
D-leaf check and existing physical primitive occur in the same synchronous
backend method, so no eligible NodeId or version capability escapes.

The cache uses the actual `SessionNodeDemoteOutcome` and
`SessionCheckedDemoteOutcome` class definitions. Every construction uses keyword
arguments so field reordering cannot silently corrupt the observable contract.

## 4. Release and aggregate semantics

For a current generation in Full-only scope, target priority release is a
one-way baseline action. It remains applied even when zero nodes are physically
demoted. The result records `priority_release=RELEASED`; there is no rollback,
hidden retry, or background work. A stale generation or unsupported component
set does not release anything.

The actual tracker test must observe exactly one
`release_session(session_id)` call, removal of that session from the component
frontier index, preservation of generation, and no close tombstone. A preceding
stale call must return `None`, make zero release calls, and leave the frontier
unchanged.

| Aggregate | Exact source-contract rule |
|---|---|
| `Accepted` | at least one fake physical demotion completed and every requested frontier completed |
| `Clipped` | at least one completed and at least one frontier was deferred or rejected; a permanent reject does not override a completion |
| `Deferred` | zero completed and at least one transient blocker exists, with no permanent reject |
| `Rejected` | stale/unsupported/empty target, or zero completed with any permanent reject; a permanent reject overrides transient blockers only when zero completed |

Transient reasons: write pending, load pending, device lock, structural owner,
remaining non-target coverage, Host copy not committed, or not currently a
D-leaf. Permanent reasons: unsupported backend/components, dead NodeId, or
missing device value. G2 may later define bounded retries; G0 does not.

## 5. Executable counterexample oracle

The test runs first on untouched stock and must fail because the atomic cache,
interface, backend, tracker, and actual outcome surfaces are absent. On the
patched checkout it must load the actual interface and registry with dependency
stubs; extract the actual outcome class definitions and the tracker/cache/core
methods; construct legacy and overriding backends through the actual registry;
and never import or invoke the real physical `demote` implementation.

The 22 registered unittest cases cover:

1. every vertical surface, including both actual cache outcome classes;
2. legacy registered backend construction, `REJECTED/UNSUPPORTED_BACKEND`, no
   result, and zero recording physical calls;
3. all-safe multi-frontier -> `Accepted`, actual outcome instances, one release,
   two fake demotes, and one drain per returned resource;
4. safe-first plus write-pending and pending-first plus safe-second -> `Clipped`
   with only the safe frontier demoted;
5. safe plus dead -> `Clipped`;
6. write-pending plus dead -> `Rejected`;
7. write and load pending -> `Deferred` with distinct per-node reasons;
8. load-only -> `Deferred/LOAD_BACK_PENDING`;
9. dead, empty, and device-absent target -> `Rejected`, with explicit release;
10. missing Host copy -> `Deferred`;
11. non-target coverage and device lock -> `Deferred`;
12. insert and eviction walk -> `Deferred`, no result, and no increase in
    recording physical calls;
13. release mutation adds a device child -> `Deferred` and no demote; clearing
    that child device value lets the same NodeId intent complete later;
14. auxiliary component scope and fake stale generation -> reject before
    release;
15. actual stale tracker call -> `None`, no release, unchanged frontier;
16. actual current tracker call -> exactly one release, removed frontier,
    preserved generation, no close tombstone;
17. freed-ID observation failure -> no terminal result and both device and Host
    cleanup attempted exactly once;
18. cleanup failure -> no terminal result, independent Host cleanup attempted,
    and any undrained resource retains exactly one owner.

## 6. Commands and retained artifacts

RED:

```bash
/opt/homebrew/bin/python3 \
  toolgap/experiments/g0/artifacts/test_atomic_checked_demote_contract_v5.py \
  --checkout /private/tmp/toolgap-kv-g0-sglang-92b1d382
```

GREEN:

```bash
/opt/homebrew/bin/python3 \
  toolgap/experiments/g0/artifacts/test_atomic_checked_demote_contract_v5.py \
  --checkout /private/tmp/toolgap-kv-g0-sglang-atomic-prototype-005
```

Required artifacts: finalized `manifest.g0-c-005.json`, immutable
`artifacts/g0-c-005-registration.json`, stock blocker readbacks, the v5 test,
retained v5 patch, RED/GREEN summaries, patched identity, updated matrices,
independent review, and final verification.

## 7. Decision boundary

- `PASS` is impossible on stock because the contract is absent and no real
  physical/runtime result is produced.
- `RESHAPE` is allowed only if the patch exposes exactly one cache caller
  surface, final check and existing physical primitive are in the same backend
  method, actual interface/registry/outcome types are tested, every registered
  counterexample passes, the patch adds no second ownership system, and a fresh
  independent review finds no blocker.
- `STOP` applies if those properties require a broad backend rewrite, mutation-
  version ownership system, second physical index/data plane, or candidate-
  owned physical demotion algorithm.

Any change to fixed source/configuration, contract fields, test cases, or branch
requires a new immutable revision. This file is frozen after its checksum enters
the raw registration snapshot.
