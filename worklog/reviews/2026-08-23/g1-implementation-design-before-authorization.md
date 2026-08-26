# G1 implementation-design before authorization

> Status: route corrected; no G1 implementation or GPU execution
>
> Tracker: [G1: design the concrete implementation and local verification plan](https://github.com/icebeeeeeeeef/Toolgap/issues/16)
>
> Canonical owners: [`experiments/g1/SPEC.md`](../../../experiments/g1/SPEC.md)
> and the Wayfinder map.

## Decision

The accepted `G1-PROTOCOL-001` freezes the mechanism question and evidence
oracle, but expressly does not invent an implementation. The reviewed source
route identifies an existing four-file SGLang seam, not the concrete test
harness, observation hooks, normal-request handoff, or exact changed-file
set needed to exercise it. Therefore implementation authorization must be
blocked on a source-backed, reviewable implementation and local-verification
design.

## Consequence

No code or formal experiment is authorized. The authorization ticket remains
open but blocked until the new design review resolves; the later owner freeze
of exact source and formal GPU protocol remains unchanged.

## Source-review correction

A source review of the draft found five design details that change the local
verification contract without changing the four-file runtime seam:

- rejection rows 1--3 release target-session priority before the backend
  declines the physical demote, so the record must retain
  `priority_release`/`released_component_leaves` and every rejection must use a
  fresh server; stale generation remains pre-release;
- the shared-target row uses deterministic identical cached token sequences
  and asserts that both source-managed frontiers identify the same node with
  Full `session_ref == 2` before the action;
- the active-request row records that structural ownership and write/load
  pending checks precede `DEVICE_LOCKED`, and admits the row only when normal
  requests expose the exact lock with all earlier checks clear;
- immediate enabled/bypass wrappers do not span a scheduler step, while the
  stock-liveness wrapper spans scheduler steps until an eviction or timeout;
  zero immediate stock eviction is a guard, not independent evidence; and
- the current facade accepts only the Full component set, so G1 fixes a
  non-SWA model/configuration and keeps `available_size()` rather than adding
  an unexercised SWA branch.

These corrections are applied to
[`experiments/g1/IMPLEMENTATION_DESIGN.md`](../../../experiments/g1/IMPLEMENTATION_DESIGN.md).
`G1-PROTOCOL-001` remains frozen, implementation remains unauthorized, and the
exact source/configuration/runtime freeze still occurs before the first formal
GPU attempt.

## Owner acceptance

On 2026-08-23, the project owner accepted the corrected concrete design:
existing SGLang scripted-test runtime, no new public/external interface, no
ToolGap runtime cache module, the retained four-file SGLang seam, and one
test-only module. This resolves the design review only. It unblocks the
separate implementation-authorization review and does not authorize code or a
GPU experiment.

This acceptance supersedes the earlier statement that implementation
authorization is blocked on the design review: the authorization review is now
available to be worked, but no authorization has yet been granted.
