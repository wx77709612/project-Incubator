# Project Incubator

当 Maker 需要长期 AI 协作，将一个初始想法推进为具有稳定上下文、明确 Workflow 位置、可执行计划、可验证 Artifact 和受控迭代的项目时，使用 Project Incubator。

本 Skill 适用于项目孵化工作。Agent 必须跨会话保持项目上下文，尊重 Maker 决策，并避免在未授权时改变项目方向。

## 何时使用

当 Maker 提出以下需求时，使用本 Skill：

- 从一个想法开始孵化新项目；
- 澄清项目 Intent、目标用户、成功标准或约束；
- 建立或恢复项目 Context 文件；
- 判断当前项目 Phase 的含义；
- 基于当前 Context 准备下一步项目行动；
- 按冻结的 Project Incubator V1 Core Workflow 推进；
- 评估项目 Artifact 是否具备进入下一步的条件；
- 根据 Validation Feedback 处理 Iteration；
- 识别风险、缺失信息或需要 Maker 决策的问题。

不要将本 Skill 用作通用项目管理平台、自动决策者，或 Maker 项目方向判断的替代品。

## Core Workflow

Project Incubator V1 使用以下冻结的 Core Workflow：

```text
P0 Intent Discovery
P1 Project Definition
P2 Solution Design
P3 Execution Planning
P4 Creation
P5 Validation
P6 Iteration
```

Iteration 只能返回冻结 Workflow Contract 已允许的目标。

## Core Context

V1 Core Context 文件包括：

- `PROJECT_PROFILE.md`
- `PROJECT_STATE.md`
- `PROJECT_PLAN.md`
- `PROJECT_DECISIONS.md`

`PROJECT_STATE.md` 是当前项目状态的唯一 Source of Truth。Agent 不得使用历史聊天、临时记忆、计划、Artifact 或 Runtime temporary state 覆盖它。

## Runtime 入口

对于确定性的项目状态变化、Context Mutation、Gate 处理、Script Invocation、Transition Commit 和持久化状态验证，Agent 必须通过 Project Incubator Runtime 路由执行，而不是直接修改受控状态。

Runtime 支持由 `runtime/` 下的包提供。Runtime 实现细节由冻结的 Runtime Specification 和 Implementation Plan 定义。

## Agent 使用边界

Agent 可以分析 Context、提出方案、准备 Artifact、暴露风险，并向 Maker 请求决策。

Agent 不得：

- 替代 Maker Authorization；
- 在没有 Maker 确认时扩大 Project Goal 或 Scope；
- 绕过 Runtime 执行受控状态变化；
- 将 Advisory Output 视为 Runtime Command；
- 将 Script Validation 视为 Gate Result；
- 创建新的 Workflow Phase、Transition、Gate Type、Context Authority 或 Runtime Rule。
