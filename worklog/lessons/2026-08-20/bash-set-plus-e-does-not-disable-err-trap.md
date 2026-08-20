# Bash `set +e` does not disable an `ERR` trap

Canonical owner: `experiments/g0/RESULTS.md`.

Disabling `errexit` is not sufficient when a script also has an active `ERR`
trap. A command whose nonzero status is expected must appear in a Bash context
that suppresses `ERR`, such as the condition of an `if`, and its status must be
captured explicitly. Retain a counterexample check for every expected-failure
control path.
