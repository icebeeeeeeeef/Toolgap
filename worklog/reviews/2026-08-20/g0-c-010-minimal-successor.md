# G0-C-010 minimal-successor review

Canonical owners: `experiments/g0/SPEC.g0-c-010.md` and D024 in
`docs/DECISIONS.md`.

The credible alternative was to add a clone retry layer, a mirror, a container,
or broader provider handling. It is rejected: none repairs an index that can
self-mutate after sealing. The necessary vertical slice is exactly canonical
path setup plus silent failure finalization, with a redirected-log regression
test. All runtime, ownership, and serving semantics remain unchanged.
