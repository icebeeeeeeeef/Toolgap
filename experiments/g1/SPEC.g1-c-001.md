# G1-C-001: Formal checked-demotion runtime revision

**Canonical state:** `roadmap`
**Gate:** G1
**Revision identity:** `G1-C-001`

## Purpose and boundary

This is the first formal, independently executable G1 runtime revision. It tests
the narrow checked-demotion contract in `experiments/g1/SPEC.md` against one
real SGLang runtime. It is not `G1-PREFLIGHT-001` and it is not
`CUDA12-COMPAT-001`: those predecessor bundles remain frozen evidence with
their own, narrower conclusions.

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
`00-g1-c-001-bootstrap.sh` restores a detached clean ToolGap checkout from the
input seed only after validating its own manifest-bound bytes.
`20-g1-c-001.sh` is taken from that restored checkout and refuses a dirty
tracked tree.

The runner verifies all staged archive hashes before extracting them, validates
safe archive member names, applies exactly the three patches to the restored
SGLang seed, and records the resultant SGLang commit/tree/diff provenance. It
installs the immutable runtime wheel into a fresh virtual environment. The six
special CUDA wheels are installed with `--find-links` and the provider mirror
as the only dependency index, so transitive `nvidia-*` dependencies may resolve
from that mirror but no special upstream wheel index is contacted.

## Arms and selectors

Every selector is executed once in a separate process group and fresh SGLang
runtime. The runner records a distinct command, PID/PGID, log, extracted JSON
record, process-group cleanup observation, listener cleanup observation, and
GPU-PID delta for each arm. The only accepted selector set is:

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

`g1_c_001_finalize.py` independently validates the raw arm records. A
successful `PASS` requires all seven exactly once, Full-only qualification,
enabled acceptance with a committed host copy, nonempty exact freed IDs and an
increase in allocator `available_size`, bypass priority-only behavior, each
rejection reason with no physical free or capacity increase, and observed stock
eviction with a real victim. This is an execution result only; the project
claim remains `roadmap` until the canonical Gate process accepts it.

`STOP` is permitted only for a well-formed enabled/bypass comparison that
directly contradicts the causal G1 predicate: enabled has no allocator-visible
physical reclaim or bypass exhibits one. Bad input binding, host mismatch,
resolver failure, malformed/missing records, test failure, unsafe scope,
cleanup failure, or any non-causal observation is `INVALID`. `INVALID` never
becomes evidence for a G1 rejection.

The terminal artifacts are immutable: `execution-status.json`,
`artifact-index.json`, and `completion-receipt.json`. The finalizer's
`verify` mode checks them off-host using only the sealed directory. The
operator-only `scripts/anchor-g1-c-001-oss.sh` first performs that
verification, uploads each indexed artifact to a versioned OSS prefix, and
writes an external anchor that binds every OSS object version. The ECS role only
needs input reads; the anchor step is not an ECS action.
