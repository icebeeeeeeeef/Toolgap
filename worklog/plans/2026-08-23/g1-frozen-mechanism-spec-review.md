# G1 frozen mechanism SPEC review

> Status: completed
>
> Tracker: [G1: review the frozen mechanism SPEC](https://github.com/icebeeeeeeeef/Toolgap/issues/8)
>
> Canonical owners: [`docs/ROADMAP.md`](../../../docs/ROADMAP.md),
> [`docs/DEMOTION_CONTRACT.md`](../../../docs/DEMOTION_CONTRACT.md), and the
> future accepted `experiments/g1/SPEC.md`.

## Executable scope

- conduct the claimed Wayfinder grilling ticket one decision at a time;
- test whether the smallest G1 quiescent mechanism protocol can be frozen from
  the accepted source-path and allocator/bypass-oracle decisions;
- if and only if the owner accepts a complete contract, record the decision in
  the canonical G1 SPEC and resolve the tracker ticket; otherwise preserve the
  unresolved decision without beginning G1 execution.

## Boundaries

- no G1 implementation, GPU run, execution authorization, or Gate claim;
- no modification of the frozen G0 source pin, patch, artifacts, or results;
- no G2 lifecycle semantics, G3/G4 performance comparison, public API,
  dynamic policy, L3, prefetch, second physical data plane, or cache-backend
  replacement.

## Acceptance

- the review fixes or rejects the exact source identity, quiescent admission,
  forced enabled/bypass arms, evidence and invalid-attempt rules, sealing and
  independent-review requirements, and terminal `PASS`/`STOP` branches;
- the result is linked from the GitHub issue and preserves the project claim
  state as `roadmap`.

## Completion

The owner accepted the protocol through the Wayfinder grilling review. The
frozen protocol is [`experiments/g1/SPEC.md`](../../../experiments/g1/SPEC.md).
It freezes the G1 question and evidence boundary, while reserving exact source,
environment, and formal commands for a later owner-approved runtime revision
after implementation. See the linked tracker resolution and
[`g1-mechanism-protocol-decision.md`](../../reviews/2026-08-23/g1-mechanism-protocol-decision.md).
