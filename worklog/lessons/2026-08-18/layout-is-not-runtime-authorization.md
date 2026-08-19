# Directory layout is not runtime authorization

> Status: active rule
>
> Claim state: `roadmap`
>
> Date: 2026-08-18

## Trigger

The repository needs visible landing points for future source code while G0 is
`RESHAPE` and G1 is blocked.

## Incorrect assumption corrected

A plausible but wrong reading is that creating the eventual package tree means
the project has started, or is authorized to start, the runtime implementation.
That would turn organizational scaffolding into an unsupported progress claim.

## Evidence

[`docs/ARCHITECTURE.md`](../../../docs/ARCHITECTURE.md#9-source-layout-and-gate-conditional-landing)
states that runtime files may land only after a reviewed successor seam and an
exact pin, then after G0 passes for the candidate runtime. The current root
README records that G1 remains blocked.

## Correction

Keep only explanatory markers in the planned source directories until their
listed Gate authorization exists. Do not add empty importable modules,
placeholder interfaces, fake tests, or generic shared utilities merely to make
the tree look complete.

## Rule for future work

Before adding a runtime, upstream-integration, test, or benchmark file, cite
the exact Gate condition in the plan and verify that the canonical owner shows
it satisfied. If the real invocation seam keeps candidate logic inside the
SGLang patch, keep it there rather than manufacturing a standalone package.
