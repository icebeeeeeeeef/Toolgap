# G0 independent counterexample review

> Claim state: `roadmap`
>
> Final reviewed revision: `G0-C-ATOMIC-006`
>
> Final disposition: `PASS` for the frozen source-seam oracle; no remaining
> Gate-blocking counterexample found

## Review method

An independent reviewer read the fixed-pin source mappings, every frozen
successor SPEC, retained test and patch, and the counterexample matrix. For each
candidate revision it attempted to construct a wrong implementation that would
still pass the registered oracle. It independently reran stock and patched arms,
checked source/patch/oracle identities, compared the retained patch byte-for-byte
with the patched worktree diff, and ran `git apply --check` against stock.

## Invalid revisions retained

| Revision | Execution | Independent disposition | Why it is not Gate evidence |
|---|---|---|---|
| `G0-C-SEAM-001` | stock 5 RED; patch 5 GREEN | invalid | tracker-only proof omitted exact successor runtime fields and the maintained backend boundary |
| `G0-C-ADMISSION-002` | stock 14 RED; patch 14 GREEN | `NEEDS_FIX` | eligible NodeIds escaped before later demote; interface/registry and aggregate semantics were not proven |
| `G0-C-ATOMIC-003` | stock 16 RED; patch 16 GREEN | `NEEDS_FIX` | eight credible wrong implementations escaped despite GREEN |
| `G0-C-ATOMIC-004` | not executed | invalid before execution | frozen oracle omitted actual cache outcome definitions |
| `G0-C-ATOMIC-005` | stock 22 RED; patch 22 GREEN | `NEEDS_FIX` | seven additional identity/order/attribution counterexamples escaped |

The 003 review found missing observation of current/stale tracker side effects,
mixed aggregate priority, incorrect permanent treatment of a recoverable
not-current-D-leaf, unobserved structural and legacy physical side effects,
cleanup skipped by observation failure, and surrogate rather than actual cache
outcome types. Revision 005 closed all eight.

The 005 review then found missing target-only multi-session preservation, cache
caller identity forwarding, permanent-first traversal, the Host-lock negative
constraint, per-node NodeId attribution, legacy vertical one-way release,
multi-index freed-ID copying, and an initially unindexed inherited executable
dependency. Revision 006 froze both dependency hashes and distinguished all
seven wrong implementations without expanding the source patch.

## Final 006 review

Fresh reviewer execution:

| Check | Result |
|---|---|
| stock v6 oracle | exit 1; 27/27 expected failures caused by absent atomic surface |
| patched v6 oracle | exit 0; 27/27 pass |
| commit/tree/`pyproject.toml` | match frozen values |
| v3/v5/v6 oracle hashes | match manifest and registration evidence |
| treatment patch hash/size | match frozen values |
| patched four-file diff | byte-identical to retained patch |
| `git apply --check` on stock | pass |
| patched `git diff --check` | pass |

The reviewer separately confirmed executable discrimination for:

- target-only release with a non-target session sharing path coverage;
- exact non-default caller session/generation identity;
- transient-first and permanent-first mixed frontier traversal;
- Host-lock-only non-blocking versus device-lock blocking;
- exact per-node NodeId attribution;
- registered legacy backend release-before-reject with zero physical calls;
- every freed ID from a multi-index returned value;
- all earlier pending/Host/coverage/structural/D-leaf/cleanup branches.

Final reviewer statement: `PASS`; no remaining Gate-blocking counterexample.

## Evidence boundary

This review admits only the frozen fixed-source, extracted-method,
registered-fake-backend seam contract. The oracle never imports or invokes the
real upstream physical `demote` implementation. It proves no real SGLang
import/build, CUDA behavior, allocator-visible reclamation, lifecycle/recovery
correctness, output equivalence, or performance result.
