# G1 real checked-demote path audit

> Status: completed
>
> Tracker: [G1: audit the real checked-demote path](https://github.com/icebeeeeeeeef/Toolgap/issues/7)
>
> Canonical owners: [`docs/ARCHITECTURE.md`](../../../docs/ARCHITECTURE.md),
> [`docs/DEMOTION_CONTRACT.md`](../../../docs/DEMOTION_CONTRACT.md), and the
> future accepted `experiments/g1/SPEC.md`.

## Executable scope

- audit the exact G0 patch, its source-contract oracle, and the fixed upstream
  source around the caller, backend, final eligibility, physical demote, and
  free-drain observations;
- distinguish what is source-proven from what G1 must observe on the real
  engine;
- record the narrowest G1 SPEC inputs and the precise stop condition if the
  seam cannot be used without widening ownership.

## Boundaries

- no G1 implementation, frozen SPEC, runtime/GPU run, or claim-state change;
- no alternate upstream pin, second physical index, allocator replacement,
  public pause API, or G2 lifecycle design.

## Completion

The audit is recorded in
[`g1-real-checked-demote-path-audit.md`](../../reviews/2026-08-22/g1-real-checked-demote-path-audit.md).
It selects the already reviewed, four-file SGLang seam as the only G1 physical
route and leaves its real-CUDA observation to the future accepted G1 SPEC.
