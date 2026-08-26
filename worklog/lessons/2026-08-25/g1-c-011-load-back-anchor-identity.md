# G1-C-011 load-back anchor identity

Canonical owners:
`experiments/g1/SPEC.g1-c-011.md` and `experiments/g1/SPEC.g1-c-012.md`.

## Falsified assumption

G1-C-011 assumed that replaying the exact reconstructed session frontier would
make the existing frontier leaf the load-back anchor. The frozen attempt
`g1-c-011-a1-20260825T113123Z` falsified this: its
`reject_load_back_pending` arm completed the loader without observing pending
state and the sealed terminal classification is `INVALID`.

Preserved raw-evidence prefix:
`oss://agentic-kv-c0-evidence-20260812/g1/g1-c-011/3b61f49/raw/`.
The externally read-back `INVALID` anchor is
`oss://agentic-kv-c0-evidence-20260812/g1/g1-c-011/3b61f49/anchors/g1-c-011-a1-20260825T113123Z/external-anchor-26925a11c91dc8d4871544696b4a349bf05dc9a110c33409bb7439ad84ec7d25.json`,
version
`CAEQnAYYgYDAi9Ws44EaIiA2NjdlYzBkOGFhZWE0OTFhOWM3NzVjNzIyODIzOGEyYw--`,
SHA-256 `26925a11c91dc8d4871544696b4a349bf05dc9a110c33409bb7439ad84ec7d25`.
It binds 170 indexed artifacts against 172 raw objects with
`gate_decision=INVALID`.

## Root cause

Pinned SGLang caps radix matching at `input_len - 1`. Exact frontier replay
therefore split the session leaf; the new parent became the real load-back
anchor while the fixture continued observing the original child NodeId. The
failure was a fixture identity error, not evidence that the production guard
was absent or that G1 passed or failed.

## Correction

G1-C-012 appends one valid token to the loader input so the capped match covers
the complete frontier leaf. The fixture must additionally prove that the
observed target NodeId equals `load_back_pending_id` and is present in
`ongoing_load_back`. Removing the appended suffix is retained as a
counterexample that restores the invalid C-011 shape.
