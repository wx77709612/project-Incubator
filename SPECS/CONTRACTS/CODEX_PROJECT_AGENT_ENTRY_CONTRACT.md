# Codex 项目级协作入口契约

状态：DRAFT / REVISION REQUIRED；当前只补充首次初始化，待[接入与恢复分流提案](../ARCHITECTURE/MANAGED_PROJECT_ENTRY_AND_RECOVERY_CHANGE_PROPOSAL.md)审阅后修订，不得作为完整分流的实现依据。原上游：[Design](../DESIGN/CODEX_PROJECT_AGENT_ENTRY_DESIGN.md)。不改变既有 Maker 授权或三个 JSON Schema。

## 1. 输入与输出

`initialize_project` 输入仍为 `project_root`、`request_id`、`scope_digest`、`session_id`、`turn_id`。服务继续先验证 Pending Activation、路由、初始状态、PromptRef 与 Maker Authorization。失败授权不得产生 `AGENTS.md` 或三个权威文件。

成功返回保留 `activation` 和 `receipt`，新增：

```json
"agent_entry": {
  "path": "AGENTS.md",
  "status": "CREATED | EXISTING_REVIEW_REQUIRED"
}
```

上述 `status` 表示互斥枚举值，不是实际返回的含竖线字符串。`CREATED` 只在新文件与模板字节一致、回读成功时出现；`EXISTING_REVIEW_REQUIRED` 只在已有可读普通文件完全未修改时出现。成功 Receipt 仍仅证明权威 State 变更闭合；`agent_entry` 独立证明协作入口处理结果，不增加第四份权威状态。Maker 应看到已有文件的人工核对提示。

## 2. 错误码与副作用

| 稳定错误码 | 触发条件 | 合同结果 |
| --- | --- | --- |
| `AGENT_ENTRY_TEMPLATE_INVALID` | 包内模板缺失、不可读、空白或违反最小模板检查 | 初始化停止；不消费请求 |
| `AGENT_ENTRY_PATH_UNSAFE` | 目标已存在但不是可读普通文件，含目录、链接、不可读文件 | 不覆盖目标；初始化停止 |
| `AGENT_ENTRY_CONFLICT` | 排他创建遭遇并发 `EEXIST` | 不覆盖、不删除竞争者文件；初始化停止 |
| `AGENT_ENTRY_WRITE_FAILED` | 新建或同步写入失败 | 尝试安全撤销；初始化停止 |
| `AGENT_ENTRY_READBACK_MISMATCH` | 新建内容回读与模板不一致 | 尝试安全撤销；初始化停止 |
| `AGENT_ENTRY_ROLLBACK_INCOMPLETE` | 本次失败后无法证明入口或权威文件已安全恢复 | 失败且报告残留路径；不得声称未初始化或完整初始化 |

既有 `PROJECT_ALREADY_INITIALIZED`、`PROJECT_CONTROL_STATE_INCOMPLETE`、授权与 Receipt 错误语义保留。失败返回使用现有 MCP `isError` 与 `structuredContent.error.code` 形状；可追加 `error.residual_paths` 为相对项目路径数组，仅在回滚不完整时使用，不暴露临时 Runtime Data。不得把原始系统错误文本当作稳定错误码。

## 3. 初始化顺序与幂等边界

在项目串行化域内，先确认三个权威文件均不存在，再检查/创建 Agent Entry，然后写三个 JSON 并验证 Receipt；只有全部成功才消费 Pending Activation。已有可读普通 `AGENTS.md` 不更改，即使含旧版内容也只报告人工核对，不自动将其改为新模板。

`initialize_project` 不变成修复已激活项目的 API。失败后重试仍需通过原授权有效期、PromptRef 与权威文件检查；不保证任意部分失败都可自动重试。权威文件部分残留由现行失败关闭规则处理。
