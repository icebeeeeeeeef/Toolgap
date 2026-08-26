# G1-C-008 importable arm module

Canonical owner: `experiments/g1/SPEC.g1-c-008.md`.

## Goal

Preserve frozen C-007 commit `529866d` and issue one minimal successor after
the formal enabled arm exposed that its synthetic `g1_c_007_scripted` module
identity could not be imported by the SGLang scheduler-hook executor.

## Executable scope

- Copy the complete C-007 bundle to C-008 names without editing C-001 through
  C-007 or the shared model and patch inputs.
- Replace only the generated arm runner's synthetic file-loader identity: add
  the scripted test file's parent to the parent process `sys.path`, import the
  module by its real filename stem, and bind the imported `__file__` back to
  the manifest-selected path. Multiprocessing spawn inherits that `sys.path`.
- Add a focused regression whose selected callable exposes its real
  `__module__` and whose independent spawn child imports and resolves it.
- Update only C-008 identities, static bindings, finalizer/verifier paths,
  anchor, and specification narrative. Preserve C-007 cleanup, process-group,
  evidence, oracle, selectors, runtime inputs, and 24 GiB preflight contracts.

## Verification

Capture the focused spawn regression failing before the runtime delta, then
run all C-008 focused tests, `bash scripts/verify-g1-c-008-bundle.sh`, frozen
predecessor equality checks, and `git diff --check 529866d..HEAD`.

## Boundaries

No ECS or OSS operation, remote cleanup, formal execution, Gate decision, or
change to `docs/DECISIONS.md` or `CONTEXT.md` is part of this revision.
