# CUDA12-COMPAT-001 dependency-lock name normalization

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

`pip freeze` can preserve underscores from a wheel's distribution metadata.
Treating its textual left-hand side as a canonical package identifier creates a
false dependency-resolution failure. Validate locked package identities with
PEP 503-style normalization, while comparing the version string exactly.
