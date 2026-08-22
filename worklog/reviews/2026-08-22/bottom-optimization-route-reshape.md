# Bottom optimization route reshape

Canonical decision: D035 in `docs/DECISIONS.md`. Conditional performance
diagnosis in `docs/ROADMAP.md` owns only Gate timing and routing;
`docs/engineering/PERFORMANCE_ENGINEERING.md` owns the diagnostic method.

Decision question: should the earlier bottom-optimization discussion become a
general Demote Pacing implementation, or a narrower evidence-triggered rule?

Evidence and history: the repository had no accepted Demote Pacing decision and
has no runtime/performance evidence for a pacing bottleneck. The PR5 data-plane
review keeps PD-transfer slicing and concurrent channels in
`docs/future/PD_TRANSFER_SLICE.md`, while retaining fixed-pin small-transfer
coalescing and pinned-buffer work as symptom-triggered performance-diagnosis
candidates. The PR5 restore preflight review keeps L3 out of the mainline,
preserves fixed-pin restore-path verification, and lets those copy-path
candidates compete with layer-wise restore for the same optimization slot.
That review used a local single-series disposition while D033 canonically
recorded data-plane scope; neither document authorized an implementation or
general Demote Pacing. Both historical reviews remain unchanged.

Strongest case for general pacing: bounded issue could reduce bursts across
copy, release, and restore and provide one control surface for interference.
The counterexample is causal: Publication D2H, checked reclamation, and Recovery
H2D occur at different times, have different owners, and may prefer conflicting
controls. Without a reproducible stage-attributed symptom, one controller adds
scope but proves no contract gap.

Decision: reject general Demote Pacing as the default. Preserve three-stage
attribution and one conditional optimization slot in G3/G4. Admit at most one
series after a reproducible symptom: Checked Reclamation Chunking for measured
reclamation-side interference; an independently reviewed on-demand Publication
series for decisive eager Publication cost; one shared narrow substrate fix for
verified Recovery/H2D limits, selected among layer-wise restore,
small-transfer coalescing, and pinned-buffer reuse; or event-driven completion
only for critical-path polling. No symptom means no patch.

Rejected alternatives: a `PacingController`, public pacing knobs, a new Gate or
module; parallel optimization series; bundling Publication, reclamation, and
Recovery; pulling PD-transfer slicing/coalescing/concurrent channels, L3,
prefetch, or dynamic policy into the mainline; judging by bandwidth or
microbenchmark alone.

Reopen only with a reproducible G3/G4 symptom, stage attribution, one selected
series, SPEC revision, ablation, deletion test, losing workload, and fair arm
treatment. All claims remain `roadmap`; no prior evidence is rewritten.
