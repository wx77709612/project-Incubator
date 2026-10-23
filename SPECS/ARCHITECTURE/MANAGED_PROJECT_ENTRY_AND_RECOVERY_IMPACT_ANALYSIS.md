# Managed Project 接入与恢复分流影响分析

状态：DRAFT / AUDIT EVIDENCE；依赖[分流架构变更提案](MANAGED_PROJECT_ENTRY_AND_RECOVERY_CHANGE_PROPOSAL.md)获 Maker 审阅。本文识别影响，不构成实施授权。

## 已核实的现状与缺口

- Router 已定义 `NEW_PROJECT` 与 `ADOPT_EXISTING` 两种首次接入模式；现有项目级 `AGENTS.md` 草稿只写“新项目”，实施／验收未明确覆盖中途接入。
- `initialize_project` 只调用当前三 JSON 初始化；`assertProjectUninitialized` 对完整集合报 `PROJECT_ALREADY_INITIALIZED`，对部分集合报 `PROJECT_CONTROL_STATE_INCOMPLETE`。因此它不能承担已激活项目补齐或残缺状态修复。
- `inspect_project` 是只读恢复与状态查询。已有有效 JSON 的项目，根目录缺少 `AGENTS.md` 不应使其权威状态失效。
- 旧 V1／RC Markdown 材料属于 Legacy 证据，不是现行权威；现行 Runtime 不提供从旧资料到三 JSON 的受控迁移，也不提供三 JSON 损坏后的受控恢复。
- 现有五项实施计划和 A01–A09 只覆盖首次初始化。它们即使全部通过，也不能证明已激活补齐、旧版迁移或残缺恢复可用。

## 分层影响

| 层级 | 新增或修订的职责 | 不得改变 |
| --- | --- | --- |
| Architecture | 四路分流、双维分类、Maker 权限与 Decision 016 的适用范围；明确迁移／恢复新 Receipt 的身份 | Decision 015 的三 JSON 唯一权威与只读 `inspect_project` |
| Design | 新建／中途接入差别，`AGENTS.md` 差异呈现和逐项目审阅，旧资料字段来源及恢复草案 | 不让 Runtime 推断阶段或替 Maker 决定 |
| Contract | 专用只读诊断、入口补齐／核对、旧版迁移、权威恢复的输入输出和授权前置条件 | 不把 `initialize_project` 当存量修复接口 |
| Runtime | 安全文件操作、并发变化检测、迁移／恢复的受控持久化与失败关闭 | 不从聊天重建权威，不伪造旧 Receipt |
| Plan / Tests | 分流程工作包、故障注入、旧版样本、残缺样本、Maker 审阅和真实安装后验证 | 不用单元测试代替宿主验证 |

## 需下游解决而不能留给编码时猜测的问题

1. 只读诊断如何在 JSON 无法验证时仍报告逐文件事实，同时避免把不可信数据包装为有效状态。
2. 既有 `AGENTS.md` 的差异如何呈现；Maker 批准修改后，如何用文件摘要／身份检查防止覆盖刚被他人更新的版本。
3. 对已知 V1／RC 四份 Core Context 的版本识别、字段映射、来源记录和缺失字段处理；未知布局或无法映射路由只诊断。本次迁移 Receipt 不得冒充旧变更。
4. 部分 JSON 修复时区分“延续可验证历史”与“新恢复起点”，并明确原始字节保护、证据区、授权范围、失败回滚与 Pending Request 处理。若资料冲突或不足，必须停在草案。
5. 不存在任何 JSON 时，如何区分真正未激活与三个文件均被删除；不能仅凭文件数自动推断。

## 文档与实现边界

待修订的活动文件包括 Architecture Decisions、现有项目级入口 Design／Contract／Runtime、两份 Plan 及 `SPECS/README.md`。实现范围将涉及 Plugin Kernel、MCP Tool、Router、包内模板与测试，但只能在修订后的上游规格和计划获批后确定具体文件与接口。历史 `_V*`、真实 Managed Project 和已安装插件缓存均不在本次文档工作范围内。
