# CUDA12-COMPAT-001 restricted test import correction

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

The valid r6 attempt `cuda12-compat-001-20260824T1524Z` passed the Torch CUDA
and standalone CUDA 12.8 compiler probes, but its restricted startup stopped
before SGLang initialization: `python -m unittest` could not resolve the
top-level `test.registered` selector. The patched test file exists in the
treatment tree. The host Python path excludes the treatment root and an
installed dependency occupies the top-level `test` name.

Load only the hash-bound test file via `importlib.util.spec_from_file_location`,
register it under a private module name, and run only the selector's class and
method through `unittest`. Do not add `TREATMENT/python` to `PYTHONPATH`: that
would blur the installed-wheel provenance boundary. The r6 result remains a
valid startup-import failure; a corrected attempt requires a new frozen seed,
receipt, and attempt ID.
