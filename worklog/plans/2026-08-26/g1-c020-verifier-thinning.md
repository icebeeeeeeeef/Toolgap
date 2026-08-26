# G1-C020 verifier thinning

Canonical owners: `experiments/g1/SPEC.g1-c-020.md` for protocol semantics,
`experiments/g1/RESULTS.md` for the sealed Gate result, and
`docs/ROADMAP.md` for Gate order.

## Scope

Make a forward, non-blocking cleanup of the current C020 development and
replay tooling. Keep only checks that can detect changed runtime inputs or
behavior, lost process cleanup, or invalid/unreplayable sealed evidence.
Remove self-referential mutation, predecessor-normalization, source-text, and
test-presence defenses; remove all development tests and operator tools from
the static manifest at the same time.
Repair the missing-plan verifier input and stale output spelling test.

## Boundaries

- Do not change `0001` checked-demote behavior, the `0002` nine-arm runtime,
  frozen SPEC semantics, `experiments/g1/raw/`, `RESULTS.md`, or the G1 Gate
  result.
- Do not rewrite the frozen C020 commit or claim this tooling change is new
  runtime or Gate evidence. The project remains `roadmap`.
- Verify the retained tests, the compact bundle verifier, and whitespace after
  the change.
