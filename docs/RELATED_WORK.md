# Related Work and Upstream Boundary

> Status: `roadmap`
>
> Document role: research input
>
> This document prevents attribution drift. It does not claim novelty from the
> absence of a repository or search result.

## 1. Positioning Rule

ToolGap does not claim to invent tool-gap KV retention, offload, eviction,
prefetch, workflow prediction, or hierarchical KV caching.

The candidate contribution, if implemented and validated, is narrower:

> a fixed-version, auditable SGLang HiCache session-scoped checked-demotion and
> recovery contract, with failure semantics, strongest-simple-baseline
> comparison, and a reproducible single-node performance boundary.

Prior art changes attribution, baselines, and scope before it changes the core
engineering question.

## 2. Directly Relevant Work

| Work | Occupied idea space | Required comparison or boundary |
|---|---|---|
| [SGLang Agentic KV RFC](https://github.com/sgl-project/sglang/issues/27574) | Orchestrator hints, engine arbitration, publication/reclamation separation | Align ownership and avoid direct external node manipulation |
| [SGLang session preemption RFC](https://github.com/sgl-project/sglang/issues/29099) | Session-level preemption and policy overlap | Recheck upstream trajectory before implementation |
| [InferCept](https://arxiv.org/abs/2402.09369) | Preserve/swap/discard around tool or API interruption | Compare lifecycle action framing and breakeven evidence |
| [TokenCake](https://arxiv.org/abs/2510.18586) | Tool-stall proactive offload/upload and agent scheduling | Treat proactive movement as occupied prior art; compare implementation and evidence boundaries |
| [PBKV](https://arxiv.org/abs/2605.06472) | Workflow-aware KV management based on SGLang and HiCache | Compare shared-prefix policy and SGLang integration directly; do not describe it as a vLLM/PyTorch prototype |
| [KVFlow](https://arxiv.org/abs/2507.07400) | Workflow-guided eviction and proactive CPU-to-GPU movement | Keep workflow prediction outside the unconditional mainline |
| [Continuum](https://arxiv.org/abs/2511.02230) | Tool-aware KV lifetime/TTL | Use as a dynamic-policy baseline only if G5 opens |
| [TraceLab](https://github.com/uw-syfi/TraceLab) | Public client-side agent/tool traces | Use for workload calibration, not server residency or cost truth |

PBKV is explicitly treated as SGLang/HiCache prior art in this project. The
comparison dimensions are substrate and fixed revision, ownership of lifecycle
and physical movement, shared-prefix behavior, hint/prediction source,
failure/cleanup semantics, measurement boundary, and reproducibility. A paper
or search result can establish an occupied idea space; it cannot establish an
unverified implementation or evidence claim for this project.

## 3. Upstream Contract Boundary

The fixed-pin source facts and links are owned by
[ARCHITECTURE.md](ARCHITECTURE.md). They show that SGLang already provides
physical tree demotion, hierarchical cache machinery, eviction logic, session
generations, and session-aware priority. The draft must therefore avoid
unqualified claims that:

- the existing upstream physical demotion primitive is missing;
- existing upstream lifecycle semantics are nonexistent;
- session references are hard pins;
- the backend registry is necessarily a small callback seam.

The missing candidate contract must be demonstrated more precisely: safe
session-scoped target resolution, admission semantics, lifecycle composition,
completion fencing, cleanup, attribution, and baseline value.

## 4. Evidence Language

- “The paper describes” requires the paper body.
- “The implementation contains” requires a fixed source revision.
- Repository-availability observations must state search date, method, and
  evidence level.
- Public-availability claims require stronger evidence than a failed search.
- “Upstream validated” requires maintainer review, acceptance, or merged evidence;
  opening an issue is only a public artifact.
- Priority, completeness, and absence claims are not project claims.

## 5. Reverification Triggers

Repeat upstream and prior-art review when:

- selecting the final SGLang commit;
- G0 identifies a missing interface;
- starting an upstream issue or patch;
- G5 considers dynamic policy;
- a new SGLang release changes session, eviction, prefetch, or demotion behavior;
- preparing a resume or public project description.
