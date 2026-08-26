# G1 allocator and bypass evidence oracle

> Status: completed
>
> Tracker: [G1: define the allocator and bypass evidence oracle](https://github.com/icebeeeeeeeef/Toolgap/issues/10)
>
> Canonical owners: [`docs/ROADMAP.md`](../../../docs/ROADMAP.md),
> [`docs/DEMOTION_CONTRACT.md`](../../../docs/DEMOTION_CONTRACT.md), and the
> future accepted `experiments/g1/SPEC.md`.

## Executable scope

- inspect only the fixed SGLang revision and reviewed G0 patch to identify the
  upstream-owned allocator observation, physical-completion readback, and
  cache-owned free-drain boundary;
- define the enabled/bypass pair that preserves publication, target-priority
  release, workload, and ordinary stock eviction while removing only the
  candidate checked-demote invocation;
- produce a pre-registrable observation order and PASS/STOP evidence shapes
  for the future G1 SPEC.

## Boundaries

- no GPU run, G1 implementation, frozen SPEC, source-pin change, or claim-state
  change;
- no ToolGap allocator adapter, cache tree, independent physical mover, stock
  eviction change, public API, or G2 lifecycle fencing.

## Completion

The source-backed findings are recorded in
[`g1-allocator-bypass-evidence-oracle.md`](../../reviews/2026-08-23/g1-allocator-bypass-evidence-oracle.md).
They are an input to the subsequent G1 SPEC review, not a Gate result or an
authorization to execute a GPU experiment.
