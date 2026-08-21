# G0-C-015 Ninja prerequisite review

Canonical owner: `docs/DECISIONS.md` D029 and
`experiments/g0/SPEC.g0-c-015.md`.

The stock server loaded the fixed model and allocated the fixed KV cache before
FlashInfer's CUDA JIT failed to execute `ninja`. Changing attention backends or
disabling prefill CUDA graphs would change the frozen runtime path. Installing
`ninja` manually without admission would make the environment irreproducible.

The accepted minimum is Ubuntu's ordinary `ninja-build` package, installed by
the existing project-prerequisite command and checked/versioned by preflight.
It is not GPU infrastructure and does not change the experimental mechanism.
