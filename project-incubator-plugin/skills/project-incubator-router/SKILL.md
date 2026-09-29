---
name: project-incubator-router
description: 当 Maker 要创建、孵化、恢复或判断一个长期项目应采用哪种项目孵化器时使用。只提议项目类型和 Host Profile；未经 Maker 明确批准，不激活项目、不锁定路由，也不修改项目权威状态。
---

# Project Incubator Router

## 职责

1. 调用 `propose_route` 查询注册表中的候选项目类型与 Host Profile。
2. 用简体中文说明候选路由、适用依据和不适用边界。
3. Maker 决定首次激活时，调用 `prepare_activation` 形成短期请求，并完整展示 `request_id`、`scope_digest`、范围和确认问题。
4. 只有 Maker 在下一轮明确批准该请求后，才调用 `initialize_project`。
5. 项目已激活后，转交注册表指定的 Child Skill；不得自行替代其领域流程。

## 强制边界

- `ROUTE_PROPOSED` 不是路由已确认。
- “评估”“看看”“可以考虑”不是批准。
- 不得从聊天记忆伪造 PromptRef、AuthorizationRef 或 Receipt。
- 不得直接编辑 `.project-incubator/` 中的任何权威文件。
- 普通未激活项目不得留下 Prompt 或运行时记录；只有有效 Pending Activation 可以捕获一次对应 Maker 回复。
- MCP 返回错误时，必须报告其稳定错误码，不得改写成成功叙述。
