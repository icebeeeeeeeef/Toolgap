# G1 implementation authorization decision

> Status: accepted owner authorization; no implementation or GPU execution in
> this ticket
>
> Tracker: [G1: authorize implementation of the accepted protocol](https://github.com/icebeeeeeeeef/Toolgap/issues/9)
>
> Canonical owners: [`experiments/g1/SPEC.md`](../../../experiments/g1/SPEC.md)
> and [`experiments/g1/IMPLEMENTATION_DESIGN.md`](../../../experiments/g1/IMPLEMENTATION_DESIGN.md)

## Decision

On 2026-08-23, the project owner explicitly authorized bounded local G1
implementation and test iteration: retain the four-file SGLang checked-demote
seam and add one scripted-runtime test module. The work has no public or
external interface, no ToolGap runtime cache module, and no replacement of
SGLang's physical KV ownership.

No additional cost or environment constraint was specified. The authorization
does not include a formal GPU experiment, a G1 `PASS` or `STOP` conclusion, a
public API, G2 lifecycle work, performance comparison, or a second physical
KV data plane.

## Required local handoff

The implementation must produce the local checks named in
`IMPLEMENTATION_DESIGN.md` section 7: retained G0 source-contract tests, an
importable and schema-validated test record, static scope checks, a changed-path
inventory, and a mapping from every observation to the frozen G1 protocol.
Only then may the later owner review freeze exact source and formal GPU runtime
protocol.

## Canonical follow-up

The next frontier is [G1: implement the accepted mechanism protocol](https://github.com/icebeeeeeeeef/Toolgap/issues/12). It is a separate Wayfinder session;
this authorization ticket does not begin implementation.
