# G1-C-008 anchor portability

Canonical owner: `experiments/g1/SPEC.g1-c-008.md`.

C-007's operator anchor failed closed before upload, so it produced no remote
evidence. Two local assumptions were false: Bash 3.2 brace-expanded a Python
set literal inside process substitution, and the anchor's safe artifact-path
regex omitted `+` even though the frozen runtime wheel uses it.

C-008 uses a tuple for terminal membership and explicitly admits `+` in the
otherwise unchanged safe relative-path alphabet. An offline regression seals a
local fixture, executes the real anchor prefix through plan generation under
the host Bash, and requires the `+` runtime wheel in `plan.tsv`; it performs no
OSS operation.
