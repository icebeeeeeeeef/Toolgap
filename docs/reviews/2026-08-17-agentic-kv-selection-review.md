---
Document role: historical review input
Project claim state: roadmap
Canonical technical sources:
- [PROJECT.md](../PROJECT.md)
- [ARCHITECTURE.md](../ARCHITECTURE.md)
- [DEMOTION_CONTRACT.md](../DEMOTION_CONTRACT.md)
- [POLICY.md](../POLICY.md)
- [EVALUATION.md](../EVALUATION.md)
- [ROADMAP.md](../ROADMAP.md)
- [DECISIONS.md](../DECISIONS.md)
- [RELATED_WORK.md](../RELATED_WORK.md)
- [future/PREFETCH_ADMISSION.md](../future/PREFETCH_ADMISSION.md)

⚠️ Archive warning: This file preserves the supplied review as historical input.
It is not a canonical technical fact source. It contains statements that were
later source-audited and either overturned or narrowed, including claims about
upstream absence, lifecycle coverage, session metadata semantics, Mooncake,
prefetch, and prior art. Use the canonical documents above for current scope,
claim state, and fixed-version source facts. The historical body is intentionally
not silently rewritten.
---


# Agentic × KV Cache 选题评审：对抗式裁决报告

> 评审人立场：推理团队面试官视角，对抗式。所有 upstream 论断均经过源码级核验（sgl-project/sglang main 分支，2025；7/7 论断属实）。

> ⚠️ **口径修正（2026-08-17，用户独立核验后）**：本报告初版的两条论断已被推翻——
> 1. **"上游空白"不成立**：SGLang 官方已有 Programmatic KV Cache RFC 与 Distributed KVCache for Agentic Workload Roadmap，方向为 router/orchestrator 发出 PREFETCH/DEMOTE/PIN hint、HiCache 执行分层移动，session radix cache 已落地，proactive prefetch / demote execution API 列为后续工作。这是官方高优先级路线，非旁支。
> 2. **"Prior art 无人做掉"不成立**：InferCept（ICML'24，tool/API 中断的 Preserve/Swap/Discard）、Continuum（tool-aware KV TTL）、KVFlow（agent workflow 驱动 CPU→GPU proactive prefetch）均为直接 prior art。
>
> 初版正向代码论断（7/7）仍然成立；被推翻的是负向论断。教训：**负向主张（"无人做过"）默认弱证据，廉价检索代理搜不到 ≠ 不存在。**
> 项目定位已从"发现无人解决的空隙"调整为：**在固定 SGLang 版本上，实现并验证 upstream 尚未落地的 session-scoped demote/resume correctness contract，形成可审计 patch、故障矩阵和性能边界**（详见 §2 修订与 §5.5 差异化防守）。

> ⚠️ **第二轮修正（2026-08-17，四处硬伤）**：
> ① demote 与 proactive prefetch **解绑**——二者可独立成败，主线只做 demote/resume correctness，prefetch 须通过独立 Gate P（§5.2）；
> ② correctness contract 重述为 **Publication / Unprotection / Reclamation 三操作分离**，难点全在 Reclamation 的共享前缀安全（§5.1）；
> ③ 新增最强简单 baseline ⑦ **release-refs-only + stock eviction**，配 Reclamation kill gate；
> ④ 实验矩阵废除先验网格（64K×128 在 24G 单卡上不自洽），改为**从实测 KV pool 容量反推**的派生程序。

> ⚠️ **第三轮修正（2026-08-17，策略层架构定稿 + prior art 扩充）**：
> ① 策略层重构为**约束优先免权重**四层架构（§5.3），否决"价值密度 score"方案；时间信号改用 survival/hazard 形态；oracle 梯子重画为 B0/B1/B2/O\*（动作 regret 度量）；Workflow Automaton 与跨 session 估值移出主线。
> ② 新增已核验 prior art：**TokenCake**（arXiv:2510.18586，vLLM 上 tool-stall 主动 offload + 预测 upload，重叠度极高，未开源）、**PBKV**（arXiv:2605.06472，动态 workflow 预测驱动 KV 管理，未开源）；数据主校准源定为 **TraceLab**（UW，开放下载）。
> ③ SGLang 源码核验 5/5：session radix cache 实为全新 `unified_cache` 架构（`ComponentData{lock_ref, host_lock_ref, session_ref, session_ids}`、`FullComponent` 按 `(ref>0, ref, priority)` 排序、`_cascade_evict` 级联）——Reclamation 是介入共享逐出语义，不是删几个块。

---

## 0. 先说结论（TL;DR）

**冠军项目：Tool-Gap-Aware KV Lifecycle Controller（方向 A + D 合并），底座 SGLang + HiCache + Mooncake（TCP 模式，单卡可跑）。**

- 方向 D（prefetch）不独立成题；**且不与主线捆绑**——主线只交付 demote/resume correctness，prefetch 须先通过独立 Gate P（实测存在正的 prefetch_slack，§5.2）才进入交付范围。
- 方向 C、G、H、I 直接否决；方向 B、E、F 否决为旗舰但 B 可作为后期扩展。
- 你原来的直觉是对的，但**不是因为它"听起来好"，而是因为 upstream 源码证实了三个具体空隙**（见 §2）。
- 同时有一个你必须正视的坏消息：**SGLang 已经上线了 `--enable-session-radix-cache`**，它吃掉了"KEEP/保护"这一半的故事。你的项目必须把它作为 baseline 之一，且叙事必须从"session-aware 保护"转向"**gap-aware demote/resume 的正确性合同与性能边界**（prefetch 为 Gate P 条件项）"。这反而让项目更窄、更诚实、更能防守。

---

## 1. Upstream 事实基础（全部经二次核验）

### SGLang + HiCache 现状（已确认）

| 能力 | 状态 | 证据位置 |
|---|---|---|
| 三层 KV（HBM→Host DRAM→L3 storage） | ✅ 已有 | `mem_cache/hiradix_cache.py`、`managers/cache_controller.py` |
| 可插拔 eviction（LRU/LFU/Priority/SLRU） | ✅ 已有 | `mem_cache/evict_policy.py`，`--radix-eviction-policy` |
| Session 级 KV 保护 | ✅ **已有**（近期上线） | `--enable-session-radix-cache`，`UnifiedSessionRefTracker`，`/open_session` `/close_session` |
| per-request `priority` / `session_id` / `cache_salt` | ✅ 已有 | `managers/io_struct.py` `GenerateReqInput` |
| 自定义 cache backend 注册点 | ✅ 已有 | `mem_cache/registry.py` `register_radix_cache_backend()` |
| Prefetch（storage→host） | ⚠️ **纯 reactive**：仅在请求进入 waiting queue 时由 `Scheduler._prefetch_kvcache()` 触发 | `managers/scheduler.py`、`hiradix_cache.py: prefetch_from_storage()` |
| 请求到达前的 proactive prefetch hook | ❌ **不存在** | 核验确认 |
| tool-gap / 生命周期驱动的主动 demote | ❌ **不存在**（offload 只由 write-through 备份 + 显存压力 eviction 被动触发） | 核验确认 |
| per-block TTL | ❌ 不存在 | 核验确认 |
| Mooncake TCP fallback（无需 RDMA） | ✅ 已有 | `MOONCAKE_PROTOCOL="tcp"`，单卡可全链路 |

### vLLM + LMCache 现状（已确认）

- `KVConnectorBase_V1` 生命周期严格绑定调度循环，**无 per-request 的外部 suspend/demote/restore 控制**；sleep mode 是 engine 级全局的。
- LMCache 有 L2→L1 prefetch REST API，但无任何 tool-gap / agent 生命周期语义；与 vLLM 的接缝在 connector 层，单人改造需动 vLLM v1 scheduler 状态机 + BlockPool，**难度对学生单人不可行**。

### Prior art（❌ 初版结论已被推翻，2026-08-17 修正）

~~Mooncake / MemServe / Preble / Parrot / ServerlessLLM / SGLang Router 均未实现"利用 tool-gap 信号做 KEEP/DEMOTE/DROP/PREFETCH"的 runtime 通路。~~

**修正后的 prior art 地图：**

| 系统 | 已做到 | 与本项目的关系（待逐一源码核验，当前为初步判断） |
|---|---|---|
| **InferCept** (ICML'24) | tool/API 中断时的 Preserve / Swap / Discard 决策 + min-waste 调度 | 占据"gap 期间 KV 去留决策"的核心思想；需核验：底座与版本、是否覆盖异步正确性（cancel/stale/泄漏）、是否有 resume 前 proactive prefetch、开源与可复现状态 |
| **Continuum** | tool-aware KV TTL（按工具类型预估 gap 设置驻留时限） | 占据"gap 时长信号 → 驻留决策"；需核验：是否只有 TTL 一种机制、有无三层介质、有无故障语义 |
| **KVFlow** | agent workflow DAG 驱动的 eviction + CPU→GPU proactive prefetch | 占据"workflow 先验 → 主动预取"；需核验：真实 runtime 还是模拟、粒度、正确性覆盖 |
| **SGLang 官方 RFC/Roadmap** | PREFETCH/DEMOTE/PIN hint 接口设计、session radix cache 已落地；proactive prefetch、demote execution API 为**未落地的后续工作** | 问题重要性的最强外部背书；同时是最直接的竞速者与合作对象（E5 通道） |

**结论：问题的重要性获得官方与学术界三重背书（这是好消息）；"无人做过"叙事作废，项目价值必须落在工程合同所有权上（见 §2 修订）。**

---

## 2. 项目立足点（2026-08-17 修订：从"空隙发现"改为"合同所有权"）

三个技术事实仍然成立（在 pin 定的版本上，代码里没有）：主动 DEMOTE 执行路径未落地、proactive PREFETCH 未落地、异步生命周期正确性语义（epoch/stale/cancel/cleanup）零覆盖。但它们的性质变了——**不再是"无人想到的空隙"，而是"官方已宣布、尚未交付的工作"。**

因此项目立足点重述为：

> **在固定 SGLang 版本（pin commit）上，实现并验证一份 session-scoped demote/resume correctness contract：给出可审计的 patch series、完整的故障注入矩阵（E4）、以及带边界声明的性能刻画（E3）。**

这个定位下，项目的防守点从"我发现了"变成"我拥有"：

1. **合同定义权**：demote 传输中收到 resume 怎么办、stale completion 撞上新 epoch 怎么办、storage miss 后 fallback 的所有权归谁——RFC 只画了接口，**没有人写下并验证过这份正确性合同**。这份合同 + 证明它的测试矩阵，是我的核心资产。
2. **实现与证据**：prior art（InferCept/Continuum/KVFlow）各占一个策略思想，但（待核验）均未在当前 SGLang HiCache 三层 + Mooncake L3 上交付带故障语义的可复现实现。
3. **E5 通道升级**：官方 RFC 的存在使"向上游提交实现/测试/bug report"从可选项变成项目的天然出口——对着官方接口设计做实现，命中率远高于凭空提 RFC。

---

## 3. 候选池与五道闸门攻击

保留 3 个最强候选进入闸门：**A+D（合并）**、**B**、**E**。其余先决：

- **C（Fork-aware sharing）**：❌ 否决。radix tree 天然做 prefix 共享 + refcount，`cache_salt`/`extra_key` 做隔离。你会花三个月重新发明 upstream 已有的东西。Gate 2 = 0。
- **F（Admission/QoS）**：❌ 否决。`priority` 字段 + PriorityStrategy 已占据入口；往深做必然膨胀成完整 scheduler，违反 scope 约束。
- **G（Agent-aware eviction score）**：❌ 否决为旗舰。upstream 的 `EvictionStrategy` 插件让它退化成 150 行的 `get_priority()` 子类——这恰好是你 SOP 里"薄 policy callback"的定义。**但它作为冠军项目内部的 Candidate 之一存活**（见 Gate 3）。
- **H（Prefix stability）**：❌ 否决。agent framework 侧工作，runtime ownership ≈ 0。
- **I（RL GC）**：❌ 否决。research 味，与岗位信号错位。

### 候选 1：A+D — Tool-Gap-Aware KV Lifecycle Controller

- **Gate 0（岗位边际价值）**：✅ 强。直接证明：读懂 HiRadixCache/cache_controller 源码、拥有 demote/restore 真实路径、异步状态机 + epoch + cleanup、TTFT 分解性能工程。全部命中你缺的信号，零重叠于你已有的存储背景（存储背景反而是加分的迁移叙事：分层存储 → 分层 KV）。
- **Gate 1（目标函数）**：✅ 清晰。最终指标 = **Goodput@P95-resumed-TTFT-SLO**（固定 HBM budget、固定到达率下，满足 resumed-TTFT SLO 的完成 session 吞吐）。proxy = 释放的 HBM 字节 → 允许更大有效 batch → goodput↑；critical-path restore 时间 → resumed TTFT↓。**因果链断裂 regime（必须诚实写进结论）**：① HBM 无压力时 demote 纯亏（多付传输）；② gap 太短（< 传输时间）时 prefetch 藏不住；③ KV 小 / prefill 快时 recompute 比 restore 便宜，整个 restore 路径失去意义。
- **Gate 2（路径所有权）**：✅ 这是所有候选中唯一"接缝清晰但路径空白"的：接缝（registry、cache_controller 的异步队列、scheduler prefetch 入口、session API）upstream 已铺好，但 `tool_wait→decision→demote→async completion→resume→prefetch→re-admission` 这条**完整路径不存在，必须自己建**。退化风险：如果只调 `/flush_cache` 或只写 EvictionStrategy 子类就是 wrapper——防线是必须拥有异步传输的 completion/epoch/cleanup 语义。
- **Gate 3（判断密度）**：✅ 天然多候选：
  - Candidate α：static gap threshold（gap 预期 > T 秒 → demote；resume 信号到 → prefetch）
  - Candidate β：cost model（demote 当且仅当 `E[gap] × HBM 租金 > demote+restore 成本 × P[resume]`，压力自适应）
  - Candidate γ：纯 eviction-score 方案（G 降级而来：不主动 demote，只改压力下的 eviction 优先级 + reactive restore）
  - **X\*** = Candidate α。**β 打不过 α 就 STOP 在 α；α 打不过 stock 就整体 STOP 并如实报告 negative result。**
  - 上界 baseline：oracle（gap 时长完全已知）——你和 oracle 的差距就是"信号价值"的诚实度量。
- **Gate 4（证据）**：✅ E2：forced demote/restore/recompute 路径 trace；E3：gap 分布 × KV 大小 × 并发 × HBM 压力的受控扫描，A/B + 消融 + manifest；E4：cancel-during-transfer、stale completion、storage miss、duplicate resume、泄漏检测 long-run。**E4 面在所有候选里最富。**

### 候选 2：B — Branch-Aware KV GC

- Gate 0：中。GC 语义有价值但能力面窄。
- Gate 2：⚠️ 致命伤：`/close_session` + session ref tracker 已经给了"branch 终止 → 释放引用"的 90% 机制。每个 branch 开一个 sub-session、终止时 close，就复现了大部分功能——**项目退化成"正确使用 upstream API"的 wrapper 风险极高**。
- Gate 3：⚠️ 更致命：强 baseline（压力驱动 LRU）在大多数 regime 下近似最优——死 branch 的 KV 没人再碰，LRU 很快会自己评掉它。semantic GC 只在"HBM 压力极高 + 死 branch 巨大 + 死亡到压力到来的窗口极短"的窄 regime 有价值。**先定答案再补实验的风险大。**
- 裁决：❌ 不做旗舰。作为冠军项目 Phase 6 之后的可选扩展（branch terminate 作为一种 lifecycle 事件并入状态机，边际成本低）。

### 候选 3：E — KV-Affinity Routing

- Gate 0/2：空隙真实（router 不感知 demoted KV 的驻留节点），但需要多节点/多 GPU 环境，且改造对象是 Rust router + 分布式元数据——项目重心滑向 distributed router，KV runtime 占比萎缩。
- 裁决：❌ 否决（硬件与 scope 双重不可行）。写进冠军项目的 future work，面试时作为"我知道下一步是什么"的视野展示。

---

## 4. Substrate 裁决

**SGLang + HiCache + Mooncake（storage backend，TCP 协议）。** 理由：

1. vLLM 侧无 per-request KV 控制原语，改造需动 v1 scheduler + BlockPool，单人不可行（已核验）。
2. SGLang 全 Python 的 mem_cache 层 + 官方注册点（`registry.py`）+ 会话 API + 异步 cache_controller 队列 = 接缝质量最高。
3. Mooncake TCP fallback 单卡可跑全链路（已核验），不需要 RDMA 网卡。
4. 降级方案：Phase 1 可先用 HiCache file/本地 backend 打通，再切 Mooncake——降低环境搭建吃掉时间的风险。

硬件：一张 24G+ GPU（3090/4090 即可，7B/8B 模型）。用 `--mem-fraction-static` 压小 KV pool **人为制造 HBM 压力**——这是单卡实验成立的关键技巧，否则测不出 demote 的价值。

---

## 5. 冠军项目完整定义

### 项目名称
**Agentic KV Lifecycle Controller: Tool-Gap-Aware Demotion & Prefetch for SGLang HiCache**

### 一句话问题定义
在 agent tool-call 等待期间，利用 session 生命周期信号对 KV 执行安全的 demote（Publication→Unprotection→有条件 Reclamation）并保证 resume 正确性，在固定 HBM budget 下提升 Goodput@P95-resumed-TTFT-SLO——cancel/timeout/stale-completion 下零泄漏零污染。proactive prefetch 仅在 Gate P 通过后加入（§5.2）。

### 为什么现在值得做（修订）
Agent workload（tool gap 2–30s+，session KV 数十 K token）已成主流；SGLang 官方 Agentic KV RFC/Roadmap 已把 PREFETCH/DEMOTE/PIN 列为高优先级方向但 demote execution / proactive prefetch **尚未落地**——问题重要性有官方背书，实现与正确性合同是尚未被交付的部分。这不再是"窗口期"叙事，而是"对着已宣布的接口，交付第一份经过故障矩阵验证的实现"。

### 为什么 upstream 默认行为不够
三个已核验事实（pin 版本上）：无主动 DEMOTE 执行路径（tool wait 期 KV 要么占显存要么被盲评）；无 proactive PREFETCH（restore 全在 critical path 上）；无异步生命周期正确性语义（epoch/stale/cancel/cleanup）。

### 我真正拥有的 runtime path
```
tool_wait 信号 → lifecycle 状态机(decision)
→ Publication(异步 commit host/Mooncake 副本)
→ Unprotection(释放 session 引用，页面可被普通 eviction)
→ [有条件] Reclamation(定向回收私有 GPU pages)
→ completion/epoch 处理 → resume → restore/recompute → re-admission → first token
→ [Gate P 通过后] resume_imminent hint → proactive prefetch(Mooncake→host)
```
覆盖：cancel、timeout、session 终止、new epoch、stale transfer completion、restore miss、partial transfer、cleanup ownership、fallback recompute。

### §5.1 Correctness contract 的真实结构：三操作分离（第二轮修正核心）

初版把"demote"当一个操作，这是错的。它是三个语义不同、危险度递增的操作，官方 RFC 同样强调 publication 与 reclamation 分离：

| 操作 | 语义 | 危险度 |
|---|---|---|
| **Publication** | 确保 host/L3 副本 committed、对齐、完整 | 低（纯增副本，失败可重试） |
| **Unprotection** | 解除 session 保护，页面回到普通 eviction 候选池 | 低（复用 upstream eviction 正确性） |
| **Reclamation** | 立即定向回收指定 GPU pages | **高——合同的全部难点在此** |

**Reclamation 安全前提（合同条款，E1/E4 逐条验证）：**
1. 目标 page 的 lower-tier 副本已 committed（Publication 完成且校验）；
2. 无 running request 持有 lock（`lock_ref == 0`）；
3. **共享前缀条款：radix 节点被多 session 引用时（ref_count > 1）最多做 Unprotection，永不定向 Reclaim**——只有本 session 私有的后缀段可回收。否则"session-scoped active demote"只是安全地伤害另一个 session 的命中率；
4. transfer completion 与 epoch 切换之间存在明确线性化点（stale completion 不得改变新 epoch 状态）；
5. 任一步失败后可恢复：副本在 → restore；副本不在 → fallback recompute，且块账本无泄漏；
6. 无 hint 的普通请求完全 bypass，行为与 stock 逐字节一致（默认路径零侵入）。

**必报指标新增：跨 session 命中率损害检查**——开启 controller 前后，其他 session 的 prefix cache hit rate 不得退化（这是条款 3 的量化验证）。

**合同条款的源码落点（2026-08-17 已核验，5/5 属实）**：条款 2/3 对应 `unified_cache/components/tree_component.py` 中 `ComponentData` 的四个字段——`lock_ref`（device 侧请求锁）、`host_lock_ref`（host 侧锁）、`session_ref`（session 保护计数）、`session_ids`（覆盖集合）。合法回收叶 = 四者共同许可。eviction 在 unified cache 中以 component 为单位组织并有 `_cascade_evict` 级联（`unified_tree_core.py:1505+`），stock 路径为叶子驱动 + 父节点级联（`radix_cache.py:592-620`）——**因此定向 Reclamation 不是"绕过 eviction 删几个块"，而是介入这套共享排序/级联语义**。

### §5.2 Gate P：prefetch 的独立准入（不再与主线捆绑）

demote 与 prefetch 可独立成败。prefetch 的存在性前提是**正的可利用提前量**：

```
prefetch_slack = request_arrival_time − resume_imminent_hint_time
```

slack 是**部署属性而非 runtime 属性**，取决于 hint 模型，Gate P 必须写明采用哪种：
- (a) tool 启动时携带预计时长 → slack ≈ gap − 预测误差（最大但依赖预测）；
- (b) tool 完成、LLM 请求组装前发 hint → slack = 框架组装/网络耗时（真实但通常很小）；
- (c) 只有 resume 请求本身 → slack = 0，"prefetch"退化为 upstream 已有的 reactive restore，**无新东西可做**。

**Gate P 通过判据（P5 末测量）**：在选定 hint 模型下，实测 slack 分布满足 `P(slack > restore_transfer_time) ≥ 50%`，且预期 P95 resumed-TTFT 改善 ≥ 10%。不过 → prefetch 整体移出交付范围，只在报告中写明测得的 slack 分布与结论。主线交付不依赖 Gate P。

### §5.3 策略层架构（2026-08-17 第三轮修正定稿）

> 演化记录：初版 = 单一 breakeven 公式（太薄）→ 二版 = "索引层 + 价值密度 score + 两个消费者"（**已否决**：跨约束类标量化 = 汇率玄学；score 是 V(s) 而决策需要 Q(s,a)；demote/prefetch 目标异向不可共用一个分数；恰好重演了 toolgap-kv D029→D030 已否决过的漂移）→ 本版 = **约束优先、免权重**。

**四层结构（缺一不可，顺序即权威顺序）：**

```
正确性/执行层  哪些 KV 可以安全回收？异步 completion 是否属于当前 epoch？
      │        → 产出：合法动作集合。score 只能排序，不能授权。本项目所有权在此层。
预测层         何时返回、是否返回 → 离散 hazard 表（见下）
成本层         移动/恢复/重算/干扰各多少钱 → 全部实测，不拍
决策层         硬约束内选动作 → lexicographic，无合成权重
```

**决策流程 = 硬过滤 → 候选集内排序：**

第一步，七条硬过滤谓词（全部来自正确性层，任一不满足即不可回收）：
1. lifecycle 状态合法；2. Publication committed；3. 无 pending transfer；4. `lock_ref == 0`（含 host_lock_ref）；5. 无其他 active session 覆盖（`session_ref`/`session_ids` 检查）；6. 合法 device leaf（尊重 component 级联结构）；7. victim QoS 预算可行。

第二步，仅在过滤后的候选集内排序：`expected recovery/interference/collateral penalty ÷ unique reclaimable bytes`（GreedyDual-Size 谱系；shared bytes 不计入分母因为不释放内存）。**候选集内成员已正确性/QoS 等价，此处标量不交易任何不可交易的东西——被否决的是跨约束类标量化，不是标量本身。**

**时间信号的正确形态 = survival/hazard，不是分位数查表：**
- `returned?` 是右删失数据（未返回/超时/轨迹结束），朴素 p50/p90 + EWMA 有 survivor bias 且 EWMA 无法维护分位数。
- 决策端消费形式：`P(resume ≤ h | 已等待 t, 可观测特征)`，h 取传输时间等具体量——时间通过条件概率进入成本，**不作分母**。
- v1 实现上限：per tool_group × 等待时长桶的离散 hazard 表（KM 式估计，在线增量），**不做参数化生存模型**——防 survival analysis 膨胀成子项目。

**信息价值梯子（决定预测层是否进 runtime）：**

```
B0：只用 runtime pressure + 当前 KV 状态        ← 最强免信息 baseline
 │ Δtool
B1：B0 + tool profile（hazard 表）
 │ Δhistory
B2：B1 + 当前轨迹前缀特征
 │ residual ceiling
O*：知道真实未来的离线 action oracle（同 executor、同合法动作集、同 QoS 约束）
```

- 度量 = out-of-sample **动作 regret + joint-SLO 结果**，不是 gap 预测 RMSE。
- Δtool 不显著 → hazard 表**不进 runtime**（离线算免费 ≠ 进 runtime 免费）；Δhistory 不显著 → 不做任何轨迹级机制；O*−B2 大只说明信息缺口存在，不构成堆模型的许可。
- oracle 必须与候选共享 executor/合法动作/QoS 约束，否则混入未来到达与执行器差异，无法解释为信息价值。

**明确移出主线的机制**：Workflow Automaton/转移图（独立机制、与 KVFlow Agent Step Graph 及 PBKV 重叠、服务对象是 Gate P 后置的 prefetch）→ post-Gate-P 可选扩展；跨 session 未来 hit value 估计（安全 demotion 只需要 coverage invariant = 硬过滤谓词 5，估值即滑向全局 prefix-cache replacement 项目）→ 删除。

**策略薄是设计结论而非缺陷**：硬过滤是正确性层产物，候选集内只剩一个每字节代价排序，预测层可整体裁剪（B1−B0 不显著时）。价值在合同，不在策略。

### 数据基础：双 trace join

客户端 trace 只能证明 workload 真实，不能证明 GPU residency/可回收字节/逐出原因/恢复成本。校准必须两份 trace 连接：
- **客户端 gap 事件**：`trace_id, session_id, session_generation, gap_id, gap_start_time, next_request_admit_time | censor_time, tool_group, blocking/parallel_group, workflow_prefix, prefix_tokens, returned`（censor_time 支撑 hazard 估计的右删失处理）
- **服务端 trace**：`unique_reclaimable_bytes, shared_bytes, device/host residency, session_ref/locks, allocator headroom, transfer queue, runtime pressure, 实测 restore/recompute/interference`

数据源定位（**2026-08-17 已核验**）：**TraceLab = 主校准源**（UW SyFi，arXiv:2606.30560，github.com/uw-syfi/TraceLab，DuckDB/JSONL 开放下载；~4,300 session / ~43 万次 tool call，字段含 `emitted_at`/`result_at`/`tool_wall_latency_ms`/`prefix_tokens`/`append_tokens`/`session_id`/`tool_name`，正是 hazard 估计与 gap 分布校准需要的全部客户端字段；注意脱敏——无工具输入文本，仅 `input_chars`）。OpenHands 日志（有 ISO 时间戳，可算真实 wall latency）= 外部效度验证；**SWE-agent `.traj` 只有相对 `execution_time`、无 wall-clock 时间戳，不作延迟主源**（已核验）；τ-bench = 模拟环境、BFCL = 函数调用结构，均不当部署延迟分布用。回退方案：自建 harness 构造校准混合（InferCept 式）。

### 最终指标
Goodput@P95-resumed-TTFT≤S（主）；P95 resumed TTFT 及其分解（副）；recompute prefill tokens（副）。

### 核心 baseline
① stock HiCache；② stock + session-radix-cache；③ always-retain（锁 HBM）；④ always-demote-on-gap；⑤ static threshold（=X\*）；⑥ oracle gap（上界）；⑦ **release-refs-only：Publication + Unprotection、无定向 Reclamation，交给 stock eviction**（第二轮修正新增，**最强简单 baseline**——上游官方 Demote hint 很可能就实现成这样）。

**Reclamation kill gate**：主动定向 Reclaim（全链路）必须在压力时刻的 headroom 时效性或 P95 latency 上显著打败 ⑦，否则状态机中 Reclamation 一步与 tree 修改无价值，收敛到 ⑦ 语义交付。注意：差值大小取决于 HiCache write policy——write_through 下副本本已在 host，主动 demote 的剩余优势只剩"headroom 提前到位 + 传输移出压力时刻"，必须实测，不得假设。

### X\*
B0（只用 runtime pressure + 当前 KV 状态的免信息版本，见 §5.3 梯子）即 X\*。任何带信息的方案（hazard 表、轨迹特征）必须在动作 regret 与 joint-SLO 上显著打败它，否则收敛到 B0 为最终交付。

### STOP 条件
1. forced-demote 的 restore 路径不比 recompute 快（restore/recompute breakeven 不存在于目标模型/KV 尺寸）→ 全项目 STOP，换 KV 尺寸更大的设定或换题。
2. 施加 HBM 压力后，stock LRU goodput ≥ oracle 的 ~95% → 生命周期信号无价值，如实 negative result。
3. Gate P 不过（slack 分布无可利用提前量）→ prefetch 移出交付范围，主线不受影响。
4. 定向 Reclamation 打不过 baseline ⑦ → 收敛到 release-refs-only 语义，如实记录。

### 主要工程模块
1. Session lifecycle API 扩展（`/session/pause` `/session/resume` 或 generate 请求上的 gap hint 字段）
2. Lifecycle 状态机（ACTIVE→TOOL_WAIT→DEMOTING→DEMOTED→PREFETCHING→RESUMING，per-session epoch，事件驱动）
3. 主动 demote 路径 = Publication / Unprotection / Reclamation 三操作分离实现（复用 cache_controller 异步队列；Reclamation 受 §5.1 合同条款约束）
4. Proactive prefetch 路径（新 hook，请求到达前 storage→host）——**Gate P 通过后才实现**
5. DecisionTrace instrumentation + resumed-TTFT 分解（decision/queue/transfer/re-admission/prefill/first-token）
6. Agent workload driver（多 session、可配 gap 分布/KV 尺寸/并发/到达率，开环）
7. Benchmark harness（manifest、raw JSONL、多次运行、A/B 脚本）
8. Failure injection 框架（E4）

### 实验设计：从实测容量反推，不用先验网格（第二轮修正）

初版 4×3×3×3×2 网格作废：64K token × 128 session 在 24G 单卡上不自洽。以 Qwen2.5-7B（28 层、4 KV heads、head_dim 128、BF16、默认 ctx 32768）为例：

```
KV bytes/token = 2(K,V) × 28 × 4 × 128 × 2B = 57,344 B ≈ 56 KiB
→ 单个 64K session ≈ 3.5 GiB KV（且超出模型默认上下文）
→ 24G 卡减去 ~15G 权重 + activation，KV pool 实际只有若干 GiB
```

**派生程序（P1 执行，产出锚点网格）：**
1. 固定 model / dtype / page size / `--mem-fraction-static`，实测可用 KV pool 字节数 → `pool_tokens = pool_bytes / bytes_per_token`；
2. 选压力档位 = **oversubscription 比率** `Σ(session ctx) / pool_tokens ∈ {1.5×, 3×, 6×}`；
3. 在模型 ctx 上限内反解 (ctx_len, 并发) 组合，每档取 2 个点（长 ctx×少并发 / 短 ctx×多并发）；
4. gap 分布 {短/中/长尾} × restore 介质 {host, Mooncake-TCP} 叠加其上。

初始锚点网格 ≈ 3 压力档 × 2 组合 × 3 gap × 2 介质 = **36 点起步**，扫描范围按 P5 发现再扩。明确寻找 losing regime（低压、短 gap、小 KV）。若需要更宽的 (ctx×并发) 可行域，备选更小模型（如 Qwen2.5-3B）并重算 bytes/token。

### 主要性能优化机会
demote 释放 HBM → 有效 batch↑ → goodput↑（主）；restore vs recompute 的 breakeven 决策；把 restore 从 resumed-TTFT critical path 移入 tool-gap slack（仅当 Gate P 通过）。

### E1–E4 路线
E1 状态机单测/contract → E2 forced path trace（强制 demote/restore/recompute 三路径可区分）→ E3 受控 A/B + 消融 + manifest → E4 failure injection + 并发 + long-run 泄漏检测。争取 E5：向 SGLang 提 RFC issue（proactive prefetch hook），无论是否被接受都是外部评审证据。

### 最大三个风险与缓解（修订）
1. **Upstream 竞速（已从风险升级为事实）**：官方 RFC 明确要做 demote execution API 与 proactive prefetch。缓解：① pin commit，交付物定义为"该版本上的可审计 patch series + 故障矩阵"，不受后续上游变化影响；② 把重心压在 RFC 未覆盖、上游最难短期交付的正确性合同（E4）上；③ 若上游先落地，项目立即转向"对上游实现跑我的故障矩阵 + 差异对比"——测试矩阵资产不会作废，找到 bug 反而是更强的 E5。
2. **单卡测不出压力** → 缓解：`--mem-fraction-static` 压 KV pool + 高并发 driver 制造压力；Phase 1 kill gate 验证。
3. **异步正确性复杂度失控** → 缓解：epoch 化设计先行（所有 completion 带 epoch，stale 直接丢弃）；状态机先在 mock transfer 上做 contract test 再接真实路径。

### §5.5 与 prior art 的差异化防守（必须在 P0 完成核验）

面试必答题："InferCept/Continuum/KVFlow 都做过了，你做了什么？"回答框架（每格都需要读论文/源码后填实，**当前为待核验假设**）：

| 维度 | InferCept | Continuum | KVFlow | **TokenCake**（已核验） | **PBKV**（已核验） | 本项目 |
|---|---|---|---|---|---|---|
| 决策思想 | Preserve/Swap/Discard | tool-aware TTL | workflow DAG prefetch | tool-stall 主动 offload + 预测 upload | 动态 workflow 多步预测 → 分级淘汰 + 保守预取 | 约束优先免权重（§5.3），承认思想全部来自 prior art |
| 底座与版本 | 待核验（较老 vLLM/自研?） | 待核验 | 待核验（真实 runtime or 模拟?） | vLLM 深度定制（arXiv:2510.18586） | vLLM/PyTorch 原型（arXiv:2605.06472） | 当前 SGLang unified_cache 三层 + Mooncake L3，pin commit |
| 异步正确性合同（cancel/stale/epoch/泄漏） | 待核验（预计薄弱） | 待核验 | 待核验 | 有机制（gradual block reservation、CPU buffering）但**无故障注入矩阵证据** | 未见 | **核心交付物：E4 故障矩阵** |
| resumed-TTFT 分解 + 边界/负 regime 报告 | 待核验 | 待核验 | 待核验 | 未见 | 未见 | 核心交付物 |
| 可复现性（单卡、一条命令） | 待核验 | 待核验 | 待核验 | **未开源** | **未开源** | 核心交付物 |

**TokenCake 是重叠度最高的直接 prior art（tool-stall offload/upload 概念几乎完全重合）**。本项目的差异化因此进一步收窄且必须明说：① 底座不同（SGLang unified_cache/HiCache 三层 + Mooncake L3 vs vLLM 两层）；② TokenCake/PBKV 均未开源——可审计 patch + 单卡可复现是它们没有的交付物；③ 正确性合同的验证深度（E4 故障矩阵、跨 session 命中率损害检查）无人交付。**prefetch 不能作为默认主贡献的裁决由 TokenCake 的存在进一步锁死（Gate P 维持）。**

P0 增加一项 kill gate：**逐一精读五个系统（InferCept/Continuum/KVFlow + TokenCake/PBKV）的论文与开源代码（若有），如实填表。若某系统已在真实 runtime 上交付了完整正确性合同 + 可复现证据，本项目对应部分改为"复现 + 找边界 + 找 bug"定位。**新颖性不是本项目的主张；被明确引用和对比过的诚实工程是。

### 面试官最可能的三问（提前备防）
1. "session radix cache 已经保护 KV 了，你多做了什么？"→ 保护≠管理：upstream 只防误评，不做主动下沉与预取；给 TTFT 分解数据说话。
2. "为什么不直接 recompute？现代 GPU prefill 很快。"→ 给出 restore/recompute breakeven 曲线（KV 尺寸 × 介质带宽），承认小 KV regime 输，展示大 KV regime 赢。
3. "gap 信号来自 agent 框架，错了/晚了怎么办？"→ timeout + fallback recompute 的正确性保证，信号只影响性能不影响正确性——这正是状态机设计的核心原则。

### 简历 bullet（占位符形式）
> 基于 SGLang HiCache + Mooncake 实现 tool-gap-aware KV lifecycle controller（主动 demote + resume 前 prefetch + epoch 化异步正确性）；在 X 并发 agent session、Y–Z s gap 分布、固定 HBM budget 下，较 stock baseline 将 Goodput@P95-resumed-TTFT≤S 提升 A%，P95 resumed TTFT 降低 B%，recompute prefill tokens 减少 C%；通过 failure injection 验证 cancel/stale-completion/storage-miss 下零 KV 泄漏。

---

## 6. Roadmap（Phase 0–9，含 kill gate）

| Phase | 内容 | Kill gate / 出口判据 |
|---|---|---|
| **P0 可行性**（~1周） | pin SGLang 版本；单卡跑通 `--enable-hierarchical-cache`；确认 registry/cache_controller/session API 与调研一致；Mooncake TCP 或 file backend 二选一打通 | ❌ 单卡跑不通 HiCache 全链路 → 换 file backend；仍不通 → 换题 |
| **P1 Stock 基线**（~1周） | agent workload driver v0；**实测 KV pool 容量并执行 §5 派生程序产出锚点网格**；证明 KV 确实经历 HBM→host→storage；forced retain/restore/recompute 三路径可区分并可测 | ❌ restore 不比 recompute 快（breakeven 不存在）→ **STOP 或调大 KV 设定** |
| **P2 Instrumentation**（~1-2周） | DecisionTrace；resumed-TTFT 六段分解；transfer timing；cache state dump | 分解各段之和 ≈ 端到端（误差<5%），否则测量体系不可信 |
| **P3 最小控制器**（~2周） | pause/resume API；always-retain / always-demote / static-threshold 三策略；先 mock transfer 后接真实路径 | E2 达成：三策略 trace 可区分 |
| **P4 Runtime correctness**（~2-3周） | §5.1 三操作合同逐条落地：epoch 状态机、共享前缀条款、cancel、timeout、stale completion、cleanup ownership、fallback recompute | E1+E4 初版：故障注入下无泄漏、无污染、跨 session 命中率无损害 |
| **P5 性能刻画**（~2周） | 锚点网格扫描，找 positive 与 losing regime；**Reclamation vs baseline ⑦ 判定**；**测 prefetch_slack 分布 → Gate P 裁决** | ❌ 所有 regime 下 static threshold ≤ stock → **STOP，negative result 交付**；Reclamation 打不过 ⑦ → 收敛到 release-refs-only |
| **P6 自适应优化**（~2周） | 仅当 P5 显示机会：cost model、压力感知；**proactive prefetch 仅当 Gate P 通过** | β 打不过 α → 收敛到 α，如实记录 |
| **P7 A/B + 消融**（~1-2周) | 七 baseline 全对比、多次运行、消融（只 Unprotection / +Reclamation / +prefetch） | E3 达成 |
| **P8 E4 强化**（~1-2周） | failure injection 矩阵、并发压力、long-run 泄漏检测、duplicate/乱序事件 | E4 达成 |
| **P9 证据打包**（~1周） | raw JSONL + manifest + 复现脚本 + regime 图 + STOP/boundary 文档 + 面试 Q&A；提 SGLang RFC issue（E5） | 一条命令可复现主结果 |

总计约 14–18 周，适配大三下学期到秋招前的窗口。

---

## 7. 最后一句对抗式提醒

这个项目最大的死法不是技术做不出来，而是两个退化态：**做成"给 HiCache 加了个开关"**，或者做完发现**打不过 release-refs-only（baseline ⑦）却没提前测**。防线：把工程重心压在 §5.1 的 Reclamation 合同（共享前缀安全、epoch 线性化、块账本）与 E4 故障矩阵上，P5 尽早跑 ⑦ 对比和 Gate P 裁决，让每一个性能数字都能沿 TTFT 分解向下拆到具体传输段。做到这点，45 分钟面试里没有一个问题能把你从这条路径上打下来。
