# 阶段变更请求批准回复：事实与影响分析

状态：APPROVED / AUDIT EVIDENCE；配套[架构提案](PREPARED_CHANGE_REPLY_CHANGE_PROPOSAL.md)，不单独授权实现。

## 已验证事实

- `project-incubator-plugin/src/server.mjs` 的 `prepare_change` 创建 `request_id`、`scope_digest`，通过 `commitProjectState` 增加 `PENDING` 请求并返回 `CHANGE_PREPARED`、两个标识及 Receipt；不返回批准句。
- `project-incubator-plugin/hooks/stop.mjs` 验证最新 Receipt 与轮次 marker；本轮 revision 变化时只检查最终回复包含最新 `receipt_id`。`stop_hook_active === true` 时，失败结果改为 `continue: true` 和警告。
- `project-incubator-plugin/src/kernel/prompt-events.mjs` 解析 Maker Prompt 的明确批准意图、唯一请求 ID 与唯一 64 位摘要；`authorization.mjs` 再核对请求、摘要、session、turn 和时效。Agent 展示批准句本身不构成授权。
- `project-incubator-plugin/src/kernel/authorization.mjs` 要求待批准请求的 `project_revision` 等于当前 revision，因此后续提交覆盖旧请求的 revision 后，旧请求不再可执行。
- 当前 `hooks.test.mjs` 的受控变更回复测试只覆盖 Receipt ID；既有续轮测试证明第二次 Stop 不重复阻断。定向基线：18 项中 17 项通过，1 项因当前 Windows 环境不允许创建 symlink 而失败；这不是本缺陷的行为失败。
- [Codex Hooks 文档](https://learn.chatgpt.com/docs/hooks)说明 Stop `decision: "block"` 只触发自动续行；`stop_hook_active` 标识已续行。文档未提供直接替换最终回复的 Stop 输出字段。

## 推断与影响

| 层级 | 预期改动 | 风险与验证重点 |
| --- | --- | --- |
| Architecture / Design | 定义“待批准请求交付”与“本轮新建且仍有效”的边界 | 不能把展示文本等同 Maker 决策；避免旧请求误拦 |
| Contract | `prepare_change` 增加 `approval_message`；Stop 校验字段及失败原因 | 保持旧字段兼容；批准句必须可被现有 Prompt 解析器识别 |
| Runtime | 从已验证 Receipt、当前 Snapshot、精确 marker 关联本轮请求 | 仅查询、其他 session、后续 mutation、缺失 marker 均有明确处理 |
| Implementation / Tests | `server.mjs`、`hooks/stop.mjs` 与定向集成及端到端测试 | 覆盖漏 ID、错摘要、漏批准句、漏 Receipt、全部正确、旧请求查询 |

## 未验证的解释

本次现场报告中的首次回复确实漏了 Receipt ID，Stop Hook 按现行规则拦截；尚无证据证明 Agent 在其他轮次一定会漏掉批准字段。加强闭合检查是针对可复现的契约缺口，而不是对此次 Agent 行为成因的唯一解释。
