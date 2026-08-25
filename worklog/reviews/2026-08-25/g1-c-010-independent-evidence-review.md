# G1-C-010 independent evidence review

Canonical owners: `experiments/g1/RESULTS.md` and `docs/ROADMAP.md`.

Independent review found no P0, P1, or P2 blocker and selected `Ready: Yes` for
the sealed G1-C-010/A1 `PASS` within its frozen scope.

The review recomputed all 159 local sealed-file hashes and sizes, fetched all
159 raw OSS objects by exact version ID and recomputed their hashes and sizes,
and checked the seven frozen input object versions. All matched. It verified the
sealed selector logs, bindings, records, cleanup evidence, identity, and
provenance, then replayed the PASS oracle offline. The enabled arm freed exact
IDs 257 through 264 and increased allocator capacity from 3832 to 3840; bypass
retained the same IDs and capacity with no checked or physical action. All four
rejection controls and stock-eviction liveness met their frozen predicates.

External anchor:

`oss://agentic-kv-c0-evidence-20260812/g1/g1-c-010/ac31ff2/anchors/g1-c-010-a1-20260825T095119Z/external-anchor-09f2594d1162122591484b2ad034f9749821d0cfceb39303dc85bc425c922ac5.json`

Version ID:
`CAEQnAYYgYCAyd_b4YEaIiAyY2YyYmQwNTZjNmE0MzQ3YTNmNGYyZDg2NzkyZjgwZg--`.

The accepted boundary is one A10/CUDA 12.8 host, Qwen3-0.6B, Full-only, one
generation, one action, and one eight-token private tail. The result does not
prove performance, output equivalence, restore/recovery, concurrent or repeated
lifecycle behavior, SWA/MAMBA, production API/policy, or statistical
repeatability.
