# G1-C-007 scripted module identity

Canonical successor: `experiments/g1/SPEC.g1-c-008.md`.

The C-007 main-guard regression proved only that a spawn child did not execute
the arm runner's `main()` again. It did not prove that a selected callable's
`__module__` was importable. Formal attempt
`g1-c-007-a1-20260825T042407Z` falsified that assumption when the enabled arm's
scheduler-hook executor tried to import `g1_c_007_scripted` and recorded a
`ModuleNotFoundError` at `2026-08-25 12:30:51 CST`. The attempt had not sealed a
terminal state when C-008 implementation began.

C-008 keeps the main guard and adds the missing identity contract: import the
scripted test under its real filename stem from a parent `sys.path` inherited
by spawn children. Its focused regression passes a real module-level callable
through spawn and has the child import and resolve the callable from
`__module__`.
