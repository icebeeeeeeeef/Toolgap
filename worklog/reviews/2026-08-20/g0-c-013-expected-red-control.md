# G0-C-013 expected RED control review

Canonical owner: `docs/DECISIONS.md` D027 and
`experiments/g0/SPEC.g0-c-013.md`.

The stock oracle did exactly what the protocol required: exit 1 after 27
expected failures. `set +e` prevented shell termination but did not disable the
inherited `ERR` trap, so command 21 sealed `INVALID_SCOPE` before reading the
exit code. Removing the trap globally would weaken real failure handling.

The accepted minimum is Bash's existing conditional exception: run only the
expected-RED command in `if ...; then ...; else stock_status=$?; fi`. Commands
inside an `if` condition do not trigger `ERR`; every later unexpected failure
remains trapped. The oracle and its three exact acceptance assertions remain
unchanged.
