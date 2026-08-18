# G1 candidate-removal and bypass test

Status: design only; G1 remains blocked by G0 `RESHAPE`.

## Claim to distinguish

Candidate checked demotion, not publication or eventual stock eviction, causes
an immediate target-scoped physical action and earlier allocator-visible
headroom.

## Frozen comparison shape for the future G1 SPEC

Both arms must use the same fixed upstream revision, model/configuration,
`write_through` publication, committed Host copy, target session-priority
release, workload, and instrumentation.

| Arm | Candidate resolver/executor | Stock eviction | Required observation |
|---|---|---|---|
| candidate enabled | checked facade runs after the forced internal trigger | enabled | target node admitted/demoted, exact frees drained, allocator headroom changes after terminal return |
| candidate bypassed | intent is recorded but resolver/executor is not called | enabled | no immediate candidate demote or candidate operation result; ordinary requests continue; eventual stock eviction remains possible |

Disabling only instrumentation is a separate negative control and must not
change behavior.

## Counterexample oracle

The candidate claim fails if any of these hold:

1. bypass produces the same immediate demote call;
2. allocator availability changes in both arms before any physical free drain;
3. only session priority/logical bookkeeping changes while physical free IDs
   and allocator capacity do not;
4. bypass disables ordinary stock eviction or changes request semantics;
5. the candidate arm observes only requested/offered tokens rather than exact
   upstream frees and allocator state.

The future test must capture the linearized sequence:

```text
Host commit ack
-> target priority release
-> forced internal candidate trigger (or bypass)
-> checked admission
-> physical demote result
-> exactly-once free drain
-> allocator available-size sample
```

Time-to-headroom is measured from the forced trigger to the first post-drain
allocator sample. It is not measured in G0.

## Ownership deletion test

Delete or bypass these candidate responsibilities together:

- target intent admission;
- session-to-leaf safe resolution;
- immediate checked physical invocation.

Keep upstream publication, target-only priority release, physical cache,
allocator, stock eviction, and evidence taps. If the immediate action survives
this deletion, ownership attribution is wrong and G1 cannot PASS.
