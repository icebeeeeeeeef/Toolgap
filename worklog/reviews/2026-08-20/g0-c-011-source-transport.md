# G0-C-011 source transport review

Canonical owner: `docs/DECISIONS.md` D025 and
`experiments/g0/SPEC.g0-c-011.md`.

The strongest case for retaining live GitHub clones was provenance simplicity:
both arms would originate directly from the canonical remote. Two independently
sealed 010 attempts instead showed that this incidental network path could stop
the experiment before any arm. Retrying, mirroring, or adding a proxy would
test infrastructure rather than the G0 question.

The accepted minimum is one operator-staged Git seed whose transport bytes are
SHA-256-bound and whose scientific identity is still proved by canonical
remote, commit, tree, clean worktrees, and the unchanged patch. No other
environment or experimental input changes.
