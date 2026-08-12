# Project Incubator V1 Context Access Contract

# 1. Contract Purpose

本文档定义 Project Incubator V1 中 Runtime 与 Context 之间的访问契约。

本文档属于：

Contract Layer。

本文档是以下内容的 Source of Truth：

- Read Permission；
- Write Permission；
- Mutation Authority；
- Access Boundary。

本文档依赖：

- `PROJECT_INCUBATOR_V1_DOCUMENT_ARCHITECTURE.md`；
- `PROJECT_INCUBATOR_V1_DESIGN.md`；
- `PROJECT_INCUBATOR_V1_WORKFLOW_DESIGN.md`；
- `PROJECT_INCUBATOR_V1_GATE_DESIGN.md`；
- `PROJECT_INCUBATOR_V1_CONTEXT_MODEL_DESIGN.md`；
- `PROJECT_INCUBATOR_V1_PHASE_ADVISORY_DESIGN.md`。

本文档不重新定义：

- Context Type；
- Context Responsibility；
- Context Lifecycle；
- Context Authority；
- Context Source of Truth；
- Workflow Domain Model；
- Gate Domain Model；
- Advisory Domain Model。

Context 的领域含义由：

`SPECS/DESIGN/PROJECT_INCUBATOR_V1_CONTEXT_MODEL_DESIGN.md`

定义。

Context Access Contract 只回答：

- 谁可以读取 Context；
- 谁可以提出 Context 修改；
- 谁可以授权 Context 修改；
- 谁可以执行 Context 修改；
- Context Access 必须满足什么边界。

具体 Runtime 如何加载、验证、执行、持久化和写回 Context，由：

`SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`

定义。

---

# 2. Context Access Model

## 2.1 Access Participants

Project Incubator V1 定义以下 Context Access Participant：

- Maker；
- Agent；
- Runtime；
- Workflow Runtime Component；
- Gate Runtime Component；
- Script。

各 Participant 的 Context Access Authority 相互独立。

一个 Participant 拥有某种访问能力，不代表同时拥有其他访问能力。

例如：

具备 Read Permission：

不代表具备 Mutation Permission。

具备 Mutation Request Permission：

不代表具备 Mutation Execution Authority。

---

## 2.2 Access Type

Context Access Contract 定义以下 Access Type：

### READ

读取已有 Context 信息。

READ 不产生 Context Mutation。

---

### REQUEST_MUTATION

提出 Context Mutation Request。

REQUEST_MUTATION 只表示：

存在修改请求。

不表示：

- 修改已经获得授权；
- Gate Requirement 已经满足；
- Runtime 可以立即执行修改；
- Context 已经发生变化。

---

### AUTHORIZE_MUTATION

对要求 Maker Authorization 的 Context Mutation 提供明确授权。

V1 中：

Maker 是唯一可以提供 Maker Authorization 的 Participant。

Agent、Runtime、Workflow Runtime Component、Gate Runtime Component 与 Script 均不得替代 Maker 提供 Maker Authorization。

---

### EXECUTE_MUTATION

执行已经满足 Contract Requirement 的 Context Mutation。

V1 中：

只有 Runtime 拥有 Context Mutation Execution Authority。

其他 Participant 均不得直接执行 Context Persisted Mutation。

---

## 2.3 Permission State

本文档使用以下 Permission State：

### ALLOW

Participant 在满足本 Contract 基础要求时拥有对应权限。

### CONDITIONAL

Participant 只有在本文档明确列出的条件满足时拥有对应权限。

条件未满足时：

等同于 DENY。

### DENY

Participant 不拥有对应权限。

---

# 3. Read Permission

## 3.1 Core Read Principle

Context Read 必须遵守：

- Context Authority；
- Context Responsibility；
- Source of Truth；
- 最小必要访问范围。

Read Permission 不允许 Participant：

- 改变 Context 内容；
- 改变 Context Authority；
- 使用非权威信息覆盖 Context Source of Truth。

---

## 3.2 Read Permission Matrix

| Participant | PROJECT_PROFILE.md | PROJECT_STATE.md | PROJECT_PLAN.md | PROJECT_DECISIONS.md | Optional Context |
| --- | --- | --- | --- | --- | --- |
| Maker | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |
| Agent | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |
| Runtime | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |
| Workflow Runtime Component | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL |
| Gate Runtime Component | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL |
| Script | DENY | DENY | DENY | DENY | DENY |

---

## 3.3 Maker Read Permission

Maker 可以读取：

- 所有 Core Context；
- 当前有效的 Optional Context。

Maker Read Permission 不受 Agent、Workflow 或 Gate 的判断结果限制。

Maker Read Permission 不等于：

Context Mutation Execution Authority。

---

## 3.4 Agent Read Permission

Agent 可以读取：

- `PROJECT_PROFILE.md`；
- `PROJECT_STATE.md`；
- `PROJECT_PLAN.md`；
- `PROJECT_DECISIONS.md`；
- 当前有效的 Optional Context。

Agent 必须优先使用 Context Source of Truth 判断项目事实。

Agent 不得使用以下内容覆盖 Context Source of Truth：

- 历史聊天记录；
- Agent 临时记忆；
- 未确认方案；
- 未持久化推测；
- Runtime 临时状态；
- Artifact 临时状态。

Agent Read Permission 不包含直接写权限。

---

## 3.5 Runtime Read Permission

Runtime 可以读取全部 Core Context 和当前有效 Optional Context。

Runtime Read Permission 的目的仅限于：

- 支撑 Workflow 执行；
- 支撑 Context Interaction；
- 支撑 Gate Evaluation；
- 支撑确定性执行；
- 支撑受控 Context Mutation。

Runtime 不得因为拥有 Read Permission：

重新定义 Context Authority。

---

## 3.6 Workflow Runtime Component Read Permission

Workflow Runtime Component 不拥有无条件 Context Read Permission。

Workflow Runtime Component 只有在以下条件之一满足时可以读取目标 Context：

1. 当前 Phase 的 Input 明确引用该 Context；
2. 当前 Phase 的 Required Artifact Requirement 明确依赖该 Context；
3. 当前 Workflow Requirement 明确依赖该 Context；
4. State Change Requirement 需要引用该 Context 中已经存在的项目事实。

读取范围必须限制在：

当前 Workflow Requirement 所需的 Context。

Workflow Runtime Component 不得为了扩展分析范围而读取无关 Context。

如果当前冻结的 Workflow Definition 没有引用某个 Context：

默认不得读取该 Context。

Workflow Runtime Component 不因 Read Permission 获得 Context Mutation Authority。

---

## 3.7 Gate Runtime Component Read Permission

Gate Runtime Component 只有在目标 Gate Definition 的 Evaluation Requirement 需要对应 Context Evidence 时可以读取 Context。

允许读取的内容必须与以下内容直接相关：

- Trigger Condition；
- Risk Object；
- Evaluation Requirement；
- Required Authorization。

Gate Runtime Component 不得读取与当前 Gate Evaluation 无关的 Context。

Gate Runtime Component 不因读取 Context 获得修改 Context 的权限。

---

## 3.8 Script Read Permission

Script 不拥有 Context Direct Read Permission。

Script 不得直接：

- 打开 Core Context；
- 遍历 Core Context；
- 获取未经过 Runtime 限定的完整 Context；
- 自主选择需要读取的 Context。

如果 Script 执行确定性检查需要 Context 信息：

由 Runtime 根据后续 Script Contract 提供明确、有限的输入数据。

Runtime 向 Script 提供 Context-derived Input：

不等于 Script 获得 Context Read Permission。

---

## 3.9 Optional Context Read Boundary

Optional Context 默认继承以下 Core Access Principle：

- Maker 可以读取；
- Agent 可以读取当前有效 Optional Context；
- Runtime 可以读取当前有效 Optional Context；
- Workflow Runtime Component 只有在 Workflow Requirement 明确依赖该 Optional Context 时可以读取；
- Gate Runtime Component 只有在 Gate Evaluation Requirement 明确依赖该 Optional Context 时可以读取；
- Script 不拥有 Direct Read Permission。

如果没有已冻结的 Project Type Extension 明确要求使用某个 Optional Context：

Workflow Runtime Component 与 Gate Runtime Component 默认不得扩大读取范围。

当前 `PROJECT_ARTIFACTS.md` 作为 Optional Context 时：

必须遵守本节规则。

---

# 4. Write Permission

## 4.1 Write Separation Principle

Project Incubator V1 将 Context 修改划分为三个不同权限：

1. Mutation Request；
2. Mutation Authorization；
3. Mutation Execution。

三种权限不得合并。

---

## 4.2 Direct Write Rule

除 Runtime 外：

任何 Participant 均不得直接执行 Persisted Context Write。

因此：

Maker：

不拥有 Runtime 内部的 EXECUTE_MUTATION Authority。

Agent：

不拥有 EXECUTE_MUTATION Authority。

Workflow Runtime Component：

不拥有 EXECUTE_MUTATION Authority。

Gate Runtime Component：

不拥有 EXECUTE_MUTATION Authority。

Script：

不拥有 EXECUTE_MUTATION Authority。

Runtime：

是 V1 唯一 Context Mutation Executor。

---

## 4.3 Mutation Request Permission Matrix

| Participant | PROJECT_PROFILE.md | PROJECT_STATE.md | PROJECT_PLAN.md | PROJECT_DECISIONS.md | Optional Context |
| --- | --- | --- | --- | --- | --- |
| Maker | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |
| Agent | ALLOW | CONDITIONAL | ALLOW | ALLOW | ALLOW |
| Runtime | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL |
| Workflow Runtime Component | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL |
| Gate Runtime Component | DENY | DENY | DENY | DENY | DENY |
| Script | DENY | DENY | DENY | DENY | DENY |

---

## 4.4 Maker Mutation Request

Maker 可以针对任意 Core Context 或当前 Optional Context提出 Mutation Request。

Maker 提出 Mutation Request：

不代表该 Request 可以绕过：

- Context Boundary；
- Gate Requirement；
- Context Authority；
- Context Lifecycle。

如果 Maker Request 本身要求改变已经冻结的 Context Domain Model 或 Source of Truth Definition：

该请求不属于普通 Context Mutation。

必须返回：

`BOUNDARY_VIOLATION`。

---

## 4.5 Agent Mutation Request

Agent 可以提出：

- `PROJECT_PROFILE.md` Mutation Request；
- `PROJECT_PLAN.md` Mutation Request；
- `PROJECT_DECISIONS.md` Mutation Request；
- Optional Context Mutation Request。

Agent 对 `PROJECT_STATE.md` 的 Mutation Request 为 CONDITIONAL。

只有当 Request 基于以下内容之一时才允许提出：

- Workflow 已形成的 State Change Requirement；
- Runtime 已确认的确定性执行事实；
- Maker 明确要求处理的状态纠正。

Agent 不得仅根据：

- 自己的推测；
- 历史聊天；
- 未确认计划；
- 个人判断；

提出将某个事实写入 `PROJECT_STATE.md` 的 Mutation Request。

Agent REQUEST_MUTATION：

永远不等于 Agent 可以直接写入 Context。

---

## 4.6 Runtime Mutation Request

Runtime 可以构造 Context Mutation Request。

Runtime-originated Mutation Request 必须机械地来源于已经存在的上游依据。

允许依据包括：

- Workflow Output；
- State Change Requirement；
- 已满足的 Gate Requirement；
- Maker 已确认的信息；
- 已验证的确定性执行结果；
- Context Lifecycle Requirement；
- 已确认的 Project Type Context Requirement。

Runtime 不得自行创造新的：

- Project Goal；
- Project Scope；
- Maker Decision；
- Context Authority；
- Domain Fact。

Runtime 不能通过自行生成 Mutation Request 获得新的决策权。

---

## 4.7 Workflow Runtime Component Mutation Request

Workflow Runtime Component 只有在 Workflow Domain Model 已明确产生以下内容时可以提出对应 Mutation Request：

- Context 作为 Phase Output；
- State Change Requirement；
- Workflow 明确要求更新的 Context；
- Maker 已确认 Decision 需要记录至 `PROJECT_DECISIONS.md`。

Workflow Runtime Component 不得：

- 自行决定新的 Context Type；
- 自行创造 Context Domain Fact；
- 自行扩大 Context Mutation Scope。

Workflow Runtime Component 只可以表达：

Workflow 已经定义的 Context Change Requirement。

---

## 4.8 Gate Runtime Component Mutation Permission

Gate Runtime Component：

不得提出 Context Mutation Request。

Gate Runtime Component 只负责向 Runtime 提供当前 Gate Evaluation 所需结果。

Gate Evaluation：

不得直接转化为 Context Write。

如果 Gate 状态需要反映到 `PROJECT_STATE.md`：

必须由 Runtime 根据 Workflow、Gate Contract 和本 Contract 形成独立 Mutation Request。

---

## 4.9 Script Mutation Permission

Script：

不得提出 Context Mutation Request。

Script：

不得直接修改任何 Core Context 或 Optional Context。

Script 只能返回：

后续 Script Contract 所定义的确定性结果。

Script Result：

不得被视为 Context Mutation 本身。

---

# 5. Mutation Authority

## 5.1 Mutation Authority Model

Context Mutation Authority 包含：

### Proposal Authority

谁可以提出修改。

### Authorization Authority

当修改需要 Maker Authorization 时，由谁提供授权。

### Execution Authority

谁可以实际执行持久化修改。

V1 固定：

- Maker 是唯一 Maker Authorization Authority；
- Runtime 是唯一 Context Mutation Execution Authority。

---

## 5.2 Mutation Authority Matrix

| Context | Proposal Authority | Maker Authorization Requirement | Execution Authority |
| --- | --- | --- | --- |
| PROJECT_PROFILE.md | Maker / Agent / Runtime / Workflow Runtime Component | REQUIRED | Runtime |
| PROJECT_STATE.md | Maker / Agent（Conditional）/ Runtime / Workflow Runtime Component | CONDITIONAL | Runtime |
| PROJECT_PLAN.md | Maker / Agent / Runtime / Workflow Runtime Component | CONDITIONAL | Runtime |
| PROJECT_DECISIONS.md | Maker / Agent / Runtime / Workflow Runtime Component | REQUIRED | Runtime |
| Optional Context | Maker / Agent / Runtime / Workflow Runtime Component（Conditional） | CONDITIONAL | Runtime |

Gate Runtime Component 和 Script：

均不拥有 Proposal Authority 或 Execution Authority。

---

# 6. PROJECT_PROFILE.md Mutation Contract

## 6.1 Mutation Boundary

`PROJECT_PROFILE.md` 表达：

- 项目身份；
- 项目类型；
- Intent；
- 用户对象；
- 成功标准；
- 长期约束。

Mutation 不得写入：

- 当前执行状态；
- 临时任务；
- 未来执行计划；
- 未确认方案。

---

## 6.2 Maker Authorization

任何对 `PROJECT_PROFILE.md` 的创建或实质性修改：

必须具有 Maker 明确确认。

任何修改 `PROJECT_PROFILE.md` 的行为：

同时属于 Authority Document Gate 的保护范围。

Runtime 执行 Mutation 前：

必须存在满足对应 Gate Requirement 的 Evidence。

本 Contract 不定义 Gate Evaluation Result 的具体结构。

该结构由：

`PROJECT_INCUBATOR_V1_GATE_CONTRACT.md`

定义。

---

## 6.3 Allowed Mutation Intent

V1 对 `PROJECT_PROFILE.md` 支持：

- `CREATE_CONTEXT`；
- `UPDATE_CONTEXT`。

不支持通过普通 Context Mutation：

- 将 `PROJECT_PROFILE.md` 转换为其他 Context Type；
- 改变其 Authority Scope；
- 改变其 Source of Truth 职责。

---

# 7. PROJECT_STATE.md Mutation Contract

## 7.1 Mutation Boundary

`PROJECT_STATE.md` 是项目当前实际状态的唯一 Source of Truth。

Mutation 只允许反映已经成为当前事实的内容。

不得将以下内容写入 `PROJECT_STATE.md`：

- 未来计划；
- 未执行方案；
- 设计讨论；
- Agent 推测；
- Runtime 临时状态。

---

## 7.2 Normal State Mutation Basis

正常状态 Mutation 必须存在明确 State Change Basis。

允许的 Basis：

- Workflow State Change Requirement；
- Workflow 已完成事项产生的当前事实；
- 已完成 Gate 处理产生的当前 Gate 状态事实；
- 已验证的执行结果形成的当前事实。

Runtime 不得仅根据自身临时 Runtime State：

更新 `PROJECT_STATE.md`。

---

## 7.3 Phase-related State Mutation

如果 `PROJECT_STATE.md` Mutation 涉及：

- Current Phase；
- Phase State；
- Phase Transition；
- Phase Skip；
- Phase Rollback；

必须同时满足：

- Workflow Transition Boundary；
- Phase Gate Requirement。

如果 Gate 要求 Maker Authorization：

必须包含 Maker Authorization Evidence。

---

## 7.4 Context Recovery Mutation

如果 Mutation 的目的属于：

重建具有长期影响的项目状态，

必须：

- 进入 Context Integrity Gate；
- 获得 Maker 明确授权。

如果当前 Context 已知不完整，但请求仍要求执行高影响状态修改：

必须遵守 Context Integrity Gate 的 Required Authorization。

---

## 7.5 Allowed Mutation Intent

V1 对 `PROJECT_STATE.md` 支持：

- `CREATE_CONTEXT`；
- `UPDATE_CONTEXT`。

不允许：

- 用其他 Context 替代 `PROJECT_STATE.md`；
- 将 Runtime State 直接持久化为 Project State；
- 改变 `PROJECT_STATE.md` 的 Source of Truth Authority。

---

# 8. PROJECT_PLAN.md Mutation Contract

## 8.1 Mutation Boundary

`PROJECT_PLAN.md` 只表达：

当前有效的未来执行计划。

Mutation 可以涉及：

- 阶段目标；
- 阶段任务；
- 执行顺序；
- 依赖关系；
- 预期 Artifact；
- 风险；
- 验证方式。

不得通过 `PROJECT_PLAN.md` Mutation：

写入当前实际执行状态。

---

## 8.2 Proposal Authority

Maker、Agent、Runtime 和符合 Workflow Requirement 的 Workflow Runtime Component：

可以提出 `PROJECT_PLAN.md` Mutation Request。

---

## 8.3 Maker Authorization Requirement

普通计划调整：

如果没有触发任何要求 Maker Authorization 的 Gate：

不额外要求 Maker Authorization。

如果 Plan Mutation 同时改变：

- Project Goal；
- Project Scope；
- Architecture Decision；
- 已冻结长期规则；
- 其他 Gate Definition 明确要求 Maker Authorization 的对象；

则必须先满足对应 Gate Required Authorization。

Context Access Contract 不得通过 Plan Mutation：

绕过 Scope Gate、Architecture Decision Gate 或其他 Gate。

---

## 8.4 Workflow Boundary

Execution Planning 产生 `PROJECT_PLAN.md` 时：

Workflow Runtime Component 可以形成对应 Mutation Request。

Iteration 对 `PROJECT_PLAN.md` 进行实际调整时：

Workflow Runtime Component 可以形成对应 Mutation Request。

Workflow Requirement 只提供 Mutation Basis。

Runtime 仍是唯一 Execution Authority。

---

## 8.5 Allowed Mutation Intent

V1 对 `PROJECT_PLAN.md` 支持：

- `CREATE_CONTEXT`；
- `UPDATE_CONTEXT`。

不得通过 Plan Mutation：

改变 `PROJECT_STATE.md`。

---

# 9. PROJECT_DECISIONS.md Mutation Contract

## 9.1 Mutation Boundary

`PROJECT_DECISIONS.md` 只保存：

Maker 已确认的重要项目决策。

不得记录：

- 普通讨论；
- 临时想法；
- Agent 自主判断；
- 未确认方案。

---

## 9.2 Maker Authorization

任何新增 Decision Record：

必须存在 Maker 明确确认。

Agent Proposal：

不能作为 Maker Authorization Evidence。

Runtime 判断：

不能作为 Maker Authorization Evidence。

Advisory Decision Needed：

不能作为 Maker Authorization Evidence。

---

## 9.3 Append-only Rule

`PROJECT_DECISIONS.md` 的历史 Decision：

不得覆盖。

V1 对 `PROJECT_DECISIONS.md` 的正常 Mutation Mode 为：

`APPEND_RECORD`。

新的已确认 Decision：

通过新的 Decision Record 追加。

普通 Context Mutation 不允许：

- 覆盖已有 Decision；
- 删除已有 Decision；
- 将未确认 Decision Proposal 写成已确认 Decision。

---

## 9.4 Gate Requirement

修改 `PROJECT_DECISIONS.md`：

属于 Authority Document Gate 的保护范围。

Runtime 执行 Append 前：

必须存在对应 Maker Authorization 和 Gate Requirement Evidence。

---

# 10. Optional Context Mutation Contract

## 10.1 Optional Context Boundary

Optional Context 只保存：

对应 Project Type 的扩展上下文。

Optional Context 不得：

- 覆盖 `PROJECT_PROFILE.md` Authority；
- 覆盖 `PROJECT_STATE.md` Authority；
- 覆盖 `PROJECT_PLAN.md` Authority；
- 覆盖 `PROJECT_DECISIONS.md` Authority；
- 重新定义 Core Context Model。

---

## 10.2 Creation Requirement

创建 Optional Context 必须满足：

- 当前 Project Type 存在 Core Context 无法表达的额外 Context Requirement；
- Optional Context 已具有明确的数据职责；
- Optional Context 已具有明确 Authority Scope。

Runtime 不得仅为了存储方便创建 Optional Context。

---

## 10.3 Proposal Authority

Maker、Agent 和 Runtime 可以提出 Optional Context Mutation Request。

Workflow Runtime Component：

只有在已经冻结的 Workflow 或 Project Type Extension 明确产生对应 Optional Context Requirement 时才能提出 Request。

Gate Runtime Component：

不得提出。

Script：

不得提出。

---

## 10.4 Authorization Requirement

Optional Context 的普通创建或更新：

如果没有触发任何要求 Maker Authorization 的 Gate：

不额外要求 Maker Authorization。

如果 Mutation：

- 改变 Project Scope；
- 影响 Core Context Authority；
- 修改受 Gate 保护的长期规则；
- 影响其他需要 Maker Authorization 的 Risk Object；

则必须满足对应 Gate Required Authorization。

---

## 10.5 Retirement

当 Optional Context 对应的 Project Type Context Requirement 不再适用时：

可以形成：

`RETIRE_OPTIONAL_CONTEXT`

Mutation Request。

Retire 表示：

该 Optional Context 不再作为当前有效扩展 Context 参与项目。

Retire 不允许：

通过删除或覆盖 Core Context 来完成。

---

## 10.6 PROJECT_ARTIFACTS.md

当前 Context Model 中的：

`PROJECT_ARTIFACTS.md`

属于 Optional Context Extension。

其 Access 和 Mutation：

必须遵守本章全部规则。

其内容不得替代：

- `PROJECT_STATE.md`；
- Workflow Artifact Flow；
- Core Context Authority。

---

# 11. Access Boundary

## 11.1 Agent Direct Modification Prohibited

Agent 不得：

- 直接写入 Core Context；
- 直接写入 Optional Context；
- 绕过 Runtime 执行 Persisted Mutation；
- 将自身判断直接持久化为项目事实；
- 将未确认信息写入 Maker-authoritative Context。

Agent 必须使用：

REQUEST_MUTATION。

---

## 11.2 Runtime Self-authorization Prohibited

Runtime 可以执行 Mutation。

Runtime 不可以：

- 自行提供 Maker Authorization；
- 自行改变 Project Goal；
- 自行扩大 Project Scope；
- 自行产生 Maker Decision；
- 自行改变 Context Source of Truth；
- 通过内部 Runtime State 覆盖 `PROJECT_STATE.md`。

Runtime Execution Authority：

不是 Domain Decision Authority。

---

## 11.3 Workflow Boundary

Workflow Runtime Component 不得：

- 直接写 Context；
- 自行创建 Workflow 未定义的 Context Change；
- 将 State Change Requirement 当作已经完成的 State Mutation。

Workflow State Change Requirement：

只构成 Mutation Basis。

---

## 11.4 Gate Boundary

Gate Runtime Component 不得：

- 修改 Context；
- 将 Gate Evaluation 直接写入 Context；
- 绕过 Runtime；
- 获得 Context Mutation Authority。

Gate 只提供：

Context Mutation 是否满足相关 Gate Requirement 所需的控制信息。

---

## 11.5 Script Boundary

Script 不得：

- Direct Read Core Context；
- Direct Write Context；
- 修改 Project State；
- 推进 Phase；
- 绕过 Gate；
- 将 Validation Result 直接持久化为 Context Fact。

Script 必须通过 Runtime 获得限定输入并返回确定性结果。

---

## 11.6 Authority Boundary

任何 Access 或 Mutation：

不得改变 Context Model 已冻结的 Authority 分配。

以下请求必须返回：

`BOUNDARY_VIOLATION`

而不是执行普通 Mutation：

- 将未来计划写入 `PROJECT_STATE.md`；
- 将当前状态写入 `PROJECT_PLAN.md` 作为状态 Authority；
- 将临时任务写入 `PROJECT_PROFILE.md`；
- 将未确认方案写入 `PROJECT_DECISIONS.md`；
- 使用 Optional Context 覆盖 Core Context Authority；
- 将其他数据源设为新的 Current State Source of Truth。

---

## 11.7 Source of Truth Conflict

如果 Access Request 或 Mutation Request 使用的信息与 Context Source of Truth 冲突：

不得自动选择非权威信息覆盖当前 Context。

必须返回：

`CONTEXT_CONFLICT`。

如果冲突影响可靠判断：

应继续遵守 Context Integrity Gate。

---

## 11.8 Gate-protected Mutation

如果某个 Mutation 命中 Gate Design 已定义的 Trigger Condition：

Runtime 执行 Mutation 前：

必须具有对应 Gate Requirement 已处理的 Evidence。

Context Access Contract：

不定义 Gate Evaluation Result。

Gate Evaluation Result 由：

`SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_GATE_CONTRACT.md`

定义。

---

# 12. Context Access Request Contract

## 12.1 Definition

Context Access Request 表达：

一个 Participant 请求进行一次 Context Access。

Context Access Request 只定义交互信息。

不定义：

Runtime 如何处理该 Request。

---

## 12.2 Required Contract Fields

每一个 Context Access Request 必须包含：

- Request ID；
- Access Target；
- Access Type；
- Request Source；
- Access Purpose。

---

## 12.3 Access Target

Access Target 必须标识：

- Context Type；
- Context Instance / Context Reference。

允许的 Context Type：

- `PROJECT_PROFILE`；
- `PROJECT_STATE`；
- `PROJECT_PLAN`；
- `PROJECT_DECISIONS`；
- `OPTIONAL_CONTEXT`。

Optional Context：

还必须标识具体 Optional Context Identity。

Access Target 不定义 Context 内部业务字段 Schema。

---

## 12.4 Access Type

Access Type 必须是：

- `READ`；
- `REQUEST_MUTATION`；
- `AUTHORIZE_MUTATION`；
- `EXECUTE_MUTATION`。

不允许使用未在本 Contract 定义的 Access Type。

---

## 12.5 Request Source

Request Source 必须是：

- `MAKER`；
- `AGENT`；
- `RUNTIME`；
- `WORKFLOW_RUNTIME_COMPONENT`；
- `GATE_RUNTIME_COMPONENT`；
- `SCRIPT`。

Request Source 必须对应实际访问参与方。

不得伪装为其他 Participant。

---

## 12.6 Access Purpose

Access Purpose 必须说明本次访问所对应的系统职责。

对于 CONDITIONAL Permission：

Access Purpose 必须能够关联到允许该访问的上游 Requirement。

包括：

- Workflow Requirement；
- Gate Evaluation Requirement；
- Context Lifecycle Requirement；
- Maker Request；
- Runtime deterministic execution requirement。

Access Purpose：

不得用作扩大访问权限的理由。

---

# 13. Mutation Intent Contract

## 13.1 Required Condition

当 Access Type 为：

`REQUEST_MUTATION`

时：

Context Access Request 必须包含 Mutation Intent。

---

## 13.2 Mutation Intent

Mutation Intent 必须包含：

- Mutation Type；
- Target Context；
- Change Purpose；
- Change Basis；
- Proposed Change Reference。

---

## 13.3 Mutation Type

V1 定义以下 Mutation Type：

- `CREATE_CONTEXT`；
- `UPDATE_CONTEXT`；
- `APPEND_RECORD`；
- `RETIRE_OPTIONAL_CONTEXT`。

使用限制：

`APPEND_RECORD`：

用于 `PROJECT_DECISIONS.md`。

`RETIRE_OPTIONAL_CONTEXT`：

只用于 Optional Context。

Core Context 不支持普通 Delete / Retire Mutation。

---

## 13.4 Change Basis

Change Basis 必须能够追溯到至少一个有效依据：

- Maker Confirmed Change；
- Workflow Output；
- Workflow State Change Requirement；
- Confirmed Decision；
- Validated Execution Fact；
- Context Lifecycle Requirement；
- Project Type Context Requirement。

Mutation Request 不得使用：

- Agent Guess；
- Unconfirmed Plan；
- Historical Chat Assumption；
- Runtime Temporary State；

作为唯一 Change Basis。

---

# 14. Authorization Evidence Contract

## 14.1 Required Condition

当目标 Mutation 满足以下任一条件时：

Authorization Evidence 为必填：

- 修改 `PROJECT_PROFILE.md`；
- 新增 `PROJECT_DECISIONS.md` Decision Record；
- Gate Definition 明确要求 Maker Authorization；
- 重建具有长期影响的项目状态；
- 其他已经冻结的 Gate Requirement 明确要求 Maker Authorization。

---

## 14.2 Authorization Evidence Semantics

Authorization Evidence 必须能够证明：

- Authorization 来自 Maker；
- Authorization 对应当前 Mutation；
- Authorization 对应当前 Risk Object 或受保护行为；
- Authorization 没有被用于批准其他未授权修改。

本 Contract 不定义：

- Authorization UI；
- Prompt；
- Confirmation Interaction；
- Runtime Capture Mechanism。

---

## 14.3 Invalid Authorization

以下内容不能作为 Maker Authorization Evidence：

- Agent Recommendation；
- Agent Assumption；
- Advisory Response；
- Runtime Decision；
- Script Result；
- Gate 自身的判断；
- 历史未对应当前 Mutation 的 Maker 表述。

---

# 15. Gate Evidence Reference

## 15.1 Required Condition

当 Mutation 命中 Gate Trigger Condition 时：

Context Access Request 必须能够关联对应 Gate Evidence。

---

## 15.2 Boundary

本 Contract 只要求存在 Gate Evidence Reference。

不定义：

- Gate Input；
- Gate Output；
- Evaluation Result；
- Gate Invocation；
- Gate Runtime Execution。

这些内容由：

`PROJECT_INCUBATOR_V1_GATE_CONTRACT.md`

和：

`PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`

定义。

---

# 16. Context Access Result Contract

## 16.1 Definition

Context Access Result 表达：

一次 Context Access Request 的 Contract-level 判定结果。

Context Access Result：

不描述 Runtime 内部执行步骤。

---

## 16.2 Result Status

V1 定义以下唯一 Result Status：

- `ACCEPTED`；
- `REJECTED`；
- `AUTHORIZATION_REQUIRED`；
- `GATE_REQUIREMENT_UNRESOLVED`；
- `BOUNDARY_VIOLATION`；
- `CONTEXT_CONFLICT`。

---

## 16.3 ACCEPTED

表示：

当前 Request 满足本 Contract 的访问条件。

对于 READ：

表示允许执行对应读取。

对于 REQUEST_MUTATION：

表示 Mutation Request 可以进入后续受控处理。

对于 EXECUTE_MUTATION：

表示 Contract 层面已经具备执行资格。

`ACCEPTED`：

不等于 Runtime 已经完成持久化。

---

## 16.4 REJECTED

表示：

Request 不具备目标 Access Type 所要求的 Permission。

典型情况：

- Request Source 没有对应权限；
- CONDITIONAL Permission 的条件未满足；
- Request 缺少必要 Contract 信息；
- Script 请求 Direct Context Access；
- Gate Runtime Component 请求 Context Mutation。

---

## 16.5 AUTHORIZATION_REQUIRED

表示：

Request 在其他 Contract Boundary 上可以成立，

但当前缺少必须存在的 Maker Authorization。

该状态不得被 Runtime 自动转换为 ACCEPTED。

---

## 16.6 GATE_REQUIREMENT_UNRESOLVED

表示：

目标 Access 或 Mutation 已命中 Gate Requirement，

但当前没有足够 Evidence 证明该 Gate Requirement 已完成处理。

Context Access Contract：

不得自行将该结果改为 Gate PASS。

---

## 16.7 BOUNDARY_VIOLATION

表示：

Request 本身违反已经冻结的 Context Responsibility、Context Authority 或 Access Boundary。

包括：

- 写入错误 Context；
- Optional Context 覆盖 Core Context；
- Request 要求改变 Source of Truth；
- Request 要求 Participant 获得未授权能力；
- Request 要求绕过 Runtime Direct Write。

Boundary Violation：

不能仅通过 Maker Authorization 转化为普通 Mutation。

如果 Request 实际要求修改上游 Domain Model：

必须回到对应 Design Layer。

---

## 16.8 CONTEXT_CONFLICT

表示：

当前 Request 依赖的信息与已有权威 Context 发生冲突。

发生 Context Conflict 时：

不得自动使用非权威信息覆盖 Authority Context。

需要重新确认：

- Authority Context；
- Context Integrity；
- 必要的 Maker Clarification。

---

## 16.9 Result Fields

Context Access Result 必须能够表达：

- Request ID；
- Result Status；
- Access Target；
- Requested Access Type；
- Decision Reason；
- Missing Requirement；
- Authorization Requirement；
- Gate Requirement Reference；
- Conflict Reference；
- Boundary Reference。

不存在的项目：

必须明确表示为空。

不得通过省略 Result Status 表达隐含结果。

---

# 17. Participant Permission Summary

## 17.1 Maker

Maker：

可以：

- Read 全部 Context；
- Request 全部 Context Mutation；
- 提供 Maker Authorization。

Maker：

不是 Runtime Context Mutation Executor。

Maker Request：

不能绕过 Context Domain Boundary。

---

## 17.2 Agent

Agent：

可以：

- Read Core Context；
- Read 当前有效 Optional Context；
- 提出允许范围内的 Mutation Request；
- 分析 Mutation 影响。

Agent：

不可以：

- Direct Write Context；
- 自己授权需要 Maker Authorization 的 Mutation；
- 使用推测覆盖 Source of Truth；
- 将 Advisory 自动转化为 Context Mutation；
- 自行改变项目当前状态。

---

## 17.3 Runtime

Runtime：

可以：

- Read 全部有效 Context；
- 根据有效上游依据形成 Mutation Request；
- 执行满足 Contract Requirement 的 Context Mutation。

Runtime：

不可以：

- 自己提供 Maker Authorization；
- 自行创建新的 Domain Fact；
- 绕过 Gate；
- 修改 Context Authority；
- 修改 Context Source of Truth 定义。

---

## 17.4 Workflow Runtime Component

Workflow Runtime Component：

可以：

- 读取当前 Workflow Requirement 明确依赖的 Context；
- 根据 Phase Output 或 State Change Requirement 提出 Mutation Request。

Workflow Runtime Component：

不可以：

- Direct Write；
- 读取无关 Context；
- 自行扩大 Mutation Scope；
- 将 Workflow Requirement 视为已完成 Mutation。

---

## 17.5 Gate Runtime Component

Gate Runtime Component：

可以：

- 读取 Gate Evaluation Requirement 所需的限定 Context。

Gate Runtime Component：

不可以：

- 提出 Context Mutation；
- 执行 Context Mutation；
- 将 Gate Decision 直接写入 Context；
- 使用 Context 修改自身 Gate Definition。

---

## 17.6 Script

Script：

不拥有 Direct Context Access Authority。

Script：

不可以：

- Direct Read；
- Request Mutation；
- Authorize Mutation；
- Execute Mutation。

Script 需要的 Context-derived Data：

只能由 Runtime 根据 Script Contract 提供。

---

# 18. Contract Boundary

## 18.1 Context Model Design

`PROJECT_INCUBATOR_V1_CONTEXT_MODEL_DESIGN.md`

负责定义：

- Context Type；
- Context Responsibility；
- Context Lifecycle；
- Context Authority；
- Context Source of Truth。

本 Contract 不重新定义上述内容。

---

## 18.2 Context Access Contract

本文档负责定义：

- Read Permission；
- Write Permission；
- Mutation Request Permission；
- Mutation Authorization；
- Mutation Execution Authority；
- Access Boundary；
- Access Request Contract；
- Access Result Contract。

---

## 18.3 Workflow Contract

后续：

`PROJECT_INCUBATOR_V1_WORKFLOW_CONTRACT.md`

负责定义 Workflow Runtime Interface。

Workflow Contract：

不得重新定义本文件中的 Context Access Permission。

---

## 18.4 Gate Contract

后续：

`PROJECT_INCUBATOR_V1_GATE_CONTRACT.md`

负责定义：

- Gate Invocation Contract；
- Gate Input；
- Gate Output；
- Evaluation Result。

本 Contract 只引用 Gate Requirement。

不重新定义 Gate Evaluation Result。

---

## 18.5 Script Contract

后续：

`PROJECT_INCUBATOR_V1_SCRIPT_CONTRACT.md`

负责定义 Runtime 与 Script 之间的：

- Script Input；
- Script Output；
- Error Handling；
- Validation Result。

Script Contract：

不得通过 Script Input 赋予 Script Direct Context Access Authority。

---

## 18.6 Runtime Specification

`PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`

负责定义：

- Runtime 如何调用 Context Access Contract；
- Context 如何被加载；
- Access Request 如何被处理；
- Mutation 如何被验证；
- Mutation 如何执行；
- Context 如何持久化；
- Context 如何写回。

Runtime Specification：

不得重新定义本 Contract 的 Permission 或 Mutation Authority。

---

# 19. Source of Truth Rule

Project Incubator V1 Context 相关 Source of Truth 固定如下：

Context 是什么、保存什么、生命周期和领域 Authority：

`PROJECT_INCUBATOR_V1_CONTEXT_MODEL_DESIGN.md`

Context 谁可以读取、谁可以修改、谁可以授权、谁可以执行 Mutation：

`PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md`

Workflow 何时产生 Context Change Requirement：

`PROJECT_INCUBATOR_V1_WORKFLOW_DESIGN.md`

Gate 哪些 Context 变化需要保护与 Maker Authorization：

`PROJECT_INCUBATOR_V1_GATE_DESIGN.md`

Runtime 如何执行上述 Contract：

`PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md`

低层文档不得重新定义高层 Domain Model。

Runtime 不得重新定义 Contract。

Contract 不得重新定义 Design。

---

# 20. V1 Contract Summary

Project Incubator V1 Context Access Contract 采用：

```text
Context Domain Model
        ↓
Context Access Contract
        ↓
Runtime Execution
```

核心访问原则：

1. Maker、Agent 和 Runtime 可以读取 Core Context。

2. Workflow Runtime Component 与 Gate Runtime Component 只能进行 Requirement-scoped Read。

3. Script 不拥有 Direct Context Read Permission。

4. Agent 可以提出 Context Mutation Request，但不能直接写 Context。

5. Maker 是 Maker Authorization 的唯一来源。

6. Runtime 是唯一 Context Mutation Execution Authority。

7. Workflow Runtime Component 可以表达 Workflow 已定义的 Context Change Requirement，但不能直接修改 Context。

8. Gate Runtime Component 不拥有 Context Mutation Authority。

9. Script 不拥有 Context Mutation Authority。

10. `PROJECT_PROFILE.md` 的创建和实质性修改必须获得 Maker Authorization。

11. `PROJECT_STATE.md` 只能记录当前实际状态，并必须基于有效 State Change Basis。

12. `PROJECT_PLAN.md` 只能记录当前有效未来计划。

13. `PROJECT_DECISIONS.md` 只记录 Maker 已确认的重要决策，并采用 Append-only 原则。

14. Optional Context 不得覆盖 Core Context Authority。

15. 任何 Mutation 如果触发 Gate Requirement，都必须在 Runtime 执行前满足对应 Gate Requirement。

16. Access Request 与权威 Context 冲突时，不得自动覆盖 Source of Truth。

17. Context Access Contract 不定义 Runtime Execution Flow。

18. Runtime Specification 必须依赖本 Contract 实现 Context Interaction。