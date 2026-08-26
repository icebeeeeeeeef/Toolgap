# G1-C-016: Formal checked-demotion runtime revision

**Canonical state:** `roadmap`
**Gate:** G1
**Revision identity:** `G1-C-016`

## Purpose and boundary

This is a new formal, independently executable G1 runtime revision. It tests
the narrow checked-demotion contract in `experiments/g1/SPEC.md` against one
real SGLang runtime. `G1-C-001` sealed a `pre_execution` `INVALID` before any
arm when its source-restoration glob was passed literally to `sha256sum`.
`G1-C-002` also sealed a `pre_execution` `INVALID`, after it applied the three
patches: its changed-path check consulted only `git diff --name-only`, which
does not list the patch-created, untracked scripted test module before
`git add -A`. `G1-C-003` then sealed a `pre_execution` `INVALID` at resolver:
it successfully restored the patched source, prepared the model, and installed
the CUDA wheelhouse plus mirror dependencies, but copied the valid runtime
wheel under the generic filename `runtime-wheel.whl`, which pip rejects before
examining wheel bytes. All three attempts remain frozen evidence. C-004 changes
only the runtime-wheel evidence/install filename. It sealed a separate
`pre_execution` `INVALID` at `2026-08-25T01:32:28Z`, after reaching its first
enabled arm: its generated `arm-runner.py` invoked unittest at import time, so
the SGLang multiprocessing spawn child reimported the main module and failed
`_check_not_importing_main`. Its `formal_arms` exit was `1`; enabled-arm
PID/PGID, listener, and GPU cleanup evidence was clean. C-005 changed only
generated arm-runner import safety, then sealed a separate `pre_execution`
`INVALID` at resolver when the host reported `ENOSPC`. C-006 froze a 64 GiB
disk preflight but was never executed: pre-run review found that its builder's
exact schema rejected the `storage_preflight` field it had just generated, and
that its pre-execution terminal did not structurally bind failure phase/exit or
stage-appropriate preflight evidence. Commit
`0ad49f1afdf5c59285a2828afbfe36d3409caa68` remains the frozen C-006
predecessor. C-007 repairs only those review findings and changes the bound to
an executable 24 GiB; it does not reinterpret C-006 as an attempted run.
Commit `529866d7fb10c88fbbfd174a320089b5ca0f8ab8` freezes those C-007 repairs.
Formal attempt `g1-c-007-a1-20260825T042407Z` then reached its enabled arm. At
`2026-08-25 12:30:51 CST`, the SGLang scheduler-hook executor attempted to
import the selected callable's synthetic module identity and recorded
`ModuleNotFoundError: No module named 'g1_c_007_scripted'`. At C-008 freeze
time, that parent remained under its frozen 2400-second timeout, so C-008 did
not claim a premature C-007 terminal state or receipt. C-008 changed only the
generated arm-runner module identity/import path and its reviewed operator
bindings. Commit `937eb8665e8d8102b0daf0b2f06268e660ba91d4` freezes C-008.
Formal attempt `g1-c-008-a1-20260825T053604Z` sealed `pre_execution INVALID`
at `formal_arms`, exit `1`, after three complete arm records. Enabled and
bypass passed. Its fourth arm failed in `_script_non_target_coverage` when two
ordinary session-native requests produced distinct private frontiers and
`assert target_nodes == other_nodes` observed `((21,), (24,))`; the intended
`session_ref == 2` rejection state was never constructed. The same sealed
attempt's raw write-through record also exposed a second evidence defect: its
facade was `DEFERRED/DEFERRED` while its node reason was
`WRITE_THROUGH_PENDING`, but the C-008 finalizer incorrectly required the
node-specific reason on the facade. Patch 0001 source confirms that the facade
reason is the aggregate disposition for deferred node outcomes, while stale
generation remains `REJECTED/STALE_GENERATION` before backend execution.
C-009 made only those two bounded test/evidence repairs: a deterministic
shared-coverage fixture and the source-backed rejection-oracle mapping. Commit
`28a094182905fb4b8a8bc52182fb0314490baf08` freezes the reviewed C-009
bundle. Formal attempt `g1-c-009-a1-20260825T082527Z` sealed
`pre_execution INVALID` at `formal_arms`, exit `1`. Its enabled arm completed
and emitted a record, but the bypass arm failed before emitting its record:
`_complete_private_session` spent all 400 scheduler steps before the
fire-and-forget background `/generate` reached the tokenizer receive proxy.
The assertion precedes the eventual HTTP 200 in the sealed log, and no bypass
target prefill was observed. Pre-run review then found the same fire-and-forget
race in the stale-generation arm's `/close_session` control request. C-010
changed only the ordinary-request and close-session control admission fences.
Its formal attempt
`g1-c-010-a1-20260825T095119Z` sealed and externally anchored a seven-arm
`PASS`, but the final independent matrix review rejected that Gate conclusion:
the selected rows did not distinguish removal of the `LOAD_BACK_PENDING` or
settled Host-copy guards required by `experiments/g1/SPEC.md`. C-011 added
those two rows without changing the mechanism or runtime envelope. Its formal
attempt `g1-c-011-a1-20260825T113123Z` sealed `INVALID`: the load-back loader
finished before the fixture observed pending state. Source review showed that
the fixture replayed the exact session frontier while pinned SGLang caps radix
matching at `input_len - 1`; the resulting split put the real load-back anchor
on a new parent while the fixture watched the original child NodeId. C-012
repaired that match boundary and exact-anchor assertion. Its formal attempt
`g1-c-012-a1-20260825T123410Z` sealed `INVALID` after seven passing arms: the
load-back row's real Host-only tail contained eight Full-KV tokens, below the
pinned runtime's ten-token `load_back_threshold`, so the loader recomputed the
tail without creating pending state. C-013 added the threshold-derived request
length and explicit Host-tail qualification. Frozen commit
`6347aae14a98b5a2eda68d6fcf7bb92c1c3baada` was rejected before execution:
its mutation test blacklisted direct pending-state assignments but did not
exclude equivalent indirect fabrication. C-014 preserves the complete C-013
runtime protocol and adds a positive basis check: after reverting only the
three threshold-qualification source blocks, the whole scripted module must
equal frozen C-012 exactly. It does not reinterpret C-009, C-010, C-011,
C-012, or unexecuted C-013 as an accepted G1 result and is not
`G1-PREFLIGHT-001` or `CUDA12-COMPAT-001`, whose predecessor evidence remains
frozen with its own narrower conclusions.

Frozen C-014 commit `3ea9e48b2a97b68e59ec622372f31f5a69408896`
was executed as formal attempt `g1-c-014-a2-20260825T144921Z`. It sealed
`pre_execution INVALID` at `formal_arms`, exit `1`, when FlashInfer JIT tried
to execute bare `ninja` and received `FileNotFoundError`. Cleanup and offline
verification passed, and the invalid attempt remains externally anchored.

Frozen C-015 commit `d6358c1195d0b58407ba4ff053b04bf1188fbcb7`
was independently rejected before GPU execution. Review found that its
`/usr/bin/ninja` evidence did not bind bare-command PATH resolution; its
staging manifest and script verified each other without a trust root before
`apt`; its verifier did not mechanically constrain the timeout, runner, or
finalizer; and its narrow install blacklist missed conditional privileged
branches. C-016 removes the privileged prerequisite surface entirely. It uses
only the `ninja` Python distribution already installed by the frozen ordinary
requirements into the runtime venv, binds exact resolution and executable
identity before any formal arm, and does not reinterpret C-014 or unexecuted
C-015 as a Gate result.

The sole lifecycle intervention on target identity and tree state is the private, internal
`UnifiedRadixCache.checked_demote_session(session_id, generation)` path added
by patch 0001. A normal request first creates a private Full KV tail and a
committed host copy. The scripted protocol then invokes that internal path in
one bounded scheduler window and records its result. It does not expose a
ToolGap public endpoint or construct a second physical KV data plane.
The missing-Host-copy rejection fixture separately reserves and restores the
source-owned Host allocator through its existing `alloc` and `free` APIs; it
does not assign target nodes, KV values, Host values, pending identifiers, or
tree ownership.

This revision explicitly excludes G2/G3: no persistent ToolGap controller,
public pause/cancel/resume API, routing policy, cross-request reuse policy,
benchmark, recovery result, or performance claim is in scope. SGLang remains
the owner of tree residency, allocator state, device movement, eviction, and
model execution.

## Frozen runtime inputs

The generated input manifest is the execution authority. It binds one clean
ToolGap commit/tree, source seed, model snapshot, and these immutable inputs:

1. a bare ToolGap source seed;
2. a bare SGLang source seed at `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`;
3. the local-only `Qwen/Qwen3-0.6B` snapshot at
   `c1899de289a04d12100db370d81485cdf75e47ca`;
4. the G0 prebuilt runtime payload with only CUDA12 metadata rewriting and its
   provenance sidecar;
5. a minimal CUDA wheelhouse archive whose index binds the six special wheels:
   `sglang-kernel`, `sgl-deep-ep`, `sgl-deep-gemm`, `torch`,
   `torchvision`, and `torchaudio`.

The runtime wheel provenance must state
`G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite`, bind its output
wheel SHA-256, and bind the SHA-256 values of patches 0001, 0002, and 0003.
No current-tree wheel build, Rust/Cargo invocation, `$TREATMENT/python`
installation, GitHub wheel endpoint, SGLang wheel endpoint, or PyTorch wheel
endpoint is permitted. Ordinary Python dependencies may resolve only through
the G0-observed provider-internal mirror
`http://mirrors.cloud.aliyuncs.com/pypi/simple/`; a failed ordinary resolver is
an `INVALID`, not a G1 conclusion.

Patch 0001 is the unchanged internal checked-demotion implementation. The
C-016-specific patch `0002-g1-scripted-forced-demote-c016.patch` is
byte-equivalent in applied module content to frozen C-014 and C-015 and adds only the named
scripted G1 test module. Relative to C-012 patch 0002, only the load-back row
gives its ordinary private-session request a generation length derived from
`load_back_threshold + 2`, then requires the exact target's committed Full Host
value to contain at least `load_back_threshold` tokens before it submits the
loader. It retains C-012's appended token `7` and exact pending NodeId checks.
The C-016 bundle retains the basis mutation oracle outside that runtime patch. The
other eight arms, `host_value_present`, Host-pool reservation fixture, record
schema, and finalizer semantics are unchanged. Patch 0003 is
unchanged and changes only Python wheel metadata for the CUDA12 compatibility
route. The formal runtime wheel is the prebuilt G0 payload plus that metadata
rewrite, not a recompiled copy of the current source tree. Its C-016 provenance
sidecar binds the new test-only patch hash without claiming that the wheel
payload contains that test module.

## Host envelope and restoration

The executor requires one Alibaba Cloud Ubuntu 24.04 NVIDIA GPU image, Linux
x86_64, one A10 (22-25 GiB), driver `580.126.09`,
`/usr/local/cuda-12.8`, and Python 3.12.
`00-g1-c-016-bootstrap.sh` restores a detached clean ToolGap checkout from the
input seed only after validating its own manifest-bound bytes.
`20-g1-c-016.sh` is taken from that restored checkout and refuses a dirty
tracked tree.

A valid attempt ID, absolute regular staged inputs, absent output paths, a
runnable bootstrap Python/finalizer pair, Git, and a clean restored checkout
are prerequisites before an attempt can be identified. Once those basics pass,
the runner creates the attempt directory, records the absolute `work_root` in
`attempt-context.json`, and captures best-effort environment evidence before
checking Python 3.12, Linux/Ubuntu, CUDA, GPU count/type, or driver admission.
Those host-envelope mismatches therefore seal an offline-verifiable
`pre_execution INVALID`; inability to run the finalizer itself remains a
pre-attempt bootstrap failure.

The runner verifies all staged archive hashes before extracting them, validates
safe archive member names, and applies exactly three explicit manifest-bound
paths: `0001-atomic-checked-demote.patch`,
`0002-g1-scripted-forced-demote-c016.patch`, and
`0003-cuda12-compat-packaging.patch`. It records those same paths and hashes in
the resultant SGLang commit/tree/diff provenance. Before it commits, it derives
the changed inventory as the sorted union of tracked `git diff --name-only` and
untracked `git ls-files --others --exclude-standard` paths. Every candidate must
be a regular non-symlink file contained by the restored source root, and the
result must equal the frozen six-path set, including
`test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py`. The
manifest binds the runtime-wheel archive `path` to its original valid PEP 427
filename, `sglang-0.0.0.dev2+g734a8e921-cp312-cp312-linux_x86_64.whl`; the
runner preserves that basename for the immutable copied evidence and the pip
install argument. The finalizer replays that exact manifest-bound evidence path
and byte hash off-host. The six special CUDA wheels are installed with
`--find-links` and the provider mirror as the only dependency index, so
transitive `nvidia-*` dependencies may resolve from that mirror but no special
upstream wheel index is contacted.

No C-016 `19-*` prerequisite command exists, and the executor performs no
privileged action or host-package mutation. After the ordinary resolver
completes and before the first formal arm, the runner requires the exact
executable `$RUNTIME_VENV/bin/ninja`. It defines the sole formal-arm PATH as
`$RUNTIME_VENV/bin:$CUDA_HOME/bin:/usr/bin:/bin`, then requires both shell
`command -v ninja` and Python `shutil.which("ninja")` under that exact PATH to
resolve to `$RUNTIME_VENV/bin/ninja`. The sealed runtime evidence records the
exact PATH, executable path, version, and executable SHA-256. Every formal arm
receives that PATH explicitly, and the finalizer replays the path, both
resolutions, version, SHA binding, and installed `ninja` distribution off-host.
Missing or mismatched evidence seals `pre_execution INVALID` before the first
arm; it is not a G1 mechanism result.

The input manifest binds `storage_preflight.minimum_free_bytes` to
`25769803776` (24 GiB). The supporting filesystem-size observations are
`experimentally validated` only as execution-budget evidence, not as a G1
runtime result: C-004's completed resolver/first-arm work tree peaked at
`14922854400` bytes (about 13.90 GiB), so the bound is about 10.10 GiB above
that observed peak. The five sealed attempts' work trees total
`33479200768` bytes (about 31.18 GiB). The separately authorized cleanup of
only those temporary work trees therefore gives a `simulated` first-gate
budget of about 31.18 GiB available, about 7.18 GiB above the 24 GiB bound, on
the existing 99.8G root disk. The resolver gate runs before the runtime venv
and CUDA wheelhouse are created; the observed source-plus-model predecessor at
that point is about 1.71 GiB, giving a `simulated` 29.47 GiB available and
about 5.47 GiB of resolver-gate margin after that cleanup.

Before source restore and again before dependency installation, the runner
records the available and total bytes for the actual work-root filesystem. A
failed current-stage preflight may record fewer available bytes than the
manifest minimum; every required earlier-stage preflight must have passed.
The runner writes a read-only `pre-execution-failure.json` with the exact phase
and exit code before asking the finalizer to seal `pre_execution INVALID`.
Both sealing and offline verification require no preflight for `bootstrap` or
`input_binding`, the source record for `source_restore` and later, and both
records for `resolver` and later. This does not change source, model, wheel,
selector, cleanup, or G1 terminal semantics. A C-016 formal completion still
requires both passing immutable preflight records.

The same offline check binds both preflight `path` values to the context's
absolute `work_root` and validates completed-stage evidence rather than trusting
the claimed phase alone. A `source_restore` failure requires completed input
binding; `model` requires source provenance; `resolver` requires the model
receipt; `formal_arms` requires resolver/runtime setup; `scope` requires all
nine arm and cleanup records; `render` requires those arm milestones plus a
clean scope scan but permits the manifest to be absent; and `seal` requires
clean scope plus the rendered manifest checksum. The runner enters `render`
after scope succeeds and before classification/render/checksum, and enters
`seal` only after the manifest checksum exists. The currently failing stage may
be incomplete, but every earlier milestone must be present and structurally
valid.

The generated arm runner defines `main()` and invokes it only under
`if __name__ == "__main__"`. It resolves the selected scripted test path,
prepends that file's parent directory to the parent process `sys.path`, imports
the module by its real filename stem, and verifies that the imported
`module.__file__` resolves back to the selected path. Multiprocessing spawn
inherits this `sys.path`, so a scheduler-hook child can import a callable's
real `__module__` identity. The main guard still lets a spawn child reimport the
runner as its bootstrap main module without resolving a selector, loading a
test suite, or starting another arm. The selected unittest suite must still
resolve exactly one named selector and executes only in the isolated parent
arm process.

The test-only ordinary session request helper uses the pinned scripted
runtime's existing `_http_post_and_await_recv_msg` primitive. Its predicate
accepts only the exact request `rid`, so unrelated or stale tokenizer messages
cannot start the completion budget. The unchanged 400 scheduler-step bound
begins only after that exact request has reached the tokenizer receive proxy.
This adds no endpoint, scheduler event, sleep, retry policy, or runtime API; it
only orders the existing request submission before the existing completion
poll.

The stale-generation arm uses the same pinned arrival primitive for its
existing `/close_session` control request. Its predicate requires both a
`CloseSessionReqInput` instance and the exact `session_id`. Only after that
control message reaches the tokenizer receive proxy does the unchanged
400-step wait check that the old generation was released. No bare
`_submit_post` remains in the scripted fixture.

The positive enabled and bypass arms remain fully request-native: an ordinary
request creates their real private Full node and no test mutates its tree, KV
value, or allocator state. For only the deterministic
`reject_non_target_session_coverage` arm, the first ordinary request likewise
creates and settles the real target. The test then uses SGLang's existing
`ensure_session_generation` and `TreeComponent.register_session_leaf` APIs to
register a second session's logical coverage on that leaf. Those source-owned
APIs maintain `_session_leaves`, `session_ids`, and path `session_ref`; the test
asserts the target reference changes from `1` to `2` before the action and back
to `1` after target-session priority release. It does not manufacture a node,
NodeId, KV value, Host copy, allocator entry, or physical ownership. This
supersedes only the executable design's falsified assumption that two distinct
session-native requests would share the same private frontier.

## Arms and selectors

Every selector is executed once in a separate process group and fresh SGLang
runtime. The runner records a distinct command, PID/PGID, log, extracted JSON
record, process-group cleanup observation, listener cleanup observation, and
GPU-PID delta for each arm. GPU PID samples begin immediately after the arm
PID is known and continue at 0.25-second intervals until that arm exits; the
immutable sample ledger is replayed into `during`, with
`attributable = during - before` and `leaked = attributable intersection after`.
The only accepted selector set is:

The internal arm launcher calls `setsid` before importing or executing any arm
workload. It then creates a read-only, exclusive PID/PGID handshake and waits up
to ten seconds for a read-only parent acknowledgement. The parent requires the
handshake PID to equal the background PID and `pgid == pid`, records that PGID,
and only then writes the acknowledgement that permits the launcher to `exec`
the bounded workload. Both files are per-arm sealed evidence. Failure before
the handshake cannot start workload descendants; after the handshake, cleanup
uses the recorded group even if its leader has already exited, then waits for
the group to disappear. That bounded group-exit observation is mandatory: a
timeout propagates as runner failure while retaining the PID/PGID identity.
`seal_invalid` must not write failure evidence, invoke the finalizer, or create
terminal artifacts unless cleanup proves the group is gone. Such a cleanup
timeout leaves only unsealed raw diagnostics and is not `PASS`, `STOP`, or
`INVALID`.

| Arm | Selector | Required observation |
| --- | --- | --- |
| `enabled` | `TestG1EnabledArm.test_enabled_checked_demotion_records_allocator_visible_release` | accepted checked path, Full-only committed host copy, allocator-visible release and exact freed device IDs |
| `bypass` | `TestG1BypassArm.test_bypass_releases_priority_without_physical_reclamation` | priority release only; no checked, physical, drain, allocator, or stock-eviction action |
| `reject_write_through_pending` | `TestG1WriteThroughPending.test_uncommitted_host_copy_is_deferred_without_physical_free` | no physical free while host write-through is pending |
| `reject_non_target_session_coverage` | `TestG1NonTargetCoverage.test_shared_target_is_deferred_for_the_other_session` | no physical free for a tail covered by another session |
| `reject_device_locked` | `TestG1DeviceLocked.test_active_request_is_deferred_at_the_device_lock_check` | no physical free while a device lock is live |
| `reject_stale_generation` | `TestG1StaleGeneration.test_stale_generation_is_rejected_before_priority_release` | stale generation rejected before priority release |
| `stock_eviction_liveness` | `TestG1StockEvictionLiveness.test_stock_eviction_remains_reachable_after_bypass` | ordinary pressure reaches stock eviction after the bypass arm |
| `reject_load_back_pending` | `TestG1LoadBackPending.test_inflight_host_to_device_load_is_deferred_without_physical_free` | no physical free while a real Host-to-device transfer remains pending, before the later device-lock guard |
| `reject_host_copy_not_committed` | `TestG1HostCopyNotCommitted.test_settled_missing_host_copy_is_deferred_without_physical_free` | no physical free when pending work and locks are clear but the Full Host value is absent |

The six rejection cases are the six `reject_*` rows above. The tests issue
ordinary local `/generate` requests to create real private KV state. The only
lifecycle intervention on the target is the private internal call described
above; the missing-Host-copy row additionally uses the bounded Host allocator
reservation fixture described above.

## Evidence and terminal classification

`g1_c_016_finalize.py` independently validates the raw arm records. A
successful `PASS` requires all nine exactly once, Full-only qualification,
enabled acceptance with a committed host copy, nonempty exact freed IDs and an
increase in allocator `available_size`, bypass priority-only behavior, each
rejection reason with no physical free or capacity increase, and observed stock
eviction with a real victim. For write-through pending, non-target session
coverage, and device lock, the operation must contain exactly `session_id` and
`supplied_generation`; requested, scheduled, and node-outcome IDs must be the
same nonempty unique sequence; eligible and completed IDs must be empty; and
live before/after observations must exactly cover those IDs while preserving
nonempty device IDs. Released component leaves must be positive. The facade
must be `DEFERRED/DEFERRED` and each node outcome must carry the arm-specific
reason. Write-through observations remain pending, non-target coverage changes
`session_ref` from `2` to `1` while preserving committed host/device-leaf
state, and device-lock observations retain a positive lock. The ordered backend
reason must also be replayable. Load-back observations retain the Host value,
a live pending identifier, and a positive device lock while `host_committed`
remains false until the transfer settles. The Host-copy row records
`host_value_present == false`, no pending identifier, no lock, and an unchanged
device-resident leaf. Its raw Host-pool evidence requires
`available_before_reservation == logical_size`, a full unique reservation that
leaves zero available slots, and a release return/count that restores
`available_after_release == logical_size`; no scheduler yield is permitted
between that release and the checked action. Non-target observations have no write/load
pending state and all locks are zero; device-lock observations have no
write/load pending state and retain a committed host copy. Write-through and
device-lock observations change target `session_ref` from `1` to `0` after
priority release. Stale generation must be `REJECTED/STALE_GENERATION` with an
exact three-field operation whose
non-boolean supplied and current generations differ, zero released leaves, an
empty target, and no backend or node outcome. This is an execution result only;
the project claim remains `roadmap` until the canonical Gate process accepts
it.

Every live node observation is also pinned-source schema evidence. Although
this experiment qualifies only `FULL`, SGLang's `component_data` retains the
fixed `FULL`, `SWA`, and `MAMBA` slots, so `lock_refs` has exactly three
nonnegative integers; the observed C-008 write-through shape is `[1, 0, 0]`.
`session_ref` is nonnegative. Every NodeId sequence contains unique,
nonnegative exact integers, and before/after observation NodeIds exactly match
the requested order. Within each before or after snapshot, live allocator IDs
are globally unique; the two snapshots and stock-victim history are not
incorrectly merged. `eligible_node_ids` is recomputed from before observations:
live, host-committed, device-leaf, zero locks, and `session_ref == 1`. Enabled
and bypass additionally require the prepared source state to have no pending
transfer and nonempty device IDs. Their after observations must remain live,
host-committed, pending-free, zero-locked, and at `session_ref == 0`. Each is
either the exact unchanged prepared device shape or the demoted host-only shape
with empty device IDs and `device_leaf == false`; tombstones, host loss, and
hybrids are `INVALID`. For bypass, demoted after NodeIds exactly equal the
instrumented physical-demote NodeIds. Stock liveness requires the same prepared
before state and `session_ref == 0` for any live after observation, but permits
pressure-time locks. A live target that retains device IDs must preserve the
before IDs and device-leaf state. An empty-device or tombstone target after is
accepted only when the same NodeId has a stock-victim record whose `after`
observation is exactly equal, so pressure explains the mutation. Enabled binds requested, eligible,
scheduled, completed,
node-outcome, and physical-demote NodeIds; each nonempty outcome is
`COMPLETED/DEMOTED`. Its physical-demote and cache-drain counts each equal the
requested node count. Bypass and stock liveness bind requested/eligible and
leave scheduled, completed, and node outcomes empty. A passing bypass has no
physical demote; a causal bypass counterexample may report requested physical
IDs only when the demote count, ID count, and cache-drain count agree.
Enabled and each non-stale rejection also require `checked_backend` to equal
the requested NodeId count; stale rejection requires zero backend calls.
For each ordered enabled node, a demoted after shape requires that node's freed
IDs to exactly equal its own before device IDs; an unchanged after shape
requires empty node frees. The aggregate is the ordered flattening of those
per-node values, so frees cannot be reassigned across nodes. An all-unchanged
record also requires unchanged allocator capacity and is the coherent
missing-reclaim `STOP`; a demoted record with exact frees is `STOP` when
capacity is unchanged and can `PASS` only when capacity increases.
Stock candidates are unique nonnegative NodeIds. Allocator device indices are
nonnegative and unique per observation; enabled observations are also globally
unique. Per-node freed indices flatten exactly to the aggregate freed indices,
and any nonempty freed evidence exactly matches the original device-tail order.
Malformed or contradictory IDs are `INVALID`; a structurally consistent empty
enabled free result remains the causal missing-reclaim `STOP` case.

Patch 0002 asserts setup, route, priority release, and normal return before
emitting enabled/bypass records, but deliberately does not assert the PASS-side
free, capacity, or post-device effects. Thus a source-produced causal
counterexample reaches the runner and finalizer instead of dying before record
extraction. `STOP` is permitted only after all rejection and stock-liveness
semantics have passed, the enabled and bypass records are formally complete,
and only for the two causal counterexamples: enabled lacks
allocator-visible physical reclaim, or bypass exhibits one. A wrong bypass
priority-release result, wrong facade, wrong checked-route counter, malformed
record, rejection/liveness anomaly, or any other non-causal anomaly is
`INVALID` before causal `STOP` is considered, even if the same record set also
lacks or exhibits reclaim. Bad input binding, host mismatch, resolver failure,
test failure,
unsafe scope, or cleanup failure is also `INVALID`. `INVALID` never becomes
evidence for a G1 rejection.

The terminal artifacts are immutable: `execution-status.json`,
`artifact-index.json`, and `completion-receipt.json`. The finalizer's
`verify` mode replays context/input/runtime provenance, selectors, per-arm
PID/PGID/listener/GPU cleanup evidence, scope scan, raw records, and the
classification oracle off-host using only the sealed directory. The
runner terminates and waits for the active sampler and isolated arm process
group before recording an `INVALID` after any error or a handled `HUP`, `INT`,
or `TERM` signal. Offline verification requires the artifact-index paths to be
sorted and exactly equal the sealed directory's regular files other than the
index and completion receipt themselves; it rejects unindexed files, symlinks,
and a non-canonical or non-exact completion receipt.
operator-only `scripts/anchor-g1-c-016-oss.sh` first performs that
verification, uploads each indexed artifact to a versioned OSS prefix, and
writes an external anchor that binds every OSS object version. The ECS role only
needs input reads; the anchor step is not an ECS action.
