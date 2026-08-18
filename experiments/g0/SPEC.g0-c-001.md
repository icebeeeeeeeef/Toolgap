# G0-C Seam-Contract Prototype Specification

> Status: `roadmap`
>
> Specification state: `frozen`
>
> Revision: `G0-C-SEAM-001`
>
> Run identity: `g0-c-seam-contract-001`
>
> Frozen at: `2026-08-17T15:17:32Z`
>
> Claim ceiling: fixed-source interface-gap evidence only; no stock-engine,
> allocator-visible, recovery, lifecycle, or performance claim

## 1. Parent and decision purpose

This revision is downstream of immutable `G0-SOURCE-001`. The parent source
audit selected exactly one Host mode, `write_through`, because the fixed source
defines an authoritative D2H ack and a settled Host-duplicate predicate for
that mode.

This run does not attempt a stock HiCache server smoke. Its only executable arm
is a red/green contract test for the narrowly missing upstream session-control
operation:

```text
generation-checked session frontier snapshot
+ target-only component priority release
+ preserved open generation
```

The prototype does not implement checked physical demotion. It only tests that
the upstream part of the proposed cache-level checked-demote facade can be
expressed as one small internal contract without a second ownership index.

## 2. Frozen source and patch identity

| Field | Frozen value |
|---|---|
| Upstream | `https://github.com/sgl-project/sglang.git` |
| Commit | `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2` |
| Commit tree | `25e9bf86d04c27fe380024d9c8c421c3b5b51f3c` |
| Stock checkout | `/private/tmp/toolgap-kv-g0-sglang-92b1d382` |
| Patched checkout | `/private/tmp/toolgap-kv-g0-sglang-seam-prototype` |
| Candidate repository HEAD | `db0b4fa8c8b530fb78e2242328b48bc292b83255` |
| Intended patch surface | `python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py` only |
| Patch artifact | `toolgap/experiments/g0/artifacts/sglang-session-priority-release.patch` |
| Contract test | `toolgap/experiments/g0/artifacts/test_priority_release_contract.py` |

The patched checkout must start detached at the exact stock commit. The red
test runs against the untouched stock checkout. Only after the expected red
result may the patch be applied to the separate prototype checkout.

## 3. Frozen configuration and environment

| Runtime/config field | Frozen value |
|---|---|
| Host write mode | `write_through` |
| Mode source oracle | settled Host duplicate requires device+Host with both pending IDs clear; D2H ack synchronization precedes pending clear |
| Model and revision | `N/A: no stock runtime is admitted on this non-CUDA host` |
| Tokenizer/template revision | `N/A: no model or request is loaded` |
| Dtype | `N/A: source-interface test creates no KV tensors` |
| Page size | `N/A: source-interface test creates no allocator` |
| Context limit | `N/A: no request is run` |
| Cache flags | `N/A: no server starts; semantic mode is fixed to write_through` |
| Memory fraction | `N/A: no device pool is created` |
| GPU | `N/A: local host is macOS arm64 with no CUDA-compatible device` |
| OS | `macOS 15.7.4 build 24G517, arm64` |
| Python | `/opt/homebrew/bin/python3`, `Python 3.14.2` |
| Dependency environment | Python standard library only; upstream module is loaded by file path |
| Workload | deterministic in-memory fake components and node IDs; no engine workload |
| Seeds/arrival process | `N/A: deterministic contract test` |
| SLO/statistics | `N/A: no treatment or performance measurement` |

The missing CUDA runtime is not used to justify PASS or to infer physical
behavior. A stock server command is intentionally not fabricated: G0 remains
`RESHAPE`, and runtime admission requires the missing contract to be accepted,
pinned, and frozen in a later SPEC.

## 4. Contract oracle

The wished-for internal method is:

```python
release_session_priority(session_id: str, generation: int)
    -> SessionPriorityRelease | None
```

Required behavior:

1. stale or absent generation fails closed and mutates nothing;
2. the current frontier node IDs for every component are snapshotted before
   release from the already-owned `_session_leaves` index;
3. only the target session's component contributions are released;
4. the current generation remains registered and no close tombstone is added;
5. the return is immutable and carries the generation, frontier IDs, and
   released frontier count;
6. disabled tracking is a no-op.

This is an internal scheduler-thread contract, not a public pause API. The full
proposed cache facade must consume the snapshot synchronously, revalidate live
tree/transfer predicates, and call the existing physical path in the same
scheduler-thread operation. Returning the snapshot to an external orchestrator
would be an unsafe implementation and is not authorized.

## 5. Red/green commands and failure accounting

Red command:

```bash
/opt/homebrew/bin/python3 \
  toolgap/experiments/g0/artifacts/test_priority_release_contract.py \
  --checkout /private/tmp/toolgap-kv-g0-sglang-92b1d382
```

Expected red oracle: non-zero exit and assertions naming the missing
`release_session_priority` contract. Import, syntax, path, or fixture errors do
not count as the expected red result.

Green command:

```bash
/opt/homebrew/bin/python3 \
  toolgap/experiments/g0/artifacts/test_priority_release_contract.py \
  --checkout /private/tmp/toolgap-kv-g0-sglang-seam-prototype
```

Expected green oracle: zero exit with every contract test passing. The patched
checkout must still report the frozen upstream commit as `HEAD`; its dirty diff
must equal the retained patch artifact.

All stdout/stderr and exit codes are retained. A red result for an unintended
reason invalidates the attempt. A green result does not prove physical demotion,
allocator release, recovery, or end-to-end runtime behavior.

## 6. Artifacts

- `manifest.g0-c-001.json`;
- `artifacts/test_priority_release_contract.py`;
- `artifacts/sglang-session-priority-release.patch`;
- `artifacts/g0-c-red.txt`;
- `artifacts/g0-c-green.txt`;
- `artifacts/g0-c-patched-identity.txt`;
- `artifacts/priority-release.md`;
- `artifacts/session-to-leaf.md`;
- `artifacts/checked-demote-interface.md`.

## 7. Outcome boundary

- This contract test may support only `RESHAPE`: a single narrow missing
  upstream contract is representable by a small patch and a test that fails on
  stock.
- It cannot support `PASS`, because stock lacks the contract and no physical
  runtime is executed.
- It supports `STOP` only if the test reveals that the contract requires a
  second ownership index or broad backend replacement.

Any change to the source commit, contract oracle, patch surface, or executable
commands requires a new revision and run identity.
