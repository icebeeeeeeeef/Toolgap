# Candidate session-demotion module

> Status: `roadmap`; no runtime implementation is authorized yet.

This directory is the reserved home for candidate-owned lifecycle behavior
after G0 proves a maintainable invocation seam. It must not become a second KV
data plane or a replacement SGLang cache backend.

Expected implementation slices:

- G1: identity/value types, the forced mechanism executor, the fixed-pin
  adapter, DecisionTrace fields, and real physical/bypass tests;
- G2: resume, cancellation, stale-completion fencing, fallback, and cleanup
  ownership;
- G5 only: a policy module, if independent evidence admits dynamic selection.

Until then this README is a structure marker, not a claim that any runtime
class or public pause API exists.
