# G1-C-018 oracle strengthening

Canonical owner: `experiments/g1/SPEC.g1-c-018.md`

## Trigger

Frozen C-017 commit `538c753b723227e9555eff6108abac173756e108`
was rejected by two independent reviews before input generation or GPU
execution. Helper/runtime-env blocks could move, block and inline digest could
be jointly rebaselined, verifier paths could be overridden, and system pip was
outside the privilege oracle.

## Executable scope

- Derive C-018 from frozen C-016 with identical runtime behavior: nine arms,
  selectors, timeout, model, patches, runtime venv Ninja binding, and oracle.
- Compare every runtime executable and Ninja block directly to frozen C-016;
  prove helper, binding, runtime-env, child PATH, and finalizer block ordering.
- Exercise missing runtime-venv Ninja through the complete pre-arm transition;
  seal a verified `pre_execution INVALID` with no arm artifacts.
- Keep production verifier inspection fixed to canonical `ROOT` paths. Run
  mutations only by modifying canonical files inside temporary local clones.
- Reject helper/runtime-env moves, joint block/digest rebaseline, path override,
  and GPU-only system-interpreter pip mutations with the full verifier.
- Scan every runtime executable for host package/root/privilege mutation.

## Boundaries

- Do not modify C-017 or any earlier frozen file.
- Do not execute a GPU attempt or generate/upload frozen inputs in this task.
- Do not touch `docs/DECISIONS.md`, `CONTEXT.md`, Gate results, or the roadmap.
- Local verifier PASS freezes runnable `roadmap` evidence only; it is not a G1
  experiment result.
