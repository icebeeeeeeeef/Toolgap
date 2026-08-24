# G1-PREFLIGHT-001 cross-review

> Canonical owner: `experiments/g1/SPEC.g1-preflight-001.md`

## Decision

Retain the preformal admission scope, with no G1 Gate decision. Cross-review
rejected a live cache qualification during this revision: the inherited
scripted-runtime flow could warm up through generation or reset/flush state.
The retained startup test disables warmup and does not execute a runtime
script, request, demotion, or cache assertion.

## Corrections required before freezing

- make the ToolGap bootstrap Bash-3-compatible and restore from its bare seed;
- repair `0002`'s new-file hunk count, then prove `git apply` and Python
  compilation in a disposable clone of the pinned SGLang base;
- make static replay disposable rather than modifying its caller's checkout;
- bind the finalizer's context, input manifest, bootstrap receipt, rendered
  manifest, archives, and indexed terminal artifacts; and
- require teardown of the startup receipt's exact listener as well as the
  process group and attributable GPU PIDs.

The finalizer reports internal consistency only. Whole-directory adversarial
rewrites require the OSS versioned-object anchor specified in the canonical
preflight SPEC; that is evidence retention, not an in-run network dependency.

## Verification retained

- ToolGap bare-seed bootstrap restored the pinned detached commit/tree and
  passed input-manifest verification.
- The full SGLang seed replay applied `0001`, then `0002`, and compiled the
  resulting test module without dirtying the source checkout.
- Finalizer success verification passed; direct receipt tampering and a
  coherently reindexed manifest-input substitution were both rejected.
