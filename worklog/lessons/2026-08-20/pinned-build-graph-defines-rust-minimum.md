# Pinned build graph defines the Rust minimum

Canonical owner: `experiments/g0/RESULTS.md` and
`experiments/g0/SPEC.g0-c-011.md`.

## Trigger

G0-C-011 attempt 001 found provider Rust 1.75 could not parse the pinned
Edition 2024 workspace. Attempt 003 then showed Rust 1.85 could parse that
edition but not the pinned `let-chains` use. Attempt 004 established the real
minimum: the pinned `rustpython-ruff` package declares `rustc >=1.92`.

## Incorrect assumption

The language edition, or the Ubuntu image's default Rust package, was treated
as a sufficient proxy for the fixed source's build compatibility. It was not.
The transitive pinned build graph sets the effective compiler minimum.

## Evidence

The preserved pre-arm environments record Rust 1.75 for attempt 001, Rust 1.85
for attempts 002/003, and Rust 1.88 for attempt 004. Each stopped before either
serving arm and has a verified failure seal. `RESULTS.md` records the exact
compiler failures and the declared `rustc >=1.92` dependency requirement.

## Correction

Treat Rust 1.92 or later as an ordinary project build prerequisite, distinct
from the provider-owned GPU driver/CUDA substrate. Install or stage that
toolchain before an attempt, record exact `cargo` and `rustc` readbacks, and
warm a bounded Cargo cache only outside sealed attempts without changing the
source, dependency lock, or wheel identity.

## Future rule

For a source build, derive toolchain minima from the exact pinned transitive
build graph and prove them with a consuming build. Do not infer compatibility
from a language edition, a package manager's default version, or an earlier
successful parse step.
