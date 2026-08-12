# Project Incubator V1 Gate Contract

# 1. Contract Purpose

本文档定义 Project Incubator V1 的 Gate Invocation Contract。

本文档属于：

Contract Layer。

本文档负责定义：

- Gate Invocation Contract；
- Gate Input；
- Gate Output；
- Evaluation Result；
- Maker Authorization Contract。

本文档将已经冻结的 Gate Domain Model 转化为 Runtime 可以消费的交互契约。

本文档不重新定义：

- Gate Model；
- Gate Type；
- Gate Classification；
- Gate Lifecycle；
- Gate Trigger Condition；
- Gate Risk Object；
- Gate Evaluation Nature；
- Gate Evaluation Requirement；
- Required Authorization；
- Allowed Action；
- Blocked Action。

Gate Domain Model 由：

`SPECS/DESIGN/PROJECT_INCUBATOR_V1_GATE_DESIGN.md`

定义。

Workflow Runtime Interface 由：

`SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_WORKFLOW_CONTRACT.md`

定义。

Context Access Permission 由：

`SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md`

定义。

Gate 的具体 Runtime Invocation 与执行机制由：

`SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`

定义。

---

# 2. Gate Contract Model

## 2.1 Contract Responsibility

Gate Contract 向 Runtime 暴露：

- Gate Invocation Request；
- Gate Input；
- Evaluation Evidence；
- Maker Authorization Evidence；
- Evaluation Result；
- Gate Output。

Gate Contract 不执行：

- Gate Trigger Detection；
- Gate Runtime Invocation；
- Runtime State Change；
- Workflow Transition；
- Context Mutation；
- Artifact Mutation；
- Script Invocation。

---

## 2.2 Gate Definition Reference

每一次 Gate Invocation：

必须引用一个已经存在于 Gate Domain Model 中的 Gate Definition。

Gate Definition Reference 必须能够关联：

- Gate ID；
- Gate Name；
- Scope；
- Trigger Condition；
- Risk Object；
- Evaluation Nature；
- Evaluation Requirement；
- Required Authorization；
- Allowed Action；
- Blocked Action。

Gate Contract：

只引用上述 Domain Definition。

不得在 Invocation 中重新定义上述字段。

---

## 2.3 V1 Gate Set

Project Incubator V1 Gate Contract 支持当前 Gate Design 中已经定义的 Gate：

| Gate ID | Gate Name |
| --- | --- |
| GATE-GIT | Git Gate |
| GATE-PHASE | Phase Gate |
| GATE-AUTHORITY-DOCUMENT | Authority Document Gate |
| GATE-SCOPE | Scope Gate |
| GATE-BUILDER | Builder Gate |
| GATE-UNCLOSED-TASK | Unclosed Task Gate |
| GATE-CONTEXT-INTEGRITY | Context Integrity Gate |
| GATE-LOCAL-PROTOCOL | Local Protocol Gate |
| GATE-ARTIFACT-BOUNDARY | Artifact Boundary Gate |
| GATE-CHALLENGE-RESPONSE | Challenge Response Gate |
| GATE-CORRECTION-PERSISTENCE | Correction Persistence Gate |
| GATE-ARCHITECTURE-DECISION | Architecture Decision Gate |
| GATE-FRAMEWORK-MODIFICATION | Framework Modification Gate |
| GATE-PHASE-MODEL-MODIFICATION | Phase Model Modification Gate |
| GATE-MATRIX-MODIFICATION | Gate Matrix Modification Gate |

该列表只绑定：

现有 Gate Definition

与：

Gate Invocation Contract。

不得通过本表新增或修改 Gate Type。

---

# 3. Gate Invocation Contract

## 3.1 Gate Invocation Request

Gate Invocation Request 表示：

Runtime 请求针对一个已经触发的 Gate Requirement 形成 Gate Evaluation。

Gate Invocation Request：

只表达交互请求。

不表示：

- Gate 已经完成 Evaluation；
- Gate Requirement 已满足；
- Maker 已经授权；
- Runtime 可以继续执行受保护行为。

---

## 3.2 Required Fields

每一个 Gate Invocation Request 必须能够表达：

- Invocation ID；
- Gate Definition Reference；
- Gate Trigger Reference；
- Trigger Event Reference；
- Risk Object Reference；
- Requested Action Reference；
- Current Project Context Reference；
- Current Workflow / Phase Reference；
- Evaluation Requirement Reference；
- Required Authorization Reference；
- Evaluation Evidence；
- Maker Authorization Evidence；
- Validation Evidence Reference。

不存在的 Optional Evidence：

必须明确表示为空。

不得通过省略字段表达隐含状态。

---

## 3.3 Invocation ID

Invocation ID：

唯一标识一次 Gate Evaluation Request。

同一个 Gate：

在不同 Trigger Event、不同 Risk Object 或不同 Requested Action 下：

必须使用不同 Invocation。

Gate Reopened：

不得继续使用已经失去事实基础的旧 Invocation Result 作为当前 Evaluation Result。

---

## 3.4 Gate Trigger Reference

Gate Trigger Reference 必须能够关联：

- Gate ID；
- Trigger Event；
- Trigger Object；
- Trigger Source；
- Trigger Context。

Gate Trigger Reference 必须对应：

目标 Gate Definition 已存在的 Trigger Condition。

Gate Contract 不得创造新的 Trigger Condition。

---

## 3.5 Trigger Event Reference

Trigger Event Reference 表示：

实际进入 Gate Protection Boundary 的项目事件。

该 Reference 必须能够证明：

当前事件与目标 Gate Trigger Condition 存在直接对应关系。

Gate Contract 不负责：

检测 Trigger Event 是如何发生的。

---

## 3.6 Risk Object Reference

Risk Object Reference 必须指向：

当前 Gate Invocation 实际保护或约束的对象。

Risk Object：

必须属于目标 Gate Definition 已定义的 Risk Object Scope。

不得在 Contract 中扩展 Gate 的 Risk Object Domain。

---

## 3.7 Requested Action Reference

Requested Action Reference 表示：

如果 Gate Requirement 被满足，调用方希望继续的受保护行为。

Requested Action 必须能够与目标 Gate Definition 中的：

- Allowed Action；
- Blocked Action

建立对应关系。

Gate Output：

只能决定当前 Requested Action 是否满足 Gate Contract 条件。

不得自动执行 Requested Action。

---

# 4. Gate Input Contract

## 4.1 Gate Input Purpose

Gate Input 表示：

完成当前 Gate Evaluation 所需要的领域事实、引用和 Evidence。

Gate Input 只能承载：

上游冻结文档已经存在的信息。

不得通过 Gate Input：

新增 Domain Rule。

---

## 4.2 Core Gate Input

每一个 Gate Input 必须能够表达：

- Gate Definition Reference；
- Trigger Event；
- Risk Object；
- Requested Action；
- Evaluation Requirement；
- Current Context Reference；
- Current Workflow / Phase Reference；
- Relevant Artifact Reference；
- Evidence Set；
- Maker Authorization Evidence；
- Validation Evidence Reference。

并非所有 Gate 都需要所有 Reference。

实际 Required Input：

由目标 Gate Definition 的 Evaluation Requirement 决定。

---

# 5. Evaluation Evidence Model

## 5.1 Evidence Purpose

Evaluation Evidence 用于支撑：

Gate Evaluation Requirement 中已经定义的事实或判断。

Evidence：

不改变 Gate Definition。

---

## 5.2 Evidence Category

Gate Input 可以引用以下 Evidence Category：

- Context Evidence；
- Workflow Evidence；
- Artifact Evidence；
- Operation Evidence；
- Builder Task Evidence；
- Rule / Protocol Evidence；
- Architecture Evidence；
- Maker Statement Evidence；
- Judgment Evidence；
- Validation Evidence。

上述 Category：

只表示 Evidence 来源类别。

不是新的 Gate Type。

---

## 5.3 Context Evidence

Context Evidence 必须来自：

Gate Runtime Component 依法可以读取的 Context。

Context Read 必须遵循：

`PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md`

Gate Runtime Component：

只有在目标 Gate Evaluation Requirement 需要对应 Context Evidence 时：

才能读取该 Context。

---

## 5.4 Workflow Evidence

Workflow Evidence 可以引用：

- Current Phase；
- Requested Next Phase；
- Required Artifact Requirement；
- State Change Requirement；
- Gate Trigger Requirement；
- Transition Eligibility Information；
- Workflow Artifact Reference。

Workflow Evidence 必须来源于：

`PROJECT_INCUBATOR_V1_WORKFLOW_CONTRACT.md`

已经定义的信息。

Gate Contract：

不得修改 Allowed Next Phase。

---

## 5.5 Validation Evidence

当 Gate Evaluation Requirement 包含：

可以通过确定性验证确认的事实时，

Gate Input 可以包含：

Validation Evidence Reference。

Validation Evidence：

可以支撑 Gate Evaluation。

但：

Validation Result 不等于 Gate Evaluation Result。

Gate Contract 不定义：

- Script Input；
- Script Output；
- Script Error Handling；
- Script Invocation Protocol。

这些由：

`PROJECT_INCUBATOR_V1_SCRIPT_CONTRACT.md`

定义。

---

## 5.6 Judgment Evidence

Judgment-Based 或 Mixed Gate：

可以接收 Judgment Evidence。

Judgment Evidence 必须：

- 与当前 Risk Object 直接相关；
- 基于当前项目事实；
- 明确说明判断依据；
- 不把 Agent 判断表示为 Maker Authorization。

Judgment Evidence：

不自动获得决策 Authority。

---

# 6. Evaluation Nature Contract Projection

## 6.1 Evidence-Based

当目标 Gate 的 Evaluation Nature 为：

`Evidence-Based`

Gate Input 必须提供足以确认目标 Evaluation Requirement 的事实 Evidence。

不存在足够 Evidence 时：

Evaluation Result 必须为：

`EVIDENCE_INSUFFICIENT`

不得通过无依据推测形成满足结果。

---

## 6.2 Judgment-Based

当 Evaluation Nature 为：

`Judgment-Based`

Gate Input 必须包含：

足以支持当前 Evaluation Requirement 的项目语义、Risk、Context 或 Maker Intent Evidence。

仅存在机械事实：

但不足以完成领域判断时：

不得返回：

`REQUIREMENT_SATISFIED`

---

## 6.3 Mixed

当 Evaluation Nature 为：

`Mixed`

Gate Input 必须同时支持：

- 可以确定性验证的事实部分；
- 需要项目语义或风险判断的部分。

任一必要部分不足：

不得返回：

`REQUIREMENT_SATISFIED`

---

# 7. Evaluation Result Model

## 7.1 Result Set

Project Incubator V1 Gate Contract 只允许以下五种 Evaluation Result：

- `REQUIREMENT_SATISFIED`；
- `REQUIREMENT_UNSATISFIED`；
- `AUTHORIZATION_REQUIRED`；
- `EVIDENCE_INSUFFICIENT`；
- `ACTION_BLOCKED`。

不得另外使用：

- PASS；
- SUCCESS；
- ALLOW；
- FAIL；
- DENY；
- APPROVED；
- REJECTED

作为 Gate Evaluation Result。

---

## 7.2 REQUIREMENT_SATISFIED

表示：

当前 Gate Evaluation 已经完成，

并且：

- 所有必要 Evaluation Requirement 已满足；
- 所需 Evidence 已充分；
- 如果当前行为要求 Maker Authorization，则已经存在有效 Authorization Evidence；
- 当前 Requested Action 不处于 Blocked Action 状态。

只有：

`REQUIREMENT_SATISFIED`

可以表示：

当前 Gate Contract 不再阻止对应 Requested Action。

该 Result：

不表示 Requested Action 已经执行。

---

## 7.3 REQUIREMENT_UNSATISFIED

表示：

Gate Evaluation 已经具有充分信息，

但至少一个 Evaluation Requirement 当前不满足。

该状态用于表达：

当前问题属于可以识别的未满足 Requirement，

而不是 Evidence 不足。

例如：

- Required Artifact Requirement 当前未满足；
- 当前 Task 尚未收敛；
- 当前 Context 仍存在可明确识别的完整性问题；
- Builder Task Requirement 尚未满足；
- 某项保护条件尚未达到。

`REQUIREMENT_UNSATISFIED`：

不允许当前 Requested Action 继续。

如果 Requirement 后续被修复：

必须基于新的或更新后的 Evidence 重新形成 Evaluation Result。

---

## 7.4 AUTHORIZATION_REQUIRED

表示：

当前 Evaluation 已经具有足够 Evidence，

并且当前行为命中目标 Gate Definition 的：

Required Authorization。

但：

当前没有有效 Maker Authorization Evidence。

`AUTHORIZATION_REQUIRED`：

不表示 Gate Evaluation 失败。

它表示：

当前唯一未解决的必要条件属于 Maker Authorization。

Runtime 不得：

自动将该 Result 转换为 `REQUIREMENT_SATISFIED`。

---

## 7.5 EVIDENCE_INSUFFICIENT

表示：

当前 Gate Input 不足以形成可靠 Evaluation。

包括：

- 必要 Context 缺失；
- 必要 Workflow Information 缺失；
- 必要 Artifact Evidence 缺失；
- 必要 Validation Evidence 缺失；
- Context Evidence 相互冲突；
- Judgment-Based Requirement 缺少足够判断依据。

在该状态下：

不得推定 Requirement 已满足。

---

## 7.6 ACTION_BLOCKED

表示：

Gate Evaluation 已经具有足够 Evidence，

并确认当前 Requested Action 本身不能在当前 Gate Definition 下继续。

`ACTION_BLOCKED` 用于：

当前行为已经落入 Gate Definition 的 Blocked Action，

且不是单纯等待补充 Maker Authorization 或补充 Evaluation Evidence。

包括：

- 当前 Requested Action 与冻结的保护边界直接冲突；
- 当前请求要求绕过 Gate；
- 当前行为要求改变不允许由 Gate Contract 覆盖的上游 Source of Truth；
- 当前行为即使具备普通 Evidence，也不能通过当前 Invocation 合法继续。

如果需要改变受保护的 Domain Rule：

必须返回对应上游 Design Layer。

不得通过 Runtime 自行解除 `ACTION_BLOCKED`。

---

# 8. Evaluation Result Selection Rule

Evaluation Result 必须遵守以下互斥语义。

## Rule 1

如果必要 Evidence 不足：

结果必须为：

`EVIDENCE_INSUFFICIENT`

---

## Rule 2

如果 Evidence 已充分，

且当前行为命中 Required Authorization，

但缺少有效 Maker Authorization：

结果必须为：

`AUTHORIZATION_REQUIRED`

---

## Rule 3

如果 Evidence 已充分，

并确认当前 Requested Action 本身违反不可由当前 Invocation 满足的保护边界：

结果必须为：

`ACTION_BLOCKED`

---

## Rule 4

如果 Evidence 已充分，

当前 Requested Action 不属于不可继续行为，

但至少一个可满足的 Evaluation Requirement 当前未满足：

结果必须为：

`REQUIREMENT_UNSATISFIED`

---

## Rule 5

只有所有必要 Requirement 与 Authorization 均满足时：

结果必须为：

`REQUIREMENT_SATISFIED`

---

# 9. Maker Authorization Contract

## 9.1 Maker Authorization Principle

Maker 是：

需要 Maker Authorization 的 Gate 行为唯一授权来源。

以下内容均不等于 Maker Authorization：

- Agent Recommendation；
- Agent Judgment；
- Runtime Decision；
- Script Result；
- Validation Result；
- Gate Evaluation 本身；
- Workflow Result；
- 历史但未明确对应当前 Risk Object / Action 的 Maker 表述。

---

## 9.2 Authorization Evidence

Maker Authorization Evidence 必须能够表达：

- Authorization ID；
- Authorizer；
- Gate ID；
- Risk Object Reference；
- Authorized Action Reference；
- Authorization Scope；
- Authorization Statement Reference。

Authorizer：

必须为：

`MAKER`

---

## 9.3 Authorization Scope

Authorization Evidence：

只能覆盖其明确对应的：

- Gate；
- Risk Object；
- Action；
- Change Scope。

不得将一个 Maker Authorization：

自动扩展至其他 Gate、其他 Risk Object 或其他 Action。

---

## 9.4 Authorization Status

Gate Contract 使用以下 Authorization Status：

- `NOT_REQUIRED`；
- `REQUIRED_MISSING`；
- `PRESENT_VALID`；
- `PRESENT_INVALID`。

---

## 9.5 NOT_REQUIRED

表示：

当前 Requested Action：

未命中当前 Gate Definition 的 Required Authorization 条件。

---

## 9.6 REQUIRED_MISSING

表示：

当前 Requested Action 要求 Maker Authorization，

但没有提供对应有效 Authorization Evidence。

Evaluation Result 必须为：

`AUTHORIZATION_REQUIRED`

除非存在更高优先级的：

`EVIDENCE_INSUFFICIENT`

或：

`ACTION_BLOCKED`

条件。

---

## 9.7 PRESENT_VALID

表示：

当前 Authorization Evidence：

- 来自 Maker；
- 对应当前 Gate；
- 对应当前 Risk Object；
- 对应当前 Requested Action；
- 对应当前 Scope。

---

## 9.8 PRESENT_INVALID

表示：

提供了 Authorization Evidence，

但不能证明该 Authorization 对当前 Invocation 有效。

`PRESENT_INVALID`：

不得视为已授权。

---

# 10. Gate Output Contract

## 10.1 Gate Output Purpose

Gate Output 表达：

一次 Gate Invocation 的 Contract-level Evaluation Result。

Gate Output：

不执行任何项目修改。

---

## 10.2 Required Fields

每一个 Gate Output 必须能够表达：

- Invocation ID；
- Gate ID；
- Evaluation Result；
- Evaluation Reason；
- Unsatisfied Requirement；
- Required Authorization Status；
- Relevant Risk；
- Evidence Reference；
- Permitted Action Reference；
- Blocked Action Reference；
- Workflow Requirement Reference；
- Context Reference。

不存在的字段：

必须明确表示为空。

---

## 10.3 Evaluation Reason

Evaluation Reason：

必须说明当前 Evaluation Result 与 Gate Evaluation Requirement 的对应关系。

不得只输出：

“未通过”

或：

“存在风险”。

必须能够说明：

- 哪一个 Requirement 满足或未满足；
- 哪一个 Evidence 支撑该结论；
- 是否涉及 Maker Authorization；
- 为什么当前 Requested Action 可以或不能继续。

---

## 10.4 Unsatisfied Requirement

当 Evaluation Result 为：

- `REQUIREMENT_UNSATISFIED`；
- `AUTHORIZATION_REQUIRED`；
- `EVIDENCE_INSUFFICIENT`；
- `ACTION_BLOCKED`

时：

Gate Output 必须明确指出：

当前仍未解决的 Requirement。

如果不存在可补充 Requirement，

而是 Requested Action 本身被阻止：

Unsatisfied Requirement 应明确表示：

当前 Requested Action 与 Blocked Action / Protection Boundary 冲突。

---

## 10.5 Relevant Risk

Relevant Risk 必须引用：

目标 Gate Definition 中已经存在的 Risk Object。

不得通过 Gate Output：

创建新的长期 Risk Classification。

---

## 10.6 Permitted Action Reference

只有 Evaluation Result 为：

`REQUIREMENT_SATISFIED`

时：

Permitted Action Reference 才可以引用：

对应 Gate Definition 的 Allowed Action。

Permitted Action Reference：

不表示 Runtime 已经执行该 Action。

---

## 10.7 Blocked Action Reference

当 Evaluation Result 不是：

`REQUIREMENT_SATISFIED`

时：

Gate Output 必须能够引用：

当前 Gate Definition 中与当前 Requested Action 相关的 Blocked Action。

---

## 10.8 No Side Effect Rule

Gate Output 不得直接：

- 修改 Workflow；
- 修改 Context；
- 修改 Artifact；
- 修改 Runtime State；
- 修改 Gate Definition；
- 执行 Script；
- 执行 Requested Action。

---

# 11. Gate-specific Input Requirement Matrix

本章只将现有 Gate Domain Definition 投影为 Runtime 所需 Input Requirement。

本章不重新定义 Gate。

---

## 11.1 GATE-GIT

Gate Input 必须能够引用：

- Git Operation；
- Current Repository State；
- Target Branch / Remote Reference；
- Unhandled Change Evidence；
- History / Remote Impact Evidence。

如果 Requested Action 是：

- push；
- merge；
- Git History 修改；
- Branch 删除；

必须包含 Maker Authorization Evidence。

---

## 11.2 GATE-PHASE

Gate Input 必须能够引用：

- Current Phase；
- Target Phase；
- Workflow Allowed Next Phase；
- Required Artifact Requirement Status；
- State Change Requirement；
- Current unresolved Workflow Condition；
- Transition Request。

以下行为必须提供 Maker Authorization Evidence：

- Skip Core Phase；
- Rollback 到非正常 Workflow Path；
- 修改 Phase Model。

如果 Requested Next Phase 不属于 Workflow Contract 的 Allowed Next Phase：

Maker Authorization 不得自动改变 Workflow Contract。

---

## 11.3 GATE-AUTHORITY-DOCUMENT

Gate Input 必须能够引用：

- Target Authority Document；
- Current Source of Truth Responsibility；
- Proposed Change；
- Document Responsibility Boundary；
- Frozen Rule Impact；
- Long-Term Project Fact Impact。

以下行为必须包含 Maker Authorization Evidence：

- 修改 `PROJECT_PROFILE.md`；
- 修改 `PROJECT_DECISIONS.md`；
- 改变 Source of Truth；
- 改变已冻结 Framework Rule。

---

## 11.4 GATE-SCOPE

Gate Input 必须能够引用：

- Current Project Intent；
- Current Project Scope；
- Target User；
- Business Objective；
- Success Criteria；
- Proposed Scope Change；
- Deliverable Boundary；
- Scope Impact Judgment Evidence。

任何 Scope Expansion：

必须包含 Maker Authorization Evidence。

---

## 11.5 GATE-BUILDER

Gate Input 必须能够引用：

- Builder Task；
- Task Goal；
- Non-Goal；
- Input；
- Expected Output；
- Validation Requirement；
- Execution Boundary；
- Current Execution Readiness。

以下行为必须包含 Maker Authorization Evidence：

- Builder 修改核心架构；
- Builder 修改 Authority Document；
- Builder 执行不可逆操作。

---

## 11.6 GATE-UNCLOSED-TASK

Gate Input 必须能够引用：

- Current Task State；
- Unfinished Change；
- Incomplete Artifact；
- Required Artifact Status；
- Current Work Context；
- Proposed Task Switch / Abandon Action。

以下行为必须包含 Maker Authorization Evidence：

- 放弃当前 Task；
- 删除未完成 Artifact；
- 丢弃具有项目价值的未完成变更。

---

## 11.7 GATE-CONTEXT-INTEGRITY

Gate Input 必须能够引用：

- Required Context Presence；
- Current Project State；
- Project Identity；
- Decision History；
- Authority Context；
- Context Conflict；
- Context Trustworthiness；
- Maker Clarification Evidence。

以下行为必须包含 Maker Authorization Evidence：

- 在已知 Context 不完整时继续高影响修改；
- 重建具有长期影响的项目状态。

如果 Context Conflict 导致 Evaluation 无法形成可靠结论：

Evaluation Result 必须为：

`EVIDENCE_INSUFFICIENT`

而不是推测 Gate Requirement 已满足。

---

## 11.8 GATE-LOCAL-PROTOCOL

Gate Input 必须能够引用：

- Current Local Protocol；
- Output Rule；
- Agent Behavior Rule；
- Rule Priority；
- Rule Exception；
- Proposed Protocol Change；
- Rule Conflict Evidence；
- Long-Term Behavior Impact。

修改长期规则：

必须包含 Maker Authorization Evidence。

---

## 11.9 GATE-ARTIFACT-BOUNDARY

Gate Input 必须能够引用：

- Current Artifact Type；
- Expected Artifact Type；
- Workflow Required Artifact；
- Artifact Carrier；
- Deliverable Type；
- Proposed Artifact Change；
- Workflow Impact。

改变核心 Artifact Type：

必须包含 Maker Authorization Evidence。

---

## 11.10 GATE-CHALLENGE-RESPONSE

Gate Input 必须能够引用：

- Maker Challenge；
- Current Design；
- Current Recommendation；
- Current Decision Assumption；
- Maker Intent Interpretation；
- Re-analysis Evidence；
- Proposed Adjustment Scope。

如果重新判断导致：

- Project Direction；
- Architecture；
- Frozen Decision

发生变化：

必须包含 Maker Authorization Evidence。

Agent 自己的重新判断：

不能作为 Maker Authorization Evidence。

---

## 11.11 GATE-CORRECTION-PERSISTENCE

Gate Input 必须能够引用：

- Current Correction；
- Proposed Persistent Rule；
- Persistent Behavior Constraint；
- Current Project Protocol；
- Long-Term Applicability Judgment；
- Existing Rule Conflict；
- Future Behavior Impact。

任何新的长期规则或长期行为约束：

必须包含 Maker Authorization Evidence。

---

## 11.12 GATE-ARCHITECTURE-DECISION

Gate Input 必须能够引用：

- Proposed Architecture Decision；
- Existing Architecture Decision；
- Long-Term Architecture；
- System Boundary；
- Architectural Constraint；
- Multi-module Impact；
- Frozen Architecture Boundary Impact。

新增或修改 Architecture Decision：

必须包含 Maker Authorization Evidence。

---

## 11.13 GATE-FRAMEWORK-MODIFICATION

Gate Input 必须能够引用：

- Proposed Framework Modification；
- Current Framework Boundary；
- Framework Responsibility；
- Framework Long-Term Rule；
- Core Architecture Impact；
- Frozen System Boundary Impact；
- Downstream Design / Contract / Runtime Impact。

任何 Framework Modification：

必须包含 Maker Authorization Evidence。

---

## 11.14 GATE-PHASE-MODEL-MODIFICATION

Gate Input 必须能够引用：

- Proposed Phase Model Change；
- Current Core Phase Model；
- Phase Definition；
- Phase Goal；
- Phase Lifecycle；
- Core Phase Relationship；
- Workflow Source of Truth Impact；
- Downstream Contract / Runtime Impact。

任何 Core Phase Model Modification：

必须包含 Maker Authorization Evidence。

---

## 11.15 GATE-MATRIX-MODIFICATION

Gate Input 必须能够引用：

- Proposed Gate Model Change；
- Current Gate Type；
- Current Gate Definition；
- Gate Scope；
- Gate Protection Boundary；
- Maker Authorization Requirement；
- Control Strength Impact；
- Long-Term Gate Semantics Impact。

任何 Gate Model、Gate Type 或 Gate Definition 的实质性修改：

必须包含 Maker Authorization Evidence。

---

# 12. Workflow Boundary

## 12.1 Workflow Owns Transition Definition

Workflow 是以下内容的 Source of Truth：

- Phase；
- Phase Relationship；
- Required Artifact；
- State Change Requirement；
- Allowed Next Phase；
- Transition Contract。

Gate Contract：

不得修改上述内容。

---

## 12.2 Workflow Gate Trigger Requirement

Workflow 可以形成：

Gate Trigger Requirement。

该 Requirement：

可以作为 Gate Invocation 的 Trigger Reference。

Workflow 形成 Gate Trigger Requirement：

不表示 Gate Requirement 已经满足。

---

## 12.3 Workflow-side Gate Resolution

当前 Workflow Contract 使用：

- `UNRESOLVED`；
- `RESOLVED_FOR_TRANSITION`

表达 Workflow 对 Gate Result 的消费状态。

只有 Gate Evaluation Result 为：

`REQUIREMENT_SATISFIED`

时：

对应 Workflow Gate Requirement 才可以被视为：

`RESOLVED_FOR_TRANSITION`

其他 Result：

- `REQUIREMENT_UNSATISFIED`；
- `AUTHORIZATION_REQUIRED`；
- `EVIDENCE_INSUFFICIENT`；
- `ACTION_BLOCKED`

均不得形成：

`RESOLVED_FOR_TRANSITION`

---

## 12.4 Transition Boundary

Gate Contract：

不执行 Phase Transition。

即使 Gate Result 为：

`REQUIREMENT_SATISFIED`

Workflow Transition 仍必须继续满足：

`PROJECT_INCUBATOR_V1_WORKFLOW_CONTRACT.md`

定义的全部 Transition Eligibility Requirement。

---

# 13. Context Boundary

## 13.1 Context as Evidence

Gate 可以引用 Context：

作为 Evaluation Evidence。

Gate Contract：

不获得 Context Domain Authority。

---

## 13.2 Context Read Permission

Gate Runtime Component 读取 Context：

必须遵守：

`PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md`

只有在当前 Gate Evaluation Requirement 明确需要对应 Context 时：

才能读取目标 Context。

---

## 13.3 Context Mutation Prohibited

Gate Contract：

不得：

- 提出 Context Mutation；
- 执行 Context Mutation；
- 将 Gate Output 直接写入 Context；
- 使用 Gate Result 覆盖 Context Source of Truth。

如果 Gate Result 后续需要反映为项目状态：

必须由 Runtime 与 Context Access Contract 形成独立受控 Mutation。

---

## 13.4 Context Conflict

如果 Gate Evaluation 所依赖的信息：

与权威 Context 发生冲突，

且该冲突影响 Gate Evaluation：

Gate Contract 不得自行选择非权威信息。

当前 Evaluation Result 应为：

`EVIDENCE_INSUFFICIENT`

并保留：

Context Conflict Reference。

---

# 14. Script and Validation Boundary

## 14.1 Validation Role

Gate Evaluation 可以依赖：

确定性 Validation Evidence。

Validation Evidence 用于：

证明某项 Evaluation Requirement 是否具有确定性事实基础。

---

## 14.2 Script Boundary

Gate Contract 不定义：

- Script Identity；
- Script Input Schema；
- Script Output Schema；
- Script Error Handling；
- Script Invocation；
- Script Retry；
- Script Runtime。

这些属于：

`PROJECT_INCUBATOR_V1_SCRIPT_CONTRACT.md`

和：

`PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`

---

## 14.3 Validation Result Is Not Gate Result

Validation Result：

不得直接作为：

`REQUIREMENT_SATISFIED`

或其他 Gate Evaluation Result。

Gate Evaluation：

仍必须依据目标 Gate Definition 的完整 Evaluation Requirement。

尤其：

Judgment-Based Gate：

不得因为存在一个确定性 Script Result，

就自动转化为 Evidence-Based Gate。

---

# 15. Gate Result and Runtime Boundary

## 15.1 Runtime Consumption

Runtime 可以消费 Gate Output 中的：

- Evaluation Result；
- Required Authorization Status；
- Unsatisfied Requirement；
- Permitted Action Reference；
- Blocked Action Reference；
- Relevant Risk；
- Evidence Reference。

---

## 15.2 Runtime Must Not Infer

Runtime 不得自行推导：

- 新的 Gate Type；
- 新的 Trigger Condition；
- 新的 Required Authorization；
- 新的 Allowed Action；
- 新的 Blocked Action；
- 新的 Evaluation Result Status。

---

## 15.3 Runtime Execution

本 Contract 不定义 Runtime：

- 如何检测 Gate Trigger；
- 什么时候创建 Gate Instance；
- 如何调用 Gate Evaluation；
- 如何等待 Maker；
- 如何恢复执行；
- 如何写回 Gate State；
- 如何持久化 Gate Result。

上述机制由：

`PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`

定义。

---

# 16. Multi-Gate Boundary

## 16.1 Multiple Gate Requirements

同一个 Requested Action：

可以同时进入多个已经定义的 Gate Protection Boundary。

每一个 Gate：

必须产生独立 Gate Invocation 和独立 Gate Output。

---

## 16.2 No Cross-Gate Substitution

一个 Gate 的：

`REQUIREMENT_SATISFIED`

不得自动满足其他 Gate。

一个 Gate 的 Maker Authorization：

不得自动视为另一个 Gate 的 Authorization。

除非：

同一 Maker Authorization Evidence 明确同时引用两个独立 Gate Requirement。

---

## 16.3 Combined Action Eligibility

如果一个 Requested Action 同时存在多个 Gate Requirement：

只有所有相关 Gate Output 均为：

`REQUIREMENT_SATISFIED`

时：

Gate Contract 才不再阻止该 Action。

只要存在任一：

- `REQUIREMENT_UNSATISFIED`；
- `AUTHORIZATION_REQUIRED`；
- `EVIDENCE_INSUFFICIENT`；
- `ACTION_BLOCKED`

对应 Requested Action：

不得视为 Gate Requirements 已全部解决。

---

# 17. Gate Re-evaluation Contract

## 17.1 Re-evaluation Basis

当以下任一事实发生变化时：

旧 Gate Output 不得自动视为当前有效：

- Risk Object 发生实质变化；
- Trigger Action 发生变化；
- Evaluation Evidence 发生变化；
- Maker Authorization 发生变化；
- Context 发生影响原判断的变化。

这些情况对应 Gate Design 中已经定义的 Reopened 领域语义。

---

## 17.2 New Evaluation

Re-evaluation：

必须基于当前有效 Gate Input。

旧 Result：

可以作为历史 Reference。

不得直接作为新的当前 Result。

Gate Contract 不定义：

Runtime 如何创建新的 Gate Invocation。

---

# 18. Contract Validation Rules

任何 Gate Contract Consumer 必须满足以下规则。

## Rule 1

Gate ID：

必须对应已存在 Gate Definition。

---

## Rule 2

Gate Trigger：

必须对应目标 Gate 已定义的 Trigger Condition。

---

## Rule 3

Risk Object：

必须属于目标 Gate 已定义的 Risk Object Scope。

---

## Rule 4

Gate Input：

不得创造新的 Gate Evaluation Requirement。

---

## Rule 5

Evidence 不充分时：

不得返回 `REQUIREMENT_SATISFIED`。

---

## Rule 6

需要 Maker Authorization 但缺失时：

不得返回 `REQUIREMENT_SATISFIED`。

---

## Rule 7

Agent Judgment：

不得作为 Maker Authorization。

---

## Rule 8

Script / Validation Result：

不得直接作为 Gate Evaluation Result。

---

## Rule 9

Gate Output：

不得直接执行 Workflow Transition。

---

## Rule 10

Gate Output：

不得直接执行 Context Mutation。

---

## Rule 11

Gate Output：

不得直接修改 Artifact。

---

## Rule 12

Gate Output：

不得直接修改 Runtime State。

---

## Rule 13

Phase Gate：

不得修改 Workflow Allowed Next Phase。

---

## Rule 14

Scope Gate：

不得由 Runtime 自动授权 Scope Expansion。

---

## Rule 15

Authority Document Gate：

不得由 Contract 自行改变 Source of Truth。

---

## Rule 16

Gate Matrix Modification Gate：

不得由 Gate Contract 自行修改 Gate Domain Model。

---

## Rule 17

多个 Gate Requirement：

必须独立满足。

---

## Rule 18

只有：

`REQUIREMENT_SATISFIED`

可以表示当前 Gate Requirement 对应行为不再被本 Gate 阻止。

---

# 19. Gate Extension Contract Boundary

Gate Design 允许未来定义：

- Universal Gate；
- Project Type Specific Gate；
- Project Incubator Specific Gate。

新增 Gate Type：

必须先在 Gate Design 中形成完整 Gate Definition。

只有上游 Gate Design 已经正式定义：

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
- Blocked Action

后：

才能接入本 Gate Invocation Contract。

如果新 Gate 仅需要现有 Gate Input / Output 能力：

复用本 Contract。

如果新 Gate 需要改变 Gate Interaction Contract：

必须修改本 Contract。

Runtime 不得自行扩展 Contract。

---

# 20. Source of Truth Boundary

Project Incubator V1 Gate 相关 Source of Truth 固定如下：

Gate 是什么、Gate Type、Lifecycle、Trigger Condition、Risk Object、Evaluation Requirement、Required Authorization、Allowed Action、Blocked Action：

`PROJECT_INCUBATOR_V1_GATE_DESIGN.md`

Gate Invocation、Gate Input、Gate Output、Evaluation Result：

`PROJECT_INCUBATOR_V1_GATE_CONTRACT.md`

Workflow 哪些流程事件形成 Gate Trigger Requirement：

`PROJECT_INCUBATOR_V1_WORKFLOW_DESIGN.md`

Workflow Runtime Interface 中如何表达 Gate Requirement：

`PROJECT_INCUBATOR_V1_WORKFLOW_CONTRACT.md`

Context Read / Mutation Permission：

`PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md`

Runtime 如何实际执行 Gate Invocation：

`PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`

层级关系：

```text
Gate Design
    ↓
Gate Contract
    ↓
Runtime Specification
```

Contract 不重新定义 Design。

Runtime 不重新定义 Contract。

---

# 21. V1 Contract Summary

Project Incubator V1 Gate Contract 定义：

- Gate Invocation Request；
- Gate Input；
- Evaluation Evidence；
- Evaluation Result；
- Maker Authorization Contract；
- Gate Output；
- Gate-specific Input Requirement；
- Workflow Boundary；
- Context Boundary；
- Script / Validation Boundary；
- Multi-Gate Boundary；
- Re-evaluation Boundary。

核心 Contract 原则：

1. Gate Domain Rule 全部来自已经冻结的 Gate Design。

2. Gate Contract 不新增 Gate Type。

3. Gate Contract 不新增 Trigger Condition。

4. Gate Contract 不新增 Required Authorization。

5. Runtime 请求 Gate Evaluation 时必须明确：

   - Gate；
   - Trigger；
   - Risk Object；
   - Requested Action；
   - Evaluation Requirement；
   - Evidence；
   - Authorization Evidence。

6. Gate Evaluation Result 只允许：

```text
REQUIREMENT_SATISFIED
REQUIREMENT_UNSATISFIED
AUTHORIZATION_REQUIRED
EVIDENCE_INSUFFICIENT
ACTION_BLOCKED
```

7. `REQUIREMENT_SATISFIED` 表示当前 Gate Requirement 已满足。

8. `REQUIREMENT_UNSATISFIED` 表示当前存在明确未满足 Requirement。

9. `AUTHORIZATION_REQUIRED` 表示当前缺少必须存在的 Maker Authorization。

10. `EVIDENCE_INSUFFICIENT` 表示当前 Evidence 不足以形成可靠判断。

11. `ACTION_BLOCKED` 表示当前 Requested Action 本身必须停止。

12. Maker 是 Maker Authorization 的唯一来源。

13. Agent Judgment、Runtime Decision、Script Result 或 Validation Result 均不能替代 Maker Authorization。

14. Gate 可以使用 Context Evidence，但必须遵守 Context Access Contract。

15. Gate 可以使用 Workflow Evidence，但不得修改 Allowed Next Phase。

16. Gate 可以使用 Validation Evidence，但 Validation Result 不等于 Gate Evaluation Result。

17. Gate Output 不直接修改 Workflow、Context、Artifact 或 Runtime State。

18. Workflow-side Gate Requirement 只有在 Gate Result 为 `REQUIREMENT_SATISFIED` 时才能视为 `RESOLVED_FOR_TRANSITION`。

19. 一个 Requested Action 同时触发多个 Gate 时，每个 Gate 必须独立满足。

20. Gate 的具体 Invocation、执行、等待、恢复和状态持久化机制由 Runtime Specification 定义。