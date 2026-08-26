# G1-PREFLIGHT-001 provider CUDA drift review

> Canonical owner: `docs/DECISIONS.md` D036

## Question

Can the frozen CUDA 13.0 preflight be launched on the currently available
Alibaba Cloud Ubuntu 24.04 GPU image?

## Live evidence

On 2026-08-24, `DescribeImages` in `cn-beijing` returned exactly one member of
the official image family
`acs:ubuntu_24_04_x64_with_nvidia_gpu_driver_and_cuda`:

- image ID/name:
  `ubuntu_24_04_x64_100G_with_gpu_driver_and_cuda_alibase_20260519.vhd`;
- image version: `v2026.6.9`;
- provider description: kernel `6.8.0-111-generic`, driver `580.126.09`, CUDA
  `12.8`.

`DescribeInstances` returned no retained Beijing instance. The frozen SPEC and
pin require provider CUDA 13.0, and the frozen runner checks that `nvcc`
reports release 13.0 before it can start the no-action startup test.

## Decision

The image is not admissible. Do not create a billed GPU instance, substitute a
driver check for the CUDA toolkit check, install CUDA manually, or mutate the
frozen preflight in place. The result is a provisioning blocker before runtime,
not a G1 result.

## Operational state

The versioned OSS input prefix has been populated and verified by object size
and the manifest/bootstrap SHA-256 readback. A dedicated `cn-beijing-i`
vSwitch, SSH `/32` security group, imported public key, and an ECS role with
only `oss:GetObject` under the frozen input prefix now exist. These resources
are not experimental evidence and must be deleted when the successor host
decision is settled.
