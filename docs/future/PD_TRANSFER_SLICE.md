# PD KV Transfer Slice Admission Contract

> Status: `roadmap`
>
> Project claim state: `roadmap`
>
> Admission: separate future review; this is not a Gate and is not part of the
> G0-G4 unconditional mainline. It is expected to live in a separate repository
> or a clearly separated extension.
>
> Implementation: not started. Experimental evidence: none.

## 1. Purpose and Boundary

This document specifies how to decide whether a narrow prefill-to-decode KV
transfer slice deserves a separate implementation review. It does not authorize
implementation, does not change the checked-demotion contract, and does not add
distributed, multi-node, RDMA, or PD claims to the mainline. The mainline
non-goals in [`PROJECT.md`](../PROJECT.md) remain in force.

The question is narrow:

> On a fixed transport that the candidate does not implement, does a
> candidate-owned transfer lifecycle contract — slice granularity, small-object
> coalescing, bounded concurrent channels, per-slice integrity verification,
> and atomic destination visibility — measurably improve transfer tail latency
> and time-to-decode-admission over the same transport's naive per-block
> per-layer baseline, while preserving abort, partial-failure, stale-completion,
> and retry correctness?

The mainline must remain correct, complete, and meaningful if this document,
its repository, and its experiments are deleted.

## 2. Ownership Boundary

The candidate must reuse an existing transport and must not build one:
admissible transports include an existing transfer engine (for example
Mooncake TransferEngine or NIXL), GPU peer-to-peer copy, or a TCP plus
pinned-host-memory relay. The candidate must not implement an RDMA stack, a
replacement KV store, an allocator, an eviction policy, or a second physical
KV data plane inside ToolGap.

The candidate may own only:

- slice granularity policy: splitting a large KV payload into fixed-size
  slices and coalescing small objects into batched transfer jobs;
- bounded concurrent transfer channels with backpressure;
- per-slice integrity verification plus a whole-payload check, so a single
  slice is self-checking and the full value is verifiable;
- decoupling of request lifecycle from KV lifecycle via refcount or lease on
  source blocks while a transfer is in flight;
- atomic destination visibility: the destination marks KV usable only after
  every required rank, layer, and slice completes and verifies;
- abort, partial completion, stale completion, idempotent retry, and fallback
  to recompute;
- transfer-level measurement: effective bandwidth, per-slice latency
  distribution, and end-to-end time-to-decode-admission.

This lifecycle contract deliberately mirrors the mainline's operation
identity, stale-completion fencing, and cleanup ownership; the extension is a
transfer-domain application of the same discipline, not a new philosophy.

## 3. Admission Preconditions

All of the following must hold before an implementation review is scheduled:

1. G1 has a real physical-demotion PASS on the fixed pin, so the mainline's
   claim to real CUDA evidence does not depend on this extension;
2. the extension has its own frozen environment manifest: hosts, GPUs, NICs,
   link topology, transport software versions, and exact configuration;
3. a baseline transport path runs unmodified end to end before any candidate
   policy is added;
4. the mainline deletion test in Section 7 is accepted as binding.

Two or three rented machines are sufficient; the design must not assume five.
A single multi-GPU host using peer-to-peer copy is an admissible degenerate
topology if the claim language follows Section 4.

## 4. Hardware Honesty Contract

Every published claim must name the actual transport and topology measured:
RDMA verbs on InfiniBand or RoCE, GPUDirect, NVLink or PCIe peer-to-peer,
or TCP with pinned host memory. If the rented machines have no RDMA-capable
NICs, no claim may use the words RDMA, GDR, or zero-copy. Absence of RDMA
hardware narrows the claim language; it does not block admission, because the
lifecycle and slicing contract is transport-independent.

## 5. Baselines and Fair Comparison

At minimum compare, with identical transport, payloads, workload, machines,
and instrumentation:

1. **T0 — naive baseline:** per-block or per-layer transfers issued in arrival
   order on the unmodified transport path;
2. **T1 — candidate path:** sliced, coalesced, bounded-concurrency transfers
   with per-slice verification and atomic visibility;
3. **T2 — ablations:** the candidate with slicing disabled, coalescing
   disabled, or concurrency fixed to one, to attribute any effect to a
   specific policy rather than to the bundle.

Primary endpoints are transfer completion tail latency (p95/p99),
time-to-decode-admission, and effective bandwidth versus payload size.
Losing regimes must be preserved: small payloads where batching adds waiting,
low concurrency where channels add overhead, and fast links where coalescing
is irrelevant.

## 6. Correctness and Failure Semantics

The admission record must include deterministic evidence for:

- corruption injection: a corrupted slice is detected by its own check, the
  payload is not marked usable, and retry or recompute fallback is observed;
- abort while in flight: source blocks stay protected by refcount or lease
  until abort completes, then are released exactly once;
- partial transfer: the destination never serves a partially transferred
  payload;
- stale completion: a completion for a superseded transfer generation cannot
  publish destination visibility but still releases its buffers and jobs;
- idempotent retry: a retried slice cannot double-publish or leak;
- cleanup ledger: buffers, jobs, channels, leases, and destination
  reservations return to quiescence after every failure case.

## 7. Deletion Test

Before any implementation is accepted:

1. remove the extension's repository, code, flags, and traces;
2. run the G0-G4 mainline tests and baselines;
3. verify that checked demotion, lifecycle correctness, fallback,
   DecisionTrace, and joint-SLO evaluation retain the same ownership and
   meaning;
4. verify that no mainline title, contract, or success condition mentions PD
   transfer, slicing, or multi-node behavior.

If deletion changes the mainline contract, the projects have been coupled and
this extension must be rejected or redesigned.

## 8. Decision Rules

### PASS

Grant an implementation review only if T1 beats T0 beyond measured noise on a
pre-registered payload and concurrency regime, at least one ablation
attributes the effect, every Section 6 failure case passes, and the claim
language satisfies Section 4.

### DEFER

Defer when the effect exists only on unrepresentative payloads, the rented
topology cannot support the intended claim, or mainline Gates still need the
hardware budget. Record the result; the mainline is unaffected.

### REJECT

Reject when T1 is indistinguishable from or worse than T0 after costs, when
correctness cannot be owned on the chosen transport, or when the extension
would need to modify the transport or the mainline to win. A REJECT is a
valid engineering result and does not weaken G0-G4 conclusions.
