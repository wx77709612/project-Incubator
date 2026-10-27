# Codex 协作入口与权威恢复契约

状态：APPROVED；Maker 于 2026-10-23 批准本契约及配套实施与验收计划，并于 2026-10-26 批准真实宿主授权上下文修正。上游：[Design](../DESIGN/CODEX_PROJECT_AGENT_ENTRY_DESIGN.md)。

## 1. 首次接入返回

`initialize_project` 输入和既有授权语义不变。成功返回增加：

```json
"agent_entry": {
  "path": "AGENTS.md",
  "status": "CREATED | CURRENT | EXISTING_REVIEW_REQUIRED"
}
```

枚举竖线仅表示互斥选项。`CREATED` 表示本次排他创建并回读成功；`CURRENT` 和 `EXISTING_REVIEW_REQUIRED` 均表示原文件未修改。Agent Entry 不进入 State、revision 或 Receipt。

## 2. 任务首次入口检查与补建

`prepare_agent_entry` 输入：`project_root`、`session_id`。`session_id` 必须来自 Codex 宿主的 `CODEX_SESSION_ID`，不得由 Agent 推测。它不读取或修改权威 JSON。

- 文件与模板相同：返回 `{event:"AGENT_ENTRY_INSPECTED",agent_entry:{path,status:"CURRENT"}}`。
- 文件存在但不同：返回 `status:"EXISTING_REVIEW_REQUIRED"` 和双方 SHA-256，不创建写入请求。
- 文件不存在：在 Runtime Data 建立 24 小时短期请求，返回 `{event:"AGENT_ENTRY_INSTALL_PREPARED",request_id,scope_digest,agent_entry:{path,status:"MISSING"}}`。

`install_agent_entry` 输入：`project_root`、`request_id`、`scope_digest`、`session_id`；兼容调用可携带但不要求 `turn_id`。Agent 不取得或猜测宿主内部 `turn_id`。Kernel 从 Hook Runtime Data 的最新指针中定位同一规范项目根、同一项目 ID、同一 session、同一请求编号及摘要且意图为明确批准的 Prompt，并使用该记录的真实 `turn_id` 完成既有授权校验。指针发布由带唯一所有者和前置写入意图的同一上下文排他锁串行化；锁、冲突、意图目录或遗留 `claimed-*` 任一存在时均不得读取授权。若 Hook 记录重叠，后到调用不得等待后插入，而是标记顺序不明确，任何一条都不能授权。后续第一条无并发 Prompt 仅确认并隔离冲突且仍返回 `PROMPT_ORDER_AMBIGUOUS`；再下一条独立、无并发且明确的 Prompt 经第二次原子搬移和静默复查后才可重建指针。冲突确认必须在删除旧证据前持久化；确认写入失败或搬移中断仍须保留可见阻断。异常退出留下的陈旧锁遵循同样的两步确认规则；超过时限的写入意图不依赖可能复用的 PID，先转成冲突证据再清理。被回收 intent 的调用不得复用旧 token；取得锁和每次发布前必须同时校验 owner token 与自身 intent token。旧所有者不得删除或冒充新锁。`captured_at` 不决定先后；旧 Prompt 不得在较新 Prompt 不匹配、拒绝、指针不完整、并发歧义或已被替代时回退使用。只有请求未过期且授权证据精确匹配时，才排他创建模板并回读，返回 `status:"CREATED"`。目标在准备后出现时返回 `AGENT_ENTRY_SOURCE_CHANGED`，不覆盖。

Router 仅在当前 Codex 任务首次进入该 `project_root` 时调用 `prepare_agent_entry`。这是一条 Agent 行为契约，不通过持久业务状态追踪。

## 3. 权威恢复准备

`prepare_authority_recovery` 输入：

```text
project_root, session_id, summary, proposed_activation, proposed_state
```

Kernel 分别诊断三个权威路径并返回 `authority_diagnostics`，每项包含 `path`、`status`（`MISSING | VALID | INVALID`）、可用时的稳定错误码和现存字节 SHA-256。只有完整集合不能通过现行 Snapshot／Receipt 验证时才能准备恢复；完整且有效时返回 `AUTHORITY_RECOVERY_NOT_REQUIRED`。

Kernel 校验候选 Activation、State、Registry Route 与 Workflow；`proposed_state.pending_requests` 必须为空。若现存 State 可解析，候选 revision 必须是其 revision + 1；否则必须是 0。请求的 `scope_digest` 覆盖项目规范路径、诊断指纹、完整候选、summary 和操作名。请求保存在 Runtime Data，24 小时过期，不写项目。

成功返回：

```json
{
  "event": "AUTHORITY_RECOVERY_PREPARED",
  "request_id": "recovery-...",
  "scope_digest": "...",
  "authority_diagnostics": [],
  "proposed_revision": 0
}
```

## 4. 权威恢复提交

`recover_project_authority` 输入：`project_root`、`request_id`、`scope_digest`、`session_id`；兼容调用可携带但不要求 `turn_id`。Kernel 按与补建相同的规范项目根和最新 Prompt 规则，从 Hook Runtime Data 取得真实 turn，并要求当前 Maker Prompt 明确批准同一请求和摘要；写入前仍重新核对三个路径的存在性与字节 SHA-256。

Kernel 清空 Pending Request，覆盖 `last_change` 为 `RECOVER_PROJECT_AUTHORITY`，受控写入完整三个 JSON、回读并验证新 Receipt。成功返回 `{activation,receipt,recovery:{baseline:"CONTINUED"|"REESTABLISHED"}}`；`CONTINUED` 对应可解析旧 State 的下一 revision，`REESTABLISHED` 对应 revision 0 恢复基线。

新 Receipt 的 Authorization Ref 指向本次 Maker Prompt。旧文件和旧资料只是恢复输入，不被新 Receipt 宣称为已验证历史。

## 5. 稳定失败语义

| 错误码 | 含义 | 写入结果 |
| --- | --- | --- |
| `AGENT_ENTRY_TEMPLATE_INVALID` | 包内模板缺失、空白或含禁用旧指令 | 不写项目 |
| `AGENT_ENTRY_PATH_UNSAFE` | 目标是目录、链接或不可读对象 | 不覆盖 |
| `AGENT_ENTRY_SOURCE_CHANGED` | 准备后目标出现或变化 | 不覆盖 |
| `AGENT_ENTRY_REQUEST_NOT_FOUND` / `AGENT_ENTRY_REQUEST_EXPIRED` | 补建请求不存在或过期 | 不写项目 |
| `AUTHORITY_RECOVERY_NOT_REQUIRED` | 三 JSON 已完整并验证通过 | 不创建恢复请求 |
| `AUTHORITY_RECOVERY_REQUEST_NOT_FOUND` / `AUTHORITY_RECOVERY_REQUEST_EXPIRED` | 恢复请求不存在或过期 | 不写项目 |
| `PROMPT_ORDER_AMBIGUOUS` | 最新 Prompt 指针不完整、损坏、指向不存在的记录，或同一上下文的 Hook 记录发生重叠 | 不写项目，不回退旧批准；第一条无并发 Prompt 只确认冲突并仍失败，再发送一条独立明确 Prompt 重建指针 |
| `PROMPT_SUPERSEDED` | 授权消费前已出现后续 Prompt | 不写项目，不回退旧批准 |
| `RECOVERY_SOURCE_CHANGED` | 准备后任一权威路径变化 | 不写项目 |
| `RECOVERY_STATE_REVISION_INVALID` | 候选 revision 不符合延续或重建规则 | 不创建请求 |
| `RECOVERY_WRITE_FAILED` | 写入或回读失败但操作前字节已恢复 | 恢复失败，原状保留 |
| `RECOVERY_ROLLBACK_INCOMPLETE` | 无法完整恢复操作前字节 | 报告 `residual_paths`，不得宣称成功 |

现有授权、Prompt、Scope、项目路径、Registry、Schema 和 Workflow 错误继续使用既有稳定码。`inspect_project`、`prepare_change`、`commit_change`、`decline_change` 的接口和成功形状不因本契约变化。
