# Managed Project 权威恢复与 AGENTS 补齐影响分析

状态：APPROVED / AUDIT EVIDENCE；配套[架构提案](MANAGED_PROJECT_ENTRY_AND_RECOVERY_CHANGE_PROPOSAL.md)，不单独授权实现。

## 已核实的现状

- `initialize_project` 只写三个权威 JSON，目标项目的 `AGENTS.md` 不在现行闭合条件中。
- `inspect_project` 会读取并验证完整权威集合；任一文件缺失、JSON 无法解析或 Receipt 不一致时失败关闭。
- `prepare_activation` 对部分权威文件返回 `PROJECT_CONTROL_STATE_INCOMPLETE`；普通变更也要求先读到完整 Snapshot。
- 现有公开 MCP Tool 没有修复残缺权威集合的操作。现有“恢复”仅指从完整 Snapshot 恢复工作上下文。
- State Store 在一次可捕获的写入失败中会恢复操作前字节，但不能修复任务开始前已经残缺或损坏的项目。
- Codex 会把发现的 `AGENTS.md` 注入任务上下文；没有必要在同一任务的每次 Plugin 调用中重复加载。

## 必要改动

| 位置 | 最小新增能力 | 保持不变 |
| --- | --- | --- |
| Router Skill | 当前任务首次进入项目时检查一次 `AGENTS.md`；权威文件只在实际使用时报错并转入恢复提案 | 不批量扫描，不给每次调用增加四文件预检 |
| Agent Entry | 包内中文模板、只读检查、首次接入创建、已接入项目经确认补建 | 已有文件不覆盖；不参与 revision 或 Receipt |
| Kernel | 两步授权的权威恢复请求；写入前校验原文件指纹，写后三文件回读和 Receipt 验证 | 正常初始化和 Mutation 接口不改义 |
| Packaging / Tests | 模板自包含、首次接入、任务首次检查、权威恢复和正常路径无重复检查 | 不恢复 Legacy Python/Markdown Runtime |

## 主要风险与验收重点

1. 恢复请求准备后文件被外部修改：提交必须因指纹变化停止。
2. 现存 State 可解析与不可解析的 revision 处理不同：分别验证“下一 revision”和“revision 0 恢复基线”。
3. 新 Receipt 只能证明本次恢复，不能宣称补回丢失历史；旧 Pending Request 不继承。
4. 当前任务中途创建 `AGENTS.md` 后，当前 Agent 必须显式读取一次；后续任务验证 Codex 原生加载。
5. 已有正常项目不应因为本能力增加额外入口预检、阶段、Gate 或状态 Mutation。

活动 Architecture Decision、Design、Contract、Runtime 和两份计划需要同步；历史 `_V*`、真实 Managed Project 和已安装缓存不在规格修改范围内。
