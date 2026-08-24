# Write-policy scope steelman review

> Status: completed
>
> Claim state: `roadmap`
>
> Date: 2026-08-22
>
> Canonical owner: [`docs/DECISIONS.md` D033](../../../docs/DECISIONS.md#2026-08-22--d033-keep-write-through-as-the-qualification-mode-not-the-production-optimum)
> and [`docs/EVALUATION.md`](../../../docs/EVALUATION.md#3-required-baselines)

## Decision question

Should the fixed `write_through` choice be retained only as the cleanest mode
for proving checked demotion, or treated as the final production write policy
and the only performance baseline?

## Evidence and strongest formulations

The fixed-pin source and the accepted G0 artifacts show that `write_through`
creates a settled Host duplicate before a later physical demotion. This
separates Publication from reclamation and lets the release-only and active-
reclamation arms share the same committed Host copy. It is therefore the
smallest auditable mode for G1/G2 and the primary G3 causal comparison. See
[`host-mode-selection.md`](../../../experiments/g0/artifacts/host-mode-selection.md)
and [`G0 RESULTS`](../../../experiments/g0/RESULTS.md#host-mode-and-stock-reproduction).

The strongest alternatives solve different production costs rather than the
same first proof problem. Fixed-pin `write_through_selective` waits for a hit-
count threshold before Publication and can avoid one-hit Host pollution;
`write_back` performs Publication when upper-tier eviction is required and can
avoid eager I/O when pressure is rare or lower-tier capacity is constrained.
SGLang's [HiCache design guidance](https://www.lmsys.org/blog/2025-09-10-sglang-hicache/)
describes the same bandwidth, hotness, and capacity trade-off. Neither
alternative supplies the stable pre-existing Host duplicate required by the
first checked-reclamation proof without adding another causal variable.

## Adversarial findings

- Treating `write_through` as production-optimal is **serious and testable**:
  eager D2H traffic and Host occupancy may outweigh earlier headroom for
  one-shot or low-reuse KV.
- Replacing G1 with `write_through_selective` is **mitigable but unnecessary**:
  hit-count eligibility would make the first physical-demotion result depend on
  an unrelated reuse condition.
- Replacing G1 with `write_back` is **serious for attribution**: Publication,
  completion, and reclamation would be coupled on the pressure path, so one
  result could not isolate checked reclamation.
- Adding ToolGap-triggered on-demand Publication now is **premature scope
  expansion**. It is a plausible later branch only if measurements attribute a
  production-level loss to eager Publication rather than to the reclamation
  premise itself.

## Decision

Retain `write_through` as the qualification/reference mode for G1, G2, and the
first G3 causal comparison. Both causal arms must share the same committed Host
copy so the independent variable remains immediate checked reclamation versus
target-only priority release plus stock eviction.

Do not treat that selection as a production-optimality claim. Before describing
ToolGap as an end-to-end production optimization, compare it under the same
workload and joint SLO with tuned stock `write_through_selective` and
`write_back` configurations. If ToolGap wins only against its same-publication
baseline but not against the best stock policy, retain the narrow mechanism
result and withhold the production optimization claim.

Do not authorize adaptive policy or ToolGap-triggered Publication through this
review. Such a branch requires measured evidence that eager Publication is the
blocking cost and a separate accepted contract. G5 remains the only dynamic-
policy admission Gate.

## Consequences and reopen conditions

Frozen G0 artifacts remain unchanged, G1 execution remains unauthorized, and
the overall project remains `roadmap`. Reopen this decision if fixed-pin source
semantics change, a conforming stronger causal baseline is found, or measured
G3/G4 evidence shows that eager Publication rather than checked reclamation is
the decisive production boundary.
