# G1-C-010 control admission review

Canonical owner: `experiments/g1/SPEC.g1-c-010.md`

Review rejected the first C-010 candidate because the stale-generation arm
still submitted `/close_session` with fire-and-forget `_submit_post`. Its
generation-release budget could therefore expire before the control request
reached the tokenizer receive proxy, reproducing the same ordering defect as
the C-009 ordinary request path.

C-010 now uses the pinned arrival helper for both paths. The close predicate
requires a `CloseSessionReqInput` with the exact `session_id`; only then does
the unchanged 400-step release wait begin. Increasing the bound or accepting a
same-prefix or wrong-type message remains rejected.
