# Project Incubator V1 Script Contract

# 1. Contract Purpose

本文档定义 Project Incubator V1 中 Runtime 与 Script 之间的交互契约。

本文档属于：

Contract Layer。

本文档负责定义：

- Script Input；
- Script Output；
- Error Handling；
- Validation Result。

本文档将 Architecture Layer 中已经确定的 Script 确定性能力边界，转换为 Runtime 可以消费的 Script Contract。

本文档不定义：

- Script 源代码；
- Script 文件实现位置；
- Shell / Python 实现；
- Runtime Script Runner；
- Script Invocation 顺序；
- Retry Flow；
- Runtime Execution Flow；
- Workflow Domain Rule；
- Gate Domain Rule；
- Context Domain Rule；
- 项目具体验证逻辑。

Script 的具体调用和执行机制由：

`SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`

定义。

Script 的具体文件和实现任务由：

`SPECS/IMPLEMENTATION/PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md`

定义。

---

# 2. Script Contract Model

## 2.1 Script Role

Script 是 Project Incubator V1 中由 Runtime 使用的确定性能力。

Script 负责：

- 接收明确输入；
- 执行确定性检查；
- 执行确定性工具操作；
- 返回结构化执行结果；
- 在 Validation 场景中返回 Validation Result；
- 提供可供 Runtime 或 Gate 使用的 Evidence。

Script 不负责：

- Maker Decision；
- Project Direction；
- Agent Reasoning；
- Workflow Transition；
- Gate Authorization；
- Context Domain Authority；
- Runtime State Control。

---

## 2.2 Runtime and Script Relationship

Runtime：

负责协调和调用 Script。

Script：

接收 Runtime 提供的 Contract Input，

并返回：

Contract Output。

关系为：

```text
Runtime
   ↓
Script Input
   ↓
Script Deterministic Capability
   ↓
Script Output
   ↓
Runtime
```

本文档只定义：

Runtime 与 Script 交换什么信息。

本文档不定义：

Runtime 在什么时间调用 Script，

也不定义：

Runtime 如何执行该调用。

---

## 2.3 Deterministic Capability Boundary

Script 只处理能够形成确定性结果的任务。

包括：

- 文件存在性检查；
- 文件状态检查；
- 数据格式检查；
- 数据结构检查；
- 明确规则验证；
- 已定义条件比较；
- 自动化文件处理；
- 自动化数据处理；
- 其他具有明确 Input、Operation 和 Result 的工具操作。

Script 不负责：

需要以下内容才能完成的最终判断：

- Project Intent 解释；
- Project Scope 价值判断；
- Architecture Decision；
- Maker Intent 判断；
- 商业决策；
- 创造性方案选择；
- 其他 Judgment-Based 决策。

---

# 3. Script Authority Boundary

## 3.1 No Maker Decision Authority

Script 不具有：

Maker Decision Authority。

Script Result：

不能作为 Maker Authorization。

---

## 3.2 No Workflow Transition Authority

Script 不具有：

Workflow Transition Authority。

Script 不允许：

- 改变 Current Phase；
- 选择 Requested Next Phase；
- 将 Workflow Gate Requirement 标记为 Resolved；
- 将 Transition Result 直接改为 `READY_FOR_TRANSITION`；
- 执行 Phase Transition。

---

## 3.3 No Gate Authorization Authority

Script 不具有：

Gate Authorization Authority。

Script 可以提供：

Validation Evidence。

Script 不可以：

- 输出 Maker Authorization；
- 输出 Gate Approval；
- 输出 Gate Evaluation Result；
- 将 Validation Result 解释为 Gate 已满足。

---

## 3.4 No Context Authority

Script 不具有：

Context Domain Authority。

Script 不允许：

- Direct Read Core Context；
- Request Context Mutation；
- Authorize Context Mutation；
- Execute Context Mutation；
- 改变 Context Source of Truth；
- 改变 Context Authority。

Script 所需的 Context-derived Data：

必须由 Runtime 根据 Context Access Contract 提供。

---

# 4. Script Identity Contract

## 4.1 Script Identity

每一个可以被 Runtime 调用的 Script Capability：

必须具有稳定 Script Identity。

Script Identity 用于：

- 标识被调用能力；
- 关联 Script Input；
- 关联 Script Output；
- 关联 Validation Result；
- 关联 Diagnostic Information。

---

## 4.2 Identity Semantics

Script Identity：

只标识逻辑 Script Capability。

本文档不定义：

- Script 文件名；
- Script 文件路径；
- Script 编程语言；
- Script Entry Point；
- Command Line Interface。

这些属于后续 Implementation。

---

# 5. Script Invocation Purpose

## 5.1 Invocation Purpose Definition

每次 Script Input：

必须明确 Invocation Purpose。

Invocation Purpose 表示：

Runtime 请求 Script 完成哪一种已经明确的确定性任务。

---

## 5.2 Invocation Purpose Type

V1 Script Contract 定义以下 Invocation Purpose Type：

- `VALIDATION`；
- `DETERMINISTIC_OPERATION`。

---

## 5.3 VALIDATION

表示：

Script 用于检查一个已经明确的 Validation Requirement 是否满足。

VALIDATION：

必须产生 Validation Result。

---

## 5.4 DETERMINISTIC_OPERATION

表示：

Script 执行一个具有明确 Input 和预期确定性结果的工具操作。

DETERMINISTIC_OPERATION：

不强制产生 Validation Result。

如果该 Operation 同时包含明确 Validation Requirement：

可以同时返回 Validation Result。

如果该 Operation 不包含 Validation Requirement：

- Validation Result 必须显式为空；
- 不得生成 REQUIREMENT_SATISFIED；
- 不得生成 REQUIREMENT_UNSATISFIED；
- 不得使用 VALIDATION_NOT_COMPLETED 表示“本次 Invocation 不需要 Validation”。

“没有 Validation Requirement”与“Validation 未完成”属于不同语义。

---

# 6. Script Input Contract

## 6.1 Script Input Purpose

Script Input 表达：

Runtime 向 Script 提供的一次确定性执行请求。

Script Input：

只定义交互信息。

不定义：

Runtime 如何准备、传输或调用这些信息。

---

## 6.2 Required Fields

每一个 Script Input 必须能够表达：

- Invocation ID；
- Script Identity；
- Invocation Purpose；
- Input Data；
- Context Reference；
- Artifact Reference；
- Validation Requirement；
- Execution Parameter。

对于当前 Invocation 不需要的 Optional Field：

必须明确表示为空。

不得通过省略字段表达隐含 Contract 语义。

---

# 7. Invocation ID

Invocation ID：

唯一标识一次 Script Invocation。

每一个 Script Output：

必须引用对应 Invocation ID。

Validation Result：

如果存在，

也必须能够追溯到对应 Invocation ID。

同一次 Invocation 的：

Input、Output、Evidence、Diagnostic Information

必须使用同一个 Invocation ID 建立关联。

---

# 8. Input Data Contract

## 8.1 Input Data Definition

Input Data 表示：

Script 完成当前确定性操作所需要的实际数据。

Input Data 必须：

- 范围明确；
- 与 Invocation Purpose 直接相关；
- 足以执行目标确定性操作；
- 不要求 Script 自行寻找未声明的数据源。

---

## 8.2 Input Data Boundary

Script 不得：

- 自行扩展 Input Scope；
- 自行选择额外 Context；
- 自行推断缺失的关键业务事实；
- 使用历史对话填补缺失 Input；
- 将未提供的信息假定为已确认事实。

如果 Input Data 不满足 Contract Requirement：

不得继续将结果表示为正常 Script Execution。

---

# 9. Context Reference Contract

## 9.1 Context Reference Purpose

Context Reference 用于说明：

当前 Script Input 中的部分数据来源于哪个 Context。

Context Reference：

只用于：

- Traceability；
- Source Reference；
- Evidence Attribution。

---

## 9.2 No Direct Context Access

Context Reference：

不授予 Script Context Read Permission。

Script 不得因为获得：

`PROJECT_PROFILE`

`PROJECT_STATE`

`PROJECT_PLAN`

`PROJECT_DECISIONS`

或 Optional Context Reference

而直接读取对应 Context。

Context Access Contract 已固定：

Script 不拥有 Direct Context Access Authority。

---

## 9.3 Context-derived Input

如果 Script 需要 Context 信息：

Runtime 必须按照：

`PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md`

获得合法 Context 数据，

再将明确、有限的 Context-derived Data 放入：

Input Data。

Script 只能消费：

Runtime 已经提供的 Input Data。

---

## 9.4 Context Source of Truth Boundary

Script 不得：

- 使用自己的输出覆盖 Context Source of Truth；
- 把 Validation Result 直接写入 Context；
- 把检测到的事实直接持久化为 Project State。

如果 Script Result 后续需要影响 Context：

必须由 Runtime 根据 Context Access Contract 形成独立受控 Mutation。

---

# 10. Artifact Reference Contract

## 10.1 Artifact Reference Purpose

Artifact Reference 用于标识：

当前 Script Operation 或 Validation 所针对的 Workflow Artifact。

可以引用：

- Required Artifact；
- Phase Output Artifact；
- Project Artifact；
- Validation Target Artifact；
- 其他已经由 Workflow 定义的 Artifact。

---

## 10.2 Artifact Boundary

Artifact Reference：

不重新定义：

- Artifact Type；
- Artifact Lifecycle；
- Artifact Flow；
- Artifact Domain Model。

Script Contract 不得通过 Artifact Reference：

创建新的 Workflow Artifact Requirement。

---

# 11. Validation Requirement Contract

## 11.1 Definition

Validation Requirement 表示：

Script 在 VALIDATION Invocation 中必须检查的明确条件。

Validation Requirement 必须来自：

已经存在的上游 Requirement。

包括：

- Workflow Requirement；
- Gate Evaluation Requirement 中可确定性验证的部分；
- Runtime 已经合法获得的确定性检查 Requirement；
- 已冻结的 Validation Criteria。

---

## 11.2 Required Properties

Validation Requirement 必须能够表达：

- Requirement ID；
- Requirement Description；
- Validation Target；
- Expected Condition；
- Evidence Requirement。

---

## 11.3 Requirement ID

Requirement ID：

用于唯一识别当前被验证条件。

Script 不得修改 Requirement ID 所代表的 Requirement 语义。

---

## 11.4 Requirement Description

Requirement Description：

必须描述要验证什么。

不得要求 Script：

自行推导最终业务判断。

---

## 11.5 Validation Target

Validation Target：

必须明确本次验证对象。

可以是：

- Artifact；
- File；
- Data；
- Structure；
- State Snapshot；
- Operation Result；
- 其他已经明确的确定性目标。

---

## 11.6 Expected Condition

Expected Condition：

必须可以通过确定性检查形成结果。

如果 Expected Condition 本身需要：

- Maker 判断；
- Agent 创造性判断；
- Project Scope 判断；
- Architecture Judgment；

则不能由 Script 单独形成最终 Validation Result。

---

## 11.7 Evidence Requirement

Evidence Requirement：

定义 Validation Result 需要返回哪些事实依据，

以便 Runtime 或 Gate 判断结果是否可使用。

---

# 12. Execution Parameter Contract

## 12.1 Definition

Execution Parameter 表示：

执行当前 Script Capability 所需的非领域执行参数。

Execution Parameter：

只能控制已经确定的 Script Operation。

不得改变：

- Workflow Rule；
- Gate Rule；
- Context Authority；
- Validation Requirement；
- Maker Authorization Requirement。

---

## 12.2 Parameter Boundary

本文档不定义：

具体 Script 使用哪些：

- Command Line Flag；
- Environment Variable；
- File System Path Convention；
- Programming Language Parameter；
- Retry Parameter。

具体 Execution Parameter：

由对应 Script Implementation Task 在遵守本 Contract 前提下确定。

---

# 13. Script Output Contract

## 13.1 Script Output Purpose

Script Output 表示：

一次 Script Invocation 的结构化执行结果。

无论执行成功或失败：

Runtime 都必须能够根据 Script Output 区分：

- Script 是否正常执行；
- 是否产生 Validation Result；
- 是否产生 Evidence；
- 是否出现 Contract / Execution Error。

---

## 13.2 Required Fields

Script Output 必须能够表达：

- Invocation ID；
- Script Identity；
- Execution Status；
- Validation Result；
- Evidence；
- Diagnostic Information；
- Error Information。

当前不存在的字段：

必须明确表示为空。

---

# 14. Execution Status Model

## 14.1 Result Set

Script Execution Status 只允许：

- `COMPLETED`；
- `INVALID_INPUT`；
- `UNSUPPORTED_INVOCATION`；
- `EXECUTION_ERROR`。

不得使用：

- PASS；
- FAIL；
- SUCCESS；
- VALID；
- INVALID

作为 Execution Status。

这些名称容易与 Validation Result 混淆。

---

## 14.2 COMPLETED

表示：

Script 已按照当前 Script Contract：

正常完成本次 Invocation。

`COMPLETED`：

只表示 Script Execution 成功完成。

不表示：

Validation Requirement 已满足。

因此以下组合合法：

```text
Execution Status = COMPLETED
Validation Result = REQUIREMENT_SATISFIED
```

以及：

```text
Execution Status = COMPLETED
Validation Result = REQUIREMENT_UNSATISFIED
```

---

## 14.3 INVALID_INPUT

表示：

当前 Script Identity 与 Invocation Purpose 可以被识别，

但 Script Input 不满足当前 Script Contract 的必要输入条件。

包括：

- Required Input Data 缺失；
- Input Data 类型或结构无法用于目标操作；
- Validation Requirement 缺少必要信息；
- 必需 Target Reference 缺失；
- Input 与 Invocation Purpose 明确矛盾。

在此状态下：

目标 Script Operation 不得被表示为正常完成。

---

## 14.4 UNSUPPORTED_INVOCATION

表示：

当前请求不属于目标 Script Identity 已支持的 Invocation Capability。

包括：

- Script Identity 与 Invocation Purpose 不匹配；
- 请求 Script 执行不属于其确定性职责的操作；
- 请求 Script 执行 Judgment-Based 最终判断；
- 请求 Script 获得其 Contract 明确禁止的 Authority。

---

## 14.5 EXECUTION_ERROR

表示：

Script Input 合法，

目标 Invocation 也受支持，

但 Script 本身没有正常完成执行。

该状态表示：

Execution Failure。

不表示：

Validation Requirement 未满足。

---

# 15. Validation Result Model

## 15.1 Validation Result Scope

Validation Result：

只存在于需要执行确定性 Validation 的 Invocation。

Validation Result 表示：

Script 对一个明确 Validation Requirement 的确定性检查结果。

---

## 15.2 Result Set

Validation Result 只允许：

- `REQUIREMENT_SATISFIED`；
- `REQUIREMENT_UNSATISFIED`；
- `VALIDATION_NOT_COMPLETED`。

---

## 15.3 REQUIREMENT_SATISFIED

表示：

Script 已正常完成 Validation，

并且现有 Evidence 明确证明：

Expected Condition 已满足。

该结果必须满足：

```text
Execution Status = COMPLETED
```

---

## 15.4 REQUIREMENT_UNSATISFIED

表示：

Script 已正常完成 Validation，

但现有 Evidence 明确证明：

Expected Condition 未满足。

该结果就是：

Validation Failure。

Validation Failure：

不是 Script Execution Error。

合法组合为：

```text
Execution Status = COMPLETED
Validation Result = REQUIREMENT_UNSATISFIED
```

---

## 15.5 VALIDATION_NOT_COMPLETED

表示：

当前没有形成有效 Validation Conclusion。

包括：

- Execution Status = `INVALID_INPUT`；
- Execution Status = `UNSUPPORTED_INVOCATION`；
- Execution Status = `EXECUTION_ERROR`；
- 完成 Validation 所需事实无法被当前 Script 确定性确认。

`VALIDATION_NOT_COMPLETED`：

不等于 Requirement Unsatisfied。

它表示：

没有形成可用的 Satisfied / Unsatisfied 判断。

---

# 16. Execution Status and Validation Result Matrix

| Execution Status | Validation Result | Contract Meaning |
| --- | --- | --- |
| COMPLETED | REQUIREMENT_SATISFIED | Script 正常完成，Validation Requirement 满足 |
| COMPLETED | REQUIREMENT_UNSATISFIED | Script 正常完成，Validation Requirement 不满足 |
| COMPLETED | VALIDATION_NOT_COMPLETED | Script 完成操作，但无法形成有效 Validation Conclusion |
| INVALID_INPUT | VALIDATION_NOT_COMPLETED | 输入无效，Validation 未完成 |
| UNSUPPORTED_INVOCATION | VALIDATION_NOT_COMPLETED | 当前 Invocation 不受支持，Validation 未完成 |
| EXECUTION_ERROR | VALIDATION_NOT_COMPLETED | Script 执行异常，Validation 未完成 |

以下组合非法：

```text
INVALID_INPUT + REQUIREMENT_SATISFIED
INVALID_INPUT + REQUIREMENT_UNSATISFIED

UNSUPPORTED_INVOCATION + REQUIREMENT_SATISFIED
UNSUPPORTED_INVOCATION + REQUIREMENT_UNSATISFIED

EXECUTION_ERROR + REQUIREMENT_SATISFIED
EXECUTION_ERROR + REQUIREMENT_UNSATISFIED
```

---

# 17. Validation Result Evidence

## 17.1 Evidence Requirement

以下 Validation Result：

- `REQUIREMENT_SATISFIED`；
- `REQUIREMENT_UNSATISFIED`

必须携带：

足以支持该结论的 Evidence。

---

## 17.2 Evidence Model

Validation Evidence 必须能够表达：

- Requirement ID；
- Validation Target；
- Observed Fact；
- Expected Condition；
- Comparison Result；
- Evidence Reference。

---

## 17.3 Observed Fact

Observed Fact：

必须表达 Script 实际确认到的确定性事实。

不得包含：

Script 自行生成的价值判断。

---

## 17.4 Comparison Result

Comparison Result：

说明：

Observed Fact

与：

Expected Condition

之间的确定性关系。

---

## 17.5 Evidence Boundary

Evidence：

可以被 Runtime 或 Gate 消费。

Evidence：

不直接产生：

- Workflow Transition；
- Context Mutation；
- Gate Authorization；
- Maker Decision。

---

# 18. Diagnostic Information

## 18.1 Purpose

Diagnostic Information 用于帮助 Runtime 或后续实现理解：

Script 执行过程形成的非 Authority 诊断信息。

可以表达：

- Detected Condition；
- Execution Observation；
- Validation Detail；
- Error Detail；
- Unsupported Capability Detail。

---

## 18.2 Boundary

Diagnostic Information：

不是项目 Source of Truth。

不得通过 Diagnostic Information：

覆盖：

- Context；
- Workflow；
- Gate；
- Maker Decision。

---

# 19. Error Handling Contract

## 19.1 Error Categories

Script Contract 必须严格区分：

- Invalid Input；
- Unsupported Invocation；
- Script Execution Error；
- Validation Failure。

---

## 19.2 Invalid Input

对应：

```text
Execution Status = INVALID_INPUT
```

含义：

Script 无法基于当前输入开始或可靠完成目标操作。

Invalid Input 属于：

Contract Input Failure。

不是：

Validation Failure。

---

## 19.3 Unsupported Invocation

对应：

```text
Execution Status = UNSUPPORTED_INVOCATION
```

含义：

Runtime 请求了当前 Script Capability 不支持的操作。

Unsupported Invocation 属于：

Capability Boundary Failure。

不是：

Validation Failure。

---

## 19.4 Script Execution Error

对应：

```text
Execution Status = EXECUTION_ERROR
```

含义：

Script 已接受有效 Input，

但 Script 自身没有正常完成目标 Operation。

Script Execution Error 属于：

Execution Failure。

不是：

Validation Failure。

---

## 19.5 Validation Failure

对应：

```text
Execution Status = COMPLETED
Validation Result = REQUIREMENT_UNSATISFIED
```

含义：

Script 正常完成 Validation，

并可靠判断：

被检查对象不满足 Validation Requirement。

Validation Failure：

不是 Script Error。

Runtime 不得把 Validation Failure：

错误归类为 Script Execution Error。

---

# 20. Error Information Contract

## 20.1 Required Fields

当 Execution Status 为：

- `INVALID_INPUT`；
- `UNSUPPORTED_INVOCATION`；
- `EXECUTION_ERROR`

时：

Error Information 必须能够表达：

- Error Type；
- Error Reason；
- Related Input Reference；
- Diagnostic Information。

---

## 20.2 Error Type

Error Type 必须与 Execution Status 保持一致：

| Execution Status | Error Type |
| --- | --- |
| INVALID_INPUT | INVALID_INPUT |
| UNSUPPORTED_INVOCATION | UNSUPPORTED_INVOCATION |
| EXECUTION_ERROR | SCRIPT_EXECUTION_ERROR |

Validation Failure：

不进入 Error Type。

---

# 21. Gate Integration Boundary

## 21.1 Script as Validation Evidence Provider

Gate Contract 可以使用：

Script Validation Result

作为：

Validation Evidence。

---

## 21.2 Validation Result Is Not Gate Evaluation Result

Script Validation Result：

```text
REQUIREMENT_SATISFIED
REQUIREMENT_UNSATISFIED
VALIDATION_NOT_COMPLETED
```

与 Gate Evaluation Result：

```text
REQUIREMENT_SATISFIED
REQUIREMENT_UNSATISFIED
AUTHORIZATION_REQUIRED
EVIDENCE_INSUFFICIENT
ACTION_BLOCKED
```

属于两个不同 Contract。

即使存在相同名称：

`REQUIREMENT_SATISFIED`

或：

`REQUIREMENT_UNSATISFIED`

两者语义层级不同。

Script Validation Result：

只回答：

确定性 Validation Requirement 是否满足。

Gate Evaluation Result：

回答：

完整 Gate Requirement 是否满足。

不得直接互相替换。

---

## 21.3 Evidence-Based Gate

Evidence-Based Gate：

可以依赖 Script Validation Evidence。

但 Gate Design 已明确：

Evidence-Based

并不意味着：

必须由 Script 执行。

Runtime 如何获得 Gate Evidence：

属于 Runtime Specification。

---

## 21.4 Judgment-Based Gate

Judgment-Based Gate：

不得被 Script Contract 转化为确定性 Gate。

Script 可以提供其中可确定性观察的事实。

Script 不得对以下问题形成最终 Gate Conclusion：

- Project Scope 是否合理；
- 是否属于 Architecture Decision；
- 是否应该形成长期规则；
- 是否改变项目方向；
- 其他依赖项目语义或 Maker Intent 的 Judgment。

---

## 21.5 Mixed Gate

Mixed Gate 可以同时依赖：

- Script Validation Evidence；
- Judgment Evidence。

Script 只负责：

其中可确定性验证部分。

Script Result：

不得替代 Judgment Evidence。

---

## 21.6 Gate Result Ownership

Gate Evaluation Result：

只能由：

`PROJECT_INCUBATOR_V1_GATE_CONTRACT.md`

定义的 Gate Evaluation Contract 形成。

Script 不允许返回：

- `AUTHORIZATION_REQUIRED`；
- `ACTION_BLOCKED`

作为 Script Validation Result。

---

# 22. Workflow Integration Boundary

## 22.1 Workflow Requirement as Validation Source

Workflow 已定义的：

- Required Artifact Requirement；
- Phase Requirement；
- Transition Requirement；
- Validation Requirement

可以成为 Script Validation Requirement 的来源。

---

## 22.2 Script Does Not Own Workflow Result

Script 不得：

- 生成新的 Allowed Next Phase；
- 改变 Required Artifact；
- 形成 Phase Transition；
- 修改 State Change Requirement；
- 将 Workflow Gate Requirement 标记为 Resolved。

---

## 22.3 Validation and Transition

即使 Script 返回：

```text
Validation Result = REQUIREMENT_SATISFIED
```

也不表示：

Workflow Transition 已经具备全部条件。

Workflow Transition Eligibility：

仍必须由：

`PROJECT_INCUBATOR_V1_WORKFLOW_CONTRACT.md`

判断。

---

# 23. Context Integration Boundary

## 23.1 No Direct Read

Script：

不拥有 Direct Context Read Permission。

---

## 23.2 No Mutation

Script：

不拥有：

- REQUEST_MUTATION；
- AUTHORIZE_MUTATION；
- EXECUTE_MUTATION。

---

## 23.3 Context-derived Data

Runtime 可以根据：

`PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md`

将合法获得的有限 Context-derived Data：

作为 Script Input Data 提供。

该行为：

不赋予 Script Context Read Authority。

---

## 23.4 Script Result and Context

Script Output：

不能直接成为 Context Mutation。

如果 Runtime 需要基于 Script Result 更新 Context：

必须：

1. 将 Script Result 作为 Validated Execution Fact 或其他合法 Change Basis；
2. 形成独立 Context Mutation Request；
3. 遵守 Context Access Contract；
4. 满足必要 Gate Requirement。

本文档不定义：

Runtime 如何执行上述流程。

---

# 24. Artifact Integration Boundary

Script 可以：

针对 Runtime 提供的 Artifact Reference：

执行确定性检查或工具操作。

Script 不得：

- 重新定义 Artifact Type；
- 重新定义 Artifact Flow；
- 自行改变 Workflow Required Artifact；
- 将自己的 Output 自动登记为新的 Workflow Artifact；
- 因修改 Artifact 而自动改变 Project State。

具体 Artifact Operation：

由 Runtime Specification 与后续 Implementation Plan 定义。

---

# 25. Maker Boundary

Script 不与 Maker 建立独立 Authorization Contract。

Script 不得：

- 请求 Maker Authorization；
- 保存 Maker Authorization；
- 解释 Maker Authorization Scope；
- 代替 Gate 验证 Maker Authorization。

Maker Authorization：

由 Gate Contract 和 Context Access Contract 中对应规则处理。

---

# 26. Runtime Boundary

## 26.1 Contract Responsibility

本文档只定义：

Runtime 与 Script 交换：

- Script Input；
- Script Output；
- Execution Status；
- Validation Result；
- Evidence；
- Error Information。

---

## 26.2 Runtime Specification Responsibility

以下内容只属于：

`PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`

- Runtime 什么时候调用 Script；
- Script Invocation 顺序；
- Script Runner；
- Script Discovery；
- Script Loading；
- Script Execution；
- Retry；
- Timeout；
- Runtime Error Recovery；
- Script Result Routing；
- Gate Invocation 与 Script Invocation 的执行顺序；
- Workflow 与 Script 的执行协调；
- Runtime Lifecycle。

---

## 26.3 No Runtime Flow in Contract

Script Contract：

不得描述类似以下执行流程：

```text
Runtime Load
→ Detect Requirement
→ Select Script
→ Execute Script
→ Retry
→ Invoke Gate
→ Persist Result
```

上述内容属于 Runtime Layer。

---

# 27. Unsupported Script Responsibilities

以下 Request：

必须被视为：

`UNSUPPORTED_INVOCATION`

如果 Runtime 请求 Script：

- 决定 Project Direction；
- 替 Maker 做 Decision；
- 确认 Maker Authorization；
- 修改 Context；
- 选择 Workflow Transition；
- 批准 Gate；
- 修改 Gate Definition；
- 判断 Project Scope 是否应该扩大；
- 判断 Architecture Decision 是否应该被接受；
- 判断一次纠偏是否应该形成长期规则；
- 直接修改 Runtime State。

---

# 28. Script Output Consumption Rule

## 28.1 Runtime Consumption

Runtime 可以消费：

- Execution Status；
- Validation Result；
- Evidence；
- Diagnostic Information；
- Error Information。

---

## 28.2 Gate Consumption

Gate 可以消费：

- Validation Result；
- Evidence。

Gate 不得把 Script Output：

直接视为 Maker Authorization。

---

## 28.3 Workflow Consumption

Workflow-related Runtime 可以消费：

Validation Result

用于判断某个确定性 Requirement 的当前状态。

但 Script Output：

不得直接形成 Workflow Transition Result。

---

## 28.4 Context Consumption

Script Result：

可以作为后续 Runtime 判断的事实 Evidence。

但：

Script Result 不直接获得 Context Write Authority。

---

# 29. Contract Validation Rules

任何 Script Contract Consumer 必须满足以下规则。

## Rule 1

每次 Script Invocation：

必须具有 Script Identity。

---

## Rule 2

每次 Script Invocation：

必须具有明确 Invocation Purpose。

---

## Rule 3

Script Input：

必须足以执行目标确定性 Operation。

---

## Rule 4

Script 不得自行扩展 Input Scope。

---

## Rule 5

Context Reference：

不授予 Direct Context Read Permission。

---

## Rule 6

Script 不拥有 Context Mutation Authority。

---

## Rule 7

Script 不拥有 Workflow Transition Authority。

---

## Rule 8

Script 不拥有 Gate Authorization Authority。

---

## Rule 9

Script 不拥有 Maker Decision Authority。

---

## Rule 10

Execution Status：

必须与 Validation Result 分离。

---

## Rule 11

Validation Failure：

必须表达为：

```text
Execution Status = COMPLETED
Validation Result = REQUIREMENT_UNSATISFIED
```

---

## Rule 12

Script Execution Error：

必须表达为：

```text
Execution Status = EXECUTION_ERROR
Validation Result = VALIDATION_NOT_COMPLETED
```

---

## Rule 13

Invalid Input：

不得被表示为 Validation Requirement Unsatisfied。

---

## Rule 14

Unsupported Invocation：

不得被表示为 Validation Failure。

---

## Rule 15

Validation Result：

必须携带 Evidence 或无法完成 Validation 的明确 Reason。

---

## Rule 16

Validation Result：

不得直接作为 Gate Evaluation Result。

---

## Rule 17

Judgment-Based Gate：

不得由 Script 自动转化为确定性 Gate。

---

## Rule 18

Mixed Gate：

Script 只承担其确定性验证部分。

---

## Rule 19

Script Result：

不得直接执行 Context Mutation。

---

## Rule 20

Script Result：

不得直接执行 Workflow Transition。

---

## Rule 21

Script Result：

不得直接修改 Runtime State。

---

## Rule 22

Runtime 不得通过 Script Input：

赋予 Script 上游 Contract 已禁止的权限。

---

# 30. Source of Truth Boundary

Project Incubator V1 Script 相关 Source of Truth 固定如下。

系统中 Script 的总体定位、Script 与 Runtime 的架构关系：

`PROJECT_INCUBATOR_V1_DESIGN.md`

Script Input、Script Output、Error Handling、Validation Result：

`PROJECT_INCUBATOR_V1_SCRIPT_CONTRACT.md`

Context Access Permission：

`PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md`

Workflow Schema、Phase Interface、Transition Contract：

`PROJECT_INCUBATOR_V1_WORKFLOW_CONTRACT.md`

Gate Input、Gate Output、Evaluation Result：

`PROJECT_INCUBATOR_V1_GATE_CONTRACT.md`

Runtime 如何实际调用 Script：

`PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`

具体 Script 文件与实现任务：

`PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md`

层级关系：

```text
Architecture / Design
        ↓
Script Contract
        ↓
Runtime Specification
        ↓
Implementation Plan
```

Contract 不重新定义上游 Domain Model。

Runtime 不重新定义 Script Contract。

Implementation 不重新设计 Script Contract。

---

# 31. V1 Contract Summary

Project Incubator V1 Script Contract 定义：

- Script Contract Model；
- Script Identity；
- Invocation Purpose；
- Script Input；
- Context Reference；
- Artifact Reference；
- Validation Requirement；
- Execution Parameter；
- Script Output；
- Execution Status；
- Validation Result；
- Validation Evidence；
- Diagnostic Information；
- Error Handling；
- Gate Integration Boundary；
- Workflow Integration Boundary；
- Context Integration Boundary；
- Runtime Boundary。

核心 Contract 原则：

1. Script 是 Runtime 使用的确定性能力。

2. Script 接收明确 Input，执行确定性操作并返回结构化 Output。

3. Script Invocation Purpose 只分为：

```text
VALIDATION
DETERMINISTIC_OPERATION
```

4. Script Execution Status 只允许：

```text
COMPLETED
INVALID_INPUT
UNSUPPORTED_INVOCATION
EXECUTION_ERROR
```

5. Script Validation Result 只允许：

```text
REQUIREMENT_SATISFIED
REQUIREMENT_UNSATISFIED
VALIDATION_NOT_COMPLETED
```

6. Execution Status 与 Validation Result 必须分离。

7. Validation Failure 表示：

```text
COMPLETED + REQUIREMENT_UNSATISFIED
```

8. Script Execution Error 表示：

```text
EXECUTION_ERROR + VALIDATION_NOT_COMPLETED
```

9. Validation Failure 不是 Script Execution Error。

10. Invalid Input 不是 Validation Failure。

11. Unsupported Invocation 不是 Validation Failure。

12. Validation Result 必须提供 Evidence 或无法完成 Validation 的 Reason。

13. Script 不拥有 Maker Decision Authority。

14. Script 不拥有 Workflow Transition Authority。

15. Script 不拥有 Gate Authorization Authority。

16. Script 不拥有 Context Domain Authority。

17. Script 不拥有 Direct Context Read Permission。

18. Context-derived Data 只能由 Runtime 按 Context Access Contract 提供。

19. Script Result 不得直接修改 Context。

20. Script Result 不得直接推进 Workflow。

21. Script Result 不得直接改变 Runtime State。

22. Gate 可以使用 Script Validation Evidence。

23. Validation Result 不等于 Gate Evaluation Result。

24. Evidence-Based Gate 可以使用 Script Evidence，但不要求必须由 Script 执行。

25. Judgment-Based Gate 不得被 Script 自动转化为确定性判断。

26. Mixed Gate 中 Script 只负责可确定性验证部分。

27. Runtime 负责协调 Script Invocation 与 Gate Invocation。

28. Script Invocation、执行顺序、Retry、Runner 与 Runtime Lifecycle 全部属于 Runtime Specification。

29. Script 源代码、文件位置和项目具体验证实现全部属于 Implementation Layer。
