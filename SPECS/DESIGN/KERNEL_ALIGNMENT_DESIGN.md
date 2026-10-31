# 唯一入口与恢复设计

状态：APPROVED；上游：[ACP](../ARCHITECTURE/KERNEL_ALIGNMENT_CHANGE_PROPOSAL.md)、[影响分析](../ARCHITECTURE/KERNEL_ALIGNMENT_IMPACT_ANALYSIS.md)。

## 职责

Router 是唯一现行入口，Child 与 Host 只能在激活路由验证后接管。保留一个同名旧 Skill 时，其内容只描述转交 Plugin Router、插件不可用则停止，不包含阶段模型、状态写入、模板创建、安装回退或工具流程复制。

新项目通过现行 Router 激活；已有已激活项目先 inspect_project，按已验证路由恢复。Desktop 必须匹配 windows-desktop；Web Host 为 null/FORBIDDEN；Mod 与 Sims 4 的领域阶段和 Evidence 保留。Host Profile 不自行决定 Project Type 或 Stage。

## 状态与派生文档

activation.json 表达身份与路由；state.json 是唯一项目业务状态；latest-receipt.json 证明提交闭合。所有 Child 恢复与状态查询统一使用 inspect_project。get_project_state 可保留为低层兼容 API，但不能独立作为 Agent 恢复或成功报告依据。

Markdown 可作为普通 Artifact、历史迁移输入或按需导出；不能作为 Core 状态权威或默认恢复先决条件。PROJECT_OVERVIEW.md 继续仅为按需投影。不得自动迁移旧 Markdown 或修改已有 Managed Project 状态。

## 分发与兼容

Plugin 包内 Skill 必须自包含，研发 SPECS 路径只是来源溯源，不得要求安装环境读取包外规格。旧 AGENTS 分发模板只提供 Router、inspect_project 与禁止直写边界。Legacy context 模板和 Python 资产有明确非现行标签，不进入 Plugin 候选包。

安装从已记录权威源码构建唯一候选；正式插件管理器消费候选或已更新 marketplace source。旧全局 Skill 通过可审计、可恢复的安装步骤退出活动路径或被最小兼容路由替换；不能直接删除用户自定义内容。

## Stop Hook 续轮闭合

Codex 宿主可能在用户轮次被中断后，以新的 `turn_id` 自动恢复同一 `session_id`，而不再次触发 `UserPromptSubmit`。Stop Hook 不能把“每个 Stop 前必有同 `turn_id` marker”作为宿主不变量，也不能因此补造 marker 或把 Hook 生成消息当作 Maker Prompt。

精确 turn marker 缺失时，Stop Hook 只可把最近的同 `project_id`、同 `session_id` 有效 marker 用作只读基线。只有该基线的 `baseline_revision` 与 `baseline_receipt_id` 同当前已验证 Snapshot 完全一致时，才能证明自最近用户 Prompt 起没有权威状态变化并放行。缺少同 session 基线、基线损坏、revision 或 Receipt ID 不一致、当前 Receipt 无法验证时继续失败关闭。该兼容不改变授权的同 turn 约束，也不允许无 marker 的轮次提交或证明状态变更。

## 正式批准记录

Maker 于 2026-10-19 对本 chat 上轮列出的正式规格、逐项 Invariant 调整及实施/验收计划回复“确认”，批准本轮范围实施。该批准不授权更改任何真实 Managed Project 状态。

Maker 于 2026-10-31 确认 Stop Hook 续轮闭合方案：只在同 project、同 session 最近有效 marker 的 revision 与 Receipt ID 均证明零状态变化时兼容放行；不得补造 marker、放宽 Receipt/revision 校验或修改真实 Managed Project 权威状态。
