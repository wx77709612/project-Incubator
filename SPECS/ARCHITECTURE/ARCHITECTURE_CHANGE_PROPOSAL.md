> 作用域（2026-10-19）：本文保留 V1.x Legacy 兼容设计/回归语义，不定义 Plugin 0.3.x 的状态权威、入口或执行机制。现行 Kernel 规则由 [Kernel Alignment ACP](../ARCHITECTURE/KERNEL_ALIGNMENT_CHANGE_PROPOSAL.md) 及其 Design、Contract、Runtime 和两份 Plan 约束；冲突条款已被 Decision 015 明确替代。非冲突的 Maker Authority、Evidence 和领域方法可作为参考。

# Project Incubator V1.1 Architecture Change Proposal

## 1. 文档状态

| 字段 | 值 |
| --- | --- |
| Specification Version | V1.1 |
| Status | APPROVED |
| Previous Baseline | `SPECS/_V1.0/` |
| Change Type | Core Evolution + Capability Extension |
| Implementation Authorization | NOT GRANTED |
| Maker Approval Date | 2026-09-23 |

本文档整合本轮已经讨论并原则同意的方向，作为正式修改 Architecture、Design、Contract、Runtime Specification 与 Implementation Plan 前的书面审阅基线。

## 2. 变更动机

V1.0 的线性阶段与 Artifact 完成模型适合契约明确、结果可由本地验证推导的能力。但在依赖外部宿主、隐藏状态、非确定性执行环境、不完整契约或人工验证的 Capability 中，V1.0 存在以下结构性缺口：

- 文档或 API 证据可能被表述为完整产品能力；
- Runtime Assumption 容易被写成近似冻结的 Decision；
- P4 Creation 中发现模型错误时缺少轻量、正式的纠偏路径；
- 验证 helper 可调用后可能过早展开横向实现；
- Decision、设计、实现和真实行为可能长期漂移；
- 重复失败不会自动触发模型重审；
- 已确认工作的目标环境路径缺少回归基线；
- 人工验证成本没有进入规划与停止条件。

V1.1 的目标不是把所有项目改造成重型实验流程，而是让 Core 能够识别“什么时候不能继续假装已知”，并为高不透明 Capability 提供按需启用的证据获取方法。

## 3. 设计边界

### 3.1 Core

以下能力进入 Project Incubator Core：

1. Capability Claim；
2. Evidence Maturity E0-E5；
3. Decision、Assumption、Observation 与 Hypothesis 分离；
4. P4 内部的 Creation Correction Loop；
5. Decision Supersession 的活动视图与有界历史；
6. Repeated Failure / Model Review Trigger；
7. Known-Good Baseline 的识别与回归保护规则；
8. Artifact / Implementation / Evidence / Decision Drift 检查；
9. Confidence 可升可降；
10. Validation Cost Awareness。

### 3.2 Opaque Capability Extension

以下能力仅在 Capability 达到启用条件时生效。中文名称是规格正文中的主名称；括号中的英文 Identifier 仅用于跨文档追踪和后续结构化字段命名。

| 中文名称 | Identifier | 解决的问题 | 主要输出 | 责任边界 |
| --- | --- | --- | --- | --- |
| 能力级不透明度评估 | `OPACITY_ASSESSMENT` | 判断特定 Capability 是否无法仅凭稳定契约和本地验证推导最终产品结果 | 评估维度、证据、风险等级、Extension 启用建议 | Agent 提案，Maker 确认可接受成本与边界；Runtime 不自动判断语义风险 |
| 产品点螺旋验证 | `PRODUCT_POINT_SPIRAL` | 围绕用户可感知结果逐圈收紧能力边界、模型和证据 | 当前圈目标、扩展维度、闭合结果 | Extension 工作方法，不是新 Phase 或 Runtime 状态机 |
| 发现轮 | `DISCOVERY_RING` | 在真实模型未知时，以狭窄完整场景发现事实和候选模型 | Observation、Candidate Model、Assumption、未解释异常 | Agent 设计与执行；一次成功不得直接声明能力成立 |
| 验证轮 | `VALIDATION_RING` | 验证已有 Candidate Model 能否解释代表性变体与失败路径 | 代表性场景结果、反例、Evidence Level 变化 | Agent 设计；Gate 只检查证据是否满足 Claim，不替代语义判断 |
| 假设区分设计 | `HYPOTHESIS_DISCRIMINATION` | 避免收集无法区分竞争解释的低价值信息 | 假设、成立信号、不成立信号、区分证据 | Agent 负责；Runtime 仅验证记录结构 |
| 可观察性计划 | `OBSERVABILITY_PLAN` | 确定目标环境中需要观察的边界、生命周期、结果与异常 | 关联标识、观察点、采样范围、体积限制、停止条件 | 属于 Design / Planning；诊断不得改变被观察行为 |
| 证据到可重复验证闭环 | `EVIDENCE_TO_VERIFICATION_LOOP` | 将真实异常转化为可重复的模型、决策或边界回归验证 | 最小 Fixture / Trace、失败重现、修复后回归结果 | Agent 提取和归一化；Script 只能验证已建模输入 |
| 单圈闭合检查 | `RING_CLOSURE_CHECK` | 防止只完成代码或局部调用就扩展下一圈 | Claim、Evidence、Baseline、异常与未覆盖范围检查结果 | Gate / Advisory 可检查完整性；Maker 保留产品边界决定权 |
| 目标环境已知可用基线 | `TARGET_ENVIRONMENT_BASELINE` | 保存目标环境中已确认工作的版本、场景、交付物和证据 | Baseline ID、适用边界、环境、证据、回归集合 | Core 定义触发规则，Optional Context 保存记录，Extension 定义环境细节 |
| 人工验证预算 | `HUMAN_VALIDATION_BUDGET` | 控制依赖 Maker、设备或外部宿主的验证成本 | 单次成本、批次、次数上限、证据要求、停止条件 | Planning 与 Maker 协作协议；Runtime 不替 Maker 执行判断 |
| 兼容性扩展轮 | `COMPATIBILITY_EXPANSION_RING` | 沿版本、环境或平台维度扩展已验证边界 | 兼容范围、代表性组合、排除范围、兼容证据 | 按风险启用，不要求所有项目生成完整兼容矩阵 |

Extension 按 Capability 激活，不把整个 Project 永久标记为“不透明项目”。同一项目内可以同时存在透明能力和不透明能力。

### 3.3 Optional Context

高风险 Capability 可以创建轻量 `Capability Spiral Record`。它属于 Optional Context / Extension Artifact，不替代 Core Context，也不成为第二份项目状态 Source of Truth。透明、低风险项目不得被强制创建该记录。

## 4. 核心领域概念

### 4.1 Product Point

最小但具有用户意义的产品能力，必须说明谁在什么条件下执行什么行为、预期可观察结果、失败结果和当前不承诺的范围。

### 4.2 Capability Claim

对 Product Point 当前支持边界的正式声明。至少包含 Supported Boundary、Excluded Boundary、Required Evidence Level、Current Evidence Level、Confidence 和 Known Limitations。

### 4.3 Candidate Model

用于解释和实现 Product Point 的最小候选模型。它是可被证据推翻的 Runtime Assumption 集合，不是默认 Architecture Decision。

### 4.4 Known-Good Baseline

经适当目标环境证据确认、在明确 Capability Boundary 内表现符合预期的版本、场景、交付物和证据集合。

Core 规定何时必须识别 Baseline、何时进行回归影响分析；Optional Context 保存项目级记录；Opaque Capability Extension 定义目标环境细节。

## 5. Evidence Maturity

| Level | 含义 | 可支持的结论上限 |
| --- | --- | --- |
| E0 | 推测或未经验证的假设 | 只能陈述 Hypothesis |
| E1 | 文档、规范、公开契约或源码支持 | 可陈述接口或规则有依据，不可声明产品语义成立 |
| E2 | 隔离实验、局部调用或本地自动化成功 | 可声明局部机制可用，不可声明完整目标环境能力 |
| E3 | 单个完整目标环境场景成功 | 可声明该场景 Observed Working，不可声明代表性稳定 |
| E4 | 代表性变体与关键失败路径通过 | 可在已声明边界内标记 Representative Boundary Validated |
| E5 | 重复、长期、兼容性或真实使用证据 | 可声明对应时间、版本与使用边界内的稳定性 |

约束：Artifact 完成不自动提升 Evidence Level；API 可用不等于语义能力成立；自动化验证不替代目标环境证据；未覆盖范围必须缩小 Claim；Confidence 可随反证降低；Evidence Level 绑定具体 Claim 与 Scope。

## 6. P4 Creation Correction Loop

### 6.1 语义

Creation Correction Loop 是 P4 内部的可选纠偏活动，不是新的 Core Phase，不进入 P6 Iteration，也不正式回退到完整 P2 / P3。

### 6.2 触发条件

Correction Loop 不要求 Runtime 理解技术事实。它采用“确定性信号 + Agent 结构化判断 + Maker 权威确认”的混合判定。

每次候选异常至少记录：

```text
capability_id
scenario_id
boundary_step
observed_outcome
evidence_refs
affected_assumption_ids
affected_artifacts
failure_signature
```

`failure_signature` 由以下稳定字段组成：

```text
capability_id + scenario_id + boundary_step + observed_outcome
```

推测根因不得进入 `failure_signature`，避免通过改变解释绕过重复失败计数。

| Trigger | 判定主体 | 可执行规则 | 结果 |
| --- | --- | --- | --- |
| 相同 Failure Signature 连续失败 | Runtime 计数 | 连续 2 次失败 | `MODEL_REVIEW_ADVISORY` |
| 相同 Failure Signature 继续失败 | Runtime 计数 | 连续 3 次失败 | 暂停同方向修补，输出 `P4_CORRECTION_REQUIRED` |
| Known-Good 场景由通过变为失败 | 自动化验证或目标环境记录 | 同一 Baseline Scenario 出现 Pass → Fail | 立即输出 `P4_CORRECTION_REQUIRED` 并要求回归影响分析 |
| Evidence 推翻 Runtime Assumption | Agent 语义判断 | 提交 Assumption ID、Evidence Ref 和矛盾说明，结构检查通过 | 进入 Correction Review；Runtime 不判断解释真伪 |
| 实现出现 Active Design 未定义的领域对象或关系 | Agent 语义判断 | 提交 Drift Type 与受影响文档 | 进入 Correction Review |
| 文档引用、字段或 Artifact 结构漂移 | Script 确定性检查 | 违反已批准 Schema、引用或结构规则 | 报告 Structural Drift |
| Design、Decision、Implementation 与 Evidence 语义冲突 | Agent 语义判断 | 提交冲突双方与 Evidence Ref | 报告 Semantic Drift，Script 不自动裁决 |

“连续失败”指两次失败之间没有出现同一 Signature 的成功结果，也没有完成 Candidate Model 修订。Candidate Model 正式更新后，旧计数随原模型归档，新模型重新计数。

Project Type Profile 可以将 2/3 次阈值收紧，但不得放宽 Core 默认阈值。

### 6.3 内部活动

1. 暂停受影响工作项，不改变 `current_phase = P4`；
2. 记录反例、Observation 与失效 Assumption；
3. 执行 Model Correction；
4. 识别受影响的 Claim、Design、Decision 与 Baseline；
5. 执行 Execution Replanning；
6. 更新最小必要文档和验证资产；
7. 执行 Drift、Authority 与 Scope 检查；
8. Maker 确认需要其授权的产品或架构变化；
9. 恢复 P4 中受影响工作。

### 6.4 输出

- Invalidation Record；
- 修订后的 Candidate Model；
- 受影响范围与局部执行计划；
- 需要重放的 Repeatable Verification；
- 需要重做的目标环境场景；
- Baseline 与 Confidence 变化；
- 未解决风险和停止条件。

Runtime 可识别的 Correction Assessment Result 仅包含：

```text
NO_CORRECTION
MODEL_REVIEW_ADVISORY
P4_CORRECTION_REQUIRED
MAKER_SCOPE_REVIEW_REQUIRED
```

这些结果不直接产生 Phase Transition，也不直接修改 Core Context。

### 6.5 升级条件

升级判断必须使用结构化 Impact Assessment，不允许只记录“影响较大”或“无法限定”。

```text
changes_product_goal: boolean
changes_success_criteria: boolean
changes_maker_approved_scope: boolean
changes_core_phase_model: boolean
changes_context_authority: boolean
changes_runtime_invariant: boolean
crosses_current_work_package: boolean
affected_scope_identified: boolean
regression_set_identified: boolean
```

满足以下全部条件时，Correction 保持在 P4 内部：

- 前六个 `changes_*` 字段均为 `false`；
- `crosses_current_work_package = false`；
- `affected_scope_identified = true`；
- `regression_set_identified = true`；
- 所需变化只影响 Runtime Assumption、Candidate Model、局部 Design、Implementation Detail 或局部执行计划；
- 如局部变化涉及 Architecture Decision，已取得 Maker 对该决策变化的确认。

满足以下任一条件时，输出 `MAKER_SCOPE_REVIEW_REQUIRED`：

- 任一 `changes_*` 字段为 `true`；
- `crosses_current_work_package = true`；
- `affected_scope_identified = false`；
- `regression_set_identified = false`。

Runtime 只验证结构、计数、依赖集合和授权证据，不自行判断产品目标、设计语义或技术解释。由 Agent 提交 Impact Assessment；涉及产品或架构权威时，由 Maker 确认。

`MAKER_SCOPE_REVIEW_REQUIRED` 也不自动跳转 P2/P3。Maker 决定扩大局部纠偏范围、暂停当前 Capability，或正式重开完整设计流程。

P4 不新增到 P2/P3 的常规 Transition；Correction Loop 也不得伪装成缩小版完整 Phase。

## 7. Decision 与 Assumption

| 类型 | 权威 | 变化方式 |
| --- | --- | --- |
| Product Decision | Maker | 改变需 Maker 明确确认 |
| Architecture Decision | Maker 确认，Agent 可提案 | 通过 Architecture Change Control 更新 |
| Runtime Assumption | Evidence | 可直接被支持、降级或判定失效 |
| Implementation Detail | Agent | 在有效设计与计划边界内调整 |
| Observation | 事实记录 | 不自动转化为解释 |
| Hypothesis | 临时解释 | 通过区分证据验证或推翻 |

Decision 历史不采用无限 append-only 单文档。采用 Active Decision View、Bounded Changelog、Archived Decision History 与 Stable Decision ID。

状态支持 `ACTIVE`、`PARTIALLY_SUPERSEDED`、`SUPERSEDED`、`REVOKED`；关系字段支持 `Supersedes`、`Affected Decisions`、`New Evidence`、`Effective Scope`、`Migration Impact`。

## 8. Model Review 与 Drift

相同 Failure Signature 连续 2 次失败时触发 Model Review Advisory；连续 3 次失败时停止同方向修补并要求 P4 Correction。Known-Good 回归、真实证据与 Active Design 冲突，或代码形成未记录领域模型时，不等待次数阈值，立即进入 Correction Review。

Model Review 暂停同方向增量修补，定位最早依赖失效假设的范围，更新模型，重放受影响验证，并重新建立 Baseline 与 Confidence。

Drift 检查至少比较 Capability Claim、Active Design、Active Decisions、Implementation、Repeatable Verification、Target-Environment Evidence 和 Known-Good Baseline。

Advisory 只负责提示、解释与建议，不直接修改 Workflow、Context 或 Runtime State。

## 9. Opaque Capability Extension

### 9.1 启用评估

Opacity Assessment 按契约、状态、执行控制权、确定性、可观察性、可自动化、失败可归因性、版本与环境稳定性评估 Capability。Agent 基于证据提出建议；Maker 确认可接受的人工成本、支持边界和风险。

### 9.2 Vertical Slice 抽象

Core 不列举安装、UI 注入、存档等领域步骤。代表性端到端产品路径必须从用户可识别的触发开始，穿过主要不透明边界，到达用户可观察结果，并具备最小可重复验证与目标环境证据。

领域 Profile 可以定义常见路径，但不得把领域枚举写入 Core。

### 9.3 Spiral Ring

每圈围绕同一 Product Point 同步维护 Capability Boundary、Domain Model、Implementation、Repeatable Verification、Observability、Real-Environment Evidence、Confidence 与 Baseline。每圈只重点扩展一个主要风险维度。

## 10. Validation Cost Awareness

Planning 必须识别 Agent 可自动完成的验证、依赖 Maker 或外部环境的验证、单次成本与建议批次、失败后最小证据、重复测试上限与停止条件，以及可转化为 Fixture 或 Trace Replay 的结果。

Maker 提供 Agent 无法获得的目标环境观察，但不承担技术根因推导、证据结构设计或历史路线检查。

## 11. 文档与实现影响

- Architecture：更新 Document Architecture 和 Architecture Decisions；
- Design：新增 Evidence Model Design，更新 Workflow、Context、Gate、Advisory，新增 Opaque Capability Extension；
- Contract：定义新 Context、P4 内部纠偏、证据 Gate 与脚本证据边界；
- Runtime：定义 Correction Loop、Evidence/Confidence、Drift 与 Extension Activation；
- Skill Package：后续预计修改 Skill、JSON references、Templates、Runtime components 与 Tests。

具体产品文件范围必须由后续 Implementation Plan 冻结，本提案不直接授权修改 `PROJECT_INCUBATOR/`。

## 12. 兼容与迁移策略

- V1.0 项目不要求一次性回填全部 Claim 或历史 Evidence；
- 下一次修改触及高风险 Capability 时，才为其建立 Claim、Evidence 与 Baseline；
- 透明、低风险项目继续使用轻量流程；
- Core Phase P0-P6 与 `PROJECT_STATE.md` Authority 保持不变；
- 新字段和 Optional Context 必须允许缺省；
- 发布 V1.1 前必须证明 V1.0 正常路径未被破坏。

## 13. 非目标

V1.1 不强制所有项目启用 Spiral，不永久分类整个项目，不新增 Core Phase，不让 P4 常规跳回 P2/P3，不让 Advisory 直接控制 Runtime，不让自动化测试替代目标环境语义证据，也不要求 Maker 重复执行没有区分度的人工测试。

## 14. 书面规格验收标准

下游规格必须能够：

- 阻止 E0-E2 被表述为完整目标环境能力；
- 阻止 Runtime Assumption 被隐式冻结为 Decision；
- 在 P4 内完成有界、可追踪、可恢复的模型纠偏；
- 对高不透明 Capability 建议 Extension，但不增加低风险项目负担；
- 区分自动化验证和目标环境证据的结论边界；
- 在重复失败时触发 Model Review；
- 在高风险修改前识别 Known-Good Baseline；
- 发现 Claim、Design、Decision、Implementation 和 Evidence Drift；
- 允许 Decision 正式失效并控制历史体积；
- 保持 Maker 权威与 V1.0 Runtime Invariant。

## 15. 待 Maker 审阅结论

已确认：

1. 本提案基本准确固化此前讨论结果；
2. Active Decision View + Bounded Changelog + Archive 可作为正式策略；
3. P4 Correction Loop 采用确定性信号、Agent 结构化判断与 Maker 权威确认的混合判定；
4. 重复失败默认在连续 2 次时触发 Advisory、连续 3 次时强制暂停同方向修补；Project Type Profile 只能收紧阈值；
5. Extension 使用中文主名称和稳定 Identifier，并要求明确职责、输入输出、持久化与自动化边界。

Maker 已于 2026-09-23 确认：

1. P4 Correction Loop 的结构化 Trigger、Result 与 Impact Assessment 可以进入下游 Design；
2. Core / Extension / Optional Context 的职责划分可以进入下游 Design。

本次批准只授权继续修改 Architecture 与 Design 文档，不自动授权产品实现。
