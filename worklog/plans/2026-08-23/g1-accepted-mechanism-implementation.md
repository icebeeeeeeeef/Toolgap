# G1 accepted mechanism implementation

> Status: implementation artifact ready; local runtime validation blocked
>
> Tracker: [G1: implement the accepted mechanism protocol](https://github.com/icebeeeeeeeef/Toolgap/issues/12)
>
> Canonical owners: [`experiments/g1/SPEC.md`](../../../experiments/g1/SPEC.md),
> [`experiments/g1/IMPLEMENTATION_DESIGN.md`](../../../experiments/g1/IMPLEMENTATION_DESIGN.md),
> and [`docs/DEMOTION_CONTRACT.md`](../../../docs/DEMOTION_CONTRACT.md)

## Goal

Deliver the owner-authorized local SGLang implementation treatment: preserve the
accepted four-file checked-demote seam at the pinned SGLang source commit and
add one test-only scripted-runtime module that records the G1 protocol
observations. This ticket does not run a formal GPU experiment or select a G1
Gate outcome.

## Source and scope

`upstream/sglang/` deliberately stores patch/test integration material rather
than a vendored SGLang source tree. Work therefore happens in a fresh temporary
checkout at `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`, with the existing
`upstream/sglang/patches/0001-atomic-checked-demote.patch` applied. The durable
repository changes are the reviewed treatment/test patch material and this
plan/review record, not a copy of upstream SGLang.

Permitted runtime paths:

- `python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py`
- `python/sglang/srt/mem_cache/unified_cache/unified_tree_core_interface.py`
- `python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py`
- `python/sglang/srt/mem_cache/unified_radix_cache.py`

Permitted new test path:

- `test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py`

No public HTTP route, ToolGap runtime cache module, direct test call to
`tree_core.demote` or `cache.evict`, second physical KV data plane, GPU run,
G2 lifecycle behavior, or performance claim is in scope.

## Execution steps

1. Materialize a disposable source checkout at the fixed commit, verify its
   commit/tree identity, and apply the frozen four-file patch without modifying
   those runtime files.
2. Inspect the pinned scripted-runtime helpers and cache/session request path;
   record any source constraint that makes a required G1 row unreachable rather
   than simulating it by mutating cache internals.
3. Add `test_toolgap_g1_forced_demote.py` first. Its importable JSON schema must
   cover component/allocator qualification, priority release, released leaves,
   facade/per-node outcomes, exact freed IDs, route counters, and capacity
   samples. Run the focused test to observe its expected initial failure.
4. Implement only the test-only harness required to make that focused test pass:
   use normal `/generate` traffic and the scripted scheduler context, invoke
   exactly one enabled facade or bypass priority release, and retain the
   enabled/bypass/rejection/stock-liveness records required by the frozen design.
5. Generate a narrow treatment patch containing the one test module alongside
   the unchanged frozen runtime seam; audit its changed-path inventory and
   source for prohibited routes/calls.
6. Run the existing G0 source-contract tests against the patched checkout, the
   new focused/import/schema/static checks, and final diff inspection. Record
   all local evidence and unverified GPU boundaries in the implementation review.
7. After implementation evidence is available, ask independent reviewers to
   inspect the diff, protocol coverage, and verification. Reproduce every
   credible finding locally before resolving this ticket.

## Completion criteria

- Local checks satisfy `IMPLEMENTATION_DESIGN.md` section 7 without presenting
  them as a GPU result.
- The durable diff names only the existing patch/integration material, the new
  scripted test patch, and required worklog evidence; every behavioral source
  path remains within the five authorized SGLang files.
- Independent review has no unresolved finding, and final commands are run
  after the last code change.

## Implementation result

The test-only treatment is recorded as
`upstream/sglang/patches/0002-g1-scripted-forced-demote.patch`. It applies after
the frozen four-file `0001` seam at
`92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`; its only new upstream path is the
authorized scripted-runtime test module. The final clean replay passed patch
application, `git diff --check`, Python syntax compilation, SGLang CI marker
parsing, prohibited-call/route scanning, and the G0 direct-call inventory.

Independent code, protocol, and evidence reviews found no unresolved P1/P2 in
the final replay. The implementation repaired two target-alignment defects
found during review by reconstructing the completed frontier key for the H2D
pending loader and the device-lock active request; it also fixes `page_size=1`
for that key identity.

The local import/schema test and retained G0 installed-contract test cannot run
on this machine because importing pinned SGLang fails at `import triton`.
Therefore `IMPLEMENTATION_DESIGN.md` section 7 is not fully satisfied, no GPU
behavior or G1 Gate result is claimed, and issue #12 remains open pending the
pinned Linux CUDA/Triton environment.
