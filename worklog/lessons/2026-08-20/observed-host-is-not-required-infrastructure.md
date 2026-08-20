# An observed host is not a required infrastructure contract

Canonical correction: `docs/DECISIONS.md` D023 and
`docs/governance/EXPERIMENT_AND_EVIDENCE_SOP.md` section 2.1.

## Trigger

G0-C-008 required driver `580.65.06` and Python `3.12.11` exactly. The Alibaba
Cloud purchase flow exposed a supported Ubuntu 24.04 GPU image with a newer
CUDA-13-compatible driver and Python 3.12.3.

## Incorrect assumption

Values observed or planned on one preparation host were treated as experiment
requirements without showing that the decision question, upstream interface,
or a known defect depended on those exact patches.

## Evidence and correction

NVIDIA defines `580.65.06` as the CUDA 13.0 minimum Linux driver, while the
pinned SGLang source accepts Python `>=3.10`. G0 now freezes the causal hardware
and exact application stack, admits compatible driver/Python envelopes, and
seals the provider's exact observed substrate identity.

## Future rule

For every infrastructure pin, state whether it is causal, a compatibility
boundary, or a pairing/reproducibility constraint. If none applies, record the
exact value but specify a capability envelope. Prefer provider-supported
substrate over manual host mutation, and require a new SPEC before taking over
driver or accelerator-runtime installation.
