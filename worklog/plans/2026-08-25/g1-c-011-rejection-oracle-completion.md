# G1-C-011 rejection-oracle completion

Canonical owner: `experiments/g1/SPEC.g1-c-011.md`

## Trigger

The final independent matrix review found that sealed G1-C-010 evidence is
internally complete but its seven-arm oracle does not discriminate removal of
the `LOAD_BACK_PENDING` or settled Host-copy guards required by
`experiments/g1/SPEC.md`. G1-C-010 remains immutable and externally anchored;
its Gate `PASS` is not accepted.

## Executable scope

- Create a new G1-C-011 frozen runtime revision from G1-C-010.
- Preserve the mechanism, source/model/runtime/CUDA inputs, enabled arm, bypass
  arm, existing rejection arms, stock control, admission fence, cleanup, and
  evidence format.
- Add one real-runtime `reject_load_back_pending` arm using the existing pinned
  H-to-D fixture and require `LOAD_BACK_PENDING`, no physical demote/drain,
  unchanged device IDs and allocator capacity.
- Add one real-runtime `reject_host_copy_not_committed` arm that reaches the
  settled Host-copy guard with pending work clear and require
  `HOST_COPY_NOT_COMMITTED`, no physical demote/drain, unchanged device IDs and
  allocator capacity.
- Add counterexample tests proving each arm fails if its corresponding guard or
  reason is removed from the frozen patch.
- Run the full local bundle verifier and obtain independent code and matrix
  review before any GPU execution.
- After separate authorization for the exact remote temporary directory,
  reclaim only the superseded `work/` tree, stage C-011, run once, seal, copy
  evidence off host, replay the finalizer, anchor exact OSS versions, and obtain
  a final release-readiness review.

## Boundaries

- Do not modify or restage `docs/DECISIONS.md` or `CONTEXT.md`.
- Do not rewrite any C-010 raw evidence or its OSS anchor.
- Do not change the checked-demote mechanism, dependencies, model, CUDA host,
  or project claim state.
- Do not delete any remote path without an explicit authorization naming that
  path.
