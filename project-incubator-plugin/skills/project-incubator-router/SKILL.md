---
name: project-incubator-router
description: 当 Maker 要新建项目或产品、按 Phase 0 等阶段直接初始化、孵化、恢复，或判断应采用哪种项目孵化器时使用。新建项目默认先调用本 Router，即使 Maker 未点名 Project Incubator；只有 Maker 明确表示不用时才跳过。未经 Maker 对具体请求明确批准，不激活项目、不锁定路由，也不修改项目权威状态。
---

# Project Incubator Router

## 当前 Kernel 权威与恢复

Plugin Router `project-incubator-router` 是唯一现行入口。权威集合为 `.project-incubator/activation.json`、`.project-incubator/state.json` 和 `.project-incubator/latest-receipt.json`；State 是唯一业务状态，Activation 约束身份/路由，Receipt 证明闭合。临时 Runtime Data 和 Markdown Artifact 不替代它们。

恢复与状态查询先调用 `inspect_project`，验证失败时报告稳定错误并停止受影响推进，不从聊天补全。只使用已验证路由的 Child Skill/Host Profile；不得直接编辑权威文件。所有受控变更经现行 Kernel，提交后确认 revision、回读与 Receipt 一致再报告完成。缺少 Plugin/MCP 时停止，不调用旧执行资产。


## 职责

新建项目的交接说明即使要求“立即执行 Phase 0–3”，也先调用 Router 完成路由提案。Project Incubator 是默认入口；只有 Maker 明确表示不用时，才按普通非托管项目处理。首次工程写入必须排在路由确认、具体激活请求的下一轮明确批准、Kernel 初始化及 Receipt 验证之后。Maker 未点名插件不能视为拒绝托管。

1. 调用 `propose_route` 查询注册表中的候选项目类型与 Host Profile。
2. 用简体中文说明候选路由、适用依据和不适用边界。
3. Maker 决定首次激活时，调用 `prepare_activation` 形成短期请求，并完整展示 `request_id`、`scope_digest`、范围、将写入 Active Decision View 的 Product Decision 和确认问题；提供标准回复句“我明确批准激活请求 request_id=<实际 request_id>，scope_digest=<实际 scope_digest>”，但不得代 Maker 发送。
4. 只有 Maker 在下一轮明确批准该请求后，才调用 `initialize_project`。
5. 项目已激活后，转交注册表指定的 Child Skill；不得自行替代其领域流程。

## 当前任务首次进入项目

当前 Codex 任务第一次进入一个已激活项目并使用 Project Incubator 时，调用一次 `prepare_agent_entry` 检查根目录 `AGENTS.md`。同一任务对同一 `project_root` 的后续轮次和 Plugin 调用复用该结果，不重复检查；切换项目根目录后才对新项目检查一次。这项任务级记忆不写入项目状态。

此处 `session_id` 必须直接使用真实宿主公开的 `CODEX_SESSION_ID`，不得从工作区名称、路径、聊天内容或其他 UUID 猜测。Maker 批准后调用 `install_agent_entry` 时不传 `turn_id`；真实回合、规范项目根与最新消息由 Hook 记录，Kernel 按同一规范项目根、项目 ID、Session、`request_id` 与 `scope_digest` 定位并校验最新批准。不同根目录不共享批准；指针不完整、出现重叠记录歧义或批准已被后续消息替代时失败关闭，不回退旧记录。若报告 `PROMPT_ORDER_AMBIGUOUS`，必须请 Maker 在并发记录结束后连续发送两条独立消息：第一条用于确认并清除冲突状态且仍会失败，第二条再精确批准或拒绝；不得把第一条当作有效授权。

- 返回 `CURRENT` 时继续；返回 `EXISTING_REVIEW_REQUIRED` 时保留原文件，向 Maker 展示与包内模板的 SHA-256 差异，由 Maker 决定改动方向。
- 返回 `MISSING` 时展示 `request_id`、`scope_digest` 与补建范围。只有 Maker 下一轮明确批准后才调用 `install_agent_entry`，不得直接创建或覆盖。
- `install_agent_entry` 返回 `CREATED` 后，当前任务必须显式读取新建的 `AGENTS.md` 一次；下一个新任务由 Codex 正常加载。
- 目录、链接、不可读对象或模板错误均报告稳定错误并停止入口处理。

首次激活的 `initialize_project` 已在同一激活授权范围内处理 Agent Entry：缺失时创建，内容相同则复用，内容不同则保留并报告 `EXISTING_REVIEW_REQUIRED`，不再另行申请补建授权。

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

## 权威集合恢复

`inspect_project` 或实际状态操作因三个权威 JSON 缺失、残缺、Schema 错误、项目 ID 不一致或 Receipt 无法验证而失败时，先原样报告错误，不依据聊天自动生成或补全状态。只有现有 Artifact、Evidence、可用旧资料和 Maker 已表达事实足以形成完整候选时，才可提出恢复。

1. 调用 `prepare_authority_recovery`，逐文件展示三个固定路径各自的 `MISSING`、`VALID` 或 `INVALID` 状态、可用错误码，以及恢复候选的 revision 基线。
2. 完整展示 `request_id`、`scope_digest`、恢复摘要和候选范围，并请 Maker 在下一轮明确批准；不得代 Maker 批准。
3. Maker 明确批准同一请求编号和摘要后，调用 `recover_project_authority`。准备后任何权威文件新增、删除或字节变化都必须返回 `RECOVERY_SOURCE_CHANGED`，不得覆盖。
4. 只有 Kernel 写入三份权威 JSON、逐项回读并验证新 Receipt 后才报告恢复完成。`CONTINUED` 表示从可解析旧 State 的下一 revision 延续；`REESTABLISHED` 表示以 revision 0 建立新的恢复基线，不代表历史从未存在。

恢复准备与提交同样必须使用真实 `CODEX_SESSION_ID`；调用 `recover_project_authority` 时不传 `turn_id`，由 Kernel 使用 Hook 已记录的真实回合完成授权绑定，不要求 Agent 推断宿主未公开的标识。

证据不足时只报告缺口并等待 Maker，不得调用准备或提交恢复。恢复不新增阶段、Gate 或 Workflow；旧 Pending Request 不继承，后续需要时按现行流程重新提出。

## 强制边界

- `ROUTE_PROPOSED` 不是路由已确认。
- “评估”“看看”“可以考虑”不是批准。
- 不得从聊天记忆伪造 PromptRef、AuthorizationRef 或 Receipt。
- 不得直接编辑 `.project-incubator/` 中的任何权威文件。
- 普通未激活项目不得留下 Prompt 或运行时记录；只有有效 Pending Activation 或 Maker 已看到的 Pending Authority Recovery 可以捕获一次对应回复。
- 调用 `prepare_activation` 前必须以 Runtime 结果确认项目没有任何权威文件；完整的已初始化项目返回 `PROJECT_ALREADY_INITIALIZED`，只存在部分权威文件时返回 `PROJECT_CONTROL_STATE_INCOMPLETE`。两种情况都不得改写项目或继续生成 Request。
- `prepare_activation.state` 必须描述激活完成后的 revision 0 状态：当前行动和完成条件不得继续要求授权或初始化，`last_change.operation` 必须为 `INITIALIZE_PROJECT`，且不得包含 `ACTIVATION_DRAFT`、等待激活或尚未激活叙述。
- 新激活必须使用 State 1.1，并包含不可变的 `workflow.entry`。Entry Stage 与 State Stage、`allowed_next` 和 `return_stage` 必须符合已选 Child Workflow。
- 激活前已确认且由本次激活范围覆盖的 Product Decision 必须通过 `product_decisions` 传入；不得伪造 `authorization_ref`。Runtime 在 Maker 批准该 `request_id` 与 `scope_digest` 后绑定真实 Authorization 并写入 `decisions.active`。
- MCP 返回错误时，必须报告其稳定错误码，不得改写成成功叙述。
