# G1-PREFLIGHT-001: Offline Runtime Admission

> Gate: G1
>
> Claim state: `roadmap`
>
> Revision type: preformal runtime admission, not a G1 Gate runtime revision
>
> Formal GPU execution: not authorized by this document

## 1. Purpose and authority

This revision makes one narrow operational question answerable before renting a
formal G1 machine:

> Can the pinned SGLang treatment import on the declared CUDA host and start a
> scripted-runtime server from the sealed local Qwen snapshot without relying
> on GitHub or Hugging Face at run time?

`G1-PROTOCOL-001` remains the authority for a future forced-demotion Gate run.
This document neither replaces it nor freezes a future `G1-C-*` formal runtime
revision. It can emit only a preflight terminal: `COMPLETED`,
`BLOCKED_BEFORE_RUNTIME`, or `RUNTIME_FAILED`. Its `gate_decision` is always
`N/A`.

The fixed inputs are in
[`upstream/sglang/pin.g1-preflight-001.toml`](../../upstream/sglang/pin.g1-preflight-001.toml).
The model's file identity is in
[`artifacts/model-files.g1-preflight-001.json`](artifacts/model-files.g1-preflight-001.json).

## 2. Fixed execution envelope

| Input | Frozen value |
| --- | --- |
| SGLang base | `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`, tree `25e9bf86d04c27fe380024d9c8c421c3b5b51f3c` |
| Treatment order | `0001-atomic-checked-demote.patch`, then `0002-g1-scripted-forced-demote.patch` |
| Model | `Qwen/Qwen3-0.6B@c1899de289a04d12100db370d81485cdf75e47ca` |
| Model source | absolute local directory restored from the verified snapshot archive |
| Network policy during model startup | `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` |
| Host | Linux x86_64, Alibaba Cloud Ubuntu 24.04 GPU image, one A10, CUDA 13.0, Python 3.12.x |
| Timeout | each dependency/build/model-start command at most 1,800 seconds |

The operator first runs `00-g1-preflight-001-bootstrap.sh`, supplied beside the
generated input manifest and ToolGap bare seed. It safely restores the seed,
runs `git fsck`, clones a detached checkout at the manifest's commit/tree, and
writes a bootstrap receipt. The inner runner requires that receipt. The
generated OSS input manifest binds the ToolGap seed, the existing verified
SGLang seed, the model archive, and this revision's static artifacts by
SHA-256. OSS ETags are not evidence identities.

## 3. Permitted operation

The runner may:

1. verify the host and all offline input identities;
2. restore SGLang from the bare seed and apply the two patches in order;
3. resolve normal Python dependencies, build/install one treatment wheel, and
   prove that the installed modules match its checkout;
4. start the local model with generation warmup disabled and execute exactly
   `TestG1PreflightStartup.test_local_model_starts_without_runtime_script`;
5. record the server-start receipt and process-group, listener, and
   attributable-GPU-PID teardown evidence; and
6. seal the raw artifacts.

`0002` requires `TOOLGAP_G1_MODEL_PATH` to be an existing absolute directory.
It has no model-repository fallback. The runner supplies the directory only
after the snapshot archive and every inventory entry verify.

## 4. Prohibited operation

No preflight path may invoke or induce:

- `/generate`, request construction, session priority release, or normal
  request-pressure traffic;
- `checked_demote_session`, `release_session_priority`, `demote`, `evict`, or
  a candidate backend/mover invocation;
- enabled, bypass, rejection, stock-liveness, allocator-delta, or G1 outcome
  assertions; or
- a G1 `PASS`, `STOP`, `RESHAPE`, performance, allocator-reclamation, output,
  or lifecycle claim.

The named startup test never calls `execute_script`; this avoids the scripted
runtime's reset/flush path as well as model-generation warmup. It does not read
or qualify a live cache. Full-only allocator qualification is reserved for the
separately approved formal G1 revision, which must run any other class from the
same test module only under its own frozen contract.

## 5. Admission and evidence

Before runtime start, the runner must retain:

- ToolGap seed archive SHA-256, bootstrap receipt, commit/tree, and
  tracked-clean readback;
- host, GPU, CUDA, Python, and dependency readback;
- SGLang seed SHA-256 plus `git fsck`, base commit/tree, patch order, patch
  SHA-256 values, and changed-path inventory;
- model archive SHA-256, local snapshot receipt, and exact file inventory;
- installed-module provenance, including the test module source SHA-256; and
- immutable copies of the generated input manifest and bootstrap receipt, plus
  the rendered runtime manifest and SHA-256 before the scripted server starts.

Successful completion requires a zero-status schema check, a zero-status
startup test with one `G1_PREFLIGHT_SERVER_STARTED` record asserting disabled
generation warmup and identifying its loopback HTTP listener, and teardown
quiescence of the process group, attributable GPU PIDs, and that listener. A
failure leaves an immutable terminal receipt and raw logs. It does not
authorize a retry under the same attempt ID.

The finalizer's local `verify` command is an **internal-consistency** check: it
rechecks the exact context, input manifest, bootstrap receipt, rendered
manifest, artifact index, and terminal bindings, but cannot defend against an
actor that can rewrite the whole attempt directory and recompute every hash.
Before any completed preflight is cited as retained evidence, the operator must
place the sealed directory under a unique, versioned OSS object prefix and
record the completion-receipt SHA-256 together with the immutable object
version outside that directory. This external anchoring step is an evidence
retention requirement, not a model/runtime network dependency.

## 6. Progression

A completed `G1-PREFLIGHT-001` shows only that this frozen environment and
transport path can load the chosen local model into the patched runtime. It is
an admission input to, not a substitute for, a separate owner-approved formal
G1 runtime revision. The later revision must still freeze all Gate arms,
rejections, liveness controls, workload, evidence oracle, repeat rules, and
cleanup protocol required by `G1-PROTOCOL-001`.
