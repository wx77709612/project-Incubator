# Project Incubator V1 Implementation Plan

## 1. Document Purpose

本文档定义 Project Incubator V1 的最终实现计划。

本文档属于：

Implementation Layer。

本文档负责：

- Implementation Scope；
- Implementation Dependency；
- Implementation Order；
- Task Breakdown；
- Generated Files；
- Validation Criteria；
- Traceability。

本文档用于直接指导 Codex 实现 Project Incubator V1。

本文档只把已经冻结的：

- Architecture；
- Design；
- Contract；
- Runtime Specification

映射为具体实现任务。

本文档不得重新定义：

- Architecture；
- Workflow Domain Model；
- Gate Domain Model；
- Context Domain Model；
- Advisory Domain Model；
- Context Access Contract；
- Workflow Contract；
- Gate Contract；
- Script Contract；
- Runtime Specification。

如果 Implementation 与上游定义冲突：

以上游文档为准。

---

## 2. Upstream Dependency

Project Incubator V1 实现依赖关系固定为：

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

Implementation 只能实现：

上游已经存在的系统能力。

Implementation 不得反向修改上游定义。

---

## 3. Implementation Scope

### 3.1 V1 必须实现

Project Incubator V1 必须实现以下能力：

#### Skill Package

必须形成：

- `SKILL.md`；
- `README.md`；
- `AGENTS.md`；
- `runtime/`；
- `references/`；
- `templates/`；
- `scripts/`。

#### Workflow Runtime Support

必须支持：

- P0–P6 Core Workflow；
- Current Phase Resolution；
- Phase Input；
- Phase Result；
- Required Artifact Requirement；
- State Change Requirement；
- Gate Trigger Requirement；
- Transition Eligibility；
- P6 Iteration 返回 P2 / P3 / P4 / P5；
- Transition Commit。

#### Context Runtime Support

必须支持：

- `PROJECT_PROFILE.md`；
- `PROJECT_STATE.md`；
- `PROJECT_PLAN.md`；
- `PROJECT_DECISIONS.md`；
- Optional Context 的扩展入口；
- Context Read；
- Context Mutation Request；
- Mutation Authority Check；
- Maker Authorization；
- Runtime-controlled Mutation；
- Persisted Result Verification；
- Context Conflict Handling。

#### Gate Runtime Support

必须支持当前 Gate Design 已定义的 15 个 Gate：

- GATE-GIT；
- GATE-PHASE；
- GATE-AUTHORITY-DOCUMENT；
- GATE-SCOPE；
- GATE-BUILDER；
- GATE-UNCLOSED-TASK；
- GATE-CONTEXT-INTEGRITY；
- GATE-LOCAL-PROTOCOL；
- GATE-ARTIFACT-BOUNDARY；
- GATE-CHALLENGE-RESPONSE；
- GATE-CORRECTION-PERSISTENCE；
- GATE-ARCHITECTURE-DECISION；
- GATE-FRAMEWORK-MODIFICATION；
- GATE-PHASE-MODEL-MODIFICATION；
- GATE-MATRIX-MODIFICATION。

#### Script Runtime Support

必须支持：

- VALIDATION Invocation；
- DETERMINISTIC_OPERATION Invocation；
- Script Input；
- Script Output；
- Execution Status；
- Validation Result；
- Evidence；
- Error Handling。

#### Advisory Support

必须支持：

- Advisory Trigger；
- Advisory Context 准备；
- Advisory Information 提供给 Agent；
- Advisory Response 与 Runtime 的职责隔离。

#### Runtime Execution

必须实现：

- Runtime Request；
- Runtime Lifecycle；
- Runtime Execution State；
- Runtime Coordinator；
- Definition Resolver；
- Context Coordinator；
- Workflow Coordinator；
- Gate Coordinator；
- Script Coordinator；
- Advisory Bridge；
- Runtime Result Coordinator；
- Runtime Result。

---

## 3.2 V1 Core Templates

必须实现：

- `PROJECT_PROFILE.template.md`；
- `PROJECT_STATE.template.md`；
- `PROJECT_PLAN.template.md`；
- `DECISION_RECORD.template.md`。

---

## 3.3 Optional Extension

以下属于可选扩展：

- `PROJECT_ARTIFACTS.md`；
- Project Type Specific Context；
- Project Type Specific Gate；
- Project Type Specific Advisory。

当前 Implementation 不创建没有上游正式定义的：

- Project Type Specific Gate；
- Project Type Specific Workflow Branch；
- Project Type Specific Runtime Rule。

`PROJECT_ARTIFACTS.md`：

保留 Optional Context 支持能力，

但不作为 V1 Core Context 初始化时的强制生成文件。

---

## 3.4 V1 明确不实现

当前 V1 不实现：

- Jira / Notion / Trello 替代系统；
- 企业审批流程；
- 团队权限管理；
- 企业项目治理；
- 独立 Runtime 服务；
- 多项目 Runtime Service；
- Distributed Runtime；
- 企业级 Agent Orchestration；
- 自动替 Maker 做项目决策；
- 未定义的 Multi-Skill Orchestration；
- 未定义的 Project History Analytics；
- 未定义的 Project Retrospective Engine；
- 未定义的 Project Type Extension。

---

## 4. Implementation Technology Baseline

以下属于 Implementation Layer 技术选择。

不改变任何 Domain Rule。

### Runtime

使用：

Python 3。

优先只使用：

Python Standard Library。

V1 不引入第三方 Runtime Framework。

---

### Structured Runtime Definition

Runtime 使用：

JSON

承载需要机器读取的：

- Workflow Definition Projection；
- Gate Definition Projection；
- Context Definition Projection；
- Advisory Definition Projection；
- Runtime Configuration。

JSON 文件：

只是冻结上游定义的 Implementation Projection。

不是新的 Source of Truth。

---

### Human / Agent Artifact

以下继续使用 Markdown：

- SKILL；
- README；
- AGENTS；
- Context Template。

---

### Test

使用：

Python Standard Library `unittest`

作为 V1 基础 Test Runner。

---

## 5. Target Skill Package Structure

V1 最终 Skill Package：

```text
PROJECT_INCUBATOR/
├── SKILL.md
├── README.md
├── AGENTS.md
│
├── runtime/
│   ├── __init__.py
│   ├── config.json
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── contracts.py
│   │   ├── runtime_types.py
│   │   └── coordinator.py
│   │
│   ├── components/
│   │   ├── __init__.py
│   │   ├── definition_resolver.py
│   │   ├── context_coordinator.py
│   │   ├── workflow_coordinator.py
│   │   ├── gate_coordinator.py
│   │   ├── script_coordinator.py
│   │   ├── advisory_bridge.py
│   │   └── result_coordinator.py
│   │
│   └── adapters/
│       ├── __init__.py
│       ├── file_store.py
│       └── script_runner.py
│
├── references/
│   ├── workflow/
│   │   └── core_workflow.json
│   ├── gates/
│   │   └── gates.json
│   ├── context/
│   │   └── context_model.json
│   └── advisory/
│       └── advisory.json
│
├── templates/
│   └── context/
│       ├── PROJECT_PROFILE.template.md
│       ├── PROJECT_STATE.template.md
│       ├── PROJECT_PLAN.template.md
│       └── DECISION_RECORD.template.md
│
├── scripts/
│   ├── validate_contract_payload.py
│   ├── inspect_git_evidence.py
│   ├── validate_artifact_evidence.py
│   └── validate_context_integrity_evidence.py
│
└── tests/
    ├── unit/
    │   ├── test_contracts.py
    │   ├── test_definition_resolver.py
    │   ├── test_context_coordinator.py
    │   ├── test_workflow_coordinator.py
    │   ├── test_gate_coordinator.py
    │   ├── test_script_coordinator.py
    │   ├── test_advisory_bridge.py
    │   └── test_runtime_coordinator.py
    │
    ├── integration/
    │   └── test_runtime_execution_flow.py
    │
    └── e2e/
        └── test_v1_core_workflow.py
```

---

## 6. Runtime-generated Project Files

Runtime 操作目标项目时：

Core Context 文件位于目标 Project Root。

包括：

```text
PROJECT_PROFILE.md
PROJECT_STATE.md
PROJECT_PLAN.md
PROJECT_DECISIONS.md
```

其中：

- `PROJECT_PROFILE.md` 在 P0 建立；
- `PROJECT_STATE.md` 在项目当前状态首次建立时创建；
- `PROJECT_PLAN.md` 在 P3 Execution Planning 形成当前有效计划时建立；
- `PROJECT_DECISIONS.md` 在首次需要持久化 Maker Confirmed Decision 时建立。

Optional：

```text
PROJECT_ARTIFACTS.md
```

只在已经满足 Optional Context Extension 条件时建立。

Implementation 不强制所有 Project 默认创建 `PROJECT_ARTIFACTS.md`。

---

## 7. Reference Implementation Rule

`references/` 中的 JSON：

必须满足以下规则：

1. 每项 Definition 必须能够追溯到具体上游文件；
2. 不添加上游不存在的 Domain Field；
3. 不修改 Domain Semantics；
4. 不重新定义 Source of Truth；
5. Runtime 读取 Reference 时只能把它作为冻结定义的 Implementation Projection。

每个 Reference 顶层必须包含：

- `definition_id`；
- `source_document`；
- `definition_version`；
- 对应领域 Definition。

`definition_version`：

只作为 Implementation Projection 的版本标识。

不得改变 Project Incubator 的产品版本语义。

---

# 8. Implementation Tasks

## TASK-001 — 创建 Skill Package 骨架

### Goal

建立 Project Incubator V1 的完整实现目录骨架。

### Input

- PROJECT_INCUBATOR_V1_DESIGN.md；
- PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md。

### Dependency

无。

### Implementation Scope

创建：

- `runtime/`；
- `runtime/core/`；
- `runtime/components/`；
- `runtime/adapters/`；
- `references/workflow/`；
- `references/gates/`；
- `references/context/`；
- `references/advisory/`；
- `templates/context/`；
- `scripts/`；
- `tests/unit/`；
- `tests/integration/`；
- `tests/e2e/`。

创建对应 Python package `__init__.py`。

### Non-Goal

不得实现任何 Runtime Logic。

不得创建新的 Domain Definition。

### Generated / Modified Files

```text
runtime/__init__.py
runtime/core/__init__.py
runtime/components/__init__.py
runtime/adapters/__init__.py
```

以及上述目录。

### Expected Result

后续所有 Implementation Task 都具有固定目标目录。

### Validation Criteria

- 所有规定目录存在；
- 不存在额外 Domain Layer；
- 不创建 `artifact/` 或 `validation/` Core Module；
- Python package 可以被 import。

---

## TASK-002 — 实现 Skill Entry 与说明文件

### Goal

实现 Skill Package 的入口、用户说明和 Agent 行为边界。

### Input

- PROJECT_INCUBATOR_V1_DESIGN.md；
- PROJECT_INCUBATOR_V1_PHASE_ADVISORY_DESIGN.md；
- PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md。

### Dependency

TASK-001。

### Implementation Scope

创建：

- `SKILL.md`；
- `README.md`；
- `AGENTS.md`。

`SKILL.md`：

说明：

- Project Incubator 的使用目的；
- 适用的长期项目孵化场景；
- Core Workflow；
- Runtime 使用入口；
- Agent 什么时候应该使用 Project Incubator。

`README.md`：

说明：

- Project Incubator 是什么；
- Skill Package 结构；
- Core Context；
- Core Workflow；
- 使用方式。

`AGENTS.md`：

固化：

- Maker / Agent / Runtime Boundary；
- Agent 不绕过 Runtime；
- Agent 不自行改变 Project Goal / Scope；
- Agent 不替代 Maker Authorization；
- Agent 不使用历史聊天覆盖 PROJECT_STATE。

### Non-Goal

不得在这些文件重新定义 Workflow、Gate、Context 或 Runtime。

### Generated / Modified Files

```text
SKILL.md
README.md
AGENTS.md
```

### Expected Result

Agent 可以判断何时使用 Skill，

Maker 可以理解 Skill 的基本使用方式。

### Validation Criteria

- SKILL.md 明确 Skill 触发场景；
- AGENTS.md 明确 Human Decision Boundary；
- AGENTS.md 明确 PROJECT_STATE.md 是 Current State Source of Truth；
- 三个文件不包含新的 Gate Type 或 Phase。

---

## TASK-003 — 生成 Workflow Structured Reference

### Goal

将冻结 Workflow Design / Contract 投影为 Runtime 可读取定义。

### Input

- PROJECT_INCUBATOR_V1_WORKFLOW_DESIGN.md；
- PROJECT_INCUBATOR_V1_WORKFLOW_CONTRACT.md。

### Dependency

TASK-001。

### Implementation Scope

生成：

`references/workflow/core_workflow.json`

必须包含：

- Workflow Identity；
- P0–P6；
- Phase ID；
- Phase Name；
- Phase Goal；
- Input；
- Output；
- Required Artifact；
- State Change Requirement；
- Gate Trigger Requirement；
- Allowed Next Phase；
- P6 Iteration Transition Set。

### Non-Goal

不得修改：

- Core Phase；
- Allowed Next Phase；
- Artifact Flow。

### Generated / Modified Files

```text
references/workflow/core_workflow.json
```

### Expected Result

Runtime 不需要重新从自然语言推导 Core Workflow。

### Validation Criteria

Allowed Transition 必须精确为：

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

不存在额外 Transition。

---

## TASK-004 — 生成 Gate Structured Reference

### Goal

把冻结 Gate Definitions 投影为 Runtime 可读取定义。

### Input

- PROJECT_INCUBATOR_V1_GATE_DESIGN.md；
- PROJECT_INCUBATOR_V1_GATE_CONTRACT.md。

### Dependency

TASK-001。

### Implementation Scope

创建：

`references/gates/gates.json`

必须完整包含当前 15 个 Gate。

每一个 Gate 必须映射：

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

### Non-Goal

不得：

- 新增 Gate；
- 删除 Gate；
- 改变 Required Authorization；
- 改变 Evaluation Nature。

### Generated / Modified Files

```text
references/gates/gates.json
```

### Expected Result

Gate Coordinator 可以通过 Gate ID 获得完整冻结 Gate Definition。

### Validation Criteria

- Gate Count = 15；
- 所有 Gate ID 唯一；
- 15 个 Gate ID 与 Gate Design 完全一致；
- 无 Implementation-only Gate。

---

## TASK-005 — 生成 Context Structured Reference

### Goal

将 Context Model 的领域定义投影为 Runtime Reference。

### Input

- PROJECT_INCUBATOR_V1_CONTEXT_MODEL_DESIGN.md；
- PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md。

### Dependency

TASK-001。

### Implementation Scope

创建：

`references/context/context_model.json`

必须表达：

- Core Context Type；
- Context Responsibility；
- Context Authority Scope；
- Context Lifecycle；
- Optional Context Definition；
- PROJECT_ARTIFACTS Optional Context Identity。

### Non-Goal

不得把：

- Read Permission；
- Write Permission；
- Mutation Authority

重新写成新的 Domain Authority。

### Generated / Modified Files

```text
references/context/context_model.json
```

### Expected Result

Runtime 可以确定 Context 类型与领域归属。

### Validation Criteria

必须存在：

- PROJECT_PROFILE；
- PROJECT_STATE；
- PROJECT_PLAN；
- PROJECT_DECISIONS。

并且：

`PROJECT_STATE`

必须标识为：

Current Project State 唯一 Source of Truth。

---

## TASK-006 — 生成 Advisory Structured Reference

### Goal

把 Advisory Domain Model 投影为 Agent / Runtime 可使用 Reference。

### Input

- PROJECT_INCUBATOR_V1_PHASE_ADVISORY_DESIGN.md。

### Dependency

TASK-001。

### Implementation Scope

创建：

`references/advisory/advisory.json`

必须表达：

- Advisory Trigger；
- Advisory Context；
- Advisory Content Type；
- Advisory Response Model；
- Agent Use Boundary；
- Project Type Extension Boundary。

### Non-Goal

不得创建 Prompt Template Engine。

不得将 Advisory 转换为 Runtime Command。

### Generated / Modified Files

```text
references/advisory/advisory.json
```

### Expected Result

Advisory Bridge 可以通过结构化定义识别 Advisory Trigger。

### Validation Criteria

至少存在：

- Phase Entry；
- Maker Guidance Request；
- Missing Information；
- Risk Detected；
- Decision Required；
- Validation Feedback；
- Iteration Re-entry。

Advisory Definition 不包含：

Workflow Transition Execution。

---

## TASK-007 — 实现 PROJECT_PROFILE Template

### Goal

实现项目身份 Context 的初始化模板。

### Input

PROJECT_INCUBATOR_V1_CONTEXT_MODEL_DESIGN.md。

### Dependency

TASK-001。

### Implementation Scope

创建：

`templates/context/PROJECT_PROFILE.template.md`

模板必须覆盖：

- Project Name；
- Project Type；
- Intent；
- Target User；
- Success Criteria；
- Long-Term Constraint；
- Maker Confirmed Information。

### Non-Goal

不得包含：

- Current Phase；
- Current Runtime State；
- 临时任务；
- Future Plan。

### Generated / Modified Files

```text
templates/context/PROJECT_PROFILE.template.md
```

### Expected Result

Agent 可以基于模板创建合法 `PROJECT_PROFILE.md`。

### Validation Criteria

模板字段全部属于 PROFILE Authority。

不存在 STATE / PLAN 职责字段。

---

## TASK-008 — 实现 PROJECT_STATE Template

### Goal

实现 Current Project State 初始化模板。

### Input

PROJECT_INCUBATOR_V1_CONTEXT_MODEL_DESIGN.md。

### Dependency

TASK-001。

### Implementation Scope

创建：

`templates/context/PROJECT_STATE.template.md`

必须覆盖：

- Current Phase；
- Current Gate State；
- Current Execution State；
- Completed Items；
- Current Blockers；
- Recent State Change。

### Non-Goal

不得包含：

- Future Task Plan；
- Future Execution Order；
- 未确认设计方案。

### Generated / Modified Files

```text
templates/context/PROJECT_STATE.template.md
```

### Expected Result

Runtime 可以建立唯一 Current State Context。

### Validation Criteria

模板明确：

`PROJECT_STATE.md`

为 Current Project State Source of Truth。

---

## TASK-009 — 实现 PROJECT_PLAN Template

### Goal

实现未来执行计划模板。

### Input

PROJECT_INCUBATOR_V1_CONTEXT_MODEL_DESIGN.md。

### Dependency

TASK-001。

### Implementation Scope

创建：

`templates/context/PROJECT_PLAN.template.md`

必须覆盖：

- Phase Goal；
- Phase Task；
- Execution Order；
- Dependency；
- Expected Artifact；
- Risk；
- Validation Method。

### Non-Goal

不得记录：

Current Actual State。

### Generated / Modified Files

```text
templates/context/PROJECT_PLAN.template.md
```

### Expected Result

P3 可以创建当前有效未来执行计划。

### Validation Criteria

Plan 与 State 职责严格分离。

---

## TASK-010 — 实现 Decision Record Template

### Goal

实现 Maker Confirmed Decision 的标准记录结构。

### Input

PROJECT_INCUBATOR_V1_CONTEXT_MODEL_DESIGN.md。

### Dependency

TASK-001。

### Implementation Scope

创建：

`templates/context/DECISION_RECORD.template.md`

必须覆盖：

- Decision ID；
- Decision Context；
- Selected Option；
- Decision Owner；
- Decision Timestamp；
- Impact。

### Non-Goal

不得记录：

- Unconfirmed Proposal；
- Agent 自主判断。

### Generated / Modified Files

```text
templates/context/DECISION_RECORD.template.md
```

### Expected Result

Runtime 可以向 `PROJECT_DECISIONS.md` append Maker Confirmed Decision。

### Validation Criteria

Decision Owner 必须能够明确表达 Maker。

历史 Decision 不通过模板设计支持覆盖操作。

---

## TASK-011 — 实现 Contract 与 Runtime 基础类型

### Goal

将所有冻结 Contract Status 与 Runtime State 转换为可执行类型。

### Input

- Context Access Contract；
- Workflow Contract；
- Gate Contract；
- Script Contract；
- Runtime Specification。

### Dependency

TASK-001。

### Implementation Scope

创建：

```text
runtime/core/contracts.py
runtime/core/runtime_types.py
```

必须实现稳定 Enum / Data Structure。

### Required Contract Sets

Context Access Result：

```text
ACCEPTED
REJECTED
AUTHORIZATION_REQUIRED
GATE_REQUIREMENT_UNRESOLVED
BOUNDARY_VIOLATION
CONTEXT_CONFLICT
```

Workflow Result：

```text
NOT_READY
READY_FOR_TRANSITION
TRANSITION_NOT_ALLOWED
```

Gate Evaluation Result：

```text
REQUIREMENT_SATISFIED
REQUIREMENT_UNSATISFIED
AUTHORIZATION_REQUIRED
EVIDENCE_INSUFFICIENT
ACTION_BLOCKED
```

Script Execution Status：

```text
COMPLETED
INVALID_INPUT
UNSUPPORTED_INVOCATION
EXECUTION_ERROR
```

Script Validation Result：

```text
REQUIREMENT_SATISFIED
REQUIREMENT_UNSATISFIED
VALIDATION_NOT_COMPLETED
```

Runtime State：

```text
EXECUTING
WAITING_FOR_MAKER
BLOCKED_BY_GATE
SUSPENDED
FAILED
COMPLETED
```

### Non-Goal

不得新增新的 Contract Status。

### Generated / Modified Files

```text
runtime/core/contracts.py
runtime/core/runtime_types.py
```

### Expected Result

所有 Runtime Component 使用统一类型。

### Validation Criteria

Enum Value 必须与冻结 Contract 完全一致。

Script Validation Result 与 Gate Evaluation Result：

必须是两个独立类型。

---

## TASK-012 — 实现 Runtime Configuration 与 Definition Resolver

### Goal

实现 Frozen Definition Loading。

### Input

- TASK-003；
- TASK-004；
- TASK-005；
- TASK-006；
- TASK-011；
- Runtime Specification Component Loading Model。

### Dependency

TASK-003、TASK-004、TASK-005、TASK-006、TASK-011。

### Implementation Scope

创建：

```text
runtime/config.json
runtime/components/definition_resolver.py
```

`runtime/config.json` 只定义：

- Reference Location；
- Template Location；
- Script Location；
- Definition Identity Mapping。

Definition Resolver 必须能够加载：

- Workflow Definition；
- Gate Definition；
- Context Definition；
- Advisory Definition；
- Runtime Contract Type。

Definition 缺失时：

返回：

```text
Runtime State = FAILED
Failure Reason = RUNTIME_DEPENDENCY_FAILURE
```

### Non-Goal

不得：

- 修改 Reference；
- 自动补充缺失 Domain Definition。

### Expected Result

Runtime 可以确定性获得 Frozen Definition Set。

### Validation Criteria

删除任意 Required Reference 后：

Definition Resolver 必须失败，

不能自行使用默认推测。

---

## TASK-013 — 实现 File Store Adapter

### Goal

为 Runtime 提供受控文件读取、写入和写后验证能力。

### Input

- Context Access Contract；
- Runtime Context Mutation Flow。

### Dependency

TASK-011。

### Implementation Scope

创建：

`runtime/adapters/file_store.py`

必须支持：

- Read File；
- Atomic Write；
- Append；
- Exists；
- Read-back Verification。

用于：

- Context File；
- Reference；
- Template；
- Runtime Result 所需 File Interaction。

### Non-Goal

File Store 不判断：

- 谁拥有写权限；
- 是否应该 Mutation；
- Gate 是否满足。

这些由 Coordinator 决定。

### Expected Result

Runtime 可以通过单一 Adapter 执行文件 I/O。

### Validation Criteria

- 写入后必须 read-back；
- 写入失败必须产生明确异常；
- Adapter 不自行改变 Domain State；
- 不存在隐式 Context Authorization。

---

## TASK-014 — 实现 Context Coordinator

### Goal

实现 Context Access Contract 的 Runtime Execution。

### Input

- Context Model Design；
- Context Access Contract；
- Runtime Context Interaction；
- TASK-005；
- TASK-007–010；
- TASK-011；
- TASK-013。

### Dependency

TASK-005、TASK-007、TASK-008、TASK-009、TASK-010、TASK-011、TASK-013。

### Implementation Scope

创建：

`runtime/components/context_coordinator.py`

必须支持：

- READ；
- REQUEST_MUTATION；
- AUTHORIZE_MUTATION；
- EXECUTE_MUTATION；
- Mutation Authority Check；
- Access Result；
- Context Conflict；
- Persisted Result Verification。

必须保持：

Runtime 是唯一 Context Persisted Mutation Executor。

### Non-Goal

不得重新定义 Context Authority。

### Expected Result

所有 Context 操作都通过 Context Coordinator。

### Validation Criteria

必须验证：

- Script Direct Context Read 被拒绝；
- Agent Direct Write 被拒绝；
- PROFILE 修改缺少 Maker Authorization 时不能执行；
- DECISIONS Append 缺少 Maker Confirmation 时不能执行；
- Optional Context 无法覆盖 Core Context Authority。

---

## TASK-015 — 实现 Workflow Coordinator

### Goal

实现 Workflow Contract 的 Runtime Consumer。

### Input

- Workflow Design；
- Workflow Contract；
- Runtime Workflow Execution Flow；
- TASK-003；
- TASK-011；
- TASK-014。

### Dependency

TASK-003、TASK-011、TASK-014。

### Implementation Scope

创建：

`runtime/components/workflow_coordinator.py`

必须支持：

- Current Phase Resolution；
- Phase Input Preparation；
- Phase Result Validation；
- Required Artifact Requirement；
- State Change Requirement；
- Gate Trigger Requirement；
- Transition Request；
- Transition Eligibility；
- P6 Iteration Transition。

### Non-Goal

不得：

- 新增 Phase；
- 新增 Transition；
- 修改 Allowed Next Phase。

### Expected Result

Runtime 可以确定性判断 Workflow 是否 READY_FOR_TRANSITION。

### Validation Criteria

以下必须被拒绝：

```text
P0 → P2
P1 → P3
P5 → P4
P6 → P0
P6 → P1
P6 → P6
```

只有 Workflow Contract 中定义的 Transition 合法。

---

## TASK-016 — 实现 Contract Payload Validator Script

### Script Purpose

验证 Runtime / Script / Gate / Workflow Contract Payload 的确定性结构要求。

### Contract Input

必须接收：

- Invocation ID；
- Contract Type；
- Input Data；
- Required Field Set；
- Allowed Value Set。

### Contract Output

符合 Script Contract：

- Script Identity；
- Execution Status；
- Validation Result；
- Evidence；
- Diagnostic Information。

### Validation Responsibility

只检查：

- Required Field Presence；
- Enum Membership；
- 基础数据类型；
- 必填值是否为空。

### Error Handling Requirement

- Input 本身无法解析 → `INVALID_INPUT`；
- Unsupported Contract Type → `UNSUPPORTED_INVOCATION`；
- Script 异常 → `EXECUTION_ERROR`；
- Contract Requirement 不满足 → `COMPLETED + REQUIREMENT_UNSATISFIED`。

### Dependency

TASK-011。

### Generated File

```text
scripts/validate_contract_payload.py
```

### Non-Goal

不得判断：

- Maker Intent；
- Gate Risk；
- Project Scope；
- Workflow Domain Semantics。

### Test / Validation Criteria

必须能够检测：

- Missing Invocation ID；
- Invalid Gate Result Enum；
- Invalid Workflow Result Enum；
- Invalid Script Status Enum。

---

## TASK-017 — 实现 Git Evidence Script

### Script Purpose

为 GATE-GIT 提供确定性 Git Evidence。

### Contract Input

Runtime 提供：

- Repository Path；
- Requested Git Operation。

### Contract Output

必须提供：

- Current Branch；
- Working Tree Change Presence；
- Untracked Change Presence；
- Staged Change Presence；
- Target Operation Reference；
- Relevant Git Evidence。

### Validation Responsibility

只获取确定性 Git Facts。

### Error Handling Requirement

非 Git Repository：

不得伪造结果。

必须返回合法 Script Error / Validation Not Completed。

### Dependency

TASK-011。

### Generated File

```text
scripts/inspect_git_evidence.py
```

### Non-Goal

不得决定：

- 是否允许 push；
- 是否批准 merge；
- 是否可以删除 branch。

最终 Gate Result：

继续由 Gate Contract 形成。

### Test / Validation Criteria

至少覆盖：

- Clean Repository；
- Modified Repository；
- Untracked File；
- Invalid Repository Path。

---

## TASK-018 — 实现 Artifact Evidence Script

### Script Purpose

为 Required Artifact 与 Artifact-related Gate 提供确定性 Evidence。

### Contract Input

Runtime 提供：

- Artifact Reference；
- Expected Requirement；
- Artifact Input Data / Path。

### Contract Output

返回：

- Artifact Exists；
- Artifact Readable；
- Artifact Non-empty；
- Declared Artifact Identity；
- Evidence。

### Validation Responsibility

只验证可以确定性确认的 Artifact Requirement。

### Error Handling Requirement

- 输入无效 → INVALID_INPUT；
- 无法访问 → EXECUTION_ERROR / VALIDATION_NOT_COMPLETED；
- Artifact 不满足明确 Requirement → REQUIREMENT_UNSATISFIED。

### Dependency

TASK-011。

### Generated File

```text
scripts/validate_artifact_evidence.py
```

### Non-Goal

不得判断：

- Artifact 创意质量；
- Artifact 是否“足够好”；
- Intent 是否在价值层面满足。

### Test / Validation Criteria

覆盖：

- File Missing；
- Empty Artifact；
- Existing Artifact；
- Unreadable Artifact。

---

## TASK-019 — 实现 Context Integrity Evidence Script

### Script Purpose

为 Context Integrity Gate 提供可确定性验证的 Context Evidence。

### Contract Input

必须由 Runtime 提供：

- Required Context Type Set；
- Context-derived Data；
- Declared Context Identity；
- Required Structural Item。

Script 不直接读取 Core Context。

### Contract Output

必须能够返回：

- Required Context Presence；
- Missing Context；
- Required Structural Item Presence；
- Identity Conflict Evidence；
- Validation Result。

### Validation Responsibility

只负责：

机械可验证的完整性检查。

### Error Handling Requirement

无法形成确定性判断：

返回：

`VALIDATION_NOT_COMPLETED`

不得猜测。

### Dependency

TASK-005、TASK-011。

### Generated File

```text
scripts/validate_context_integrity_evidence.py
```

### Non-Goal

不得解决：

- Context 语义冲突；
- Maker Intent 冲突；
- Authority Judgment。

### Test / Validation Criteria

覆盖：

- All Core Context Present；
- Missing PROJECT_STATE；
- Context Identity Mismatch；
- Insufficient Input。

---

## TASK-020 — 实现 Script Runner 与 Script Coordinator

### Goal

实现 Runtime 与 Script 的完整 Invocation 机制。

### Input

- Script Contract；
- Runtime Script Invocation；
- TASK-016；
- TASK-017；
- TASK-018；
- TASK-019。

### Dependency

TASK-016、TASK-017、TASK-018、TASK-019。

### Implementation Scope

创建：

```text
runtime/adapters/script_runner.py
runtime/components/script_coordinator.py
```

必须实现：

- Script Identity Resolution；
- Script Input Preparation；
- Script Execution；
- Script Output Parsing；
- Execution Status Handling；
- Validation Result Handling；
- Evidence Routing。

默认：

不自动 Retry。

### Non-Goal

不得让 Script：

- Direct Read Context；
- 执行 Workflow Transition；
- 修改 Context；
- 批准 Gate。

### Expected Result

Runtime 可以统一调用确定性 Script。

### Validation Criteria

验证以下映射：

```text
COMPLETED + REQUIREMENT_SATISFIED
→ 返回 Evidence

COMPLETED + REQUIREMENT_UNSATISFIED
→ VALIDATION_UNSATISFIED

INVALID_INPUT
→ INVALID_SCRIPT_INPUT

UNSUPPORTED_INVOCATION
→ UNSUPPORTED_SCRIPT_INVOCATION

EXECUTION_ERROR
→ SCRIPT_EXECUTION_ERROR
```

---

## TASK-021 — 实现 Gate Coordinator

### Goal

实现 15 个 Gate 的 Runtime Invocation 与 Evaluation Coordination。

### Input

- Gate Design；
- Gate Contract；
- Runtime Gate Invocation；
- TASK-004；
- TASK-011；
- TASK-014；
- TASK-015；
- TASK-020。

### Dependency

TASK-004、TASK-011、TASK-014、TASK-015、TASK-020。

### Implementation Scope

创建：

`runtime/components/gate_coordinator.py`

必须实现：

- Trigger Matching；
- Gate Definition Resolution；
- Invocation Creation；
- Gate Input Preparation；
- Evidence Collection；
- Validation Evidence Integration；
- Judgment Evidence Integration；
- Maker Authorization Handling；
- Multi-Gate Handling；
- Gate Re-evaluation；
- Gate Output。

### Non-Goal

不得：

- 修改 Gate Definition；
- 创建新 Gate；
- 用 Script 替代 Judgment-Based Gate；
- 自动提供 Maker Authorization。

### Expected Result

Gate Result 精确映射到 Runtime State。

### Validation Criteria

必须验证：

```text
REQUIREMENT_SATISFIED
→ 可继续 Contract 检查

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

## TASK-022 — 实现 Advisory Bridge

### Goal

将 Advisory Domain Model 接入 Runtime，但保持建议性边界。

### Input

- Phase Advisory Design；
- Runtime Advisory Relationship；
- TASK-006；
- TASK-011。

### Dependency

TASK-006、TASK-011。

### Implementation Scope

创建：

`runtime/components/advisory_bridge.py`

必须识别：

- Phase Entry；
- Maker Guidance Request；
- Missing Information；
- Risk Detected；
- Decision Required；
- Validation Feedback；
- Iteration Re-entry。

必须准备：

Agent 生成 Advisory 所需的：

- Current Phase；
- Project Context；
- Relevant Artifact；
- Validation Result；
- Risk；
- Missing Information。

### Non-Goal

Advisory Bridge 不：

- 生成 Gate Result；
- 修改 Context；
- 执行 Transition；
- 执行 Recommended Action。

### Expected Result

Runtime 能够把适当信息暴露给 Agent形成 Advisory。

### Validation Criteria

Advisory Response：

不能直接改变 Runtime State。

Recommended Action：

必须转换为新的 Runtime Request 才能执行。

---

## TASK-023 — 实现 Runtime Result Coordinator

### Goal

建立统一 Runtime Result。

### Input

- Runtime Specification Runtime Result Model；
- TASK-011。

### Dependency

TASK-011。

### Implementation Scope

创建：

`runtime/components/result_coordinator.py`

Runtime Result 必须包含：

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

### Non-Goal

不得重新解释：

任何 Contract Result。

### Expected Result

每次 Runtime Execution 都产生稳定结果。

### Validation Criteria

所有 Runtime State：

```text
EXECUTING
WAITING_FOR_MAKER
BLOCKED_BY_GATE
SUSPENDED
FAILED
COMPLETED
```

都必须能够生成合法 Runtime Result。

---

## TASK-024 — 实现 Runtime Coordinator 与完整 Lifecycle

### Goal

把所有 Runtime Component 组合为完整 Runtime Engine。

### Input

- Runtime Specification；
- TASK-012；
- TASK-014；
- TASK-015；
- TASK-020；
- TASK-021；
- TASK-022；
- TASK-023。

### Dependency

TASK-012、TASK-014、TASK-015、TASK-020、TASK-021、TASK-022、TASK-023。

### Implementation Scope

创建：

`runtime/core/coordinator.py`

实现固定流程：

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

### Non-Goal

不得：

- 创建新的 Runtime Decision Rule；
- 自动绕过 Gate；
- 自动补全 Maker Input。

### Expected Result

形成 V1 Full Runtime Engine。

### Validation Criteria

必须验证：

1. Project State 始终来自 PROJECT_STATE；
2. Context Mutation 全部经过 Context Coordinator；
3. Gate 未解决时不执行受保护行为；
4. Transition 只有 State 写回成功后才完成；
5. Unsupported Condition 返回 SUSPENDED；
6. Runtime 不自行扩展 Workflow。

---

## TASK-025 — 实现 Unit Tests

### Goal

验证所有独立 Runtime Component 和 Contract Projection。

### Input

TASK-003–024。

### Dependency

TASK-024。

### Implementation Scope

创建：

```text
tests/unit/test_contracts.py
tests/unit/test_definition_resolver.py
tests/unit/test_context_coordinator.py
tests/unit/test_workflow_coordinator.py
tests/unit/test_gate_coordinator.py
tests/unit/test_script_coordinator.py
tests/unit/test_advisory_bridge.py
tests/unit/test_runtime_coordinator.py
```

### Non-Goal

不得使用 Mock Result 绕过 Contract Invariant。

### Expected Result

每个 Runtime Component 可独立验证。

### Validation Criteria

所有 Unit Test：

Exit Code = 0。

必须存在失败用例验证：

- Unauthorized Mutation；
- Invalid Transition；
- Gate Block；
- Invalid Script Result；
- Missing Definition。

---

## TASK-026 — 实现 Runtime Integration Tests

### Goal

验证 Runtime Component 之间真实组合。

### Input

TASK-024、TASK-025。

### Dependency

TASK-025。

### Implementation Scope

创建：

`tests/integration/test_runtime_execution_flow.py`

至少验证：

### Scenario A

合法 Phase Transition。

### Scenario B

Required Artifact Missing。

### Scenario C

Gate Authorization Missing。

### Scenario D

Context Conflict。

### Scenario E

Script Validation Failure。

### Scenario F

Script Execution Error。

### Scenario G

P6 Iteration 返回 P2 / P3 / P4 / P5。

### Non-Goal

不得只测试单函数。

### Expected Result

完整 Runtime Flow 可以跨 Component 工作。

### Validation Criteria

所有 Scenario 的最终 Runtime State 必须严格匹配 Runtime Specification。

---

## TASK-027 — 实现 V1 End-to-End Validation

### Goal

验证 Project Incubator V1 从新 Project 到 Iteration 的完整生命周期。

### Input

TASK-026。

### Dependency

TASK-026。

### Implementation Scope

创建：

`tests/e2e/test_v1_core_workflow.py`

E2E 必须模拟：

```text
New Project
↓
P0 Intent Discovery
↓
PROJECT_PROFILE.md
↓
P1 Project Definition
↓
PROJECT_STATE.md
↓
P2 Solution Design
↓
Solution Design Artifact
↓
P3 Execution Planning
↓
PROJECT_PLAN.md
↓
P4 Creation
↓
Project Artifact
↓
P5 Validation
↓
Validation Result
↓
P6 Iteration
↓
返回 P2 / P3 / P4 / P5 中一个合法目标
```

同时验证：

- Gate；
- Context Mutation；
- Script Evidence；
- Runtime State；
- Advisory Trigger；
- Maker Authorization。

### Non-Goal

不得使用绕过 Runtime 的直接 State Mutation。

### Expected Result

V1 Core Workflow 可以完成一次完整闭环。

### Validation Criteria

必须满足：

- 所有 Test Exit Code = 0；
- Current Phase 始终与 PROJECT_STATE 一致；
- 没有非法 Transition；
- 没有未经授权的 Context Mutation；
- 没有 Script Direct Context Read；
- 没有 Gate Result 被 Script Result 替代；
- P6 Iteration 合法回到允许 Phase。

---

# 9. Task Execution Order

Codex 实现时使用以下唯一推荐基准顺序：

```text
TASK-001
↓
TASK-002
↓
TASK-003
↓
TASK-004
↓
TASK-005
↓
TASK-006
↓
TASK-007
↓
TASK-008
↓
TASK-009
↓
TASK-010
↓
TASK-011
↓
TASK-012
↓
TASK-013
↓
TASK-014
↓
TASK-015
↓
TASK-016
↓
TASK-017
↓
TASK-018
↓
TASK-019
↓
TASK-020
↓
TASK-021
↓
TASK-022
↓
TASK-023
↓
TASK-024
↓
TASK-025
↓
TASK-026
↓
TASK-027
```

Codex 默认按照以上顺序执行。

---

## 9.1 Allowed Parallel Groups

如果执行环境支持并行 Task：

只允许以下并行。

### Parallel Group A

TASK-003  
TASK-004  
TASK-005  
TASK-006

前提：

TASK-001 已完成。

---

### Parallel Group B

TASK-007  
TASK-008  
TASK-009  
TASK-010

前提：

TASK-001 已完成。

---

### Parallel Group C

TASK-016  
TASK-017  
TASK-018  
TASK-019

前提：

各自 Dependency 已满足。

---

除上述 Group 外：

默认串行执行。

---

# 10. Implementation Checkpoints

## Checkpoint 1 — Package Foundation

完成：

TASK-001–002。

验证：

- Skill Package Structure；
- Skill Entry；
- Agent Boundary。

通过后才进入 Reference / Template Implementation。

---

## Checkpoint 2 — Frozen Definition Projection

完成：

TASK-003–006。

验证：

- Workflow Reference；
- Gate Reference；
- Context Reference；
- Advisory Reference

均可以追溯到上游 Definition。

---

## Checkpoint 3 — Context Template Foundation

完成：

TASK-007–010。

验证：

- Context Responsibility Separation；
- Core Template 完整性。

---

## Checkpoint 4 — Runtime Foundation

完成：

TASK-011–015。

验证：

- Contract Enum；
- Definition Loading；
- Context Interaction；
- Workflow Evaluation。

---

## Checkpoint 5 — Deterministic Capability

完成：

TASK-016–020。

验证：

- Script Contract；
- Script Result；
- Validation Evidence；
- Script Error Handling。

---

## Checkpoint 6 — Gate / Advisory Runtime

完成：

TASK-021–023。

验证：

- Gate Result Mapping；
- Maker Authorization；
- Advisory Boundary；
- Runtime Result。

---

## Checkpoint 7 — Runtime Integration

完成：

TASK-024。

验证：

Core Runtime Execution Flow。

---

## Checkpoint 8 — Verification

完成：

TASK-025–027。

只有全部 Test 通过：

Project Incubator V1 Implementation 才可以视为完成。

---

# 11. Generated Files

## 11.1 Skill Entry

```text
PROJECT_INCUBATOR/SKILL.md
PROJECT_INCUBATOR/README.md
PROJECT_INCUBATOR/AGENTS.md
```

---

## 11.2 Runtime Core

```text
PROJECT_INCUBATOR/runtime/__init__.py
PROJECT_INCUBATOR/runtime/config.json

PROJECT_INCUBATOR/runtime/core/__init__.py
PROJECT_INCUBATOR/runtime/core/contracts.py
PROJECT_INCUBATOR/runtime/core/runtime_types.py
PROJECT_INCUBATOR/runtime/core/coordinator.py
```

---

## 11.3 Runtime Components

```text
PROJECT_INCUBATOR/runtime/components/__init__.py
PROJECT_INCUBATOR/runtime/components/definition_resolver.py
PROJECT_INCUBATOR/runtime/components/context_coordinator.py
PROJECT_INCUBATOR/runtime/components/workflow_coordinator.py
PROJECT_INCUBATOR/runtime/components/gate_coordinator.py
PROJECT_INCUBATOR/runtime/components/script_coordinator.py
PROJECT_INCUBATOR/runtime/components/advisory_bridge.py
PROJECT_INCUBATOR/runtime/components/result_coordinator.py
```

---

## 11.4 Runtime Adapters

```text
PROJECT_INCUBATOR/runtime/adapters/__init__.py
PROJECT_INCUBATOR/runtime/adapters/file_store.py
PROJECT_INCUBATOR/runtime/adapters/script_runner.py
```

---

## 11.5 Workflow Reference

```text
PROJECT_INCUBATOR/references/workflow/core_workflow.json
```

---

## 11.6 Gate Reference

```text
PROJECT_INCUBATOR/references/gates/gates.json
```

---

## 11.7 Context Reference

```text
PROJECT_INCUBATOR/references/context/context_model.json
```

---

## 11.8 Advisory Reference

```text
PROJECT_INCUBATOR/references/advisory/advisory.json
```

---

## 11.9 Templates

```text
PROJECT_INCUBATOR/templates/context/PROJECT_PROFILE.template.md
PROJECT_INCUBATOR/templates/context/PROJECT_STATE.template.md
PROJECT_INCUBATOR/templates/context/PROJECT_PLAN.template.md
PROJECT_INCUBATOR/templates/context/DECISION_RECORD.template.md
```

---

## 11.10 Scripts

```text
PROJECT_INCUBATOR/scripts/validate_contract_payload.py
PROJECT_INCUBATOR/scripts/inspect_git_evidence.py
PROJECT_INCUBATOR/scripts/validate_artifact_evidence.py
PROJECT_INCUBATOR/scripts/validate_context_integrity_evidence.py
```

---

## 11.11 Unit Tests

```text
PROJECT_INCUBATOR/tests/unit/test_contracts.py
PROJECT_INCUBATOR/tests/unit/test_definition_resolver.py
PROJECT_INCUBATOR/tests/unit/test_context_coordinator.py
PROJECT_INCUBATOR/tests/unit/test_workflow_coordinator.py
PROJECT_INCUBATOR/tests/unit/test_gate_coordinator.py
PROJECT_INCUBATOR/tests/unit/test_script_coordinator.py
PROJECT_INCUBATOR/tests/unit/test_advisory_bridge.py
PROJECT_INCUBATOR/tests/unit/test_runtime_coordinator.py
```

---

## 11.12 Integration Test

```text
PROJECT_INCUBATOR/tests/integration/test_runtime_execution_flow.py
```

---

## 11.13 End-to-End Test

```text
PROJECT_INCUBATOR/tests/e2e/test_v1_core_workflow.py
```

---

# 12. Runtime-generated Context Files

以下文件不是 Skill Package Source File。

它们由 Project Incubator 对目标 Project 执行时创建。

```text
<PROJECT_ROOT>/PROJECT_PROFILE.md
<PROJECT_ROOT>/PROJECT_STATE.md
<PROJECT_ROOT>/PROJECT_PLAN.md
<PROJECT_ROOT>/PROJECT_DECISIONS.md
```

Optional：

```text
<PROJECT_ROOT>/PROJECT_ARTIFACTS.md
```

---

# 13. Script Capability Mapping

| Script | Deterministic Responsibility | Primary Consumer |
| --- | --- | --- |
| validate_contract_payload.py | Contract Payload 结构与 Enum 验证 | Runtime |
| inspect_git_evidence.py | Git Repository 确定性 Evidence | GATE-GIT |
| validate_artifact_evidence.py | Artifact 存在性与机械 Requirement Evidence | Workflow / Gate |
| validate_context_integrity_evidence.py | Context Presence / Structural Integrity Evidence | GATE-CONTEXT-INTEGRITY |

以下 Gate：

主要依赖 Judgment 或 Mixed Evaluation，

不创建独立“自动判断 Script”：

- GATE-SCOPE；
- GATE-CHALLENGE-RESPONSE；
- GATE-CORRECTION-PERSISTENCE；
- GATE-ARCHITECTURE-DECISION；
- GATE-FRAMEWORK-MODIFICATION；
- GATE-PHASE-MODEL-MODIFICATION；
- GATE-MATRIX-MODIFICATION。

这些 Gate 的确定性部分：

可以复用现有 Script Evidence。

最终 Gate Result：

不得由 Script 自动决定。

---

# 14. Validation Criteria

## 14.1 Single Task Validation

每一个 Task 完成后必须确认：

1. 所有 Generated Files 存在；
2. 文件可以正常解析 / import；
3. Task Validation Criteria 全部通过；
4. 没有修改 Dependency Task 的冻结语义；
5. 没有新增未定义 Domain Rule。

任何一项失败：

Task 不得标记 Completed。

---

## 14.2 Module Validation

### Context Module

必须验证：

- PROJECT_STATE 是唯一 Current State Source；
- Agent 无 Direct Write；
- Script 无 Direct Read；
- Runtime 是唯一 Mutation Executor；
- DECISIONS Append-only；
- PROFILE 修改受 Maker Authorization 控制。

---

### Workflow Module

必须验证：

- P0–P6 完整；
- Transition Matrix 完全匹配；
- Output ≠ Required Artifact；
- State Change Requirement ≠ Context Mutation；
- P6 只返回 P2/P3/P4/P5。

---

### Gate Module

必须验证：

- 15 Gate 全部加载；
- Gate ID 唯一；
- Evaluation Result 只有五种；
- Authorization 只来自 Maker；
- Multiple Gate 独立满足；
- Script Result 不直接成为 Gate Result。

---

### Script Module

必须验证：

Execution Status：

```text
COMPLETED
INVALID_INPUT
UNSUPPORTED_INVOCATION
EXECUTION_ERROR
```

Validation Result：

```text
REQUIREMENT_SATISFIED
REQUIREMENT_UNSATISFIED
VALIDATION_NOT_COMPLETED
```

并验证：

Validation Failure ≠ Script Execution Error。

---

### Advisory Module

必须验证：

- Advisory Trigger 可识别；
- Advisory Context 可准备；
- Advisory Response 不直接触发 Runtime；
- Advisory 不修改 Workflow；
- Advisory 不决定 Gate；
- Advisory 不修改 Context。

---

# 15. Runtime Integration Validation

完整 Runtime Integration 必须验证：

```text
Runtime Request
↓
Definition Resolution
↓
Context Establish / Restore
↓
Current Phase Resolution
↓
Workflow Evaluation
↓
Script Evidence
↓
Gate Evaluation
↓
Maker Requirement
↓
Context Mutation
↓
Transition Eligibility
↓
PROJECT_STATE Commit
↓
Runtime Result
```

必须证明：

不存在：

- Contract Bypass；
- Gate Bypass；
- Direct Agent Mutation；
- Direct Script Context Access；
- Illegal Transition；
- Implicit Maker Authorization。

---

# 16. End-to-End Validation

V1 End-to-End 必须至少完成：

### E2E-01 New Project Bootstrap

验证：

没有 PROJECT_STATE 时：

只允许进入 P0 Bootstrap。

---

### E2E-02 Intent Discovery

验证：

P0 可以创建：

`PROJECT_PROFILE.md`

---

### E2E-03 Project Definition

验证：

P1 可以建立：

`PROJECT_STATE.md`

---

### E2E-04 Solution Design

验证：

P2 Required Artifact：

Solution Design Artifact

包含：

- Design Document；
- Solution Definition。

Decision Proposal：

不是固定 Required Artifact。

---

### E2E-05 Execution Planning

验证：

P3 创建：

`PROJECT_PLAN.md`

并且 Plan 不成为 Current State Source。

---

### E2E-06 Creation

验证：

P4 形成 Project Artifact。

---

### E2E-07 Validation

验证：

P5 形成 Validation Result。

---

### E2E-08 Iteration

验证：

P6 根据 Validation Result：

只允许进入：

- P2；
- P3；
- P4；
- P5。

---

### E2E-09 Gate Authorization

模拟需要 Maker Authorization 的行为。

验证：

缺少 Authorization：

```text
WAITING_FOR_MAKER
```

获得有效 Authorization 后：

重新执行 Gate Evaluation。

---

### E2E-10 Gate Block

模拟：

`ACTION_BLOCKED`

验证：

Runtime 不执行受保护 Action。

---

### E2E-11 Context Conflict

模拟 Authority Context 冲突。

验证：

Runtime 返回：

```text
SUSPENDED
CONTEXT_CONFLICT
```

不得自动覆盖 PROJECT_STATE。

---

### E2E-12 Script Failure

验证：

Script：

```text
EXECUTION_ERROR
```

映射：

```text
Runtime State = FAILED
Failure Reason = SCRIPT_EXECUTION_ERROR
```

---

### E2E-13 Validation Failure

验证：

```text
COMPLETED
+
REQUIREMENT_UNSATISFIED
```

不得被 Runtime 表示为 Script Error。

---

# 17. V1 Completion Criteria

Project Incubator V1 只有同时满足以下条件：

才可以标记 Implementation Complete。

## Skill

- SKILL.md 存在；
- Agent 可以识别何时使用 Project Incubator。

## Context

- 四个 Core Context 可以建立和维护；
- PROJECT_STATE 是 Current State 唯一 Source of Truth。

## Workflow

- P0–P6 Runtime Support 完整；
- 所有合法 Transition 可以执行；
- 所有非法 Transition 被阻止。

## Gate

- 15 个 Gate Definition 可以加载；
- Gate Invocation 正常；
- Maker Authorization Boundary 生效。

## Script

- Runtime 可以调用确定性 Script；
- Script Result 符合 Script Contract；
- Script 不拥有状态控制权。

## Advisory

- Agent 可以获得 Phase Advisory；
- Advisory 不控制 Runtime。

## Runtime

- Runtime Lifecycle 可完整执行；
- Runtime State 与 Project State 分离；
- PROJECT_STATE Mutation 成功后才完成 Transition。

## Test

必须满足：

```text
Unit Tests       = PASS
Integration Test = PASS
End-to-End Test  = PASS
```

任何一个失败：

V1 不得标记完成。

---

# 18. Traceability Matrix

| Upstream Requirement | Implementation Task | Generated File / Component | Validation |
| --- | --- | --- | --- |
| Skill Package Architecture | TASK-001 / 002 | SKILL.md / README.md / AGENTS.md / package dirs | Package Validation |
| Workflow Domain Model | TASK-003 | core_workflow.json | Transition Matrix Test |
| Workflow Runtime Interface | TASK-015 | workflow_coordinator.py | Workflow Unit Test |
| Context Domain Model | TASK-005 / 007–010 | context_model.json / templates | Context Boundary Test |
| Context Read / Write / Mutation | TASK-014 | context_coordinator.py | Context Unit Test |
| Gate Domain Model | TASK-004 | gates.json | Gate Definition Test |
| Gate Invocation Contract | TASK-021 | gate_coordinator.py | Gate Unit Test |
| Script Contract | TASK-011 / 020 | contracts.py / script_coordinator.py | Script Contract Test |
| Deterministic Validation | TASK-016–019 | scripts/*.py | Script Unit Test |
| Advisory Model | TASK-006 | advisory.json | Reference Validation |
| Advisory Runtime Relationship | TASK-022 | advisory_bridge.py | Advisory Unit Test |
| Runtime Component Loading | TASK-012 | definition_resolver.py / config.json | Resolver Test |
| Runtime Context Interaction | TASK-013 / 014 | file_store.py / context_coordinator.py | Context Integration |
| Runtime Workflow Execution | TASK-015 / 024 | workflow_coordinator.py / coordinator.py | Workflow Integration |
| Runtime Gate Invocation | TASK-021 / 024 | gate_coordinator.py / coordinator.py | Gate Integration |
| Runtime Script Invocation | TASK-020 / 024 | script_runner.py / script_coordinator.py | Script Integration |
| Runtime Result | TASK-023 | result_coordinator.py | Result Test |
| Runtime Lifecycle | TASK-024 | core/coordinator.py | Integration Test |
| V1 Success Criteria | TASK-027 | e2e/test_v1_core_workflow.py | End-to-End Test |

---

# 19. Source of Truth Traceability

Implementation 必须始终保持以下关系：

```text
Workflow Definition
→ PROJECT_INCUBATOR_V1_WORKFLOW_DESIGN.md

Workflow Interaction
→ PROJECT_INCUBATOR_V1_WORKFLOW_CONTRACT.md

Context Domain
→ PROJECT_INCUBATOR_V1_CONTEXT_MODEL_DESIGN.md

Context Permission
→ PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md

Gate Domain
→ PROJECT_INCUBATOR_V1_GATE_DESIGN.md

Gate Interaction
→ PROJECT_INCUBATOR_V1_GATE_CONTRACT.md

Advisory Domain
→ PROJECT_INCUBATOR_V1_PHASE_ADVISORY_DESIGN.md

Script Interaction
→ PROJECT_INCUBATOR_V1_SCRIPT_CONTRACT.md

Execution Mechanism
→ PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

Implementation
→ PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md
```

`references/*.json`

和：

`runtime/*.py`

都不是新的 Domain Source of Truth。

它们只是：

上游冻结定义的实现载体。

---

# 20. Upstream Design Gap Handling

Codex 在实现过程中如果发现：

某项实现需要一个上游没有定义的：

- Domain Rule；
- Gate Rule；
- Workflow Rule；
- Context Authority；
- Contract Result；
- Runtime Decision Rule；

必须：

停止该部分实现。

记录：

```text
UPSTREAM_DESIGN_GAP
```

必须指出：

- Gap 所属 Layer；
- 缺失定义；
- 当前 Task；
- 被阻止的 Generated File / Behavior。

Codex 不得：

自行补齐该 Domain Rule。

---

## 20.1 Non-blocking Implementation Choice

以下内容属于 Implementation Choice：

不属于 Upstream Design Gap：

- Python 文件拆分；
- JSON 文件路径；
- Class / Function 名；
- Test Organization；
- File I/O 实现；
- JSON Parsing；
- Python Standard Library 使用；
- Runtime internal object representation。

这些选择必须：

保持上游语义不变。

---

# 21. Optional Extension Boundary

V1 完成条件：

不依赖任何 Project Type Specific Extension。

未来如果实现：

- Project Type Specific Gate；
- Project Type Specific Advisory；
- Optional Context；
- Additional Script；

必须先确认：

上游 Design 已经定义对应领域规则。

Implementation Plan 不预先为未知 Extension 创建 Domain Logic。

---

# 22. Implementation Invariants

Codex 实现任何 Task 时：

必须始终满足以下规则。

### Invariant 1

不得修改 P0–P6 Core Phase。

### Invariant 2

不得新增 Workflow Transition。

### Invariant 3

不得新增 Gate Type。

### Invariant 4

不得改变任何 Gate Required Authorization。

### Invariant 5

不得改变 Context Authority。

### Invariant 6

PROJECT_STATE.md 始终是 Current Project State 唯一 Source of Truth。

### Invariant 7

Runtime State 不能替代 Project State。

### Invariant 8

Agent 不直接执行 Persisted Context Mutation。

### Invariant 9

Runtime 是 Context Persisted Mutation Executor。

### Invariant 10

Script 不直接读取 Core Context。

### Invariant 11

Script 不修改 Context。

### Invariant 12

Script Validation Result 不等于 Gate Evaluation Result。

### Invariant 13

Gate Result 不直接改变 Workflow、Context 或 Artifact。

### Invariant 14

Advisory 不产生 Runtime Command。

### Invariant 15

State Change Requirement 不等于 State 已经修改。

### Invariant 16

READY_FOR_TRANSITION 不等于 Transition 已经执行。

### Invariant 17

PROJECT_STATE 写入和验证成功后：

Phase Transition 才完成。

### Invariant 18

Maker Authorization：

只能来自 Maker。

### Invariant 19

Judgment-Based Gate：

不得自动转换为 Script Check。

### Invariant 20

上游未定义行为：

不得由 Codex 自行扩展。

---

# 23. Final Implementation Rule

Codex 必须严格按照：

```text
TASK-001
→
TASK-027
```

推进实现。

每一个 Task：

必须：

1. 完成规定 Scope；
2. 生成规定文件；
3. 执行规定 Validation；
4. Validation 全部通过；
5. 才能标记 Completed；
6. 再进入依赖该 Task 的后续 Task。

不得：

- 一次性跳过多个 Task 直接生成完整 Runtime；
- 在未验证前宣布 Task 完成；
- 为方便实现而修改冻结设计；
- 创建新的 Architecture / Design 文档；
- 将 Implementation Decision 写回上游 Source of Truth。

TASK-027 全部通过后：

Project Incubator V1 才进入：

```text
IMPLEMENTATION_COMPLETE
```

状态。

该状态表示：

当前 Implementation Plan 中定义的 V1 必须实现范围已经完成并通过验证。

不表示：

未来版本 Extension 已完成。