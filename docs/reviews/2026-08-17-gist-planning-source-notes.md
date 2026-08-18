# Gist 规划来源与吸收审查

> 性质：`research input`，不是 canonical roadmap，不改变 Gate 顺序、
> decision status 或 project claim state。
>
> 读取日期：2026-08-17（Asia/Shanghai）
>
> 来源：[Gist 页面](https://gist.github.com/icebeeeeeeeef/3af909a9f3dac42fedfb9b23a8493b50)；
> [固定 raw revision](https://gist.githubusercontent.com/icebeeeeeeeef/3af909a9f3dac42fedfb9b23a8493b50/raw/93aeea9112761d269329ed2c71e59708c757ef91/markdown-document.md)
>
> 读取范围：GitHub API 返回的固定 `raw_url`（路径标识
> `93aeea9112761d269329ed2c71e59708c757ef91`）中的 `markdown-document.md`
> 全文 961 行、67,196 字节。API `history[0].version` 为
> `f1580e764ee0ff0049db8b32e57d6fa5844c94e3`；它与 `raw_url` 路径标识是
> 两个不同的元数据字段，本文件不把二者混写成同一个 revision。

## 1. Evidence boundary

Gist 是项目规划的演化记录，不是代码、测试、源码审计或实验结果。正文中
“已核验”“已实现”“已写入报告”等表述只证明对话里出现过这些结论；除非当前
仓库存在对应 artifact，否则不能据此升级为 `shipped`、
`experimentally validated` 或 `simulated`。

Gist 中的 `1202 lines` 和 `142 lines` 是未展开附件标记。本次没有读取这些附件
正文，因此不从行数推断其内容。

当前技术和执行 authority 仍按以下顺序处理：

```text
PROJECT
-> ARCHITECTURE
-> DEMOTION_CONTRACT
-> ROADMAP
-> EVALUATION + evidence SOP
-> DECISIONS
-> gate-local artifacts
```

## 2. Overall verdict

**不应把 Gist 整体迁入当前规划。** 它前半段包含后来被明确否决的宽方案，后半段
最有价值的结论已经进入 canonical 文档。整段复制会产生第二份 roadmap，并重新
引入 Mooncake、prefetch、mock-first、大网格和强制优化等已被收窄的范围。

Gist 的正确用途是：

1. 保存项目如何被对抗审查逐步收窄的 decision provenance；
2. 检查 canonical 文档是否遗漏最终裁决；
3. 曾为 D0 owner review 提供历史理由，但不能替代 owner acceptance；当前
   acceptance 由 D020 单独记录。

## 3. Planning evolution

### Stage A — early broad proposal

早期方案把以下内容放进同一个项目：

- SGLang + HiCache + Mooncake/L3；
- active demotion + proactive prefetch；
- epoch lifecycle；
- tool/workflow prediction；
- broad performance sweep；
- mandatory performance-optimization pass。

该版本的优点是暴露了 runtime ownership、failure recovery 和 physical
measurement 的重要性；缺点是多个机制可以独立成功或失败，不满足 one causal
question。

### Stage B — mechanism and baseline correction

对抗审查把核心问题改为：

- 分开 Publication、session-priority release 和 checked reclamation；
- demotion 与 proactive prefetch 解耦；
- 增加最强简单 baseline：release target session priority + stock eviction；
- 从实测 KV pool 和 realized pressure 派生实验点；
- 用 removal/bypass test 判断 candidate ownership。

### Stage C — policy correction

策略讨论从“value-density score + workflow index”收窄为：

```text
correctness/execution -> prediction -> cost -> decision
```

安全过滤定义合法动作集合；prediction 和 cost 不能授权不安全动作。B0/B1/B2/O*
与 discrete hazard 被保留为 G5 的条件设计；Workflow Automaton、cross-session
future-hit valuation 和 prefetch 被移出主线。

### Stage D — execution correction

最终 v1 接受最小推进原则：

```text
source-grounded counterexample
-> real quiescent forced-demotion vertical slice
-> deterministic lifecycle race/failure tests on the real seam
-> strongest-simple-baseline comparison
-> sentinel-derived performance boundary
-> policy only if G5 admits it
```

Mock、property-based model 和形式验证只在真实测试暴露具体覆盖缺口时加入；性能
优化只在稳定症状、candidate-owned seam 和最小区分实验同时存在时触发。

## 4. Absorption matrix

| Gist final finding | Current canonical owner | Verdict |
|---|---|---|
| Fixed SGLang version and one narrow lifecycle question | `PROJECT.md`, `ARCHITECTURE.md` | absorbed |
| Candidate owns logical lifecycle/checked execution; SGLang owns physical data plane | `PROJECT.md`, `ARCHITECTURE.md` | absorbed |
| Host-tier-only unconditional mainline | `PROJECT.md`, D002/D007 | absorbed |
| Publication/release/reclamation are distinct | `DEMOTION_CONTRACT.md` | absorbed |
| Generation/operation identity, final eligibility, stale completion and cleanup | `ARCHITECTURE.md`, `DEMOTION_CONTRACT.md` | absorbed |
| Shared-prefix non-target protection and cascade safety | `DEMOTION_CONTRACT.md`, G0 SPEC | absorbed |
| Removal/bypass test decides ownership | `PROJECT.md`, ROADMAP G0/G1 | absorbed |
| Release-only + stock eviction is the strongest simple baseline | `EVALUATION.md`, ROADMAP G3 | absorbed |
| Joint resumed/foreground SLO is the endpoint; headroom is a mediator | `EVALUATION.md`, ROADMAP G3/G4 | absorbed |
| Capacity and workload points come from measured sentinels | `EVALUATION.md`, ROADMAP G3/G4 | absorbed |
| G1 is a quiescent real-engine vertical slice; G2 owns interleavings | ROADMAP G1/G2, D018 | absorbed |
| Policy four-layer design and B0/B1/B2/O* are conditional on G5 | `POLICY.md`, ROADMAP G5 | documented, not authorized |
| TraceLab is client-side calibration, not server residency/cost truth | `EVALUATION.md`, `RELATED_WORK.md` | documented, optional |
| Prefetch needs independent signal/slack/executor review | `future/PREFETCH_ADMISSION.md` | separated, not authorized |
| Performance work is symptom-triggered, not a mandatory story patch | ROADMAP conditional diagnosis, `PERFORMANCE_ENGINEERING.md` | absorbed |
| Prior art changes attribution/baselines before scope | `RELATED_WORK.md`, selection SOP | absorbed |
| Project remains one-substrate engineering closure, not universal method | `PROJECT.md`, `CAREER_VALUE.md` | absorbed |

## 5. Content that must not be re-imported

- Mooncake/L3 as an unconditional dependency;
- proactive prefetch coupled to checked demotion;
- KEEP/DEMOTE/PREFETCH packed into one score or one success criterion;
- Workflow Automaton or cross-session future-hit valuation in G0-G4;
- a prior-art-reading Gate or novelty kill gate;
- precommitted 216/36-point grids, fixed context/concurrency combinations, or
  a fixed seed count before the comparison SPEC is frozen;
- mock transfer, random interleaving counts, TLA+, or a replacement radix model
  before a real seam exposes a concrete coverage problem;
- B0/B1/B2/O* in the G3 mechanism comparison;
- a mandatory bottleneck/optimization patch for recruiting narrative;
- the 14+1 node plan, P0-P9, or any other second global roadmap;
- unqualified “upstream blank”, “first”, “no prior art”, or cross-engine
  generalization claims;
- hypothetical percentages, zero-leak statements, completion verbs, or resume
  bullets without matching artifacts。

## 6. Small remaining supplementation candidates

### Candidate 1 — substrate-choice interview defense (applied)

The Gist contains a useful challenge that is not explicit in
`CAREER_VALUE.md`: “Why SGLang instead of vLLM?”

The version-safe answer shape has been added to `CAREER_VALUE.md`, and D001's
reason/reopen condition now states the same selection criterion:

> Select the engine by whether a fixed source revision offers the smallest
> maintainable seam for the owned contract, not by ecosystem maturity alone.
> D001 is reopened if G0 cannot prove that seam or a newly audited alternative
> offers a materially narrower owned path.

This documentation supplement did not itself accept D001 or freeze G0. D001 is
now accepted through D020's owner-approved D0 closure; the G0 SPEC remains
draft and not executable. Do not import the Gist's detailed negative vLLM
claims without a fresh, version-matched audit, and do not add a vLLM comparison
Gate to G0.

### Candidate 2 — preserve the final anti-overdesign decision packet

The final Gist rulings are useful historical reasons for D017-D019 and the
owner-approved D001-D016 packet, but the current documents already encode the
resulting behavior and D020 records D0 closure. No new architecture or roadmap
document is needed.

### Candidate 3 — real RCA only after the first anomaly

The Gist's “difficulty story should come from a real RCA” is already represented
by D016 and `PERFORMANCE_ENGINEERING.md`. Do not create an empty casebook. When
the first admitted anomaly exceeds a Gate-local RESULTS entry, create one RCA
artifact from the existing template fields.

## 7. Recommended action

1. Keep this file in `reviews/` as non-canonical provenance.
2. Do not modify `PROJECT.md`, `ROADMAP.md`, `EVALUATION.md`, `POLICY.md`, or
   `PREFETCH_ADMISSION.md` from the Gist; the final valid rulings are already
   present.
3. Keep the applied Candidate 1 wording version-bound; D001 is `accepted`
   through D020, while the project claim remains `roadmap`.
4. D0 is closed; complete and freeze the G0 SPEC before any G0 source or runtime
   attempt.
5. The next legal action remains G0 source/config freeze and the
   session-to-leaf/counterexample audit—not policy, prefetch, Mooncake, broad
   profiling, or a performance grid.

## 8. Claim boundary

The current project remains `roadmap`. This review establishes only that the
Gist's final planning corrections are largely represented in current documents.
It does not establish runtime implementation, correctness, physical reclamation,
GPU measurements, performance value, policy value, or prefetch value.
