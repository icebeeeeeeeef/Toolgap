# Fixed-source index

All entries are from SGLang commit
`92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2`, tree
`25e9bf86d04c27fe380024d9c8c421c3b5b51f3c`.

| Source | SHA-256 | Audit role |
|---|---|---|
| [`session_ref_tracker.py`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py) | `21353af6b20585132b65e3952dc5ce3f2450780db1fd8d0d809e184d3fb37007` | generation, tombstone, terminal release |
| [`tree_component.py`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/components/tree_component.py) | `e79eab56f3803fa81181cfa4d6a42d7aeba95b5d89a1420195c4003483bbad0e` | frontier index, per-component fields and session release |
| [`full_component.py`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/components/full_component.py) | `edf7ff730f81db8d2d322d54329f74953175cba5745ed55ab6e5d24115706d66` | Full path coverage, eviction order, locks and allocator drain |
| [`unified_tree_core.py`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py) | `2b66bd6c8105c12d8b57b5d6c1abd3a87136bfaf0524fd9606c7746c81327aed` | leaf/pending/cascade/demote implementation |
| [`unified_tree_core_interface.py`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_cache/unified_tree_core_interface.py) | `cbffb202a3a4bc2e91b184c19551ff1a310eaebdf70fb8fe93e52c5ac8c3f9a5` | supported Controller-to-TreeCore physical seam |
| [`unified_radix_cache.py`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/unified_radix_cache.py) | `6e29ffa01adb96c9d400331850fe60b054cd83c980f033d36552e369a5d5c6ce` | Host ack processing, free drain, cache facade |
| [`cache_controller.py`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/managers/cache_controller.py) | `3f323c0b08acb8b1de6f3ff8c08f1ed34d508afd186ae61d370f4e1087d89974` | D2H/H2D submission and completion events |
| [`allocator/base.py`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/allocator/base.py) | `bef214db92cd02170caa825fe2880c59a441d9b606868e60fc38ead2b140ab5e` | allocator-visible availability |
| [`allocator/token.py`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/sglang/srt/mem_cache/allocator/token.py) | `07372fc82e58c58ff9fa749aa6573b0b1c9d7eb59d5e8c779c3b198a4da4370e` | actual free-list mutation |
| [`test_session_unified_radix_cache.py`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/test/registered/unit/mem_cache/test_session_unified_radix_cache.py) | `460ff70d98a9d8687b545387274be1222e6f8361da7ed21687499d1f34b3cdb4` | terminal-release and priority behavior tests |
| [`test_unified_radix_cache_unittest.py`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/test/registered/unit/mem_cache/test_unified_radix_cache_unittest.py) | `d869d6ecc147bcebf96bacb6a1e50a5dad440eb4e2d599cfef8c1619f6393b1a` | demotion, pending transfer, cascade and drain tests |
| [`python/pyproject.toml`](https://github.com/sgl-project/sglang/blob/92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2/python/pyproject.toml) | `c4d204a1d24f7ba87a150e0d563d8b946fd94c989c4e92985d488e088d424446` | dependency/runtime identity (`requires-python >=3.10`) |

The local checkout path is an acquisition cache, not a second source of truth.
The immutable commit links and hashes above make every cited file independently
checkable.
