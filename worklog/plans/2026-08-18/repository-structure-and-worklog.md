# Repository structure and worklog foundation

> Status: completed
>
> Claim state: `roadmap`
>
> Date: 2026-08-18

## Goal

Make the planned source landing points visible without implying a runtime
implementation, and establish a small, durable place for task plans, material
reviews, and corrections.

## Scope

- Record the Gate-conditional source layout in
  [`docs/ARCHITECTURE.md`](../../../docs/ARCHITECTURE.md#9-source-layout-and-gate-conditional-landing).
- Add documentation-only markers for the future `src/`, `upstream/`, `tests/`,
  and `benchmarks/` landing points.
- Create the date-partitioned `worklog/` and make its maintenance contract
  discoverable from the repository guide and collaboration instructions.

## Non-goals

- Do not create a runtime package, upstream pin, SGLang patch, CUDA test, or
  benchmark harness.
- Do not change Gate order, checked-demotion semantics, or the frozen G0
  evidence.
- Do not make `worklog/` a duplicate of `docs/ROADMAP.md` or
  `docs/DECISIONS.md`.

## Acceptance evidence

- The source-layout document says when each future component may land and
  keeps G1 blocked while G0 remains `RESHAPE`.
- Each worklog category is partitioned as
  `YYYY-MM-DD/<topic>.md` and has a documented authority boundary.
- `AGENTS.md` directs contributors to search and maintain the worklog without
  allowing it to replace canonical documents.
- Repository whitespace and frozen-G0 evidence checks still pass.

## Result

Completed with documentation-only structure markers and the worklog contract.
No runtime, CUDA, allocator, upstream-integration, or performance claim is
made by this record.
