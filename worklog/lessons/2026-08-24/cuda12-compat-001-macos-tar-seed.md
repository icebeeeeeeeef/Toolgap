# CUDA12-COMPAT-001 macOS seed archive correction

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

Observed: a locally generated ToolGap bare-seed archive contained macOS
AppleDouble member `._toolgap-source.git`. The bootstrap safety check rejected
it before extraction, so the already uploaded `142a8f2/inputs` set is invalid
for execution and is retained only as a failed staging record.

Correction: use `COPYFILE_DISABLE=1` while creating the new seed archive and
make `cuda12_compat_001_bundle_manifest.py` reject unsafe ToolGap seed members
before it can create an input manifest. The replacement input set must use a
new OSS prefix and receipt.
