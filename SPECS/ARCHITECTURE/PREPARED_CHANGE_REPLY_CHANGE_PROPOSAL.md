# 阶段变更请求的批准回复闭合提案

状态：APPROVED；Maker 于 2026-11-06 确认有界方案并要求对 Agent 提供明确的言语引导。配套[事实与影响分析](PREPARED_CHANGE_REPLY_IMPACT_ANALYSIS.md)。本批准不授权任何真实 Managed Project 的阶段转换或权威文件写入。

## 问题与目标

`prepare_change` 已经通过 Kernel 创建待批准请求并提交 `PREPARE_CHANGE` Receipt，但结果仅交付 `request_id`、`scope_digest` 和 `receipt`。Agent 必须自行组织 Maker 的批准回复。Stop Hook 目前仅在本轮 revision 变化时检查最终消息是否包含最新 `receipt_id`，因此不能发现错误或缺失的批准信息。

目标是让 Kernel 给出可直接复制的批准句，并在正常 Stop 闭合时核对本轮刚准备、仍可执行的请求及最新 Receipt。批准句只是供 Maker 下一轮选择的文本，不代表授权；`commit_change` 仍须验证真实 Maker Prompt、会话、轮次、请求与摘要。

## 拟议变更

1. `prepare_change` 在现有返回字段之外增加 `approval_message`：`我明确批准变更请求 <request_id>，scope_digest: <scope_digest>。` 字段由 Kernel 使用本次持久化请求的两个标识生成，不从 Agent 文案或 Runtime Data 推断。
2. Stop Hook 完成现有 Snapshot、Receipt 与精确轮次 marker 校验后，若最新已验证 Receipt 的 operation 为 `PREPARE_CHANGE`、对应的 `PENDING` 请求的 `project_revision` 等于当前 revision、请求所属 session 等于当前 session，且当前 revision 大于该 marker 的 baseline，则逐项检查最终回复：准确的 `request_id`、准确的 `scope_digest`、完整的 `approval_message`、当前 `receipt_id`。错误原因指出缺失或不匹配的字段。
3. 只读查询、前轮遗留请求、当前轮没有新建请求、已被后续状态变更覆盖的旧请求，均不触发新增批准回复检查。现有 Receipt 校验、缺失 marker 失败闭合与 Maker 授权边界保持。
4. Hook 首次 `decision: "block"` 要求 Agent 补齐回复。由于宿主的 `stop_hook_active` 表示该轮已经续行，现有防循环分支仍只发出警告；该分支应带上由已验证权威状态重建的缺失字段与完整批准句，尽量让 Maker 可见，但不把 Hook 警告当作 Agent 最终回复或 Maker 授权。

## 宿主能力限制与待决事项

Codex 的 Stop Hook 可以要求 Agent 再生成一次，但不能直接替换最终回复；Hook 可能被关闭、失败或超时。现有 `stop_hook_active` 防循环策略在第二次仍有遗漏时会放行。因此“Maker 最终回复在所有情况下必定完整”不能由当前 Hook 机制保证。反复返回 `block` 可能造成无限续轮，也没有证据表明宿主会提供安全上限。

Maker 已确认“Kernel 确定性生成 + 正常 Stop 首次强制补全 + 续轮警告展示完整信息”的有界保证，并特别要求给 Agent 明确的言语引导。验收按可观察的单次闭合约束执行；无条件的最终回复保证需要宿主提供最终回复替换或不可绕过的终结前校验能力，本插件当前不能宣称实现。

## 不变边界与下游顺序

- 不修改 `activation.json`、`state.json`、`latest-receipt.json` 的 Schema；不增加新的权威文件。
- `approval_message` 不产生 Maker Authorization，不自动执行 `commit_change`、`decline_change` 或阶段转换。
- 不直接编辑任何 Managed Project 权威状态；测试仅使用临时项目并通过 Kernel 写入。
- Maker 确认本提案后，再依次更新 Architecture Decision、Design、Contract、Runtime Specification、Implementation Plan 与 Acceptance Test Plan，批准计划后才修改插件源码和测试。
