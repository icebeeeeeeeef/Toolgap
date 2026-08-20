# ToolGap

> Status: `roadmap`

ToolGap is an independent repository for a narrow SGLang HiCache lifecycle
project. Its D0 documentation contract is accepted; historical Agentic-KV
materials were not migrated as evidence for this project.

The current candidate project is:

> **Safe Session Demotion Executor for SGLang HiCache**

The project asks whether a session-scoped, checked demotion executor can safely
turn committed Host-tier KV copies into earlier allocator-visible GPU headroom,
and whether that mechanism beats the same committed-copy path with only a
generation-preserving target session-priority release and stock eviction under
a joint serving SLO.

[Gate G0 ended at `RESHAPE`](experiments/g0/RESULTS.md): the fixed stock pin
lacks one atomic cache-level checked-demote contract that composes generation-
preserving frontier release with backend-owned final checks, the existing
physical primitive, and cache-owned drain. G1 remains blocked until that
contract is accepted in a new exact pin and G0 is rerun on the frozen CUDA-
capable environment.

The current rental execution bundle is
[G0-C-ATOMIC-015](experiments/g0/SPEC.g0-c-015.md). It preserves frozen 014/001,
which completed admission and all controls, then loaded the fixed model/KV
cache before FlashInfer's first CUDA JIT failed because the ordinary `ninja`
tool was absent; no request or treatment arm ran. Successor 015 adds only
Ubuntu `ninja-build` to project prerequisites and admits/version-records it; it
retains the same provider GPU image, source/model seeds, SGLang
commit/tree/patch, dependencies, controls, serving protocol, and `roadmap`
claim ceiling.

Start with [docs/README.md](docs/README.md).

No runtime implementation or performance result is claimed in this directory.

The planned source ownership and Gate-conditional directory layout is recorded
in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#9-source-layout-and-gate-conditional-landing).
The structure markers under `src/`, `upstream/`, `tests/`, and `benchmarks/`
contain no runtime behavior; they make the future landing points explicit while
G1 remains blocked.

Local implementation plans, decision-changing reviews, and reusable lessons
are maintained in [worklog/](worklog/README.md). It is historical context, not
a second roadmap or a source of current technical facts.

## Repository checks

The historical G0 command artifacts retain their original paths and hashes.
Run the root-native verifier below after changing the evidence bundle; it checks
the migrated bundle without changing the frozen historical command files.

Some frozen manifests also retain the original `toolgap-kv/toolgap` repository-
relative paths and original candidate checkout path as execution provenance. In
this standalone repository, the referenced files live at the same path after
removing the leading `toolgap/`; those recorded values are not active runtime
dependencies and are intentionally not rewritten.

```bash
bash scripts/verify-g0-evidence.sh
bash scripts/verify-g0-c-007-bundle.sh
bash scripts/verify-g0-c-008-bundle.sh
bash scripts/verify-g0-c-009-bundle.sh
bash scripts/verify-g0-c-010-bundle.sh
bash scripts/verify-g0-c-011-bundle.sh
bash scripts/verify-g0-c-012-bundle.sh
bash scripts/verify-g0-c-013-bundle.sh
bash scripts/verify-g0-c-014-bundle.sh
bash scripts/verify-g0-c-015-bundle.sh
```
