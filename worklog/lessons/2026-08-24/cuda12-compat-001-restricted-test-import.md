# CUDA12-COMPAT-001 restricted test import

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

A test selector expressed as a top-level import path can be shadowed by an
installed package, even when the intended test file is present. For an
installed-wheel startup check, load the bound test file directly and avoid
adding the treatment source package directory to Python's import path.
