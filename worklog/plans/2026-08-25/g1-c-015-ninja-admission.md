# G1-C-015 Ninja admission repair

Canonical owner: `experiments/g1/SPEC.g1-c-015.md`

## Trigger

Formal C-014 attempt `g1-c-014-a2-20260825T144921Z` sealed
`pre_execution INVALID` at `formal_arms`, exit `1`, after FlashInfer JIT tried
to execute bare `ninja` and received `FileNotFoundError`. Its cleanup evidence
is clean, offline verification passed, and its external OSS anchor remains the
authority for that invalid attempt.

## Executable scope

- Mechanically derive the complete C-015 bundle from frozen C-014 commit
  `3ea9e48b2a97b68e59ec622372f31f5a69408896`.
- Keep all nine arms, runtime inputs, timeouts, selectors, patches 0001/0003,
  action, thresholds, and Gate oracle unchanged.
- Add one manifest-bound project prerequisite command that installs only
  Ubuntu `ninja-build` when `/usr/bin/ninja` is absent and validates its own
  bytes before the first privileged action.
- Require `/usr/bin/ninja` after attempt identification but before any arm, record its path, runtime
  version, and dpkg package version, and replay those bindings off-host.
- Add mutation and shell counterexamples for the new admission boundary and
  for immutability of C-014.

## Boundaries

- Do not modify C-014 or any earlier frozen file.
- Do not install or replace the provider GPU/CUDA substrate.
- Do not touch `docs/DECISIONS.md`, `CONTEXT.md`, Gate results, or the roadmap.
- A local verifier PASS freezes runnable `roadmap` evidence only; it is not a
  G1 experiment result.
