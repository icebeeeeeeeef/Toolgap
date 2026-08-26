# G1 verifier over-defense displaced the experiment

Canonical owners: `docs/ROADMAP.md` for Gate order and
`experiments/g1/SPEC.g1-c-019.md` for the current formal protocol.

## Falsified assumption

More local protection was treated as monotonically increasing experimental
confidence. That stopped being true after the real C-014 runtime failure was
repaired by the runtime-venv Ninja binding. C-017 through C-019 preserved the
same model, patches, nine arms, timeout, thresholds, and runtime behavior, but
formal GPU execution remained blocked while the verifier was repeatedly
hardened against its own markers, normalization, environment, and mutation
tests.

The protection and tests were no longer serving the behavior under study or
the shortest path to a reviewable Gate result. They had become self-referential:
each defense created another verifier surface to defend, another complete
bundle revision, and another review cycle. This is over-optimization and
premature defense, not evidence-first execution.

## Boundary

A pre-run check is blocking only when its failure can, in the trusted operator
environment, change the real runtime behavior, admit different frozen inputs,
produce a false Gate decision, lose cleanup, or make the sealed evidence
unverifiable. Input identity, dependency admission, formal-arm semantics,
cleanup, terminal sealing, offline replay, and external anchoring remain hard
requirements.

Hypothetical joint corruption of the runtime, verifier, normalization, golden
values, tests, and caller environment is outside this Gate's operational threat
model. Defending the verifier from an author who simultaneously controls every
oracle has no finite local stopping point. Such concerns may be recorded as
tooling debt, but they do not block the GPU experiment without a concrete path
to a wrong result under normal operation.

## Correction

Before adding a guard, mutation, review round, or new frozen bundle, answer:

1. Which real experiment behavior or evidence property can be wrong without it?
2. Is that failure credible in the trusted execution environment rather than
   requiring a malicious joint rewrite of implementation and oracle?
3. Would a bounded smoke or formal GPU run produce more direct information?
4. Can the risk be recorded without blocking a reproducible, auditable result?

If the first two answers are not concrete, the work is non-blocking. Prefer the
smallest check that protects the main path, cap pre-run review to one repair
cycle, and move to runtime evidence. A new bundle revision requires a change to
runtime behavior, frozen input identity, Gate semantics, cleanup, or evidence
integrity; verifier self-protection alone is insufficient.
