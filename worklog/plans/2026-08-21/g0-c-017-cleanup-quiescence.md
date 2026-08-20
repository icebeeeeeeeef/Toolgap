# G0-C-017 cleanup quiescence repair

Canonical owner: `experiments/g0/SPEC.g0-c-017.md` and
`experiments/g0/RESULTS.md`.

## Executable scope

- Preserve frozen G0-C-016 and attempts 001/002 unchanged.
- Keep the existing 60-second cleanup deadline, but wait for the process
  group, target listener, and attributable GPU PIDs to quiesce together before
  taking the final immutable snapshots.
- Add local counterexamples for a listener that disappears within the deadline
  and one that survives the deadline.
- Keep source, patch, model, dependency lock, server parameters, requests,
  cleanup receipt schema, claim boundary, and off-host seal unchanged.
- Execute one fresh G0-C-017 attempt through off-host verification.

## Non-goals

- No generic retry framework, signal wrapper, daemon supervisor, server patch,
  relaxed leak oracle, artifact reuse, phase resume, or G1 work.
