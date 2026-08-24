# CUDA12-COMPAT-001 runtime admission

> Tracker: [G1: decide CUDA 12.8 preformal runtime admission](https://github.com/icebeeeeeeeef/Toolgap/issues/17)
>
> Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`
>
> Status: in progress

## Scope

Freeze a separate, no-action compatibility probe for the only currently
available Alibaba Cloud Ubuntu 24.04 GPU image: one NVIDIA A10, driver
`580.126.09`, and provider toolkit `CUDA 12.8`. The question is deliberately
narrow:

> Can this provider CUDA 12.8 host, using the pinned SGLang source's own CUDA
> 12 packaging transformation and cu129 dependency route, compile a bounded
> CUDA program and complete the local-model no-action startup test?

The pinned source's Dockerfile provides the packaging transformation, but it
accepts CUDA 12.6.3 and 12.9.2 rather than 12.8. Therefore CUDA 12.8 is a
measured compatibility question, not an upstream-supported configuration.

## Frozen treatment and exclusions

- retain the existing source seed, base commit, local model inventory, and
  `0001` then `0002` patch order;
- add a separately hash-bound `0003-cuda12-compat-packaging.patch` which only
  applies the three documented metadata substitutions: `cuda-python` major
  range, FlashInfer `cu12`, and no CUDA-specific Cutlass extra;
- use the source-provided cu129 PyTorch resolver route, record its actual lock,
  and make no claim that the full upstream Docker image was reproduced; and
- create no request, cache, demotion, priority-release, eviction, allocator,
  liveness, benchmark, or G1 Gate operation. `G1-PREFLIGHT-001` remains
  unchanged and is never executed.

## Acceptance and terminals

1. Static bundle: an exact clean ToolGap revision, source/model archives,
   patch hashes, manifest template, bootstrap, runner, finalizer, and static
   verifier exist before a host is rented.
2. Host and restore identity: exact Ubuntu 24.04 image family, one A10,
   driver, CUDA 12.8 `nvcc`, source, patches, and local model verify. Any
   mismatch is `BLOCKED_HOST_IDENTITY`.
3. Runtime loader: the cu129-resolved Torch wheel imports and performs a
   synchronized CUDA tensor operation. Failure is `RUNTIME_INCOMPATIBLE`.
4. Compiler boundary: a standalone fixed `sm_86` CUDA program compiles and
   executes through `/usr/local/cuda-12.8/bin/nvcc`. Failure is
   `TOOLKIT_COMPILER_FAILED`.
5. Restricted startup: only
   `TestG1PreflightStartup.test_local_model_starts_without_runtime_script` may
   run, with offline flags and warmup disabled. Its failure is a narrowly
   classified startup failure, never a Gate result.
6. All terminals retain `claim_state: roadmap` and `gate_decision: N/A`; a
   successful terminal can establish only
   `COMPATIBLE_FOR_RESTRICTED_STARTUP_ONLY`.

## Required evidence

The sealed attempt retains host readbacks, input and bootstrap receipts,
resolved package lock/install report, CUDA source/build/output, startup and
teardown receipts, terminal, and artifact index. The operator uploads these
afterward to a new versioned OSS prefix and records immutable object versions
outside the attempt directory. The ECS role remains read-only for OSS input.

## Completion boundary

This task ends after independent static review and the frozen compatibility
bundle are committed. Renting an instance requires a fresh stock/image check,
cost disclosure, and explicit confirmation for the billed creation request.
No formal G1 run follows from this task.
