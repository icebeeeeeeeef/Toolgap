# ToolGap collaboration guide

## Working relationship

- Treat the user as an engineering peer: challenge a decision when source
  evidence or first-principles reasoning disagrees, and explain the evidence.
- Keep designs small. Do not add an abstraction, subsystem, or future-facing
  extension unless it closes a demonstrated contract gap.
- Inspect the current source and canonical documents before making code claims;
  label inferences as inferences.

## Evidence and scope

- Every material claim must use one state defined in `docs/README.md`:
  `roadmap`, `shipped`, `experimentally validated`, or `simulated`.
- The current project state is `roadmap`. G0 ended at `RESHAPE`; its source
  contract evidence does not prove a real SGLang import, CUDA behavior,
  allocator-visible reclamation, recovery, or performance result.
- Preserve frozen specs, preregistration receipts, invalid attempts, negative
  results, and raw evidence. Do not rewrite prior evidence to make a later
  narrative look cleaner.
- `docs/PROJECT.md` owns project scope, `docs/ROADMAP.md` owns Gate order,
  `docs/DEMOTION_CONTRACT.md` owns checked-demotion semantics, and
  `experiments/<gate>/` owns frozen execution evidence.

## Ownership boundary

- ToolGap may own logical lifecycle identity, admissibility, idempotence,
  cancellation, fallback, cleanup orchestration, and DecisionTrace.
- SGLang remains the dependency owner for the physical KV tree, residency,
  references, allocator, movement, eviction, and model execution.
- Prefer one small upstream extension point. Do not create a second physical KV
  data plane, a replacement cache tree, a global eviction policy, or a public
  pause API without a separately accepted contract.

## Repository hygiene

- Keep local-machine environment files and generated raw runs out of version
  control, but do not ignore frozen experiment artifacts.
- Run the relevant repository checks before claiming a change is complete.
- Use GitHub Issues in `icebeeeeeeeef/Toolgap` for project tracking once the
  repository is available.
