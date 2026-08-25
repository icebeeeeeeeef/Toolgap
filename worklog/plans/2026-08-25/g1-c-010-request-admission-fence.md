# G1-C-010 request admission fence

Canonical owner: `experiments/g1/SPEC.g1-c-010.md`

## Scope

- Preserve G1-C-009 as sealed `pre_execution INVALID`; do not rewrite or rerun it.
- Create a new G1-C-010 runtime revision from G1-C-009.
- Change only the test-only ordinary session request helper so `/generate`
  waits for the exact `rid` to reach the pinned scripted-runtime tokenizer
  receive proxy before scheduler-step completion polling begins.
- Keep the request payload, 400-step completion/frontier bounds, seven arms,
  checked-demote implementation, thresholds, finalizer, storage preflight,
  model, CUDA route, and claim state unchanged.
- Add a counterexample test proving a delayed background HTTP coroutine cannot
  consume the scheduler-step budget before admission.
- Regenerate C-010 identifiers, frozen patch binding, manifest tooling,
  verifier, anchor script, and input bundle. Run independent code/oracle review
  before another ECS attempt.

## Acceptance

- The RED test fails against the C-009 fire-and-forget helper.
- The GREEN helper uses the pinned upstream
  `_http_post_and_await_recv_msg` with an exact-`rid` predicate and retains the
  existing payload.
- The full C-010 verifier, patch application, frozen-artifact equality for
  C-001 through C-009, and independent review pass.
- A formal C-010 run is staged only after C-009 evidence is externally
  anchored and remote storage again satisfies the 24 GiB preflight.
