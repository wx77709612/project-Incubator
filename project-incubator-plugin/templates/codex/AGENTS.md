# AGENTS.md

## Project Incubator 协作规则

项目孵化、接入、恢复、状态查询和推进统一使用已安装插件的 `project-incubator-router`。缺少插件或 MCP 时应报告并停止，不得临时建立另一套 Runtime。

同一 Codex 任务第一次进入当前项目并使用 Project Incubator 时，使用 Router 提供的 Agent Entry 操作检查一次本文件；后续调用复用本任务已取得的结果。已有 `AGENTS.md` 不得自动覆盖、追加或合并。

需要项目状态或恢复上下文时调用 `inspect_project`。只有验证通过后，才按已确认路由使用对应 Child Skill 与 Host Profile；不得从聊天、计划或普通 Markdown 推测当前状态。

Managed Project 的权威集合只有 `.project-incubator/activation.json`、`.project-incubator/state.json` 和 `.project-incubator/latest-receipt.json`。State 保存业务状态，Activation 约束项目身份与路由，Receipt 证明最近一次受控变更已经闭合。本文件是协作入口，不是第四份权威状态。

所有权威变更必须经过 Kernel MCP。Maker 保留产品与架构决定权；Agent 负责分析、提案和实现；Kernel 负责校验、受控写入、revision、回读和 Receipt。未经 Maker 对具体请求明确授权，不得执行受控变更；没有通过回读与 Receipt 验证，不得宣称变更完成。

`READY_FOR_TRANSITION` 只表示具备提出转换的条件，不表示阶段已经转换。Gate Result、Validation Result 和 Advisory 都不能自行修改项目阶段、Workflow 或权威状态。

面向人类的新建或实质性改写文本默认使用简体中文。必要的英文技术术语、协议字段、代码标识符、枚举值和文件名可以保留。
