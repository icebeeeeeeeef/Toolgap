# Benchmark harness

> Status: `roadmap`; benchmark code is not authorized before G3.

When G3/G4 is opened, `toolgap_bench/` will own the reusable open-loop
workload runner, measured workload dimensions, and metric extraction. A Gate's
frozen commands, manifests, raw JSONL, and results remain under
`experiments/<gate>/`.

The harness must compare checked reclamation with the same committed-copy,
target-priority-release, and stock-eviction baseline. It must report physical
mediators and the joint resumed/foreground SLO, including losing regimes.
