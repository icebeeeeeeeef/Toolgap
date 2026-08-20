# An ERR trap also intercepts an expected nonzero wait

Canonical owner: `experiments/g0/SPEC.g0-c-016.md`.

`set +e` disables `errexit` but does not disable an active `ERR` trap. The same
failure pattern seen with the expected stock RED also applies to `wait` after
an intentional signal. Capture an expected nonzero status as an `if` condition
and separately prove signal attribution plus cleanup invariants.
