# G0-C-017 independent Gate review

> Review date: 2026-08-21
>
> Attempt: `g0-c-017-a10-attempt-001`
>
> Decision: `PASS`
>
> Project claim state: `roadmap`

## Reviewed identity

- ToolGap protocol commit: `dbaa3ccfad71beec87676cac8414ae9c5f678323`
- ToolGap protocol tree: `c940fb078ec859985adae3dee3d9f66b0c0a32b0`
- G0-C-017 SPEC SHA-256:
  `1abeb4b6869c2694022e0b32c74f80e81a53bef51100fb7105e9392212cbcc27`
- SGLang base commit: `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`
- SGLang base tree: `25e9bf86d04c27fe380024d9c8c421c3b5b51f3c`
- treatment patch SHA-256:
  `e69776678909b4ee49b1c0fa4a8e208666893b659c0508387c83fcdf11e82a9a`
- stock wheel SHA-256:
  `c180d592868014116445ba77bee4791c6a20eef9d3b2b35e8f27574ff121b779`
- treatment wheel SHA-256:
  `68c63d2fe77cc37b4eccd29ae49678160302744e883934e306d36b0725138f89`
- dependency-lock SHA-256:
  `1882bcd727f9aa765b48dddfab2804d07bac2bba4df54ecfc4d9349e611dd37f`

The attempt, manifest, retained wheels, provenance, and current frozen 017
executables agree with these identities. Changes after the attempt were limited
to result documentation.

## Independent checks

Both prescribed read-only verifiers exited zero against the off-host bundle:

```text
python3 experiments/g0/commands/g0_c_016_verify_evidence.py \
  --run-dir experiments/g0/raw/g0-c-017/g0-c-017-a10-attempt-001
python3 experiments/g0/commands/g0_c_017_finalize.py verify \
  --run-dir experiments/g0/raw/g0-c-017/g0-c-017-a10-attempt-001
```

The reviewer also checked the raw wheel contents and provenance, source and
installed controls, request receipts and SSE streams, server logs, cleanup
snapshots, and completion bindings. The observed results were:

- stock 27/27 expected RED; treatment 27/27 GREEN;
- installed treatment seam returned `UNSUPPORTED_BACKEND`, applied priority
  release, and made zero physical `demote` calls;
- static inventory found no production caller outside the one registered cache
  surface;
- both stock and treatment initialized real A10 CUDA HiCache serving;
- four requests returned HTTP 200 with valid terminal SSE, and each arm's
  second request reported 48 device-cached tokens;
- both runner-attributed shutdowns reaped status 137 and left no process-group,
  target-listener, or attributable-GPU survivor;
- artifact-index, execution-status, and completion-receipt bindings match.

## Decision and boundary

No Gate-blocking counterexample remained. Combined with the independently
reviewed G0-C-006 source evidence, this closes the frozen G0 PASS conditions.

The only promoted `experimentally validated` claim is that, on the exact frozen
source, patch, wheels, dependency lock, model, and A10/CUDA host, the treatment
package installs; its registered seam can fail closed; and the patched package
coexists with ordinary HiCache CUDA serving and complete cleanup.

This does not prove a CUDA serving call to checked demotion, physical `demote`,
allocator-visible reclamation, lifecycle/recovery correctness, output equality,
performance benefit, upstream acceptance, or compatibility outside the frozen
environment. G1 planning and a frozen SPEC may proceed; G1 execution is not
authorized by this review.
