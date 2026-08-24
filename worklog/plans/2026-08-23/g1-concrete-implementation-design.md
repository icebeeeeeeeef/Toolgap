# G1 concrete implementation design

> Status: completed
>
> Tracker: [G1: design the concrete implementation and local verification plan](https://github.com/icebeeeeeeeef/Toolgap/issues/16)
>
> Canonical owners: [`experiments/g1/SPEC.md`](../../../experiments/g1/SPEC.md)
> and the Wayfinder map.

## Scope

- inspect the pinned SGLang source path needed to drive a normal request into
  the G1 test-only action;
- draft one source-backed changed-path, interface, and local-test design;
- identify which facts the existing G0 patch already exposes and which test-only
  observations still need a change;
- leave implementation, formal GPU execution, and Gate classification out of
  scope.

## Completion

The project owner accepted the resulting design on 2026-08-23. The separate
implementation-authorization review remains required; no code or formal GPU
execution is included in this plan.
