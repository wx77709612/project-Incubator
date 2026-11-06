# 待批准变更回复运行规范

状态：APPROVED；上游：[契约](../CONTRACTS/PREPARED_CHANGE_REPLY_CONTRACT.md)。

1. Kernel 在 `commitProjectState` 成功返回已验证 Receipt 后，按刚生成并持久化的 `request_id` 与 `scope_digest` 形成 `approval_message`；不修改 State Schema。
2. Stop 先执行现有根目录定位、Snapshot 读取、最新 Receipt 验证和 marker 分支；验证时要求回读的最新 Receipt ID 等于刚读取的 Snapshot Receipt ID，避免跨两次读取误绑定。无精确 marker 时维持现行零状态变化兼容，绝不借兼容 marker 证明本轮创建请求。
3. 精确 marker 下，若 revision 未变化，直接按现行规则放行。若发生变化，先验证 Receipt 属于本轮，再核对最新 `receipt_id`。
4. 只有 Receipt operation 为 `PREPARE_CHANGE`、Receipt 的新 revision 等于当前 revision、当前 `PENDING` 请求的 `project_revision` 等于该 revision 且 session 匹配时，检查 `request_id`、`scope_digest` 和完整 `approval_message`。没有匹配请求时按现有 Receipt 规则处理，不从聊天或 Runtime Data 猜测请求。
5. 失败原因列明实际缺失项，并附 `approval_message` 与 `receipt_id`，引导 Agent 在本轮最终回复中原样展示。宿主续轮若换了 `turn_id` 且缺少精确 marker，仍按现有规则失败关闭；若最新已验证请求属于同 session，可在失败警告中附准确批准句与回执，不据此放宽 marker 校验。`stop_hook_active` 保持一次续行上限。Hook 被禁用、失败或超时时不声称强制闭合。
