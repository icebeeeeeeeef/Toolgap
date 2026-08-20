# G0 infrastructure reuse steelman review

Canonical decision: `docs/DECISIONS.md` D023. Successor contract:
`experiments/g0/SPEC.g0-c-009.md`.

## Decision question

Which smallest host contract preserves a decisive G0 integration result while
using Alibaba Cloud's supported GPU infrastructure instead of rebuilding it?

## Steelman

The strongest form of the original exact-host design is reproducibility: one
OS, driver, Python, source, and model identity minimizes hidden drift. Its valid
core is to make both arms attributable and comparable, not to insist that the
project install every component itself.

## Extend

Separate causal invariants from substrate provenance. Keep one A10, real CUDA,
paired arm identity, pinned source/application packages, and workload exact.
Let the provider own its supported Ubuntu GPU image; admit compatible driver
and Python envelopes and seal the exact observed image and versions. Prefer:

1. official preinstalled GPU image plus project virtual environments;
2. provider-managed driver installation only if no suitable image exists;
3. a container only after a demonstrated isolation conflict;
4. manual driver/runtime installation only in a new justified SPEC.

## Adversarial attack

- A mutable image label could hide drift: require bounded IMDSv2 readback and
  seal the exact image ID before either arm.
- A newer driver could appear compatible but fail the application: require
  Torch CUDA 13, one visible A10, and `torch.cuda.is_available()` in both arm
  environments.
- Provider CUDA 12.8 may be the default: select and record the provider's
  `/usr/local/cuda-13.0` path without installing another toolkit.
- Provider tuning could confound performance: retain visible KeenTune state;
  G0 makes no performance claim, and later paired performance Gates must freeze
  the exact substrate/tuning state.
- Containers would improve isolation but add a second launch/provenance layer
  without a demonstrated G0 problem, so they are rejected now.

## Synthesis

Adopt G0-C-009 with the official Alibaba Cloud Ubuntu 24.04 NVIDIA GPU image on
`gn7i`. Recommend the currently selected `ecs.gn7i-c16g1.4xlarge`, but treat
CPU/RAM SKU as recorded operational provenance rather than the checked-demote
cause. Do not select the separate driver-install option. Permit only missing
ordinary SGLang build tools to be installed before the sealed attempt.

This preserves 008 unchanged, removes two false exact requirements, and adds no
provisioning framework, container contract, or manual GPU setup path.
