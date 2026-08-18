# G0 Host mode selection

Selected mode for the next admissible runtime specification: `write_through`.

This is a source-semantic selection, not a runtime result.

## Why this mode

In the fixed source, write-through backup allocates Host slots, submits D2H,
commits Host indices, and marks the node pending at
[`unified_radix_cache.py#L925-L948`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_radix_cache.py#L925-L948).
The D2H controller ack carries a `finish_event` at
[`cache_controller.py#L693-L733`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/managers/cache_controller.py#L693-L733).
`writing_check` synchronizes that event before finishing the write-through ack
at
[`unified_radix_cache.py#L1880-L1919`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_radix_cache.py#L1880-L1919).
Only the finish step clears `write_through_pending_id` and updates duplicate
tracking at
[`unified_tree_core.py#L2004-L2018`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L2004-L2018).

The authoritative G0 committed-copy predicate is therefore the source's
settled Full Host duplicate:

```text
Full device value present
and Full Host value present
and write_through_pending_id is None
and load_back_pending_id is None
```

The predicate is implemented at
[`unified_tree_core.py#L1163-L1173`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py#L1163-L1173).

## Rejected shortcuts

- `host_value is not None` or `backuped` alone: Host metadata is published
  before the D2H completion event.
- `write_back`: its stock eviction flow couples backup and immediate demotion;
  it is not the clean publication-plus-later-action baseline required by G3.
- `write_through_selective`: threshold-dependent publication adds an unrelated
  eligibility variable to the first proof slice.

No model was loaded and no GPU was used. The mode choice only freezes the
semantic branch for a later CUDA-capable runtime SPEC after G0 RESHAPE is
resolved.
