# SGLang integration area

> Status: `roadmap`; no active upstream patch is authorized in this directory.

This directory records the narrow SGLang seam needed by ToolGap without
vendoring or copying the SGLang source tree. The authoritative current source
audit and frozen patch artifacts remain under `experiments/g0/` and
`docs/ARCHITECTURE.md`.

The current successor execution contract uses:

- `pin.g0-c-009.toml` for the exact source/application identity and admitted
  provider capability envelope;
- `patches/0001-atomic-checked-demote.patch` as the temporary reviewed patch;
- contract tests that run against the selected SGLang checkout.

The physical KV tree, allocator, movement, and eviction remain SGLang-owned.
An upstream merge is valuable external evidence but must not be confused with
ToolGap runtime ownership or treated as a prerequisite unless the active Gate
SPEC explicitly requires it.
