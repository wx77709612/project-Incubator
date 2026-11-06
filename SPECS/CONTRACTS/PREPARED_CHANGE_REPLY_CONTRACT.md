# 待批准变更回复契约

状态：APPROVED；上游：[设计](../DESIGN/PREPARED_CHANGE_REPLY_DESIGN.md)。

| ID | 输入与前提 | 输出与失败语义 |
| --- | --- | --- |
| PCR-01 | `prepare_change` 成功提交 `PREPARE_CHANGE` | 现有 `event`、`request_id`、`scope_digest`、`receipt` 保留；新增 `approval_message = "我明确批准变更请求 <request_id>，scope_digest: <scope_digest>。"`；失败不返回可误认有效的批准句 |
| PCR-02 | Stop 的精确 marker 和最新 Snapshot/Receipt 验证通过，且最新 Receipt 为本轮 `PREPARE_CHANGE` | 从当前 `PENDING` 请求读取 `request_id`、`scope_digest`；最终回复须包含两个准确标识、完整 `approval_message` 与当前 `receipt_id` |
| PCR-03 | PCR-02 任一字段缺失或不匹配 | 首次 Stop 返回 `decision: "block"`，原因逐项列出字段并附准确的可复制文本；`stop_hook_active` 时返回 `continue: true` 和包含准确信息的警告 |
| PCR-04 | 没有本轮可执行的 `PREPARE_CHANGE` 请求 | 不新增批准回复义务；既有 Receipt、marker 与其他闭合检查照常执行 |

Agent 展示 `approval_message` 不构成 Maker Authorization。`commit_change` 仍须在下一轮从真实 Maker Prompt 验证请求、摘要、session、turn、时效与明确批准意图。

新激活项目的包内 `AGENTS.md` 模板应提醒 Agent 原样展示 `approval_message` 与 `receipt_id`，并明确等待 Maker 下一轮批准；已有项目的文件不得自动覆盖，Stop Hook 仍提供当轮纠正提示。
