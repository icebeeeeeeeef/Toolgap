# CUDA12-COMPAT-001 runtime wheel install-path correction

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

## Observed evidence

The sealed attempt `cuda12-compat-001-20260824T1334Z` restored all inputs,
installed the local CUDA wheelhouse and its ordinary dependencies, then failed
when pip parsed the immutable evidence copy named `runtime-wheel.whl`. That
stable artifact name is not a valid wheel distribution filename, although its
SHA-256 matches the input manifest.

## Executable scope

Keep `runtime-wheel.whl` as the sealed evidence copy required by the finalizer.
Use the original staged runtime wheel pathname, which is already bound by the
manifest and receipt and has a valid distribution filename, for pip install,
metadata dependency extraction, and the generated runtime environment.

This correction changes neither resolved CUDA dependencies nor the allowed
test. The sealed resolver failure is retained; a replacement execution must
use a new commit, source seed, manifest, OSS prefix, and receipt.
