# G0-C-012 model transport review

Canonical owner: `docs/DECISIONS.md` D026 and
`experiments/g0/SPEC.g0-c-012.md`.

The strongest case for retaining `snapshot_download` was simplicity and direct
provenance from the canonical repository. G0-C-011 attempt 005 nevertheless
proved that both wheels, both dependency-identical environments, and CUDA
self-checks could succeed while the experiment still stopped at a TCP route
failure to Hugging Face. A proxy or mirror would add infrastructure unrelated
to the G0 question.

The accepted minimum is one operator-staged archive bound by a frozen SHA-256
and an exact per-file inventory for the same repository revision. The runner
extracts it without links or path escapes, rehashes every file before each
phase, and forces local-only loading. No scientific input or Gate claim changes.
