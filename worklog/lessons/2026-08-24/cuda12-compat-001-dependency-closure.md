# CUDA12-COMPAT-001 dependency closure

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

The initial frozen resolver assumed every ordinary requirement had a binary
distribution on the G0-proven internal mirror. G0-C-011 attempt 005 proves the
contrary: `cuda-tile==1.6.0rc5` was built from source on the CUDA 13 host.
CUDA12-COMPAT-001 must not repeat that build on ECS. The no-action probe now
installs its fixed cu12 FlashInfer wheel without dependency resolution, records
`cuda-tile` as deliberately uninstalled, and excludes any path that imports it
from its success scope.
