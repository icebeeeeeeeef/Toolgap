# CUDA12-COMPAT-001 evidence copy filename

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

The runner deliberately copies the staged runtime wheel and provenance into a
sealed attempt as `runtime-wheel.whl` and `runtime-wheel-provenance.json`.
Those names are evidence artifact names, not input-manifest filenames. The
first actual restricted attempt compared the copied filename to the manifest's
original filename and sealed `BLOCKED_HOST_IDENTITY` before dependency setup.

Validate the original staged inputs, then keep the identical copies for
installation and evidence. The retained attempt does not establish a CUDA or
G1 result.
