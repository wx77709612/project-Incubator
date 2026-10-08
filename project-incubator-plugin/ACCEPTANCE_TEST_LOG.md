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
| 10A | 合法 `M0 -> M1` 变更准备 | FAIL | `prepare_change` 闭环正确并生成 Pending Request，但拟议状态仍将“精确版本待 Maker 提供”保留为 Active Decision，与已记录版本 `1.126.73.1030` 冲突；Runtime 也没有拒绝或撤回错误 Pending Request 的受控入口 | 不批准 Commit；补齐 Pending Request 拒绝路径和 Decision 授权绑定后重放 |
| 10A Cleanup | 错误 Pending Request 受控拒绝 | PASS | 加载 `0.1.0+codex.20261001212236`；`decline_change` 跨会话精确拒绝目标 Request；Revision `1 -> 2`、Pending `1 -> 0`，业务状态未应用，Receipt 为 `DECLINE_CHANGE` 且授权可验证 | 重放修正后的合法 `M0 -> M1` 变更准备 |
| 10A Replay | 修正后的合法 `M0 -> M1` 变更准备 | PASS | Revision `2 -> 3`、当前阶段仍为 M0、Pending `0 -> 1`；完整 Payload 已更新版本 Decision、Boundary、Gate、Risk 与 M1 Plan，未提前应用业务状态 | Maker 精确批准 Request 后执行 Round 10B Commit |
| 10B | 长授权 Prompt 提交 | FAIL | 唯一一次 `commit_change` 返回 `PROMPT_SCOPE_NOT_CONFIRMED`；Hook 只保存前 240 字符，Request ID 在 excerpt 内而 Digest 被截断；状态与 Receipt 未变化 | 使用短授权恢复当前 Request，并修复结构化授权证据 |
| 10B Retry | 短授权 Prompt 提交 | PASS | Revision `3 -> 4`、M0 进入 M1、Pending `1 -> 0`；变更 Decision 绑定新 Authorization，其他 Decision 保留旧 Authorization；Receipt 验证通过 | 修复长 Prompt 授权截断并独立重放 |
| 11A | M1 风险模型与 M2 变更准备 | FAIL | 新会话加载正确版本并恢复 Revision 4，但兼容格式 MCP 未继承 Hook 的 `PLUGIN_DATA`，启动时返回 `RUNTIME_DATA_ROOT_REQUIRED`；`prepare_change` 调用 0 次，权威状态未变 | 修复 Hook/MCP Runtime Data 同源解析后重放 Round 11A |
| 11A Replay | M1 风险模型与 M2 变更准备重放 | PASS | 加载 `0.1.0+codex.20261001224335`；Revision `4 -> 5`、当前阶段仍为 M1、Pending `0 -> 1`；八维风险模型总分 13，拟议 M2 Payload、Gate、E0 与 `UNSET / 0` 经独立回读一致 | 使用长授权 Prompt 提交该精确 Request，验证结构化授权不受 240 字符摘要限制 |
| 11B | 长授权 Prompt 宿主提交 | PASS | Revision `5 -> 6`、M1 进入 M2、Pending `1 -> 0`；完整 Prompt 中位于旧摘要边界后的唯一 Request/Digest 被识别，Receipt 绑定真实 Authorization；六项 Decision 授权未被改写 | 长 Prompt 授权与 Runtime Data 缺陷关闭；进入 M2 垂直切片方案验收 |
| 12A | M2 垂直切片方案设计 | PASS | 只读恢复 Revision 6；按加载、注入、触发、创建、投递建立可归因完整路径；三次人工验证分别绑定可区分假设且只作提议；Runtime Mutation 与文件修改均为 0 | Maker 确认候选机制、诊断边界、预算与隔离条件后准备受控变更 |
| 12B | M2 方案与预算变更准备 | PASS | Revision `6 -> 7`、阶段仍为 M2、Pending `0 -> 1`；拟议预算为 `3 / 0`，新增两个 Architecture Decision，M2 Gate、E0 与空 Baseline 未提前改变 | Maker 精确批准 Request 后提交 M2 方案与预算 |
| 12C | M2 方案与预算提交 | PASS | Revision `7 -> 8`、Pending `1 -> 0`、预算成为 `3 / 0`；预算 Decision 与两项 Architecture Decision 绑定本轮 Authorization，其余五项 Decision 授权未变 | 核心治理链验收完成；进入受限技术调查，尚不实施 Mod |
| 13A | M2 实现前只读技术调查 | PASS | 权威状态保持 Revision 8；本机路径、游戏与 Studio 版本、工具链及唯一冰箱 `fridgeLOW_01_set1`/`0x459B` 获得本地证据；Package-only 宿主语义仍保持未证明 | Plugin 人工验收可在实现前收口；继续将进入真实 Mod 工程 |
| Closeout | 发布候选收口 | PASS | Plugin `88/88`、Legacy `132+32+3` 全绿；最终审阅修复控制目录 basename 写入绕过；候选 `0.1.0+codex.20261002144305` 在仓库外安装并从全局缓存启动 | 等待选择本地合并、PR 或保留分支 |

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
- Round 10A 的 Runtime 机械闭环通过：Revision `0 -> 1`、阶段仍为 `M0_BOUNDARY`、Pending Request `0 -> 1`，Receipt operation 为 `PREPARE_CHANGE`，Stop 正常放行。
- Round 10A 的拟议内容验收失败：Boundary、Capability、Gate 与 Risk 已记录 Maker 提供的版本 `1.126.73.1030`，但 `decisions.active` 仍保留 `versions-maker-supplied` 的“精确游戏版本和补丁版本待 Maker 提供”陈述。若直接提交，权威状态将产生 Active Decision 与目标环境事实冲突。
- 恢复路径缺口：当前 MCP 仅提供 `prepare_change` 与 `commit_change`，没有受控的 `decline_change` 或 `withdraw_change`；错误 Pending Request 无法在不直接写权威文件的前提下正式作废。Round 10B 暂停，且不得批准或提交 `request-1003e089-b892-4a0d-bd00-8674e3296735`。
- Round 10A 修复已实现：新增可跨 Agent 会话恢复的 `decline_change`，要求同一项目、精确 Request/Digest 与 Maker 明确拒绝；拒绝只移除目标 Pending Request，不应用拟议业务状态，并生成授权 Receipt。
- Decision Mutation 修复已实现：`commit_change` 自动将新增或内容变化的 Decision 绑定本次真实 Authorization 与确认时间，未变化的 Decision 保留原授权。测试先分别因 `TOOL_NOT_FOUND` 与旧授权残留失败，修复后完整 Plugin 套件 `82/82` 通过。
- 当前 Codex 安装中的旧 `plugin-creator/validate_plugin.py` 已不存在；`skill-creator/quick_validate.py` 在系统 Python 与 bundled Python 中均因缺少 PyYAML 无法启动。本轮不将验证器环境错误表述为 Skill 失败，继续使用完整测试、Manifest 解析、候选包和安装缓存烟雾测试验证。
- 修复候选已打包并安装为 `0.1.0+codex.20261001212236`。仓库外候选与全局安装缓存均成功启动 Kernel，返回 `ROUTE_PROPOSED`，且 `decline_change` 已实际注册；安装缓存中的 `server.mjs`、`authorization.mjs` 与 `mod-incubator/SKILL.md` 哈希和源码一致。
- Round 10A Cleanup 已通过人工重放与独立回读：Revision 为 `2`、阶段仍为 `M0_BOUNDARY / ACTIVE`、Pending Request 为 `0`，Receipt 为 `receipt-9146dd5e-f3d1-415d-8577-f79b341460e2` 且 operation 为 `DECLINE_CHANGE`。Boundary 未出现版本 `1.126.73.1030`，Active Decision 仍保留清理前原值，证明被拒绝 Request 的拟议业务状态未泄漏。
- Round 10A Replay 已通过：Request `request-98d771b6-c3cb-41f4-bf7a-698aa615bdf3` 的 Payload 经独立回读，版本、安装边界、修正后的 Decision、M0 Gate、风险集合与 M1 Plan 一致；准备后仅控制状态发生变化。
- Round 10B 首次提交安全失败：完整 Prompt 哈希存在，但授权检查只读取 240 字符 `excerpt`，导致位于截断边界后的 Scope Digest 不可见。Revision、M0 阶段、Pending Request 与 PREPARE_CHANGE Receipt 均保持不变。
- Round 10B Retry 使用令牌前置的短 Prompt 成功提交。独立回读确认 Revision `4`、阶段 `M1_RISK_MODEL / ACTIVE`、Pending `0`、Receipt `receipt-f725bc5c-381e-4f1c-a6de-4fb41cb73550`；变更 Decision 的授权等于 Receipt Authorization，其余五项 Decision 保留原授权，Evidence 为 `E0`，人工预算仍为 `UNSET / 0`。
- 长 Prompt 授权修复已实现：Prompt Record 继续仅保存完整哈希、240 字符 excerpt 与有界结构化 Claim；Claim 从完整 Prompt 提取唯一 Request ID、唯一 Scope Digest 和明确意图。歧义意图或多令牌不形成可用授权，旧记录继续使用 excerpt 回退。失败测试先复现 `PROMPT_SCOPE_NOT_CONFIRMED`，修复后完整 Plugin 套件 `86/86` 通过。
- 修复版已打包并安装为 `0.1.0+codex.20261001222139`。安装缓存中 `prompt-events.mjs` 与 `authorization.mjs` 的 SHA-256 均与源码一致；直接从安装缓存重放 457 字符 Prompt，授权令牌位于 240 字符 excerpt 之后仍成功授权，且未持久化完整 Prompt。尚差一次新 Codex 会话的 Hook + MCP 宿主重放。
- Round 11A 未进入业务变更：失败发生在 MCP 创建 Kernel Service 之前，因此无 Request、无 Pending、无 Receipt 和 Revision 变化。根因是兼容格式插件的 Hook 获得 `PLUGIN_DATA`，但本地 stdio MCP 配置显示 `env=null` 且 `env_vars=[]`；运行时将改为从 Codex 安装缓存结构推导同一 `plugins/data/<plugin>-<marketplace>/runtime-events` 目录，无法验证结构时仍 fail closed。
- Runtime Data 修复版已打包并安装为 `0.1.0+codex.20261001224335`。完整 Plugin 套件 `87/87` 通过；安装缓存在 `PLUGIN_DATA` 与 `CODEX_HOME` 均缺失时，正确解析到 `C:\Users\Xenia_Woo\.codex\plugins\data\project-incubator-plugin-personal\runtime-events`，Kernel Service 启动并成功执行只读 `inspect_project`。尚待新 Codex 会话重放 Round 11A。
- Round 11A Replay 已通过人工重放与独立回读：唯一 Pending Request 为 `request-f3d1b9e5-2681-4346-a2e9-da4852bf3baf`，Scope Digest 为 `41761c9bdf381524a20261d8382799418288db9c02737ca6d7dd0ec1854819b5`；权威阶段仍为 `M1_RISK_MODEL / ACTIVE`，拟议状态才进入 M2，Revision 为 `5`，Receipt operation 为 `PREPARE_CHANGE`。拟议八维风险模型、M1/M2 Gate、E0、空 Baseline 与 `UNSET / 0` 均与报告一致，未夹带实验、API 选择或实现。
- Round 11B 已通过人工重放与独立回读：Revision 为 `6`，阶段为 `M2_VERTICAL_SLICE / ACTIVE`，Pending Request 已清空；Receipt `receipt-99dc6fba-0776-41e3-8647-55061c47ab74` 的 operation 为 `ADVANCE_MOD_STAGE`，Authorization 精确绑定本轮 Request 与完整 Prompt digest。六项既有 Decision 的 statement、授权和确认时间均未改变，M1 Gate 为 `PASSED`、M2 Gate 为 `PENDING`，Evidence 仍为 `E0`，Baseline 为空，人工预算仍为 `UNSET / 0`。长 Prompt 结构化授权与 Hook/MCP Runtime Data 同源缺陷至此关闭。
- Round 12A 已通过方案验收与状态复核：权威状态保持 Revision `6`、`M2_VERTICAL_SLICE / ACTIVE`、Pending `0`、Evidence `E0`、Baseline 空、人工预算 `UNSET / 0`。方案没有选择具体 API，也没有实施或写入状态；它把 Package 加载、互动注入/显示、玩家触发、食物创建和正确投递拆成可关联的诊断阶段，并将三次人工验证分别绑定加载/显示、完整路径、执行者绑定与重复性假设。预算仍明确等待 Maker 决定。
- Round 12B 已通过准备闭环与 Pending Payload 复核：唯一 Request 为 `request-d40c05b4-17aa-4b8c-b92c-f194ae58ae67`，Scope Digest 为 `64a99a29c291c51f2ca1d6470a4efd63d5954110a442144b09fec80d3f3c71be`；Revision 为 `7`，权威阶段仍为 M2，当前预算仍为 `UNSET / 0`。拟议状态才将预算设为 `3 / 0`，新增 Package-only additive 与诊断/隔离/MODEL_REVIEW 两项 Architecture Decision；其余五项 Decision 保留原授权，Evidence、M2 Gate 与 Baseline 均未提前改变。
- Round 12C 已通过提交闭环与独立回读：Revision 为 `8`，阶段仍为 `M2_VERTICAL_SLICE / ACTIVE`，Pending 已清空，预算为 `3 / 0`。Receipt `receipt-6294053e-2273-440f-afe7-7d4e1ea20b1b` 精确绑定本轮 Request 与 Authorization；修改后的预算 Decision 和两项新增 Architecture Decision 均绑定该 Authorization，其余五项 Decision 的 statement、授权与确认时间未变化。Capability 仍为 `E0 / HYPOTHESIZED / LOW`，M2 Gate 仍为 `PENDING`，Baseline 为空，未开始实现或消耗人工验证。
- Round 13A 已通过调查边界与本地证据抽查：权威状态仍为 Revision `8`、M2、Pending `0`、预算 `3 / 0`、Evidence `E0`。游戏、用户数据、Mods、基础模拟资源、Sims 4 Studio 与资源索引路径均实际存在；程序版本为 `1.126.73.1030`，Studio 产品版本为 `3.2.6.4+5d11d0e5c2e9a9f09a1ad7503a6ab2816c4abf94`。资源索引只读查询确认 `fridgeLOW_01_set1` 的 Instance 为 `17819`（`0x459B`）、GameId `1`、PackID `0`、价格 `375`，并存在对应 COBJ/OBJD 类型记录。Agent 没有将这些可用性证据提升为完整宿主语义，也没有修改文件、状态或消耗人工测试。

## 最终收口

- 自动化：Node `88/88`；Legacy unit `132/132`、integration `32/32`、e2e `3/3`。
- 最终审阅：发现并以 RED→GREEN 测试修复控制目录内使用 `state.json` 等 basename 绕过 PreToolUse 的问题；修复后相对 Shell 写入和结构化写入均拒绝，只读 basename 继续放行。
- 候选包：`0.1.0+codex.20261002144305`；白名单内容、9 个 JSON、三份 Skill 等价结构检查、禁用研发绝对路径扫描均通过，生产依赖安装 `95` 个包且审计 `0` 漏洞。
- 独立运行：候选已写入个人 Plugin 源与版本化 Codex 缓存；从安装缓存启动 Router、`inspect_project` 和 Hook，恢复 Revision `8`、Receipt 验证通过、只读放行、直接写入拒绝，关键文件哈希与源码一致。
- 验证工具限制：官方 `quick_validate.py` 在系统与 Codex bundled Python 中都因缺少 `PyYAML` 无法启动；已按该脚本实际规则执行等价 frontmatter、命名、字段和 TODO 检查，三份 Skill 均通过。
- 人工验收边界：模拟项目停在 `M2_VERTICAL_SLICE / ACTIVE`，未把技术调查升级为宿主语义证据；继续推进属于真实 Mod 工程，不属于本 Plugin MVP 收口。

## Desktop Product 0.2.0 自动验收 — 2026-10-07

| Stage | 结果 | 关键证据 | 下一步 |
| --- | --- | --- | --- |
| A–E Registry / Entry / Workflow / Activation / Skill | PASS | 对应测试进入 Plugin 全量；Desktop 显式 Host、NEW/ADOPT Entry、P0–P6、完整 Scope 摘要重验、Entry 不可变、D06、P4 Correction 与 Browser 不越界均通过 | 全量回归 |
| F Plugin Regression | PASS | `npm test`：`132/132`，0 failures；原有 88 项继续在同一套件内执行 | Legacy 回归 |
| F Legacy Regression | PASS | unit `132/132`、integration `32/32`、e2e `3/3` | Candidate Package |
| G Candidate Package | PASS | Manifest `0.2.0+codex.20261008084456`；Package `0.2.0`；安装 94 个生产依赖；必需 Skills/Profiles/Workflow 均存在，`SPECS`、tests、Legacy Runtime 与旧归档未进入包 | 人工行为验收 |
| G Repository-external Smoke | PASS | 从系统临时目录加载 Registry 的 `mod` 与 `desktop-product`，两个 Entry evaluator 均返回 `WORKFLOW_ENTRY_ALLOWED`，Desktop Route 返回 `desktop-product-incubator + windows-desktop`，Kernel package version 为 `0.2.0` | 清理临时候选 |
| Whole-branch Review Remediation | PASS / FINAL RE-REVIEW PENDING | 首轮 1 个 Important 与 4 个 Minor 已关闭；第二轮新增 `Entry = null` Minor 已以 RED→GREEN 工具级测试修复 | 对最终新 HEAD 复审 |
| Protected Mod/Sims Assets | PASS | SHA-256：Mod Skill `304a789b...5017`、Sims Skill `b159ded0...bc4a`、Mod Profile `a959016c...f83a`、Sims Profile `f47f1292...0bf` | 保持冻结 |
| Skill Validator | BLOCKED（工具环境） | 系统与 Codex bundled Python 均缺少 `PyYAML`，`quick_validate.py` 无法启动；未向仓库安装依赖；等价结构约束由 Contract Test 覆盖 | 有 PyYAML 环境时补跑官方校验器 |
| Manual M1–M6 | PENDING | 当前串行实现会话没有独立行为测试 Agent；静态文本匹配不能证明真实触发、停下与升级行为 | 用安装候选执行六轮并保存答复、Tool、Result Code 与状态变化 |

自动化与 Candidate Smoke 不能证明未来 Managed Desktop Product 的安装器、权限、签名、升级、卸载、安全软件交互或业务能力。浏览器自动化本轮未运行，因为 Browser Extension Project Type 尚未实现；本轮只证明它不会被错误路由到 Desktop Child。
