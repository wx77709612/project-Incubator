# Project Incubator 兼容资产

现行实现为 `project-incubator-plugin/` 的 Plugin Router 与 0.3.x MCP Kernel。安装应从经验证的 Plugin 源码候选通过正式插件管理器完成；不要把本目录当作现行 Plugin 安装包。

本目录 `SKILL.md` 仅把旧名称转交 `project-incubator-router`。`AGENTS.md` 与集成模板提供当前协作边界；不自动写入任何已有 Managed Project。

`runtime/`、`scripts/`、`references/` 的旧投影和 `templates/context/` 属于 Legacy 兼容资产，仅供显式 RC 回归。`references/legacy/` 保存被最小路由替代前的执行指导与集成模板，供兼容构建读取，不是另一个活动 Skill。Plugin 不加载这些文件。

现行项目以 `.project-incubator/activation.json`、`state.json`、`latest-receipt.json` 为权威集合；恢复统一使用 `inspect_project`。旧 Markdown 模板不作为 Plugin 的状态先决条件。
