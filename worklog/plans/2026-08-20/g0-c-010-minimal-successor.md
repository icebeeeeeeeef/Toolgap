# G0-C-010 minimal successor

Status: terminal retained — `BLOCKED_BEFORE_EXECUTION`

Canonical owners: `experiments/g0/SPEC.g0-c-010.md` and `docs/DECISIONS.md`
(D024).

## Scope

Preserve G0-C-009 and its raw attempts. Duplicate its frozen execution package
as 010 and make only two corrections: establish the already-required canonical
CUDA path before bare-command discovery, and ensure failure finalization cannot
mutate an indexed redirected log after sealing.

## Proof

The 010 verifier must fail under the discovered redirected-log behavior and
pass after the minimum implementation. It must also assert the CUDA-path
ordering. No change may alter source pin, patch, model, control, serving, or
timeout semantics.

## Observed terminal

On the verified provider host, `g0-c-010-a10-attempt-001` passed canonical CUDA
path discovery and stopped before an arm when the fixed SGLang GitHub remote
could not establish HTTPS. Its remote and off-host failure seals both verified.
No alternate mirror, source, or dependency path was used.
