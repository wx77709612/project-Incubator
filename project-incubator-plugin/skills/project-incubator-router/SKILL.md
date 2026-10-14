---
name: project-incubator-router
description: 当 Maker 要创建、孵化、恢复或判断一个长期项目应采用哪种项目孵化器时使用。只提议项目类型和 Host Profile；未经 Maker 明确批准，不激活项目、不锁定路由，也不修改项目权威状态。
---

# Project Incubator Router

## 职责

1. 调用 `propose_route` 查询注册表中的候选项目类型与 Host Profile。
2. 用简体中文说明候选路由、适用依据和不适用边界。
3. Maker 决定首次激活时，调用 `prepare_activation` 形成短期请求，并完整展示 `request_id`、`scope_digest`、范围、将写入 Active Decision View 的 Product Decision 和确认问题；提供标准回复句“我明确批准激活请求 request_id=<实际 request_id>，scope_digest=<实际 scope_digest>”，但不得代 Maker 发送。
4. 只有 Maker 在下一轮明确批准该请求后，才调用 `initialize_project`。
5. 项目已激活后，转交注册表指定的 Child Skill；不得自行替代其领域流程。

## Entry 与 Host 确认

路由提议必须同时说明 `project_type_id`、`host_profile_requirement`、候选 `host_profile_id` 与 Workflow Entry Mode，不得用 Registry 中第一个 Host 或 `windows-desktop` 作为默认值。

- `NEW_PROJECT`：使用 Child Workflow 的标准初始阶段；`desktop-product` 和 `web-product` 为 P0，`mod` 为 M0。
- `ADOPT_EXISTING`：Maker 提供项目来源和背景；Agent 检查现有设计、计划、Artifact、实现与 Evidence，判断正常阶段，写入 `assessment_summary` 和至少一个 `evidence_refs`。Kernel 不替 Agent 判断阶段。
- `REQUIRED`：Maker 未明确确认匹配 Host 时停止，Runtime 返回 `HOST_PROFILE_REQUIRED`。
- `OPTIONAL`：允许 Host 为空；非空时仍必须匹配 Project Type。
- `FORBIDDEN`：不得绑定 Host。

当前 `desktop-product` 需要显式选择 `windows-desktop` 才能激活；这表示当前只有一个受支持候选，不表示它是默认值。目标 Host 不受支持时报告并停止，不得回退到 Windows。

浏览器扩展在本版本中不支持，不能路由为 `desktop-product`，也不能作为 Desktop Child Skill 自动接管的 Delivery Surface。若 Maker 同时描述桌面端和浏览器扩展，只路由本轮明确要孵化且已支持的产品形态，并把另一部分标为未路由范围；不得代替未来 Project Type 或跨项目关系设计。

## Web Product 路由边界

只有通用浏览器为主要用户界面、同时具有前端与后端逻辑职责，且至少一条核心旅程穿过浏览器与后端或数据边界时，才可提议 `web-product`。目标完成条件包含可重复 Build、localhost 运行和真实浏览器核心结果；前后端职责不要求分离进程或仓库。

`NEW_PROJECT` 标准阶段为 P0；`ADOPT_EXISTING` 由 Agent 根据既有 Artifact 和 Evidence 评估 P0–P6 正常阶段，提供 `assessment_summary` 和至少一个 `evidence_refs`。

`web-product` 的 Host Requirement 为 `FORBIDDEN`，`host_profile_id = null`；不得为浏览器、localhost 或操作系统创建或选择 Host Profile。浏览器版本、URL、端口和命令属于项目配置与 Evidence 条件。

浏览器扩展、无后端职责的静态前端、纯后端、独立 MCP Service、CLI、SDK、库、移动、桌面和 Mod 均不属于 Web Child；按其他已注册类型提议或明确报告不支持，不因存在 HTTP 或辅助网页而误分类。

绑定 Web 后端既有 Capability 的 MCP 等次级界面，在同一 Product Boundary、主要结果、业务/数据/授权政策和版本生命周期下不改变 Project Type。出现独立产品目标或主要独立交付物时只触发 Maker Review，不自动迁移；Transport、进程或包的变化不能代替产品归属判断。

不得把 `web-product` 作为默认类型。路由提议不是激活；继续遵守完整请求、下一轮 Maker 明确批准和 Kernel 初始化协议。

## 项目状态查询

Maker 询问“项目状态”“当前进度”“下一步做什么”“有什么阻塞”“需要我决定什么”或语义等价问题时，必须调用 `inspect_project`，并按其返回的固定摘要回答。

- `inspect_project` 是只读查询，不得顺便推进阶段或修改状态。
- 权威状态或 Receipt 不可验证时必须报告错误，不得依据聊天记忆猜测或补全。
- 不默认生成 `PROJECT_OVERVIEW.md`。只有 Maker 当轮明确要求导出项目状态概览时，才调用 `export_project_overview`。
- 展示顺序遵循 [状态摘要契约](references/status-summary.md)。

## 强制边界

- `ROUTE_PROPOSED` 不是路由已确认。
- “评估”“看看”“可以考虑”不是批准。
- 不得从聊天记忆伪造 PromptRef、AuthorizationRef 或 Receipt。
- 不得直接编辑 `.project-incubator/` 中的任何权威文件。
- 普通未激活项目不得留下 Prompt 或运行时记录；只有有效 Pending Activation 可以捕获一次对应 Maker 回复。
- 调用 `prepare_activation` 前必须以 Runtime 结果确认项目没有任何权威文件；完整的已初始化项目返回 `PROJECT_ALREADY_INITIALIZED`，只存在部分权威文件时返回 `PROJECT_CONTROL_STATE_INCOMPLETE`。两种情况都不得改写项目或继续生成 Request。
- `prepare_activation.state` 必须描述激活完成后的 revision 0 状态：当前行动和完成条件不得继续要求授权或初始化，`last_change.operation` 必须为 `INITIALIZE_PROJECT`，且不得包含 `ACTIVATION_DRAFT`、等待激活或尚未激活叙述。
- 新激活必须使用 State 1.1，并包含不可变的 `workflow.entry`。Entry Stage 与 State Stage、`allowed_next` 和 `return_stage` 必须符合已选 Child Workflow。
- 激活前已确认且由本次激活范围覆盖的 Product Decision 必须通过 `product_decisions` 传入；不得伪造 `authorization_ref`。Runtime 在 Maker 批准该 `request_id` 与 `scope_digest` 后绑定真实 Authorization 并写入 `decisions.active`。
- MCP 返回错误时，必须报告其稳定错误码，不得改写成成功叙述。
