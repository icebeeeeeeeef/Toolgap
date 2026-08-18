# Performance Boundary

> Status: `roadmap`
>
> Document role: result template; it contains no current performance claim
>
> This document intentionally contains no performance claim. Populate it only
> from Gate G4 artifacts.

## 1. Result Question

Under what declared engine, model, hardware, workload, pressure, sharing, and
recovery conditions does checked demotion improve, lose, or become irrelevant to
the joint serving SLO relative to the strongest simple baseline?

## 2. Fixed Testbed

To be filled from the G4 manifest:

- SGLang commit: `[commit]`
- candidate patch/hash: `[hash]`
- model and revision: `[model]`
- tokenizer/template identity: `[identity]`
- GPU/CPU/DRAM: `[hardware]`
- HiCache configuration: `[flags]`
- workload source and seeds: `[workload]`
- SLO thresholds: `[S_resume, S_itl, S_success]`

## 3. Causal Decomposition

Report evidence for every edge:

```text
eligible bytes
  -> completed physical demotion
  -> allocator-visible headroom
  -> changed scheduling/admission behavior
  -> sustainable-load delta
  -> resume recovery cost
  -> foreground interference
```

A missing edge breaks the end-to-end optimization claim even when an earlier
metric improves.

## 4. Required Boundary Axes

- realized device-pool pressure;
- unique reclaimable bytes;
- shared-prefix ratio and protected non-target coverage;
- pause duration and resume probability;
- Host restore versus recompute cost;
- foreground decode load;
- stock eviction response time;
- concurrent demotion/restore work.

## 5. Required Result Tables

### Mechanism table

| Regime | Requested bytes | Eligible bytes | Freed bytes | Time to headroom | Cleanup |
|---|---:|---:|---:|---:|---|
| `[name]` | `[value]` | `[value]` | `[value]` | `[value]` | `[pass/fail]` |

### Joint-SLO table

| Regime | Baseline | Sustainable lambda | Resumed TTFT p95 | Foreground ITL p95 | Success rate |
|---|---|---:|---:|---:|---:|
| `[name]` | `[baseline]` | `[value]` | `[value]` | `[value]` | `[value]` |

### Recovery table

| Regime | Restore queue | H2D | Recompute prefill | First token | Fallback rate |
|---|---:|---:|---:|---:|---:|
| `[name]` | `[value]` | `[value]` | `[value]` | `[value]` | `[value]` |

## 6. Mandatory Losing Regions

At minimum, report:

- low pressure where early reclaim has no capacity value;
- small/private KV where control overhead dominates;
- fast stock eviction where active reclamation adds no timeliness;
- expensive recovery or interference where the joint SLO regresses;
- shared-prefix-heavy conditions where eligibility collapses.

## 7. Optimization Discipline

Optimization follows evidence in this order:

1. delete work that does not affect allocator or scheduler behavior;
2. reduce critical-path synchronization and duplicate bookkeeping;
3. reduce transfer and compute interference using measured queues;
4. improve target resolution only when it is a measured bottleneck;
5. consider dynamic policy only after G5;
6. consider another storage tier or prefetch only through a separate review.

Do not add a mechanism merely because it could improve a synthetic microbenchmark.

## 8. Allowed Conclusion Shape

```text
On [fixed testbed], checked demotion [won/lost/was neutral] relative to
release-priority-only plus stock eviction in [registered regimes]. The result was
caused by [measured chain]. It did not generalize to [losing boundary].
```

Until every placeholder is backed by an exact artifact, the conclusion remains
`roadmap`.
