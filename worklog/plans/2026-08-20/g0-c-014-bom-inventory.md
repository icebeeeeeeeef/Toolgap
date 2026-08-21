# G0-C-014 BOM-safe inventory repair

Canonical owner: `experiments/g0/SPEC.g0-c-014.md` and
`experiments/g0/RESULTS.md`.

## Executable scope

- Preserve frozen G0-C-013 and attempt 001 unchanged.
- Add one successor revision whose only behavioral change is decoding Python
  source with `utf-8-sig` in its frozen full-tree AST inventory.
- Add a counterexample fixture containing a legal UTF-8 BOM and retain the
  exact zero-caller, one-backend-call, and zero-dynamic-route assertions.
- Keep every source/model/host/dependency/oracle/serving identity and claim
  boundary unchanged; execute a fresh attempt through off-host verification.

## Non-goals

- No skipped source file, generic encoding fallback, parse-error suppression,
  mechanism patch, artifact reuse, phase resume, serving change, or G1 work.
