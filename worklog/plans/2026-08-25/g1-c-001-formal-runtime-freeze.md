# G1-C-001 formal runtime freeze

Canonical owners: `experiments/g1/SPEC.md`, `docs/ROADMAP.md`, and
`docs/DEMOTION_CONTRACT.md`.

## Executable scope

The project owner has authorized preparation, independent review, and then one
formal G1 execution attempt after the completed CUDA12-COMPAT-001 probe. Create
one new CUDA 12-compatible `G1-C-001` runtime revision rather than mutating any
sealed preflight or compatibility bundle.

The revision must freeze the existing checked-demote seam and scripted runtime
treatment, exact offline model/runtime inputs, fresh enabled and bypass arms,
the four protocol rejection rows, stock-eviction liveness, allocator evidence,
cleanup, terminal validation, and external versioned OSS anchoring. A later
formal attempt may select only the frozen `PASS`, `STOP`, or invalid/blocked
terminal defined by the new revision.

## Boundaries

No G2 lifecycle case, public pause API, ToolGap physical KV ownership, second
data plane, performance comparison, or mutation of already sealed evidence is
in scope. The completed CUDA12 compatibility probe removes only startup
admission uncertainty; it does not supply any G1 mechanism evidence.

## Completion

Commit the formal runtime bundle, run its static checks, obtain an independent
review, then stage the exact committed bundle and execute it once on the
existing compatible host. Preserve every terminal and do not retry under an
attempt ID.
