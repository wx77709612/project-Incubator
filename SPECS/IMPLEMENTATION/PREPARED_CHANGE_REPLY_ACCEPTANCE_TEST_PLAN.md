# 待批准变更回复验收计划

状态：TARGETED PASSED / FULL SUITE NOT GREEN；上游：[实施计划](PREPARED_CHANGE_REPLY_IMPLEMENTATION_PLAN.md)。测试对象为临时 Managed Project，通过 Kernel 建立和变更权威状态。

| ID | 场景 | 预期 |
| --- | --- | --- |
| PCR-A01 | `prepare_change` 成功 | 返回完整 `approval_message`；两个标识与当前权威请求一致；Receipt 为 `PREPARE_CHANGE` |
| PCR-A02 | 最终回复漏 `request_id` | 首次 Stop 阻断并提示正确请求 ID 与完整句 |
| PCR-A03 | 漏 `scope_digest` 或抄错摘要 | 首次 Stop 阻断并提示正确摘要 |
| PCR-A04 | 只有两个标识、没有完整批准句 | 首次 Stop 阻断并提示原样展示批准句 |
| PCR-A05 | 漏当前 `receipt_id` | 现有 Stop 规则继续阻断并提示正确回执 |
| PCR-A06 | 两个标识、完整批准句和最新 Receipt 均正确 | Stop 放行；阶段仍待 Maker 下一轮批准，不自动转换 |
| PCR-A07 | 仅查询已有请求、没有本轮 `prepare_change` | 不要求重复展示批准句 |
| PCR-A08 | 已续行 Stop 仍缺字段 | 防循环放行，但警告包含准确字段与引导；此路径不宣称强制保证 |
| PCR-A08b | 宿主续轮换 `turn_id` 且无精确 marker | 不把旧 marker 当作变更证明；警告仍附同 session 当前请求的准确批准句和回执 |
| PCR-A09 | Maker 下一轮真实批准 | 保留现有 Prompt 授权边界；仅显示批准句不能触发 Commit |

定向测试需先观察新增用例失败，再观察修复后通过。全量插件测试出现环境性 symlink `EPERM` 时单独记录，不把它计为本功能通过或失败。不得使用真实 English Learning Hub 状态作测试夹具。

## 结果（2026-11-06）

- PCR-A01–A08b：新增 Hook 集成测试先因缺少 `approval_message` 失败，修复后通过；宿主换 `turn_id` 的续轮提示测试也先失败后通过。Hook 文件除符号链接用例外 18/18 通过。
- PCR-A09：Web P0→P1 端到端测试 20/20 通过；准备后阶段保持 P0，缺 Maker Prompt 的 Commit 被拒绝，使用 `approval_message` 作为下一轮 Maker Prompt 后才转入 P1。
- 模板定向测试先失败后通过，最终 1/1；候选结构验证通过，包含 `src/kernel/approval-message.mjs`。
- 插件全量运行未通过。排除标题含链接、symlink、link 的用例后为 398/400：1 项仍因当前 Windows 无法创建 symlink（`EPERM`），1 项既有 Agent Entry 回滚竞争测试因 `AGENTS.md` 缺失返回 `ENOENT`；该后者单独重跑仍失败，与本次变更的文件及行为无交集。全量验收保持未闭合。
- 对最终代码再排除上述两项后，回归 398/398 通过，0 失败。该结果证明可运行范围内无新增失败，不替代无排除全量验收。
- 构建号 `0.3.0+codex.20261106223727` 的候选结构与独立 MCP 子进程 Full 均通过；ZIP 已核对包含 `.codex-plugin/plugin.json`、`.mcp.json`、新批准句模块、Stop Hook 和生产依赖。候选聚合哈希与 ZIP 哈希见[实施计划](PREPARED_CHANGE_REPLY_IMPLEMENTATION_PLAN.md)。
- 2026-11-07 正式安装后，CLI 列表显示新版本已安装且启用；安装目录聚合哈希与候选完全一致，从安装目录独立启动的 MCP Full 验证通过。现有聊天未作为热加载验收；无排除全量测试限制保持。
