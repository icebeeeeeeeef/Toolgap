# G0-C-012 offline model seed

Canonical owner: `experiments/g0/SPEC.g0-c-012.md` and
`experiments/g0/RESULTS.md`.

## Executable scope

- Preserve frozen G0-C-011 and attempts 001-005 unchanged.
- Add one successor revision that replaces the live Hugging Face snapshot
  download with one operator-staged, SHA-256-bound model archive.
- Retain the exact model repository and revision, SGLang source seed, base
  commit/tree, patch, dependency resolution, host admission, controls, serving
  protocol, evidence seal, and claim ceiling.
- Verify the archive SHA-256, safe extraction, exact file inventory, and every
  model file digest before admission and again before every later phase.
- Force tokenizer and server model loading into offline mode and point both
  arms at the same verified local snapshot.
- Execute one unused attempt through final verification, copy its complete
  sealed evidence off host, and independently review the Gate decision.

## Non-goals

- No proxy, mirror service, object-store dependency, retry subsystem, model
  conversion, dependency/source change, driver/CUDA change, G1 execution, or
  mutation of prior evidence.
