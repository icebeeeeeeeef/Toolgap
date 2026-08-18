# G0 preflight admission record

Captured: `2026-08-17T15:01:06Z`

## Repository state before G0

- Candidate repository: `/Users/bytedance/toolgap-kv`
- Branch: `codex/ai-infra-interview-map`
- HEAD observed before G0: `db0b4fa`
- The worktree already contained unrelated modified and untracked files.
- The entire `toolgap/` directory was already untracked.
- G0 work is therefore confined to `toolgap/experiments/g0/`, except for a
  future minimal `toolgap/docs/DECISIONS.md` update only if evidence changes a
  major accepted choice.
- No pre-existing file is reverted, cleaned, staged, or overwritten outside
  the G0 artifact directory.

## Draft fields and admission resolution

| Previously open field | Admission value |
|---|---|
| Adopted SGLang commit | `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2` |
| Local checkout identity | `/private/tmp/toolgap-kv-g0-sglang-92b1d382`, detached clean sparse checkout; tree `25e9bf86d04c27fe380024d9c8c421c3b5b51f3c` |
| Local patch/worktree identity | No upstream patch; candidate HEAD `db0b4fa`; dirty state pre-existed G0 |
| Selected Host write mode | `N/A: source-only; selection is a G0-B output` |
| Model/revision | `N/A: source-only` |
| Dtype/page size/context/cache flags/memory fraction | `N/A: source-only; a G0-C revision must freeze them` |
| Dependency/runtime identity | `N/A: source-only; source is not imported or executed` |
| Source command paths | `commands/00-acquire-source.sh`, `01-source-identity.sh`, `02-source-audit.sh` |
| Runtime command paths | `N/A: G0-C is not authorized by this revision` |
| Matrix and evidence paths | Fixed in `SPEC.md` section 6 |
| Manifest path | `toolgap/experiments/g0/manifest.json` |
| SPEC checksum procedure | `shasum -a 256 toolgap/experiments/g0/SPEC.md`; digest recorded before decisive audit |

## Source availability

The sandboxed network check failed with `Could not resolve host: github.com`.
An approved official-repository clone then succeeded. The exact commit exists,
its commit object and tree were resolved locally, and the sparse checkout was
detached at that commit. Source acquisition is therefore admitted; the initial
sandbox network failure is retained as a preflight fact, not a G0 mechanism
result.

## Admission decision

`ADMIT SOURCE-ONLY G0-A/G0-B AFTER SPEC CHECKSUM IS RECORDED.`

No source-semantic conclusion, runtime attempt, prototype, or Gate decision was
made during preflight.
