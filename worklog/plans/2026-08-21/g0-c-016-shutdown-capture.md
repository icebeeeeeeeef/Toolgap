# G0-C-016 shutdown capture repair

Canonical owner: `experiments/g0/SPEC.g0-c-016.md` and
`experiments/g0/RESULTS.md`.

## Executable scope

- Preserve frozen G0-C-015 and attempt 001 unchanged.
- Before cleanup, require the server PID to be alive and the process-group
  SIGTERM to succeed.
- Capture `wait` with an `if` so the active ERR trap cannot intercept a normal
  signaled exit; accept this fixed SGLang revision's observed 137 alongside
  0/143 only when all existing no-process/no-port/no-GPU-survivor checks pass,
  in both the serving receipt and final evidence verifier.
- Keep every input, control, server parameter, request, and claim boundary
  unchanged; execute a fresh attempt through off-host review.

## Non-goals

- No signal retry framework, server wrapper, graceful-shutdown patch, ignored
  cleanup leak, artifact reuse, phase resume, or G1 work.
