# Project Incubator 项目协作入口

项目孵化、恢复、状态查询和推进统一使用已安装 Plugin 的 `project-incubator-router` Skill。缺少 Plugin/MCP 时报告并停止，不创建替代 Runtime。

恢复和状态查询先调用 `inspect_project`；只根据已验证的路由交给对应 Child Skill 与 Host Profile，不从聊天或派生文档补全状态。

权威文件是 `.project-incubator/activation.json`、`.project-incubator/state.json` 与 `.project-incubator/latest-receipt.json`。State 是唯一业务状态，Activation 约束身份与路由，Receipt 证明最近变更闭合。不得直接编辑这些文件。

所有受控变更通过 Kernel MCP；Maker 保留产品与架构决定权。没有有效授权、持久化、revision、回读和当前 Receipt 验证，不得宣称变更完成。`READY_FOR_TRANSITION` 不等于已经转换；Gate Result 和 Advisory 不直接修改状态。

Markdown 可以作为普通 Artifact 或按需导出，不能作为现行状态权威。不得要求四份 Core Context、旧 Python Runtime、旧 Host Bootstrap 或逐文件 Mutation 流程。

本入口模板仅供明确要求生成的新协作文件使用；不得覆盖或自动追加已有项目 AGENTS.md。人类可读文本默认简体中文。
