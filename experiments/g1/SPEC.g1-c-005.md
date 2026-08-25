# G1-C-005: Formal checked-demotion runtime revision

**Canonical state:** `roadmap`
**Gate:** G1
**Revision identity:** `G1-C-005`

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
only the runtime-wheel evidence/install filename; `G1-C-004` is a separate
in-flight frozen attempt that reached its first enabled arm. Its generated
`arm-runner.py` invokes unittest at import time, so the SGLang multiprocessing
spawn child reimports the main module and fails `_check_not_importing_main`.
Its parent remains under the frozen 2400-second timeout and must not be
interrupted or rewritten. C-005 changes only generated arm-runner import
safety; it is not `G1-PREFLIGHT-001` or `CUDA12-COMPAT-001`, whose predecessor
evidence also remains frozen with its own narrower conclusions.

The sole intervention is the private, internal
`UnifiedRadixCache.checked_demote_session(session_id, generation)` path added
by patch 0001. A normal request first creates a private Full KV tail and a
committed host copy. The scripted protocol then invokes that internal path in
one bounded scheduler window and records its result. It does not expose a
ToolGap public endpoint or construct a second physical KV data plane.

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

Patch 0001 is the internal checked-demotion implementation. Patch 0002 adds
only the named scripted G1 test module. Patch 0003 changes only Python wheel
metadata for the CUDA12 compatibility route. The formal runtime wheel is the
prebuilt G0 payload plus that metadata rewrite, not a recompiled copy of the
current source tree.

## Host envelope and restoration

The executor requires one Alibaba Cloud Ubuntu 24.04 NVIDIA GPU image, Linux
x86_64, one A10 (22-25 GiB), driver `580.126.09`,
`/usr/local/cuda-12.8`, and Python 3.12.
`00-g1-c-005-bootstrap.sh` restores a detached clean ToolGap checkout from the
input seed only after validating its own manifest-bound bytes.
`20-g1-c-005.sh` is taken from that restored checkout and refuses a dirty
tracked tree.

The runner verifies all staged archive hashes before extracting them, validates
safe archive member names, and applies exactly three explicit manifest-bound
paths: `0001-atomic-checked-demote.patch`,
`0002-g1-scripted-forced-demote.patch`, and
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

The generated arm runner defines `main()` and invokes it only under
`if __name__ == "__main__"`. A multiprocessing spawn child may therefore
reimport the runner as its bootstrap main module without resolving a selector,
loading a test suite, or starting another arm. The selected unittest suite must
still resolve exactly one named selector and executes only in the isolated
parent arm process.

## Arms and selectors

Every selector is executed once in a separate process group and fresh SGLang
runtime. The runner records a distinct command, PID/PGID, log, extracted JSON
record, process-group cleanup observation, listener cleanup observation, and
GPU-PID delta for each arm. GPU PID samples begin immediately after the arm
PID is known and continue at 0.25-second intervals until that arm exits; the
immutable sample ledger is replayed into `during`, with
`attributable = during - before` and `leaked = attributable intersection after`.
The only accepted selector set is:

| Arm | Selector | Required observation |
| --- | --- | --- |
| `enabled` | `TestG1EnabledArm.test_enabled_checked_demotion_records_allocator_visible_release` | accepted checked path, Full-only committed host copy, allocator-visible release and exact freed device IDs |
| `bypass` | `TestG1BypassArm.test_bypass_releases_priority_without_physical_reclamation` | priority release only; no checked, physical, drain, allocator, or stock-eviction action |
| `reject_write_through_pending` | `TestG1WriteThroughPending.test_uncommitted_host_copy_is_deferred_without_physical_free` | no physical free while host write-through is pending |
| `reject_non_target_session_coverage` | `TestG1NonTargetCoverage.test_shared_target_is_deferred_for_the_other_session` | no physical free for a tail covered by another session |
| `reject_device_locked` | `TestG1DeviceLocked.test_active_request_is_deferred_at_the_device_lock_check` | no physical free while a device lock is live |
| `reject_stale_generation` | `TestG1StaleGeneration.test_stale_generation_is_rejected_before_priority_release` | stale generation rejected before priority release |
| `stock_eviction_liveness` | `TestG1StockEvictionLiveness.test_stock_eviction_remains_reachable_after_bypass` | ordinary pressure reaches stock eviction after the bypass arm |

The four rejection cases are the four `reject_*` rows above. The tests issue
ordinary local `/generate` requests only to create real private KV state; the
only lifecycle intervention is the private internal call described above.

## Evidence and terminal classification

`g1_c_005_finalize.py` independently validates the raw arm records. A
successful `PASS` requires all seven exactly once, Full-only qualification,
enabled acceptance with a committed host copy, nonempty exact freed IDs and an
increase in allocator `available_size`, bypass priority-only behavior, each
rejection reason with no physical free or capacity increase, and observed stock
eviction with a real victim. This is an execution result only; the project
claim remains `roadmap` until the canonical Gate process accepts it.

`STOP` is permitted only after the enabled and bypass records are formally
complete, and only for the two causal counterexamples: enabled lacks
allocator-visible physical reclaim, or bypass exhibits one. A wrong bypass
priority-release result, wrong facade, wrong checked-route counter, malformed
record, or any other non-causal anomaly is `INVALID`, even if it also lacks
reclaim. Bad input binding, host mismatch, resolver failure, test failure,
unsafe scope, or cleanup failure is also `INVALID`. `INVALID` never becomes
evidence for a G1 rejection.

The terminal artifacts are immutable: `execution-status.json`,
`artifact-index.json`, and `completion-receipt.json`. The finalizer's
`verify` mode replays context/input/runtime provenance, selectors, per-arm
PID/PGID/listener/GPU cleanup evidence, scope scan, raw records, and the
classification oracle off-host using only the sealed directory. The
runner terminates and waits for the active sampler and isolated arm process
group before recording an `INVALID` after any error or termination signal.
operator-only `scripts/anchor-g1-c-005-oss.sh` first performs that
verification, uploads each indexed artifact to a versioned OSS prefix, and
writes an external anchor that binds every OSS object version. The ECS role only
needs input reads; the anchor step is not an ECS action.
