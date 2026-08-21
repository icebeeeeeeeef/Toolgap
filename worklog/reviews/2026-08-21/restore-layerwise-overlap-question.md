# Restore layer-wise overlap verification question — preflight rejection

Canonical owners: D033 in `docs/DECISIONS.md` (single-series discipline), the
"Conditional performance diagnosis (not a Gate)" section in `docs/ROADMAP.md`,
and `docs/future/PREFETCH_ADMISSION.md` (the future hiding-latency family).

Decision question: should ToolGap absorb a layer-wise pipelined fetch of KV
cache from an external L3 store (Mooncake-style, overlapped with per-layer
prefill compute) as a "preflight" mainline mechanism, and separately, does the
pin's resumed-session Host-to-Device restore path already use any existing
layer-wise overlapped loader?

On the pin, `python/sglang/srt/managers/cache_controller.py` owns D2H/H2D
submission and completion events; this is an accepted G0 source fact
(`experiments/g0/artifacts/source-index.md`). Two supporting claims are
**inferences, not yet verified on the pin**: (a) upstream SGLang is believed to
already implement layer-by-layer H2D loading overlapped with per-layer prefill
compute; (b) the pin's L3 storage-to-host prefetch is believed to be
request-time and page-granularity, not layer-wise pipelined with compute.
Mooncake supplies a store and transfer engine (get/put/batch, zero-copy) but
not an engine-side layer-wise pipelining scheduler; LMCache's layerwise
pipelining and the Cake paper are existing prior art, so no novelty claim is
available for this mechanism.

Decision: reject adopting the L3/Mooncake preflight variant into the G0-G4
mainline — it would add a storage tier and dependency excluded by
`docs/PROJECT.md` non-goals and duplicate LMCache prior art. Any L3 variant
belongs to the same "hide transfer latency" future family as
`docs/future/PREFETCH_ADMISSION.md` and needs its own future admission review.
Admit one narrow verification question into the existing measurement-driven
series (the symptom-triggered diagnosis path in `docs/ROADMAP.md`, per D033's
single-series discipline): does the pin's resumed-session restore/load_back
path go through the existing layer-wise overlapped loader, or a synchronous
bulk path? If verification finds a bulk path, extending the existing upstream
layer-wise machinery to restore becomes one candidate root-cause fix competing
with transfer coalescing/pinned-buffer work for the same optimization slot;
the profiler decides which fix is implemented. No new Gate; no new requirement
on G2/G3 beyond this observation question for future SPEC authors.

Rejected alternatives: absorbing Mooncake/L3 layer-wise preflight into the
mainline (tier and dependency expansion, prior-art duplication); claiming
novelty for layer-wise pipelining (LMCache/Cake exist); implementing the
restore-path extension now, before pin verification and profiling evidence;
treating this as a second parallel optimization series (D033 allows only one
measurement-driven series).

All claims remain `roadmap`; no experimental evidence was created.
