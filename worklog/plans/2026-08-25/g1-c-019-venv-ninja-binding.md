# G1-C-019 oracle strengthening

Canonical owner: `experiments/g1/SPEC.g1-c-019.md`

## Trigger

Frozen C-018 commit `8417f2cda4bc53c92836d53179d362ff49d9fdf1`
was rejected before input generation or GPU execution. Caller-controlled
Python could spoof success, mutations could skip, raw pip allowance was not
exact, and the storage failure fixture used available rather than total bytes.

## Executable scope

- Derive C-019 from frozen C-016 with identical runtime behavior: nine arms,
  selectors, timeout, model, patches, runtime venv Ninja binding, and oracle.
- Compare every runtime executable and Ninja block directly to frozen C-016;
  prove helper, binding, runtime-env, child PATH, and finalizer block ordering.
- Exercise missing runtime-venv Ninja through the complete pre-arm transition;
  seal a verified `pre_execution INVALID` with no arm artifacts.
- Fix production Python/PATH, reject injection variables, and require one exact
  inline-oracle completion token before mutation tests run.
- Hard-fail mutation basis drift and reject a selective Python wrapper plus a
  variable-interpreter GPU-only fifth raw pip install.
- Use recorded `total_bytes + 1` for the storage failure threshold.
- Scan every runtime executable for host package/root/privilege mutation.

## Boundaries

- Do not modify C-018 or any earlier frozen file.
- Do not execute a GPU attempt or generate/upload frozen inputs in this task.
- Do not touch `docs/DECISIONS.md`, `CONTEXT.md`, Gate results, or the roadmap.
- Local verifier PASS freezes runnable `roadmap` evidence only; it is not a G1
  experiment result.
