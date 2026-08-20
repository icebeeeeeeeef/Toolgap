# G0-C-009 rental attempt 001

Status: terminal retained — `BLOCKED_BEFORE_EXECUTION`

Canonical owners: `experiments/g0/SPEC.g0-c-009.md` and
`docs/governance/EXPERIMENT_AND_EVIDENCE_SOP.md`.

## Executable scope

Run one fresh attempt, `g0-c-009-a10-attempt-001`, on the already verified
Alibaba Cloud Ubuntu 24.04 `ecs.gn7i-c16g1.4xlarge` instance. The host checkout
must detach at ToolGap commit `1f59969afca994e09902221f27bc63f0c79fa85e`, remain
tracked-clean, and run commands 19 through 23 once and in numeric order.

## Boundaries

- Reuse the provider's installed driver and CUDA only. Command 19 may install
  only its listed ordinary build tools when absent.
- Do not change the frozen SPEC, pin, patch, model revision, versions, or
  timeouts in response to a failure.
- Stop at the first terminal. Preserve the generated, ignored attempt directory
  and copy it off host before any instance release.

## Completion evidence

The authoritative result is the sealed raw attempt under
`experiments/g0/raw/g0-c-009/g0-c-009-a10-attempt-001/`, not this worklog.
This entry will be superseded with the terminal and canonical evidence link
after the run.

## Observed terminal

Command 19 completed after installing only its allowlisted project build tools.
Command 20 then sealed `BLOCKED_BEFORE_EXECUTION` before either arm because
`nvcc` was not on the initial shell `PATH`. The provider CUDA executable was
separately observed at `/usr/local/cuda-13.0/bin/nvcc`; command 20 checks that
same absolute path only after its earlier bare-command admission. The complete
raw attempt was copied off host and passed the offline finalizer verification.
No phase was rerun and no Gate conclusion follows from this pre-arm terminal.
