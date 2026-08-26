# G1-C-009 request admission race

Canonical owner: `experiments/g1/SPEC.g1-c-010.md`

G1-C-009 sealed `pre_execution INVALID` during the bypass arm. Its helper
submitted `/generate` with fire-and-forget `_submit_post` and immediately spent
a scheduler-step completion budget. In the preserved run, all 400 empty steps
elapsed before the background HTTP request reached the tokenizer receive
proxy; the assertion precedes the eventual HTTP 200 and no target prefill was
observed. G1-C-008 happened to win the same race, so its earlier bypass success
did not validate the helper's admission ordering.

The lesson is narrow: a scripted scheduler-step bound is meaningful only after
the request has crossed the runtime's existing tokenizer admission fence.
Increasing `_MAX_STEPS` would retain the race and is rejected. G1-C-010 uses
the pinned scripted runtime's exact-`rid` arrival wait before the unchanged
completion bound.
