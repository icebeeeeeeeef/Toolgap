# CUDA12-COMPAT-001: Restricted CUDA 12.8 Runtime Compatibility Probe

> Gate: G1
>
> Claim state: `roadmap`
>
> Revision type: preformal compatibility probe, not a G1 Gate runtime revision
>
> Formal GPU execution: not authorized by this document

## 1. Purpose and authority

This revision answers one constrained deployment question left open when the
frozen CUDA 13.0 `G1-PREFLIGHT-001` host was unavailable:

> Can the declared Alibaba Cloud CUDA 12.8 host apply the pinned SGLang
> source's CUDA 12 packaging transformation, perform bounded CUDA runtime and
> compiler probes, and complete the existing no-action local-model startup
> test?

`G1-PROTOCOL-001` and `G1-PREFLIGHT-001` remain unchanged. This probe neither
replaces them nor produces a G1 result. Its `claim_state` is always `roadmap`
and its `gate_decision` is always `N/A`.

The pinned input identities are in
[`upstream/sglang/pin.cuda12-compat-001.toml`](../../upstream/sglang/pin.cuda12-compat-001.toml).
The local model identity remains the existing
[`artifacts/model-files.g1-preflight-001.json`](artifacts/model-files.g1-preflight-001.json).

## 2. Fixed execution envelope

| Input | Frozen value |
| --- | --- |
| SGLang base | `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`, tree `25e9bf86d04c27fe380024d9c8c421c3b5b51f3c` |
| Treatment order | `0001-atomic-checked-demote.patch`, then `0002-g1-scripted-forced-demote.patch`, then `0003-cuda12-compat-packaging.patch` |
| Model | `Qwen/Qwen3-0.6B@c1899de289a04d12100db370d81485cdf75e47ca` |
| Model source | verified local snapshot archive only |
| Runtime wheel | A G0 treatment runtime wheel with a sidecar bearing `G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite`; its Python payload is bound to the three-patch tree where 0001 affects runtime, 0002 is test-only, and 0003 is metadata-only; only wheel `METADATA` and `RECORD` receive the four CUDA12 substitutions |
| CUDA wheelhouse | One hash-bound archive containing exactly `sglang-kernel`, `sgl-deep-ep`, `sgl-deep-gemm`, `torch`, `torchvision`, and `torchaudio` CUDA 12.9 wheels plus `wheelhouse-index.json` |
| Host | Linux x86_64, Alibaba Cloud Ubuntu 24.04 NVIDIA GPU image, one A10, driver `580.126.09`, system CUDA `12.8`, Python `3.12.x` |
| Device code | standalone fixed `sm_86` CUDA program compiled by `/usr/local/cuda-12.8/bin/nvcc` |
| Network policy during model startup | `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` |
| Timeout | each dependency, compiler, and startup command at most 1,800 seconds |

The pinned SGLang Dockerfile contains a CUDA 12 packaging route: it changes
`cuda-python` to the CUDA 12 major range, selects the FlashInfer CUDA 12 extra,
removes the CUDA-specific Cutlass extra, and resolves PyTorch through the
`cu129` index. Humming Kernels exposes a separate CUDA 12 extra, so `0003`
also selects it instead of its CUDA 13 extra. `0003` is exactly those four
metadata substitutions. It does not change ToolGap lifecycle code, SGLang
runtime behavior, tests, cache code, or model inputs.

That Dockerfile accepts CUDA 12.6.3 and 12.9.2, not 12.8. Consequently this
host is a measured port probe, not an upstream-supported CUDA 12.8 image or a
reproduction of the full upstream Docker build. The resolver lock and every
installed package are evidence, not assumptions.

The generated input manifest binds six inputs: ToolGap source, SGLang source,
the local model snapshot, the repackaged G0 runtime wheel, its provenance
sidecar, and the minimal CUDA wheelhouse. The operator runs
`19-cuda12-compat-001-project-prereqs.sh` first, then
`00-cuda12-compat-001-bootstrap.sh`, and only then
`20-cuda12-compat-001.sh`. The prerequisite script may install ordinary build
commands only. It must not install, replace, or alter the NVIDIA driver, CUDA,
cuDNN, or NCCL substrate; it instead rejects a host without the declared
provider GPU/CUDA paths. It validates its own static-input binding before any
privileged command. The runner receives absolute `CUDA12_COMPAT_RUNTIME_WHEEL`,
`CUDA12_COMPAT_RUNTIME_WHEEL_PROVENANCE`, and
`CUDA12_COMPAT_CUDA_WHEELHOUSE_ARCHIVE` paths, verifies each against the input
manifest, preserves the wheel and provenance sidecar in the attempt, and
rejects any wheel whose metadata is not exactly the four declared CUDA12
substitutions.

This is deliberately **not** a current-tree source rebuild. Patch 0001 changes
the Python runtime payload; patch 0002 adds only the named test file and is not
part of that payload; patch 0003 changes only package metadata. The local
repackaging helper therefore verifies the G0 prebuilt wheel payload against the
three-patch source tree, permits only build-generated `sglang/_version.py` to
differ, and rewrites only the four `METADATA` dependencies plus `RECORD`. The
GPU host must install that staged wheel; it must not install `$TREATMENT/python`
or invoke a source/Cargo build route.

The OSS input prefix must separately contain the generated input manifest,
ToolGap source seed, SGLang source seed, model snapshot, runtime wheel,
runtime wheel provenance, CUDA wheelhouse archive,
`19-cuda12-compat-001-project-prereqs.sh`, and
`00-cuda12-compat-001-bootstrap.sh`, plus the generated
`input-oss-receipt.json`. On the operator machine,
`scripts/stage-cuda12-compat-001-inputs-oss.sh` uploads precisely that set and
records each OSS object URI, version ID, SHA-256, and size in the receipt. The
generated manifest's `static_inputs`
bounds the SHA-256 and size of both scripts. Each script validates its own
downloaded bytes against that binding before `19` performs any privileged
installation or `00` reads the ToolGap seed. The operator downloads and runs
`19`, then `00`; `20` is taken only from the exact
checkout restored by `00`, never from an independently copied script.
The inner runner additionally checks the receipt against every locally staged
input before it creates a Python environment, so a mutable OSS object name is
not sufficient evidence of the downloaded input set.

The bootstrap script is provided with the generated input manifest and ToolGap
bare seed. It restores the exact detached ToolGap checkout and writes a
bootstrap receipt. The inner runner requires that receipt and verifies every
input before it creates a Python environment.

## 3. Permitted operation

The runner may only:

1. verify the host, GPU, toolkit, source, patch, bootstrap, and local-model
   identities;
2. restore the fixed SGLang source and apply the three patches in the declared
   order;
3. restore the exact patched source, install the staged prebuilt runtime wheel
   without source building, and resolve only ordinary dependencies through the
   Alibaba PyPI mirror. The six top-level CUDA wheels are selected from the
   indexed local wheelhouse; their ordinary transitive dependencies may resolve
   only through that internal mirror. `cuda-tile==1.6.0rc5` is the one declared
   exception: G0 built it from a CUDA 13.1+-only source distribution, so this
   CUDA 12.8 restricted-startup probe first installs the fixed `cu12`
   FlashInfer wheel without resolving that transitive requirement, then leaves
   `cuda-tile` uninstalled and records the exception rather than
   source-building on ECS. A successful probe therefore says nothing about a
   path that imports `cuda-tile`. Record
   the exact lock after the upstream CUDA12 route's CUDA 13 cleanup, including
   the four unqualified NVIDIA CUDA 13 packages selected by the Humming
   Kernels CUDA 13 extra, and local CUDA 12.9 wheelhouse reinstall; the lock
   must contain neither `-cu13` packages nor those unqualified packages at
   version 13. Then import Torch and perform one
   synchronized CUDA tensor operation;
4. compile and run one fixed standalone `sm_86` CUDA program with the declared
   `nvcc` executable; and
5. with offline flags and generation warmup disabled, execute exactly
   `TestG1PreflightStartup.test_local_model_starts_without_runtime_script`,
   record its loopback listener and teardown receipts, scan its command/log
   receipts for scope violations, and seal the resulting artifacts.

The named test does not invoke the scripted action path or create model
requests. It is the only allowed SGLang test selector. The runner must reject
any other selector before execution.

## 4. Prohibited operation

This probe must not create or induce any request, cache lifecycle, priority
release, demotion, eviction, allocator, liveness, benchmark, performance, or
Gate-arm operation. It must not call a model inference HTTP endpoint, use a
candidate backend or mover, or claim device-memory reclamation.

It must not emit a G1 `PASS`, `STOP`, `RESHAPE`, capability conclusion for the
formal protocol, or result for `G1-PREFLIGHT-001`. The compatibility runner
must record `INVALID_SCOPE` and seal its receipts if its command or startup log
indicates an operation outside this section.

## 5. Terminals and evidence

Each sealed attempt has exactly one terminal below. Every terminal preserves
`claim_state: roadmap` and `gate_decision: N/A`.

| Terminal | Meaning |
| --- | --- |
| `BLOCKED_HOST_IDENTITY` | Host, GPU, driver, system CUDA 12.8, input, or patch identity did not match before a runtime probe. |
| `BLOCKED_DEPENDENCY_TRANSPORT` | The recorded resolver download failed by timeout, network, TLS/proxy, or HTTP transport error; it is not a CUDA result. |
| `BLOCKED_DEPENDENCY_RESOLUTION` | Resolver/source-build work failed without affirmative transport evidence; it is not a CUDA result. |
| `RUNTIME_INCOMPATIBLE` | The CUDA 12 resolver route could not import Torch or complete the bounded CUDA tensor operation. |
| `TOOLKIT_COMPILER_FAILED` | The standalone `sm_86` program did not compile or run with the declared CUDA 12.8 toolkit. |
| `SGLANG_STARTUP_JIT_FAILED` | The sole restricted startup test failed with an attributable runtime JIT/compiler failure. |
| `SGLANG_STARTUP_FAILED_OTHER` | The sole restricted startup test failed for another recorded startup reason. |
| `INVALID_SCOPE` | The enforced selector/command/log scope check found a prohibited operation. |
| `COMPATIBLE_FOR_RESTRICTED_STARTUP_ONLY` | All permitted operations completed with clean teardown. This is not G1 admission. |

For every attempt, retain host and GPU readbacks; input and bootstrap receipts;
the staged runtime wheel, G0 provenance sidecar, runtime metadata validation,
CUDA wheelhouse index and validation; source/patch provenance; resolver command, report, exact
package lock, and pre/post CUDA13-distribution cleanup lists; Torch CUDA probe;
CUDA source, compiler log, and program output; startup
command/log/listener/process/GPU-PID teardown receipts; scope-scan log;
manifest; terminal; and artifact index. The ECS host only retrieves inputs. On
the operator machine, after local terminal verification,
`scripts/anchor-cuda12-compat-001-oss.sh` uploads the indexed artifacts to one
unique raw OSS prefix and writes an external JSON anchor at a separate prefix.
That anchor binds the completion receipt, execution status, artifact index,
and every indexed artifact to its OSS object version. A completed probe is
retained only once the command prints the external anchor URI and version ID.

## 6. Progression

`COMPATIBLE_FOR_RESTRICTED_STARTUP_ONLY` permits consideration of a separately
frozen CUDA 12-compatible preflight revision. It does not unfreeze the CUDA
13.0 `G1-PREFLIGHT-001` contract, prove the full upstream Docker image,
authorize the formal G1 protocol, or prove any ToolGap mechanism claim. Any
future Gate execution still needs its own host choice, frozen runtime revision,
arms, controls, evidence oracle, and explicit billed-host approval.
