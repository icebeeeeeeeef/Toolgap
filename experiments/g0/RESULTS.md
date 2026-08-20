# G0 Results — Fixed Source and Atomic Safe Seam

> Claim state: `roadmap`
>
> Last accepted Gate decision: `RESHAPE`
>
> Successor protocol: G0-C-017/001 `COMPLETED`; independent Gate review pending
>
> Source: SGLang `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`
>
> A paired stock/treatment GPU serving integration result now exists. No real
> physical demotion, allocator-reclamation, lifecycle, output-correctness, or
> performance result was produced.

## Decision

The last accepted G0 decision remains `RESHAPE` until an independent review
selects a successor Gate decision from the completed G0-C-017 evidence.

The fixed source already owns the physical tree, Host transfer completion,
device/Host values, live leaf predicate, `demote` primitive, free payload,
cache-side drain, allocator mutation, exact per-session frontier index, and Full
path coverage counts. Correctness needs neither a replacement backend nor a
second ownership system, so `STOP` is not supported.

Stock lacks one atomic vertical contract:

```text
validate exact current caller identity and Full-only scope
-> snapshot target frontiers before mutation
-> non-terminally release only the target session contribution
-> registered backend performs every final live check
-> same backend method invokes its existing demote primitive only if safe
-> cache observes every freed ID and always enters its unique drain path
-> return actual typed per-node and aggregate outcomes
```

The independently reviewed `G0-C-ATOMIC-006` source prototype proved that the
missing seam was narrow enough for `RESHAPE`. G0-C-017/001 now proves that its
fixed treatment wheel installs, preserves the fail-closed registered seam, and
coexists with ordinary HiCache GPU serving under the frozen protocol. That
completed protocol has not yet received the independent review required to
replace the accepted Gate decision, and it never invoked physical demotion.

## Fixed-source findings

| G0 question | Result |
|---|---|
| exact target mapping | existing per-component session frontier index plus Full path `session_ref`; `session_ids` is frontier-only |
| committed Host copy | write-through ack synchronization followed by both pending markers clear; `backuped`/Host value alone is insufficient |
| target-only priority release | component mutation exists, but public release is terminal close and stock has no generation-checked non-terminal composition |
| dynamic blockers | device locks, both pending IDs, resumable insert, eviction walk, live/device/leaf state, remaining coverage, and cascade scope; Host lock alone is not a blanket device blocker |
| physical invocation | maintained TreeCore interface and existing `demote`; stock lacks an atomic session-aware final-check wrapper |
| completion/free observation | `DemoteResult` carries device-index tensors/counts; cache owns observation and pop/drain |
| allocator-visible capacity | Full free action reaches the upstream allocator; no real before/after sample was taken |

The full mapping is in
[`artifacts/capability-matrix.md`](artifacts/capability-matrix.md).

## Host mode and stock reproduction

Exactly one mode was selected: `write_through`. It is the smallest source-
auditable branch with a published Host copy, authoritative D2H completion, and
a later settled duplicate.

`G0-C-ATOMIC-006` freezes the exact Qwen model/tokenizer revision, Ubuntu/A10/
CUDA target, dependency metadata, dtype, page/context/capacity flags, and launch
command. The unchanged stock preflight exited 78 before launch on the observed
macOS arm64 host because the frozen CUDA x86_64 environment and runtime are
absent. This is `blocked before execution`, neither smoke success nor failure of
the source-contract arm.

- [`commands/10-stock-hicache-smoke.sh`](commands/10-stock-hicache-smoke.sh)
- [`artifacts/g0-c-006-runtime-readbacks.txt`](artifacts/g0-c-006-runtime-readbacks.txt)

## Rental-host admission terminals

The provider host itself was admitted as Ubuntu 24.04 on one NVIDIA A10 with
the required CUDA 13.0 path and compatible driver. The rows below preserve
every rental-host terminal; none is silently upgraded into a Gate result.

| Revision and attempt | Terminal | Interpretation |
| --- | --- | --- |
| 009 / `g0-c-009-a10-attempt-001` | `BLOCKED_BEFORE_EXECUTION` before an arm because bare `nvcc` was discovered before the script established its canonical provider CUDA path | preserved, independently verifiable preflight counterexample; not a Gate result |
| 009 / `g0-c-009-a10-attempt-002` | fixed SGLang clone ended with a GitHub connection reset | preserved raw evidence exposed an invalid failure seal; D024 retains it but it cannot be treated as a verified terminal |
| 010 / `g0-c-010-a10-attempt-001` | `BLOCKED_BEFORE_EXECUTION` before an arm because GitHub HTTPS to the fixed SGLang remote could not connect | remote and off-host failure seals verified; not a Gate result |
| 010 / `g0-c-010-a10-attempt-002` | `BLOCKED_BEFORE_EXECUTION` before an arm after about 90 MB of the fixed SGLang Git pack was received and the connection reset with `early EOF` | remote and off-host failure seals verified; D025 replaces only live source transport in successor 011; not a Gate result |
| 011 / `g0-c-011-a10-attempt-001` | `BLOCKED_BEFORE_EXECUTION` because provider Rust 1.75 could not parse the pinned Edition 2024 workspace | remote and off-host failure seals verified; ordinary build-tool prerequisite, not a Gate result |
| 011 / `g0-c-011-a10-attempt-002` | `BLOCKED_BEFORE_EXECUTION` after the bounded stock wheel build spent 1,800 seconds obtaining the pinned Cargo graph | remote and off-host failure seals verified; exact Cargo cache was warmed outside any attempt without changing source or lock |
| 011 / `g0-c-011-a10-attempt-003` | `BLOCKED_BEFORE_EXECUTION` because Rust 1.85 supports Edition 2024 but not the pinned `let-chains` use | remote and off-host failure seals verified; not a Gate result |
| 011 / `g0-c-011-a10-attempt-004` | `BLOCKED_BEFORE_EXECUTION` because pinned `rustpython-ruff` packages declare `rustc >=1.92` | remote and off-host failure seals verified; established the fixed source's true minimum compiler |
| 011 / `g0-c-011-a10-attempt-005` | `BLOCKED_BEFORE_EXECUTION` after both wheels, same-lock isolated installs, and both CUDA self-checks succeeded; fixed Hugging Face snapshot failed with `Network is unreachable` | remote and off-host failure seals verified; D026 replaces only live model transport in successor 012; no arm started and no Gate result |
| 012 / `g0-c-012-a10-attempt-001` | `INVALID_SCOPE` in command 21 after admission and model/identity revalidation; stock produced the required 27/27 RED, but its expected exit 1 triggered the active `ERR` trap before status inspection | remote and off-host failure seals verified; D027 changes only expected-RED status capture in successor 013; no treatment control or arm started and no Gate result |
| 013 / `g0-c-013-a10-attempt-001` | `INVALID_SCOPE` in command 21 after admission, exact stock 27/27 RED, treatment 27/27 GREEN, and the installed seam; the full-tree AST inventory rejected a legal UTF-8 BOM in an unrelated upstream Python file | remote and off-host failure seals verified; D028 changes only the successor inventory decoder to `utf-8-sig`; no arm started and no Gate result |
| 014 / `g0-c-014-a10-attempt-001` | `EXECUTION_FAILED_AFTER_START` in command 22 after admission and all controls; stock loaded the fixed model and KV cache, then FlashInfer CUDA JIT failed before health because `ninja` was absent | remote and off-host failure seals verified; cleanup left no process-group or attributable GPU PID survivor; D029 adds only the ordinary project tool in successor 015; no request or treatment arm ran and no Gate result |
| 015 / `g0-c-015-a10-attempt-001` | `EXECUTION_FAILED_AFTER_START` in command 22 after stock passed FlashInfer JIT, health, and both frozen streaming requests; runner-issued SIGTERM led fixed SGLang to self-kill with 137, and the active `ERR` trap intercepted `wait` before cleanup receipt creation | both request JSON files say `passed: true`; remote and off-host failure seals verify; no process-group, listener, or attributable GPU PID survived; D030 changes only attributed shutdown capture in successor 016; treatment did not run and no Gate result was produced |
| 016 / `g0-c-016-a10-attempt-001` | `EXECUTION_FAILED_AFTER_START` after stock completed health, both requests, and attributed cleanup; the operator requested a network pause while treatment was starting | remote and off-host failure seals verify; no process, listener, or GPU PID survived; the interruption is not a Gate result |
| 016 / `g0-c-016-a10-attempt-002` | `EXECUTION_FAILED_AFTER_START` after both arms completed health and both requests; treatment process-group and GPU evidence quiesced, but its unowned listener entry remained in the immediate cleanup snapshot | remote and off-host failure seals verify; a later residual probe found no process, listener, or GPU PID; D031 keeps the same deadline and waits for joint cleanup quiescence in successor 017; not a Gate result |
| 017 / `g0-c-017-a10-attempt-001` | `COMPLETED`: admission, 27/27 stock RED, 27/27 treatment GREEN, installed fail-closed seam, static inventory, both arms' health and two streaming requests, joint cleanup, final evidence verification, and completion seal passed | remote and off-host seals verify; all four requests returned HTTP 200, each second request reported 48 cached tokens, both cleanups reaped attributed status 137 with no process-group/listener/GPU survivor; independent Gate review remains pending |

The authoritative raw attempt directories remain Git-ignored. The observed
source-network failures do not authorize an alternate SGLang mirror, source
pin, dependency, or model under the frozen protocols. D025 authorizes one
SHA-256-bound operator-staged Git seed in successor 011 while retaining the
same canonical remote, commit, tree, and patch identity.

The 011 sequence also proved that incidental model transport can remain after
source transport is removed. D026 authorizes one exact-file, SHA-256-bound
model seed in successor 012, retaining the same model repository/revision and
requiring per-file verification before every phase and serving arm.

The first 012 attempt proved the offline input path and full admission, then
exposed a Bash control-runner defect rather than a contract failure. D027
authorizes only conditional capture of the preregistered stock RED in successor
013; every oracle assertion and later phase remains unchanged.

The first 013 attempt then proved both source oracles and the installed seam,
but exposed a Python-source decoding defect in the full-tree inventory before
either server started. D028 preserves it and authorizes only a BOM-safe frozen
inventory in successor 014; all call-site assertions and later phases remain
unchanged.

The first 014 attempt completed admission and all controls, then proved that
the stock package could load the fixed model and allocate the fixed KV cache.
FlashInfer's first CUDA JIT exposed the missing ordinary `ninja` tool before
health. D029 preserves the failure and authorizes only installation, admission,
and version readback of Ubuntu `ninja-build` in successor 015.

The first 015 attempt then proved stock JIT, health, and both native streaming
requests. Its intentional shutdown exposed the same Bash `ERR`-trap pattern at
`wait`; cleanup itself left no survivor. D030 preserves the attempt and
authorizes only conditional wait-status capture plus live-PID/TERM attribution
in successor 016.

The first 016 attempt was deliberately interrupted and sealed without residue.
The second completed health and both requests in both arms. Its treatment
cleanup showed the process group and attributable GPU PID gone while the
kernel still exposed the target listener for one immediate snapshot; a later
probe found it gone. D031 preserves both attempts and authorizes only waiting
for all three cleanup observations to quiesce within the unchanged deadline in
successor 017.

G0-C-017/001 then completed the full preregistered protocol on the admitted
Alibaba Cloud A10 host. Stock and treatment used separate wheels and isolated
environments resolved from one dependency lock. Each arm returned HTTP 200 for
both native streaming requests; the second request in each arm reported 48
device-cached tokens. Both runner-issued shutdowns reaped with attributed status
137 and retained empty process-group, target-listener, and attributable-GPU
survivor evidence. The completion receipt remains `roadmap` and explicitly
records that independent review is pending.

## Decisive atomic seam evidence

[`SPEC.g0-c-006.md`](SPEC.g0-c-006.md), its preregistration manifest/receipt,
both inherited executable dependency hashes, and the exact treatment patch were
sealed before the v6 oracle existed.

| Phase | Checkout | Result |
|---|---|---|
| stock RED | untouched exact pin | exit 1; 27/27 failed because the atomic surfaces were absent |
| patched GREEN | separate exact-pin worktree | exit 0; 27/27 passed |
| independent rerun | both arms | reproduced 27 RED / 27 GREEN; final `PASS` for the frozen oracle |

The retained four-file, 216-insertion source prototype exposes one cache caller
surface. Its tracker sub-step preserves exact target/generation identity and
non-target coverage. The maintained interface gives legacy backends a concrete
zero-side-effect fail-closed default. The Python backend combines final checks
and its existing `demote` call in one synchronous method. The cache uses actual
typed outcomes, preserves NodeId and every freed ID, and enters cleanup even if
observation fails. It adds no physical algorithm, allocator, movement path,
worker, second index, public pause API, or candidate lifecycle executor.

The oracle loads the actual interface and registry with dependency stubs,
executes actual cache outcome definitions and extracted patched methods, and
uses registered fake backends/resources. The real upstream physical `demote`
implementation is neither imported nor invoked.

Evidence:

- [`artifacts/test_atomic_checked_demote_contract_v6.py`](artifacts/test_atomic_checked_demote_contract_v6.py)
- [`artifacts/sglang-session-atomic-checked-demote-v5.patch`](artifacts/sglang-session-atomic-checked-demote-v5.patch)
- [`artifacts/g0-c-006-red.txt`](artifacts/g0-c-006-red.txt)
- [`artifacts/g0-c-006-green.txt`](artifacts/g0-c-006-green.txt)
- [`artifacts/g0-c-006-patched-identity.txt`](artifacts/g0-c-006-patched-identity.txt)
- [`artifacts/g0-c-006-registration.json`](artifacts/g0-c-006-registration.json)
- [`artifacts/independent-review.md`](artifacts/independent-review.md)

## Aggregate and release semantics

For a valid Full-only current generation, target priority release remains
applied even when zero fake demotions complete. It removes only the target
session contribution; shared non-target frontier and coverage state remain.

- all requested fake completions: `ACCEPTED`;
- any completed safe subset: `CLIPPED`, independent of frontier order;
- zero completed with transient blockers only: `DEFERRED`;
- stale/unsupported/empty, or zero completed with any permanent reject:
  `REJECTED`.

The 27-case matrix distinguishes caller identity, target/non-target release,
write/load pending, missing Host copy, device versus Host locks, shared coverage,
structural owners, D-leaf mutation/retry, auxiliary cascade, all mixed orders,
legacy vertical behavior, exact NodeIds/freed IDs, and cleanup failure modes:
[`artifacts/counterexample-matrix.md`](artifacts/counterexample-matrix.md).

## Invalid attempts retained

| Revision | Status | Why invalid |
|---|---|---|
| 001 | executed | tracker-only and missing exact successor runtime fields |
| 002 | executed | eligible NodeIds escaped before physical call; interface and aggregates incomplete |
| 003 | executed | independent review found eight oracle/contract blockers |
| 004 | registered, never executed | actual cache outcome definitions omitted from frozen oracle |
| 005 | executed | independent review found seven additional identity/order/attribution blockers |

Their frozen SPECs, manifests, tests/patches where created, and outputs remain
retained. Every invalid manifest records `N/A` Gate decision.

## Limits

Still unproven:

- upstream acceptance and real-environment import/build compatibility;
- real registered Python backend behavior under CUDA;
- physical demotion, allocator-visible headroom, and output equality;
- resume, cancel, retry, stale completion, fallback, and production failure
  orchestration;
- any latency, throughput, capacity, or GPU-memory result.

The proposed interface and G1 deletion test remain design artifacts:

- [`artifacts/checked-demote-interface.md`](artifacts/checked-demote-interface.md)
- [`artifacts/g1-removal-test.md`](artifacts/g1-removal-test.md)
- [`artifacts/session-to-leaf.md`](artifacts/session-to-leaf.md)
- [`artifacts/priority-release.md`](artifacts/priority-release.md)

## Only legal next action

G1 remains blocked. The only legal next action is upstream review/integration of
the atomic vertical contract, selection of the resulting exact source pin,
provisioning of the frozen CUDA-capable dependency environment, and a new G0
run. Only that new frozen run may authorize a G1 real physical mechanism test.
