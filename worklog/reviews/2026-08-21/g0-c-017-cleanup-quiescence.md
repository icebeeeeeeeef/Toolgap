# G0-C-017 cleanup quiescence review

Canonical owner: `docs/DECISIONS.md` D031 and
`experiments/g0/SPEC.g0-c-017.md`.

016/002 cannot be promoted from a later ad hoc probe because its frozen cleanup
receipt is false. Dropping the listener oracle would hide a real leaked server,
and a fixed sleep would encode timing rather than the contract. The accepted
minimum keeps the same deadline and final evidence, but resamples the three
existing cleanup observations until they are jointly clear. A permanent target
listener remains a deterministic failure.
