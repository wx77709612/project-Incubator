# Codex 项目级协作入口设计

状态：DRAFT / MAKER REVIEW REQUIRED；上游：[ACP](../ARCHITECTURE/CODEX_PROJECT_AGENT_ENTRY_CHANGE_PROPOSAL.md)、[Decision 016](../ARCHITECTURE/ARCHITECTURE_DECISIONS.md#decision-016codex-managed-project-初始化协作入口)。

## 目标与职责

Codex Plugin 初始化新的 Managed Project 时，为尚无项目级 `AGENTS.md` 的项目创建稳定的原生协作入口。Codex 后续任务通过该入口找到 Plugin Router、恢复方法和协作边界。它不是状态副本：任何项目当前阶段、计划、Decision、Gate 或 Receipt 均须通过现行 Kernel 查询。

本能力分为三个单一职责单元：

1. **包内模板**：插件分发自包含的简体中文文本，只包含稳定入口规则；研发仓库旧 `PROJECT_INCUBATOR/` 模板不作为运行依赖。
2. **Agent Entry 文件操作**：只处理项目根目录 `AGENTS.md` 的类型检查、排他创建、回读及可证明安全的撤销；不读写三个权威 JSON。
3. **初始化协调**：在授权通过后、Pending Activation 消费前，把 Agent Entry 操作与原有 JSON 初始化放入同一项目串行化闭合过程；向调用者分别返回权威 Receipt 和入口结果。

Project Type 与 Host Profile 不参与入口选择：Codex 分发的 `mod`、`desktop-product`、`web-product` 新激活都遵守同一规则。`host_profile_id = null` 不是非 Codex 环境信号。普通 MCP 再分发不在本设计承诺范围内。

## 模板内容边界

模板需有 Project Incubator 集成标记、Router 唯一入口、`inspect_project` 恢复、三个 JSON 权威文件及职责、受控变更通过 Kernel、Maker 决策权、缺少 Plugin/MCP 时停止，以及人类可读文本默认简体中文。标记用于人工识别，不作为已有文件可自动覆盖的许可。

不得包含旧全局 Skill 执行指令、旧 Python Runtime、四份 Markdown Core Context、包外 `SPECS/` 路径、动态阶段或当前项目事实。不同项目复制同一稳定模板；不注入项目名、类型、状态或授权引用。

## 初始化结果与用户可见语义

| 初始条件 | 行为 | Agent Entry 结果 | 权威初始化 |
| --- | --- | --- | --- |
| 根目录无 `AGENTS.md` | 排他创建模板并回读验证 | `CREATED` | 仅在入口和 JSON/Receipt 均闭合后成功 |
| 已有可读普通文件 | 不修改、不推断兼容 | `EXISTING_REVIEW_REQUIRED` | 可以成功；Router 必须提醒 Maker 人工核对 |
| 目录、链接、不可读文件 | 不跟随、不覆盖 | 无成功结果；`AGENT_ENTRY_PATH_UNSAFE` | 失败关闭 |
| 排他创建时出现竞争者文件 | 不覆盖、不删除竞争者文件 | 无成功结果；`AGENT_ENTRY_CONFLICT` | 失败关闭 |
| 新建入口或回读失败 | 撤销本次可识别的写入 | 无成功结果；`AGENT_ENTRY_WRITE_FAILED` 或 `AGENT_ENTRY_READBACK_MISMATCH` | 失败关闭 |

失败时 Pending Activation 不消费。若本次已创建入口且后续 JSON 初始化失败，只在文件仍是本次创建的同一对象、内容仍等于模板时撤销；否则保留并报告 `AGENT_ENTRY_ROLLBACK_INCOMPLETE` 及残留路径。三个 JSON 的恢复仍按 Kernel 原有闭合原则执行。部分恢复失败须保留可检查残留，不得报告完整成功，也不得用聊天推定项目状态。

## 边界与后续任务

`initialize_project` 的返回保留现有 `activation`、`receipt` 字段，并增加独立 `agent_entry` 结果；后者不进入 State Schema、Receipt Hash 或 revision。已有项目的 `inspect_project` 仍只验证权威集合，不因为过去缺少 `AGENTS.md` 而判状态无效。

本设计不自动补写已激活项目，不处理已有文件自动合并，不保证创建文件会在当前已启动的 Codex 任务中重新加载。存量项目补齐需另行请求和审批。
