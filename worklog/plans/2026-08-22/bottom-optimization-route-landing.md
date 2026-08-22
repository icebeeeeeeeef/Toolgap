# Bottom optimization route canonical landing

Status: complete

Canonical owners: D034-D035 in `docs/DECISIONS.md`, the existing conditional
diagnosis section in `docs/ROADMAP.md`, baseline/evidence rules in
`docs/EVALUATION.md`, and the diagnosis method in
`docs/engineering/PERFORMANCE_ENGINEERING.md`.

## Goal

Record the owner-approved bottom-optimization route without changing Gate order
or authorizing runtime work: qualify `write_through` as the first causal
comparison mode, require a later stock-policy challenge for a production claim,
and admit at most one measurement-driven conditional optimization series after
a reproducible G3/G4 symptom.

## Scope

1. Add D034 for the two-level Publication baseline and claim ceiling.
2. Add D035 for Publication / checked reclamation / Recovery attribution and
   the conditional one-series rule.
3. Add only the minimum matching rules to `ROADMAP.md`, `EVALUATION.md`, and
   `engineering/PERFORMANCE_ENGINEERING.md`.
4. Record the write-policy review and the reshape from the earlier discussion
   to the canonical rule.

## Non-goals

- no change to G0-G5 order, `PROJECT.md`, frozen G0 evidence, upstream patch,
  future-project documents, runtime, tests, or code;
- no PacingController, public pacing parameter, new Gate/module, on-demand
  Publication, layer-wise/L3/prefetch/PD implementation, or dynamic selector;
- no runtime or performance claim and no performance number.

## Acceptance evidence

- all changed statements remain `roadmap` and keep action -> mediator -> joint
  endpoint as the only performance-win chain;
- D034/D035 and their worklog links are internally consistent;
- `bash scripts/verify-g0-evidence.sh` and `git diff --check` pass;
- the requested decision-term search is reviewed and only the eight owned paths
  differ from the baseline.

## Final status

Complete. D034-D035, the three canonical method/evaluation owners, and both
decision-changing reviews now express the accepted route. Fresh G0 evidence
verification and whitespace checks passed; the decision-term search and exact
eight-path ownership boundary were reviewed.
