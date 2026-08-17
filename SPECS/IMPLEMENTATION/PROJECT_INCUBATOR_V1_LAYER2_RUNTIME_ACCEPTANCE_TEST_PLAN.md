
# Project Incubator V1 Layer 2 Runtime Acceptance Test Plan

## 1. Document Purpose

本文档定义 Project Incubator V1 的 Layer 2 Runtime Acceptance Test。

Layer 2 Test 位于：

```text
Implementation
    ↓
Component Implementation
    ↓
Layer 2 Runtime Acceptance
    ↓
Codex Automated Verification
    ↓
Final Maker Acceptance
```

本文件不属于新的 Architecture、Design、Contract 或 Runtime Definition。

本文件不修改：

- `PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md`；
- TASK-001 ～ TASK-027；
- Task Dependency；
- Task Execution Order；
- Implementation Completion Criteria；
- Frozen Architecture；
- Frozen Design；
- Frozen Contract；
- Frozen Runtime Specification。

本文件仅定义：

**在现有 Implementation Task 推进过程中，Maker 如何分阶段人工验证已经完成的 Runtime 能力。**

---

# 2. Layer 2 Test Boundary

Layer 2 不验证：

```text
Maker Natural Language
        ↓
Agent Understanding
        ↓
Agent Reasoning
        ↓
Intent Resolution
```

Layer 2 从以下边界开始：

```text
假设 Agent 已正确理解 Maker Intent
        ↓
构造已经解析完成的结构化输入
        ↓
Runtime Component / Runtime Coordinator
        ↓
Workflow
        ↓
Context
        ↓
Script
        ↓
Gate
        ↓
Mutation
        ↓
Runtime Result
```

因此：

Layer 2 Test 不用于判断 Agent 是否正确理解自然语言。

测试时允许直接构造：

- Runtime 所需要的结构化输入；
- Component Input；
- Contract Input；
- Script Invocation Input；
- Gate Evidence；
- Maker Authorization；
- Context Fixture；
- Workflow State。

不得通过 Agent 自主推理补充测试输入。

如果测试需要某项输入，而现有 Contract / Runtime Interface 没有定义：

不得自行发明新的 Runtime Field 或 Interface。

必须标记：

```text
TEST_BLOCKED
```

并指出：

- 缺失的可调用入口；
- 对应 Component；
- 对应 Implementation Task；
- 是否属于实现缺陷或 Upstream Design Gap。

---

# 3. Relationship with Implementation Plan

Layer 2 Acceptance 不改变 Implementation Task。

它只在指定 Task 完成后启动对应 Test Stage。

执行关系：

```text
TASK-011 ～ TASK-015 完成
        ↓
Stage A
Runtime Foundation Acceptance

TASK-016 ～ TASK-020 完成
        ↓
Stage B
Deterministic Capability Acceptance

TASK-021 ～ TASK-023 完成
        ↓
Stage C
Gate / Advisory / Runtime Result Acceptance

TASK-024 完成
        ↓
Stage D
Runtime Orchestration Acceptance

TASK-025 ～ TASK-027 完成
        ↓
Stage E
Layer 2 Final Regression / Package Isolation Acceptance
```

Stage E 完成后：

Layer 2 Test 结束。

真实 Maker Natural Language → Agent → Runtime 的完整产品验收：

不属于本文档。

该部分由 Final Maker Acceptance 单独执行。

---

# 4. Current Implementation Position

当前 Implementation Progress：

```text
TASK-015 = COMPLETED
```

因此当前允许执行：

```text
Stage A — Runtime Foundation Acceptance
```

当前不得提前执行：

```text
Stage B
Stage C
Stage D
Stage E
```

因为对应 Implementation Component 尚未全部完成。

---

# 5. Test Responsibility

## 5.1 Maker

Maker 是 Layer 2 Acceptance 的最终验收者。

Maker 负责：

- 决定何时开始一个 Test Stage；
- 确认 Test Input；
- 决定是否执行 Test Case；
- 查看实际输出；
- 查看真实文件变化；
- 判断实际行为是否符合预期；
- 对 Test Case 给出 ACCEPT / REJECT；
- 对整个 Test Stage 给出 ACCEPT / REJECT。

Codex 不得替 Maker 给出最终 Acceptance Decision。

---

## 5.2 Codex

Codex 在 Layer 2 Test 中是：

```text
Test Operator
+
Test Fixture Builder
+
Evidence Collector
```

不是：

```text
Product Acceptance Authority
```

Codex 负责：

- 阅读当前实现；
- 阅读对应冻结 Contract / Runtime Specification；
- 根据 Test Case 准备准确输入；
- 根据当前真实函数 / Class Interface 生成可执行命令；
- 建立隔离 Test Fixture；
- 执行 Maker 已授权的 Test Case；
- 原样报告关键输出；
- 报告文件变化；
- 清理临时 Fixture；
- 定位失败涉及的 Implementation Task。

Codex 不得：

- 因测试失败直接修改代码；
- 为使测试通过修改预期结果；
- 修改冻结 Definition；
- 自动执行下一个 Test Case；
- 自动执行下一个 Test Stage；
- 自动宣布 Stage ACCEPTED。

---

# 6. Test Execution Safety

所有 Layer 2 Test 默认使用：

```text
Temporary Test Workspace
```

不得直接破坏：

```text
PROJECT_INCUBATOR/references/
PROJECT_INCUBATOR/templates/
真实 Managed Project
当前 Implementation Source Files
```

需要测试：

- Missing Reference；
- Invalid Definition；
- Invalid Context；
- Corrupted Artifact；
- Git Repository；
- File Persistence Failure

时：

必须创建隔离副本或临时目录。

不得为了制造 Failure Case：

直接删除或修改正式实现文件。

测试完成后必须清理临时 Test Fixture。

Layer 2 Test 默认不得产生 Repository Source Change。

如果测试必须修改 Repository Source File 才能执行：

停止测试并报告：

```text
TEST_BLOCKED
```

等待 Maker 决定。

---

# 7. Test Input Construction Rule

本文档描述的是：

```text
Semantic Test Input
```

而不是重新定义 Runtime Schema。

每个 Test Case 执行前，Codex 必须根据当前真实实现确定：

- 实际 Class；
- 实际 Function；
- 实际 Method；
- 实际 Dataclass；
- 实际 Enum；
- 实际 Payload Structure；
- 实际 Constructor；
- 实际可调用入口。

不得因为本文档没有写 Python 参数名而自行建立新的 Runtime Interface。

如果当前真实实现已经提供调用接口：

使用当前接口。

如果没有：

报告：

```text
TEST_BLOCKED
Reason: no callable implementation path
```

不得为了测试方便修改 Product Interface。

---

# 8. Maker Execution Protocol

每个 Test Case 使用两步执行。

## Step 1 — Prepare

Maker：

```text
准备 <Test Case ID>，不要执行。
```

Codex必须返回：

```text
Test Case:
Target:
Precondition:

Semantic Input:

Actual Runtime Entry:

Exact Command:

Expected Output:

Expected File Change:

Cleanup:

Source Basis:
```

Maker检查后决定是否执行。

---

## Step 2 — Execute

Maker可以选择：

### Mode A — Maker Manual Execution

Maker自己执行 Codex 给出的命令。

然后将输出交给 Codex分析。

这是 Layer 2 首选模式。

### Mode B — Maker Authorized Codex Execution

Maker明确发送：

```text
执行 <Test Case ID>
```

Codex只允许执行当前一个 Test Case。

完成后立即停止。

不得自动执行下一个 Case。

---

# 9. Stage A — Runtime Foundation Acceptance

## Execution Point

允许执行时间：

```text
TASK-011 ～ TASK-015 全部 COMPLETED
```

当前项目已经达到此条件。

Stage A 覆盖：

```text
TASK-011 Contract / Runtime Types
TASK-012 Definition Resolver
TASK-013 File Store
TASK-014 Context Coordinator
TASK-015 Workflow Coordinator
```

Stage A 不测试：

- Script Runner；
- Gate Coordinator；
- Advisory Bridge；
- Runtime Coordinator；
- Full Runtime Lifecycle。

---

## L2-A01 — Contract Type Integrity

### Target

```text
runtime/core/contracts.py
runtime/core/runtime_types.py
```

### Input Construction

直接 import 当前实现中的：

```text
Context Access Result
Workflow Result
Gate Evaluation Result
Script Execution Status
Script Validation Result
Runtime State
```

### Expected Output

必须精确存在冻结值：

```text
Context Access Result
ACCEPTED
REJECTED
AUTHORIZATION_REQUIRED
GATE_REQUIREMENT_UNRESOLVED
BOUNDARY_VIOLATION
CONTEXT_CONFLICT

Workflow Result
NOT_READY
READY_FOR_TRANSITION
TRANSITION_NOT_ALLOWED

Gate Evaluation Result
REQUIREMENT_SATISFIED
REQUIREMENT_UNSATISFIED
AUTHORIZATION_REQUIRED
EVIDENCE_INSUFFICIENT
ACTION_BLOCKED

Script Execution Status
COMPLETED
INVALID_INPUT
UNSUPPORTED_INVOCATION
EXECUTION_ERROR

Script Validation Result
REQUIREMENT_SATISFIED
REQUIREMENT_UNSATISFIED
VALIDATION_NOT_COMPLETED

Runtime State
EXECUTING
WAITING_FOR_MAKER
BLOCKED_BY_GATE
SUSPENDED
FAILED
COMPLETED
```

不得出现额外值。

同时确认：

```text
Script Validation Result
≠
Gate Evaluation Result
```

它们必须是两个独立类型。

### Maker Acceptance

Maker确认：

```text
ACCEPT L2-A01
```

或：

```text
REJECT L2-A01
```

---

## L2-A02 — Frozen Definition Loading

### Target

```text
runtime/config.json
runtime/components/definition_resolver.py
```

### Input Construction

使用正常 Skill Package。

不修改 Reference。

调用 Definition Resolver 的正常 Resolution Entry。

### Expected Output

必须得到：

```text
Runtime State = COMPLETED
```

并形成完整 Frozen Definition Set，至少包括：

```text
Workflow Definition
Gate Definition
Context Definition
Advisory Definition
Runtime Contract Types
```

每个 JSON Definition：

```text
实际 definition_id
=
config.json 中 expected definition identity
```

---

## L2-A03 — Missing Required Reference

### Input Construction

创建 Skill Package 临时副本。

只在临时副本中：

让一个 Required Reference 不存在。

不得修改正式：

```text
PROJECT_INCUBATOR/references/
```

### Expected Output

```text
Runtime State = FAILED
Failure Reason = RUNTIME_DEPENDENCY_FAILURE
```

并明确指出 Missing Requirement。

不得：

- 自动创建缺失 Reference；
- 使用默认 Definition；
- 从 SPECS 推导 Definition；
- 猜测缺失内容。

---

## L2-A04 — Definition Identity Mismatch

### Input Construction

在临时 Fixture 中：

保持 Reference 文件存在，

但让：

```text
actual definition_id
≠
expected definition identity
```

### Expected Output

Definition Resolution 必须失败。

必须形成：

```text
Runtime State = FAILED
Failure Reason = RUNTIME_DEPENDENCY_FAILURE
```

不得继续加载错误 Definition。

---

## L2-A05 — File Store Read / Write / Verification

### Target

```text
runtime/adapters/file_store.py
```

### Input Construction

创建临时目录与临时文件。

依次执行：

```text
Exists
Write
Read
Atomic Write
Read-back Verification
Append
Read
```

### Expected Output

必须满足：

```text
Write 后实际文件存在
Read 与写入内容一致
Atomic Write 后内容完整
Read-back Verification 成功
Append 不覆盖已有内容
最终内容与预期完全一致
```

File Store 不得：

- 判断 Maker Authorization；
- 判断 Gate；
- 决定 Context Mutation 是否应该执行。

---

## L2-A06 — Context Legal Read

### Target

```text
runtime/components/context_coordinator.py
```

### Input Construction

建立 Temporary Managed Project。

按照现有 Template 建立合法 Core Context Fixture。

构造合法：

```text
READ
```

请求。

### Expected Output

必须获得符合 Context Access Contract 的成功结果。

读取内容必须来自目标 Context File。

不得：

- 使用历史聊天；
- 使用 Agent Memory；
- 使用 Runtime State 替代 PROJECT_STATE。

---

## L2-A07 — Agent Direct Write Boundary

### Input Construction

构造：

```text
Actor = Agent
Operation = Direct Persisted Write
```

尝试绕过 Context Coordinator 的合法 Mutation Flow。

### Expected Output

必须：

```text
不允许产生 Persisted Mutation
```

返回值必须属于冻结 Context Access Contract。

不得返回：

```text
ACCEPTED
```

Codex在执行前的 Run Sheet 中：

必须根据冻结 Context Access Contract 标出本实现应返回的**精确 Result Enum**。

不得在测试时自行推测。

---

## L2-A08 — Script Direct Context Read Boundary

### Input Construction

模拟：

```text
Actor = Script
Request = Direct Core Context Read
```

### Expected Output

Script Direct Context Read 必须被拒绝。

Core Context 内容不得直接提供给 Script。

精确 Result Enum：

必须由 Codex在执行前从冻结 Context Access Contract 中确认。

---

## L2-A09 — PROFILE Mutation Without Maker Authorization

### Input Construction

建立合法 PROJECT_PROFILE。

构造影响 PROFILE Authority 的 Mutation Request。

不提供 Maker Authorization。

### Expected Output

Mutation 不得持久化。

必须形成：

```text
AUTHORIZATION_REQUIRED
```

或冻结 Contract 对该具体请求定义的对应结果。

Codex执行前必须给出 Contract Trace。

---

## L2-A10 — DECISIONS Append Without Maker Confirmation

### Input Construction

建立 PROJECT_DECISIONS。

构造新的 Decision Append Request。

不提供 Maker Confirmation。

### Expected Output

不得向：

```text
PROJECT_DECISIONS.md
```

写入新 Decision。

历史内容保持不变。

---

## L2-A11 — Optional Context Authority Boundary

### Input Construction

构造：

```text
Core Context
+
Optional Context
```

使 Optional Context 中存在与 Core Context Authority 冲突的数据。

### Expected Output

Optional Context 不得覆盖 Core Context Authority。

尤其不得覆盖：

```text
PROJECT_STATE
```

作为 Current Project State Source of Truth。

---

## L2-A12 — Legal Workflow Transition Matrix

### Target

```text
runtime/components/workflow_coordinator.py
```

### Input Construction

直接构造满足 Workflow Evaluation 所需条件的 Transition Request。

逐项验证：

```text
P0 → P1
P1 → P2
P2 → P3
P3 → P4
P4 → P5
P5 → P6
P6 → P2
P6 → P3
P6 → P4
P6 → P5
```

### Expected Output

在其余 Workflow Requirement 均满足时：

```text
READY_FOR_TRANSITION
```

注意：

```text
READY_FOR_TRANSITION
≠
Transition 已经执行
```

Stage A 不执行完整 Runtime Transition Commit。

---

## L2-A13 — Illegal Workflow Transition

至少验证：

```text
P0 → P2
P1 → P3
P5 → P4
P6 → P0
P6 → P1
P6 → P6
```

### Expected Output

```text
TRANSITION_NOT_ALLOWED
```

不得：

- 自动修正目标 Phase；
- 自动选择其他 Phase；
- 修改 Allowed Transition。

---

## Stage A Acceptance Criteria

全部 A01 ～ A13：

```text
PASS
```

后：

Maker 才可以给出：

```text
STAGE A ACCEPTED
```

如果任一 Case FAIL：

```text
STAGE A REJECTED
```

Codex必须定位对应：

```text
TASK-011 ～ TASK-015
```

中的实现责任。

不得直接修复。

等待 Maker发出修复指令。

---

# 10. Stage B — Deterministic Capability Acceptance

## Execution Point

允许执行时间：

```text
TASK-016 ～ TASK-020 全部 COMPLETED
```

覆盖：

```text
validate_contract_payload.py
inspect_git_evidence.py
validate_artifact_evidence.py
validate_context_integrity_evidence.py
script_runner.py
script_coordinator.py
```

Stage B 必须实际覆盖所有四个 Script。

---

## L2-B01 — Contract Payload Validator

### Input Cases

至少构造：

```text
Valid Payload

Missing Invocation ID

Invalid Enum

Empty Required Value

Unsupported Contract Type

Invalid Input
```

### Expected Output

合法 Requirement：

```text
COMPLETED
+
REQUIREMENT_SATISFIED
```

明确 Contract Requirement 不满足：

```text
COMPLETED
+
REQUIREMENT_UNSATISFIED
```

输入无法解析：

```text
INVALID_INPUT
```

Unsupported Contract Type：

```text
UNSUPPORTED_INVOCATION
```

---

## L2-B02 — Git Evidence Script

### Input Fixture

使用临时 Git Repository。

依次构造：

```text
Clean Repository

Modified Repository

Untracked File

Staged Change

Invalid Repository Path / Non-Git Directory
```

### Expected Output

合法 Git Repository：

返回真实：

```text
Current Branch
Working Tree Change Presence
Untracked Change Presence
Staged Change Presence
Relevant Git Evidence
```

非 Git Repository：

不得伪造 Evidence。

必须返回符合 Script Contract 的：

```text
Script Error
/
VALIDATION_NOT_COMPLETED
```

具体状态按照当前 Script Contract 与实现确定。

Script不得决定：

```text
是否允许 push
是否批准 merge
是否允许删除 branch
```

---

## L2-B03 — Artifact Evidence Script

### Input Cases

临时构造：

```text
File Missing
Empty Artifact
Existing Non-empty Artifact
Unreadable Artifact
```

### Expected Output

必须能够区分：

```text
Artifact Exists
Artifact Readable
Artifact Non-empty
Declared Artifact Identity
Evidence
```

Requirement 不满足：

```text
REQUIREMENT_UNSATISFIED
```

输入本身无效：

```text
INVALID_INPUT
```

无法访问：

```text
EXECUTION_ERROR
/
VALIDATION_NOT_COMPLETED
```

Script不得判断：

```text
Artifact 创意质量
Artifact 是否“足够好”
Intent 是否在价值层面满足
```

---

## L2-B04 — Context Integrity Evidence Script

### Input Cases

直接向 Script 提供：

```text
Required Context Type Set
Context-derived Data
Declared Context Identity
Required Structural Item
```

不得让 Script 自行读取 Core Context。

至少验证：

```text
All Core Context Present

Missing PROJECT_STATE

Context Identity Mismatch

Required Structural Item Missing

Insufficient Input
```

### Expected Output

能够返回：

```text
Required Context Presence
Missing Context
Required Structural Item Presence
Identity Conflict Evidence
Validation Result
```

无法确定时：

```text
VALIDATION_NOT_COMPLETED
```

不得猜测。

---

## L2-B05 — Script Runner / Coordinator Mapping

通过 Script Coordinator 调用前述 Script。

不是直接调用 Script 文件。

必须验证：

```text
COMPLETED + REQUIREMENT_SATISFIED
→ Evidence 正常返回

COMPLETED + REQUIREMENT_UNSATISFIED
→ VALIDATION_UNSATISFIED

INVALID_INPUT
→ INVALID_SCRIPT_INPUT

UNSUPPORTED_INVOCATION
→ UNSUPPORTED_SCRIPT_INVOCATION

EXECUTION_ERROR
→ SCRIPT_EXECUTION_ERROR
```

## B5-06 Pure DETERMINISTIC_OPERATION

### Input

构造：

```text
Invocation Purpose = DETERMINISTIC_OPERATION
Validation Requirement = empty
Execution Status = COMPLETED
Validation Result = empty
```

### Expected Result

必须满足：

- Script Invocation 正常完成；
- Validation Result 保持为空；
- Runtime Script Layer 可以继续后续 Runtime Flow；
- 不得生成 VALIDATION_NOT_COMPLETED；
- 不得仅因为 Validation Result 为空进入 SUSPENDED；
- 不得生成 REQUIREMENT_SATISFIED；
- 不得生成 REQUIREMENT_UNSATISFIED；
- Script Output 与已有 Evidence 必须保留。

本 Scenario 只验证 Script Runtime Layer 的正常完成与 Continue 语义。

不得把它解释为：

完整 Runtime Execution 已经最终 COMPLETED。

同时验证：

```text
默认无 Automatic Retry
```

以及：

Script不得：

```text
Direct Read Context
Execute Workflow Transition
Modify Context
Approve Gate
```

---

## Stage B Acceptance Criteria

必须满足：

```text
四个 Script 均至少完成一个 Success Case
四个 Script 均完成规定 Failure / Unsatisfied Case
Script Coordinator Mapping 全部正确
没有 Script 获得 Context Authority
没有 Script 获得 Workflow Authority
没有 Script 获得 Gate Authority
```

Maker最终决定：

```text
STAGE B ACCEPTED
```

或：

```text
STAGE B REJECTED
```

---

# 11. Stage C — Gate / Advisory / Runtime Result Acceptance

## Execution Point

允许执行时间：

```text
TASK-021 ～ TASK-023 全部 COMPLETED
```

覆盖：

```text
gate_coordinator.py
advisory_bridge.py
result_coordinator.py
```

---

## L2-C01 — Gate Definition Resolution

### Input Construction

从 Gate Reference 获取全部 Gate ID。

逐一让 Gate Coordinator Resolve Definition。

### Expected Output

必须能够识别全部 15 个 Gate。

不得：

- 创建第 16 个 Gate；
- 删除 Gate；
- 修改 Required Authorization；
- 修改 Evaluation Nature。

---

## L2-C02 — Gate Result Mapping

分别构造能够形成以下 Gate Result 的输入：

```text
REQUIREMENT_SATISFIED
REQUIREMENT_UNSATISFIED
AUTHORIZATION_REQUIRED
EVIDENCE_INSUFFICIENT
ACTION_BLOCKED
```

### Expected Output

```text
REQUIREMENT_SATISFIED
→ 允许继续后续 Contract 检查

REQUIREMENT_UNSATISFIED
→ BLOCKED_BY_GATE

AUTHORIZATION_REQUIRED
→ WAITING_FOR_MAKER

EVIDENCE_INSUFFICIENT
→ SUSPENDED

ACTION_BLOCKED
→ BLOCKED_BY_GATE
```

---

## L2-C03 — Maker Authorization

### Input 1

触发需要 Maker Authorization 的 Gate。

不提供 Authorization。

### Expected

```text
AUTHORIZATION_REQUIRED
→ WAITING_FOR_MAKER
```

Runtime / Agent / Script 不得自动补充 Authorization。

### Input 2

Maker明确提供有效 Authorization。

### Expected

执行：

```text
Gate Re-evaluation
```

不得因为之前等待过就自动视为满足。

---

## L2-C04 — Multiple Gate Independence

### Input Construction

同一个 Requested Action 同时触发至少两个 Gate。

构造：

```text
Gate A = REQUIREMENT_SATISFIED
Gate B = REQUIREMENT_UNSATISFIED
```

### Expected Output

整体 Protected Action：

不得继续。

不得因为：

```text
Gate A satisfied
```

而忽略：

```text
Gate B unsatisfied
```

所有触发 Gate 必须独立满足。

---

## L2-C05 — Script Evidence Is Not Gate Result

### Input Construction

提供：

```text
Script Validation Result
=
REQUIREMENT_SATISFIED
```

同时让完整 Gate Requirement 仍需要额外 Judgment 或 Authorization。

### Expected Output

Script Result只能成为：

```text
Validation Evidence
```

不得直接成为：

```text
Gate Evaluation Result
```

---

## L2-C06 — Advisory Trigger Coverage

逐项构造：

```text
Phase Entry
Maker Guidance Request
Missing Information
Risk Detected
Decision Required
Validation Feedback
Iteration Re-entry
```

### Expected Output

Advisory Bridge 必须能够准备相应：

```text
Current Phase
Project Context
Relevant Artifact
Validation Result
Risk
Missing Information
```

按照实际 Trigger 所需提供。

---

## L2-C07 — Advisory Boundary

构造一个 Advisory Response：

其中包含：

```text
Recommended Action
```

### Expected Output

Advisory Response 本身不得：

- 修改 Runtime State；
- 修改 Context；
- 修改 Workflow；
- 执行 Transition；
- 产生 Gate Result；
- 直接执行 Recommended Action。

Recommended Action 如需执行：

必须转化成：

```text
新的 Runtime Request
```

---

## L2-C08 — Runtime Result Coverage

分别构造：

```text
EXECUTING
WAITING_FOR_MAKER
BLOCKED_BY_GATE
SUSPENDED
FAILED
COMPLETED
```

### Expected Output

每一种 Runtime State 均能形成合法 Runtime Result。

Runtime Result 必须能够承载：

```text
Execution Reference
Runtime Execution State
Runtime Reason
Current Phase Reference
Workflow Result Reference
Context Access Result Reference
Gate Output Reference
Script Output Reference
Pending Requirement
Required Maker Input
Completed Action Reference
Next Allowed Action
```

Result Coordinator 不得重新解释 Contract Result。

---

# 12. Stage D — Runtime Orchestration Acceptance

## Execution Point

允许执行时间：

```text
TASK-024 = COMPLETED
```

Stage D 是 Layer 2 的核心。

此时不再逐个调用 Component。

Maker假设：

```text
Agent 已经正确解析 Maker Intent
```

然后直接构造：

```text
Runtime Request
```

交给 Runtime Coordinator。

---

## L2-D01 — Legal Transition

建议第一条使用：

```text
P3 → P4
```

建立 Temporary Managed Project：

```text
PROJECT_PROFILE.md
PROJECT_STATE.md
PROJECT_PLAN.md
PROJECT_DECISIONS.md
```

使：

```text
Current Phase = P3
```

并构造所有必要 Workflow / Artifact / Gate 条件满足。

### Expected Flow

必须真实经过：

```text
Runtime Request
↓
Resolve Contracts / Definitions
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
Collect Evidence
↓
Invoke Script when required
↓
Invoke Gate
↓
Handle Maker Requirement
↓
Prepare Context Mutation
↓
Evaluate Workflow Transition
↓
Execute Authorized Context Mutation
↓
Commit PROJECT_STATE Last
↓
Verify Persisted State
↓
Form Runtime Result
```

### Expected Final State

只有：

```text
PROJECT_STATE.md
```

成功写回并 Read-back Verification 后：

Transition 才能视为完成。

---

## L2-D02 — Illegal Transition

构造：

```text
P0 → P2
```

### Expected Output

Workflow：

```text
TRANSITION_NOT_ALLOWED
```

Runtime：

不得 Commit 新 Phase。

`PROJECT_STATE.md`：

保持原状态。

---

## L2-D03 — Missing Maker Authorization

构造需要 Maker Authorization 的 Requested Action。

不提供 Authorization。

### Expected Output

```text
Runtime State = WAITING_FOR_MAKER
```

不得：

- 自动授权；
- 修改受保护 Context；
- 执行受保护 Action。

---

## L2-D04 — Gate Block

构造：

```text
Gate Result = ACTION_BLOCKED
```

### Expected Output

```text
Runtime State = BLOCKED_BY_GATE
```

受保护 Action 不执行。

PROJECT_STATE 不得被错误推进。

---

## L2-D05 — Context Conflict

构造 Authority Context Conflict。

### Expected Output

```text
Runtime State = SUSPENDED
Reason = CONTEXT_CONFLICT
```

不得自动覆盖 PROJECT_STATE。

---

## L2-D06 — Script Validation Failure

让 Script 正常执行：

```text
Execution Status = COMPLETED
Validation Result = REQUIREMENT_UNSATISFIED
```

### Expected Output

不得表示为：

```text
SCRIPT_EXECUTION_ERROR
```

必须按 Runtime Specification 处理：

```text
VALIDATION_UNSATISFIED
```

对应的 Runtime Suspension / Result 必须符合冻结 Runtime Specification。

---

## L2-D07 — Script Execution Error

让 Script 返回：

```text
EXECUTION_ERROR
```

### Expected Output

```text
Runtime State = FAILED
Failure Reason = SCRIPT_EXECUTION_ERROR
```

不得表示为普通 Validation Failure。

---

## L2-D08 — P6 Iteration Matrix

建立：

```text
Current Phase = P6
```

分别测试：

```text
P6 → P2
P6 → P3
P6 → P4
P6 → P5
```

在对应 Requirement 满足时：

必须允许进入正常 Transition Eligibility。

然后验证非法目标：

```text
P6 → P0
P6 → P1
P6 → P6
```

必须拒绝。

---

## L2-D09 — PROJECT_STATE Commit Last

构造一次实际需要 Context Mutation 的 Transition。

记录：

```text
其他 Context Mutation
PROJECT_STATE Mutation
```

执行顺序。

### Expected Output

`PROJECT_STATE.md` 必须最后 Commit。

只有：

```text
Persist
+
Read-back Verification
```

成功后：

Transition 才能报告完成。

如果当前实现允许在不修改 Product Code 的情况下安全制造 Persistence Failure：

增加 Failure Case。

如果当前 Public Interface 无法安全构造该 Failure：

标记：

```text
TEST_BLOCKED
```

不得为了测试新增 Product Interface。

---

# 13. Stage E — Layer 2 Final Regression and Package Isolation

## Execution Point

允许执行时间：

```text
TASK-025
TASK-026
TASK-027
```

全部完成并通过 Automated Verification 后。

Stage E 仍然不测试：

```text
Maker Natural Language → Agent Understanding
```

---

## L2-E01 — Layer 2 Regression

重新执行：

```text
Stage A Critical Cases
Stage B All Script Cases
Stage C Critical Gate / Authorization Cases
Stage D Runtime Orchestration Cases
```

确认 TASK-025～027 的测试实现没有造成 Runtime Regression。

---

## L2-E02 — Clean Package Isolation

这是发布前必须执行的 Layer 2 Test。

创建全新 Temporary Environment。

只复制：

```text
PROJECT_INCUBATOR/
```

不得复制：

```text
SPECS/
backup/
zzztemp/
Repository Root AGENTS.md
Implementation Prompt
Implementation Plan
其他开发仓库文件
```

在该环境运行 Runtime。

### Expected Output

必须能够：

```text
加载 Runtime Configuration
加载全部 Required Reference
加载 Runtime Contract Types
建立 Context
执行 Workflow
调用 Script
执行 Gate Flow
形成 Runtime Result
```

不得尝试访问：

```text
SPECS/
```

Reference 中：

```text
source_document
```

只允许作为：

```text
Traceability / Provenance Metadata
```

不得成为 Runtime Dependency。

---

## L2-E03 — No Development Repository Dependency

监控 Runtime 实际文件读取路径。

### Expected Output

运行时依赖必须来自发布包本身或 Managed Project：

```text
PROJECT_INCUBATOR/runtime/
PROJECT_INCUBATOR/references/
PROJECT_INCUBATOR/templates/
PROJECT_INCUBATOR/scripts/

<Managed Project>/PROJECT_PROFILE.md
<Managed Project>/PROJECT_STATE.md
<Managed Project>/PROJECT_PLAN.md
<Managed Project>/PROJECT_DECISIONS.md
```

不得依赖：

```text
SPECS/
backup/
zzztemp/
Implementation Repository Root
历史开发文件
```

---

# 14. Failure Handling

Layer 2 Test 失败时：

Codex不得直接修复。

必须输出：

```text
Test Case:

Status: FAILED

Expected:

Actual:

Evidence:

Affected Component:

Likely Implementation Task:

Source Rule:

Repository Source Changed:
NO

Recommended Next Action:
等待 Maker 决定是否重新打开对应 Implementation Task。
```

如果无法执行：

```text
Test Case:

Status: TEST_BLOCKED

Blocking Reason:

Missing Callable Interface:

Affected Component:

Relevant Implementation Task:

Possible Upstream Design Gap:
YES / NO / UNDETERMINED
```

---

# 15. Stage Report

每个 Stage 完成后：

Codex只输出：

```text
Layer 2 Acceptance Stage:

Implementation Range:

Test Cases:

PASS:
- ...

FAIL:
- ...

BLOCKED:
- ...

Repository Source Changes:
NONE

Observed Issues:
- ...

Codex Assessment:
READY_FOR_MAKER_REVIEW
```

不得输出：

```text
STAGE ACCEPTED
```

Acceptance 只能由 Maker给出。

---

# 16. Maker Acceptance Command

Maker接受 Stage：

```text
ACCEPT LAYER2 STAGE A
```

或：

```text
ACCEPT LAYER2 STAGE B
```

拒绝：

```text
REJECT LAYER2 STAGE A

Issues:
- ...
```

Maker Acceptance 不自动启动后续 Implementation Task。

---

# 17. Layer 2 Completion

只有：

```text
Stage A = ACCEPTED
Stage B = ACCEPTED
Stage C = ACCEPTED
Stage D = ACCEPTED
Stage E = ACCEPTED
```

才可以认为：

```text
LAYER 2 RUNTIME ACCEPTANCE = ACCEPTED
```

这只表示：

> 在假设 Agent 已经正确解析 Maker Intent 的条件下，Project Incubator V1 的确定性 Runtime、Workflow、Context、Script、Gate、Advisory 和 Runtime Result 已经通过 Maker 主导的人工运行验收。

它不表示：

```text
Final Product Acceptance = ACCEPTED
```

Final Product Acceptance 仍必须单独验证：

```text
真实 Maker Natural Language
↓
Agent Understanding
↓
Agent Reasoning
↓
Intent Resolution
↓
Runtime
↓
完整 Project Incubator 使用体验
```

---

# 18. Current Required Action

当前 Implementation 已完成：

```text
TASK-015
```

因此当前下一步 Layer 2 Acceptance 是：

```text
Stage A — Runtime Foundation Acceptance
```

建议当前顺序：

```text
暂停进入 TASK-016
↓
执行 L2-A01 ～ L2-A13
↓
Maker Review
↓
STAGE A ACCEPTED
↓
再继续 TASK-016
```

如果 Stage A 出现失败：

先定位并修复 TASK-011 ～ TASK-015 对应问题，

重新执行受影响 Case，

直到 Maker 接受 Stage A。
