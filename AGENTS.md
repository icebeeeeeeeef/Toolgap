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

## Verification discipline

- Protection and tests must serve the real behavior under study or a concrete
  evidence property. Do not let verifier self-protection, speculative threats,
  or test-framework hardening displace the shortest path to runtime evidence.
- A pre-run check may block execution only when its failure can credibly change
  runtime behavior, admit different frozen inputs, produce a false Gate result,
  lose cleanup, or make sealed evidence unverifiable in the trusted operator
  environment. Record other hardening as non-blocking tooling debt.
- Do not treat simultaneous malicious rewrites of the implementation, verifier,
  normalization, golden values, tests, and caller environment as the default
  threat model. Expanding the threat model requires a separately accepted
  contract and a finite stopping rule.
- Before adding a guard, mutation, review round, or frozen revision, identify
  the concrete wrong result it prevents and ask whether a bounded smoke or
  formal run would provide more direct evidence. If omitting it still permits a
  reproducible and auditable result, it must not block the main path.
- A new frozen experiment revision requires a material change to runtime
  behavior, input identity, Gate semantics, cleanup, or evidence integrity;
  verifier-only defense is insufficient. See
  `worklog/lessons/2026-08-26/g1-verifier-overdefense.md` for the failure mode.

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

## Worklog discipline

- `worklog/` is a lightweight history of local plans, decision-changing
  reviews, and lessons. It is not a second roadmap, experiment record, or
  source of current technical truth.
- Before a non-trivial task that can change implementation, project scope,
  architecture, experiment evidence, or a Gate decision, search the relevant
  `worklog/` entries first. Record its executable scope in
  `worklog/plans/YYYY-MM-DD/<topic>.md`.
- Record a review in `worklog/reviews/YYYY-MM-DD/<topic>.md` only when the
  discussion changes a decision or rejects a credible alternative. Record a
  lesson in `worklog/lessons/YYYY-MM-DD/<topic>.md` after a falsified
  assumption, error, or counterexample.
- Each record links to its canonical owner. Update the owner itself when a
  fact, scope, Gate order, contract, or experiment result changes:
  `docs/PROJECT.md`, `docs/ROADMAP.md`, `docs/DEMOTION_CONTRACT.md`,
  `docs/DECISIONS.md`, or `experiments/<gate>/` as applicable.
- Keep records concise and evidence-linked. Do not store raw chat transcripts,
  private reasoning, secrets, generated logs, or duplicated frozen artifacts.
  Preserve an earlier record; append a correction or supersession rather than
  rewriting its observed rationale.
