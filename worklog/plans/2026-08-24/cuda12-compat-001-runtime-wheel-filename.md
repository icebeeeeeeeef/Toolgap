# CUDA12-COMPAT-001 runtime wheel filename correction

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

## Observed evidence

The sealed attempt `cuda12-compat-001-20260824T1343Z` completed the CUDA
wheelhouse install but pip rejected the staged runtime artifact because its
filename did not satisfy the wheel filename grammar. Its internal METADATA and
WHEEL tag identify it as
`sglang-0.0.0.dev2+g734a8e921-cp312-cp312-linux_x86_64.whl`.

## Executable scope

The metadata-only CUDA12 rewrite preserves the pinned G0 payload's name,
version, and compatibility tag. Require its output filename to equal the
pinned G0 wheel filename in both the repackage tool and bundle builder.
Generate a successor input set with the same wheel bytes under that filename
and a provenance sidecar whose output filename is corrected accordingly.

All four retained sealed attempts remain `roadmap`/`N/A`; this changes no
runtime payload, dependency, model, host, or G1 scope.
