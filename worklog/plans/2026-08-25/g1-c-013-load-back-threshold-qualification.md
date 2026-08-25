# G1-C-013 load-back threshold qualification

Canonical owner: `experiments/g1/SPEC.g1-c-013.md`

## Trigger

Formal attempt `g1-c-012-a1-20260825T123410Z` sealed `INVALID` after its first
seven arms passed. The load-back arm used an eight-token Host-only frontier,
but pinned SGLang requires at least ten Full-KV tokens before it starts a
load-back. The request therefore recomputed its tail and never created the
pending state required by the rejection row.

## Executable scope

- Create a complete G1-C-013 bundle mechanically from G1-C-012 while preserving
  the source, model, runtime, CUDA target, nine arms, and terminal oracle.
- Let the private-session helper accept an arm-specific generation length. Only
  the load-back arm derives that length from the pinned runtime's
  `load_back_threshold`, with a two-token margin.
- Before pressure and loader submission, require the exact target's committed
  Full Host value to contain at least `load_back_threshold` tokens.
- Preserve the appended loader token, exact pending-anchor identity checks,
  production-guard mutation, and suffix-removal counterexample.
- Add a mutation proving that restoring the load-back setup to eight generated
  tokens violates the explicit threshold qualification.
- Run the complete local G1-C-013 bundle verifier. Do not run a GPU attempt or
  change the project claim state in this scope.

## Boundaries

- Do not modify G1-C-012, G1-C-011, G1-C-010, or earlier frozen evidence.
- Do not modify `docs/DECISIONS.md`, `CONTEXT.md`, `RESULTS.md`, or
  `docs/ROADMAP.md`.
- Do not change the production load-back threshold, call `load_back` directly,
  or construct pending IDs, locks, nodes, or KV values by hand.
- Do not change the checked-demote mechanism, other arm behavior, finalizer
  semantics, dependencies, model, or CUDA target.
- Do not commit, anchor, delete remote paths, or classify G1 from local checks.
