# G2 Wayfinder map

> Status: charted
>
> Canonical owners: [`docs/ROADMAP.md`](../../../docs/ROADMAP.md) and
> [`docs/DEMOTION_CONTRACT.md`](../../../docs/DEMOTION_CONTRACT.md)
>
> Tracker: [Wayfinder: G2 lifecycle correctness and recovery](https://github.com/icebeeeeeeeef/Toolgap/issues/19)

## Executable scope

- create one GitHub Wayfinder map for a reviewable terminal decision for G2 —
  Lifecycle Correctness and Recovery;
- chart only decision and investigation tickets needed to establish lifecycle
  safety, recovery/fallback, cleanup, and evidence integrity;
- use GitHub issue bodies for parent and blocker links when its available
  interface lacks native child/dependency operations;
- resolve at most one ticket per session after the map is created.

## Boundaries

- This worklog is not a second Gate roadmap, a frozen G2 SPEC, or runtime
  authorization.
- G2 must preserve SGLang ownership of the physical KV tree, allocator,
  residency, movement, eviction, and model execution. ToolGap may own logical
  lifecycle identity, admissibility, idempotence, cancellation, fallback,
  cleanup orchestration, and DecisionTrace.
- G3/G4 comparisons, dynamic policy, L3/prefetch, distributed claims, and a
  second physical KV data plane are out of scope. G2 may decide the smallest
  lifecycle-intent ingress, but must not presume that a public pause API is
  needed or authorized.
- GitHub Issues is the canonical map. The local GitHub CLI credential is not
  used for this work.

## Completion

The GitHub map exists with a `wayfinder:map` parent, child issues labelled by
type, and explicit body-based blocking links. It is a planning artifact only;
it does not close a G2 decision or upgrade the project beyond `roadmap`.
