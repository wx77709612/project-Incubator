# Project Incubator V1 Gate Design


# 1. Gate Architecture Overview


## 1.1 Gate Purpose

Gate 是 Project Incubator Runtime 中用于限制 Agent 高影响行为的控制边界。

Gate 的核心目标：

- 防止 Agent 在未经 Maker 确认情况下改变项目关键状态；
- 防止 Agent 扩大项目范围；
- 防止 Agent 修改权威事实来源；
- 防止 Agent 将单次纠偏错误沉淀为长期规则；
- 在高风险动作发生前强制进入确认流程。


Gate 不负责：

- 替代 Maker 做项目方向决策；
- 替代 Agent 进行创造性工作；
- 替代 Workflow 定义项目阶段；
- 替代 Validation 判断产物质量。


---

# 2. Gate Responsibility Boundary


## 2.1 Workflow Responsibility

Workflow 负责：

- 定义 Phase；
- 定义 Phase Transition；
- 定义 Phase Goal；
- 定义 Phase Input；
- 定义 Phase Output；
- 定义 Phase Required Artifact。


Workflow 可以声明：

- 当前 Phase 是否存在 Gate Requirement。


Workflow 不负责：

- 判断 Agent 动作风险；
- 定义 Gate Rule；
- 执行 Gate Evaluation。


---

## 2.2 Gate Responsibility

Gate Layer 负责：

- 定义 Gate Model；
- 定义 Gate Type；
- 定义 Gate Lifecycle；
- 定义 Gate Trigger Condition；
- 定义 Gate Risk Object；
- 定义 Gate Evaluation Requirement；
- 定义 Maker Authorization Requirement；
- 定义 Gate Allowed Action；
- 定义 Gate Blocked Action。

Gate Layer 不负责：

- 执行具体项目任务；
- 修改项目状态；
- 直接写入权威文件；
- 替 Maker 做最终决策；
- 定义 Gate Invocation Contract；
- 定义 Gate Input / Output；
- 定义 Evaluation Result；
- 定义 Gate Runtime Engine；
- 定义 Script 实现。

Gate Invocation Contract、Gate Input、Gate Output 与 Evaluation Result 由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_GATE_CONTRACT.md

定义。

Gate 的具体执行机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

---

# 3. Gate Model


## 3.1 Gate Definition Model

每一个 Gate 必须定义：

- Gate ID；
- Gate Name；
- Scope；
- Purpose；
- Trigger Condition；
- Risk Object；
- Evaluation Nature；
- Evaluation Requirement；
- Required Authorization；
- Allowed Action；
- Blocked Action。

字段语义：

Gate ID：

- Gate 的唯一领域标识。

Gate Name：

- Gate 的稳定名称。

Scope：

- Gate 适用范围。

Purpose：

- Gate 需要保护的项目边界。

Trigger Condition：

- 哪类项目事件会使 Gate 进入 Triggered 状态。

Risk Object：

- Gate 所保护或约束的对象。

Evaluation Nature：

- Gate 判断属于 Evidence-Based、Judgment-Based 或 Mixed。

Evaluation Requirement：

- Gate 在领域层面需要确认哪些事实、风险或条件。

Required Authorization：

- 哪些情况必须由 Maker 明确授权。

Allowed Action：

- Gate Requirement 满足后允许继续的项目行为。

Blocked Action：

- Gate Requirement 未满足时不得继续的项目行为。

本文件不定义：

- Gate Input；
- Gate Output；
- Evaluation Result；
- Invocation Interface；
- Runtime Execution。

---

## 3.2 Gate Trigger Model

Gate Trigger 表示某个项目事件进入 Gate 保护范围。

Gate 可以由以下类型的领域事件触发：

- Phase 变化；
- 项目状态变化；
- 权威信息变化；
- Project Scope 变化；
- Builder 执行边界变化；
- Context 完整性或可信度变化；
- 项目长期规则变化；
- Artifact Boundary 变化；
- Architecture Decision 变化；
- Framework 或 Gate Model 变化。

Gate Trigger 只表示：

- 当前行为已经进入某个 Gate 的保护范围。

Gate Trigger 不代表：

- Gate 已经通过；
- Maker 已经授权；
- Runtime 已经执行；
- 项目状态可以立即改变。

具体 Gate Invocation 机制由 Runtime Specification 定义。

---

## 3.3 Gate Lifecycle

每一个 Gate Instance 在领域层面可以处于以下状态：

- Inactive；
- Triggered；
- Awaiting Evaluation；
- Awaiting Authorization；
- Resolved；
- Reopened。

### Inactive

当前不存在满足该 Gate Trigger Condition 的项目事件。

Gate 尚未进入当前项目行为的控制范围。

### Triggered

已经发生满足 Gate Trigger Condition 的项目事件。

Gate Requirement 必须被处理后，相关行为才能继续。

### Awaiting Evaluation

Gate 已被触发，但完成 Gate 判断所需的事实、上下文或风险信息尚未形成稳定结论。

### Awaiting Authorization

Gate 的 Evaluation Requirement 已经能够形成判断，但当前行为属于 Required Authorization 范围，需要 Maker 明确授权。

### Resolved

当前 Gate Requirement 已经完成处理。

Gate 在领域层面不再存在未解决的 Evaluation 或 Authorization Requirement。

Resolved 不定义 Runtime 应输出什么 Evaluation Result。

具体 Evaluation Result 属于 Gate Contract。

### Reopened

已经 Resolved 的 Gate 因以下情况之一重新进入 Gate Lifecycle：

- Risk Object 发生实质变化；
- Trigger Action 发生变化；
- Evaluation 所依据的事实发生变化；
- Maker 修改相关授权；
- 项目上下文发生影响原判断的变化。

Reopened 后必须重新满足当前 Gate Definition。

Gate Lifecycle 只定义领域状态及其语义。

Gate Lifecycle 的具体 Runtime State Transition 机制由 Runtime Specification 定义。

---

# 4. Gate Classification


## 4.1 Universal Gate


适用于所有 Project 类型：

包括：

- App；
- Skill；
- Script；
- Code Project；
- Video Content；
- Other Creative Project。


---

## 4.2 Project Type Specific Gate

Project Type Specific Gate 只适用于特定 Project Type。

用于表达某一种 Project Type 独有的：

- 风险；
- 项目约束；
- Artifact Boundary；
- Workflow Requirement；
- Project Type 特定保护边界。

例如：

不同 Project Type 可以根据自身特点定义：

- App 特定 Gate；
- Skill 特定 Gate；
- Code Project 特定 Gate；
- Video Content 特定 Gate；
- 其他 Project Type 特定 Gate。

Project Type Specific Gate 不允许：

- 重新定义 Universal Gate；
- 降低 Universal Gate 的保护要求；
- 绕过 Universal Gate；
- 修改 Core Workflow Domain Model；
- 修改 Core Context Domain Model；
- 修改 Runtime Architecture。

Project Type Specific Gate 只能增加特定 Project Type 所需的额外保护边界。

---

## 4.3 Project Incubator Specific Gate


只适用于 Project Incubator 自身：

包括：

- Framework 修改；
- Phase Model 修改；
- Gate System 修改；
- Runtime Architecture 修改。


---

# 5. Gate Evaluation Model

Gate Evaluation 在 Domain Model 中只描述判断所依赖的信息性质，不定义由 Agent、Script 或 Runtime 如何执行。

Gate Evaluation Nature 分为：

## 5.1 Evidence-Based

Gate 可以主要依据明确、可观察、可验证的事实进行判断。

例如：

- 文件是否存在；
- Artifact 是否存在；
- 当前 Phase 是否明确；
- Git 状态是否发生变化；
- 必需信息是否缺失。

Evidence-Based 只描述判断依据的性质，不代表必须由 Script 执行。

---

## 5.2 Judgment-Based

Gate 必须依赖项目语义、风险、上下文或 Maker Intent 才能完成判断。

例如：

- 是否扩大 Project Scope；
- 是否属于 Architecture Decision；
- 是否应该沉淀长期规则；
- 是否改变项目方向。

Judgment-Based 只描述判断性质，不定义具体执行者。

---

## 5.3 Mixed

Gate 同时依赖：

- 可验证事实；
- 项目语义或风险判断。

Mixed Gate 的 Domain Model 只定义需要判断什么。

具体 Evaluation 如何执行，由 Runtime Specification 决定。

---

# 6. Gate Type Definition

## 6.1 Git Gate

Gate ID：

GATE-GIT

Gate Name：

Git Gate

Scope：

Universal Gate。

Purpose：

保护 Git Repository 状态和版本历史，防止未经确认的高影响 Git 操作。

Trigger Condition：

以下行为进入 Git Gate：

- commit；
- push；
- merge；
- branch 创建；
- branch 切换；
- Git history 修改；
- branch 删除。

Risk Object：

- Repository State；
- Branch；
- Commit History；
- Remote Repository。

Evaluation Nature：

Evidence-Based。

Evaluation Requirement：

需要确认：

- 当前 Git 状态是否明确；
- 当前操作目标是否明确；
- 当前操作是否存在未处理修改；
- 当前操作是否可能影响远程仓库或版本历史。

Required Authorization：

以下行为必须获得 Maker 明确授权：

- push；
- merge；
- 修改 Git History；
- 删除 Branch。

Allowed Action：

Gate Requirement 满足后，可以继续对应 Git 操作。

Blocked Action：

Gate Requirement 未满足时，不允许执行对应 Git 操作。

---

## 6.2 Phase Gate

Gate ID：

GATE-PHASE

Gate Name：

Phase Gate

Scope：

Universal Gate。

Purpose：

保护 Core Workflow 的 Phase Boundary，防止项目在不满足 Workflow Requirement 时改变 Phase。

Trigger Condition：

以下行为进入 Phase Gate：

- Phase Transition；
- Phase Skip；
- Phase Rollback；
- 修改当前 Phase 状态。

Risk Object：

- Current Phase；
- Target Phase；
- Required Artifact；
- State Change Requirement；
- Phase Transition Boundary。

Evaluation Nature：

Mixed。

Evaluation Requirement：

需要确认：

- Current Phase 是否明确；
- Target Phase 是否属于允许的下一 Phase；
- 当前 Phase 的 Required Artifact Requirement 是否满足；
- 必要的 State Change Requirement 是否已经形成；
- 是否存在阻止 Phase Transition 的未解决条件。

Required Authorization：

以下行为必须获得 Maker 明确授权：

- Skip Core Phase；
- Rollback 到非正常 Workflow Path；
- 修改 Phase Model。

Allowed Action：

Gate Requirement 满足后，可以提出或继续对应 Phase Transition。

Blocked Action：

Gate Requirement 未满足时，不允许完成对应 Phase Transition。

---

## 6.3 Authority Document Gate

Gate ID：

GATE-AUTHORITY-DOCUMENT

Gate Name：

Authority Document Gate

Scope：

Universal Gate。

Purpose：

保护项目中的 Authority Document 与 Source of Truth 关系。

Trigger Condition：

以下行为进入 Authority Document Gate：

- 修改 Authority Document；
- 修改文档职责归属；
- 修改 Source of Truth；
- 修改长期规则文件。

Risk Object：

- Authority Document；
- Source of Truth；
- Document Responsibility Boundary；
- Long-Term Project Rule。

Evaluation Nature：

Mixed。

Evaluation Requirement：

需要确认：

- 目标文档是否属于 Authority Document；
- 修改是否改变 Source of Truth；
- 修改是否改变文档职责边界；
- 修改是否改变已经冻结的长期规则或项目事实。

Required Authorization：

以下行为必须获得 Maker 明确授权：

- 修改 PROJECT_PROFILE；
- 修改 PROJECT_DECISIONS；
- 改变 Source of Truth；
- 改变已冻结的 Framework Rule。

Allowed Action：

Gate Requirement 满足后，可以继续对应 Authority Document 修改。

Blocked Action：

Gate Requirement 未满足时，不允许修改相关 Authority Document 或 Source of Truth。

---

## 6.4 Scope Gate

Gate ID：

GATE-SCOPE

Gate Name：

Scope Gate

Scope：

Universal Gate。

Purpose：

防止项目目标、用户范围、商业目标或交付范围在未经 Maker 确认时扩大。

Trigger Condition：

以下行为进入 Scope Gate：

- 新增 Project Goal；
- 新增目标用户；
- 新增商业目标；
- 新增 Project Type；
- 扩大 Deliverable Scope；
- 将当前项目扩展到新的问题域。

Risk Object：

- Project Goal；
- Project Scope；
- Target User；
- Business Objective；
- Deliverable Boundary。

Evaluation Nature：

Judgment-Based。

Evaluation Requirement：

需要判断：

- 新增内容是否属于当前 Project Scope；
- 是否改变原始 Project Intent；
- 是否显著增加项目复杂度；
- 是否更适合作为独立 Project；
- 是否改变当前项目的 Success Criteria。

Required Authorization：

任何 Scope Expansion 必须获得 Maker 明确授权。

Allowed Action：

Maker 明确授权后，可以将新增范围纳入当前 Project。

Blocked Action：

未经 Maker 授权，不允许扩大当前 Project Scope。

---

## 6.5 Builder Gate

Gate ID：

GATE-BUILDER

Gate Name：

Builder Gate

Scope：

Universal Gate。

Purpose：

确保 Builder 或 Codex 开始实现前，任务边界、目标和预期结果已经明确。

Trigger Condition：

以下行为进入 Builder Gate：

- Agent 将任务交给 Builder；
- Codex 开始执行代码修改；
- Codex 开始执行文件修改；
- Builder 准备执行可能影响项目结构的任务。

Risk Object：

- Builder Task；
- Task Scope；
- Input；
- Expected Output；
- Validation Requirement；
- Execution Boundary。

Evaluation Nature：

Mixed。

Evaluation Requirement：

需要确认：

- Task Goal 是否明确；
- Non-Goal 是否明确；
- Input 是否充分；
- Expected Output 是否明确；
- Validation Requirement 是否明确；
- Builder Boundary 是否明确；
- 当前任务是否具备执行条件。

Required Authorization：

以下行为必须获得 Maker 明确授权：

- Builder 修改核心架构；
- Builder 修改 Authority Document；
- Builder 执行不可逆操作。

Allowed Action：

Gate Requirement 满足后，可以将任务交给 Builder 执行。

Blocked Action：

Gate Requirement 未满足时，不允许开始 Builder Implementation。

---

## 6.6 Unclosed Task Gate

Gate ID：

GATE-UNCLOSED-TASK

Gate Name：

Unclosed Task Gate

Scope：

Universal Gate。

Purpose：

防止项目在当前 Task 或相关 Artifact 尚未正确收敛时无控制地切换到其他工作。

Trigger Condition：

以下情况进入 Unclosed Task Gate：

- 当前 Task 尚未完成；
- 当前 Task 存在未处理变更；
- Required Artifact 尚未完成；
- 当前工作准备被放弃或切换。

Risk Object：

- Current Task；
- Unfinished Change；
- Incomplete Artifact；
- Current Work Context。

Evaluation Nature：

Mixed。

Evaluation Requirement：

需要确认：

- 当前 Task 是否仍然处于未完成状态；
- 是否存在需要保留的未完成工作；
- 是否存在尚未处理的 Artifact；
- 切换 Task 是否会造成项目上下文丢失。

Required Authorization：

以下行为必须获得 Maker 明确授权：

- 放弃当前 Task；
- 删除未完成 Artifact；
- 丢弃具有项目价值的未完成变更。

Allowed Action：

Gate Requirement 满足后，可以结束、暂停或切换当前 Task。

Blocked Action：

Gate Requirement 未满足时，不允许无记录地放弃或跳过当前 Task。

---

## 6.7 Context Integrity Gate

Gate ID：

GATE-CONTEXT-INTEGRITY

Gate Name：

Context Integrity Gate

Scope：

Universal Gate。

Purpose：

防止 Agent 在项目上下文不完整、不可信或相互冲突时继续执行高影响操作。

Trigger Condition：

以下情况进入 Context Integrity Gate：

- Context 不完整；
- Context 信息发生冲突；
- Agent 无法确认当前项目状态；
- Context 压缩导致重要信息缺失；
- Source of Truth 与当前理解不一致。

Risk Object：

- Project Context；
- Current State；
- Project Identity；
- Decision History；
- Context Trustworthiness。

Evaluation Nature：

Mixed。

Evaluation Requirement：

需要确认：

- 必需 Context 是否存在；
- 当前 Context 是否足以判断项目状态；
- 是否存在相互冲突的信息；
- 是否需要重新读取 Authority Context；
- 是否需要 Maker 澄清。

Required Authorization：

以下行为必须获得 Maker 明确授权：

- 在已知 Context 不完整的情况下继续高影响修改；
- 重建具有长期影响的项目状态。

Allowed Action：

Context 足够可信后，可以继续依赖当前 Context 推进项目。

Blocked Action：

Context 不足以支持可靠判断时，不允许继续执行高影响项目变更。

---

## 6.8 Local Protocol Gate

Gate ID：

GATE-LOCAL-PROTOCOL

Gate Name：

Local Protocol Gate

Scope：

Universal Gate。

Purpose：

保护项目中的长期协议、输出约束和 Agent 行为规则。

Trigger Condition：

以下行为进入 Local Protocol Gate：

- 修改 Project Rule；
- 修改 Output Protocol；
- 修改 Agent Behavior Constraint；
- 新增长期例外规则。

Risk Object：

- Local Protocol；
- Output Rule；
- Agent Behavior Rule；
- Rule Priority；
- Rule Exception。

Evaluation Nature：

Mixed。

Evaluation Requirement：

需要确认：

- 当前修改是否与既有规则冲突；
- 修改是否改变规则优先级；
- 是否引入新的长期例外；
- 是否会改变 Agent 的长期行为边界。

Required Authorization：

修改长期规则必须获得 Maker 明确授权。

Allowed Action：

Maker 明确确认后，可以修改或新增长期 Project Protocol。

Blocked Action：

未经授权，不允许改变长期 Project Protocol。

---

## 6.9 Artifact Boundary Gate

Gate ID：

GATE-ARTIFACT-BOUNDARY

Gate Name：

Artifact Boundary Gate

Scope：

Universal Gate。

Purpose：

保护项目 Artifact 的承载类型和成果边界，防止项目成果在未经确认时改变性质。

Trigger Condition：

以下情况进入 Artifact Boundary Gate：

- Artifact Type 发生变化；
- Artifact 承载形式发生变化；
- 当前输出无法明确归属于预期 Artifact；
- 核心 Deliverable 类型准备改变。

Risk Object：

- Artifact Type；
- Artifact Boundary；
- Deliverable Type；
- Artifact Carrier。

Evaluation Nature：

Mixed。

Evaluation Requirement：

需要确认：

- 当前 Artifact 是否符合项目目标；
- 当前 Artifact 是否属于 Workflow 所要求的成果；
- Artifact 类型变化是否影响后续 Workflow；
- 是否正在改变核心 Deliverable 形式。

Required Authorization：

改变核心 Artifact Type 必须获得 Maker 明确授权。

Allowed Action：

Gate Requirement 满足后，可以继续生成或修改对应 Artifact。

Blocked Action：

Gate Requirement 未满足时，不允许改变核心 Artifact Boundary。

---

## 6.10 Challenge Response Gate

Gate ID：

GATE-CHALLENGE-RESPONSE

Gate Name：

Challenge Response Gate

Scope：

Universal Gate。

Purpose：

确保 Maker 对当前方案提出质疑后，Agent 必须重新判断而不是自动维护原有方案或直接改变方向。

Trigger Condition：

以下情况进入 Challenge Response Gate：

- Maker 质疑当前设计；
- Maker 质疑当前判断；
- Maker 要求重新分析已经确定的方案。

Risk Object：

- Current Design；
- Current Recommendation；
- Current Decision Assumption；
- Maker Intent Interpretation。

Evaluation Nature：

Judgment-Based。

Evaluation Requirement：

需要：

- 重新理解 Maker 的质疑；
- 重新分析原判断依据；
- 判断原方案是否仍然成立；
- 明确哪些内容需要调整，哪些内容可以保持。

Required Authorization：

如果重新判断导致项目方向、架构或已冻结决策发生变化，必须获得 Maker 明确确认。

Allowed Action：

完成重新分析后，可以提出保持、调整或重新设计建议。

Blocked Action：

不得忽略 Maker Challenge，也不得将 Agent 自己的重新判断直接视为 Maker Authorization。

---

## 6.11 Correction Persistence Gate

Gate ID：

GATE-CORRECTION-PERSISTENCE

Gate Name：

Correction Persistence Gate

Scope：

Universal Gate。

Purpose：

防止一次性的纠偏被 Agent 自动沉淀为长期规则。

Trigger Condition：

以下情况进入 Correction Persistence Gate：

- Agent 准备将一次纠偏写入长期规则；
- Agent 准备根据单次反馈修改长期行为约束；
- Agent 准备将当前例外转化为永久协议。

Risk Object：

- Long-Term Rule；
- Persistent Behavior Constraint；
- Project Protocol；
- Agent Guidance。

Evaluation Nature：

Judgment-Based。

Evaluation Requirement：

需要判断：

- 当前纠偏是否具有长期适用性；
- 是否只是当前场景例外；
- 是否会影响未来项目行为；
- 是否可能与既有长期规则冲突。

Required Authorization：

任何新的长期规则或长期行为约束必须获得 Maker 明确授权。

Allowed Action：

Maker 明确确认后，可以将纠偏沉淀为长期规则。

Blocked Action：

未经 Maker 明确确认，不允许将单次纠偏自动沉淀为长期规则。

---

## 6.12 Architecture Decision Gate

Gate ID：

GATE-ARCHITECTURE-DECISION

Gate Name：

Architecture Decision Gate

Scope：

Universal Gate。

Purpose：

保护具有长期系统影响的 Architecture Decision。

Trigger Condition：

以下行为进入 Architecture Decision Gate：

- 新增 Architecture Decision；
- 修改已有 Architecture Decision；
- 修改具有长期系统影响的架构原则。

Risk Object：

- Architecture Decision；
- Long-Term Architecture；
- System Boundary；
- Architectural Constraint。

Evaluation Nature：

Mixed。

Evaluation Requirement：

需要确认：

- 当前决定是否属于 Architecture Decision；
- 决定是否具有长期影响；
- 是否影响多个模块或下游设计；
- 是否改变已冻结的 Architecture Boundary。

Required Authorization：

新增或修改 Architecture Decision 必须获得 Maker 明确授权。

Allowed Action：

Maker 明确确认后，可以记录或修改 Architecture Decision。

Blocked Action：

未经 Maker 授权，不允许将架构建议确立为长期 Architecture Decision。

---

## 6.13 Framework Modification Gate

Gate ID：

GATE-FRAMEWORK-MODIFICATION

Gate Name：

Framework Modification Gate

Scope：

Project Incubator Specific Gate。

Purpose：

保护 Project Incubator Framework 的整体结构和长期行为。

Trigger Condition：

以下行为进入 Framework Modification Gate：

- 修改 Project Incubator Framework；
- 修改 Framework 核心职责；
- 修改 Framework 核心结构；
- 修改 Framework 长期规则。

Risk Object：

- Project Incubator Framework；
- Framework Boundary；
- Framework Responsibility；
- Framework Long-Term Rule。

Evaluation Nature：

Mixed。

Evaluation Requirement：

需要确认：

- Framework 修改是否必要；
- 是否改变核心架构；
- 是否影响已经冻结的系统边界；
- 是否影响下游 Design / Contract / Runtime。

Required Authorization：

任何 Framework Modification 必须获得 Maker 明确授权。

Allowed Action：

Maker 明确确认后，可以继续 Framework Modification。

Blocked Action：

未经 Maker 授权，不允许修改 Project Incubator Framework。

---

## 6.14 Phase Model Modification Gate

Gate ID：

GATE-PHASE-MODEL-MODIFICATION

Gate Name：

Phase Model Modification Gate

Scope：

Project Incubator Specific Gate。

Purpose：

保护已经冻结的 Core Phase Model 和 Workflow Domain Model。

Trigger Condition：

以下行为进入 Phase Model Modification Gate：

- 修改 Core Phase；
- 修改 Phase Definition；
- 修改 Phase Goal；
- 修改 Phase Lifecycle；
- 修改 Core Phase Relationship。

Risk Object：

- Core Phase Model；
- Phase Definition；
- Phase Lifecycle；
- Workflow Domain Model。

Evaluation Nature：

Mixed。

Evaluation Requirement：

需要确认：

- 修改是否改变 Core Phase 身份；
- 是否改变 Phase 基础目标；
- 是否改变 Phase Lifecycle；
- 是否影响 Workflow Source of Truth；
- 是否要求同步修改下游 Contract 或 Runtime。

Required Authorization：

任何 Core Phase Model Modification 必须获得 Maker 明确授权。

Allowed Action：

Maker 明确确认后，可以修改 Phase Model。

Blocked Action：

未经 Maker 授权，不允许修改已经冻结的 Phase Model。

---

## 6.15 Gate Matrix Modification Gate

Gate ID：

GATE-MATRIX-MODIFICATION

Gate Name：

Gate Matrix Modification Gate

Scope：

Project Incubator Specific Gate。

Purpose：

保护 Gate Domain Model 自身，防止 Gate Protection Boundary 被未经授权地改变或削弱。

Trigger Condition：

以下行为进入 Gate Matrix Modification Gate：

- 新增 Gate Type；
- 删除 Gate Type；
- 修改现有 Gate Definition；
- 修改 Gate Scope；
- 修改 Required Authorization；
- 修改 Gate Protection Boundary。

Risk Object：

- Gate Model；
- Gate Type；
- Gate Definition；
- Gate Protection Boundary；
- Maker Authorization Requirement。

Evaluation Nature：

Mixed。

Evaluation Requirement：

需要确认：

- Gate 变化是否改变现有保护边界；
- 是否降低已有 Gate 的控制强度；
- 是否改变 Maker Authorization Requirement；
- 是否改变 Gate Domain Model 的长期语义。

Required Authorization：

任何 Gate Model、Gate Type 或 Gate Definition 的实质性修改必须获得 Maker 明确授权。

Allowed Action：

Maker 明确确认后，可以修改 Gate Domain Model。

Blocked Action：

未经 Maker 授权，不允许新增、删除或实质性修改 Gate Type。

---

# 7. Gate Extension Model

Project Incubator V1 允许根据新的项目风险和保护边界新增 Gate Type。

新增 Gate Type 时，必须完整定义：

- Gate ID；
- Gate Name；
- Scope；
- Purpose；
- Trigger Condition；
- Risk Object；
- Evaluation Nature；
- Evaluation Requirement；
- Required Authorization；
- Allowed Action；
- Blocked Action。

新增 Gate Type 必须明确属于以下 Scope 之一：

- Universal Gate；
- Project Type Specific Gate；
- Project Incubator Specific Gate。

新增 Gate Type 必须满足：

- 不降低现有 Gate 的保护边界；
- 不绕过 Maker Authorization Requirement；
- 不改变其他 Gate Type 已冻结的领域语义；
- 不重新定义 Workflow Domain Model；
- 不重新定义 Context Domain Model；
- 不重新定义 Runtime Architecture；
- 不定义 Gate Invocation Contract；
- 不定义 Gate Runtime Engine；
- 不定义 Script 实现。

如果新增 Gate 需要新的交互契约：

由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_GATE_CONTRACT.md

定义。

如果新增 Gate 需要新的执行机制：

由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

Gate Extension Model 只负责新增 Gate Type 的领域定义规则。

---

# 8. V1 Scope

Project Incubator V1 Gate Design 定义：

- Gate Model；
- Gate Type；
- Gate Classification；
- Gate Trigger Model；
- Gate Lifecycle；
- Gate Definition Model；
- Gate Evaluation Nature；
- Gate Evaluation Requirement；
- Gate Risk Object；
- Maker Authorization Requirement；
- Allowed Action；
- Blocked Action；
- Gate Extension Model。

V1 Gate Design 不定义：

- Gate Input；
- Gate Output；
- Evaluation Result；
- Gate Invocation Contract；
- Gate API；
- Gate Runtime Engine；
- Gate Runtime Execution；
- Script Invocation；
- Validation Script；
- Script Implementation；
- Runtime Component；
- Codex Implementation Task。

Gate Input、Gate Output、Evaluation Result 与 Gate Invocation Contract 由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_GATE_CONTRACT.md

定义。

Gate 的具体执行机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

具体实现任务由：

SPECS/IMPLEMENTATION/PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md

定义。