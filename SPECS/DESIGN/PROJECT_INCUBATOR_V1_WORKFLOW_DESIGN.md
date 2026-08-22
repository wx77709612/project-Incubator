# Project Incubator V1 Workflow Design


## 1. Workflow Overview


Project Incubator V1 Workflow 定义项目从初始 Idea 到持续迭代的标准推进流程。


Workflow 负责定义：

- Phase 顺序；
- Phase 目标；
- Phase 输入；
- Phase 输出；
- Artifact 流转；
- State 变化需求；
- Gate 触发条件。


Workflow 不负责：

- Runtime Component 实现；
- Script 实现；
- Agent 内部推理过程；
- Maker 决策。


Runtime 执行规则由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。



## 2. Workflow Model

Project Incubator V1 使用循环式 Phase Workflow。

Workflow 由以下 Core Phase 组成：

1. Intent Discovery；
2. Project Definition；
3. Solution Design；
4. Execution Planning；
5. Creation；
6. Validation；
7. Iteration。

Core Phase 的标准顺序为：

Intent Discovery

↓

Project Definition

↓

Solution Design

↓

Execution Planning

↓

Creation

↓

Validation

↓

Iteration

Workflow 不要求项目只按照单向线性流程完成。

Iteration 可以根据 Validation Result 返回：

- Solution Design；
- Execution Planning；
- Creation；
- Validation。

Workflow 负责定义：

- Core Phase Model；
- Phase 顺序关系；
- Phase 输入；
- Phase Process；
- Phase 输出；
- Required Artifact；
- Context Mutation；
- State Change Requirement；
- Gate Trigger Requirement；
- Artifact Flow；
- Phase Transition Relationship。

Workflow 不直接执行：

- Phase Transition；
- State Update；
- Gate Evaluation；
- Artifact Writeback。

上述执行机制由 Runtime Layer定义。

---

## 3. Phase Model

每个 Core Phase 必须定义：

- Phase ID；
- Phase Name；
- Phase Goal；
- Input；
- Process；
- Output；
- Required Artifact；
- State Change Requirement；
- Gate Trigger Requirement；
- Allowed Next Phase。

Required Artifact 表示当前 Phase 请求 Phase Transition 前必须已经存在，或已经完成本 Phase 所要求更新的 Artifact。

Required Artifact 不要求必须由当前 Phase 首次创建。

对于使用既有 Artifact 的 Phase，只要该 Artifact 已满足当前 Phase 的 Workflow Requirement，即视为 Required Artifact Requirement 已满足。

Phase Artifact Output 与 Required Artifact 不完全等价：

- Phase Artifact Output 表示 Phase 可以产生或更新的 Artifact；
- Required Artifact 表示 Phase Transition 必须依赖的 Artifact 条件。

Phase Artifact 与 Context Mutation 必须分开表达：

- Phase Artifact 表示当前 Phase 产生或更新的项目成果；
- Context Mutation 表示当前 Phase 对 Core Context 提出的持久化变更需求；
- Core Context 文件被更新时，不自动等同于该 Phase 的 Required Artifact。

P0-P6 统一使用以下 Phase Boundary Matrix 表达：

| Phase | Required Artifact | Phase Artifact Output | Context Mutation |
| --- | --- | --- | --- |
| P0 | PROJECT_PROFILE.md | 无 | PROJECT_PROFILE.md；PROJECT_STATE.md |
| P1 | PROJECT_STATE.md | 无 | PROJECT_STATE.md |
| P2 | Solution Design Artifact | Design Document；Solution Definition；Decision Proposal（如需要） | PROJECT_DECISIONS.md（Maker 确认重要决策时）；PROJECT_STATE.md |
| P3 | Implementation Plan | Implementation Plan | PROJECT_PLAN.md；PROJECT_STATE.md |
| P4 | Project Artifact | Project Artifact | PROJECT_STATE.md |
| P5 | Validation Result | Validation Result | PROJECT_STATE.md |
| P6 | Validation Result；本轮实际修改的 Workflow Artifact | Solution Design Artifact；Implementation Plan；Project Artifact（均仅在实际调整时） | PROJECT_PLAN.md；PROJECT_STATE.md |

表中的 Context Mutation Target 不是 Phase Artifact Output，也不因列入 Required Artifact 而自动成为 Phase Artifact。

Core Phase 定义如下：

| Phase ID | Phase Name         | 基础目标　　　　　　　　　　　　　　　　　　　　　|
| ----------| --------------------| ---------------------------------------------------|
| P0       | Intent Discovery   | 明确 Maker 的项目意图、目标、对象、问题和成功标准 |
| P1       | Project Definition | 建立项目身份、范围、约束和当前状态基础　　　　　　|
| P2       | Solution Design    | 形成项目解决方案、系统边界和关键设计决策　　　　　|
| P3       | Execution Planning | 建立项目执行路线、任务顺序、依赖和预期成果　　　　|
| P4       | Creation           | 执行项目创建并产生项目 Artifact　　　　　　　　　 |
| P5       | Validation         | 验证项目 Artifact 是否满足 Intent、计划和项目约束 |
| P6       | Iteration          | 根据 Validation Result 调整方案、计划或 Artifact　|

Phase 生命周期包括：

- Not Started；
- Active；
- Awaiting Gate；
- Completed；
- Reopened。

生命周期语义：

Not Started：

- Phase 尚未进入。

Active：

- Phase 已进入，相关 Process 正在进行。

Awaiting Gate：

- Phase 已完成必要 Process，正在等待 Gate 结果。

Completed：

- Phase 已满足退出要求，可以进入允许的下一 Phase。

Reopened：

- Phase 因 Validation Result 或 Maker 决策重新进入。

Workflow 只声明：

- 哪个流程节点需要 Gate；
- Gate 被触发的原因；
- Gate 通过后允许进入的下一 Phase。

具体 Gate Model 与 Gate Definition 由：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_GATE_DESIGN.md

定义。

Gate Invocation Contract 由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_GATE_CONTRACT.md

定义。

Gate 的具体执行机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

---

## 4. Intent Discovery


### 4.1 Phase Goal


明确 Maker 创建项目的目标。


需要确认：

- 为什么创建；
- 解决什么问题；
- 服务什么对象；
- 成功标准是什么。



### 4.2 Input


输入：

- Maker Idea；
- 初始需求；
- 背景信息。



### 4.3 Process


Agent：

- 理解用户目标；
- 发现关键问题；
- 澄清项目边界。


Maker：

- 确认项目方向；
- 确认成功标准。



### 4.4 Phase Artifact Output 与 Context Mutation

Phase Artifact Output：

- 无。

Context Mutation：

- 建立或更新 PROJECT_PROFILE.md；
- 建立或更新 PROJECT_STATE.md。

Required Artifact：

- PROJECT_PROFILE.md。



### 4.5 State Change Requirement

当前 Phase 完成相关 Process 后，应产生 State Change Requirement。

State Change Requirement 描述：

- 当前 Phase；
- Phase 当前状态；
- 已完成的 Workflow 事项；
- 当前阻塞事项；
- 请求进入的下一 Phase。

Workflow 只定义状态变化需求及其与 Phase Transition 的关系。

具体 Context 修改权限由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md

定义。

具体状态更新与写回机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。



### 4.6 Gate Trigger Requirement

以下流程事件需要触发 Gate：

- Intent Discovery 提出进入 Project Definition 的 Phase Transition Request；
- PROJECT_PROFILE.md 作为本 Phase Required Artifact，其状态发生影响后续流程推进的变化；
- Intent Discovery 提出影响项目当前状态的 State Change Requirement。

Gate 通过后：

- Intent Discovery 可以进入 Project Definition。

具体 Gate Model 与 Gate Definition 由：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_GATE_DESIGN.md

定义。

## 5. Project Definition


### 5.1 Phase Goal


建立项目执行上下文。



### 5.2 Input


输入：

- PROJECT_PROFILE.md



### 5.3 Process


建立：

- 项目状态；
- 项目约束；
- 当前执行范围。



### 5.4 Phase Artifact Output 与 Context Mutation

Phase Artifact Output：

- 无。

Context Mutation：

- 建立或更新 PROJECT_STATE.md。

Required Artifact：

- PROJECT_STATE.md。



### 5.5 State Change Requirement

当前 Phase 完成相关 Process 后，应产生 State Change Requirement。

State Change Requirement 描述：

- 当前 Phase；
- Phase 当前状态；
- 已完成的 Workflow 事项；
- 当前阻塞事项；
- 请求进入的下一 Phase。

Workflow 只定义状态变化需求及其与 Phase Transition 的关系。

具体 Context 修改权限由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md

定义。

具体状态更新与写回机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

### 5.6 Gate Trigger Requirement

以下流程事件需要触发 Gate：

- Project Definition 提出进入 Solution Design 的 Phase Transition Request；
- PROJECT_STATE.md 作为本 Phase Required Artifact，其状态发生影响后续流程推进的变化；
- Project Definition 提出影响项目当前状态的 State Change Requirement。

Gate 通过后：

- Project Definition 可以进入 Solution Design。

具体 Gate Model 与 Gate Definition 由：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_GATE_DESIGN.md

定义。

## 6. Solution Design


### 6.1 Phase Goal


形成项目解决方案设计。


### 6.2 Input


输入：

- PROJECT_PROFILE.md；
- PROJECT_STATE.md；
- Solution Design Artifact。


### 6.3 Process


定义：

- 解决方案；
- 系统边界；
- 技术方向；
- Design Artifact；
- Decision Proposal。


### 6.4 Phase Artifact Output 与 Context Mutation


生成：

- Design Document；
- Solution Definition；
- Decision Proposal。


经过 Maker 确认的重要决策：

记录至：

PROJECT_DECISIONS.md。

Context Mutation：

- Maker 确认重要决策时，更新 PROJECT_DECISIONS.md；
- 更新 PROJECT_STATE.md 中的当前 Phase 状态。

Required Artifact：

- Solution Design Artifact。

Solution Design Artifact 至少由以下内容构成：

- Design Document；
- Solution Definition。

Decision Proposal 属于 Solution Design Phase 的 Output，但只有在存在需要 Maker 确认的重要决策时才产生，不作为所有 Solution Design Phase Transition 的通用 Required Artifact。

经过 Maker 确认的重要决策继续记录至：

PROJECT_DECISIONS.md。


### 6.5 State Change Requirement

当前 Phase 完成相关 Process 后，应产生 State Change Requirement。

State Change Requirement 描述：

- 当前 Phase；
- Phase 当前状态；
- 已完成的 Workflow 事项；
- 当前阻塞事项；
- 请求进入的下一 Phase。

Workflow 只定义状态变化需求及其与 Phase Transition 的关系。

具体 Context 修改权限由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md

定义。

具体状态更新与写回机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

### 6.6 Gate Trigger Requirement

以下流程事件需要触发 Gate：

- Solution Design 提出进入 Execution Planning 的 Phase Transition Request；
- Solution Design Artifact 发生影响后续流程推进的变化；
- Solution Design 提出影响项目当前状态的 State Change Requirement。

Gate 通过后：

- Solution Design 可以进入 Execution Planning。

具体 Gate Model 与 Gate Definition 由：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_GATE_DESIGN.md

定义。


## 7. Execution Planning

### 7.1 Phase Goal


建立项目执行路线。



### 7.2 Input


输入：

- PROJECT_PROFILE.md；
- PROJECT_STATE.md。



### 7.3 Process


制定：

- Implementation Plan；
- Project Type 对应的实施任务拆解；
- 执行顺序；
- 依赖关系；
- Artifact 目标；
- 验证方式。



### 7.4 Phase Artifact Output 与 Context Mutation


Phase Artifact Output：

Implementation Plan。

Implementation Plan 是 Phase Artifact。

Implementation Plan 用于将 Solution Design 转换为可执行实施方案。

Implementation Plan 不属于 Core Context，也不替代 PROJECT_PLAN.md。

Implementation Plan 的具体结构由 Project Type 决定。

Software、Skill、Video 等不同 Project Type 可以拥有不同 Implementation Plan 内容结构。

Context Mutation：

- 更新 PROJECT_PLAN.md 中的项目生命周期规划；
- 更新 PROJECT_STATE.md 中的当前 Phase 状态。

PROJECT_PLAN.md 记录项目生命周期规划，不记录 Implementation Task Breakdown Artifact。

当前执行状态由 PROJECT_STATE.md 管理。

Required Artifact：

- Implementation Plan。

### 7.5 State Change Requirement

当前 Phase 完成相关 Process 后，应产生 State Change Requirement。

State Change Requirement 描述：

- 当前 Phase；
- Phase 当前状态；
- 已完成的 Workflow 事项；
- 当前阻塞事项；
- 请求进入的下一 Phase。

Workflow 只定义状态变化需求及其与 Phase Transition 的关系。

具体 Context 修改权限由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md

定义。

具体状态更新与写回机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

### 7.6 Gate Trigger Requirement

以下流程事件需要触发 Gate：

- Execution Planning 提出进入 Creation 的 Phase Transition Request；
- Implementation Plan 作为本 Phase Required Artifact，其状态发生影响后续流程推进的变化；
- PROJECT_PLAN.md Context Mutation 影响项目生命周期规划；
- Execution Planning 提出影响项目当前状态的 State Change Requirement。

Gate 通过后：

- Execution Planning 可以进入 Creation。

具体 Gate Model 与 Gate Definition 由：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_GATE_DESIGN.md

定义。

### 7.7 Implementation Plan Artifact Boundary

Implementation Plan 属于 Project Artifact 层面的 Phase Artifact。

通用目标：

- 将 Solution Design 转换为可执行实施方案；
- 表达 Project Type 对应的实施任务拆解、执行顺序、依赖、验证方式和交付对象；
- 为 Creation Phase 提供执行依据。

Implementation Plan 不属于 Core Context。

Implementation Plan 不替代 PROJECT_PLAN.md。

PROJECT_PLAN.md 仍然是 Core Context，用于记录项目生命周期规划，包括 Phase Goal、Gate、Next Action、Expected Artifact 和 High-level Dependency。

Implementation Plan 的具体结构由 Project Type 决定。

不同 Project Type 可以拥有不同模板，例如：

- Software Implementation Plan；
- Skill Implementation Plan；
- Video Implementation Plan。

## 8. Creation


### 8.1 Phase Goal


执行项目创建。



### 8.2 Input


输入：

- PROJECT_PROFILE.md；
- PROJECT_STATE.md；
- PROJECT_PLAN.md；
- Implementation Plan。



### 8.3 Process


根据项目类型、已确认生命周期规划和 Implementation Plan 完成项目创建活动。

创建活动可以包括：

- 编码；
- 内容创作；
- Skill 开发；
- 文档生成；
- 其他项目活动。

Workflow 只定义 Creation Phase 的目标、输入、Process 边界和输出要求。

具体执行方式不属于 Workflow Domain Model。



### 8.4 Phase Artifact Output 与 Context Mutation

Phase Artifact Output：

Project Artifact。

Context Mutation：

- 更新 PROJECT_STATE.md 中的当前 Phase 状态。

Required Artifact：

- Project Artifact。

### 8.5 State Change Requirement

当前 Phase 完成相关 Process 后，应产生 State Change Requirement。

State Change Requirement 描述：

- 当前 Phase；
- Phase 当前状态；
- 已完成的 Workflow 事项；
- 当前阻塞事项；
- 请求进入的下一 Phase。

Workflow 只定义状态变化需求及其与 Phase Transition 的关系。

具体 Context 修改权限由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md

定义。

具体状态更新与写回机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

### 8.6 Gate Trigger Requirement

以下流程事件需要触发 Gate：

- Creation 提出进入 Validation 的 Phase Transition Request；
- Project Artifact 发生影响后续流程推进的变化；
- Creation 提出影响项目当前状态的 State Change Requirement。

Gate 通过后：

- Creation 可以进入 Validation。

具体 Gate Model 与 Gate Definition 由：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_GATE_DESIGN.md

定义。

## 9. Validation


### 9.1 Phase Goal


确认项目成果是否满足目标。



### 9.2 Input


输入：

- Artifact；
- PROJECT_PROFILE.md；
- PROJECT_PLAN.md。



### 9.3 Process


验证：

- Artifact 完整性；
- Intent 一致性；
- 质量要求；
- 项目约束。


### 9.4 Phase Artifact Output 与 Context Mutation

Phase Artifact Output：

Validation Result。

Context Mutation：

- 更新 PROJECT_STATE.md 中的当前 Phase 状态。

Required Artifact：

- Validation Result。



### 9.5 State Change Requirement

当前 Phase 完成相关 Process 后，应产生 State Change Requirement。

State Change Requirement 描述：

- 当前 Phase；
- Phase 当前状态；
- 已完成的 Workflow 事项；
- 当前阻塞事项；
- 请求进入的下一 Phase。

Workflow 只定义状态变化需求及其与 Phase Transition 的关系。

具体 Context 修改权限由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md

定义。

具体状态更新与写回机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

### 9.6 Gate Trigger Requirement

以下流程事件需要触发 Gate：

- Validation 提出进入 Iteration 的 Phase Transition Request；
- Validation Result 产生或发生影响后续流程推进的变化；
- Validation 提出影响项目当前状态的 State Change Requirement。

Gate 通过后：

- Validation 可以进入 Iteration。

具体 Gate Model 与 Gate Definition 由：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_GATE_DESIGN.md

定义。

## 10. Iteration


### 10.1 Phase Goal


根据 Validation Result 推进下一轮优化。



### 10.2 Input


输入：

- Validation Result；
- PROJECT_STATE.md。



### 10.3 Process

根据 Validation Result：

- 调整解决方案；
- 调整 Implementation Plan；
- 调整项目生命周期规划 Context；
- 修改 Artifact；
- 返回 Solution Design；
- 返回 Execution Planning；
- 返回 Creation；
- 返回 Validation。



### 10.4 Phase Artifact Output 与 Context Mutation

Phase Artifact Output：

根据本轮 Iteration 的实际调整范围，可以更新：

- Solution Design Artifact；
- Implementation Plan；
- Project Artifact。

Context Mutation：

- 更新 PROJECT_PLAN.md 中的项目生命周期规划；
- 更新 PROJECT_STATE.md 中的当前 Phase 状态。

Required Artifact：

- Validation Result；
- 本轮 Iteration 实际修改的 Workflow Artifact。

其中：

- 返回 Solution Design 时，Validation Result 必须能够说明需要重新进入 Solution Design 的问题；
- 返回 Execution Planning 时，Implementation Plan 属于本轮需要继续调整的 Phase Artifact，PROJECT_PLAN.md 属于生命周期规划 Context Mutation 目标；
- 返回 Creation 时，Project Artifact 属于本轮需要继续调整的目标 Artifact；
- 返回 Validation 时，必须存在可再次进入 Validation 的 Project Artifact。

Iteration 不要求创建新的固定 Artifact 类型。


### 10.5 Gate Trigger Requirement

Iteration 根据 Validation Result 可以提出以下 Phase Transition Request：

- 返回 Solution Design；
- 返回 Execution Planning；
- 返回 Creation；
- 返回 Validation。

以下流程事件需要触发 Gate：

- Iteration 提出上述任一 Phase Transition Request；
- Iteration 对 Implementation Plan、PROJECT_PLAN.md、Project Artifact 或其他 Workflow Artifact 提出影响后续流程推进的变更；
- Iteration 提出影响项目当前状态的 State Change Requirement。

Gate 通过后：

- Iteration 可以进入对应的目标 Phase。

具体 Gate Model 与 Gate Definition 由：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_GATE_DESIGN.md

定义。

## 11. Phase Transition Model

Phase Transition 表示项目从当前 Phase 进入允许的下一 Phase。

Phase Transition 必须满足：

- 当前 Phase 已完成必要 Process；
- 当前 Phase 的 Required Artifact Requirement 已满足；
- 当前 Phase 已提出必要的 State Change Requirement；
- 当前 Phase 所需 Gate 已被触发；
- Gate 结果允许项目继续推进。

Workflow 定义：

- Phase 之间允许的转换关系；
- Transition 所需的领域条件；
- Transition 前后需要表达的状态变化需求。

Workflow 不负责：

- 执行 Phase Transition；
- 修改 PROJECT_STATE.md；
- 调用 Gate；
- 执行 State Writeback；
- 持久化 Runtime State。

Phase Transition Contract 由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_WORKFLOW_CONTRACT.md

定义。

Phase Transition 的具体执行机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

## 12. Artifact Flow

Artifact 是 Workflow 推进过程中产生和流转的实际项目成果。

Core Artifact Flow：

Intent Discovery

↓

PROJECT_PROFILE.md

↓

Project Definition

↓

PROJECT_STATE.md

↓

Solution Design

↓

Solution Design Artifact

↓

Execution Planning

↓

Implementation Plan

↓

Creation

↓

Project Artifact

↓

Validation

↓

Validation Result

↓

Iteration

各 Phase 的 Artifact 关系：

Intent Discovery：

- 产生项目身份与目标相关的 Context Artifact；
- 为 Project Definition 提供输入。

Project Definition：

- 建立项目当前状态基础；
- 为 Solution Design 提供项目上下文。

Solution Design：

- 产生 Solution Design Artifact；
- 为 Execution Planning 提供解决方案依据。

Execution Planning：

- 产生 Implementation Plan；
- 更新 PROJECT_PLAN.md 中的项目生命周期规划；
- 为 Creation 提供 Project Type 对应的实施任务、顺序、依赖和 Artifact 目标。

Creation：

- 产生 Project Artifact；
- 为 Validation 提供验证对象。

Validation：

- 产生 Validation Result；
- 为 Iteration 提供问题、差距和后续方向。

Iteration：

- 根据 Validation Result 决定返回 Solution Design、Execution Planning、Creation 或 Validation。

Workflow 只定义 Artifact 的产生、依赖和 Phase 间流转关系。

Artifact 的具体数据结构不属于当前文档。

Artifact 相关的 Runtime 处理机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

---

## 13. Workflow Extension Rules

Project Incubator V1 支持不同 Project Type 在 Core Workflow 基础上进行扩展。

Project Type 可以扩展：

- Phase Detail；
- Phase Process Detail；
- Artifact Requirement；
- Validation Requirement；
- 可选 Workflow 分支；
- Project Type 特定的 Phase Guidance。

Project Type Extension 必须保持：

- Core Phase 身份不变；
- Core Phase 基础目标不变；
- Core Workflow Boundary 不变；
- Core Context Boundary 不变；
- Gate Boundary 不变；
- Runtime Boundary 不变。

Project Type 不允许：

- 删除 Core Phase；
- 重新定义 Core Phase；
- 绕过 Core Gate Requirement；
- 直接修改 Context Domain Model；
- 重新定义 Gate Model；
- 定义 Runtime 执行机制；
- 定义 Contract；
- 改变 Core Workflow 的 Source of Truth。

如果 Project Type 需要特殊 Gate：

- Workflow 只声明该流程节点需要额外 Gate；
- 具体 Gate Definition 由 Gate Design 负责。

如果 Project Type 需要特殊 Runtime 能力：

- Workflow 只声明所需能力；
- 具体执行机制由 Runtime Specification 负责。

具体 Contract、Runtime Capability 和实现文件位置，不属于当前 Workflow Domain Model。
