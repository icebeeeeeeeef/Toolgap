# G0 counterexample matrix

Target: fixed-pin SGLang session-scoped atomic checked-demote seam.

Confidence ceiling: `G0-C-ATOMIC-006` executes extracted patched methods and
the actual cache outcome definitions with fake KV resources through the actual
fixed-pin TreeCore interface and registry. It neither imports nor invokes real
upstream physical demotion and proves no engine, CUDA, allocator, lifecycle,
output-correctness, or performance behavior.

| Obligation | Credible wrong implementation | Distinguishing 006 oracle | Current evidence | Remaining later-Gate evidence |
|---|---|---|---|---|
| One maintained atomic contract | Return eligible NodeIds, then call `demote` later | Cache calls `demote_session_checked`; Python backend does final checks and its existing `demote` in the same synchronous method | Stock 27-case RED; overriding fake built through actual registry | Real engine executes an accepted patch on a new exact pin |
| Legacy fail-closed compatibility | Default calls physical `demote`, or cache rejects it before release | Recording/raising legacy `demote`; direct default has no result/calls; vertical current request releases once then returns `REJECTED/UNSUPPORTED_BACKEND` | direct and vertical legacy tests GREEN | Each production external backend opts in explicitly |
| Actual caller outcome types | Correct surrogate hides wrong real field order | Execute actual outcome class AST; bind it to cache method; assert typed fields; patch uses keyword construction | actual-outcome test GREEN | Real import/build on accepted pin |
| Current target release | Clear every session after releasing target | Actual tracker releases a once, preserves b frontier and shared coverage, preserves both generations, and omits tombstones | multi-session actual tracker test GREEN | Real Full path counter fixture in G1/G2 |
| Stale generation | Ignore generation and release by session ID | Actual tracker stale call returns `None`, makes zero release calls, and preserves frontier | actual tracker test GREEN | Full stale-completion fencing is G2 |
| Vertical caller identity | Ignore caller and hard-code session-a/generation 3 | Non-default session/generation/NodeId must reach tracker and every typed result field exactly | vertical identity test GREEN | Full operation/pause identity is G2 |
| Mutation after snapshot | Check once before returning NodeId | Release hook adds device child; backend returns `DEFERRED`, no demote; child clearance lets same NodeId intent complete | mutation/retry test GREEN | Real scheduler fixture confirms synchronous backend section |
| Completed write-through | Treat `backuped` or Host value as commitment | Write pending returns `WRITE_THROUGH_PENDING`; no fake demote | partial/all-pending tests GREEN | Real D2H ack fixture |
| Independent load-back exclusion | Fold load into write or ignore it | Load-only reports `LOAD_BACK_PENDING`; mixed case retains both reasons | load-only and all-pending tests GREEN | Real H2D ack fixture |
| Host materialization exists | Treat clear pending IDs as sufficient | `host_value=None` returns `HOST_COPY_NOT_COMMITTED`; no demote | missing-host test GREEN | Real settled-host readback |
| Protect non-target coverage | Use frontier-only `session_ids` as full coverage | Remaining Full `session_ref > 0` defers; no second index | coverage test GREEN plus fixed-source mapping | Two real sessions sharing a prefix |
| Device lock exclusion | Check only Full lock | Non-Full device component lock returns `DEVICE_LOCKED`; no demote | device-lock test GREEN | Real component fixture if scope broadens |
| Host lock separation | Treat any Host lock as a device blocker | Host-lock-only with zero device locks completes | host-lock negative test GREEN plus fixed-source mapping | Real Host eviction interleaving later |
| Structural owners | Report blocker after still demoting | Insert and eviction cases assert `DEFERRED`, no result, and unchanged recording demote count | structural test GREEN | Real scheduler interleaving |
| Full-only cascade | Ignore SWA/Mamba cascade | Auxiliary scope rejects before tracker release | auxiliary test GREEN plus source cascade mapping | Any broadened component set requires a new Gate |
| Live NodeId/device value | Test only child mutation | Dead NodeId and absent device value are distinct permanent rejects | dead/device-absent tests GREEN | Real arena/eviction fixture |
| Aggregate all-safe | Report eligibility as physical acceptance | Two fake demotes return, actual typed IDs copied, all resources drained before `ACCEPTED` | all-safe test GREEN | Real physical action and allocator observation in G1 |
| Aggregate mixed completed/rejected | Let any reject override a completion | safe+dead is `CLIPPED`, with safe demoted | safe-plus-dead test GREEN | Real partial execution/trace |
| Aggregate order independence | Stop after first transient or permanent blocker | pending-first+safe-second and dead-first+safe-second both demote safe and return `CLIPPED` | both reversed-order tests GREEN | Real multi-frontier trace |
| Exact target attribution | Fill every node result with a constant NodeId | Accepted, mixed, dead, identity, and legacy cases assert requested NodeId sequences | strengthened attribution tests GREEN | DecisionTrace operation identity later |
| Aggregate zero transient/permanent | Let transient override permanent | pending+dead with zero completed is `REJECTED` | pending-plus-dead test GREEN | Real fallback/DecisionTrace later |
| Aggregate zero transient | Roll back release or hide retry | all write/load pending is `DEFERRED`, release persists, no worker exists | all-pending test GREEN | Bounded retry ownership belongs to G2 |
| Empty target | Treat empty as successful no-op | valid current release persists and aggregate is `REJECTED/EMPTY_TARGET_FRONTIER` | empty test GREEN | Real fallback trace later |
| Cleanup success | Return raw `DemoteResult` | Cache copies IDs and drains device/Host resources exactly once before terminal success | all-safe ownership assertions GREEN | Real upstream allocator action in G1 |
| Exact freed-ID observation | Copy only the first index from each tensor/value | One fake value returns `(70,71,72)` and the typed outcome retains all three before one drain | multi-index observation test GREEN | Real tensor result in G1 |
| Observation failure cleanup | Read IDs before entering cleanup | `.tolist()` throws; both device and Host cleanup still occur exactly once; no terminal result | observation-failure test GREEN | Real tensor/synchronization fault injection later |
| Drain failure cleanup | Emit success after device drain throws | Device failure propagates, Host cleanup still runs, undrained resource retains one owner | cleanup-failure test GREEN | General failure orchestration remains G2 |

Revisions 001 through 003 and 005 are preserved executed-but-invalid attempts.
Revision 004 is preserved as a registered-but-never-executed invalid attempt.
Revision 006 hash-checks both inherited oracle dependencies and is the only
candidate for the final Gate decision.
