# G1-PREFLIGHT-001 cloud provisioning

> Canonical owner: `experiments/g1/SPEC.g1-preflight-001.md`

## Scope

Provision one disposable Alibaba Cloud Beijing A10 host solely to run the
already frozen `G1-PREFLIGHT-001` offline runtime admission. The host must use
the declared Ubuntu 24.04 GPU image, download the exact `a48e8d1` inputs from
the versioned OSS prefix, and run the supplied bootstrap then no-action
preflight runner once.

## Required controls

- create a vSwitch in an A10-available zone because the pre-existing default
  vSwitch is in `cn-beijing-f`, which has no stock for the chosen SKU;
- attach an ECS RAM role with only `oss:GetObject` under
  `g1/preflight-001/a48e8d1/`; never copy account access keys to the host;
- use a dedicated security group allowing SSH only from the operator's current
  public IPv4 address and a dedicated imported public key; and
- set an explicit automatic release time before starting the billed instance,
  retain the final sealed attempt in the separately versioned OSS output
  prefix, then delete the disposable compute and access resources if they are
  no longer needed.

## Exclusions

This plan does not authorize a formal G1 run, source revision change, use of
the existing world-open security group, reuse of an unknown private key, or
any G1 Gate decision. The priced `RunInstances` request requires an explicit
operator confirmation after its dry-run and cost details are known.

## Observed blocker

Live image discovery on 2026-08-24 found that the sole available official
Ubuntu 24.04 NVIDIA GPU image in the requested family currently reports CUDA
12.8. The frozen preflight requires CUDA 13.0, so no priced instance was
created. See `worklog/reviews/2026-08-24/g1-preflight-provider-cuda-drift.md`.
