# G1-C-012 load-back threshold

Canonical owners:
`experiments/g1/SPEC.g1-c-012.md` and `experiments/g1/SPEC.g1-c-013.md`.

## Falsified assumption

G1-C-012 correctly made the session frontier leaf the exact load-back anchor,
but assumed that this identity repair was sufficient to create a pending
transfer. Formal attempt `g1-c-012-a1-20260825T123410Z` falsified that
assumption: its first seven arms passed, then `reject_load_back_pending` ended
when the loader completed without exposing pending state. The sealed terminal
classification is `INVALID`.

Preserved raw-evidence prefix:
`oss://agentic-kv-c0-evidence-20260812/g1/g1-c-012/d276c7f/raw/`.
The externally read-back anchor is
`oss://agentic-kv-c0-evidence-20260812/g1/g1-c-012/d276c7f/anchors/g1-c-012-a1-20260825T123410Z/external-anchor-da841bedc82c8da6e926b01e6f13b8de7fb45b11f2e41d808cbc6e5379a4078d.json`,
version
`CAEQnAYYgYCAqNaC5IEaIiAxOTRhNmZmMmRkNGI0MWQ3OWIwMDRkMTJkYTQxZDYwNQ--`,
SHA-256 `da841bedc82c8da6e926b01e6f13b8de7fb45b11f2e41d808cbc6e5379a4078d`.
It binds 170 indexed artifacts with `gate_decision=INVALID`.

## Root cause

The arm's ordinary private session generated an eight-token Host-only tail.
Pinned `UnifiedRadixCache` sets `load_back_threshold` to ten and returns before
allocation, commit, or `ongoing_load_back` when a Full-only transfer is smaller
than that threshold. The observed loader batch recomputed nine tokens: the
eight-token Host tail plus the appended identity token. No pending window had
been created, so this was fixture qualification failure rather than evidence
about the checked guard.

## Correction

G1-C-013 sizes only the load-back arm's ordinary private session from the
pinned runtime threshold, then asserts that the exact target's committed Host
value meets that threshold before pressure or loader submission. Lowering the
specialized setup back to eight tokens is retained as a counterexample. The
production threshold and load-back path remain unchanged.
