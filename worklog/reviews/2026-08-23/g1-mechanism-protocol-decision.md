# G1 mechanism protocol decision

> Status: accepted planning protocol; no implementation or GPU execution
>
> Tracker: [G1: review the frozen mechanism SPEC](https://github.com/icebeeeeeeeef/Toolgap/issues/8)
>
> Canonical owner: [`experiments/g1/SPEC.md`](../../../experiments/g1/SPEC.md)

## Decision question

What must be fixed before implementation so a later G1 GPU result can answer
one causal question without pretending that not-yet-written code is already
frozen?

## Evidence

The closed checked-path audit selects the cache facade, backend checks, cache
free drain, and upstream Full-KV allocator as the real route. The closed
allocator/bypass audit fixes the capacity reading and causal control. The owner
then accepted: a normal request must create the positive target; G1 proves only
immediate allocator capacity; all physical-completion and bypass conditions
are required; four unsafe cases reject; and formal GPU execution waits for a
separate owner-approved exact source/run revision.

## Decision

Freeze the G1 protocol in `experiments/g1/SPEC.md` now. It fixes the positive
path, enabled/bypass comparison, rejection cases, PASS/STOP/invalid branches,
and claim ceiling.

The existing four-file SGLang seam is the protocol starting point, not a
line-count limit. Implementation may change SGLang and/or ToolGap when needed
for the accepted result, provided the final runnable revision identifies every
behavior-changing change and does not replace SGLang's physical cache/data-plane
ownership.

Use two freezes:

1. this protocol freeze before implementation; then
2. a later exact source, environment, command, and artifact freeze before any
   formal GPU attempt, approved by the owner.

## Rejected alternatives

- treat a hand-built cache/tree/allocator state as the positive case;
- declare a formal experiment source patch frozen before implementation exists;
- allow source, workload, or analysis changes during a formal run;
- use a public API, G2 lifecycle path, performance comparison, or second
  physical data plane to make the first mechanism result easier to obtain.

## Canonical follow-up

The next frontier is [G1: authorize implementation of the accepted
protocol](https://github.com/icebeeeeeeeef/Toolgap/issues/9). It may authorize
local implementation only; a later Wayfinder ticket owns owner approval of the
final runnable source and formal GPU protocol.
