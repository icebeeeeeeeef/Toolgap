# G1-PREFLIGHT-001 runtime admission

> Canonical owner: `experiments/g1/SPEC.g1-preflight-001.md`

## Scope

Freeze and independently review a preformal, offline runtime-admission bundle
for the accepted G1 mechanism source. It verifies only source restoration,
patched SGLang install/import, a sealed local model, and a read-only scripted
runtime cache qualification record on the declared GPU host.

## Required controls

- bind ToolGap, SGLang, and model snapshot archives in one generated
  SHA-256 manifest; do not trust a mutable repo name, branch, or OSS ETag;
- apply `0001` then `0002`, require an absolute local model directory, and set
  the Hugging Face and Transformers offline flags;
- run the sole no-action `TestG1PreflightSmoke` class, not the formal G1 test
  module or any request/demotion/liveness arm; and
- emit immutable success/failure terminals whose Gate decision is always
  `N/A`.

## Exclusions

This work does not run `checked_demote_session`, normal `/generate` traffic,
rejections, bypass/liveness controls, or a formal G1 Gate attempt. Completion
does not authorize a future G1 runtime revision.
