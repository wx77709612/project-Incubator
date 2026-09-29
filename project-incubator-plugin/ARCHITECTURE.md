# Project Incubator Plugin 架构契约

状态：`APPROVED`（Maker 于 2026-09-29 确认；Pending Activation Bootstrap 修正于同日确认）

## 1. 目标

构建一个可全局安装的 Project Incubator Plugin。它不再用一个大而全的 Skill 管理所有项目，而是由三层协作：

```text
Router Skill
    -> 选择并锁定项目类型
Shared Enforcement Kernel
    -> 管理权威状态、授权、Receipt 与强制边界
Child Incubator Skill + Host Profile
    -> 提供项目类型和目标宿主的领域流程
```

首个可交付组合是：

```text
Mod Incubator Skill + Sims 4 Host Profile
```

现有 `PROJECT_INCUBATOR/`、V1.1 RC 与历史规格保持原样，作为 Legacy Baseline、迁移输入和回归对照。新 Plugin 必须通过第 13 节的集成矩阵说明旧资产被保留、适配或专门化到哪里；不得以“重新实现”为由无证据丢弃既有治理语义。

## 2. 明确不做

- 不把 P0-P6 完整迁移到 Mod 流程。
- 不让 Router 自动替 Maker 决定项目类型。
- 不依靠 Markdown 约束权威状态变更。
- 不为每次 Skill 迭代生成 Architecture、Design、Contract、Runtime Spec 等多套重复文档。
- 不要求每个 Managed Project 默认维护大量人读文档。
- 不让全局 Hook 在未激活项目中捕获 Prompt 或阻止工具。

## 3. 组件与权威

| 组件 | 职责 | 不得承担 |
| --- | --- | --- |
| Router Skill | 提议项目类型、解释选择依据、请求 Maker 确认 | 自动确认项目类型或修改权威状态 |
| Enforcement Kernel / MCP | 初始化项目、读取与提交状态、校验授权、生成和验证 Receipt | 创造产品方案或替 Maker 决策 |
| Shared Hooks | 捕获有效授权、阻止绕过 Kernel、阻止未闭合任务结束 | 定义领域流程或推断授权 |
| Child Incubator Skill | 定义该项目类型的阶段、产物、风险与下一步 | 绕过 Kernel 或改变其他子 Skill |
| Host Profile | 描述具体宿主的安装、打包、运行证据和兼容边界 | 成为独立项目类型或替代 Mod Skill |

## 4. 项目激活与 Hook 作用域

插件可以全局安装，Hook 信任按当前定义哈希在本机持久化。每个项目是否受管理，由项目根目录中的激活记录决定：

```text
.project-incubator/activation.json
```

正常管理逻辑只有满足以下全部条件时才执行：

1. 当前工作目录位于该项目根目录内；
2. `activation.json` 结构合法；
3. `status` 为 `ACTIVE`；
4. `plugin_id` 与当前插件一致。

首次激活采用唯一的受限例外 `Pending Activation Bootstrap`：

1. `prepare_activation` 只能在 Plugin Runtime Data 中建立绑定项目规范路径、随机 `request_id`、`scope_digest` 与失效时间的短期候选请求；
2. 它不得创建 `.project-incubator/`、不得修改项目文件，也不构成已激活状态；
3. `UserPromptSubmit` 在未激活项目中只可查询是否存在与当前项目规范路径严格匹配的有效候选请求；没有候选请求时必须零副作用放行；
4. 存在候选请求时，只捕获下一轮对应 Maker Prompt，用于校验当前 request、scope、project、session 与 turn；
5. 明确批准后 Kernel 才原子创建三个权威文件；批准、拒绝、消费或超过 24 小时后，候选请求与 Prompt 临时记录立即删除；
6. Bootstrap Runtime Data 不是第四份项目状态，不能用于恢复项目、推进 Workflow 或覆盖三个权威文件。

除已激活项目和上述有效 Bootstrap 候选外，所有 Hooks 必须直接返回 `continue`，不得保存 Prompt、修改文件或阻止任务。

插件更新导致 Hook 定义哈希变化时，需要重新审查信任；新增普通项目或任务不需要重新审查。

## 5. Managed Project 权威状态

首个版本只使用三个机器可读文件：

```text
.project-incubator/
├── activation.json
├── state.json
└── latest-receipt.json
```

- `activation.json`：项目身份、项目类型、Host Profile、插件版本和激活状态。
- `state.json`：唯一权威项目状态，包含恢复当前项目所需的完整语义。
- `latest-receipt.json`：最近一次已验证变更的闭合证据。

`state.json` 至少必须表达：

- 当前项目目标、支持边界与排除边界；
- 当前 Child Skill 阶段、阶段状态和合法下一步；
- 当前 Capability Claim、Evidence 等级与证据引用；
- Active Maker Decision、Runtime Assumption 与待决请求；
- 当前行动、完成条件、Gate、阻塞和风险；
- Known-Good Baseline 与人工验证预算；
- 最近一次有效状态变化和历史归档引用。

设计正文、测试日志、代码和大型 Evidence 不复制进 `state.json`，只保存当前结论、适用范围和稳定引用。活动状态必须有大小与条目上限；失效或过期历史进入有界归档或由版本控制保存，不能让活动状态无限增长。

旧 Core Context 的语义职责继续保留，但不要求按 `PROJECT_PROFILE.md`、`PROJECT_STATE.md`、`PROJECT_PLAN.md`、`PROJECT_DECISIONS.md` 四个物理文件重复维护。对应信息必须在 `state.json` 中保持逻辑分区和独立权限，不得因为合并存储而混淆 Profile、State、Plan 和 Decision 的权威边界。

Markdown 只能由 Kernel 按需生成只读 Projection，不是 Source of Truth，也不能作为阶段推进依据。MVP 不默认生成或持续维护 Projection。

### 5.1 项目状态摘要能力

Plugin 必须提供 `inspect_project` 只读能力，作为 Maker 查询项目现状的标准入口。它不是一段依赖聊天记忆的自由 Prompt，而是 Skill Trigger、Kernel 查询与固定响应契约的组合。

当 Maker 询问“当前项目状态”“做到哪里了”“下一步做什么”“有什么阻塞”“需要我决定什么”或语义等价问题时：

```text
Child / Router Skill 识别状态查询意图
-> 强制调用 inspect_project
-> Kernel 读取并校验 activation.json、state.json 与 latest-receipt.json
-> 返回绑定 project_id、revision 和 receipt 状态的结构化摘要
-> Agent 使用简体中文解释，不修改项目状态
```

默认摘要固定包含：

1. 当前项目目标与支持边界；
2. 当前项目类型、Host Profile、阶段和阶段状态；
3. 最近完成事项及其证据上限；
4. 当前行动、下一步行动与完成条件；
5. 阻塞、风险和待 Maker 决策事项；
6. Capability Evidence、Known-Good Baseline 与人工验证预算摘要；
7. 最近一次已验证变更、revision 和 Receipt 状态。

摘要规则保存在共享 Skill 指令和 MCP Tool Contract 中，不依赖 Agent 自行记忆，也不要求 Managed Project 维护重复 Prompt。若权威状态损坏、版本不支持或 Receipt 与状态不一致，`inspect_project` 必须明确报告不可验证，不得根据聊天记录补全或猜测。

`PROJECT_OVERVIEW.md` 仅在 Maker 明确要求导出时由同一摘要结果生成。它是可重建的人读视图，不是持续维护的 Core Context。

## 6. 状态与 Receipt 规则

Kernel 对任何状态变更执行：

```text
读取并校验当前状态
-> 检查 expected_revision
-> 检查操作权限和 Maker Authorization
-> 在内存中形成 next_state
-> 原子写入 state.json
-> 回读并校验内容哈希
-> 写入 latest-receipt.json
-> 回读并验证 Receipt
```

必须 fail closed：

- JSON 无法解析、字段缺失、revision 非非负整数或 schema/version 不支持时拒绝提交；
- 不得把损坏状态当作空状态或自动修复；
- 不得产生 `null`、`NaN` 或无法递增的 revision；
- Receipt 必须绑定前后状态哈希、revision、操作、项目 ID 和授权引用；
- Receipt 校验必须同时验证 Receipt、当前状态哈希和 revision，不能只比较 ID。

## 7. Maker Authorization

需要 Maker 权限的操作采用两步协议：

```text
prepare_change
-> 返回 request_id、scope_digest、变更摘要和明确确认问题
Maker 回复
-> UserPromptSubmit 在激活项目中，或仅对路径严格匹配的 Pending Activation Bootstrap，保存本轮原始 Prompt 与哈希
commit_change
-> 校验 request_id、scope_digest、Prompt 来源、明确批准语义和时效
```

以下操作必须获得 Maker Authorization：

- 激活或停用 Project Incubator；
- 确认或迁移项目类型；
- 改变 Product Boundary；
- 确认 Architecture Decision；
- 启用高成本目标环境验证；
- 超出 Maker 已设测试预算；
- 撤销或替代 Maker Decision。

Runtime Assumption 被证据判定失效不等于修改 Maker Decision，但若影响产品边界或架构，必须形成新的授权请求。

## 8. Router 与 Child Skill 契约

Router 只能产生 `ROUTE_PROPOSED`，Maker 确认后 Kernel 才写入 `project_type_id`。首版支持：

```text
project_type_id = "mod"
child_skill_id = "mod-incubator"
host_profile_id = "sims-4" | null
```

每个 Child Skill 必须声明：

- 适用与排除条件；
- 专用阶段和合法转换；
- 需要 Maker 确认的操作；
- Capability、Evidence 与 Baseline 规则；
- 可用 Host Profile 接口；
- Closure 条件；
- 自动测试和目标环境验证边界。

Host Profile 只能收紧或具体化 Child Skill，不能放宽 Kernel 权限规则。

## 9. Mod Incubator 流程

Mod 项目不复刻 P0-P6，采用六个领域阶段：

| 阶段 | 目标 | 最小退出条件 |
| --- | --- | --- |
| `M0_BOUNDARY` | 明确玩家价值、宿主、Mod 类型和不支持范围 | Maker 确认 Product Point 与 Host |
| `M1_RISK_MODEL` | 识别不透明 Capability、候选模型和验证成本 | 风险有证据、未知项未伪装为事实 |
| `M2_VERTICAL_SLICE` | 完成一个代表性生命周期 Discovery Slice | 目标宿主完整路径可观察，候选模型可被推翻 |
| `M3_BUILD_PACKAGE` | 按已支持模型实现并验证最终包 | 构建、包内容、安装结构和本地回归通过 |
| `M4_TARGET_VALIDATION` | 在真实宿主验证 Capability Claim | 目标环境结果、失败和副作用有证据 |
| `M5_EXPAND_RELEASE` | 沿一个风险维度扩展或形成发布边界 | 新边界闭合，或明确保留在后续 Ring |

在 `M2`、`M3`、`M4` 中发现模型失效时进入轻量 `MODEL_REVIEW` 子流程：

```text
标记失效 Assumption
-> 暂停同方向补丁
-> 更新 Candidate Model 和受影响边界
-> 重放相关自动验证
-> 决定恢复当前阶段或请求 Maker 改变产品/架构边界
```

它不是返回旧阶段，也不是进入“已完成功能后的迭代”。

## 10. 不透明性与垂直切片

不透明性按 Capability 评估，不给整个项目永久贴标签。八个维度分别取 `0/1/2`：契约、隐藏状态、控制权、确定性、可观察性、可自动化性、可归因性、版本稳定性。

- 任一维度为 `2`：建议启用代表性 Vertical Slice；
- 至少两个维度为 `1`：建议启用；
- 未知维度按 `1` 处理，但必须显示为未知；
- Maker 可接受风险后不启用，但 Kernel 必须缩小 Capability Claim。

具体 Slice 不写死“安装、UI、存档”等固定清单，而由以下四项生成：

```text
Capability Claim
+ 完整生命周期
+ 当前最高风险边界
+ Host Profile 的可观察与交付要求
```

## 11. Evidence 与人工验证成本

Evidence 采用通用 `E0-E5`：推测、契约/源码、隔离实验、单一宿主完整路径、代表性边界、长期/兼容证据。

- API 存在只证明 Availability，不证明 Semantic Capability；
- 自动化验证不能替代目标宿主语义；
- 一次目标环境成功最高只能支持 `E3`；
- Confidence 可以降低；
- Known-Good Baseline 必须绑定 Capability、边界、环境版本和 Evidence。

人工测试预算不由 Agent 猜测固定数字。Agent 只能提出测试批次、预期区分的假设和成本；Maker 决定上限。没有 Maker 设置时，状态记录为 `UNSET`，不得伪造“最多 N 次”。

## 12. Sims 4 Host Profile 边界

首版 Profile 负责提供：

- 游戏与补丁版本记录；
- Script Mod / Package Mod 类型；
- 构建产物、压缩包和 Mods 目录安装检查；
- Python/资源加载、日志、异常与 UI/交互观察入口；
- 进程会话、存档、家庭/世界、版本兼容等可选风险维度；
- Maker 执行真实游戏验证时的结构化回传格式。

Profile 不预设每个 Mod 都需要 UI、交互、存档或跨版本测试；这些由 Capability Claim 和风险评估决定。

## 13. Legacy Baseline 集成矩阵

旧资产使用以下处置类型：

- `PRESERVE`：语义和约束保持不变，进入 Shared Kernel；
- `ADAPT`：保留目的，改变物理存储或执行机制；
- `SPECIALIZE`：进入特定 Child Skill 或 Host Profile；
- `REFERENCE`：留在旧包中作为历史证据和未来子孵化器输入，不进入默认运行上下文。

| Legacy 资产或约束 | 处置 | 新 Plugin 落点 | 可观察效果 |
| --- | --- | --- | --- |
| Maker 是 Product / Architecture Decision 的最终权威 | `PRESERVE` | Kernel Authorization Contract | 未绑定当前 Pending Request 的 Maker Prompt 不能提交受控变更 |
| Runtime 是受控 Context Mutation 的唯一执行者 | `PRESERVE` | MCP Kernel + `PreToolUse` Hook | 普通编辑、Patch 或 Shell 不能直接改权威状态 |
| 原子写入、回读、快照恢复与回滚 | `PRESERVE` | Kernel State Transaction | 写入或闭合失败不留下可被宣称为成功的半完成状态 |
| Mutation Set 的预检、授权、提交和 Closure 思想 | `ADAPT` | 单一 `state.json` 事务 + Receipt | 一次语义事件不再要求 Agent 同步修改多份 Markdown |
| `PROJECT_STATE.md` 唯一状态源原则 | `ADAPT` | revisioned `state.json` | 恢复项目只读取一个机器权威状态，不从聊天或计划猜测 |
| Profile、State、Plan、Decision 四类职责 | `ADAPT` | `state.json` 独立逻辑分区与字段权限 | 保留语义边界，但不默认生成四个物理文件 |
| Decision、Runtime Assumption、Observation、Hypothesis 分离 | `PRESERVE` | Shared State Schema + Policy | Evidence 可推翻 Assumption，但不能伪造 Maker Decision |
| Evidence `E0-E5` 与 Claim Scope | `PRESERVE` | Shared Evidence Policy | API 存在、单元测试和目标环境成功不会被混为同一种证明 |
| Opaque Capability 与 Product Point Spiral | `SPECIALIZE` | Shared 可选 Policy + Mod Incubator | 只对满足风险条件的 Capability 启用垂直切片和真实宿主验证 |
| P4 Creation Correction | `SPECIALIZE` | Mod `MODEL_REVIEW` 子流程 | 实现中模型失效可就地纠偏，不伪装成已完成功能后的 Iteration |
| Known-Good Baseline 与 Confidence 可下降 | `PRESERVE` | Capability State + Gate Policy | 高风险修改前可定位回归基线，反例可以降低结论强度 |
| P0-P6 通用 Workflow | `REFERENCE` | Legacy Baseline / 未来 Child Skill 输入 | Mod 不被迫复刻通用阶段，其他类型可选择性吸收适合部分 |
| Sims 4 安装、打包、日志、生命周期与版本经验 | `SPECIALIZE` | Sims 4 Host Profile | 仅路由到 Sims 4 的 Mod 项目加载这些规则 |
| V1.1 模板、规格与人工验收案例 | `REFERENCE` | Legacy Test Corpus | 用于提取回归测试和未来子 Skill 规则，不复制到 Managed Project |

新 Plugin 的实现必须为每个 `PRESERVE` 与 `ADAPT` 项提供自动化测试；`SPECIALIZE` 项必须在对应 Child Skill 或 Host Profile 的验收中出现。`REFERENCE` 项不得被删除或改写，也不得在普通任务中默认加载。

Spike 仅作为宿主能力证据：

- Plugin 可以同时提供 Skills、MCP 和 Hooks；
- `PreToolUse` 可以阻止直接写入；
- `Stop` 可以阻止缺少 Receipt 的结束；
- `UserPromptSubmit` 可以保存原始 Maker Prompt；
- Spike 的宽松状态解析和仅按 ID 验证 Receipt 不得进入正式实现。

## 14. 首版验收边界

MVP 只有在以下事实均被自动测试和一次宿主走查证明后才完成：

1. 未激活项目不捕获 Prompt、不阻止工具；
2. 激活项目无法用普通工具写权威状态；
3. 损坏状态导致 Kernel 拒绝提交；
4. Maker 授权不能由 Agent 伪造或从旧消息复用；
5. Router 未经 Maker 确认不能锁定项目类型；
6. Mod 六阶段及 `MODEL_REVIEW` 的非法转换被拒绝；
7. Sims 4 Profile 只细化 Mod 流程，不改变 Kernel 权限；
8. 状态变更后缺少有效 Receipt 时任务不能结束；
9. `inspect_project` 只能从已校验的当前权威状态生成固定结构摘要，不从聊天记忆补全；
10. 按需导出的 `PROJECT_OVERVIEW.md` 不影响 Gate、Transition 或权威状态；
11. 集成矩阵中的 `PRESERVE`、`ADAPT` 与 `SPECIALIZE` 项均有对应测试；
12. 现有 RC.2 测试保持通过。
