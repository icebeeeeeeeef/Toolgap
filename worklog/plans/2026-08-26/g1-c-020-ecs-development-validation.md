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

## Outcome — 2026-08-26

- The ECS development matrix passed all nine arms and remained `simulated`.
- Frozen C020 source: commit
  `e43ad7aabb7a8c0e4a17855a4745d91ba5945d96`, tree
  `47cc669e0c6f0a7c557d91eb61f4f8220dbb1a30`.
- Formal attempt `g1-c-020-a1-20260825T190159Z` sealed `PASS`; all nine arm
  cleanups reported clean process groups, listeners, and attributable GPU PIDs.
- The permission-preserving off-host copy passed the frozen C020 finalizer.
  The non-preserving `scp -r` probe retained identical bytes but changed sealed
  `0444` handshake modes to `0644`; it was rejected and not used.
- C020 raw evidence is externally anchored at SHA-256
  `7c82337eca8b98170296c2f867829c2f5ae5656f1958b5b22850349a514de440`,
  OSS version
  `CAEQnAYYgYCA6abn6YEaIiA5NjM3NjEzZGI4MDQ0NzEyODEwMWQwOWU3YjIxNjY3OQ--`.
- C019 attempt `g1-c-019-a1-20260825T170549Z` remains `INVALID` and is
  separately anchored at SHA-256
  `398da39de1027fc918d9df82d547bd8d6ecd8ea96783e844d93fac273a5c0d9f`,
  OSS version
  `CAEQnAYYgYCA2bn16YEaIiA2YTBiYTE5MDQ4NzE0YmUwYTBhYTczZmU1MGI1YjI4MA--`.
- Local operator mirrors live under ignored `experiments/g1/raw/`; OSS remains
  the off-host source of truth. Canonical Gate details are in
  `experiments/g1/RESULTS.md`.
- Three stale verifier-test assumptions and macOS Bash 3.2 lacking `mapfile`
  remain non-blocking tooling debt. Neither changes the Linux formal runtime,
  sealed evidence, offline finalizer result, or Gate conclusion.
