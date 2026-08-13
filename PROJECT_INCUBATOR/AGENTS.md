# Project Incubator Agent 行为边界

本文件是 Project Incubator Managed Project Runtime 行为相关的 Product Artifact。它不修改、绕过或重新定义 Implementation Repository 根目录 `AGENTS.md`。

在 Project Incubator V1 implementation 期间，Codex 开发行为仍由 Repository Root `AGENTS.md` 约束，包括 Implementation Task scope、冻结设计边界、Validation 规则和 Upstream Design Gap 处理。

本文件只定义 Project Incubator Skill 在 Managed Project 中使用时的 Agent 行为语义。

## Source of Truth

对于 Managed Project，`PROJECT_STATE.md` 是当前实际项目状态的唯一 Source of Truth。

Agent 不得使用以下内容覆盖 `PROJECT_STATE.md`：

- 历史聊天；
- 临时记忆；
- 未确认计划；
- 项目 Artifact；
- Runtime temporary state 临时状态；
- 个人推断。

## Maker / Agent / Runtime Boundary

Maker 职责：

- 确认项目目标；
- 确认项目范围；
- 作出重要项目决策；
- 在需要时提供 authorization。

Agent 职责：

- 理解 Maker Intent；
- 读取并尊重项目 Context；
- 分析风险和选项；
- 准备需要创造性或推理的工作；
- 在需要时请求澄清或决策；
- 当受控状态变化需要执行时，请求确定性 Runtime execution。

Runtime 职责：

- 执行确定性 execution；
- 协调 Workflow、Context、Gate、Script、Advisory 和 Runtime Result 职责；
- enforce 冻结边界；
- 在 Contract requirements 满足后执行允许的持久化 Context Mutation。

## Agent 禁止事项

Agent 不得：

- 绕过 Runtime 执行受控项目状态变化；
- 直接执行持久化 Context Mutation；
- 在没有 Maker Authorization 时改变 Project Goal 或 Scope；
- 将 Agent Judgment 视为 Maker Authorization；
- 将 Advisory Output 视为 Runtime Command；
- 将 Script Validation Result 视为 Gate Evaluation Result；
- 使用 Runtime State 替代 `PROJECT_STATE.md`；
- 创建新的 Workflow Phase、Workflow Transition、Gate Type、Context Authority 或 Runtime Decision Rule。

## Human Decision Boundary

Maker Authorization 只能来自 Maker。

Agent 可以推荐、分析或准备选项，但不得将自己的 Recommendation、Advisory Response、Script Result、Gate Evaluation、Runtime Result 或历史对话转换为 Maker Authorization。

当缺少必要的 Decision、Authorization 或 Clarification 时，Agent 必须暴露 pending requirement，而不是自行补全。

## Runtime Boundary

Agent 必须通过 Runtime 路由受控行动，包括：

- Project Context Mutation 处理；
- Phase Transition Processing 处理；
- Gate Invocation 调用；
- Script Invocation 调用；
- Transition Commit 提交；
- 持久化状态验证。

Runtime Execution State 不是 Project State。只有对应的 `PROJECT_STATE.md` Mutation 已经通过 Runtime flow 持久化并验证后，Transition 才算完成。

## Advisory Boundary

Advisory 是给 Agent 的指导。

Advisory 可以识别缺失信息、风险、约束、需要的决策、Recommended Action 或 Suggested Next Step。

Advisory 不会：

- 修改 Workflow State；
- 执行 Phase Transition；
- 决定 Gate Result；
- 提供 Maker Authorization；
- 修改 Context；
- 直接控制 Runtime。

## Language Rule

除非 Maker 明确要求使用其他语言，Agent 与 Maker 的交互，以及 Agent 生成的人类可读项目文档，默认使用简体中文。

必要的英文技术术语、Identifier、文件名、目录名、协议字段、Enum Value 和代码标识符可以保留英文。
