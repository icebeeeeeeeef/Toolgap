# CUDA12-COMPAT-001 multiprocessing-safe restricted test launcher

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

The r7 attempt passed the CUDA route checks but loaded the sole restricted
startup test through `python -`. That gives a multiprocessing child no real
main-file path, so it fails opening `<stdin>` before a valid SGLang startup.

Generate an immutable runner file in the attempt directory with a private
direct test-module loader and an `if __name__ == "__main__"` guard. Invoke it
through the installed runtime interpreter without adding `TREATMENT/python` to
`PYTHONPATH`. The resulting runner file is indexed with the attempt evidence;
a replacement attempt requires a new frozen ToolGap seed, receipt, and ID.
