# Confirmed `setsid` PGID before group cleanup

> Canonical owner: `experiments/g1/SPEC.g1-preflight-001.md`

The preflight runner originally read and stored the smoke process group
immediately after backgrounding `setsid`. Before `setsid()` runs, that child
briefly has the runner's process group. An error trap could therefore send a
negative-PGID signal to the runner or SSH session itself.

The runner now waits at most ten seconds to observe `PGID == child PID` before
recording a cleanup group. Until that condition holds, emergency cleanup may
only signal the known child PID. This preserves the existing three-part
quiescence contract without widening the runtime scope.
