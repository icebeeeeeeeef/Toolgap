# G1 implementation authorization

> Status: completed; bounded local implementation authorized
>
> Tracker: [G1: authorize implementation of the accepted protocol](https://github.com/icebeeeeeeeef/Toolgap/issues/9)
>
> Canonical owners: [`experiments/g1/SPEC.md`](../../../experiments/g1/SPEC.md)
> and [`experiments/g1/IMPLEMENTATION_DESIGN.md`](../../../experiments/g1/IMPLEMENTATION_DESIGN.md)

## Scope

- obtain the project owner's explicit decision on bounded local G1
  implementation and test iteration;
- record the authorized source boundary, prohibited work, environment/cost
  constraints, and completion evidence required before the later source-and-run
  freeze review;
- do not modify runtime code, run a formal GPU protocol, or select a G1 Gate
  outcome in this ticket.

## Authorization Candidate

The accepted local implementation boundary is the existing four-file SGLang
checked-demote seam plus one scripted-runtime test module. It has no public or
external interface, no ToolGap runtime cache module, and no replacement of
SGLang's physical KV ownership. Local completion requires the checks listed in
`IMPLEMENTATION_DESIGN.md` section 7; it remains a prerequisite for, not a
substitute for, the later owner-approved formal source-and-run freeze.

## Completion

On 2026-08-23, the project owner explicitly authorized the candidate scope:
local SGLang implementation and test iteration limited to the existing
four-file checked-demote seam plus one scripted-runtime test module. The owner
provided no additional cost or environment constraint. Formal GPU execution,
Gate classification, public interfaces, G2 lifecycle work, performance scope,
and a second physical data plane remain unauthorized.

The next implementation ticket must retain the local completion evidence from
`IMPLEMENTATION_DESIGN.md` section 7. It remains a prerequisite for, not a
substitute for, the later owner-approved formal source-and-run freeze.
