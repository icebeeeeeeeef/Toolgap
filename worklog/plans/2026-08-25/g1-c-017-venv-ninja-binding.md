# G1-C-017 oracle strengthening

Canonical owner: `experiments/g1/SPEC.g1-c-017.md`

## Trigger

Frozen C-016 commit `3ab468f943521a2e7da08c0ed48a78b65106a433`
was rejected independently before GPU execution. Its verifier removed arbitrary
marker contents during comparison and did not prove the complete binding block
ran before all formal-arm artifact creation and child launches.

## Executable scope

- Derive C-017 from frozen C-016 with identical runtime behavior: nine arms,
  selectors, timeout, model, patches, runtime venv Ninja binding, and oracle.
- Freeze each allowed Ninja block exactly and prove its ordering after resolver
  setup but before every formal-arm preparation, artifact, call, and launch.
- Exercise missing runtime-venv Ninja through the complete pre-arm transition;
  seal a verified `pre_execution INVALID` with no arm artifacts.
- Make the full verifier reject a binding moved after all arm calls and a
  GPU-conditional package install, whether or not that branch executes.
- Compare every non-C017 runtime surface to C014 after identity normalization,
  and scan every runtime executable for host package/privilege mutation.

## Boundaries

- Do not modify C-016 or any earlier frozen file.
- Do not execute a GPU attempt or generate/upload frozen inputs in this task.
- Do not touch `docs/DECISIONS.md`, `CONTEXT.md`, Gate results, or the roadmap.
- Local verifier PASS freezes runnable `roadmap` evidence only; it is not a G1
  experiment result.
