# G0-C-016 shutdown capture review

Canonical owner: `docs/DECISIONS.md` D030 and
`experiments/g0/SPEC.g0-c-016.md`.

015/001 reached stock health and completed both requests. Its 137 followed the
runner's SIGTERM and SGLang's logged SIGQUIT/self-kill cleanup; no process,
listener, or attributable GPU PID survived. Treating every 137 as success would
mask OOM or external kills, while requiring 0/143 contradicts the fixed
runtime's observed shutdown behavior.

The accepted minimum ties 137 to a live PID and successful runner-issued TERM,
captures `wait` in a Bash conditional, retains every no-survivor check, and
freezes the same status set in the successor's final evidence verifier.
