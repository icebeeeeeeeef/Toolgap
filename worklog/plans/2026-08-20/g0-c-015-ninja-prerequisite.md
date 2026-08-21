# G0-C-015 Ninja prerequisite repair

Canonical owner: `experiments/g0/SPEC.g0-c-015.md` and
`experiments/g0/RESULTS.md`.

## Executable scope

- Preserve frozen G0-C-014 and attempt 001 unchanged.
- Add Ubuntu `ninja-build` to command 19's ordinary project tools.
- Require `ninja` in command 20 and retain `ninja --version` in the sealed
  environment readback.
- Keep every source/model/host/dependency/oracle/inventory/serving identity and
  claim boundary unchanged; execute a fresh attempt through off-host review.

## Non-goals

- No CUDA/driver installation, alternate attention backend, disabled CUDA
  graph, server-parameter change, artifact reuse, phase resume, or G1 work.
