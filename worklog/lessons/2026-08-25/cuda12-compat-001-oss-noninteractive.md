# CUDA12-COMPAT-001 OSS retry input handling

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

When a partial versioned raw prefix was retried, an interactive `ossutil cp`
overwrite prompt consumed the surrounding artifact-plan standard input and
aborted the anchor. The same loop structure existed in input staging. Every
anchor and staging upload must use `ossutil -f cp` with standard input closed;
the successful retry records the newly created object versions in its receipt
or external anchor.
