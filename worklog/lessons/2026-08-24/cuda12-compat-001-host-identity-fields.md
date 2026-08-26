# CUDA12-COMPAT-001 host identity fields

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

On the first real-host attempt, `nvidia-smi --format=csv` emitted a leading
space before `driver_version`; only the first two fields were normalized, so
the exact-driver assertion failed despite the intended driver being installed.
The same attempt showed that extracting the macOS-created bare seed as root
preserved its archived local UID and triggered Git's ownership protection.

The replacement frozen revision normalizes all three CSV fields and extracts
the validated bare seed with `--no-same-owner`. The original sealed attempt is
retained as `BLOCKED_HOST_IDENTITY`; this correction does not establish a Gate
result.
