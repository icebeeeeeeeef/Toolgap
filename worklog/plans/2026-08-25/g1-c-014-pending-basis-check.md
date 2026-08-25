# G1-C-014 pending-state basis check

Canonical owner: `experiments/g1/SPEC.g1-c-014.md`

## Trigger

Independent pre-run matrix review rejected frozen C-013 commit
`6347aae14a98b5a2eda68d6fcf7bb92c1c3baada`. Its direct-assignment string
checks did not reject equivalent pending-state fabrication through `setattr`
or mapping update helpers. C-013 was not executed and has no Gate result.

## Executable scope

- Create a complete G1-C-014 bundle mechanically from G1-C-013.
- Keep the runtime patch byte-equivalent to C-013.
- Add one basis check that removes the two allowed threshold-qualification
  deltas from the C-014 load-back class and requires exact equality with the
  frozen C-012 load-back class.
- Preserve the existing threshold, qualification, suffix, exact-anchor, and
  production-guard mutations.
- Run the complete local verifier and independent code/matrix reviews before
  any GPU execution.

## Boundaries

- Do not modify C-013 or earlier frozen files.
- Do not change production code, the runtime threshold, any arm behavior, the
  finalizer, dependencies, model, CUDA target, or Gate semantics.
- Do not touch `docs/DECISIONS.md`, `CONTEXT.md`, `RESULTS.md`, or
  `docs/ROADMAP.md`.
- Do not execute C-013 or classify G1 from local checks.
