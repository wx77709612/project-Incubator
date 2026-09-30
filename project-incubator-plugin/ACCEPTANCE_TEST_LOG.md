# Project Incubator Plugin 人工验收台账

本文件是新 Plugin 人工验收的唯一记录入口。仅记录轮次、结论、关键证据和下一步，不保存完整对话。

| Round | 场景 | 结果 | 关键证据 | 下一步 |
| --- | --- | --- | --- | --- |
| 1 | 路由提议 | PASS | 提议 `mod-incubator + sims-4`；未激活；未创建项目状态 | 形成 Activation Request |
| 2 | Activation Request | PASS | 返回 `request_id`、`scope_digest`、范围和初始状态；未初始化 | Maker 明确授权初始化 |
| 3 | Project Initialization | FAIL | Receipt 闭环成功，但 `inspect_project` 同时返回 `ACTIVE` 与“等待激活”；`decisions.active` 为空 | 修复 Activation Bootstrap 后重放 |
| 4 | Activation Bootstrap 重放 | FAIL | 新 Request 仍绑定旧项目根目录；该目录已有三个权威文件，但 Runtime 仍允许 `prepare_activation` | 已激活项目必须拒绝再次准备激活 |
| 5 | 空白根目录 Activation Request | PASS | Request 绑定新根目录；六项 Product Decision 与激活后 revision 0 状态进入 `scope_digest`；权威文件仍为空 | Maker 授权初始化并验证 Active Decision View |
| 6 | Project Initialization 重放 | PASS | Revision 0、六项 Active Product Decision、真实 Authorization、状态摘要与 Receipt 均独立验证一致 | 验证直接写入拦截 |
| 7 | 权威文件直接写入拦截 | FAIL | `apply_patch` 未被 PreToolUse 拒绝，仅因补丁上下文不匹配而失败；三份权威文件、Revision 与 Receipt 均未改变 | 信任当前 Plugin Hook 后重放 |

## 失败原因与修复状态

- `Post-activation state semantic drift`：申请阶段叙述被直接持久化为初始化后的权威状态。
- 修复已实现：初始状态必须描述激活后语义；Product Decision 由激活授权绑定并写入 Active Decision View。
- 自动化验证：Plugin 测试 `67/67` 通过，修复版已安装为 `0.1.0+codex.20260930033652`。
- Round 4 证明上一项语义修复已进入 Agent 输出，但暴露新的 Runtime 前置条件缺口：已初始化项目仍能创建 Pending Activation Request。
- Runtime Guard 已实现：完整权威状态返回 `PROJECT_ALREADY_INITIALIZED`，部分权威状态返回 `PROJECT_CONTROL_STATE_INCOMPLETE`，且不创建 Pending Activation Request。
- 自动化验证：Plugin 测试 `69/69` 通过；修复版已安装为 `0.1.0+codex.20260930052300`。
- Round 4 的无效 Pending Request 已按 `request_id`、`scope_digest` 和项目根目录精确匹配后清理；已安装 Runtime 对旧项目返回 `PROJECT_ALREADY_INITIALIZED`。
- Round 5 已在全新空白根目录通过 Activation Request 重放；Round 3、Round 4 的失败历史保持不变。
- Round 6 已完成初始化闭环：六项 Product Decision 共用本轮真实 Authorization，`inspect_project` 与 Receipt 校验通过。
- Round 7 未验证到直接写入拦截。根因证据：当前 `config.toml` 只有 enforcement spike 的 Hook `trusted_hash`，没有 `project-incubator-plugin@personal` 的 Hook 信任记录；官方 Hook 规则规定未信任的插件 Hook 会被跳过。
- Round 7 状态完整性未受损：三份权威文件哈希不变，Revision 仍为 `0`，Receipt 仍为 `receipt-05769fe4-fc73-4133-8db8-7dae51f57932` 且校验成功。
- Maker 已信任当前 Plugin 的 UserPromptSubmit、PreToolUse 与 Stop Hook；CLI 确认三个 Hook 均存在对应 `trusted_hash`。
- CLI 对照检查发现带引号的相对路径可绕过旧版 PreToolUse 匹配；已新增回归测试并收紧命令文本中的权威路径边界识别。
- 自动化验证：Plugin 测试 `70/70` 通过，Plugin 结构校验与三个 Skill 校验均通过。
- 待办：安装新的缓存版本；Maker 审阅变化后的 Hook 哈希，再重放直接写入拦截。
