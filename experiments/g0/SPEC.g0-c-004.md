# G0-C Atomic Checked-Demote Seam Specification

> Status: `roadmap`
>
> Specification state: `frozen`
>
> Revision: `G0-C-ATOMIC-004`
>
> Run identity: `g0-c-atomic-seam-004`
>
> Frozen at: `2026-08-17T16:21:32Z`
>
> Claim ceiling: fixed-source seam-contract evidence with a registered fake
> backend; no real physical demotion, allocator, lifecycle, correctness, CUDA,
> or performance result

## 1. Correction and authority

This immutable revision corrects seven independent-review blockers in frozen
`G0-C-ATOMIC-003`:

1. the oracle did not observe that target contribution was really removed;
2. mixed completed/permanent and transient/permanent aggregate priorities were
   not distinguished;
3. `NOT_CURRENT_DEVICE_LEAF` was wrongly permanent even though removing a
   device-resident child can make the same intent legal;
4. structural-owner tests checked only a reason string and did not prove that
   physical demotion was skipped;
5. the legacy fail-closed test did not prove its inherited physical `demote`
   method was never called;
6. stale-generation safety was exercised only through a fake tracker rather
   than the actual patched tracker;
7. freed-ID observation happened before entering cleanup, so an observation
   failure could strand both device and Host resources.

Revisions 001 through 003, their manifests, tests, patches, and outputs remain
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
background work. The oracle must never invoke the real upstream physical
primitive; a registered fake backend supplies deterministic resources.

## 2. Fixed identities and configuration

| Field | Frozen value |
|---|---|
| Upstream | `https://github.com/sgl-project/sglang.git` |
| SGLang commit / tree | `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2` / `25e9bf86d04c27fe380024d9c8c421c3b5b51f3c` |
| Stock checkout | `/private/tmp/toolgap-kv-g0-sglang-92b1d382` |
| Patched checkout | `/private/tmp/toolgap-kv-g0-sglang-atomic-prototype-004` |
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
unchanged exact stock command is `commands/10-stock-hicache-smoke.sh`; this 004
attempt must remain `blocked before execution` on this host, not success.

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
-> cache attempts to copy observations and, even if that copy fails, drains the
   returned frees exactly once
-> cache returns only terminal per-node outcomes; no eligible capability escapes
```

`demote_session_checked` must be a concrete fail-closed interface method for
legacy/external registered backends. The Python backend overrides it. This
preserves backend construction while requiring explicit backend implementation
before any backend can demote through this seam.

Final backend predicates: Full-only components, live NodeId, device value,
settled Host duplicate, zero device component locks, zero write/load pending
IDs, no resumable insert, no active eviction walk, zero remaining Full
`session_ref`, and current D-leaf/cascade safety.

## 4. Release and aggregate semantics

For a current generation in Full-only scope, target priority release is a
one-way baseline action. It remains applied even when zero nodes are physically
demoted. The result records `priority_release=RELEASED`; there is no rollback,
hidden retry, or background work. A stale generation or unsupported component
set does not release anything.

The release is observed, not inferred: the actual tracker test must show exactly
one `release_session(session_id)` call, removal of that session from the
component frontier index, preservation of generation, and no close tombstone.

| Aggregate | Exact source-contract rule |
|---|---|
| `Accepted` | at least one fake physical demotion completed and every requested frontier completed |
| `Clipped` | at least one completed and at least one frontier was deferred or rejected; a permanent reject does not override a completion |
| `Deferred` | zero completed and at least one transient blocker exists, with no permanent reject |
| `Rejected` | stale/unsupported/empty target, or zero completed with any permanent reject; a permanent reject overrides transient blockers only in the zero-completed case |

Transient reasons: write pending, load pending, device lock, structural owner,
remaining non-target coverage, Host copy not committed, or not currently a
D-leaf. Permanent reasons: unsupported backend/components, dead NodeId, or
missing device value. G2 may later define bounded retries; G0 does not.

## 5. Executable counterexample oracle

The test first runs on untouched stock and must fail specifically because the
single cache surface, atomic backend method, and generation-preserving tracker
sub-step are absent. On the patched checkout it must:

- load the actual patched TreeCore interface with dependency stubs;
- construct both legacy and overriding fake backends through the actual fixed-
  pin `tree_core_registry.py`;
- prove the legacy backend remains constructible and fails closed with
  `demote_result is None` and zero calls to its recording physical method;
- bind the extracted Python atomic method to the overriding registered fake;
- bind the extracted cache method to fake cache state;
- never import or call the real physical TreeCore `demote` implementation.

Required cases:

1. stock cache/interface/tracker surfaces absent;
2. interface hunk required and legacy registered backend fails closed without
   invoking its physical method;
3. all-safe multi-frontier -> `Accepted`, one release, two fake demotes/drains;
4. safe plus write-pending and reversed write-pending plus safe -> `Clipped`;
5. safe plus dead NodeId -> `Clipped`, not `Rejected`;
6. write-pending plus dead NodeId -> `Rejected`, not `Deferred`;
7. all write/load pending -> `Deferred`, release persists, and a load-only case
   reports `LOAD_BACK_PENDING` distinctly;
8. dead/empty/device-absent target -> `Rejected`, release semantics explicit;
9. missing Host copy -> `Deferred`;
10. remaining non-target coverage and device lock -> `Deferred`;
11. insert and eviction walk -> `Deferred`, `demote_result is None`, and fake
    demote call count does not increase;
12. mutation during target release adds a device child -> `Deferred` and no
    demote; removing that child's device value allows the same captured intent
    to complete on a later direct backend attempt;
13. auxiliary component scope and fake stale generation -> reject before
    release;
14. on the actual tracker, a stale generation returns `None`, makes zero
    component release calls, and leaves frontier membership unchanged;
15. on the actual tracker, a current generation remains open, no tombstone is
    added, target frontier is removed, and the component observes exactly one
    release call;
16. cleanup success -> one owner and one drain per returned resource;
17. injected freed-ID observation failure -> no terminal success and both
    device and Host cleanup paths are attempted exactly once;
18. injected cleanup failure -> no terminal success; independent Host cleanup
    is attempted and any undrained resource retains one owner.

## 6. Commands and retained artifacts

RED:

```bash
/opt/homebrew/bin/python3 \
  toolgap/experiments/g0/artifacts/test_atomic_checked_demote_contract_v4.py \
  --checkout /private/tmp/toolgap-kv-g0-sglang-92b1d382
```

GREEN:

```bash
/opt/homebrew/bin/python3 \
  toolgap/experiments/g0/artifacts/test_atomic_checked_demote_contract_v4.py \
  --checkout /private/tmp/toolgap-kv-g0-sglang-atomic-prototype-004
```

Required artifacts: finalized `manifest.g0-c-004.json`, immutable
`artifacts/g0-c-004-registration.json`, stock blocker readbacks, the test,
retained patch, RED/GREEN summaries, patched identity, updated matrices, and
independent review.

## 7. Decision boundary

- `PASS` is impossible on stock because the atomic contract is absent and no
  real physical/runtime result is produced.
- `RESHAPE` is allowed only if the patch exposes exactly one cache caller
  surface, final check and existing physical primitive are in the same backend
  method, real registry construction is tested, every release/aggregate/
  structural/retry counterexample passes, the patch adds no second ownership
  system, and independent review finds no blocker.
- `STOP` applies if those properties require a broad backend rewrite, mutation-
  version ownership system, second physical index/data plane, or candidate-
  owned physical demotion algorithm.

Any change to fixed source/configuration, contract fields, test cases, or branch
requires a new immutable revision. This file is frozen after its checksum enters
the raw registration snapshot.
