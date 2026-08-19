# Test layout

> Status: `roadmap`; tests are added only with the authorized Gate that owns
> their behavior.

The test surface follows the same ownership split as the runtime:

- root tests cover the candidate module interface and fixed-pin adapter;
- `lifecycle/` belongs to G2 and covers resume, cancel, stale completion,
  duplicate operations, partial failure, and cleanup ledgers;
- `cuda/` belongs to G1/G2 and covers physical demotion, allocator-visible
  capacity, end-to-end recovery, and the candidate bypass/deletion test.

Tests must assert observable behavior through the candidate module interface or
the real SGLang seam. They must not turn fake-resource contract tests into a
claim about CUDA, allocator behavior, or performance.
