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

[G0's accepted successor decision is `PASS`](experiments/g0/RESULTS.md). The
historical stock pin lacked one atomic cache-level checked-demote contract;
G0-C-006 isolated that seam, and independently reviewed G0-C-017/001 proved
that the exact treatment package installs, fails closed through the registered
cache surface, and coexists with ordinary HiCache CUDA serving on the frozen
A10 environment. This is a narrow `experimentally validated` integration
finding; the overall ToolGap project remains `roadmap`.

The current rental execution bundle is
[G0-C-ATOMIC-017](experiments/g0/SPEC.g0-c-017.md). Frozen 016/002 completed
both stock and treatment health checks and requests, then exposed a cleanup
sampling race: the process group and attributable GPU PID disappeared before
the kernel removed the treatment listener entry. Successor 017 changes only
the existing 60-second cleanup convergence so process, port, and GPU evidence
must quiesce together. It retains the same provider image, source/model seeds,
SGLang commit/tree/patch, dependencies, controls, serving protocol, receipt
schema, and `roadmap` claim ceiling. Attempt 001 has now completed both arms,
the success seal, and off-host verification; this is an experimental serving-
integration result, not evidence of physical demotion or allocator recovery.
G0 PASS authorizes a separate G1 plan and frozen SPEC, not G1 execution.

Start with [docs/README.md](docs/README.md).

No physical-demotion implementation or performance result is claimed in this
directory.

The planned source ownership and Gate-conditional directory layout is recorded
in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#9-source-layout-and-gate-conditional-landing).
The structure markers under `src/`, `upstream/`, `tests/`, and `benchmarks/`
contain no runtime behavior; they make the future landing points explicit while
G1 execution remains unauthorized.

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
bash scripts/verify-g0-c-016-bundle.sh
bash scripts/verify-g0-c-017-bundle.sh
```
