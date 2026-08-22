# Project Incubator V1 Workflow Contract

# 1. Contract Purpose

本文档定义 Project Incubator V1 的 Workflow Runtime Interface。

本文档属于：

Contract Layer。

本文档负责定义：

- Workflow Schema；
- Phase Interface；
- Transition Contract。

本文档将已经冻结的 Workflow Domain Model 转化为 Runtime 可以消费的交互契约。

本文档不重新定义：

- Workflow Model；
- Core Phase；
- Phase Goal；
- Phase Lifecycle；
- Phase Process；
- Artifact Flow；
- Allowed Next Phase；
- Context Authority；
- Gate Definition。

Workflow Domain Model 由：

`SPECS/DESIGN/PROJECT_INCUBATOR_V1_WORKFLOW_DESIGN.md`

定义。

Context Access Permission 由：

`SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md`

定义。

Gate Evaluation Contract 由：

`SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_GATE_CONTRACT.md`

定义。

Workflow 的具体 Runtime 执行机制由：

`SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`

定义。

---

# 2. Workflow Contract Model

## 2.1 Workflow Identity

Project Incubator V1 Core Workflow 的 Contract Identity 为：

`PROJECT_INCUBATOR_V1_CORE_WORKFLOW`

对应的领域 Workflow 为：

Project Incubator V1 Workflow。

该 Contract Identity 只用于 Runtime 识别当前消费的 Workflow Definition。

不改变 Workflow Domain Model。

---

## 2.2 Workflow Contract Responsibility

Workflow Contract 向 Runtime 暴露以下信息：

- Workflow Identity；
- Core Phase Set；
- Phase Relationship；
- Current Phase Reference；
- Phase Lifecycle Reference；
- Phase Input Requirement；
- Phase Output Reference；
- Required Artifact Requirement；
- Context Mutation Requirement；
- State Change Requirement；
- Gate Trigger Requirement；
- Allowed Next Phase；
- Transition Request；
- Transition Eligibility Information。

Workflow Contract 不执行：

- Phase Process；
- Phase Transition；
- Context Mutation；
- Gate Evaluation；
- Artifact Writeback；
- Runtime State Mutation。

---

## 2.3 Core Phase Set

Project Incubator V1 Core Workflow 固定包含：

| Phase ID | Phase Name |
| --- | --- |
| P0 | Intent Discovery |
| P1 | Project Definition |
| P2 | Solution Design |
| P3 | Execution Planning |
| P4 | Creation |
| P5 | Validation |
| P6 | Iteration |

Runtime 不得通过 Workflow Contract：

- 删除 Core Phase；
- 重命名 Core Phase Identity；
- 创建新的 Core Phase；
- 修改 Core Phase 基础目标。

---

## 2.4 Core Phase Relationship

Core Workflow 的标准关系固定为：

```text
P0 Intent Discovery
        ↓
P1 Project Definition
        ↓
P2 Solution Design
        ↓
P3 Execution Planning
        ↓
P4 Creation
        ↓
P5 Validation
        ↓
P6 Iteration
```

P6 Iteration 允许请求返回：

```text
P2 Solution Design
P3 Execution Planning
P4 Creation
P5 Validation
```

除此之外：

Core Workflow Contract 不允许其他 Transition Path。

---

## 2.5 Allowed Transition Matrix

| Current Phase | Allowed Next Phase |
| --- | --- |
| P0 Intent Discovery | P1 Project Definition |
| P1 Project Definition | P2 Solution Design |
| P2 Solution Design | P3 Execution Planning |
| P3 Execution Planning | P4 Creation |
| P4 Creation | P5 Validation |
| P5 Validation | P6 Iteration |
| P6 Iteration | P2 Solution Design |
| P6 Iteration | P3 Execution Planning |
| P6 Iteration | P4 Creation |
| P6 Iteration | P5 Validation |

任何不在该表中的 Transition Request：

必须被识别为：

`TRANSITION_NOT_ALLOWED`

不得由 Runtime 自行增加 Transition Path。

---

# 3. Workflow Schema

## 3.1 Workflow Schema Definition

Runtime 消费 Workflow Definition 时，Workflow Schema 必须能够表达：

- Workflow Identity；
- Core Phase Set；
- Phase Definitions；
- Phase Relationship；
- Current Phase Reference；
- Phase Lifecycle Reference；
- Required Artifact Requirement；
- State Change Requirement；
- Gate Trigger Requirement；
- Allowed Next Phase。

Workflow Schema 是逻辑 Contract。

本文档不定义：

- JSON；
- YAML；
- 数据库存储格式；
- Runtime Loader；
- 文件序列化方式。

---

## 3.2 Phase Definition Schema

每一个 Core Phase Definition 必须暴露：

- Phase ID；
- Phase Name；
- Phase Goal；
- Input；
- Process Boundary；
- Output；
- Required Artifact；
- Context Mutation；
- State Change Requirement；
- Gate Trigger Requirement；
- Allowed Next Phase。

Runtime 不得缺省任何上述 Core Field。

---

## 3.3 Phase Lifecycle Reference

Workflow Contract 可以引用以下已经冻结的 Phase Lifecycle State：

- `Not Started`；
- `Active`；
- `Awaiting Gate`；
- `Completed`；
- `Reopened`。

Workflow Contract 不重新定义这些状态的领域语义。

Phase Lifecycle Reference 只用于：

让 Runtime 识别当前 Workflow 中已经存在的 Phase Lifecycle 状态。

---

## 3.4 Current Phase Reference

Current Phase Reference 必须能够表达：

- Workflow Identity；
- Phase ID；
- Phase Name；
- Phase Lifecycle State；
- Project State Reference。

Current Phase 的项目事实来源必须是：

`PROJECT_STATE.md`。

Workflow Contract 不允许 Runtime：

使用 Runtime Temporary State 替代 `PROJECT_STATE.md` 判断项目当前 Phase。

Current Phase Reference：

只引用当前状态。

不执行状态修改。

---

# 4. Core Phase Contract Definitions

# 4.1 P0 Intent Discovery

## 4.1.1 Phase Identity

Phase ID：

`P0`

Phase Name：

`Intent Discovery`

---

## 4.1.2 Phase Goal

明确 Maker 创建项目的目标。

包括确认：

- 为什么创建；
- 解决什么问题；
- 服务什么对象；
- 成功标准是什么。

---

## 4.1.3 Phase Input

P0 Phase Input 必须能够引用：

- Maker Idea；
- Initial Requirement；
- Background Information。

P0 不要求已有 Core Context 作为进入 Phase 的固定前置输入。

---

## 4.1.4 Process Boundary

P0 Process Boundary 包括：

Agent：

- 理解用户目标；
- 发现关键问题；
- 澄清项目边界。

Maker：

- 确认项目方向；
- 确认成功标准。

Workflow Contract 不定义：

Agent 如何完成上述分析或 Maker 如何进行交互。

---

## 4.1.5 Phase Artifact Output 与 Context Mutation

P0 Phase Artifact Output：

- 无。

P0 Context Mutation：

- 建立或更新 `PROJECT_PROFILE.md`；
- 建立或更新 `PROJECT_STATE.md`。

---

## 4.1.6 Required Artifact

P0 Required Artifact：

`PROJECT_PROFILE.md`

在提出 P0 → P1 Transition Request 前：

`PROJECT_PROFILE.md`

必须已经存在，或者已经完成当前 P0 所要求的更新。

---

## 4.1.7 State Change Requirement

P0 完成必要 Process 后：

必须形成 State Change Requirement。

---

## 4.1.8 Gate Trigger Requirement

P0 以下事件形成 Gate Trigger Requirement：

- 提出 P0 → P1 Transition Request；
- `PROJECT_PROFILE.md` 发生影响后续 Workflow 推进的变化；
- P0 提出影响项目当前状态的 State Change Requirement。

---

## 4.1.9 Allowed Next Phase

唯一 Allowed Next Phase：

`P1 Project Definition`

---

# 4.2 P1 Project Definition

## 4.2.1 Phase Identity

Phase ID：

`P1`

Phase Name：

`Project Definition`

---

## 4.2.2 Phase Goal

建立项目执行上下文。

---

## 4.2.3 Phase Input

P1 Phase Input：

- `PROJECT_PROFILE.md`

---

## 4.2.4 Process Boundary

P1 Process Boundary：

建立：

- 项目状态；
- 项目约束；
- 当前执行范围。

Workflow Contract 不定义上述内容的生成实现。

---

## 4.2.5 Phase Artifact Output 与 Context Mutation

P1 Phase Artifact Output：

- 无。

P1 Context Mutation：

- 建立或更新 `PROJECT_STATE.md`。

---

## 4.2.6 Required Artifact

P1 Required Artifact：

`PROJECT_STATE.md`

---

## 4.2.7 State Change Requirement

P1 完成必要 Process 后：

必须形成 State Change Requirement。

---

## 4.2.8 Gate Trigger Requirement

P1 以下事件形成 Gate Trigger Requirement：

- 提出 P1 → P2 Transition Request；
- `PROJECT_STATE.md` 发生影响后续 Workflow 推进的变化；
- P1 提出影响项目当前状态的 State Change Requirement。

---

## 4.2.9 Allowed Next Phase

唯一 Allowed Next Phase：

`P2 Solution Design`

---

# 4.3 P2 Solution Design

## 4.3.1 Phase Identity

Phase ID：

`P2`

Phase Name：

`Solution Design`

---

## 4.3.2 Phase Goal

形成项目解决方案设计。

---

## 4.3.3 Phase Input

P2 Phase Input：

- `PROJECT_PROFILE.md`；
- `PROJECT_STATE.md`。

---

## 4.3.4 Process Boundary

P2 Process Boundary：

定义：

- 解决方案；
- 系统边界；
- 技术方向；
- Design Artifact；
- Decision Proposal。

Workflow Contract 不定义 Solution Design 的具体设计过程。

---

## 4.3.5 Phase Artifact Output 与 Context Mutation

P2 Phase Artifact Output：

P2 可以形成：

- Design Document；
- Solution Definition；
- Decision Proposal。

Decision Proposal：

只有在存在需要 Maker 确认的重要决策时才产生。

经过 Maker 确认的重要决策：

记录至：

`PROJECT_DECISIONS.md`。

P2 Context Mutation：

- Maker 确认重要决策时，更新 `PROJECT_DECISIONS.md`；
- 更新 `PROJECT_STATE.md` 中的当前 Phase 状态。

---

## 4.3.6 Required Artifact

P2 Required Artifact：

`Solution Design Artifact`

Solution Design Artifact 至少由：

- Design Document；
- Solution Definition

组成。

Decision Proposal：

不是所有 P2 Transition 的固定 Required Artifact。

---

## 4.3.7 State Change Requirement

P2 完成必要 Process 后：

必须形成 State Change Requirement。

---

## 4.3.8 Gate Trigger Requirement

P2 以下事件形成 Gate Trigger Requirement：

- 提出 P2 → P3 Transition Request；
- Solution Design Artifact 发生影响后续 Workflow 推进的变化；
- P2 提出影响项目当前状态的 State Change Requirement。

---

## 4.3.9 Allowed Next Phase

唯一 Allowed Next Phase：

`P3 Execution Planning`

---

# 4.4 P3 Execution Planning

## 4.4.1 Phase Identity

Phase ID：

`P3`

Phase Name：

`Execution Planning`

---

## 4.4.2 Phase Goal

建立项目执行路线。

---

## 4.4.3 Phase Input

P3 Phase Input：

- `PROJECT_PROFILE.md`；
- `PROJECT_STATE.md`；
- `Solution Design Artifact`。

---

## 4.4.4 Process Boundary

P3 Process Boundary：

制定：

- Implementation Plan；
- Project Type 对应的实施任务拆解；
- 执行顺序；
- 依赖关系；
- Artifact 目标；
- 验证方式；
- PROJECT_PLAN.md 生命周期规划 Context Mutation。

---

## 4.4.5 Phase Artifact Output 与 Context Mutation

P3 Phase Artifact Output：

`Implementation Plan`

`Implementation Plan`：

- 属于 Phase Artifact；
- 用于将 Solution Design 转换为可执行实施方案；
- 不属于 Core Context；
- 不替代 `PROJECT_PLAN.md`；
- 具体结构由 Project Type 决定。

P3 可以同时形成以下 Context Mutation Requirement：

- 更新 `PROJECT_PLAN.md` 中的项目生命周期规划；
- 更新 `PROJECT_STATE.md` 中的当前 Phase 状态。

`PROJECT_PLAN.md`：

只表达项目生命周期规划。

不表达 Implementation Task Breakdown Artifact 或项目当前实际执行状态。

---

## 4.4.6 Required Artifact

P3 Required Artifact：

`Implementation Plan`

---

## 4.4.7 State Change Requirement

P3 完成必要 Process 后：

必须形成 State Change Requirement。

P3 Phase Completion 要求：

- `Implementation Plan` Artifact 已生成或完成本 Phase 所要求的更新；
- `PROJECT_PLAN.md` Context Mutation 已形成并在 Transition 执行时完成持久化；
- `PROJECT_STATE.md` 状态变更已在 Transition 执行时完成持久化。

---

## 4.4.8 Gate Trigger Requirement

P3 以下事件形成 Gate Trigger Requirement：

- 提出 P3 → P4 Transition Request；
- `Implementation Plan` 发生影响后续 Workflow 推进的变化；
- `PROJECT_PLAN.md` Context Mutation 影响项目生命周期规划；
- P3 提出影响项目当前状态的 State Change Requirement。

---

## 4.4.9 Allowed Next Phase

唯一 Allowed Next Phase：

`P4 Creation`

---

# 4.5 P4 Creation

## 4.5.1 Phase Identity

Phase ID：

`P4`

Phase Name：

`Creation`

---

## 4.5.2 Phase Goal

执行项目创建。

---

## 4.5.3 Phase Input

P4 Phase Input：

- `PROJECT_PROFILE.md`；
- `PROJECT_STATE.md`；
- `PROJECT_PLAN.md`；
- `Implementation Plan`。

---

## 4.5.4 Process Boundary

P4 根据：

- Project Type；
- 已确认生命周期规划；
- Implementation Plan

完成项目创建活动。

创建活动可以包括：

- 编码；
- 内容创作；
- Skill 开发；
- 文档生成；
- 其他项目活动。

Workflow Contract 不定义：

这些 Creation Activity 如何执行。

---

## 4.5.5 Phase Artifact Output 与 Context Mutation

P4 Phase Artifact Output：

`Project Artifact`

P4 Context Mutation：

- 更新 `PROJECT_STATE.md` 中的当前 Phase 状态。

---

## 4.5.6 Required Artifact

P4 Required Artifact：

`Project Artifact`

---

## 4.5.7 State Change Requirement

P4 完成必要 Process 后：

必须形成 State Change Requirement。

---

## 4.5.8 Gate Trigger Requirement

P4 以下事件形成 Gate Trigger Requirement：

- 提出 P4 → P5 Transition Request；
- Project Artifact 发生影响后续 Workflow 推进的变化；
- P4 提出影响项目当前状态的 State Change Requirement。

---

## 4.5.9 Allowed Next Phase

唯一 Allowed Next Phase：

`P5 Validation`

---

# 4.6 P5 Validation

## 4.6.1 Phase Identity

Phase ID：

`P5`

Phase Name：

`Validation`

---

## 4.6.2 Phase Goal

确认项目成果是否满足目标。

---

## 4.6.3 Phase Input

P5 Phase Input：

- Artifact；
- `PROJECT_PROFILE.md`；
- `PROJECT_PLAN.md`。

---

## 4.6.4 Process Boundary

P5 Process Boundary：

验证：

- Artifact 完整性；
- Intent 一致性；
- 质量要求；
- 项目约束。

Workflow Contract 不定义：

Validation 如何具体执行。

---

## 4.6.5 Phase Artifact Output 与 Context Mutation

P5 Phase Artifact Output：

`Validation Result`

P5 Context Mutation：

- 更新 `PROJECT_STATE.md` 中的当前 Phase 状态。

---

## 4.6.6 Required Artifact

P5 Required Artifact：

`Validation Result`

---

## 4.6.7 State Change Requirement

P5 完成必要 Process 后：

必须形成 State Change Requirement。

---

## 4.6.8 Gate Trigger Requirement

P5 以下事件形成 Gate Trigger Requirement：

- 提出 P5 → P6 Transition Request；
- Validation Result 产生或发生影响后续 Workflow 推进的变化；
- P5 提出影响项目当前状态的 State Change Requirement。

---

## 4.6.9 Allowed Next Phase

唯一 Allowed Next Phase：

`P6 Iteration`

---

# 4.7 P6 Iteration

## 4.7.1 Phase Identity

Phase ID：

`P6`

Phase Name：

`Iteration`

---

## 4.7.2 Phase Goal

根据 Validation Result 推进下一轮优化。

---

## 4.7.3 Phase Input

P6 Phase Input：

- Validation Result；
- `PROJECT_STATE.md`。

---

## 4.7.4 Process Boundary

P6 可以根据 Validation Result：

- 调整解决方案；
- 调整 Implementation Plan；
- 调整项目生命周期规划 Context；
- 修改 Artifact；
- 返回 Solution Design；
- 返回 Execution Planning；
- 返回 Creation；
- 返回 Validation。

Workflow Contract 不决定：

P6 应该选择哪个目标 Phase。

---

## 4.7.5 Phase Artifact Output 与 Context Mutation

Phase Artifact Output：

根据本轮 Iteration 的实际调整范围：

P6 可以更新：

- Solution Design Artifact；
- Implementation Plan；
- Project Artifact。

Context Mutation：

- 更新 `PROJECT_PLAN.md` 中的项目生命周期规划；
- 更新 `PROJECT_STATE.md` 中的当前 Phase 状态。

---

## 4.7.6 Required Artifact

P6 Required Artifact Requirement 包含：

- Validation Result；
- 本轮 Iteration 实际修改的 Workflow Artifact。

P6 不创建新的固定 Artifact Type。

---

## 4.7.7 State Change Requirement

P6 在提出 Phase Transition Request 时：

必须形成当前 Transition 所需要的 State Change Requirement。

State Change Requirement：

不得被解释为 Context 已经完成 Mutation。

---

## 4.7.8 Gate Trigger Requirement

P6 以下事件形成 Gate Trigger Requirement：

- 提出 P6 → P2 Transition Request；
- 提出 P6 → P3 Transition Request；
- 提出 P6 → P4 Transition Request；
- 提出 P6 → P5 Transition Request；
- 对 `PROJECT_PLAN.md`、Project Artifact 或其他 Workflow Artifact 提出影响后续 Workflow 推进的变更；
- 提出影响项目当前状态的 State Change Requirement。

---

## 4.7.9 Allowed Next Phase

P6 只允许：

- `P2 Solution Design`；
- `P3 Execution Planning`；
- `P4 Creation`；
- `P5 Validation`。

P6 不允许直接请求：

- P0；
- P1；
- 新的未定义 Core Phase。

---

# 5. Phase Interface

## 5.1 Phase Interface Purpose

Phase Interface 定义：

Runtime 与单个 Phase 进行 Contract-level 交互时必须交换的信息。

Phase Interface 不执行：

- Agent Reasoning；
- Maker Decision；
- Phase Process；
- Artifact Creation；
- Context Mutation；
- Gate Evaluation。

---

# 6. Phase Input Contract

## 6.1 Required Fields

每一个 Phase Input Contract 必须能够表达：

- Workflow Identity；
- Current Phase Reference；
- Phase Definition Reference；
- Context Reference；
- Artifact Reference；
- Workflow Requirement Reference。

---

## 6.2 Workflow Identity

Workflow Identity：

必须等于：

`PROJECT_INCUBATOR_V1_CORE_WORKFLOW`

除非未来存在已经正式定义的 Project Type Workflow Extension。

---

## 6.3 Current Phase Reference

Current Phase Reference 必须能够关联：

- Phase ID；
- Phase Name；
- 当前 Phase Lifecycle State；
- `PROJECT_STATE.md` 中的 Current Phase Fact。

如果 Runtime 当前理解与 `PROJECT_STATE.md` 冲突：

不得由 Workflow Contract 覆盖 `PROJECT_STATE.md`。

---

## 6.4 Phase Definition Reference

Phase Definition Reference：

必须指向当前 Phase 对应的冻结 Workflow Definition。

不得使用其他 Phase Definition 替代当前 Phase。

---

## 6.5 Context Reference

Context Reference：

只表达当前 Phase 所需 Context。

它不授予 Context Read Permission。

Context Read Permission 必须继续遵循：

`PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md`

Workflow Runtime Component 只能读取：

当前 Workflow Requirement 明确依赖的 Context。

---

## 6.6 Artifact Reference

Artifact Reference 用于引用：

当前 Phase 已经定义为 Input 或 Requirement 的 Artifact。

Artifact Reference：

不定义 Artifact Schema。

不改变 Artifact Flow。

---

## 6.7 Workflow Requirement Reference

Workflow Requirement Reference 必须能够引用当前 Phase 的：

- Phase Goal；
- Required Artifact Requirement；
- State Change Requirement；
- Gate Trigger Requirement；
- Allowed Next Phase。

Runtime 不得从 Workflow Requirement Reference 创建新的 Domain Requirement。

---

# 7. Phase Result Contract

## 7.1 Phase Result Purpose

Phase Result 表示：

当前 Phase 已形成哪些 Workflow-level 结果。

Phase Result：

不是 Phase Transition Result。

Phase Result：

也不表示项目状态已经被写回。

---

## 7.2 Required Fields

每一个 Phase Result 必须能够表达：

- Workflow Identity；
- Phase Reference；
- Process Result Status；
- Phase Output Reference；
- Required Artifact Requirement Status；
- State Change Requirement；
- Gate Trigger Requirement；
- Requested Next Phase。

---

## 7.3 Process Result Status

Process Result Status 只允许：

- `NOT_FORMED`；
- `FORMED`。

### NOT_FORMED

表示：

当前 Phase 尚未形成满足 Phase Process Boundary 的领域结果。

### FORMED

表示：

当前 Phase 已经形成领域结果，可以继续检查其他 Transition Requirement。

`FORMED`：

不等于 Phase Transition 已经具备全部条件。

---

## 7.4 Phase Output Reference

Phase Output Reference：

必须引用当前 Phase Domain Definition 已允许产生或更新的 Output。

不得在 Phase Result 中增加：

Workflow Design 未定义的固定 Output Type。

---

## 7.5 Required Artifact Requirement Status

Required Artifact Requirement Status 只允许：

- `UNSATISFIED`；
- `SATISFIED`。

### UNSATISFIED

表示：

当前 Phase Transition 所需 Required Artifact 尚未存在，或尚未完成本 Phase 所要求的更新。

### SATISFIED

表示：

Required Artifact：

已经存在，

或者：

已经完成当前 Phase 要求的更新。

Required Artifact 不要求：

必须由当前 Phase 首次创建。

---

## 7.6 State Change Requirement

Phase Result 中的 State Change Requirement 必须能够表达：

- Current Phase；
- Current Phase State；
- Completed Workflow Items；
- Current Blockers；
- Requested Next Phase。

State Change Requirement：

只是 Workflow 对项目状态变化的要求。

State Change Requirement 不表示：

- `PROJECT_STATE.md` 已修改；
- Runtime 已执行 Mutation；
- Context Mutation 已持久化。

Context Mutation 必须继续遵循：

`PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md`。

---

## 7.7 Gate Trigger Requirement

Phase Result 中的 Gate Trigger Requirement 必须能够表达：

- Trigger Source Phase；
- Trigger Event；
- Related Transition Request；
- Related Artifact Change；
- Related State Change Requirement；
- Gate Requirement Reference。

Gate Trigger Requirement：

只表示 Workflow 已产生 Gate Requirement。

不表示：

- Gate Evaluation 已完成；
- Gate 已允许继续；
- Maker 已授权。

---

## 7.8 Requested Next Phase

Requested Next Phase：

必须属于当前 Phase 的 Allowed Next Phase。

如果 Requested Next Phase 不属于 Allowed Next Phase：

该 Phase Result 不得进入有效 Transition Eligibility。

---

# 8. Required Artifact Contract

## 8.1 Required Artifact Semantics

Required Artifact 表示：

当前 Phase 提出 Transition 前必须已经存在，

或者：

必须已经完成当前 Phase 要求更新的 Artifact。

Output 和 Required Artifact：

不是同一个 Contract 概念。

Output：

表示 Phase 可以产生或更新什么。

Required Artifact：

表示 Transition 必须依赖什么 Artifact Condition。

---

## 8.2 Required Artifact Reference

Required Artifact Reference 必须能够表达：

- Phase Reference；
- Artifact Identity / Artifact Reference；
- Requirement Type；
- Requirement Status。

Requirement Type 只允许表达上游 Workflow 已经定义的：

- Existing Artifact Requirement；
- Updated Artifact Requirement；
- Composite Artifact Requirement。

本 Contract 不定义新的 Artifact Domain Type。

---

## 8.3 Core Phase Boundary Matrix

| Phase | Required Artifact | Phase Artifact Output | Context Mutation |
| --- | --- | --- | --- |
| P0 | PROJECT_PROFILE.md | 无 | PROJECT_PROFILE.md；PROJECT_STATE.md |
| P1 | PROJECT_STATE.md | 无 | PROJECT_STATE.md |
| P2 | Solution Design Artifact | Design Document；Solution Definition；Decision Proposal（如需要） | PROJECT_DECISIONS.md（Maker 确认重要决策时）；PROJECT_STATE.md |
| P3 | Implementation Plan | Implementation Plan | PROJECT_PLAN.md；PROJECT_STATE.md |
| P4 | Project Artifact | Project Artifact | PROJECT_STATE.md |
| P5 | Validation Result | Validation Result | PROJECT_STATE.md |
| P6 | Validation Result + 本轮实际修改的 Workflow Artifact | Solution Design Artifact；Implementation Plan；Project Artifact（均仅在实际调整时） | PROJECT_PLAN.md；PROJECT_STATE.md |

Context Mutation Target 不属于 Phase Artifact Output。Core Context 被更新时，不自动构成 Phase Artifact 或 Required Artifact。

---

## 8.4 P2 Composite Requirement

P2 Solution Design Artifact：

至少必须包含：

- Design Document；
- Solution Definition。

Decision Proposal：

不属于 P2 通用 Required Artifact Requirement。

---

## 8.5 P6 Composite Requirement

P6 Required Artifact Requirement：

必须同时包含：

1. Validation Result；
2. 本轮 Iteration 实际修改的 Workflow Artifact。

Runtime 不得把 Validation Result 单独视为所有 P6 Transition 的完整 Required Artifact Requirement。

---

# 9. Gate Trigger Requirement Contract

## 9.1 Purpose

Gate Trigger Requirement Contract 表达：

Workflow 中发生了需要进入 Gate 保护范围的流程事件。

Workflow Contract 不执行 Gate Evaluation。

---

## 9.2 Gate Trigger Requirement Fields

Gate Trigger Requirement 必须能够表达：

- Requirement ID；
- Source Phase；
- Trigger Event Type；
- Trigger Object Reference；
- Related Transition Request；
- Gate Requirement Reference。

---

## 9.3 Trigger Event Type

Workflow Contract 使用以下 Workflow-side Trigger Event Type：

- `PHASE_TRANSITION_REQUEST`；
- `REQUIRED_ARTIFACT_CHANGE`；
- `WORKFLOW_ARTIFACT_CHANGE`；
- `STATE_CHANGE_REQUIREMENT`。

这些 Event Type：

只描述 Workflow 侧事件。

不重新定义 Gate Type。

---

## 9.4 Gate Requirement Completion Reference

Workflow Contract 只需要知道：

当前 Gate Requirement 是否仍然阻止 Transition。

Workflow-side Gate Requirement Status 只允许：

- `UNRESOLVED`；
- `RESOLVED_FOR_TRANSITION`。

### UNRESOLVED

表示：

当前没有足够的 Gate Contract Result 证明该 Gate Requirement 已允许对应 Transition 继续。

### RESOLVED_FOR_TRANSITION

表示：

对应 Gate Contract Result 已允许当前 Transition 继续。

该状态只是 Workflow 对 Gate Contract Result 的消费状态。

它不是：

Gate Evaluation Result。

Gate Evaluation Result 的具体模型由：

`PROJECT_INCUBATOR_V1_GATE_CONTRACT.md`

定义。

---

# 10. Transition Contract

## 10.1 Transition Request Definition

Phase Transition Request 表示：

当前 Phase 请求进入一个 Allowed Next Phase。

Transition Request：

只表达请求。

不执行：

Phase Transition。

---

## 10.2 Transition Request Required Fields

每一个 Phase Transition Request 必须能够表达：

- Transition Request ID；
- Workflow Identity；
- Current Phase；
- Requested Next Phase；
- Process Result Status；
- Required Artifact Requirement；
- State Change Requirement；
- Gate Requirement；
- Transition Eligibility Information。

---

## 10.3 Current Phase

Current Phase：

必须与项目当前状态 Source of Truth 中记录的 Current Phase 一致。

如果不一致：

Transition Request 不具备 Transition Eligibility。

Workflow Contract 不修改该冲突。

---

## 10.4 Requested Next Phase

Requested Next Phase：

必须存在于当前 Phase 的 Allowed Next Phase Set。

否则：

Transition Request 状态必须为：

`TRANSITION_NOT_ALLOWED`。

---

## 10.5 Required Artifact Requirement

Transition Request 必须引用：

当前 Phase 的 Required Artifact Requirement。

不得使用：

其他 Phase 的 Required Artifact

替代当前 Phase Requirement。

---

## 10.6 State Change Requirement

Transition Request 必须包含：

当前 Phase 对本次 Transition 所形成的 State Change Requirement。

State Change Requirement 缺失时：

Transition 不具备 Eligibility。

---

## 10.7 Gate Requirement

Transition Request 必须关联：

当前 Transition 所需要处理的 Gate Requirement。

如果对应 Gate Requirement 仍为：

`UNRESOLVED`

则：

Transition 不具备 Eligibility。

---

# 11. Transition Eligibility Contract

## 11.1 Eligibility Model

Transition Eligibility Information 用于让 Runtime 判断：

当前 Transition Request 是否已经满足 Workflow Contract 所要求的全部交互条件。

Transition Eligibility：

不是 Runtime Execution Flow。

---

## 11.2 Eligibility Fields

Transition Eligibility Information 必须能够表达：

- Current Phase Match；
- Process Completion；
- Requested Next Phase Allowed；
- Required Artifact Requirement；
- State Change Requirement；
- Gate Requirement。

---

## 11.3 Current Phase Match

允许值：

- `MATCHED`；
- `MISMATCHED`。

### MATCHED

Current Phase Reference 与当前项目状态 Source of Truth 一致。

### MISMATCHED

Current Phase Reference 与当前项目状态 Source of Truth 不一致。

---

## 11.4 Process Completion

允许值：

- `PROCESS_INCOMPLETE`；
- `PROCESS_COMPLETE`。

`PROCESS_COMPLETE`：

对应 Phase Result：

`FORMED`。

---

## 11.5 Requested Next Phase Allowed

允许值：

- `NOT_ALLOWED`；
- `ALLOWED`。

---

## 11.6 Required Artifact Eligibility

允许值：

- `REQUIRED_ARTIFACT_UNSATISFIED`；
- `REQUIRED_ARTIFACT_SATISFIED`。

---

## 11.7 State Change Requirement Eligibility

允许值：

- `STATE_CHANGE_REQUIREMENT_MISSING`；
- `STATE_CHANGE_REQUIREMENT_FORMED`。

`STATE_CHANGE_REQUIREMENT_FORMED`：

不表示 Context Mutation 已执行。

---

## 11.8 Gate Requirement Eligibility

允许值：

- `GATE_REQUIREMENT_UNRESOLVED`；
- `GATE_REQUIREMENT_RESOLVED`。

`GATE_REQUIREMENT_RESOLVED`：

只表示对应 Gate Contract 已允许当前 Transition 继续。

不重新定义 Gate Evaluation Result。

---

# 12. Transition Eligibility Result

## 12.1 Result Status

Workflow Transition Eligibility Result 只允许：

- `NOT_READY`；
- `READY_FOR_TRANSITION`；
- `TRANSITION_NOT_ALLOWED`。

---

## 12.2 NOT_READY

以下任一情况成立时：

Result 必须为：

`NOT_READY`

包括：

- Current Phase Mismatched；
- Phase Process 尚未完成；
- Required Artifact Requirement 未满足；
- State Change Requirement 尚未形成；
- Gate Requirement 尚未解决。

`NOT_READY`：

不表示 Runtime Failure。

只表示：

当前 Workflow Transition Requirement 尚未满足。

---

## 12.3 READY_FOR_TRANSITION

只有以下条件全部满足时：

Result 才能为：

`READY_FOR_TRANSITION`：

1. Current Phase Match = `MATCHED`；
2. Process Completion = `PROCESS_COMPLETE`；
3. Requested Next Phase Allowed = `ALLOWED`；
4. Required Artifact Eligibility = `REQUIRED_ARTIFACT_SATISFIED`；
5. State Change Requirement Eligibility = `STATE_CHANGE_REQUIREMENT_FORMED`；
6. Gate Requirement Eligibility = `GATE_REQUIREMENT_RESOLVED`。

`READY_FOR_TRANSITION`：

只表示 Workflow Contract 条件已经具备。

不表示：

- Runtime 已执行 Transition；
- `PROJECT_STATE.md` 已写回；
- Runtime State 已改变。

---

## 12.4 TRANSITION_NOT_ALLOWED

如果：

Requested Next Phase 不属于当前 Phase 的 Allowed Next Phase：

Result 必须为：

`TRANSITION_NOT_ALLOWED`。

该状态不能通过：

- Required Artifact 已满足；
- Maker Authorization；
- Gate Resolution；
- Runtime Decision

自动改变为：

`READY_FOR_TRANSITION`。

如果需要新的 Transition Path：

必须修改上游 Workflow Domain Model。

不得在 Contract 或 Runtime 中自行增加。

---

# 13. Core Transition Contract

## 13.1 P0 → P1

Current Phase：

`P0 Intent Discovery`

Requested Next Phase：

`P1 Project Definition`

Required Artifact：

`PROJECT_PROFILE.md`

Transition 必须满足：

- P0 Process 已形成领域结果；
- `PROJECT_PROFILE.md` Required Artifact Requirement 已满足；
- P0 State Change Requirement 已形成；
- P0 Gate Requirement 已解决。

---

## 13.2 P1 → P2

Current Phase：

`P1 Project Definition`

Requested Next Phase：

`P2 Solution Design`

Required Artifact：

`PROJECT_STATE.md`

Transition 必须满足：

- P1 Process 已形成领域结果；
- `PROJECT_STATE.md` Required Artifact Requirement 已满足；
- P1 State Change Requirement 已形成；
- P1 Gate Requirement 已解决。

---

## 13.3 P2 → P3

Current Phase：

`P2 Solution Design`

Requested Next Phase：

`P3 Execution Planning`

Required Artifact：

`Solution Design Artifact`

Solution Design Artifact 至少包含：

- Design Document；
- Solution Definition。

Transition 必须满足：

- P2 Process 已形成领域结果；
- Solution Design Artifact Requirement 已满足；
- P2 State Change Requirement 已形成；
- P2 Gate Requirement 已解决。

Decision Proposal：

不是该 Transition 的通用 Required Artifact。

---

## 13.4 P3 → P4

Current Phase：

`P3 Execution Planning`

Requested Next Phase：

`P4 Creation`

Required Artifact：

`Implementation Plan`

Transition 必须满足：

- P3 Process 已形成领域结果；
- `Implementation Plan` Required Artifact Requirement 已满足；
- `PROJECT_PLAN.md` Context Mutation Requirement 已形成；
- P3 State Change Requirement 已形成；
- P3 Gate Requirement 已解决。

P3 → P4 Transition 执行完成后：

- `PROJECT_PLAN.md` 更新属于 Context Mutation 结果；
- `PROJECT_STATE.md` 状态变更属于 Context Mutation 结果；
- 二者不得被解释为 P3 Required Artifact。

---

## 13.5 P4 → P5

Current Phase：

`P4 Creation`

Requested Next Phase：

`P5 Validation`

Required Artifact：

`Project Artifact`

Transition 必须满足：

- P4 Process 已形成领域结果；
- Project Artifact Requirement 已满足；
- P4 State Change Requirement 已形成；
- P4 Gate Requirement 已解决。

---

## 13.6 P5 → P6

Current Phase：

`P5 Validation`

Requested Next Phase：

`P6 Iteration`

Required Artifact：

`Validation Result`

Transition 必须满足：

- P5 Process 已形成领域结果；
- Validation Result Requirement 已满足；
- P5 State Change Requirement 已形成；
- P5 Gate Requirement 已解决。

---

# 14. Iteration Transition Contract

## 14.1 Iteration Transition Boundary

P6 Iteration 只可以提出以下四种 Transition Request：

- P6 → P2；
- P6 → P3；
- P6 → P4；
- P6 → P5。

Workflow Contract：

不选择目标 Phase。

目标 Phase 必须来自：

当前 Iteration 已形成的 Requested Next Phase。

---

## 14.2 Common P6 Transition Requirement

所有 P6 Transition Request 必须满足：

- P6 Process 已形成领域结果；
- Validation Result 存在；
- 本轮实际修改的 Workflow Artifact 已满足 Required Artifact Requirement；
- 当前 Transition 所需 State Change Requirement 已形成；
- 当前 Transition 所需 Gate Requirement 已解决；
- Requested Next Phase 属于 P2 / P3 / P4 / P5。

---

## 14.3 P6 → P2 Solution Design

Requested Next Phase：

`P2 Solution Design`

Validation Result 必须能够说明：

需要重新进入 Solution Design 的问题。

该条件不允许 Runtime：

自行生成新的问题理由。

---

## 14.4 P6 → P3 Execution Planning

Requested Next Phase：

`P3 Execution Planning`

`Implementation Plan`：

属于本轮需要继续调整的目标 Phase Artifact。

`PROJECT_PLAN.md`：

属于生命周期规划 Context Mutation 目标，不作为 Implementation Task Breakdown Artifact。

Transition Request 必须明确引用：

- Validation Result；
- 与本轮 Iteration 实际修改范围对应的 Workflow Artifact；
- `Implementation Plan` 作为返回 Execution Planning 的目标 Artifact Reference；
- 如果生命周期规划发生变化，引用 `PROJECT_PLAN.md` 作为 Context Mutation Target。

Workflow Contract 不判断：

Execution Planning 中应该如何进一步修改 Plan。

---

## 14.5 P6 → P4 Creation

Requested Next Phase：

`P4 Creation`

Project Artifact：

属于本轮需要继续调整的目标 Workflow Artifact。

Transition Request 必须明确引用：

- Validation Result；
- 本轮实际修改的 Workflow Artifact；
- Project Artifact 作为返回 Creation 的目标 Artifact Reference。

---

## 14.6 P6 → P5 Validation

Requested Next Phase：

`P5 Validation`

必须存在：

可再次进入 Validation 的 Project Artifact。

Transition Request 必须明确引用：

- Validation Result；
- 本轮实际修改的 Workflow Artifact；
- 可再次进入 Validation 的 Project Artifact。

---

## 14.7 Iteration Invalid Transition

以下 P6 Transition Request：

必须返回：

`TRANSITION_NOT_ALLOWED`：

- P6 → P0；
- P6 → P1；
- P6 → 未定义 Phase；
- P6 → P6。

---

# 15. Workflow and Context Contract Boundary

## 15.1 Context Reference

Workflow 可以将 Context 作为：

- Phase Input；
- Context Mutation Target；
- Workflow 推进所依赖的项目事实；
- State Change Requirement 涉及对象。

Workflow Contract：

只定义这些 Context Reference。

Core Context 文件被 Phase 更新时，该更新属于 Context Mutation Requirement，不自动构成 Phase Artifact 或 Required Artifact。

除非 Workflow Design 对某个 Phase 明确声明，否则不得使用：

`Required Artifact = Core Context File`

作为表达 Phase Artifact Requirement 的唯一方式。

---

## 15.2 Context Read Permission

Workflow Contract 不授予 Context Read Permission。

Workflow Runtime Component 的 Context Read 必须遵守：

`PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md`

Workflow Runtime Component 只能读取：

当前 Workflow Requirement 明确依赖的 Context。

---

## 15.3 Context Mutation

Workflow 可以：

形成 Context Mutation Requirement。

Workflow 不可以：

执行 Context Persisted Mutation。

Workflow State Change Requirement：

不等于 Context 已经修改。

Workflow Phase Output：

如果属于 Context：

也不等于该 Context 已完成持久化。

---

## 15.4 Mutation Execution

Context Mutation 的：

- Request；
- Authorization；
- Execution；
- Access Boundary

继续由：

`PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md`

控制。

Runtime 是 Context Persisted Mutation 的执行者。

Workflow Contract：

不得重新定义 Mutation Authority。

---

# 16. Workflow and Gate Contract Boundary

## 16.1 Workflow Responsibility

Workflow 负责表达：

- 哪个流程事件需要 Gate；
- Gate Trigger Requirement；
- Gate Requirement 与当前 Transition 的关系。

---

## 16.2 Gate Responsibility

Workflow Contract 不定义：

- Gate Type；
- Gate Lifecycle；
- Gate Evaluation Requirement；
- Gate Input；
- Gate Output；
- Evaluation Result；
- Maker Authorization Result。

---

## 16.3 Gate Trigger

Workflow 产生 Gate Trigger Requirement：

不表示 Gate 已经完成 Evaluation。

---

## 16.4 Gate Resolution

Workflow Contract 只有在对应 Gate Contract Result 允许项目继续时：

才能将 Workflow-side Gate Requirement 标记为：

`RESOLVED_FOR_TRANSITION`。

Workflow Contract：

不得自行产生 Gate PASS / BLOCK 等 Evaluation Result。

---

# 17. Workflow and Advisory Boundary

Advisory 可以使用：

- Current Phase；
- Project Context；
- Validation Result；
- Workflow Requirement

形成建议。

Advisory Response：

不能被 Workflow Contract 直接视为：

- Phase Transition Request；
- Gate Resolution；
- State Change；
- Maker Authorization。

如果 Advisory 建议进入某个下一 Phase：

仍必须形成符合本 Contract 的：

Phase Transition Request。

---

# 18. Workflow and Artifact Boundary

## 18.1 Artifact Reference Only

Workflow Contract 可以引用已经由 Workflow Design 定义的：

- Phase Input Artifact；
- Phase Output Artifact；
- Required Artifact；
- Iteration Target Artifact。

Workflow Contract 不重新定义 Artifact Flow。

---

## 18.2 Artifact Structure

除已经由 Workflow Design 明确定义的：

Solution Design Artifact 至少包含：

- Design Document；
- Solution Definition

P3 Implementation Plan：

- 属于 Phase Artifact；
- 用于将 Solution Design 转换为可执行实施方案；
- 不属于 Core Context；
- 不替代 `PROJECT_PLAN.md`；
- 具体结构由 Project Type 决定。

之外，

本 Contract 不新增：

- Artifact Schema；
- Artifact Field；
- Artifact Data Model。

---

## 18.3 Artifact Runtime Processing

Artifact：

如何生成、读取、写入、验证或持久化：

不属于 Workflow Contract。

具体执行机制由：

`PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`

定义。

---

# 19. Workflow Extension Contract Boundary

## 19.1 Project Type Extension

Workflow Domain Model 允许 Project Type 扩展：

- Phase Detail；
- Phase Process Detail；
- Artifact Requirement；
- Validation Requirement；
- Optional Workflow Branch；
- Project Type Specific Phase Guidance。

---

## 19.2 Extension Invariants

任何 Project Type Extension 必须保持：

- Core Phase Identity 不变；
- Core Phase 基础目标不变；
- Core Workflow Boundary 不变；
- Core Context Boundary 不变；
- Gate Boundary 不变；
- Runtime Boundary 不变。

---

## 19.3 Contract Restriction

如果当前没有已经冻结的 Project Type Extension Definition：

Workflow Contract 不得自行创建：

- 新 Phase；
- 新 Artifact Requirement；
- 新 Optional Branch；
- 新 Transition Path；
- 新 Validation Requirement。

Runtime 也不得自行推导上述 Extension。

---

# 20. Contract Result Semantics

## 20.1 Purpose

Runtime 消费 Workflow Contract 时：

必须能够明确区分不同的 Workflow Condition。

不得把所有未推进情况统一表示为 Runtime Failure。

---

## 20.2 Phase Process Incomplete

当：

Process Result Status = `NOT_FORMED`

时：

当前状态语义为：

Phase 尚未形成必要领域结果。

Transition Result：

`NOT_READY`

---

## 20.3 Required Artifact Unsatisfied

当：

Required Artifact Requirement Status = `UNSATISFIED`

时：

当前状态语义为：

Phase Required Artifact Requirement 尚未满足。

Transition Result：

`NOT_READY`

---

## 20.4 State Change Requirement Missing

当：

State Change Requirement 尚未形成

时：

当前状态语义为：

Workflow 尚未形成当前 Transition 所要求的状态变化需求。

Transition Result：

`NOT_READY`

---

## 20.5 Gate Requirement Unresolved

当：

Gate Requirement = `UNRESOLVED`

时：

当前状态语义为：

当前 Workflow Transition 仍受到 Gate Requirement 阻止。

Transition Result：

`NOT_READY`

---

## 20.6 Transition Path Invalid

当：

Requested Next Phase 不属于 Allowed Next Phase

时：

Transition Result：

`TRANSITION_NOT_ALLOWED`

该结果不是：

普通 `NOT_READY`。

它表示：

Transition Path 本身不属于当前冻结 Workflow。

---

## 20.7 Transition Ready

只有：

- Current Phase 正确；
- Phase Process 已完成；
- Required Artifact Requirement 已满足；
- State Change Requirement 已形成；
- Gate Requirement 已解决；
- Requested Next Phase 属于 Allowed Next Phase

全部成立时：

Transition Result：

`READY_FOR_TRANSITION`

---

# 21. Runtime Consumption Contract

## 21.1 Runtime May Consume

Runtime 可以从 Workflow Contract 获取：

- Current Phase Definition；
- Phase Input Requirement；
- Phase Output Definition；
- Required Artifact Requirement；
- State Change Requirement；
- Gate Trigger Requirement；
- Allowed Next Phase；
- Transition Eligibility Result。

---

## 21.2 Runtime Must Not Infer

Runtime 不得自行推导：

- 未定义 Phase；
- 未定义 Transition；
- 未定义 Required Artifact；
- 未定义 Gate Requirement；
- 未定义 Workflow Extension；
- 未定义 Artifact Flow。

---

## 21.3 Runtime Execution Boundary

Workflow Contract 不定义 Runtime：

- 如何加载 Workflow Definition；
- 如何调用 Agent；
- 如何执行 Phase；
- 如何调用 Gate；
- 如何进行 Context Mutation；
- 如何持久化 State；
- 如何执行 Artifact Writeback；
- 如何恢复 Runtime。

上述内容属于：

`PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`。

---

# 22. Contract Validation Rules

任何 Workflow Contract Consumer 必须满足以下规则。

## Rule 1

Workflow Identity 必须明确。

---

## Rule 2

Current Phase 必须属于 Core Phase Set 或已经正式定义的合法 Project Type Extension。

---

## Rule 3

Core Transition 必须符合 Allowed Transition Matrix。

---

## Rule 4

Phase Result 不得将：

Output

自动视为：

Required Artifact Requirement 已满足。

---

## Rule 5

Required Artifact Requirement 必须单独具有明确 Status。

---

## Rule 6

State Change Requirement：

不得被视为 Context Mutation 已执行。

---

## Rule 7

Gate Trigger Requirement：

不得被视为 Gate Evaluation 已完成。

---

## Rule 8

Gate Requirement 未解决时：

Transition 不得标记为 READY。

---

## Rule 9

P2 Decision Proposal：

不得作为所有 P2 Transition 的通用 Required Artifact。

---

## Rule 10

P6 Transition：

只能请求：

- P2；
- P3；
- P4；
- P5。

---

## Rule 11

P6 Required Artifact：

必须包含：

- Validation Result；
- 本轮实际修改的 Workflow Artifact。

---

## Rule 12

Workflow Contract：

不得授予任何新的 Context Mutation Authority。

---

## Rule 13

Workflow Contract：

不得定义 Gate Evaluation Result。

---

## Rule 14

Workflow Contract：

不得定义 Runtime Execution Flow。

---

# 23. Source of Truth Boundary

Project Incubator V1 Workflow 相关 Source of Truth 固定如下：

Workflow 是什么、有哪些 Phase、Phase Goal、Phase Input / Output、Required Artifact、Artifact Flow、Allowed Transition：

`PROJECT_INCUBATOR_V1_WORKFLOW_DESIGN.md`

Workflow Runtime Interface、Workflow Schema、Phase Interface、Transition Contract：

`PROJECT_INCUBATOR_V1_WORKFLOW_CONTRACT.md`

Context Access Permission、Mutation Authority 与 Access Boundary：

`PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md`

Gate Domain Model：

`PROJECT_INCUBATOR_V1_GATE_DESIGN.md`

Gate Input、Gate Output 与 Evaluation Result：

`PROJECT_INCUBATOR_V1_GATE_CONTRACT.md`

Workflow 的具体执行机制：

`PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`

规则：

```text
Workflow Design
      ↓
Workflow Contract
      ↓
Runtime Specification
```

Contract 不重新定义 Design。

Runtime 不重新定义 Contract。

---

# 24. V1 Contract Summary

Project Incubator V1 Workflow Contract 定义：

- Workflow Contract Model；
- Workflow Schema；
- Core Phase Contract；
- Phase Input Contract；
- Phase Result Contract；
- Required Artifact Contract；
- Gate Trigger Requirement Contract；
- Transition Contract；
- Transition Eligibility Contract；
- Iteration Transition Contract；
- Workflow / Context Boundary；
- Workflow / Gate Boundary；
- Runtime Consumption Boundary。

核心 Contract 原则：

1. Core Workflow 固定包含 P0–P6 七个 Phase。

2. Core Workflow 标准顺序固定为：

```text
P0 → P1 → P2 → P3 → P4 → P5 → P6
```

3. P6 只允许返回：

```text
P2
P3
P4
P5
```

4. Runtime 不得新增 Transition Path。

5. Phase Output 与 Required Artifact 是两个不同 Contract 概念。

6. Required Artifact 必须在 Transition 前满足。

7. State Change Requirement 只是状态变化需求，不表示 `PROJECT_STATE.md` 已经修改。

8. Workflow 只能声明 Gate Requirement，不执行 Gate Evaluation。

9. Gate Requirement 未解决时，Transition 不具备 Eligibility。

10. Transition 只有在以下条件全部满足后才能标记：

`READY_FOR_TRANSITION`

- Current Phase Match；
- Process Complete；
- Allowed Next Phase；
- Required Artifact Satisfied；
- State Change Requirement Formed；
- Gate Requirement Resolved。

11. `READY_FOR_TRANSITION` 不等于 Runtime 已经执行 Transition。

12. Context 访问与 Mutation 必须继续遵循 Context Access Contract。

13. Workflow Contract 不重新定义 Artifact Flow。

14. Workflow Contract 不定义 Runtime Workflow Loader 或 Runtime Execution Flow。

15. Runtime Specification 必须直接消费本 Contract，不得自行推导新的 Workflow Rule。
