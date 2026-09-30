# Project Incubator Plugin 人工验收台账

本文件是新 Plugin 人工验收的唯一记录入口。仅记录轮次、结论、关键证据和下一步，不保存完整对话。

| Round | 场景 | 结果 | 关键证据 | 下一步 |
| --- | --- | --- | --- | --- |
| 1 | 路由提议 | PASS | 提议 `mod-incubator + sims-4`；未激活；未创建项目状态 | 形成 Activation Request |
| 2 | Activation Request | PASS | 返回 `request_id`、`scope_digest`、范围和初始状态；未初始化 | Maker 明确授权初始化 |
| 3 | Project Initialization | FAIL | Receipt 闭环成功，但 `inspect_project` 同时返回 `ACTIVE` 与“等待激活”；`decisions.active` 为空 | 修复 Activation Bootstrap 后重放 |
| 4 | Activation Bootstrap 重放 | FAIL | 新 Request 仍绑定旧项目根目录；该目录已有三个权威文件，但 Runtime 仍允许 `prepare_activation` | 已激活项目必须拒绝再次准备激活 |
| 5 | 空白根目录 Activation Request | PASS | Request 绑定新根目录；六项 Product Decision 与激活后 revision 0 状态进入 `scope_digest`；权威文件仍为空 | Maker 授权初始化并验证 Active Decision View |

## 失败原因与修复状态

- `Post-activation state semantic drift`：申请阶段叙述被直接持久化为初始化后的权威状态。
- 修复已实现：初始状态必须描述激活后语义；Product Decision 由激活授权绑定并写入 Active Decision View。
- 自动化验证：Plugin 测试 `67/67` 通过，修复版已安装为 `0.1.0+codex.20260930033652`。
- Round 4 证明上一项语义修复已进入 Agent 输出，但暴露新的 Runtime 前置条件缺口：已初始化项目仍能创建 Pending Activation Request。
- Runtime Guard 已实现：完整权威状态返回 `PROJECT_ALREADY_INITIALIZED`，部分权威状态返回 `PROJECT_CONTROL_STATE_INCOMPLETE`，且不创建 Pending Activation Request。
- 自动化验证：Plugin 测试 `69/69` 通过；修复版已安装为 `0.1.0+codex.20260930052300`。
- Round 4 的无效 Pending Request 已按 `request_id`、`scope_digest` 和项目根目录精确匹配后清理；已安装 Runtime 对旧项目返回 `PROJECT_ALREADY_INITIALIZED`。
- Round 5 已在全新空白根目录通过 Activation Request 重放；Round 3、Round 4 的失败历史保持不变。
- 待办：授权并执行初始化，验证六项 Product Decision 的真实 Authorization、revision 0、Receipt 和状态摘要。
