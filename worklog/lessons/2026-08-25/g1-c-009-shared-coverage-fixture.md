# G1-C-009 shared coverage and rejection oracle

Canonical successor: `experiments/g1/SPEC.g1-c-009.md`.

C-008 formal attempt `g1-c-008-a1-20260825T053604Z` sealed
`pre_execution INVALID` at `formal_arms`, exit `1`, after three complete arm
records. Enabled and bypass passed. The fourth arm reached
`_script_non_target_coverage` but its two session-native requests produced
distinct private frontiers `(21,)` and `(24,)`, falsifying the fixture's
same-node assumption before the intended rejection was exercised.

C-009 retains the first ordinary request's real settled Full node and uses
SGLang's existing session-generation and `register_session_leaf` APIs to add
only the second session's logical coverage to that node. This is a deterministic
negative fixture; it does not construct or mutate the tree, KV values, allocator,
or positive enabled/bypass state.

The same attempt's write-through record falsified the offline oracle's reason
placement. Patch 0001 aggregates a fully deferred checked request as facade
`DEFERRED/DEFERRED`; the concrete `WRITE_THROUGH_PENDING`,
`NON_TARGET_SESSION_COVERAGE`, or `DEVICE_LOCKED` reason is carried by each
node outcome. Stale generation is different: it returns facade
`REJECTED/STALE_GENERATION` before any backend outcome. C-009 replays these
source-owned mappings exactly instead of moving node reasons onto the facade.
