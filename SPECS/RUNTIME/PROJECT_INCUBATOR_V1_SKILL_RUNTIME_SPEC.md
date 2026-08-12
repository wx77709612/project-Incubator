# Project Incubator V1 Skill Runtime Specification

# 1. Runtime Purpose

本文档定义 Project Incubator V1 的 Runtime 执行机制。

本文档属于：

Runtime Layer。

本文档负责：

- Runtime Lifecycle；
- Runtime Component Model；
- Component Loading；
- Execution Flow；
- Workflow Execution；
- Context Interaction；
- Gate Invocation；
- Script Invocation；
- Advisory Runtime Relationship；
- Maker Interaction；
- Failure and Suspension。

本文档依赖：

- Architecture Layer；
- Design Layer；
- Contract Layer。

本文档只执行已经冻结的上游规则。

本文档不重新定义：

- Workflow Model；
- Gate Model；
- Context Model；
- Advisory Model；
- Workflow Contract；
- Gate Contract；
- Context Access Contract；
- Script Contract。

---

# 2. Runtime Model

## 2.1 Runtime Definition

Project Incubator V1 Runtime 是：

Skill Package 内部负责确定性执行和受控协调的执行层。

Runtime 负责：

- 协调 Workflow；
- 使用 Context；
- 调用 Gate；
- 调用 Script；
- 协调 Artifact 相关确定性处理；
- 承载 Phase 推进所需执行机制；
- 阻止违反 Contract 的状态变化；
- 将上游 Domain Model 和 Contract 转化为受控执行。

Runtime 不负责：

- 定义项目方向；
- 替代 Maker 决策；
- 替代 Agent Reasoning；
- 创造新的 Workflow Rule；
- 创造新的 Gate Rule；
- 创造新的 Context Authority；
- 创造新的 Script Contract。

---

## 2.2 Runtime Authority Boundary

Runtime 不拥有：

- Workflow Domain Authority；
- Gate Domain Authority；
- Context Domain Authority；
- Maker Decision Authority；
- Agent Reasoning Authority。

Runtime 拥有：

已经由 Contract 明确授予的确定性执行能力。

Runtime 可以：

执行。

Runtime 不可以：

重新决定规则。

---

## 2.3 Runtime and Agent Boundary

Agent 负责：

- 理解 Maker Intent；
- 分析项目；
- 形成 Solution；
- 执行需要推理或创造性的 Phase Process；
- 形成 Judgment Evidence；
- 向 Runtime 提出确定性执行请求。

Runtime 负责：

- 验证请求是否符合 Contract；
- 准备确定性执行所需输入；
- 执行允许的 Context Interaction；
- 执行 Gate Invocation；
- 执行 Script Invocation；
- 执行允许的 Workflow State Change；
- 返回确定性 Runtime Result。

Runtime 不替代 Agent：

生成创造性 Phase Result。

Agent 不绕过 Runtime：

直接执行受控状态变化。

---

## 2.4 Runtime and Maker Boundary

Maker 保留：

- Project Goal 决策权；
- Project Scope 决策权；
- 重要项目 Decision；
- Gate 所要求的 Maker Authorization；
- 需要人工确认的长期变化授权。

Runtime：

不得自动生成 Maker Authorization。

Runtime：

不得把以下内容当作 Maker Authorization：

- Agent Recommendation；
- Agent Judgment；
- Advisory Response；
- Script Result；
- Validation Result；
- Runtime 自身判断；
- Gate Evaluation 本身。

---

# 3. Runtime Execution State Model

## 3.1 Runtime Execution State

一次 Runtime Execution 只允许处于以下状态之一：

- `EXECUTING`；
- `WAITING_FOR_MAKER`；
- `BLOCKED_BY_GATE`；
- `SUSPENDED`；
- `FAILED`；
- `COMPLETED`。

Runtime Execution State：

只描述一次 Runtime Execution。

它不是：

Project State。

不得替代：

`PROJECT_STATE.md`

作为项目当前状态 Source of Truth。

---

## 3.2 EXECUTING

表示：

当前 Runtime Request 正在进行合法的确定性处理。

Runtime 可以继续：

- 读取允许的 Context；
- 检查 Workflow；
- 准备 Gate Input；
- 调用 Script；
- 消费 Contract Result；
- 执行已授权的 Context Mutation；
- 形成 Runtime Result。

---

## 3.3 WAITING_FOR_MAKER

表示：

当前 Runtime Execution 无法继续，

唯一仍缺少的必要条件属于 Maker 输入。

包括：

- Maker Authorization；
- Maker Decision；
- Maker Clarification。

`WAITING_FOR_MAKER`

不是：

Runtime Failure。

Runtime 不得在该状态下：

自行补全 Maker Input。

---

## 3.4 BLOCKED_BY_GATE

表示：

当前 Requested Action 已进入 Gate Protection Boundary，

并且存在仍阻止当前 Action 的 Gate Result。

包括：

- `REQUIREMENT_UNSATISFIED`；
- `ACTION_BLOCKED`。

Runtime 在该状态下：

不得继续对应受保护 Action。

---

## 3.5 SUSPENDED

表示：

Runtime 本身没有发生执行故障，

但当前外部条件不足以安全继续。

可以包括：

- Missing Context；
- Context Conflict；
- Workflow Requirement 未满足；
- Invalid Workflow State；
- Transition Not Allowed；
- Contract Violation；
- Gate Evidence Insufficient；
- Validation Unsatisfied；
- Validation Not Completed；
- Invalid Script Input；
- Unsupported Script Invocation；
- Unsupported Runtime Condition。

SUSPENDED：

表示当前执行可以在条件变化后重新进入。

---

## 3.6 FAILED

表示：

当前 Runtime Execution 发生实际执行失败。

包括：

- Runtime Dependency Failure；
- Runtime Internal Failure；
- Script Execution Error；
- Context Persistence Failure；
- Required deterministic operation 无法正常完成。

FAILED：

只表示当前 Runtime Execution 失败。

不表示：

项目本身失败。

---

## 3.7 COMPLETED

表示：

当前 Runtime Request 已完成其被授权的执行目标。

COMPLETED：

不等于：

整个 Project 已完成。

也不等于：

当前 Phase 必然 Completed。

---

# 4. Runtime Suspension Reason

当 Runtime State 为：

`SUSPENDED`

时，

必须同时提供明确 Suspension Reason。

V1 使用以下 Suspension Reason：

- `MISSING_CONTEXT`；
- `CONTEXT_CONFLICT`；
- `WORKFLOW_NOT_READY`；
- `INVALID_WORKFLOW_STATE`；
- `TRANSITION_NOT_ALLOWED`；
- `CONTRACT_VIOLATION`；
- `EVIDENCE_INSUFFICIENT`；
- `VALIDATION_UNSATISFIED`；
- `VALIDATION_NOT_COMPLETED`；
- `INVALID_SCRIPT_INPUT`；
- `UNSUPPORTED_SCRIPT_INVOCATION`；
- `UNSUPPORTED_RUNTIME_CONDITION`。

不得仅输出：

“无法继续”。

---

# 5. Runtime Failure Reason

当 Runtime State 为：

`FAILED`

时，

必须提供明确 Failure Reason。

V1 使用以下 Failure Reason：

- `RUNTIME_DEPENDENCY_FAILURE`；
- `RUNTIME_INTERNAL_FAILURE`；
- `SCRIPT_EXECUTION_ERROR`；
- `CONTEXT_PERSISTENCE_FAILURE`。

Runtime 不得把：

业务条件未满足

错误表示为：

Runtime Failure。

---

# 6. Runtime Component Model

Project Incubator V1 Runtime 使用以下逻辑 Runtime Component：

1. Runtime Coordinator；
2. Definition Resolver；
3. Context Coordinator；
4. Workflow Coordinator；
5. Gate Coordinator；
6. Script Coordinator；
7. Advisory Bridge；
8. Runtime Result Coordinator。

这些是：

Runtime Responsibility Component。

它们不是新的 Domain Module。

---

# 7. Runtime Coordinator

## 7.1 Responsibility

Runtime Coordinator 负责：

- 接收 Runtime Request；
- 创建 Runtime Execution；
- 维护当前 Runtime Execution State；
- 协调其他 Runtime Component；
- 决定当前执行继续、等待、阻塞、暂停、失败或完成；
- 形成最终 Runtime Result。

---

## 7.2 Input Dependency

依赖：

- Runtime Request；
- Contract Definition；
- 其他 Runtime Component Result。

---

## 7.3 Output Responsibility

输出：

- Runtime Execution State；
- Runtime Result；
- Pending Requirement；
- Suspension / Failure Reason。

---

## 7.4 Non-Responsibility

Runtime Coordinator 不负责：

- Domain Judgment；
- Maker Decision；
- Context Authority；
- Gate Rule；
- Workflow Rule。

---

# 8. Definition Resolver

## 8.1 Responsibility

Definition Resolver 负责获得 Runtime 执行当前 Request 所需要的冻结定义。

包括：

- Workflow Definition；
- Gate Definition；
- Context Definition Reference；
- Advisory Definition；
- Workflow Contract；
- Context Access Contract；
- Gate Contract；
- Script Contract。

---

## 8.2 Output Responsibility

输出：

当前 Runtime Execution 可以引用的：

Frozen Definition Set。

---

## 8.3 Non-Responsibility

Definition Resolver 不允许：

- 修改 Definition；
- 补充缺失 Domain Rule；
- 合并冲突规则；
- 选择性忽略上游 Contract。

如果执行所需 Definition 缺失：

Runtime State：

`FAILED`

Failure Reason：

`RUNTIME_DEPENDENCY_FAILURE`

---

# 9. Context Coordinator

## 9.1 Responsibility

Context Coordinator 负责：

- 根据 Context Access Contract 读取 Context；
- 构造 Context Access Request；
- 处理 Context Access Result；
- 形成 Context Mutation Request；
- 检查 Mutation Authority；
- 执行已经满足 Contract 的 Context Mutation；
- 验证 Context Persisted Result；
- 处理 Context Conflict。

---

## 9.2 Non-Responsibility

Context Coordinator 不负责：

- 定义 Context Authority；
- 改变 Source of Truth；
- 自动生成 Maker Authorization；
- 使用 Runtime State 覆盖 Project State。

---

# 10. Workflow Coordinator

## 10.1 Responsibility

Workflow Coordinator 负责：

- 识别 Current Workflow；
- 识别 Current Phase；
- 准备 Phase Input；
- 接收 Phase Result；
- 检查 Required Artifact Requirement；
- 处理 State Change Requirement；
- 识别 Gate Trigger Requirement；
- 构造 Transition Request；
- 消费 Transition Eligibility Result；
- 执行已经满足全部条件的 Transition。

---

## 10.2 Non-Responsibility

Workflow Coordinator 不负责：

- 修改 Core Phase；
- 新增 Transition；
- 修改 Allowed Next Phase；
- 执行 Agent 创造性 Process；
- 重新定义 Artifact Flow。

---

# 11. Gate Coordinator

## 11.1 Responsibility

Gate Coordinator 负责：

- 识别已经命中 Gate Definition 的 Trigger Event；
- 创建 Gate Invocation；
- 准备 Gate Input；
- 收集 Evaluation Evidence；
- 调用 Script 获取确定性 Validation Evidence；
- 接收 Judgment Evidence；
- 处理 Maker Authorization Evidence；
- 形成 Gate Output；
- 将 Gate Result 映射回 Runtime Execution。

---

## 11.2 Non-Responsibility

Gate Coordinator 不负责：

- 新增 Gate；
- 修改 Gate Definition；
- 替代 Agent Judgment；
- 替代 Maker Authorization；
- 直接修改 Workflow；
- 直接修改 Context。

---

# 12. Script Coordinator

## 12.1 Responsibility

Script Coordinator 负责：

- 解析需要确定性能力的 Runtime Requirement；
- 选择已经存在的 Script Capability；
- 准备 Script Input；
- 执行 Script Invocation；
- 接收 Script Output；
- 消费 Execution Status；
- 消费 Validation Result；
- 路由 Validation Evidence；
- 处理 Script Error。

---

## 12.2 Non-Responsibility

Script Coordinator 不允许：

- 使用 Script 进行 Judgment-Based 最终判断；
- 赋予 Script Context Direct Read；
- 使用 Script Result 直接推进 Workflow；
- 使用 Script Result 直接修改 Context；
- 使用 Script Result 自动批准 Gate。

---

# 13. Advisory Bridge

## 13.1 Responsibility

Advisory Bridge 负责：

在 Runtime 执行过程中识别：

当前情境是否与已定义 Advisory Trigger 对应，

并向 Agent 暴露形成 Advisory 所需的现有领域信息。

---

## 13.2 Non-Responsibility

Advisory Bridge：

不生成新的 Advisory Domain Rule。

Advisory Response：

不直接成为 Runtime Command。

Advisory Bridge 不允许：

- 修改 Workflow；
- 修改 Context；
- 解除 Gate；
- 执行 Script；
- 自动推进 Phase。

---

# 14. Runtime Result Coordinator

Runtime Result Coordinator 负责形成一次执行的最终结果摘要。

Runtime Result 至少必须能够表达：

- Execution Reference；
- Runtime Execution State；
- Runtime Reason；
- Current Phase Reference；
- Workflow Result Reference；
- Context Access Result Reference；
- Gate Output Reference；
- Script Output Reference；
- Pending Requirement；
- Required Maker Input；
- Completed Action Reference；
- Next Allowed Action。

Runtime Result：

只汇总上游 Contract Result。

不得重新解释 Contract Result。

---

# 15. Component Loading Model

## 15.1 Loading Principle

Runtime 启动执行时：

必须先获得规则，

再获得项目数据，

最后执行行为。

固定逻辑顺序为：

```text
Runtime Request
        ↓
Contract Definition Resolution
        ↓
Domain Definition Resolution
        ↓
Context Establish / Restore
        ↓
Current Workflow / Phase Resolution
        ↓
Relevant Gate Definition Resolution
        ↓
Relevant Script Capability Resolution
        ↓
Artifact / Evidence Reference Resolution
        ↓
Runtime Execution
```

---

## 15.2 Contract Loading

Runtime 必须首先确认当前执行需要的 Contract 可用。

至少包括：

- Context Access Contract；
- Workflow Contract；
- Gate Contract；
- Script Contract。

Runtime 不得：

在缺少对应 Contract 时自行推导交互规则。

---

## 15.3 Domain Definition Loading

Contract 可用后：

Runtime 必须解析其引用的 Domain Definition。

包括：

- Workflow Design；
- Gate Design；
- Context Model Design；
- Phase Advisory Design。

Domain Definition：

只作为执行依据。

Runtime 不修改 Domain Definition。

---

## 15.4 Context Loading

Context 只能在：

Context Access Contract 已解析后读取。

Runtime 必须通过合法 Context Access：

建立或恢复当前 Project Context。

---

## 15.5 Gate Definition Loading

Runtime 必须根据当前：

- Workflow Requirement；
- Requested Action；
- Context Mutation；
- Artifact Change；
- Runtime Event

匹配已经定义的 Gate Trigger Condition。

Runtime 只能加载：

已存在 Gate Definition。

---

## 15.6 Script Capability Loading

Runtime 只在：

存在明确的确定性 Requirement 时

加载对应 Script Capability。

Script Capability：

不得由 Runtime 临时创造。

具体 Script 文件位置：

由 Implementation Layer 定义。

---

## 15.7 Advisory Information Loading

Advisory 不是 Runtime 必需阻塞依赖。

只有当已定义 Advisory Trigger 出现时：

Runtime 才可以准备相关 Advisory Context 给 Agent。

---

# 16. Runtime Lifecycle

一次 Runtime Execution 采用以下生命周期：

```text
1. Receive Runtime Request

2. Resolve Required Definitions

3. Establish / Restore Project Context

4. Resolve Current Workflow and Phase

5. Validate Runtime Request

6. Prepare Phase / Operation Input

7. Coordinate Phase Result or Deterministic Operation

8. Evaluate Required Artifact / Validation Requirement

9. Detect Gate Requirement

10. Invoke Script when deterministic evidence is required

11. Invoke Gate

12. Handle Maker Requirement

13. Prepare Context Mutation

14. Re-evaluate Workflow Transition Eligibility

15. Execute Authorized Context Mutation

16. Commit Workflow Transition when applicable

17. Form Runtime Result

18. Complete / Suspend / Block / Fail
```

Runtime 不允许：

跳过中间 Contract Requirement，

直接从 Runtime Request 进入状态修改。

---

# 17. Runtime Request Entry

## 17.1 Normal Runtime Request

正常 Runtime Request：

由 Agent 提交一个明确的确定性执行目标。

Runtime 首先必须确认：

- Requested Action 是否明确；
- 需要使用哪些上游 Contract；
- 当前 Project Context 是否足以处理；
- 当前 Requested Action 是否属于 Runtime Authority。

---

## 17.2 Maker Resume Input

当 Runtime 处于：

`WAITING_FOR_MAKER`

时，

Maker 新提供：

- Authorization；
- Decision；
- Clarification

可以作为后续 Resume Execution 的输入。

Runtime 必须重新检查：

当前事实是否仍然有效。

不得自动使用已经失效的旧 Gate Result。

---

## 17.3 Unsupported Request

如果 Request 要求 Runtime：

执行上游未授权能力，

Runtime State：

`SUSPENDED`

Suspension Reason：

`UNSUPPORTED_RUNTIME_CONDITION`

Runtime 不得自行新增能力。

---

# 18. Project Context Establishment and Recovery

## 18.1 Existing Project

当 `PROJECT_STATE.md` 已存在时：

Runtime 必须以：

`PROJECT_STATE.md`

作为当前项目状态 Source of Truth。

Runtime 不得使用：

- Runtime Temporary State；
- PROJECT_PLAN.md；
- 历史聊天；
- Artifact State；
- Agent Memory

覆盖 `PROJECT_STATE.md`。

---

## 18.2 New Project Bootstrap

P0 Intent Discovery 明确允许：

在不存在既有 Core Context 的情况下开始。

因此：

当 Runtime 收到明确 New Project 初始化请求，

并确认不存在已有权威 Project State 时：

Runtime 可以建立仅用于当前执行的：

P0 Bootstrap Runtime Reference。

该 Reference：

不是 Project State Source of Truth。

它只允许：

启动 P0。

不得用于：

推断任意其他 Current Phase。

---

## 18.3 Bootstrap State Establishment

P0 形成：

State Change Requirement

后，

Runtime 可以依据：

Context Access Contract 中允许的 Change Basis

形成：

`PROJECT_STATE.md`

的 Context Mutation Request。

只有 Context Access Result 允许执行后：

Runtime 才能建立持久化 Project State。

一旦 `PROJECT_STATE.md` 建立：

后续 Current Phase 判断必须完全以其为准。

---

## 18.4 Missing Existing State

如果当前 Request 明确针对已有项目，

但 `PROJECT_STATE.md` 缺失：

Runtime 不得推测 Current Phase。

Runtime State：

`SUSPENDED`

Suspension Reason：

`MISSING_CONTEXT`

如果该 Request 同时属于高影响行为：

还必须进入：

Context Integrity Gate。

---

# 19. Current Workflow and Phase Resolution

Runtime 识别 Current Phase 时：

必须执行以下顺序：

1. 获取合法 `PROJECT_STATE.md`；
2. 读取 Current Phase；
3. 使用 Workflow Contract 检查 Phase 是否属于合法 Core Phase；
4. 检查 Current Phase Reference 与 Workflow Definition 是否一致；
5. 检查 Requested Action 是否与 Current Phase 相容。

如果 Current Phase 不属于合法 Workflow：

Runtime State：

`SUSPENDED`

Suspension Reason：

`INVALID_WORKFLOW_STATE`

Runtime 不得：

自行修正为“最可能”的 Phase。

---

# 20. Workflow Execution Flow

## 20.1 Phase Input Preparation

Runtime 根据 Workflow Contract：

准备当前 Phase 所需引用。

包括：

- Current Phase Reference；
- Context Reference；
- Artifact Reference；
- Workflow Requirement Reference。

Context Reference：

不得绕过 Context Access Contract。

---

## 20.2 Creative Phase Process

如果当前 Phase Process 需要：

- 判断；
- 推理；
- 创造性生成；

Runtime 不执行该 Process。

由：

Agent

形成对应 Phase Result。

Runtime 只消费：

符合 Workflow Contract 的 Phase Result。

---

## 20.3 Phase Result Reception

Runtime 接收 Phase Result 后：

必须检查：

- Process Result Status；
- Phase Output Reference；
- Required Artifact Requirement Status；
- State Change Requirement；
- Gate Trigger Requirement；
- Requested Next Phase。

---

## 20.4 Process Result

如果：

`Process Result Status = NOT_FORMED`

则：

Workflow Transition Result：

`NOT_READY`

Runtime 不得推进 Phase。

Runtime 可以结束当前确定性检查，

并返回：

Runtime State = `SUSPENDED`

Suspension Reason = `WORKFLOW_NOT_READY`

---

# 21. Required Artifact Processing

## 21.1 Required Artifact Check

Runtime 必须使用当前 Phase 的：

Required Artifact Requirement。

不得使用：

其他 Phase Artifact

替代。

---

## 21.2 Deterministic Artifact Validation

如果 Required Artifact Requirement 可以通过确定性条件检查：

Runtime 可以：

调用 Script。

Script Validation：

只检查明确 Requirement。

---

## 21.3 Artifact Unsatisfied

如果：

Required Artifact Requirement Status = `UNSATISFIED`

Runtime State：

`SUSPENDED`

Suspension Reason：

`WORKFLOW_NOT_READY`

Runtime 不得：

自动创建缺失的创造性 Artifact。

---

# 22. State Change Requirement Processing

State Change Requirement：

只表示 Workflow 已经形成状态变化需求。

它不表示：

`PROJECT_STATE.md`

已经发生 Mutation。

Runtime 必须：

1. 读取 State Change Requirement；
2. 构造 Context Mutation Request；
3. 通过 Context Access Contract 验证；
4. 处理可能存在的 Gate Requirement；
5. 满足 Maker Authorization Requirement；
6. 获得 `EXECUTE_MUTATION` 资格；
7. 执行实际 State Mutation；
8. 重新读取并验证持久化结果。

不得跳过：

Context Access Contract。

---

# 23. Gate Trigger Detection

Runtime 只可以根据：

已经存在的 Gate Trigger Condition

检测 Gate Requirement。

Trigger Source 可以来自：

- Workflow Gate Trigger Requirement；
- Context Mutation；
- Requested Action；
- Artifact Change；
- Builder Action；
- Architecture / Framework Change；
- Gate Model Change；
- 其他 Gate Design 已明确定义的 Trigger Event。

Runtime 不得：

发明新的 Gate Trigger。

---

# 24. Gate Lifecycle Runtime Handling

Runtime 对 Gate Lifecycle 的执行映射如下。

## 24.1 Trigger Detected

检测到 Gate Trigger：

Gate Lifecycle：

`Triggered`

---

## 24.2 Evaluation Started

Runtime 已开始准备 Gate Input：

Gate Lifecycle：

`Awaiting Evaluation`

---

## 24.3 Evidence Insufficient

Gate Result：

`EVIDENCE_INSUFFICIENT`

Gate 保持：

`Awaiting Evaluation`

Runtime State：

`SUSPENDED`

Suspension Reason：

`EVIDENCE_INSUFFICIENT`

---

## 24.4 Authorization Required

Gate Result：

`AUTHORIZATION_REQUIRED`

Gate Lifecycle：

`Awaiting Authorization`

Runtime State：

`WAITING_FOR_MAKER`

---

## 24.5 Requirement Unsatisfied

Gate Result：

`REQUIREMENT_UNSATISFIED`

Gate Requirement：

保持未解决。

Runtime State：

`BLOCKED_BY_GATE`

---

## 24.6 Action Blocked

Gate Result：

`ACTION_BLOCKED`

Gate Requirement：

保持未解决。

Runtime State：

`BLOCKED_BY_GATE`

Runtime 不得：

自动尝试绕过该 Gate。

---

## 24.7 Requirement Satisfied

Gate Result：

`REQUIREMENT_SATISFIED`

Gate Lifecycle：

`Resolved`

Runtime 可以继续：

对应 Requested Action 的后续 Contract 检查。

Resolved：

不表示 Requested Action 已经执行。

---

## 24.8 Reopened

已经 Resolved 的 Gate：

如果发生以下任何变化：

- Risk Object 实质变化；
- Trigger Action 变化；
- Evaluation Evidence 变化；
- Maker Authorization 变化；
- Context 发生影响原判断的变化；

Runtime 必须：

将该 Gate 视为：

`Reopened`

并重新执行 Gate Evaluation。

---

# 25. Gate Invocation Flow

每一次 Gate Invocation 使用以下顺序：

```text
Gate Trigger Detected
        ↓
Resolve Gate Definition
        ↓
Create Gate Invocation Reference
        ↓
Prepare Gate Input
        ↓
Collect Existing Evidence
        ↓
Collect Deterministic Evidence when needed
        ↓
Collect Judgment Evidence when needed
        ↓
Check Maker Authorization
        ↓
Form Gate Evaluation Result
        ↓
Return Gate Output
```

---

# 26. Evidence-Based Gate Execution

对于：

Evidence-Based Gate，

Runtime 可以：

- 使用已有确定性 Evidence；
- 调用 Script 获取 Validation Evidence。

Runtime 不要求：

所有 Evidence-Based Gate 都必须调用 Script。

如果现有 Evidence 已足够：

无需额外 Script Invocation。

---

# 27. Judgment-Based Gate Execution

对于：

Judgment-Based Gate，

Runtime 不得使用 Script：

形成最终 Judgment。

Runtime 必须获得：

Agent 或 Maker 提供的 Judgment Evidence。

如果 Judgment Evidence 不足：

Gate Result：

`EVIDENCE_INSUFFICIENT`

Runtime State：

`SUSPENDED`

---

# 28. Mixed Gate Execution

对于：

Mixed Gate，

Runtime 必须分别处理：

- Deterministic Evidence；
- Judgment Evidence。

Runtime 可以：

使用 Script 处理确定性部分。

Runtime 必须：

从 Agent / Maker 获得需要语义判断的部分。

任何一部分不足：

不得返回：

`REQUIREMENT_SATISFIED`

---

# 29. Multi-Gate Execution

同一个 Requested Action：

如果同时命中多个 Gate：

Runtime 必须：

为每个 Gate 建立独立 Invocation。

每个 Gate：

必须独立形成 Gate Output。

只有全部相关 Gate Result 均为：

`REQUIREMENT_SATISFIED`

Runtime 才可以：

继续对应 Requested Action。

一个 Gate 的 Authorization：

不得自动覆盖另一个 Gate。

---

# 30. Maker Authorization Flow

当 Gate Result 为：

`AUTHORIZATION_REQUIRED`

Runtime 必须：

1. 保存当前 Pending Gate Requirement Reference；
2. 保存 Risk Object Reference；
3. 保存 Requested Action Reference；
4. 保存 Authorization Scope Requirement；
5. 将 Runtime State 设置为 `WAITING_FOR_MAKER`；
6. 返回需要 Maker 授权的明确对象。

Maker 提供授权后：

Runtime 必须重新检查：

- Gate 是否仍然有效；
- Risk Object 是否变化；
- Requested Action 是否变化；
- Authorization Scope 是否匹配。

只有 Gate Contract 返回有效结果：

`REQUIREMENT_SATISFIED`

后：

Runtime 才可以继续。

---

# 31. Context Read Flow

Runtime 读取 Context 使用以下流程：

```text
Determine Required Context
        ↓
Create Context Access Request
        ↓
Access Type = READ
        ↓
Evaluate Context Access Contract
        ↓
Consume Context Access Result
        ↓
Read only if ACCEPTED
```

---

# 32. Context Access Result Handling

## 32.1 ACCEPTED

Runtime 可以继续执行对应 Access。

`ACCEPTED`

不表示 Mutation 已完成。

---

## 32.2 REJECTED

Runtime 不得继续目标 Access。

Runtime State：

`SUSPENDED`

Suspension Reason：

`CONTRACT_VIOLATION`

---

## 32.3 AUTHORIZATION_REQUIRED

Runtime State：

`WAITING_FOR_MAKER`

Runtime 不得：

自动批准。

---

## 32.4 GATE_REQUIREMENT_UNRESOLVED

如果存在明确 Gate Requirement Reference：

Runtime 必须进入：

Gate Invocation Flow。

不得直接执行 Context Mutation。

---

## 32.5 BOUNDARY_VIOLATION

Runtime State：

`SUSPENDED`

Suspension Reason：

`CONTRACT_VIOLATION`

Maker Authorization：

不得自动修复 Domain Boundary Violation。

---

## 32.6 CONTEXT_CONFLICT

Runtime State：

`SUSPENDED`

Suspension Reason：

`CONTEXT_CONFLICT`

如果后续 Requested Action 属于高影响操作：

必须进入：

Context Integrity Gate。

---

# 33. Context Mutation Flow

Context Mutation 固定采用：

```text
Identify Change Basis
        ↓
Create REQUEST_MUTATION
        ↓
Check Mutation Authority
        ↓
Check Gate Requirement
        ↓
Check Maker Authorization
        ↓
Obtain EXECUTE_MUTATION Eligibility
        ↓
Execute Mutation
        ↓
Persist Context
        ↓
Read Back
        ↓
Verify Persisted Result
```

Runtime 不得：

从 REQUEST_MUTATION

直接跳到：

Persist Context。

---

# 34. Context Mutation Basis

Runtime 只能使用 Context Access Contract 已允许的 Change Basis。

包括已经存在的：

- Maker Confirmed Change；
- Workflow Output；
- Workflow State Change Requirement；
- Confirmed Decision；
- Validated Execution Fact；
- Context Lifecycle Requirement；
- Project Type Context Requirement。

Runtime 不得使用：

- Agent Guess；
- Historical Chat Assumption；
- Runtime Temporary State；
- Unconfirmed Plan

作为唯一 Mutation Basis。

---

# 35. Context Mutation Commit Order

当一次 Workflow 推进需要多个 Context Mutation 时：

Runtime 使用以下顺序：

1. 验证所有待执行 Mutation 的 Contract Eligibility；
2. 处理全部相关 Gate；
3. 处理全部 Maker Authorization；
4. 执行非 `PROJECT_STATE.md` 的必要 Context Mutation；
5. 验证这些 Mutation 已持久化；
6. 最后执行 `PROJECT_STATE.md` Mutation；
7. 重新读取 `PROJECT_STATE.md`；
8. 确认 Current Phase / State 与预期 State Change Requirement 一致。

`PROJECT_STATE.md`

作为当前项目状态 Source of Truth：

在 Workflow Transition Commit 中最后更新。

---

# 36. Context Mutation Failure

如果某个 Context Mutation：

执行后无法验证持久化结果，

Runtime State：

`FAILED`

Failure Reason：

`CONTEXT_PERSISTENCE_FAILURE`

Runtime 不得：

假定 Mutation 已成功。

V1 Runtime：

不执行未经上游 Contract 定义的自动破坏性 Rollback。

下一次 Runtime Execution：

必须重新读取 Authority Context，

再判断当前实际状态。

---

# 37. Script Invocation Condition

Runtime 只在以下条件满足时调用 Script：

1. 存在明确 Script Identity 或可解析的既有 Script Capability；
2. Invocation Purpose 属于：
   - `VALIDATION`；
   - `DETERMINISTIC_OPERATION`；
3. 当前工作属于确定性操作；
4. Script Input 可以根据 Script Contract 完整形成；
5. 调用不会赋予 Script 未授权 Authority。

---

# 38. Script Input Preparation

Runtime 准备 Script Input 时：

必须提供 Script Contract 要求的信息。

至少包括：

- Invocation ID；
- Script Identity；
- Invocation Purpose；
- Input Data；
- Context Reference；
- Artifact Reference；
- Validation Requirement；
- Execution Parameter。

Runtime 只能向 Script 提供：

已经合法获得的 Context-derived Data。

Script：

不得获得 Direct Context Read。

---

# 39. Script Execution Flow

Script Invocation 执行顺序：

```text
Resolve Script Capability
        ↓
Prepare Contract-valid Script Input
        ↓
Execute Script
        ↓
Receive Script Output
        ↓
Inspect Execution Status
        ↓
Inspect Validation Result
        ↓
Route Evidence
        ↓
Continue / Suspend / Fail
```

---

# 40. Script Retry Policy

Project Incubator V1：

默认不执行自动 Script Retry。

原因属于 Runtime Safety Boundary：

同一个失败 Script Invocation：

不得在未确认失败性质的情况下自动重复执行。

如果需要重新调用：

必须形成新的 Script Invocation。

Runtime 可以使用：

新的 Invocation ID

重新执行。

---

# 41. Script Timeout Policy

V1 Runtime：

不定义独立于宿主执行环境的固定 Script Timeout Duration。

如果宿主执行环境终止 Script：

Runtime 将其作为：

Script Execution Error。

对应：

`Execution Status = EXECUTION_ERROR`

Runtime State：

`FAILED`

Failure Reason：

`SCRIPT_EXECUTION_ERROR`

Runtime 不得：

把 Timeout 解释为 Validation Failure。

---

# 42. Script Result Handling

## 42.1 COMPLETED + REQUIREMENT_SATISFIED

表示：

Script 正常执行，

并且确定性 Validation Requirement 满足。

Runtime 可以：

将 Validation Result 与 Evidence

提供给：

- Gate；
- Workflow-related Runtime；
- 后续确定性判断。

不得直接：

推进 Workflow。

---

## 42.2 COMPLETED + REQUIREMENT_UNSATISFIED

表示：

Validation Failure。

Runtime State：

`SUSPENDED`

Suspension Reason：

`VALIDATION_UNSATISFIED`

该结果：

不是 Runtime Failure。

---

## 42.3 COMPLETED + VALIDATION_NOT_COMPLETED

Runtime State：

`SUSPENDED`

Suspension Reason：

`VALIDATION_NOT_COMPLETED`

不得：

推断 Requirement 满足或不满足。

---

## 42.4 INVALID_INPUT

Runtime State：

`SUSPENDED`

Suspension Reason：

`INVALID_SCRIPT_INPUT`

不得自动修改 Script Input 中的领域事实。

---

## 42.5 UNSUPPORTED_INVOCATION

Runtime State：

`SUSPENDED`

Suspension Reason：

`UNSUPPORTED_SCRIPT_INVOCATION`

Runtime 不得：

扩大 Script Capability。

---

## 42.6 EXECUTION_ERROR

Runtime State：

`FAILED`

Failure Reason：

`SCRIPT_EXECUTION_ERROR`

不得将其表示为：

Validation Requirement Unsatisfied。

---

# 43. Script and Gate Integration

Script Validation Result：

只作为：

Validation Evidence。

Runtime 传递给 Gate 的是：

- Validation Result Reference；
- Evidence。

Runtime 不允许：

```text
Script REQUIREMENT_SATISFIED
        =
Gate REQUIREMENT_SATISFIED
```

两者属于不同 Contract Layer Result。

Gate：

必须继续执行完整 Gate Evaluation。

---

# 44. Validation Feedback Runtime Handling

当 Script 或其他确定性 Validation 形成：

`REQUIREMENT_UNSATISFIED`

时，

Runtime 可以识别：

Advisory Trigger = `Validation Feedback`

并向 Agent提供：

- Validation Result；
- Evidence；
- Current Phase；
- Relevant Artifact。

Advisory：

只能帮助 Agent理解后续调整方向。

Advisory 不自动修改：

- Plan；
- Artifact；
- Workflow；
- Context。

---

# 45. Workflow Transition Processing

Runtime 只有在 Workflow Contract 返回：

`READY_FOR_TRANSITION`

时，

才可以进入实际 Transition Execution。

`READY_FOR_TRANSITION`

只表示：

Transition Eligibility 已满足。

不表示：

Transition 已经发生。

---

# 46. Workflow NOT_READY Handling

如果 Workflow Result 为：

`NOT_READY`

Runtime 必须识别具体原因。

如果原因是：

Gate Requirement Unresolved：

进入 Gate Flow。

如果原因是：

Process Incomplete：

Runtime State：

`SUSPENDED`

Suspension Reason：

`WORKFLOW_NOT_READY`

如果原因是：

Required Artifact Unsatisfied：

Runtime State：

`SUSPENDED`

Suspension Reason：

`WORKFLOW_NOT_READY`

如果原因是：

State Change Requirement Missing：

Runtime State：

`SUSPENDED`

Suspension Reason：

`WORKFLOW_NOT_READY`

不得把：

`NOT_READY`

表示为 Runtime Failure。

---

# 47. TRANSITION_NOT_ALLOWED Handling

如果 Workflow Result：

`TRANSITION_NOT_ALLOWED`

Runtime State：

`SUSPENDED`

Suspension Reason：

`TRANSITION_NOT_ALLOWED`

Runtime 不得通过：

- Maker Authorization；
- Gate Resolution；
- Script Result；
- Runtime Decision

把非法 Transition 转换为：

合法 Transition。

如果需要新的 Transition Path：

必须修改：

Workflow Domain Model。

---

# 48. Transition Commit

当：

- Workflow Result = `READY_FOR_TRANSITION`；
- 所有相关 Gate = `REQUIREMENT_SATISFIED`；
- 所有必须 Context Mutation 已满足 Access Contract；
- 所有 Required Maker Authorization 已存在；

Runtime 才可以：

执行 Transition Commit。

Transition Commit 使用：

`PROJECT_STATE.md`

的受控 Mutation

记录新的 Current Phase。

只有：

该 State Mutation 成功持久化并重新验证后，

Runtime 才能认为：

Phase Transition 已经完成。

---

# 49. Iteration Transition

P6 Iteration：

Runtime 只能接受 Workflow Contract 允许的：

- P6 → P2；
- P6 → P3；
- P6 → P4；
- P6 → P5。

Runtime 不选择：

应该返回哪个 Phase。

Requested Next Phase：

必须来自合法 Phase Result。

任何其他 P6 Transition：

必须按照：

`TRANSITION_NOT_ALLOWED`

处理。

---

# 50. Phase Entry Runtime Handling

成功 Transition 后：

Runtime 可以识别：

Advisory Trigger = `Phase Entry`

并准备：

- Current Phase；
- Phase Goal；
- Project Context；
- Relevant Artifact；
- Known Risk。

Advisory：

由 Agent形成。

Runtime 不直接生成：

Advisory Decision。

---

# 51. Advisory Runtime Relationship

## 51.1 Advisory Use Conditions

Runtime 可以在以下已定义情境中：

请求或提供 Advisory 所需信息：

- Phase Entry；
- Maker Guidance Request；
- Missing Information；
- Risk Detected；
- Decision Required；
- Validation Feedback；
- Iteration Re-entry；
- 已定义 Project Type Specific Trigger。

---

## 51.2 Advisory Does Not Control Runtime

Advisory Response：

不直接改变 Runtime Execution State。

Runtime 必须根据：

实际 Contract Condition

判断：

继续、等待、阻塞、暂停或失败。

---

## 51.3 Recommended Action

如果 Advisory Response 包含：

Recommended Action

或：

Suggested Next Step，

Agent 如希望执行：

必须将其转化为新的合法 Runtime Request。

不得由 Runtime：

直接执行 Advisory Recommendation。

---

## 51.4 Decision Needed

如果 Advisory 指出：

Decision Needed

且当前 Requested Action 确实无法在缺少 Maker Decision 时继续，

Runtime State：

`WAITING_FOR_MAKER`

Runtime 不替 Maker：

生成 Decision。

---

## 51.5 Required Clarification

如果 Advisory 指出：

Required Clarification

且该缺失信息属于当前 Contract 必需输入，

Runtime State：

`WAITING_FOR_MAKER`

或：

`SUSPENDED`

判断方式：

如果必须由 Maker 提供：

`WAITING_FOR_MAKER`

如果只属于缺失的可恢复 Context / Evidence：

`SUSPENDED`

---

# 52. Maker Interaction Model

Runtime 与 Maker 的交互只发生于：

当前执行确实存在不可由 Runtime 或 Agent替代的 Maker Requirement。

分为：

- Authorization；
- Decision；
- Clarification。

---

## 52.1 Authorization

来源于：

Gate / Context Access Contract 已定义的 Authorization Requirement。

Runtime State：

`WAITING_FOR_MAKER`

---

## 52.2 Decision

来源于：

项目方向、范围、长期规则或其他 Maker Decision Boundary。

Runtime 不得把：

Agent Proposal

自动变成 Maker Decision。

---

## 52.3 Clarification

当当前执行依赖的关键事实：

无法从 Authority Context 或合法 Evidence 中获得时，

Runtime 可以：

请求 Maker Clarification。

Runtime 不得：

自己补全关键事实。

---

# 53. Failure and Suspension Model

Runtime 必须严格区分：

Business Condition

与：

Execution Failure。

---

## 53.1 Business Condition

以下属于：

业务或 Contract 条件尚未满足。

不是 Runtime Failure：

- Workflow NOT_READY；
- Gate REQUIREMENT_UNSATISFIED；
- Gate AUTHORIZATION_REQUIRED；
- Gate EVIDENCE_INSUFFICIENT；
- Gate ACTION_BLOCKED；
- Validation Requirement Unsatisfied；
- Missing Context；
- Context Conflict；
- Transition Not Allowed；
- Invalid Script Input；
- Unsupported Script Invocation。

---

## 53.2 Execution Failure

以下属于：

当前执行实际失败：

- Script Execution Error；
- Context Persistence Failure；
- Runtime Definition / Dependency 无法加载；
- Runtime Internal Failure。

---

# 54. Contract Violation Handling

以下行为进入：

Contract Violation Handling：

- Runtime Request 要求越权；
- Context Access 被 REJECTED；
- Context Access 返回 BOUNDARY_VIOLATION；
- Workflow 请求非法 Transition；
- Runtime 请求 Script 执行 Judgment-Based 最终判断；
- Runtime 请求 Gate 使用未定义 Trigger；
- Runtime 试图修改上游 Source of Truth。

Runtime 不得：

自动“修复” Contract。

Runtime State：

`SUSPENDED`

Suspension Reason：

`CONTRACT_VIOLATION`

如果 Contract 本身无法继续被正确解释：

Suspension Reason：

`UNSUPPORTED_RUNTIME_CONDITION`

---

# 55. Context Conflict Handling

发生 Context Conflict 时：

Runtime 必须：

1. 停止当前依赖冲突事实的执行；
2. 保留 Conflict Reference；
3. 重新读取 Authority Context；
4. 不采用非权威信息覆盖 Context；
5. 判断是否触发 Context Integrity Gate；
6. 在仍无法确定时请求 Maker Clarification。

Runtime State：

`SUSPENDED`

Suspension Reason：

`CONTEXT_CONFLICT`

---

# 56. Invalid Workflow State Handling

如果：

Runtime 读取的 `PROJECT_STATE.md`

与 Workflow Contract 无法形成合法 Current Phase Reference：

Runtime 不得：

自动选择一个 Phase。

Runtime State：

`SUSPENDED`

Suspension Reason：

`INVALID_WORKFLOW_STATE`

如果高影响操作正在等待：

必须同时处理：

Context Integrity Gate。

---

# 57. Gate Block Handling

如果任一必要 Gate Result 为：

- `REQUIREMENT_UNSATISFIED`；
- `ACTION_BLOCKED`；

Runtime State：

`BLOCKED_BY_GATE`

Runtime Result 必须明确：

- Gate ID；
- Risk Object；
- Requested Action；
- Unsatisfied Requirement；
- Blocked Action Reference。

Runtime 不得：

绕过 Gate 继续执行。

---

# 58. Missing Authorization Handling

如果：

Gate 或 Context Access Contract

返回：

Authorization Required，

Runtime State：

`WAITING_FOR_MAKER`

必须保留：

- Pending Requirement；
- Gate / Context Reference；
- Risk Object；
- Requested Action；
- Authorization Scope。

Runtime 不得：

自行继续执行。

---

# 59. Unsupported Runtime Condition

如果运行过程中出现：

当前所有上游冻结文档均未定义如何合法处理的情况，

Runtime：

不得自行创造新规则。

Runtime State：

`SUSPENDED`

Suspension Reason：

`UNSUPPORTED_RUNTIME_CONDITION`

Runtime Result 必须明确：

缺少哪一个上游定义。

---

# 60. Runtime Resume Model

以下状态可以通过新的 Runtime Execution 恢复：

- `WAITING_FOR_MAKER`；
- `BLOCKED_BY_GATE`；
- `SUSPENDED`；
- `FAILED`。

恢复时：

Runtime 必须重新读取：

- Current Context；
- Current Workflow State；
- Relevant Gate Definition；
- Previous Evidence Validity；
- Maker Authorization Validity。

Runtime 不得：

假定前一次执行时的所有事实仍然有效。

---

# 61. Runtime Execution Record

Runtime 可以在执行期间维护：

Runtime Execution Record。

逻辑内容至少包括：

- Execution Reference；
- Runtime Request Reference；
- Runtime Execution State；
- Current Phase Reference；
- Pending Context Access Reference；
- Pending Gate Invocation Reference；
- Pending Script Invocation Reference；
- Required Maker Input；
- Suspension / Failure Reason；
- Upstream Result Reference。

Runtime Execution Record：

不是 Project State Source of Truth。

其具体存储位置：

由 Implementation Layer 定义。

---

# 62. Runtime Result Model

每一次 Runtime Execution 结束当前处理时：

必须形成 Runtime Result。

Runtime Result 必须能够回答：

- Runtime 当前是什么状态；
- 为什么是该状态；
- 当前合法 Current Phase 是什么；
- 哪些 Workflow Requirement 已满足；
- 哪些 Requirement 尚未满足；
- 是否存在 Gate Block；
- 是否等待 Maker；
- 是否存在 Script Error；
- 是否发生 Context Mutation；
- 当前 Requested Action 是否已执行；
- 下一步允许做什么。

---

# 63. Runtime Completion Rule

Runtime 只有在：

当前 Runtime Request 的全部允许执行目标均已经完成

且不存在：

- Pending Gate；
- Pending Authorization；
- Required Context Mutation；
- Required Script Execution；
- Required Runtime Operation

时：

才可以返回：

`COMPLETED`

COMPLETED：

不得因为：

“已经给出建议”

自动产生。

---

# 64. Runtime Boundary

Runtime 不重新定义：

## Workflow

- Core Phase；
- Phase Goal；
- Required Artifact；
- Artifact Flow；
- Allowed Next Phase。

## Gate

- Gate Type；
- Gate Trigger；
- Gate Risk Object；
- Gate Evaluation Requirement；
- Required Authorization。

## Context

- Context Type；
- Context Responsibility；
- Context Authority；
- Context Source of Truth。

## Advisory

- Advisory Trigger Type；
- Advisory Content Type；
- Advisory Response Model。

## Contract

- Workflow Contract Result；
- Gate Evaluation Result；
- Context Access Result；
- Script Execution Status；
- Script Validation Result。

---

# 65. Implementation Boundary

本文档不定义：

- Codex Task ID；
- Implementation Order；
- Runtime 文件路径；
- Runtime 类名；
- Runtime 函数名；
- Script 源代码；
- Python / Shell 代码；
- Template 文件内容；
- Test 文件内容。

上述内容属于：

`PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md`

以及后续实际实现。

---

# 66. Source of Truth Rule

Project Incubator V1 Runtime 必须遵循：

```text
Architecture
    ↓
Design
    ↓
Contract
    ↓
Runtime
    ↓
Implementation
```

Runtime：

只能执行上游规则。

Runtime 不能：

向上修改规则。

---

# 67. Runtime Decision Traceability

任何 Runtime 决策必须能够追溯到以下至少一个来源：

- Workflow Contract；
- Context Access Contract；
- Gate Contract；
- Script Contract；
- 对应 Domain Design；
- Maker 提供的合法 Authorization / Decision / Clarification。

如果无法追溯：

Runtime 不得执行该决定。

---

# 68. Core Runtime Execution Flow

Project Incubator V1 Runtime 的完整核心流程固定为：

```text
Runtime Request
        ↓
Resolve Contracts
        ↓
Resolve Domain Definitions
        ↓
Establish / Restore Context
        ↓
Resolve Current Phase
        ↓
Validate Requested Action
        ↓
Prepare Phase / Operation Input
        ↓
Receive Phase Result
        ↓
Check Required Artifact
        ↓
Prepare State Change Requirement
        ↓
Detect Gate Requirement
        ↓
Collect Existing Evidence
        ↓
Invoke Script if deterministic evidence is needed
        ↓
Collect Judgment Evidence if required
        ↓
Invoke Gate
        ↓
┌─────────────────────────────────────────────┐
│ Gate Result                                 │
│                                             │
│ REQUIREMENT_SATISFIED → Continue            │
│ REQUIREMENT_UNSATISFIED → BLOCKED_BY_GATE   │
│ AUTHORIZATION_REQUIRED → WAITING_FOR_MAKER  │
│ EVIDENCE_INSUFFICIENT → SUSPENDED           │
│ ACTION_BLOCKED → BLOCKED_BY_GATE             │
└─────────────────────────────────────────────┘
        ↓
Prepare Context Mutation
        ↓
Context Access Contract
        ↓
┌──────────────────────────────────────────────┐
│ Context Access Result                        │
│                                              │
│ ACCEPTED → Continue                          │
│ REJECTED → SUSPENDED                         │
│ AUTHORIZATION_REQUIRED → WAITING_FOR_MAKER   │
│ GATE_REQUIREMENT_UNRESOLVED → Gate Flow      │
│ BOUNDARY_VIOLATION → SUSPENDED               │
│ CONTEXT_CONFLICT → SUSPENDED                 │
└──────────────────────────────────────────────┘
        ↓
Evaluate Workflow Transition
        ↓
┌─────────────────────────────────────────────┐
│ Workflow Result                             │
│                                             │
│ NOT_READY → SUSPENDED                       │
│ TRANSITION_NOT_ALLOWED → SUSPENDED          │
│ READY_FOR_TRANSITION → Continue             │
└─────────────────────────────────────────────┘
        ↓
Execute Authorized Context Mutation
        ↓
Commit PROJECT_STATE Last
        ↓
Verify Persisted State
        ↓
Form Runtime Result
        ↓
COMPLETED
```

---

# 69. V1 Runtime Invariants

Project Incubator V1 Runtime 必须始终满足以下 Invariant。

## Invariant 1

`PROJECT_STATE.md`

始终是项目当前实际状态唯一 Source of Truth。

Runtime State：

不得替代它。

---

## Invariant 2

Runtime 不替 Maker 做 Decision。

---

## Invariant 3

Runtime 不替 Agent 完成创造性工作。

---

## Invariant 4

Runtime 不新增 Workflow Transition。

---

## Invariant 5

Runtime 不新增 Gate Type。

---

## Invariant 6

Runtime 不修改 Context Authority。

---

## Invariant 7

Script 不获得 Direct Context Access。

---

## Invariant 8

Script Validation Result：

不等于 Gate Evaluation Result。

---

## Invariant 9

Gate Result：

不直接修改 Workflow、Context 或 Artifact。

---

## Invariant 10

Advisory：

不直接产生 Runtime Command。

---

## Invariant 11

State Change Requirement：

不等于 `PROJECT_STATE.md` 已经修改。

---

## Invariant 12

`READY_FOR_TRANSITION`

不等于 Transition 已经执行。

---

## Invariant 13

只有所有相关 Gate Result 均为：

`REQUIREMENT_SATISFIED`

时，

对应受保护 Action 才不再被 Gate 阻止。

---

## Invariant 14

Context Mutation：

必须经过 Context Access Contract。

---

## Invariant 15

Phase Transition：

只有对应 `PROJECT_STATE.md` Mutation 成功持久化并验证后才视为完成。

---

## Invariant 16

Runtime 遇到上游未定义情况：

必须停止推导，

不得自行创造规则。

---

# 70. V1 Runtime Summary

Project Incubator V1 Runtime 采用：

```text
Agent / Maker
      ↓
Runtime Request
      ↓
Runtime Coordinator
      ↓
┌─────────────────────────────┐
│ Workflow Coordinator        │
│ Context Coordinator         │
│ Gate Coordinator            │
│ Script Coordinator          │
│ Advisory Bridge             │
└─────────────────────────────┘
      ↓
Frozen Contracts
      ↓
Controlled Execution
      ↓
Runtime Result
```

核心原则：

1. Runtime 是确定性执行层。

2. Runtime 协调 Workflow、Context、Gate 和 Script。

3. Runtime 不拥有 Domain Authority。

4. Runtime 不拥有 Maker Decision Authority。

5. Runtime Execution State 只描述当前执行，不替代 Project State。

6. `PROJECT_STATE.md` 是 Current Project State 唯一 Source of Truth。

7. Runtime 通过 Context Access Contract 读取和修改 Context。

8. Runtime 是满足 Contract 后 Context Persisted Mutation 的执行者。

9. Workflow State Change Requirement 不等于 State 已经更新。

10. Workflow `READY_FOR_TRANSITION` 只表示 Transition Eligibility。

11. Transition 只有在 `PROJECT_STATE.md` 成功写入目标 Current Phase 后才完成。

12. Runtime 根据 Gate Definition 检测已有 Trigger，不创建新 Trigger。

13. Gate `AUTHORIZATION_REQUIRED` 进入 `WAITING_FOR_MAKER`。

14. Gate `REQUIREMENT_UNSATISFIED` 与 `ACTION_BLOCKED` 进入 `BLOCKED_BY_GATE`。

15. Gate `EVIDENCE_INSUFFICIENT` 进入 `SUSPENDED`。

16. Script 只承担确定性能力。

17. Script `EXECUTION_ERROR` 属于执行失败。

18. Script `REQUIREMENT_UNSATISFIED` 属于 Validation Failure，不属于 Script Error。

19. Judgment-Based Gate 不由 Script 自动判断。

20. Mixed Gate 中 Script 只承担确定性部分。

21. Advisory 只为 Agent 提供指导。

22. Advisory Recommendation 必须重新进入正常 Runtime Request 才能执行。

23. Runtime 不执行自动 Script Retry。

24. Runtime 不使用非权威信息覆盖 Context Source of Truth。

25. Runtime 遇到未定义 Runtime Condition 时必须暂停，而不是自行补设计。

26. Runtime 的所有执行决定必须能够追溯到 Design、Contract 或 Maker 的合法输入。

27. 本 Runtime Specification 是：

`PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md`

定义实际实现任务的 Runtime Source of Truth。