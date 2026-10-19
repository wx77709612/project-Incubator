# MCP Kernel 与 Skill 系统性对齐提案

状态：APPROVED；2026-10-19。

Maker 已批准方向，并于 2026-10-19 确认正式规格与实施/验收计划；本轮 Implementation Gate 已通过。

## 目标与权威

Project Incubator Plugin 0.3.x 的 MCP Kernel 是唯一现行实现。Plugin Router 是唯一现行入口。旧全局 `project-incubator` 退出活动执行路径；若保留同名兼容入口，只允许指向 Router、报告插件缺失，不得初始化、维护状态或复制领域流程。

Managed Project 的权威集合为 `.project-incubator/activation.json`、`state.json` 和 `latest-receipt.json`：Activation 定义身份与路由，State 是唯一项目业务状态，Receipt 证明最近变更闭合。Runtime Data 中 Pending Activation、Prompt 和 Authorization 记录不是第四份项目状态。

## 对根 AGENTS §9 Invariant 的逐项处置

| 既有规则 | 本轮提案 |
| --- | --- |
| PROJECT_STATE.md 是唯一状态权威 | 替代为 state.json；activation.json 与 latest-receipt.json 共同约束身份、路由和闭合 |
| Runtime State 不得替代 PROJECT_STATE.md | 替代为临时 Runtime Data、聊天和导出文档不得替代三个权威文件 |
| Context Mutation 经 Context Access Contract | 改为经 Kernel MCP 契约；禁止 Agent 直接编辑权威文件 |
| Transition 在 Markdown Mutation 持久化验证后完成 | 改为 Kernel 写入、revision、Read-back 与 Receipt 验证全部成功后完成 |
| Script 不直接读取或修改 Core Context | 不再要求四份 Markdown；领域 Script 不写三个权威文件，Kernel 是唯一写入者 |
| Runtime 不替 Maker Decision、不替 Agent 创作 | 保留 |
| State Change Requirement 不等于已修改；READY_FOR_TRANSITION 不等于已转换 | 保留 |
| Script Result 不等于 Gate Result；Gate 不直接改 Workflow/Context/Artifact | 保留 |
| Advisory 不产生 Runtime Command；Maker Authorization 只来自 Maker | 保留 |

以上逐项变更已由 Maker 在本正式提案审批时确认，实施时更新根 AGENTS 与活动 Decision。新增 Decision 015，按上述有效范围部分替代旧状态权威规则，不篡改历史 Decision。

## 边界

旧 Python Runtime、BOOTSTRAP_HOST_INTEGRATION、四份 Markdown Core Context 和逐文件 Multi-Context Mutation 不参与现行运行。旧资产保留为兼容回归输入，`SPECS/_V*` 始终冻结。不得把 Plugin Pending Activation Bootstrap 误删为旧 Host Bootstrap；前者属于现行授权机制。

不新增 Kernel、Tool Shape、Schema、Stage、Gate 或授权协议。Mod M0–M5、Desktop/Web P0–P6、Host Requirement 和 Evidence 上限保留。Managed Project 仍使用现行请求授权；Implementation Repository 的规格审批不要求 request_id/scope_digest。

## 交付与 Gate

影响清单见 [影响分析](KERNEL_ALIGNMENT_IMPACT_ANALYSIS.md)。下游文档均已获批：Design → Contract → Runtime → Implementation/Acceptance。审批前仅调查、规格编写与测试基线采集；审批后先提交失败漂移测试，再改 Skill、安装来源与模板。禁止直接修改插件缓存；禁止修改 scriverse 业务和状态。

## 正式批准记录

Maker 于 2026-10-19 对本 chat 上轮列出的正式规格、逐项 Invariant 调整及实施/验收计划回复“确认”，批准本轮范围实施。该批准不授权更改任何真实 Managed Project 状态。
