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
| 7R | 信任 Hook 后重放直接写入拦截 | FAIL | PreToolUse 已在命令执行前拒绝直接写入，状态与 Receipt 未变化；但 Stop Hook 因缺少 `CODEX_HOME` 重复返回 `decision: block`，形成不可终止循环 | 改用 Plugin Data 契约并增加 Stop 二次触发熔断 |
| 7S | Plugin Data 与 Stop 熔断重放 | PASS | 加载 `0.1.0+codex.20260930115950`；写入探针执行前被拒绝；三份权威文件、Revision、Action 与 Receipt 均未变化；Stop 正常放行且无循环 | 单独处理只读命令被 PreToolUse 误拦截的问题 |
| 8 | 只读放行与写入保护并存 | PASS | 加载 `0.1.0+codex.20260930143443`；两条只读命令退出码为 0；写入探针执行前被拒绝；权威文件、Revision、Action 与 Receipt 均未变化；Stop 正常结束 | 结束 Hook 基础验收，进入受控状态推进测试 |
| 9 | 非法 Mod 阶段跳级拒绝 | PASS | 加载 `0.1.0+codex.20261001102149`；`prepare_change` 对 `M0_BOUNDARY -> M4_IMPLEMENT` 返回 `ILLEGAL_TRANSITION`；未创建 Pending Request、未调用 Commit，权威状态与 Receipt 均未变化 | 使用真实宿主版本信息准备合法 `M0 -> M1` 变更 |

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
- 修复版已安装为 `0.1.0+codex.20260930064453`；CLI 对 `apply_patch` 与带引号 PowerShell 路径均返回 `deny`。Hook 配置定义未变化，既有三条信任记录继续有效。
- 待办：在重新加载插件的新测试会话中重放直接写入拦截。
- Round 7R 已证明 PreToolUse 的直接写入保护生效，但暴露 Stop Hook 对非保证环境变量 `CODEX_HOME` 的错误依赖，以及未处理 `stop_hook_active` 的循环缺陷。
- 修复策略：Plugin 运行时优先使用 `PLUGIN_DATA`，保留 `CODEX_HOME` 兼容回退；Stop 已经继续过一次时不再阻断，只报告闭合警告。
- 自动化验证：Plugin 测试 `71/71` 通过，Plugin 结构校验与三个 Skill 校验均通过。
- 修复版已安装为 `0.1.0+codex.20260930115950`；安装缓存烟雾测试确认无 `CODEX_HOME` 时 UserPromptSubmit 与 Stop 均返回 `continue: true`，所有运行目录变量缺失且 `stop_hook_active=true` 时只输出警告并允许结束。
- Round 7S 已完成：PreToolUse 写保护、权威状态完整性和 Stop 闭合均通过，原 `CODEX_HOME_REQUIRED` 循环缺陷关闭。
- Round 7S 会话记录同时证明两次只读检查被误拒绝：组合 `Get-FileHash/Get-Content` 与单独 `Get-FileHash`。根因是当前 PreToolUse 只按命令文本是否包含权威路径拒绝，尚未区分只读与写入语义；该问题不推翻 Round 7S 的写保护与 Stop 结论，但应作为下一项独立缺陷处理。
- 只读误拦截修复：PreToolUse 先识别权威路径，再仅放行明确的结构化只读工具与受限 PowerShell 只读命令链；写命令、读写混合命令、嵌套脚本、重定向及未知命令继续默认拒绝。
- 自动化验证：Plugin 测试 `73/73` 通过。下一轮 Round 8 只验证 `Get-FileHash` / `Get-Content` 可读、`Set-Content` 仍被拒绝、权威状态与 Receipt 不变。
- 修复版已安装为 `0.1.0+codex.20260930143443`；安装缓存烟雾验证中 `Get-FileHash` 返回放行、`Set-Content` 返回拒绝，缓存 Hook 与测试源码 SHA-256 一致，模拟项目三份权威文件哈希未变化。
- Round 8 已通过人工重放：Hook 面板记录 `16` 次运行、`1` 次阻止、`0` 次失败；唯一阻止对应写入探针，两条只读命令均完成，Stop 未形成续写循环。独立哈希复核与 Round 6 基线一致。
- Round 8 后审计发现 Mod Workflow 仅有独立领域测试，尚未接入 `prepare_change / commit_change`，导致非法阶段跳转可穿透 Runtime。修复采用 Registry Workflow Adapter：阶段变化必须绑定 `workflow_transition`，准备与提交均由当前项目类型的 Evaluator 校验；Shared Kernel 不直接依赖 Mod。
- 自动化验证：非法 `M0 -> M4`、缺少转换描述和无效 `MODEL_REVIEW` 均在 Pending Request 创建前拒绝；合法 `M0 -> M1` 经 Maker Authorization、Receipt 与 Stop 完整闭合；Plugin 测试 `79/79` 通过。下一轮 Round 9 只重放非法跳级拒绝与状态不变。
- Workflow 修复版已安装为 `0.1.0+codex.20261001102149`；仓库外候选包成功加载 Registry Workflow Adapter，安装缓存对临时项目的 `M0 -> M4` 返回 `ILLEGAL_TRANSITION`，并保持 `revision=0`、`pending_requests=0`。
- Round 9 已通过人工重放：Runtime 恰好拒绝一次非法转换，未调用 `commit_change`；Stop 返回 `continue: true`。Hook 面板的阻止次数为 `0` 符合预期，因为本轮由 MCP Runtime 拒绝语义非法的受控请求，不属于 PreToolUse 的直接文件写入拦截职责。
- Round 9 后独立复核确认 Revision 为 `0`、阶段为 `M0_BOUNDARY / ACTIVE`、Pending Request 为 `0`，Receipt 仍为 `receipt-05769fe4-fc73-4133-8db8-7dae51f57932`；三份权威文件哈希与 Round 6 基线一致。
