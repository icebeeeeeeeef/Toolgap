# G0-C-011 offline source seed

Canonical owner: `experiments/g0/SPEC.g0-c-011.md` and
`experiments/g0/RESULTS.md`.

## Executable scope

- Preserve frozen G0-C-010 and its rental attempts unchanged.
- Add one successor revision that replaces two live GitHub clones with two
  local clones from one preregistered, SHA-256-bound shallow bare Git seed.
- Keep the SGLang remote identity, commit, tree, patch, dependency/model pins,
  host admission, controls, serving protocol, evidence seal, and claim ceiling
  unchanged.
- Require the seed archive to pass SHA-256, extraction, `git fsck`, commit/tree,
  shallow-boundary, and clean-checkout checks before admission.
- Prove locally that a portable seed fixture restores two independent clean
  checkouts and that a wrong archive hash is rejected.
- Transfer the frozen successor runner to the rented host, run one unused
  attempt, copy its complete sealed evidence off host, and stop before any G1
  work or host release.

## Non-goals

- No Git mirror, retry subsystem, proxy, OSS dependency, driver/CUDA change,
  SGLang source change, or experiment-claim promotion.
- No mutation or reinterpretation of G0-C-009/010 evidence.
