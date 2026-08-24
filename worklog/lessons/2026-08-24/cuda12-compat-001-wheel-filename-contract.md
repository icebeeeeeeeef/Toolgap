# CUDA12-COMPAT-001 wheel filename contract

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

Wheel contents alone are insufficient for pip installation: PEP 427 filename
fields are part of the installer contract. A metadata-only repackaging must
preserve the original distribution filename when it preserves the package
name, version, Python ABI, and platform tag. The bundle builder and repackager
now reject a renamed runtime wheel before it can be staged.
