# Project Incubator V1

Project Incubator 是一个 AI 辅助项目孵化 Skill。它帮助 Maker 与 Agent 在长期项目中维持稳定 Context、明确 Workflow State、受控决策和可验证 Artifact。

本 Skill 不替代 Maker，不自行创建项目策略，也不作为项目管理平台。它提供一个 Skill Package 和内嵌 Runtime 支持，用于受控推进项目。

## Package 结构

```text
PROJECT_INCUBATOR/
├── SKILL.md
├── README.md
├── AGENTS.md
├── runtime/
├── references/
├── templates/
└── scripts/
```

- `SKILL.md` 是 Skill 入口。
- `README.md` 说明 Skill Package。
- `AGENTS.md` 定义 Managed Project 使用场景中的 Agent 行为边界。
- `runtime/` 承载确定性执行支持。
- `references/` 承载冻结定义的 Implementation Projection。
- `templates/` 承载 Context Template。
- `scripts/` 承载 Runtime 使用的确定性工具能力。

## Core Context

V1 在 Managed Project 中使用四个 Core Context 文件：

- `PROJECT_PROFILE.md`：项目身份、Intent、目标用户、成功标准和长期约束。
- `PROJECT_STATE.md`：当前实际项目状态，也是当前状态的唯一 Source of Truth。
- `PROJECT_PLAN.md`：当前有效的未来执行计划。
- `PROJECT_DECISIONS.md`：Maker 已确认的重要决策。

这些 Context 文件职责分离。Plan 不替代 State，历史对话不替代 `PROJECT_STATE.md`。

## Core Workflow

冻结的 Core Workflow 为：

```text
P0 Intent Discovery
P1 Project Definition
P2 Solution Design
P3 Execution Planning
P4 Creation
P5 Validation
P6 Iteration
```

Runtime 按冻结的 Workflow Contract 和 Runtime Specification 消费 Workflow。本 README 不重新定义 Workflow Rule。

## Runtime 使用

Runtime 协调 Workflow、Context、Gate、Script、Advisory 和 Runtime Result 职责之间的受控执行。

Runtime 负责确定性执行和边界 enforcement。它不替代 Maker 决策、Agent 推理或创造性项目工作。

以下事项应使用 Runtime-controlled path：

- Context Read 与 Mutation；
- Phase Transition Eligibility 检查；
- Gate Invocation 与 Authorization Handling；
- 确定性 Script Invocation；
- Transition Commit 与持久化状态验证；
- Runtime Result 报告。

## 基本使用

1. 使用 `SKILL.md` 判断 Project Incubator 是否适用。
2. 在声明项目状态前，读取 Managed Project 的 Core Context。
3. 将 `PROJECT_STATE.md` 作为当前状态 Authority。
4. 区分 Maker Decision 与 Agent Recommendation。
5. 通过 Runtime 路由受控状态变化。
6. 将 Advisory 仅作为指导，不作为执行 Authority。
