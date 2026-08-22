# Performance Engineering for Checked Host-Tier Demotion

> Status: `roadmap`
>
> Project claim state: `roadmap`
>
> 本文件描述如何诊断和优化已经通过正确性门的实现；它不声明当前已有
> runtime、benchmark 或性能结果。

本主线只讨论固定版本 SGLang HiCache 的 Host-tier-only、session-scoped
checked demotion。性能工作的起点不是 profiler，而是一个可比较的服务症状；
终点也不是某个局部计数器变好，而是 action、物理中介和联合服务端点在同一
workload 中闭合。下面依次说明边界、路径真值、RCA、工具升级、最小修改和
停止纪律。

## 1. 先确认问题已经属于性能，而不是 correctness

性能优化 admission 只在 G0–G2 的对应证据均已通过/具备后开始：G0 证明
source/seam 与 ownership，G1 证明 forced checked physical mechanism 确实
产生可归因的物理释放和 allocator-visible headroom，G2 证明 lifecycle
correctness、recovery 和 cleanup。至少应有 artifact 证明：

- fixed SGLang pin、可维护 integration seam 和 candidate/upstream ownership；
- committed Host copy、current legal device-leaf resolution 和 physical
  demotion completion 可被区分；
- session generation、pause sequence、operation identity、stale completion
  fencing、cancel/failure fallback 和 terminal cleanup；
- ordinary request bypass、shared-prefix/lock/pending-transfer 约束、output
  correctness 和 quiescence；
- 删除或绕过 candidate 后 checked behavior 确实消失。

缺少其中任何一项时，问题先归类为 source、correctness、lifecycle 或
ownership gate；不能用较低的 TTFT、较多的 bytes 或 microbenchmark 结果
抵消它。

当前固定 pin、物理 primitive 和 source-audit boundary 由
[ARCHITECTURE.md](../ARCHITECTURE.md) 维护；本文件不复制具体源码事实。
它们不是当前 runtime 已实现或已测量的证据。本文件保持当前 claim state
为 roadmap，不会因为文档完成而变成 shipped 或 experimentally validated。

本文件不重复 Gate、实验协议和结果表：

- Gate 顺序、PASS/RESHAPE/STOP 由 [ROADMAP.md](../ROADMAP.md) 负责；
- baseline、joint SLO、sentinel、workload、统计和 artifact 由
  [EVALUATION.md](../EVALUATION.md) 负责；
- G4 结果、losing boundary 和允许的结论句式由
  [PERFORMANCE_BOUNDARY.md](../PERFORMANCE_BOUNDARY.md) 负责。

## 2. 当前主线是一条可验证的因果链

~~~text
pause intent
  → upstream session generation + pause_seq
  → committed Host-tier copy
  → exact current legal device leaves
  → checked physical demotion
  → allocator-visible free pages/headroom
  → scheduler/admission capacity
  → resume restore or recompute
  → joint resumed/foreground SLO
~~~

candidate 拥有 logical operation identity、checked resolution、lifecycle
fencing、fallback、cleanup 和 DecisionTrace；SGLang 仍拥有 tree、physical
residency、Host/device allocation、movement、stock eviction、scheduler 和
model execution。普通请求走 stock path。

固定 pin + `write_through` 必须拆成三段，不能用一个 "Demote" duration
覆盖它们：

| 阶段 | 物理边界 | 性能关系 |
|---|---|---|
| Publication | tool gap 前更早发生的 HBM→Host D2H 与 Host commit | 是 checked reclamation 的资格前置；eager copy/Host occupancy 可独立形成成本 |
| checked reclamation | tool gap 后复用已 committed Host copy，做 target resolution、final check、existing demote、device release 和 free-drain | 目标是更早 allocator headroom；不得预设这一段再次执行 D2H |
| Recovery | resume 后 Host→HBM restore 或 recompute，再进入 first token | 直接影响 resumed TTFT，也可能与 foreground 争用 |

Target resolution 错误、completion/fence/cleanup 未闭合仍是 correctness
failure，不是可由性能抵消的 overhead。checked reclamation 的 bytes、释放速度
和 allocator delta 是 mechanism mediator；Publication D2H、Recovery H2D 以及
foreground CPU/Host/copy/allocator 争用必须分别归因，重叠 wall-clock duration
不能无条件相加。

resume 的 restore/recompute 可能在直接 TTFT critical path；异步 demotion
通常通过 HBM、Host、copy、CPU、allocator 或 scheduler 影响 foreground，
属于 shared-resource indirect path。重叠阶段的 wall-clock duration 不能
无条件相加。

性能归因的 strongest simple baseline 是相同 committed Host copy、workload、
arrival、instrumentation 和 stock eviction 下：

~~~text
release target session-priority contribution + stock eviction
vs
release target session-priority contribution + checked reclamation
~~~

这里的 `write_through` 是 G1/G2 和第一轮 G3 的 qualification/reference
mode，不是 production-optimal 假设。生产优化结论还必须按 EVALUATION.md 在
相同 workload 和 joint SLO 下挑战 tuned stock `write_through_selective` 与
`write_back`；本文件不创建第二套实验计划。

## 3. 证据层级决定结论上限

| 证据 | 最多能说什么 | 不能直接说什么 |
|---|---|---|
| Source/seam truth | fixed pin 中存在可审计的调用点和状态依赖 | runtime 已正确完成或物理释放已发生 |
| Lifecycle/path truth | 具名 run 走过 Host commit、resolution、demotion 或 resume path | allocator headroom 或端到端收益 |
| Mechanism truth | requested/eligible/scheduled/completed bytes、physical completion 和 allocator delta 可对账 | sustainable lambda 或 joint SLO 改善 |
| Resource truth | HBM free pages、allocator、queue、copy、CPU/Host pressure 发生受控变化 | resource 变化就是 endpoint 因果 |
| Endpoint truth | 固定 workload 下 resumed TTFT、foreground ITL、success 和 sustainable lambda 的 paired 结果 | 普适或 production 结论 |
| Boundary truth | 声明的 pressure、sharing、gap/recovery、foreground-load 区域中的胜/负/无关 | 未注册 regime 的泛化 |

必须拒绝这些快捷推断：

- scheduled/completed bytes 不等于 allocator-visible free pages；
- free pages 不等于 scheduler 真正扩大了可持续负载；
- resumed TTFT 改善但 foreground ITL 或 success 退化，不是 win；
- Host copy committed 不等于 device demotion completed；
- client gap trace 不能证明 server residency、allocator pressure 或 transfer cost；
- profiler hotspot、GPU utilization、单个 queue depth 不能单独证明根因；
- 旧 Agentic-KV、Mooncake、vLLM 的数字和运行结果不是当前主线证据。

## 4. 调查闭环：症状 → 路径 → 区分 → 回归

~~~text
service symptom
  → fair reproduction
  → path truth
  → lifecycle-stage decomposition
  → critical-path/resource attribution
  → competing hypotheses
  → smallest discriminating experiment
  → pinned source seam and ownership
  → smallest reversible change or handoff
  → same-workload regression
  → claim ceiling and stop decision
~~~

| 步骤 | 必须产出 | 停止或返回条件 |
|---|---|---|
| 定义症状 | expected/observed、endpoint、regime、重复条件 | 无可比较差值，先修 reproduction |
| 固定公平性 | source/build/model、arrival、seed、worker、capacity、warm-up、drain、arm order | coldness、history 或 fairness 不可证，结果无裁决权 |
| 证明路径 | operation identity、Host commit、legal target、physical completion、resume/recompute、output | join 不完整时最多“当前异常无法可靠归因” |
| 拆生命周期 | admission、publication、resolution、submit、completion、headroom、resume、cleanup | endpoint 无法映射到阶段，不直接看 kernel |
| 找中介 | free pages/headroom、queue/copy、CPU/Host、restore/recompute、foreground load | counter 与异常窗口不对齐，只作旁证 |
| 保留假设 | 主解释、替代解释、workload/order/instrumentation 混淆 | 假设没有不同预测，重写 |
| 区分实验 | 唯一 changed variable、预测、falsifier、失效条件 | 一次改变多个控制面，实验作废 |
| 判 ownership | candidate 可直接/间接控制，还是 upstream observe-only | 不可控时 handoff/STOP，不扩 scope |
| 最小修改 | patch/config、rollback、deletion test、guardrails | 需要新 data plane、scheduler 或 policy framework，停止评审 |
| 回归裁决 | action、mediator、endpoint、correctness、ITL、cleanup、losing regime | 任一核心链断裂，降低结论 |

例如“demotion 释放 bytes 但 resumed TTFT 不变”，至少保留三种解释：

| 假设 | 最小区分 |
|---|---|
| 只改变逻辑 bookkeeping，没有 physical release | 对照 physical completion 与 allocator delta |
| headroom 变了，但本轮无压力或 stock eviction 已足够及时 | low-pressure/near-capacity paired run，固定 release-only baseline |
| headroom 变了，但 restore/recompute 或 foreground interference 吞掉收益 | 分解 headroom→scheduler→resume/foreground，并锁定 arrival |

实验后不得删除失败假设。action 变化而 mediator 不变，先怀疑 executor 或
测量；mediator 变化而 endpoint 不变，最多是机制/资源结果；endpoint 变化而
mediator 不变，优先怀疑顺序、pressure、instrumentation 或 workload 混淆。

## 5. 最小观测契约必须能重建 operation

以下是诊断所需的最小 observation surface，不是已存在的 schema，也不是
通用 telemetry 平台。实现必须服从 ARCHITECTURE.md、DEMOTION_CONTRACT.md
和 EVALUATION.md。

### 5.1 显式 identity 和终态

最小 operation identity：

~~~text
(session_id, upstream_generation, pause_seq, operation_id)
~~~

事件还应带 run/pair/arm、worker/process、event identity、worker-local
monotonic timestamp 和 local sequence。跨线程、跨进程及 client/server
关联使用显式 parent/child ID；wall-clock 邻近、相似日志文本、key 猜测和
文件顺序不能作为 causal join。

accepted/clipped/deferred/rejected 只是 admission outcome。异步 completion
必须使用同一 operation identity，单独记录 demoted、failed、cancelled 和
cleaned-up 等终态；不能把“accepted”记成“physical release completed”。

### 5.2 必须覆盖资格、物理结果和 cleanup

~~~text
pause observed
  → Host copy committed
  → target resolved + final eligibility check
  → demotion submitted
  → physical completion
  → allocator-visible headroom
  → resume restore/recompute
  → first token / foreground ITL
  → terminal cleanup
~~~

最小字段应支持 requested、eligible、scheduled、completed bytes，unique/shared
bytes，allocator free pages/headroom，queue/copy timing，restore/recompute，
fallback/reason，request outcome 和 cleanup-ledger delta。没有无侵入 seam 的
字段必须标 unavailable，不能由邻近事件猜测。

### 5.3 时间和缺失规则

同一 clock domain 的 monotonic time 才能计算本地 duration；client/server
的 mapping 必须带校准和不确定度。publication、demotion、restore、recompute、
scheduler 和 foreground 工作可能 overlap。

保留 error、hang、cancel、timeout、late completion、right-censored gap、
trace loss、duplicate terminal 和 missing parent。缺失 terminal 不能默认
success；若缺失改变 action、物理分母、absence proof、headroom 或 useful
restore，该 entity/run 失去对应 claim 裁决权。

DecisionTrace 只记录 decision 时合法可见的输入、reason、目标和 physical
outcome。future resume、后续 request、held-out label、另一个 arm 结果和
post-hoc unused 信息只供离线分析，不得泄漏给 online action。trace failure
或 bounded-buffer overflow 必须优先保障 serving，并显式记录 loss。

## 6. 端点与 QoS：约束优先，不做加权总分

EVALUATION.md 定义当前主 endpoint：满足声明约束时的最大可持续到达率
lambda。比较前冻结：

~~~text
resumed_TTFT_p95 <= S_resume
foreground_ITL_p95 <= S_itl
success_rate >= S_success
correctness and cleanup invariants pass
~~~

阈值不由本文件发明。TTFT、ITL、success、lambda 是 endpoint；bytes、free
pages、headroom、restore/recompute、queue、CPU、Host、copy 和 bandwidth 是
mediator。

QoS 是 decision constraint 和 evaluation objective，不是 correctness
invariant，也不是把恢复、干扰、容量和 collateral effects 兑换成一个
weighted score。正确顺序是：

~~~text
safety/lifecycle legality
  → resource feasibility
  → foreground-QoS feasibility
  → recovery cost among remaining legal actions
~~~

违反 QoS 预算就是不合格结果；不能由另一指标改善抵消。动作不安全时，也
不能由较好 QoS 使其合法。

## 7. 分层诊断和工具升级

| 层 | 问题 | 最小证据 | 工具方向 | 不能单独推出 |
|---|---|---|---|---|
| L0 path/correctness | Host commit、legal target、physical completion、resume 是否真实？ | identity、completion、output、cleanup | 日志、DecisionTrace、client oracle | 性能提升 |
| L1 endpoint | 哪个服务端点异常？ | lambda、resumed TTFT、foreground ITL、success | client runner、service metrics、run stats | 具体根因 |
| L2 lifecycle | 等待在 resolution、submit、completion、headroom、resume 还是 scheduler？ | stage timestamps、queue/copy、operation state | lifecycle trace、定向日志 | duration 可直接相加 |
| L3 resource | 哪个共享资源制造 critical-path wait 或 interference？ | allocator、HBM/Host、CPU、copy、queue、load | OS/process counters、py-spy/perf、Nsight Systems | counter 就是 endpoint 因果 |
| L4 operator/kernel | GPU operator/copy 是否是代表性 critical path？ | shape、dependency、占比、回归 | Torch Profiler、Nsight Systems；必要时 Nsight Compute | kernel 加速等于服务收益 |

升级顺序固定为：

~~~text
logs/basic metrics
  → lifecycle/DecisionTrace
  → CPU/OS/allocator counters
  → Nsight Systems or Torch Profiler
  → Nsight Compute only after a real hot kernel family is isolated
~~~

profile run 与 benchmark run 分离；改变 eager、CUDA Graph 或执行模式时只能
作 diagnostic。SGLang tree、allocator、movement、scheduler 和 model execution
即使被定位，也仍是 upstream observe-only。没有上层证据证明 GPU operator 是
bottleneck，就不进入 kernel 层。

## 8. Action → mediator → endpoint 的 manipulation check

必须在同一冻结 workload 中闭合：

~~~text
checked reclamation vs release-only action
  → physical demotion / allocator-visible headroom
  → scheduling capacity or measured interference
  → sustainable lambda and resumed/foreground endpoint
~~~

每次 forced-action 或 patch 回归单独报告：

1. Action：请求是否真的分离，admission 与 completion 是否一致；
2. Mediator：physical completion、free pages、headroom、queue/copy、
   restore/recompute 或 interference 是否按预测变化；
3. Endpoint：resumed TTFT、foreground ITL、success、lambda 是否响应。

action 未分离表示实验未操控成功；mediator 未变表示机制链断裂；mediator
变而 endpoint 不变最多是机制/资源结果；endpoint 变而 mediator 不变先判
混淆；endpoint 改善但 ITL、success、cleanup 或 correctness 退化不是 win。

## 9. 单槽条件优化纪律：拒绝通用 Demote Pacing 默认实现

当前没有证据授权通用 Demote Pacing。不要预建 `PacingController`、公共
pacing 参数、新 Gate 或新模块。开始改动前先回答：症状能否稳定复现？path
truth 是否足够？根因属于 Publication、checked reclamation 还是 Recovery？
candidate 能否控制？是否有 release-only baseline、falsifier、rollback、
deletion test 和 losing workload？任一答案为否，先补证据或 handoff；没有
可重复 bottleneck 就不实现额外 optimization patch。

G3/G4 的 conditional diagnosis 只有一个 slot，同一时刻至多准入一个
measurement-driven series：

| 被测症状 | 最小区分 | disposition |
|---|---|---|
| Publication 的 eager D2H 或 Host occupancy 是决定性成本 | 隔离 Publication timing/occupancy，保持后续 action 与 workload 可比 | 只有独立 accepted review 才能准入 **Tool-gap-triggered On-demand Publication with Pacing**；当前不授权 |
| checked reclamation 的逐节点 final check、release 或 free-drain 造成 scheduler/CPU/allocator interference | stage timing + CPU/allocator wait + headroom/endpoint manipulation check | 可在后续 SPEC revision 考虑 candidate-owned **Checked Reclamation Chunking** |
| Recovery/H2D 主导 resumed critical path | 先验证 fixed-pin restore/load_back 实际路径，再 profile H2D/compute overlap | 窄 layer-wise/substrate patch 若获准，baseline/candidate 两组共享，不算 ToolGap differential |
| polling wait 进入 completion critical path | polling interval/CPU 与 completion→headroom endpoint 对齐 | 只有此时 event-driven completion 才恢复候选资格 |

Checked Reclamation Chunking 也不是当前实现。其最窄候选语义是按每个
scheduler cycle 的 node/byte budget 分段，达到所需 allocator headroom 后停止；
resume 只能取消尚未开始的 chunks，已释放部分仍走正常 restore/recompute。
准入必须有独立 SPEC revision、ablation、deletion test 和 losing workload。

优化仍先删除不影响 allocator/scheduler 的工作，再减少实测 critical-path
同步、重复 bookkeeping 或共享资源干扰。任何 series 都必须在同一 workload
闭合 action → mediator → joint endpoint；memcpy 带宽、释放速度或
microbenchmark 不能单独判赢。人为缩小 KV pool 可制造受控压力，但 claim
还必须用真实 occupancy/headroom/eviction activity 说明 pressure，并声明
workload reachability。

candidate 可优化 operation identity、checked resolution、fencing、fallback、
cleanup、DecisionTrace overhead 和证据生成。SGLang 负责 physical tree、
allocator、movement、eviction、scheduler 和 model execution；定位到它们时，
默认是 diagnosis、substrate limitation 或 upstream handoff。任何影响两 arm
的 substrate patch 必须公平共享。slicing、coalescing、concurrent channels
和 PD transfer 继续属于
[`future/PD_TRANSFER_SLICE.md`](../future/PD_TRANSFER_SLICE.md)；L3/prefetch
不进入主线，dynamic selector 等 G5 admission。代码量不是 ownership。

## 10. 生命周期和 non-interference 是硬 guardrail

以下任一失败都不能由 QoS 或吞吐收益抵消：

| 场景 | 必须保持 |
|---|---|
| Resume before Host commit | 未 committed copy 不支持 reclamation |
| Resume during demotion | current identity 决定 restore/wait/recompute，不 double-own |
| Duplicate request | idempotent result 或显式 conflict |
| Cancel/Host-copy failure | 无 false committed state，operation resources cleanup |
| Shared-prefix target | 按 non-target coverage contract reject/clip |
| Running lock/pending transfer | defer/reject，不强制 demote |
| Tree mutation after resolution | execution-time eligibility recheck |
| Partial physical success | freed 与 retained targets 分开记账 |
| Late/stale completion | 不改变新 state，但释放旧资源并记录 terminal |

最小 non-interference 比较是 stock ordinary request、candidate build 的
ordinary bypass 和 trace-enabled diagnostic run；另在相同 Host copy、
workload、instrumentation 和 stock eviction 下比较 release-only 与 forced
checked reclamation。trace、ID、buffer 和 collector 不得改变 tree key、batch、
retry、scheduler、movement、output 或 cleanup semantics。profile-on 不进入
正式 benchmark。

## 11. RCA 和停止纪律

真实异常按一个可证伪核心问题建 RCA，而不是按工具或 run 命名。最小记录：

| 部分 | 内容 |
|---|---|
| Symptom/Reproduction | expected/observed endpoint、run/pair、regime、source/build、arrival、capacity、warm-up/drain、profile state |
| Path truth | operation identity、Host commit、resolution、physical completion、allocator/headroom、resume/recompute、output、cleanup |
| Hypotheses | 主解释、替代解释、order/workload/instrumentation 混淆；prediction、discriminator、falsifier |
| Source mapping | pinned symbol、状态转换、candidate/upstream ownership；source fact 与 runtime observation 分开 |
| Validation | action、mediator、endpoint；same workload before/after；correctness、ITL、success、cleanup、losing regime |
| Disposition | 最小 patch、rollback、deletion test、handoff、STOP 或明确 unresolved |
| Artifacts | manifest checksum、run IDs、raw logs/traces、analysis version、profile exclusion、失败 run、remaining uncertainty |

根因句式应是：

~~~text
在固定 workload/regime 中，action 改变了 physical/runtime mediator，
该 mediator 通过 critical-path 或 shared-resource 依赖改变 endpoint；
alternative 被区分实验排除；结论不适用于已保留的 losing boundary。
~~~

不能排除主要替代解释时，写“当前异常无法可靠归因”，不要用截图、相关性
或“统计不显著”补齐因果链。

必须保留 low pressure、small/private KV、stock eviction 已及时、restore 输给
recompute、shared-prefix-heavy、foreground interference、trace污染和
inconclusive runs。不能产生 allocator-visible headroom、删除 candidate 后
行为仍存在、cleanup 不闭合，或 checked reclamation 不能超过 release-only
baseline 时，应收敛到 diagnosis/upstream contribution 或 STOP，而不是增加
policy、L3、Mooncake、prefetch 或其他 scope 外机制。

## 12. 迁移账本：复用方法，不搬运旧运行时事实

| 旧来源 | 迁移到本文 | 拒绝迁移 |
|---|---|---|
| PERFORMANCE_ENGINEERING_PLAYBOOK.md | 症状优先、path truth、critical path/overlap、竞争假设、工具阶梯、因果链、RCA、STOP | Shared-L3/Mooncake/L1-L3 publication 语义、旧 Gate 和旧数字 |
| PERFORMANCE_PATH_AND_OPTIMIZATION_MAP.md | owner/observe-only/handoff、direct vs indirect path、logical/physical/endpoint 分层 | 旧 SGLang/Mooncake 调用链、remote availability/eviction、D1 object map |
| OBSERVABILITY_AND_MEASUREMENT_CONTRACT.md | opaque identity、显式 join、monotonic clock、terminal/cleanup、missing/loss、online/post-hoc 隔离 | observation/decision/StorageOperation schema、pre-collapse Put、L3 payload 指标 |
| RUNTIME_INVARIANT_FAILURE_MATRIX.md | unique owner、terminal 不等于 cleanup、absence proof、race/failure/shutdown/late callback、证据层级 | Mooncake/Store failure 语义、旧 L3 operation/queue/protection 状态机 |
| RCA_CASEBOOK.md / RCA_TEMPLATE.md | symptom 命名、falsifier、source mapping、root cause、negative result、artifact、claim ceiling | RCA 编号、旧 Gate 字段、S1/S2/S3 标记 |

当前 canonical 文档的职责不变：

- [ARCHITECTURE.md](../ARCHITECTURE.md)：SGLang pin、组件边界和 ownership；
- [DEMOTION_CONTRACT.md](../DEMOTION_CONTRACT.md)：eligibility、non-target
  protection、linearization、fallback、failure/race、cleanup；
- [EVALUATION.md](../EVALUATION.md)：baseline、joint SLO、workload、统计、
  trace boundary 和 artifact；
- [PERFORMANCE_BOUNDARY.md](../PERFORMANCE_BOUNDARY.md)：G4 结果与 losing
  axes；
- [ROADMAP.md](../ROADMAP.md)：G0–G5 decision question 和停止分支。

以下内容明确不是当前证据：旧 Agentic-KV/Mooncake/vLLM pin、first-C0、
Shared-L3、D1、D14、S1–S3、new-physical-Put bytes、ALWAYS_ADMIT/
ALWAYS_DROP、L3/remote eviction、固定百分比和旧 benchmark。文档、source
audit、mock、simulator、trace replay 和 microbenchmark 可以分别支撑实现
验证、simulated 结果或诊断证据，但不能单独把真实引擎机制或性能结果升级为
shipped 或 experimentally validated。

## 13. 提交前检查

- [ ] 相关 G0–G2 artifact 存在，本文没有升级 claim state。
- [ ] 症状、baseline、arrival、pressure、coldness、arm order 和窗口可复现。
- [ ] operation identity、Host commit、legal target、physical completion、allocator delta、cleanup 可关联。
- [ ] direct critical path 与 shared-resource path 分开，overlap 未被求和。
- [ ] QoS 作为约束/guardrail 使用，没有 weighted score 抵消违规。
- [ ] action、mediator、endpoint 三层 manipulation check 分开报告。
- [ ] profile 与 benchmark 分离，loss、missing terminal、error、hang、censoring 保留。
- [ ] patch 有 rollback、deletion test、correctness/cleanup regression 和 losing regime。
- [ ] upstream 根因仅形成 diagnosis、handoff 或 owner review，没有静默扩 scope。
- [ ] raw artifact、manifest、analysis version 和不确定性可追溯。

最终判断很简单：先证明 checked demotion 改变了真实物理中介，再判断它是否
改变联合服务端点；中介或 guardrail 不成立时，停止优化并保留负结果。
