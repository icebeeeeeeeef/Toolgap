# Data-plane scope review — JD-driven capability gap

Canonical owners: D033 in `docs/DECISIONS.md`,
`docs/future/PD_TRANSFER_SLICE.md`, and the future-review pointer in
`docs/ROADMAP.md`.

Decision question: should ToolGap absorb distributed KV-store data-plane
features (large-value slicing with concurrent multi-node I/O, zero-copy/GDR,
small-object coalescing for PD KV transfer, end-to-end iterative CRC) to close
a job-description capability gap, given a rented-machine budget of at most
five hosts?

Decision: no mainline expansion. The cited feature set is a mature store's
published data plane; rebuilding it inside ToolGap violates the ownership
boundary and dilutes the narrow checked-demotion contract. The three
capabilities were split by evidence gap instead:

1. integrity verification → page-level checksum round-trip recorded as an
   admissible G1/G2 instrument option (not a requirement, not a data plane);
2. small-transfer coalescing / pinned-buffer work → remains the existing
   symptom-triggered performance-diagnosis path after G0-G2, not a new Gate;
3. slicing + concurrent channels + PD transfer → admitted only as a separate
   future review (`docs/future/PD_TRANSFER_SLICE.md`), gated on a real G1
   physical-demotion PASS, on a reused transport, with a hardware-honesty
   claim contract; two or three machines suffice.

Rejected alternatives: mainline absorption; starting the PD extension before
G1; RDMA/GDR claim language without RDMA hardware; making the checksum a
mandatory G2 artifact. Budget priority is G1-G4 real-GPU execution.

All claims remain `roadmap`; no experimental evidence was created.
