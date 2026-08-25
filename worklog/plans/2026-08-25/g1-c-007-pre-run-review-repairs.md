# G1-C-007 pre-run review repairs

Canonical owners: `experiments/g1/SPEC.md`, `docs/ROADMAP.md`, and the new
`experiments/g1/SPEC.g1-c-007.md`.

## Goal

Preserve rejected, never-executed C-006 commit `0ad49f1` and freeze a minimal
C-007 successor that can generate its own manifest, can run on the existing
99.8G ECS root disk after the separately approved temporary-work cleanup, and
can independently verify stage-appropriate storage-preflight evidence for a
sealed pre-execution `INVALID`.

## Executable scope

- Copy the C-006 bundle to C-007 names; do not edit C-001 through C-006.
- Bind `minimum_free_bytes` to 24 GiB. C-004's observed peak was
  `14922854400` bytes (about 13.90 GiB), so the bound leaves about 10.10 GiB
  over that measured peak. The five sealed `work/` trees total
  `33479200768` bytes (about 31.18 GiB); deleting only those trees projects
  about 7.18 GiB of first-gate margin. At the resolver gate, before venv and
  wheelhouse creation, the measured source-plus-model predecessor is about
  1.71 GiB, projecting 29.47 GiB available and about 5.47 GiB of margin.
- Add `storage_preflight` to the builder's exact manifest schema and add a
  create/verify round-trip regression that fails against C-006.
- Record the runner failure phase as immutable evidence before sealing an
  `INVALID`. Offline verification must require the source-restore preflight at
  `source_restore` and later phases, and both preflights at `resolver` and later
  phases. A failing stage may have `available_free_bytes < minimum_free_bytes`;
  every earlier required stage must have passed.
- Add missing/tampered/wrong-order counterexamples for pre-execution evidence.
- Make the bundle verifier compare all C-001 through C-006 frozen paths against
  the explicit predecessor commit `0ad49f1`, not only against the working tree.

The measured byte counts above are filesystem observations only. The
post-cleanup margins are execution-budget projections; neither is a G1 runtime
or Gate result.

## Verification

Run the focused new regressions first, then
`bash scripts/verify-g1-c-007-bundle.sh`, `git diff --check 0ad49f1..HEAD`, and a
real builder create/verify using the same immutable inputs that will be staged
for the formal run. Independent specification and code-quality reviews must
both pass before any ECS execution.

## Boundaries

Do not change the G1 mechanism, SGLang patches, model, runtime wheel, CUDA
wheelhouse, seven arms/selectors, cleanup contract, terminal oracle, or project
claim state. Do not touch `docs/DECISIONS.md` or `CONTEXT.md`. No ECS deletion,
OSS write, or formal attempt is part of this implementation task.
