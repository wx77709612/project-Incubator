# 待批准变更回复设计

状态：APPROVED；上游：[Decision 017](../ARCHITECTURE/ARCHITECTURE_DECISIONS.md#decision-017待批准变更的可复制回复与有界闭合)与[批准提案](../ARCHITECTURE/PREPARED_CHANGE_REPLY_CHANGE_PROPOSAL.md)。

`approval_message` 是 Kernel 对已持久化请求的纯文本投影，供 Agent 原样展示、Maker 下一轮选择复制。它不进入 State、不形成授权记录，也不触发 Commit。现有 Maker Prompt 解析与授权校验保持独立。

Stop 的回复义务来自精确轮次 marker、已验证的当前 Snapshot 和最新 Receipt。仅当最新 Receipt 为 `PREPARE_CHANGE`，且当前 revision 上有一个同 session 的 `PENDING` 请求，其 `project_revision` 等于当前 revision、当前 revision 高于 marker 基线时，新建请求才是本轮可执行的交付对象。前轮待批准请求、只读查询和被后续 mutation 覆盖的旧请求不触发此义务。

首次闭合失败时，逐项指出缺失的请求 ID、摘要、完整批准句或 Receipt ID，并给 Agent 一段可直接展示的正确批准文本和回执文本。已续行的 Stop 保持防循环放行，同时以可见警告重复正确字段；警告不冒充 Agent 回复或 Maker 授权。
