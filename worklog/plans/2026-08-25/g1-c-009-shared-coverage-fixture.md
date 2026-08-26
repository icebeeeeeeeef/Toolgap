# G1-C-009 shared coverage and rejection oracle

Canonical owner: `experiments/g1/SPEC.g1-c-009.md`.

## Goal

Preserve sealed C-008 attempt `g1-c-008-a1-20260825T053604Z` and issue one
minimal successor after two ordinary, session-native requests produced distinct
private frontiers `(21,)` and `(24,)` instead of the required shared target.
Also correct the offline oracle exposed by the same attempt: deferred facade
reasons are aggregate `DEFERRED`, while the specific rejection reason belongs
to each node outcome.

## Executable scope

- Copy the complete C-008 bundle to C-009 identities without editing C-001
  through C-008 or their three frozen patches.
- Keep the first ordinary request as the owner of the real settled Full node.
  For only the non-target-coverage rejection, create a second current session
  generation and register it on that real leaf through SGLang's existing
  `register_session_leaf` API. This mutates only source-owned logical coverage;
  it does not construct or alter a tree node, KV value, allocator entry, or the
  checked-demote mechanism.
- Replace patch 0002 with a C-009-specific test-only variant; patches 0001 and
  0003, model, wheel, selectors, mechanism, cleanup, terminals, and claim state
  stay fixed.
- Add a local focused counterexample that reproduces the old distinct-frontier
  equality failure and executes the new source helper against an invariant-
  maintaining fake component.
- Correct only the C-009 finalizer fixture/oracle mapping: the three backend
  deferrals require facade `DEFERRED/DEFERRED` plus arm-specific node reasons;
  stale generation requires facade `REJECTED/STALE_GENERATION`, no backend,
  and no node outcome. Add focused facade/node counterexamples.

## Verification

Capture focused RED results before both repairs, then run every focused C-009
test, `bash scripts/verify-g1-c-009-bundle.sh`, predecessor equality, and
`git diff --check 937eb86..HEAD`.

## Boundaries

No ECS, OSS, remote cleanup, `rm`, Gate decision, or change to
`docs/DECISIONS.md`, `CONTEXT.md`, or any frozen C-001 through C-008 file is in
scope.
