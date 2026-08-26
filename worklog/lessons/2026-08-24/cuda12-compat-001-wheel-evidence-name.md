# CUDA12-COMPAT-001 wheel evidence name

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

An immutable evidence artifact may use a stable descriptive filename, but pip
parses a wheel's filename as packaging metadata. `runtime-wheel.whl` therefore
cannot be passed to pip even when its contents are valid. Retain the evidence
copy for sealing and install from the already receipt-bound original wheel
pathname instead.
