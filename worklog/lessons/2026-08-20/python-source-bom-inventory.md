# Python source inventories must accept a legal UTF-8 BOM

Canonical owner: `experiments/g0/SPEC.g0-c-014.md`.

The frozen SGLang tree contains `qwen2_classification.py` with a leading UTF-8
BOM. `Path.read_text(encoding="utf-8")` preserves U+FEFF and `ast.parse`
rejects it, even though Python itself accepts the file. Full-tree source tools
must use `utf-8-sig` when they intend to mirror Python source decoding; they
must not skip the file or suppress syntax errors.
