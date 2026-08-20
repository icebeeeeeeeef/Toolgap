# G0 infrastructure reuse reshape

Status: completed locally; runtime execution pending rental host

Canonical owners: `docs/governance/EXPERIMENT_AND_EVIDENCE_SOP.md`,
`docs/DECISIONS.md`, and `experiments/g0/SPEC.g0-c-009.md`.

## Goal

Replace G0-C-008's non-causal exact host pins with a successor execution
contract that first states the experiment capabilities, then reuses Alibaba
Cloud's supported GPU substrate wherever it satisfies them.

## Scope

- preserve frozen, unexecuted G0-C-008 unchanged;
- define the repository-wide capability-first, provider-reuse-first rule;
- freeze a G0-C-009 execution package for one physical A10 using Alibaba
  Cloud's official Ubuntu 24.04 NVIDIA GPU image;
- admit a compatible CUDA 13 driver and Python 3.12 minor while retaining exact
  application dependency, source, workload, and evidence identities;
- record the exact image, instance type, versions, and tuning state observed on
  the rented host before either arm starts.

## Non-goals

- installing or replacing an NVIDIA driver, CUDA toolkit, cuDNN, NCCL,
  container runtime, or NVIDIA Container Toolkit;
- changing G0's checked-demote question, invoking physical demotion, or
  authorizing G1;
- introducing a general infrastructure abstraction or provisioning framework.

## Acceptance evidence

- frozen 008 files have no diff;
- the 009 preflight rejects an incompatible substrate, records provider
  identity, and never installs GPU infrastructure;
- the successor bundle passes its local failure, success, tamper, and portable
  seal verifier;
- existing repository checks remain green;
- the decision-changing review and corrected-assumption lesson link back to
  the canonical owners.

## Dependencies

The live attempt requires a newly rented Alibaba Cloud `gn7i` instance using
the official Ubuntu 24.04 NVIDIA GPU image. No cloud purchase or runtime result
is part of this local task.

## Completion evidence

- G0-C-008 remains unchanged; G0-C-009 is the frozen current successor.
- `scripts/verify-g0-evidence.sh` passed.
- `scripts/verify-g0-c-007-bundle.sh` passed its structural checks.
- `scripts/verify-g0-c-008-bundle.sh` passed all local counterexamples.
- `scripts/verify-g0-c-009-bundle.sh` passed its failure, success, tamper, and
  portable-seal counterexamples without claiming a CUDA run.
- `git diff --check` passed.
