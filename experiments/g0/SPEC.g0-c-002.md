# G0-C Checked-Admission Contract Specification

> Status: `roadmap`
>
> Specification state: `frozen`
>
> Revision: `G0-C-ADMISSION-002`
>
> Run identity: `g0-c-checked-admission-002`
>
> Frozen at: `2026-08-17T15:35:25Z`
>
> Claim ceiling: fixed-source checked-admission contract evidence only; no
> stock-runtime success, physical demotion, allocator, lifecycle, or performance
> claim

## 1. Correction and authority

This immutable revision corrects two independent defects found by fresh-context
review of `G0-C-SEAM-001`:

1. the first successor SPEC left model/runtime fields `N/A` although the parent
   requires exact successor configuration and a stock command;
2. its one-file tracker patch did not cover the maintained TreeCore admission
   interface, so it could not prove that exactly one vertical upstream contract
   was missing.

`G0-C-SEAM-001`, its manifest, RED, GREEN, and patch are preserved as an invalid
protocol attempt with informative tracker evidence. They are not decisive Gate
evidence. This revision does not overwrite either frozen predecessor.

The decisive question is narrower than a physical executor:

> Can one upstream `session checked-admission` contract synchronously combine
> current-generation target frontier snapshot/non-terminal priority release
> with backend-owned live eligibility checks, while leaving actual physical
> demotion at the already-existing `TreeCoreInterface.demote` seam?

## 2. Fixed identities

| Field | Frozen value |
|---|---|
| Upstream | `https://github.com/sgl-project/sglang.git` |
| SGLang commit | `92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2` |
| SGLang tree | `25e9bf86d04c27fe380024d9c8c421c3b5b51f3c` |
| Stock checkout | `/private/tmp/toolgap-kv-g0-sglang-92b1d382` |
| Patched checkout | `/private/tmp/toolgap-kv-g0-sglang-admission-prototype` |
| Model | `Qwen/Qwen2.5-0.5B-Instruct` |
| Model revision | `c89bee90d9f811437d9735454613c35b4a3c4dc8` |
| Tokenizer | same repository and revision as model |
| Model revision source | `https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/tree/c89bee90d9f811437d9735454613c35b4a3c4dc8` |
| Dependency source | fixed `python/pyproject.toml`, SHA-256 `c4d204a1d24f7ba87a150e0d563d8b946fd94c989c4e92985d488e088d424446` |
| Critical declared versions | Python `3.12.11`; Torch `2.13.0`; Transformers `5.12.1`; CUDA family `13.x` from the fixed metadata |

The upstream project has no retained full resolver lock in this sparse checkout;
therefore a successful stock smoke cannot be claimed until an actual environment
freeze supplies the complete resolved dependency readback. That is recorded as
a stock-smoke admission blocker, not hidden by using `latest`.

## 3. Exact stock single-node HiCache command

Declared runtime target, if provisioned:

| Field | Frozen value |
|---|---|
| Host OS | Ubuntu 24.04.3 LTS, x86_64 |
| GPU | one NVIDIA A10 24 GB at CUDA device 0 |
| Driver/runtime | NVIDIA driver `580.65.06`; CUDA `13.0` |
| TreeCore backend | `python` |
| Host mode | `write_through` |
| Dtype / KV dtype | `bfloat16` / `bfloat16` |
| Page size | `16` tokens |
| Context limit | `4096` tokens |
| Maximum KV tokens | `4096` |
| Static memory fraction | `0.70` |
| Host/device cache ratio | `2.0` |
| HiCache I/O / layout | `kernel` / `page_first` |
| TP / DP | `1` / `1` |
| Scheduler / seed | `fcfs` / `20260817` |
| Bind | `127.0.0.1:30000` |
| L3/storage | disabled; no storage backend flag |
| Session tracking | enabled; streaming session mode disabled |

Exact launch command:

```bash
CUDA_VISIBLE_DEVICES=0 \
SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python \
python3.12 -m sglang.launch_server \
  --model-path Qwen/Qwen2.5-0.5B-Instruct \
  --revision c89bee90d9f811437d9735454613c35b4a3c4dc8 \
  --tokenizer-path Qwen/Qwen2.5-0.5B-Instruct \
  --dtype bfloat16 \
  --kv-cache-dtype bfloat16 \
  --context-length 4096 \
  --page-size 16 \
  --max-total-tokens 4096 \
  --mem-fraction-static 0.70 \
  --tp-size 1 \
  --dp-size 1 \
  --schedule-policy fcfs \
  --random-seed 20260817 \
  --enable-hierarchical-cache \
  --hicache-ratio 2.0 \
  --hicache-write-policy write_through \
  --hicache-io-backend kernel \
  --hicache-mem-layout page_first \
  --enable-session-radix-cache \
  --host 127.0.0.1 \
  --port 30000
```

Required readbacks before classifying a smoke as started:

```text
uname -a
nvidia-smi --query-gpu=name,uuid,driver_version,memory.total --format=csv,noheader
python3.12 --version
python3.12 -c 'import torch, transformers, sglang; print(...)'
git rev-parse HEAD and HEAD^{tree}
pip freeze or equivalent complete resolved dependency lock
server resolved arguments / server-info output
```

The observed local host is macOS 15.7.4 arm64, has no `nvidia-smi`, no
`python3.12` command, and no installed SGLang/Torch environment. The frozen
stock command is recorded but is not executed. Its attempt classification is
`blocked before execution`; it is not a smoke success or a G0 blocker that can
be reworded as PASS.

## 4. One vertical missing contract

The proposed upstream surface is one cache-level operation:

```python
UnifiedRadixCache.prepare_session_checked_demote(session_id, generation)
    -> SessionCheckedAdmission
```

Its internal implementation may span tracker, TreeCore interface, and Python
TreeCore, but callers receive one contract:

1. validate generation and snapshot current target frontiers before mutation;
2. release only target session priority contributions without close/tombstone;
3. ask the registered TreeCore backend, through its maintained interface, for a
   live per-node admission result;
4. return immutable admitted/rejected NodeIds and finite reasons;
5. do not invoke physical demotion.

The backend-owned check must cover Full-only component scope, target provenance,
remaining session coverage, settled Host duplicate, device-leaf state, every
device lock, both pending IDs, resumable insert, active eviction walk, and
cascade scope. The operation is synchronous on the scheduler thread; G1 must
consume admitted IDs without yielding and use the existing `demote`/free-drain
seam. Full lifecycle and asynchronous fencing remain G2 work.

## 5. Executable counterexample oracle

The test must fail on untouched stock because the single cache-level contract
is absent. After applying the retained patch to a separate exact-pin worktree,
the same test must exercise the patched admission code through an extracted
source method and a fake registered backend; it may never import or call a real
physical executor.

Required cases:

| Case | Required oracle |
|---|---|
| stock surface absent | expected RED naming `prepare_session_checked_demote` |
| current target, settled Full-only leaf | admitted by fake seam; no real demote call |
| write-through pending only | rejected/deferred |
| load-back pending only | rejected/deferred |
| non-target `session_ref` remains | rejected |
| device child added after snapshot | rejected as not current D-leaf |
| device component lock only | rejected |
| resumable insert only | rejected |
| eviction walk only | rejected |
| SWA/Mamba component present | rejected before cascade |
| stale generation | no release and rejected |
| cleanup model: drain succeeds | one owner, one terminal success |
| cleanup model: either drain branch raises | no success; each returned resource remains owned exactly once |

The cleanup rows are an oracle model for the future cache drain, not an
implementation of physical demotion.

## 6. Commands and artifacts

Decisive RED command:

```bash
/opt/homebrew/bin/python3 \
  toolgap/experiments/g0/artifacts/test_checked_admission_contract.py \
  --checkout /private/tmp/toolgap-kv-g0-sglang-92b1d382
```

Decisive GREEN command:

```bash
/opt/homebrew/bin/python3 \
  toolgap/experiments/g0/artifacts/test_checked_admission_contract.py \
  --checkout /private/tmp/toolgap-kv-g0-sglang-admission-prototype
```

Required artifacts:

- `manifest.g0-c-002.json`;
- `commands/10-stock-hicache-smoke.sh`;
- `artifacts/g0-c-002-runtime-readbacks.txt`;
- `artifacts/test_checked_admission_contract.py`;
- `artifacts/sglang-session-checked-admission.patch`;
- `artifacts/g0-c-002-red.txt`;
- `artifacts/g0-c-002-green.txt`;
- `artifacts/g0-c-002-patched-identity.txt`;
- updated counterexample matrix and final review record.

## 7. Decision boundary

- `PASS` remains impossible on this stock pin because the contract is absent.
- `RESHAPE` is allowed only if the complete vertical contract is represented by
  the retained patch, the stock RED is specific, every executable
  counterexample passes after the patch, and no second ownership index appears.
- `STOP` applies if the maintained backend interface cannot express the checks
  without concrete-core access, broad backend replacement, or a second physical
  ownership system.

Any change to the command, source, model revision, admission fields, test cases,
or branch creates a new revision. This file is immutable after its checksum is
recorded in `manifest.g0-c-002.json`.
