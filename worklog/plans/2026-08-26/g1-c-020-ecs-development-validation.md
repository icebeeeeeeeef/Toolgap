# G1-C-020 ECS development and validation

Canonical owners: `experiments/g1/SPEC.md` and the future frozen
`experiments/g1/SPEC.g1-c-020.md`.

## Trigger

Formal C-019 attempt `g1-c-019-a1-20260825T170549Z` sealed `INVALID` before
GPU execution because the `BEGIN_C019_FORMAL_ARM_PATH` marker interrupted a
continued `timeout` command. This is an actual runner defect, not verifier
hardening debt.

## Executable scope

- Preserve the C-019 run, input prefix, checkout, and work tree.
- Create an independent ECS development checkout from frozen C-019.
- Prove the existing failure shape, then move only the formal-arm markers so
  the exact timeout, environment, runtime Python, scripted module, selector,
  process-group handshake, GPU sampling, and cleanup path execute unchanged.
- Reuse the prepared C-019 runtime venv, model, and patched SGLang checkout for
  one enabled-arm smoke followed by the exact nine-arm sequence. Store these
  development logs outside formal evidence and classify them as `simulated`.
- After nine-arm green, mechanically derive one C-020 formal bundle, run only
  runtime/input/cleanup/evidence-integrity admission, freeze one commit/tree
  and OSS input set, and execute one formal attempt to its own terminal.
- Preserve, verify offline, and externally anchor both the C-019 `INVALID` and
  the C-020 terminal before updating any Gate result.

## Boundaries

- Do not edit or relabel C-019 or its sealed attempt.
- Do not add verifier self-defense, mutation suites, abstractions, or review
  rounds that do not protect runtime behavior or evidence integrity.
- Do not change the nine arms, selectors, model, patches, 2400-second timeout,
  thresholds, checked-demotion mechanism, cleanup semantics, or Gate oracle.
- A green development run is `simulated`, not a Gate result. The project
  remains `roadmap` until the formal evidence is sealed and accepted.
