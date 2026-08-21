# G0-C-013 expected RED trap repair

Canonical owner: `experiments/g0/SPEC.g0-c-013.md` and
`experiments/g0/RESULTS.md`.

## Executable scope

- Preserve frozen G0-C-012 and attempt 001 unchanged.
- Add one successor revision changing only how command 21 captures the stock
  oracle's preregistered exit status 1.
- Execute the stock oracle as an `if` condition so Bash suppresses `ERR` for
  that expected nonzero result, then retain the exact existing checks for exit
  1, `Ran 27 tests`, and `FAILED (failures=27)`.
- Keep every source/model/host/dependency/control/serving identity and claim
  boundary unchanged; run a new attempt through off-host verification and
  independent review.

## Non-goals

- No oracle change, ignored failure, generic trap framework, phase resume,
  artifact reuse, model/source change, serving change, or G1 work.
