# CUDA12-COMPAT-001 noninteractive OSS anchor upload

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

An interrupted operator upload left a partial raw prefix. On retry, `ossutil
cp` prompted for overwrite while consuming the loop's artifact-plan standard
input, which invalidated the next plan row before an external anchor could be
written.

Make every anchor and input-staging upload noninteractive with `ossutil -f cp`
and detach its standard input from the artifact plan. Preserve an existing
versioned prefix and write new object versions; the final receipt or anchor
will bind the versions produced by the successful retry. Add static checks for
all four anchor and both staging upload sites.
