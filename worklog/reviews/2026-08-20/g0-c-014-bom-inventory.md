# G0-C-014 BOM-safe inventory review

Canonical owner: `docs/DECISIONS.md` D028 and
`experiments/g0/SPEC.g0-c-014.md`.

G0-C-013/001 proved the intended stock RED, treatment GREEN, and installed
seam before the inventory failed on the first byte of an unrelated upstream
Python file. Skipping that file or ignoring parse errors would weaken the
full-tree claim. Retrying 013 after changing its shared helper would rewrite a
frozen protocol.

The accepted minimum is a successor-specific inventory that reads every
`*.py` file with `utf-8-sig`. That codec removes an optional leading UTF-8 BOM
and otherwise behaves as UTF-8. All AST traversal and exact call-site
assertions remain unchanged.
