# G1-C-003 source-restore revision

Canonical owners: `experiments/g1/SPEC.md`, `docs/ROADMAP.md`, and the new
`experiments/g1/SPEC.g1-c-003.md`.

## Executable scope

`G1-C-001` sealed a `pre_execution` `INVALID` during source restoration when
the runner passed the literal malformed glob `000{1-3}-*.patch` to
`sha256sum`. `G1-C-002` sealed a separate `pre_execution` `INVALID` after all
three patches applied: it derived the changed-path inventory only from
`git diff --name-only`, which omits the new, untracked scripted G1 test module
until it is added to the index. Preserve both sealed attempts.

Freeze `G1-C-003` as a new formal runtime revision with the same mechanism,
host envelope, inputs, controls, and terminal oracle. Its sole repair computes
the exact pre-commit changed set as tracked diff paths plus safe untracked
regular files, so the expected scripted test module is checked before
`git add -A`.

## Boundaries

This repair does not reinterpret C-001/C-002, change the patches or runtime
inputs, add a G2/G3/public API/data-plane capability, or execute ECS/OSS
actions. C-003 has its own manifest, attempt identity, and external-anchor
namespace. Its clean-Git regression applies all three patches and asserts that
`test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py` appears in
the inventory before any index update or commit.
