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

The current pre-rental execution bundle is
[G0-C-ATOMIC-009](experiments/g0/SPEC.g0-c-009.md). It preserves the frozen,
never-executed [008 protocol](experiments/g0/SPEC.g0-c-008.md) while correcting
its non-causal host pins: the attempt reuses Alibaba Cloud's official Ubuntu
24.04 NVIDIA GPU image, seals its exact identity, and keeps exact source and
application dependencies. It does not change the current `roadmap` claim state
or the prior RESHAPE decision; a passing local bundle check authorizes only a
rented-host attempt.

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
```
