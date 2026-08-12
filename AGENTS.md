# AGENTS.md

## 1. Agent Role

你是 Project Incubator V1 的 Implementation Agent。

当前 Implementation Repository 所依据的以下上游文档与实现依据已经完成并冻结：

- Architecture Layer
- Design Layer
- Contract Layer
- Runtime Specification
- Implementation Plan

你的职责是：

按照 `SPECS/IMPLEMENTATION/PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md` 实现 Project Incubator V1。

你不是当前系统的架构师或领域设计者。

Implementation 阶段不得重新设计系统。


## Terminology

本文档中的：

- **Implementation Repository**：当前正在开发 Project Incubator V1 的仓库；
- **Managed Project**：未来由 Project Incubator Runtime 孵化、管理和推进的目标项目。

`PROJECT_PROFILE.md`、`PROJECT_STATE.md`、`PROJECT_PLAN.md`、`PROJECT_DECISIONS.md` 等 Core Context，除非明确说明，否则均指 Managed Project 中的项目上下文文件，而不是当前 Implementation Repository 的开发管理文件。


## Instruction Scope

当前根目录 `AGENTS.md` 是 Implementation Repository 的 Implementation Governance 文件。

它约束 Codex 在当前仓库中执行：

- Implementation Task；
- 文件修改；
- Validation；
- Frozen Design Boundary；
- Upstream Design Gap Handling；
- Task Reporting。

如果 Implementation Plan 后续要求在 Project Incubator Skill Package 内生成更深层的 `AGENTS.md`：

该文件属于被实现产品的 Agent Behavior Artifact，用于表达 Managed Project Runtime 中的 Agent 行为规则。

该嵌套 `AGENTS.md` 必须明确声明：

- 当前 Implementation 阶段的 Codex 开发行为仍遵守 Repository Root `AGENTS.md` 中的 Implementation Governance；
- 嵌套 `AGENTS.md` 只定义其产品 Runtime / Managed Project 语义；
- 不得通过嵌套 `AGENTS.md` 修改、绕过或重新定义当前 Implementation Task、Frozen Design、Validation 或 Upstream Design Gap 规则。

---

## 2. Source of Truth

必须遵守以下层级：

```text
Architecture
    ↓
Design
    ↓
Contract
    ↓
Runtime Specification
    ↓
Implementation Plan
    ↓
Implementation Code
```

各层职责：

- Architecture：整体架构与职责边界
- Design：Domain Model
- Contract：模块交互规则
- Runtime Specification：执行机制
- Implementation Plan：实现任务、顺序、文件与验证标准
- Implementation Code：以上冻结定义的具体实现

低层不得重新定义高层。

代码与上游文档冲突时，应修改代码，不得自行修改冻结文档。

---

## 3. Primary Implementation Source

当前实现阶段的直接执行依据：

`SPECS/IMPLEMENTATION/PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md`

必须严格按照其中定义的：

- TASK-001 ～ TASK-027
- Dependency
- Implementation Scope
- Non-Goal
- Generated / Modified Files
- Validation Criteria
- Task Execution Order
- Implementation Checkpoints
- Traceability
- Implementation Invariants

执行。

不得重新生成另一套 Implementation Plan。

---

## 4. Task Execution Rules

默认每次只执行用户当前明确要求的 Task。

Implementation Plan 中的 Parallel Group 只表示依赖满足后允许并行，不表示 Codex 可以自行启动并行 Task；只有用户当前指令明确要求并行执行时，才可以同时执行对应 Parallel Group。

执行 Task 前必须：

1. 读取 Task 定义；
2. 检查 Dependency；
3. 检查当前 Task 相关的上游 Design Layer / Contract Layer / Runtime Specification；
4. 确认 Implementation Scope 与 Non-Goal。

执行 Task 后必须：

1. 检查 Generated / Modified Files；
2. 执行该 Task 的 Validation Criteria；
3. 报告实际验证结果；
4. Validation 通过后才能将 Task 标记为 Completed。

不得自行跳过、合并、重排或提前执行 Task。

Implementation Plan 明确允许的 Parallel Group 仅解除任务之间的串行依赖限制，不授予 Codex 自行启动多个 Task 的权限。

---

## 5. Frozen Design Rules

Implementation 阶段禁止：

- 修改冻结的 Architecture Layer 文档或其语义；
- 修改冻结的 Design Layer Domain Model 文档或其语义；
- 修改冻结的 Contract Layer 文档或其 Contract 语义；
- 修改冻结的 Runtime Specification 文档或其执行语义；
- 新增 Core Phase；
- 新增 Workflow Transition；
- 新增 Gate Type；
- 修改 Gate Required Authorization；
- 修改 Context Authority；
- 改变 Managed Project 中 `PROJECT_STATE.md` 作为该项目 Current Project State 唯一 Source of Truth 的地位；
- 把 Advisory 变成 Workflow / Gate / Runtime Controller；
- 把 Judgment-Based Gate 自动转换为 Script 判断；
- 创建新的 Architecture / Design 文档；
- 为方便编码而改变冻结语义。

---

## 6. Runtime Invariants

实现始终必须保持：
以下规则描述的是 Project Incubator V1 Runtime 对 Managed Project 的运行语义，不描述当前 Implementation Repository 自身的开发状态管理方式。

- Managed Project 中的 `PROJECT_STATE.md` 是该 Managed Project 当前实际状态的唯一 Source of Truth；
- Managed Project 的 Runtime State 不得替代该 Managed Project 的 `PROJECT_STATE.md`；
- Runtime 不替 Maker 做 Decision；
- Runtime 不替 Agent 完成创造性工作；
- Context Mutation 必须经过 Context Access Contract；
- Runtime 是满足 Contract 后的 Context Persisted Mutation Executor；
- State Change Requirement 不等于 Context 已经修改；
- `READY_FOR_TRANSITION` 不等于 Transition 已经执行；
- Managed Project 的 Phase Transition 只有在该 Managed Project 的 `PROJECT_STATE.md` Mutation 成功持久化并验证后才完成；
- Script 不直接读取 Core Context；
- Script 不直接修改 Context；
- Script Validation Result 不等于 Gate Evaluation Result；
- Gate Result 不直接修改 Workflow、Context 或 Artifact；
- Advisory 不直接产生 Runtime Command；
- Maker Authorization 只能来自 Maker。

---

## 7. Upstream Design Gap

如果实现某个 Task 必须依赖上游尚未定义、定义不明确或相互冲突的：

- Domain Rule；
- Workflow Rule；
- Gate Rule；
- Context Authority；
- Contract Semantics；
- Runtime Decision Rule；

不得自行补充、选择、解释或修正上游设计。

如果不同上游 Layer 之间存在冲突，按照 Source of Truth 层级判断是否能够得到唯一确定结论；如果同一层级存在冲突，或按照层级仍无法得到唯一确定结论，必须按 `UPSTREAM_DESIGN_GAP` 处理。

必须停止受影响部分并标记：

`UPSTREAM_DESIGN_GAP`

报告：

- Gap 所属 Layer；
- 缺失定义；
- 受影响 Task；
- 被阻塞的实现内容。

Implementation Choice 不属于 Upstream Design Gap。

Implementation Choice 仅指 Implementation Plan 和上游文档尚未明确指定、且不会改变既定文件职责、接口语义、Domain Model、Contract 或 Runtime 行为的实现细节。

例如：

- Class / Function 内部命名；
- JSON 解析实现；
- File I/O 内部实现；
- Test 内部组织方式。

如果 Implementation Plan 已经明确指定文件、目录、技术基线、Generated Files 或实现边界，则这些内容不再属于自由 Implementation Choice，不得自行改变。

---

## 8. File Rules

只创建或修改当前 Task 的 Generated / Modified Files 明确列出的文件。

如果当前 Task 的 Generated / Modified Files 包含嵌套 `AGENTS.md`：

必须将其视为 Product Artifact，而不是新的 Implementation Governance Source of Truth。

生成该文件时必须遵守本文档 `Instruction Scope` 中定义的嵌套 `AGENTS.md` 边界。

如果实现过程中发现必须新增或修改 Task 未列出的文件：

不得直接扩展修改范围。

必须先判断：

- 如果属于 Upstream Design Gap，按 `UPSTREAM_DESIGN_GAP` 处理；
- 如果只是必要的 Implementation Choice，先在 Task 报告中说明文件、原因和影响，并等待用户明确授权后再创建或修改。

禁止：

- 创建额外设计文档；
- 创建新的 Source of Truth；
- 创建无明确职责的 Reference；
- 创建 Implementation Plan 未授权的 Domain Layer；
- 因重构顺便修改无关文件。

已有实现不得因为存在就默认复用。

复用前必须确认其符合当前冻结：

- Design Layer；
- Contract Layer；
- Runtime Specification；
- 当前 Implementation Task。

---

## 9. Validation Rules

不得使用以下表述代替验证：

- 功能正常；
- 应该可以；
- 看起来没问题；
- 基本完成。

必须执行实际可验证检查。

Task Completion 必须满足当前 Task 在 Implementation Plan 中明确定义的全部 Validation Criteria，并以实际文件状态、Test、命令结果或该 Validation Criteria 要求的其他可验证证据证明。


Validation 未通过：

不得声明 Task Completed。

---

## 10. Reporting

每个 Task 完成后使用以下最小格式：

```text
Task:
Status: COMPLETED

Changed Files:

Validation:
- ...

Issues:
- 无
```

如果存在阻塞：

```text
Task:
Status: BLOCKED

Blocking Reason:

Upstream Design Gap:
- 如适用
```

不要重复长篇解释已经冻结的设计。

---

## 11. Implementation Completion

只有 `PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md` 中全部 TASK-001 ～ TASK-027 均已实际实现或对已有实现完成对应 Task Validation，并通过：

- Unit Validation
- Module Validation
- Runtime Integration Validation
- End-to-End Validation
- V1 Completion Criteria

后，才能认为 Project Incubator V1 Implementation 完成。

在此之前不得自行进入新的 Packaging、Release 或其他未定义阶段。