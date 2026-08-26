# G1 concrete implementation and local-verification design

> Status: owner accepted the concrete implementation and local-verification
> design; no implementation or GPU run is authorized
>
> Claim state: `roadmap`
>
> Tracker: [G1: design the concrete implementation and local verification plan](https://github.com/icebeeeeeeeef/Toolgap/issues/16)
>
> Protocol authority: [`SPEC.md`](SPEC.md), revision `G1-PROTOCOL-001`

## 1. Decision this draft is meant to settle

G1 needs no new external endpoint and no ToolGap-owned runtime cache. It uses
the existing SGLang test-only scripted runtime to execute a normal `/generate`
request and, after that request has created the actual cache state, run the
one internal action in the scheduler process.

```text
normal SGLang request with a declared session id
-> SGLang creates/registers the real Full-KV tail
-> normal write-through Host acknowledgement completes
-> test-only scheduler script samples and invokes one existing SGLang method
-> script records the outcome, route counters, and allocator samples
```

The trigger is not an HTTP endpoint and is unavailable outside the test
runtime. The normal request is still an ordinary SGLang request; the script
neither creates nor mutates a tree node, device value, allocator entry, or
NodeId in the positive path.

## 2. Exact source shape

### SGLang runtime treatment: retain the existing four-file seam

The existing G0 treatment patch remains the only runtime change required by
this design:

| Path | Existing responsibility used by G1 |
| --- | --- |
| `python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py` | generation-checked priority release and source-owned frontier snapshot |
| `python/sglang/srt/mem_cache/unified_cache/unified_tree_core_interface.py` | typed backend result and fail-closed fallback |
| `python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py` | final live checks plus the existing physical demote |
| `python/sglang/srt/mem_cache/unified_radix_cache.py` | `checked_demote_session(session_id, generation)`, typed freed IDs, and cache-owned free drain |

The frozen input is `upstream/sglang/patches/0001-atomic-checked-demote.patch`,
applied to SGLang `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`.

### Fixed Full-only runtime prerequisite

The current checked facade rejects unless
`cache.tree_components == (BASE_COMPONENT_TYPE,)`. Therefore the G1 runtime
must use a non-SWA model and configuration. Before any arm runs, the test
records the component set, `cache.supports_swa()`, allocator class, and page
size, and requires the Full-only component set with SWA disabled.

Under that prerequisite, `cache.token_to_kv_pool_allocator.available_size()`
is the Full-KV capacity sample required by `SPEC.md`. G1 does not add an SWA
capacity branch. Supporting SWA would expand the checked-demote mechanism and
requires a separately reviewed protocol/runtime revision using the
source-appropriate Full-KV capacity method.

No ToolGap production module is added for G1. In particular, ToolGap does not
receive NodeIds, own a session-to-node map, call `tree_core.demote`, estimate
capacity, or move KV. Those would duplicate SGLang ownership without adding
evidence.

### One new SGLang test file

The implementation adds exactly one test module in the patched SGLang checkout:

```text
test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py
```

It is packaged with the G1 treatment as a separate test-only patch after the
four-file runtime patch. It may use the existing scripted-runtime helpers and
`unittest.mock` wrappers, but changes no SGLang production route. ToolGap
stores the patch and the later runner/evidence helpers under `upstream/sglang/`
and `experiments/g1/`; their exact names and hashes are frozen only after the
implementation review.

## 3. The test-only interface

The test script receives SGLang's existing `ScriptedContext`, whose
`scheduler.tree_cache` is the live cache used by the ordinary request. The
test supplies only the externally chosen session id and the generation that
SGLang itself assigned to that session. It invokes one of:

```python
# enabled arm
cache.checked_demote_session(session_id, generation)

# bypass arm
cache.session_refs.release_session_priority(session_id, generation)
```

The test never passes a NodeId into either action. The enabled facade resolves
the current frontier and performs final checks in SGLang; the bypass discards
the returned frontier IDs immediately.

The existing scripted runtime is the narrowest placement because it already:

- starts a real HTTP SGLang server;
- posts normal `/generate` traffic into its scheduler;
- runs the test function inside the scheduler process between scheduler steps;
- exposes the live scheduler only under `SGLANG_TEST_SCRIPTED_RUNTIME`.

Adding a new API route, scheduler command, daemon, or ToolGap RPC would make
the test larger without making the causal observation stronger.

## 4. Positive and bypass procedure

Each arm starts a fresh server process with the same source, model,
configuration, write-through Host cache, target request shape, and ordinary
eviction setting.

1. Send one ordinary `/generate` request carrying a unique session id. Wait
   for normal completion and assert that SGLang registered a non-root Full
   frontier for that session.
2. Wait until the real write-through acknowledgement is drained. Read only the
   actual frontier to require: a settled Host duplicate, no pending write or
   load-back, a private Full tail, and no active request. This is observation,
   not construction.
3. Recheck the fixed Full-only, non-SWA prerequisite. Read
   `cache.token_to_kv_pool_allocator.available_size()` and
   `allocator.is_not_in_free_group` as `C_before`.
4. Install immediate-window method wrappers. They count the checked facade,
   final checked backend, physical `demote`, and the stock eviction path; they
   do not alter their return values or free behavior. The script does not yield
   a scheduler step between installing these wrappers, taking `C_before`,
   running the action, and taking `C_after`.
5. Run exactly one enabled or bypass action, then take `C_after` after its
   normal return.
6. Seal the record before submitting another request.

The enabled record must show the typed checked outcome, a non-empty exact
`freed_device_ids`, the cache-owned drain's normal return, the expected route
counters, zero stock-eviction counters, and `C_after > C_before`. Because the
immediate action window contains no scheduler step, the zero stock-eviction
counter is a guard against accidental or future path changes, not independent
causal evidence. The bypass record must show priority release but no candidate
call, no physical free, and no immediate capacity gain.

## 5. Required rejection procedures

Each rejection is a fresh scripted-server run. This isolation is required
because `checked_demote_session` snapshots and permanently releases the target
session's priority before rows 1--3 reach the backend check. A same-generation
retry no longer has that frontier and normally reports `EMPTY_TARGET_FRONTIER`;
it is not a retry of the original unsafe state. The stale-generation row is
rejected before priority release.

Every rejection record contains `priority_release`,
`released_component_leaves`, the facade disposition/reason, every per-node
disposition/reason and `freed_device_ids`, the physical-route counters, and
`C_before`/`C_after`. Rows 1--3 require `priority_release="RELEASED"`; the stale
row requires `priority_release="NOT_RELEASED"`. Every row requires no physical
free and unchanged allocator capacity.

| Unsafe fact | How the test produces it with real SGLang behavior | Required result |
| --- | --- | --- |
| Host copy is not committed | Trigger after the normal request has created the session frontier but before the scheduler has consumed its write-through acknowledgement. | `priority_release="RELEASED"` and `WRITE_THROUGH_PENDING` or the source-equivalent deferred result. |
| Another session protects the target | Complete two ordinary requests with distinct session ids, identical cached token sequences, identical cache-key inputs, and deterministic greedy decoding. Before triggering the first, assert that both source-managed session frontiers contain the same target node and that its Full `session_ref` is `2`. | `priority_release="RELEASED"` and `NON_TARGET_SESSION_COVERAGE`. |
| Active request owns the target | Complete and back up the first request, then begin a second ordinary request in that session. Trigger on the existing target only after observing no structural owner, no write/load pending marker on that target, and its existing device lock greater than zero. | `priority_release="RELEASED"` and exactly `DEVICE_LOCKED`. If normal requests cannot create all preconditions together, stop rather than hand-setting any field or accepting another rejection. |
| Supplied identity is stale | Complete one session generation, close and reopen that session through existing SGLang session controls, then pass the old generation to the checked facade. | `priority_release="NOT_RELEASED"`, no node attempt, and `STALE_GENERATION`. |

For the shared-target row, `_session_leaves` indexes each session's current
frontier, while Full `session_ref` covers the path from that frontier toward the
root. The exact same-node assertion makes the intended remaining non-target
coverage deterministic instead of relying on generated sequences not to
diverge.

The backend checks structural ownership first, then device presence,
write-through pending, load-back pending, device lock, non-target coverage,
Host-copy settlement, and current device-leaf status. The active-request row is
therefore deliberately an admission check: it must establish that every check
before the device lock is clear and then observe exactly `DEVICE_LOCKED`. If
that cannot be reached on the fixed normal-request path, the owner reviews the
gap before any code or formal run claims this case covered.

## 6. Stock-eviction liveness control

After a bypass arm's immediate record is closed, start a separate fresh bypass
run. Submit one ordinary pressure request whose pre-registered allocation
demand exceeds the available Full-KV slots. A wrapper around SGLang's existing
eviction call records allocator capacity immediately before and after it and
the actual victim. This liveness wrapper is installed before submitting the
pressure request and remains installed across scheduler steps until the first
stock-eviction observation or the run timeout, then is removed. The test never
calls `cache.evict(...)` directly.

This control proves only that ordinary eviction still works. It is outside the
enabled/bypass capacity comparison and cannot repair or invalidate an earlier
immediate result.

## 7. Local checks before any formal GPU run

Implementation is complete only when all of these are reviewable:

1. the existing G0 source-contract tests still pass on the patched checkout;
2. the new scripted test is importable and its JSON record schema validates the
   component/allocator qualification, `priority_release`,
   `released_component_leaves`, facade and per-node outcomes, exact freed IDs,
   route counters, and capacity samples without claiming a GPU result;
3. static checks show the test has no HTTP route, public API, ToolGap runtime
   cache object, direct `tree_core.demote` call, or direct `cache.evict` call;
4. a source diff lists the four existing runtime files plus the one test file,
   or records and explains any smaller/different set discovered during local
   iteration;
5. every new observation field maps to a G1 `SPEC.md` requirement.

The owner then reviews the actual diff, source hashes, model/configuration,
workload size, repeat and timeout rules, evidence directory, and exact
commands as one frozen formal runtime revision. That later review—not this
draft—authorizes the first GPU attempt.

## 8. Accepted owner decision

On 2026-08-23, the project owner accepted this placement:

> Use SGLang's existing scripted test runtime for the internal G1 trigger and
> add no new public/external interface or ToolGap runtime module for G1.

The accepted shape is the retained four-file SGLang seam plus one test-only
scripted-runtime test module, with the Full-only, rejection-recording, and
control requirements above. This decision unblocks the separate implementation
authorization review. It does not authorize local code changes, a formal GPU
attempt, a Gate result, or any G2/G3/public-interface scope.
