# G0-C-007 pre-run invalidation review

> Status: accepted
>
> Claim state: `roadmap`
>
> Date: 2026-08-20

## Decision question

Should the known G0-C-007 execution defects be repaired in place, or should the
repository preserve 007 and freeze a successor revision?

## Evidence

G0-C-007 declares itself frozen before runtime. Independent source, execution,
evidence, and Gate-boundary reviews found deterministic pre-run defects: its
default attempt parent is absent, it checks the wrong SGLang packaging path,
and its launch omits the UnifiedRadixCache selection environment. They also
found missing total health timeout, phase receipts, immediate installed-package
identity, retained wheels, process-group cleanup, failure indexing, and an
unambiguous completion seal. No CUDA arm was run and no G0 result was observed.

## Decision

Preserve G0-C-007 unchanged and create G0-C-008 as the smallest repaired
successor integration contract. Record no Gate decision for 007. Continue to
exclude physical demotion and all G1 evidence from the successor G0 run.

## Rejected alternatives

- editing 007 in place would rewrite a frozen protocol;
- adding G0.5 would duplicate the existing revision mechanism;
- adding a generic runner, cgroup platform, signed artifact service, or full
  wheelhouse would not close a demonstrated G0 claim gap;
- adding real demotion would mix the G0 package/integration question with G1.

## Canonical follow-up

The durable decision is `docs/DECISIONS.md` D022. The executable successor is
`experiments/g0/SPEC.g0-c-008.md`. The implementation scope and evidence are
tracked by `worklog/plans/2026-08-20/g0-c-008-pre-rental-bundle.md`.
