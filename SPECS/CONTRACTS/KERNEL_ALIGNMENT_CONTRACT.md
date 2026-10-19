# Kernel 与 Skill 对齐契约

状态：APPROVED；上游：[Design](../DESIGN/KERNEL_ALIGNMENT_DESIGN.md)。

| ID | 输入/前提 | 输出与失败语义 |
| --- | --- | --- |
| KAC-01 | 未激活项目、Maker Intent | propose_route 仅提议；prepare_activation 建立临时请求；真实 Maker 下一轮批准后 initialize_project。保留现行 project/session/turn/request/digest 绑定 |
| KAC-02 | 已激活项目恢复、状态查询、下一步询问 | 调用 inspect_project；Snapshot、Receipt 验证失败立即报告稳定错误码，不猜测、不回退 Markdown/get_project_state |
| KAC-03 | 已验证 activation 路由 | 只分发到已注册 Child/Host；Desktop/Windows、Mod/Sims 4、Web/null；不默认类型或 Host |
| KAC-04 | 拟议受控状态变更 | prepare_change → Maker 有效授权 → commit_change；拒绝经 decline_change；不由仓库规格审批代替 Managed Project 授权 |
| KAC-05 | 初始化/Prepare/Commit/Decline 结果 | 核对 revision、Read-back、Receipt ID/state hash/last_change 引用后报告完成；不修改 Kernel 当前工具语义 |
| KAC-06 | 旧入口调用 | 仅转交 Router；Plugin 不可用则停止，无 Python/Bootstrap/Markdown 执行回退 |
| KAC-07 | 模板、安装源、候选包 | 当前指导不能声明 Markdown 权威或要求旧 Runtime、旧 Host Bootstrap、逐文件 Mutation；Legacy 资产明确分区，不混入候选包 |

API 名称、Schema、现有错误码和返回 Shape 以当前 server.mjs 与 schemas.mjs 为实现事实；本轮不新增授权机制。inspect_project 的摘要继续遵守 Plugin Router references/status-summary.md；原始 Snapshot 工具不承担摘要恢复契约。

实施仓库的 Maker 审批只需对正式文档与计划表达明确同意，不要求 Managed Project request_id/scope_digest。测试中的模拟授权只适用于临时夹具，不能为真实项目生成 Maker Authorization。

## 正式批准记录

Maker 于 2026-10-19 对本 chat 上轮列出的正式规格、逐项 Invariant 调整及实施/验收计划回复“确认”，批准本轮范围实施。该批准不授权更改任何真实 Managed Project 状态。
