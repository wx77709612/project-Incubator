<!-- project-incubator:codex-integration -->

# AGENTS.md

## Project Incubator Entry

当前项目由 Project Incubator 管理。本文件是 Codex 项目级协作入口，只用于帮助后续 Codex Task 找到项目 Context、Skill 路由和职责边界。

## Core Context

涉及项目目标、当前状态、未来计划、重要决策或项目推进时，先读取项目根目录下的 Core Context：

- `PROJECT_PROFILE.md`
- `PROJECT_STATE.md`
- `PROJECT_PLAN.md`
- `PROJECT_DECISIONS.md`

## State Source of Truth

`PROJECT_STATE.md` 是当前项目状态的唯一 Source of Truth。

不得使用历史聊天、Agent Memory、未执行 Plan 或临时推测覆盖当前 State。

## Skill Trigger

涉及以下行为时，应使用 `project-incubator` Skill：

- 判断当前 Phase；
- 判断下一步项目行动；
- Workflow Transition；
- Gate；
- Validation；
- Iteration；
- 受控 Context Mutation；
- 项目状态推进。

## Runtime Boundary

不得绕过 Project Incubator Runtime 直接执行受控状态变化、自行推进 Workflow 或自行修改受保护 Context。

## Maker Boundary

Maker 保留 Project Goal、Project Scope、Project Direction、重要 Decision，以及需要 Maker Authorization 的变更的最终决策权。
