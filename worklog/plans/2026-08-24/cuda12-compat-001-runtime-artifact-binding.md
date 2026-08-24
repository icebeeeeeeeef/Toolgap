# CUDA12-COMPAT-001 runtime artifact binding correction

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

## Observed evidence

The sealed attempt `cuda12-compat-001-20260824T1326Z` passed host identity,
input-manifest verification, receipt verification, and immutable evidence
copying. Its runtime metadata validator then rejected `runtime-wheel.whl`
because it compared the evidence-copy filename against the source archive's
manifest filename. The copied bytes, size, and SHA-256 match the manifest; the
failure is only the inconsistent filename check.

## Executable scope

Validate runtime wheel and provenance against their original staged paths,
whose filenames, receipts, sizes, and SHA-256 values are already bound. Keep
the immutable run-directory copies as the later installation and evidence
inputs. Add a static assertion for that source-path validation.

The sealed attempt is retained. This correction changes no host, dependency,
model, lifecycle, or Gate scope and requires a new commit, source seed, input
manifest, OSS prefix, and receipt before rerunning.
