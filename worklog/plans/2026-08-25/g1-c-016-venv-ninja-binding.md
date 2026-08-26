# G1-C-016 runtime-venv Ninja binding

Canonical owner: `experiments/g1/SPEC.g1-c-016.md`

## Trigger

Frozen C-015 commit `d6358c1195d0b58407ba4ff053b04bf1188fbcb7`
was rejected before GPU execution. Independent review found that its privileged
Ubuntu `ninja-build` installer lacked a pre-action trust root, did not bind bare
command resolution to `/usr/bin/ninja`, and was not mechanically constrained
enough by its verifier.

## Executable scope

- Derive C-016 from frozen C-014 while preserving all nine arms, selectors,
  2400-second timeout, runtime inputs, patches, action, and Gate oracle.
- Use only the Python `ninja` distribution already installed into the runtime
  venv by the frozen ordinary requirements. Add no privileged prerequisite
  command and perform no host mutation.
- Before the first arm, require `$RUNTIME_VENV/bin/ninja`; bind the formal arm
  PATH to `$RUNTIME_VENV/bin:$CUDA_HOME/bin:/usr/bin:/bin`; prove both shell and
  Python resolution select that executable; record its version and SHA-256;
  and replay all bindings off-host.
- Add executable fake-host-PATH and mutation counterexamples, plus normalized
  mechanical equivalence checks against frozen C-014.

## Boundaries

- Do not modify C-015, C-014, or any earlier frozen file.
- Do not execute a GPU attempt or generate/upload frozen inputs in this task.
- Do not touch `docs/DECISIONS.md`, `CONTEXT.md`, Gate results, or the roadmap.
- Local verifier PASS freezes runnable `roadmap` evidence only; it is not a G1
  experiment result.
