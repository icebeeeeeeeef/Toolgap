# CUDA12-COMPAT-001 structured package inventory

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

`pip freeze` is a provenance lock, not always a normalized installed-package
inventory. Local direct references omit the separate equality form, so exact
identity checks must consume a structured package inventory while preserving
the freeze output for auditability.
