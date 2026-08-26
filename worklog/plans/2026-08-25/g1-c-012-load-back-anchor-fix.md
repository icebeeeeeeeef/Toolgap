# G1-C-012 load-back anchor fix

Canonical owner: `experiments/g1/SPEC.g1-c-012.md`

## Trigger

The sealed G1-C-011 attempt showed that the load-back request completed before
its fixture observed `LOAD_BACK_PENDING`. Pinned SGLang limits radix matching to
`input_len - 1`, so replaying the exact frontier split the session leaf and put
the real load-back anchor on the new parent while the fixture watched the old
leaf. G1-C-011 remains immutable and is not accepted as a Gate result.

## Executable scope

- Create a complete G1-C-012 bundle mechanically from G1-C-011 while preserving
  the source, model, runtime, CUDA target, nine arms, and terminal oracle.
- In the load-back arm only, append token `7` to the reconstructed frontier
  input so the match limit covers the complete target leaf.
- Require the observed target NodeId to be the exact load-back anchor and a key
  in `ongoing_load_back` before invoking the checked facade.
- Add a counterexample proving removal of the appended suffix restores the
  G1-C-011 split-parent fixture and is rejected, while retaining the guard
  deletion mutation for `LOAD_BACK_PENDING`.
- Run the complete local G1-C-012 bundle verifier. Do not run a GPU attempt or
  change the project claim state in this scope.

## Boundaries

- Do not modify G1-C-011, G1-C-010, or any earlier frozen bundle or evidence.
- Do not modify `docs/DECISIONS.md`, `CONTEXT.md`, `RESULTS.md`, or
  `docs/ROADMAP.md`.
- Do not change the checked-demote mechanism, dependencies, model, CUDA target,
  arm ordering, or finalizer semantics.
- Do not commit, anchor, delete remote paths, or classify G1 from local checks.
