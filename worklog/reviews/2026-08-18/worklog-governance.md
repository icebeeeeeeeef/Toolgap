# Worklog governance and date layout

> Decision: accepted
>
> Claim state: `roadmap`
>
> Date: 2026-08-18

## Question

How should the repository retain implementation plans and important
discussions so future agents can recover context and learn from mistakes,
without creating a competing project plan or source of technical truth?

## Evidence

[`docs/README.md`](../../../docs/README.md) assigns scope, Gate order,
checked-demotion semantics, durable decisions, and frozen experiment evidence
to distinct canonical owners. It explicitly prohibits a second global execution
outline beside `docs/ROADMAP.md`. The repository remains in `roadmap`, with G0
at `RESHAPE` and G1 blocked.

## Alternatives considered

1. One flat directory with dates in filenames. This is minimal, but makes
   related same-day material harder to browse as the history grows.
2. A full transcript archive. It preserves volume but mixes decisions with
   discarded reasoning, duplicates evidence, and risks storing sensitive or
   low-signal material.
3. Category directories with a date subdirectory and topic documents. This
   keeps related records together while retaining topical searchability.

## Decision

Use `worklog/plans/YYYY-MM-DD/`, `worklog/reviews/YYYY-MM-DD/`, and
`worklog/lessons/YYYY-MM-DD/`. The date directory is the first partition; each
file inside names one concrete topic. There is deliberately no hand-maintained
index: directory browsing and `rg` are sufficient at this scale.

Plans carry executable local scope. Reviews record only decision-changing
discussion. Lessons record actual counterexamples or mistakes. Every record
links outward to its canonical owner, and changes to canonical facts are made
there first.

## Rejected extensions

- A worklog-specific status taxonomy or workflow state machine;
- a second Gate schedule, experiment archive, or issue tracker;
- automatic raw-chat export;
- a generic knowledge-base subsystem.

## Follow-up

The maintenance rule is in [`AGENTS.md`](../../../AGENTS.md); the user-facing
guide is [`worklog/README.md`](../../README.md).
