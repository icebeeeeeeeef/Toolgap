# CUDA12-COMPAT-001 runtime evidence review

Canonical owner: `experiments/g1/SPEC.cuda12-compat-001.md`

Decision-changing findings:

- The CUDA12 resolver must reproduce the pinned Docker route's final package
  normalization: remove package names ending in `-cu13`, then force-reinstall
  the cu129 Torch stack and `sgl-deep-gemm` `0.1.5.post2`.
- Resolver/network failure is not a CUDA runtime conclusion. The compatibility
  probe now distinguishes affirmative transport failure from other dependency
  resolution or source-build failure; only the later Torch CUDA probe may emit
  `RUNTIME_INCOMPATIBLE`.
- All sealed failures require best-effort host/GPU readback, and the two
  externally downloaded bootstrap scripts bind their own bytes to the generated
  input manifest before installation or seed restoration.
- Result retention is a single local operator command that verifies a sealed
  attempt, uploads indexed artifacts, and emits an external OSS version anchor.
  No new cloud permission design is required.

Residual pre-execution condition:

G0 showed public dependency transport from the provider host was unreliable.
The current runner records that condition without mislabeling it as CUDA
incompatibility, but a real CUDA12 compatibility attempt requires either a
validated provider egress path or a frozen Linux wheelhouse staged with the
other OSS inputs. The canonical spec remains `roadmap`; no GPU result exists.
