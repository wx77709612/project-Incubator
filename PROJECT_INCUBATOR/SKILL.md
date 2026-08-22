---
name: project-incubator
description: >
  用于长期 AI 协作中的项目孵化与受控推进。Use when：Maker 希望把一个初始 Idea
  逐步转化为明确的问题定义、可执行计划、可验证成果和可持续迭代的项目状态；
  或需要恢复已有项目上下文、判断当前项目所处阶段与下一步行动、验证阶段成果、
  处理项目迭代，并在 Maker 保留最终决策权的前提下控制项目目标、范围和状态推进。
  本 Skill 通过持久项目 Context、State-driven Workflow、Gate 与 Runtime 边界降低
  AI 发散和未经授权的项目变化。不用于一次性问答、单纯代码生成、通用任务管理，
  也不替代 Maker 作出项目方向、范围或战略决策。
---

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

`PROJECT_PLAN.md` 是 Core Context，用于记录项目生命周期规划，包括 Phase Goal、Gate、Next Action、Expected Artifact 和 High-level Dependency。

`PROJECT_PLAN.md` 不用于记录 Implementation Task Breakdown Artifact。

## Artifact 与 Context 边界

Project Incubator 区分：

- Phase Artifact
- Core Context
- Context Mutation

Phase Artifact 表示某个阶段产生的成果。

Core Context 表示项目持续维护的信息。

Context Mutation 表示 Workflow 执行过程中对 Core Context 的更新。

Artifact 与 Context Mutation 是两个独立概念。

Agent 不得因为某个 Core Context 文件被更新，就将其视为对应 Phase 的 Artifact。

## Runtime 入口

对于确定性的项目状态变化、Context Mutation、Gate 处理、Script Invocation、Transition Commit 和持久化状态验证，Agent 必须通过 Project Incubator Runtime 路由执行，而不是直接修改受控状态。

Runtime 支持由 `runtime/` 下的包提供。Runtime 实现细节由冻结的 Runtime Specification 和 Implementation Plan 定义。

## Host Environment Bootstrap

当 Project Incubator 初始化新的 Managed Project、第一次在已有 Managed Project 中建立协作上下文，或 Maker 明确请求宿主环境集成时，Agent 应先解析 Host Environment。

- Host = `CODEX`：通过 Runtime / Script Coordinator / `DETERMINISTIC_OPERATION` 调用 `BOOTSTRAP_HOST_INTEGRATION`，为尚未存在项目级 `AGENTS.md` 的 Managed Project 创建 Codex 协作入口。
- Host = `OTHER`：不创建 Codex `AGENTS.md`。
- Host = `UNKNOWN`：不猜测 Host，不创建 Codex `AGENTS.md`，并说明 Host Environment 无法确认。

Host Environment Bootstrap 只处理宿主环境集成 Artifact，不改变 Current Phase，不触发 Workflow Transition，不修改 `PROJECT_STATE.md` 或其他 Core Context。已有且未包含 Project Incubator Integration Marker 的 `AGENTS.md` 不得被自动覆盖、删除、重写或强行追加。

## Agent 使用边界

Agent 可以分析 Context、提出方案、准备 Artifact、暴露风险，并向 Maker 请求决策。

Agent 不得：

- 替代 Maker Authorization；
- 在没有 Maker 确认时扩大 Project Goal 或 Scope；
- 绕过 Runtime 执行受控状态变化；
- 将 Advisory Output 视为 Runtime Command；
- 将 Script Validation 视为 Gate Result；
- 创建新的 Workflow Phase、Transition、Gate Type、Context Authority 或 Runtime Rule。
