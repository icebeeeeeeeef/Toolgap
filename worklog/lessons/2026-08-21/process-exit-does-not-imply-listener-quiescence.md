# Process exit does not imply listener quiescence

Canonical owner: `experiments/g0/SPEC.g0-c-017.md`.

G0-C-016/002 falsified the assumption that an empty process-group snapshot
means the target listening socket is already absent. Cleanup success must be a
joint observation of the process group, target listener, and attributable GPU
PIDs within one bounded deadline; a later ad hoc probe cannot rewrite an
immutable failed receipt.
