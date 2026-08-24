# Write-policy scope decision

> Status: completed
>
> Claim state: `roadmap`
>
> Date: 2026-08-22

## Goal

Persist the reviewed boundary between `write_through` as the smallest
qualification/reference mode for checked Host-tier demotion and the separate
question of which HiCache write policy is best for a production workload.

## Scope

- record the decision-changing steelman review in `worklog/reviews/`;
- add one accepted decision to [`docs/DECISIONS.md`](../../../docs/DECISIONS.md);
- make the two comparison layers explicit in
  [`docs/EVALUATION.md`](../../../docs/EVALUATION.md): same-publication causal
  comparison first, tuned stock-policy challengers before a production
  optimization claim.

## Non-goals

- do not rewrite frozen G0 specifications or evidence;
- do not change Gate order or authorize G1 execution;
- do not implement dynamic policy, ToolGap-triggered publication, L3, or a new
  physical transfer path;
- do not claim that any write policy has won a runtime comparison.

## Acceptance evidence

- the worklog review links to the canonical decision and evaluation contract;
- `write_through` remains the G1/G2 and first G3 causal reference mode;
- `write_through_selective` and `write_back` remain required production-level
  challengers rather than being rejected globally;
- repository whitespace and frozen G0 evidence checks still pass.

## Result

Completed as a documentation-only decision clarification. No runtime behavior,
experiment result, or project claim state changed.
