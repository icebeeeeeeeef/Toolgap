# Write-policy scope steelman review

Canonical owners: D034 in `docs/DECISIONS.md` and Required Baselines in
`docs/EVALUATION.md`.

Decision question: may the G0-selected `write_through` mode serve both as the
causal reference and as the production baseline for a ToolGap optimization
claim?

Strongest case for one baseline: `write_through` exposes the cleanest committed
Host-copy predicate and lets release-only and checked reclamation differ at one
action. It is therefore the strongest qualification/reference mode for proving
the mechanism without Publication-history confounding.

Counterexample: that isolation eagerly pays Publication and Host occupancy.
Stock `write_through_selective` or `write_back` may avoid or reshape those costs
and yield a better joint-SLO result even if immediate checked reclamation beats
release-only after the copy already exists. The causal reference therefore
cannot establish production optimality.

Decision: use two levels. G1/G2 and the first G3 comparison use the same
`write_through` committed copy; a production claim additionally challenges
tuned stock `write_through_selective` and `write_back` on the same workload and
joint SLO. Winning only the first level remains a mechanism result.

Rejected alternatives: treat source-semantic selection as a production result;
give the candidate a different Publication history; add on-demand Publication
before eager Publication is measured as decisive; discard a valid mechanism
result merely because a stock policy wins end to end.

Reopen only if fixed-pin evidence invalidates the committed-copy semantics or a
measured decisive Publication cost supports an independent on-demand
Publication contract. All current claims remain `roadmap`.
