# G0-C-007: verify executable terminals, not narrative shorthand

> Date: 2026-08-19
>
> Claim state: roadmap

## Trigger

The implementation initially treated the retained v6 oracle's expected outcome
as literal output text saying 27 failures or 27 passes and supplied a
source-root argument. Direct inspection of the executable showed a different
contract: it accepts a checkout argument and emits unittest terminals, namely
Ran 27 tests, FAILED (failures=27), or OK.

## Correction

Commands 21 and 23 now assert the oracle's real argument and terminal
structure. The frozen plan and SPEC retain the semantic requirement of stock
RED and treatment GREEN, but the runner checks the executable's observable
protocol rather than an informal summary.

## Rule for future agents

Before encoding a frozen tool's expected terminal into automation, inspect its
argument parser and success/failure output. A review summary may state the
right conclusion while still being the wrong interface contract.
