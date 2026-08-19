# G0 CUDA plan Steelman review

> Status: completed
>
> Claim state: `roadmap`
>
> Date: 2026-08-18
>
> Decision: replace the proposed G0 CUDA plan with
> [`g0-cuda-real-integration-validation-v2.md`](../../plans/2026-08-18/g0-cuda-real-integration-validation-v2.md).

## Decision question

What is the smallest rented-CUDA experiment that can close the missing
integration evidence from G0-C-006, without claiming G1's physical-demotion,
allocator, lifecycle, or performance work?

## Steelman of the original plan

The original plan had the right strategic shape. It retained the audited
four-file atomic contract, selected the experimental-patch route rather than
waiting indefinitely for an upstream merge, used an exact source identity, and
kept an ordinary HiCache request separate from a physical-demotion request.
This is the narrowest useful next question after G0-C-006's fake-resource
oracle: whether the reviewed seam can inhabit a real SGLang package and server
on a frozen CUDA host.

It also correctly treated a CUDA rental as validation of a bounded integration,
not as authorization to begin a performance benchmark or build ToolGap's
lifecycle runtime.

## Extensions required for that steelman to hold

Three independent reviews converged on four additions:

1. **Real package seam.** A treatment wheel must execute
   `UnifiedRadixCache.checked_demote_session` with a registered test backend.
   The legacy-backend branch must return the real typed unsupported outcome and
   must make zero calls to physical `demote`. Otherwise source-oracle green,
   import, and `/health` still leave the cache-to-backend boundary unexercised.
2. **Reproducible installation.** Source-path imports are not a package
   integration result. Stock and treatment need separately built wheels and
   isolated environments, with interpreter, `sys.path`, imported file paths,
   module hashes, lock, and wheel hashes retained.
3. **A real yet bounded serving observation.** Each arm must run two identical
   native streaming requests whose prompt is verified by the selected tokenizer
   to span at least two 16-token pages. The oracle is HTTP/SSE protocol and
   clean process lifecycle, not response equivalence, demotion, or throughput.
4. **Auditable default-path exclusion.** Before either server starts, a static
   source inventory must establish zero production callers of
   `checked_demote_session` and the one cache-to-backend call site. This is a
   source-level statement, not a claim that the smoke observed physical bypass.

## Adversarial attacks and dispositions

| Credible wrong implementation or claim | Why it fails | v2 disposition |
| --- | --- | --- |
| A fake-resource oracle proves the installed backend seam. | The oracle extracts/stubs methods; it does not invoke the installed cache object. | Add the installed-package seam dry-run. |
| `PYTHONPATH=<source>/python` proves packaging. | It can import unbuilt local source and leak dependencies from the shell. | Build wheels; use clean, separate virtual environments and absolute interpreters. |
| A healthy server proves the patch is harmless. | Startup may never touch the patch, and one short request may not establish an ordinary cache-shaped workload. | Require the seam dry-run plus two page-spanning native requests. |
| The sparse source-audit checkout can start SGLang. | It deliberately lacks the full server entrypoint and packaging context. | Materialize full stock and treatment worktrees; disable sparse checkout. |
| Any runtime failure means `RESHAPE`. | A wrong driver, wheel, host, or missing terminal is not evidence that ownership must widen. | Distinguish blocked-before-execution and execution-failed-after-start from a reviewed Gate decision. |
| Add a dynamic tracing hook to prove the request cannot call the seam. | That introduces another changed runtime mechanism and can itself distort the result. | Use the smaller fixed-source AST inventory; a failed or ambiguous inventory invalidates the attempt. |
| Demand an upstream merge before renting. | It changes a local integration question into an external scheduling dependency. | Keep the fixed experimental patch, clearly labelled as such; a merge is separate evidence. |
| Add the G1 forced-demotion sequence while the host is leased. | It crosses the accepted Gate boundary and turns one failed premise into an unreviewable multi-question experiment. | Explicitly prohibit it. PASS authorizes only a new G1 plan/specification. |

## Synthesis

Adopt the experimental-patch route and a **single successor G0 runtime-
integration contract**, but not a physical-demote run. Its evidence chain is:

```text
full fixed source + reviewed patch
  -> stock RED / treatment GREEN source oracle
  -> isolated stock/treatment wheels with recorded provenance
  -> treatment installed cache-to-backend dry-run (no physical demote)
  -> paired native HiCache startup and ordinary request protocol smoke
```

Each arrow closes a distinct failure mode. Removing any one makes a plausible
wrong result look successful; adding allocator observation, real demotion,
recovery, or benchmarking would ask G1-or-later questions.

The detailed executable contract is v2. It is still a proposed worklog plan:
no source pin, wheel, CUDA observation, or Gate result has been created by this
review.

## Canonical follow-up

- A future accepted implementation creates and freezes
  `experiments/g0/SPEC.g0-c-007.md` and its manifest before either runtime arm.
- The owner must update canonical experiment and decision records only after a
  retained run supports a reviewed Gate decision.
- G1 stays blocked under [`docs/ROADMAP.md`](../../../docs/ROADMAP.md).
