# Write-policy scope decision

Status: complete

Canonical owners: D034 in `docs/DECISIONS.md` and Required Baselines in
`docs/EVALUATION.md`.

## Goal

Separate the first causal comparison from an end-to-end optimization claim on
the declared single-node testbed: retain `write_through` for committed-copy
qualification, then require the same workload and joint-SLO challenge against
tuned stock `write_through_selective` and `write_back`.

## Scope

- keep release-only and checked reclamation on the same committed Host copy and
  Publication history;
- set the claim ceiling to a mechanism result when the candidate does not beat
  the best measured stock policy;
- leave on-demand Publication blocked until measurement and an independent
  accepted contract justify it.

## Non-goals

No runtime policy, tuning result, on-demand Publication mechanism, performance
number, production-readiness claim, or production-scale claim is created by
this documentation task.

## Acceptance evidence

D034 and `EVALUATION.md` state both baseline levels, fairness, and the claim
ceiling without changing Gate order or frozen evidence.

## Final status

Complete. The canonical decision and evaluation contract passed fresh G0
evidence verification, whitespace validation, decision-term cross-link review,
and the owned-path boundary check.
