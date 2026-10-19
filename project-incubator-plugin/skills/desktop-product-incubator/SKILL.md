---
name: desktop-product-incubator
description: Use when：Project Incubator Router 已确认 Managed Project 的项目类型为 desktop-product，需要按 P0–P6 孵化、恢复或推进桌面产品；不适用于浏览器扩展或未完成路由确认的项目。
---

# Desktop Product Incubator

## 当前 Kernel 权威与恢复

Plugin Router `project-incubator-router` 是唯一现行入口。权威集合为 `.project-incubator/activation.json`、`.project-incubator/state.json` 和 `.project-incubator/latest-receipt.json`；State 是唯一业务状态，Activation 约束身份/路由，Receipt 证明闭合。临时 Runtime Data 和 Markdown Artifact 不替代它们。

恢复与状态查询先调用 `inspect_project`，验证失败时报告稳定错误并停止受影响推进，不从聊天补全。只使用已验证路由的 Child Skill/Host Profile；不得直接编辑权威文件。所有受控变更经现行 Kernel，提交后确认 revision、回读与 Receipt 一致再报告完成。缺少 Plugin/MCP 时停止，不调用旧执行资产。


## 启动条件

仅在 Router 已选择 `desktop-product`、Maker 已确认匹配 Host，且 Runtime 返回有效激活状态后使用。当前可用 Host 为 `windows-desktop`，但它不是默认值；缺少匹配 Host 时停止激活。

本 Skill 辅助单一桌面产品形态。浏览器扩展是后续独立 Project Type 的设计范围，本 Skill 不把它作为桌面 Delivery Surface 接管，也不决定多个 Managed Project 如何组合。网站、远端 API、游戏客户端或内容生态属于具体项目的 External Dependency 或 Domain Constraint，不是桌面 Host。

恢复项目时先调用 `inspect_project`，只从已验证的 Activation、Project State 与 Receipt 判断当前状态。不得根据聊天记忆补写状态。

## Workflow Entry

- `NEW_PROJECT`：正式入口只能是 P0，记录 `initial_stage = P0`。
- `ADOPT_EXISTING`：Agent 检查现有设计、计划、Artifact、实现和 Evidence，判断 P0–P6 中的正常阶段；至少提供一个 `evidence_refs`，并写出有界 `assessment_summary`。
- Maker 确认 Entry Mode、Project Type、Host、Product Boundary 与完整激活范围。Agent 对 Evidence 支持下的阶段判断负责，Kernel 只校验结构和阶段集合。
- Entry 激活后不可修改。发现入口判断有误时，不直接改写 `workflow.entry`，而是报告证据与需要的受控处置。

## 正式阶段

阶段 ID 与名称保持 Project Incubator 的统一语义；Desktop System Model 等术语只作为阶段内说明或检查点，不成为新阶段。

### P0 `Intent Discovery`

明确用户问题、期望结果、成功标准，以及为什么桌面产品是必要载体。区分已观察事实、可推翻假设和 Maker Product Decision。

可观察出口：Maker 已确认 Intent、核心结果、主要排除项与桌面载体理由。

### P1 `Project Definition`

形成桌面产品边界：目标用户、核心旅程、能力范围、数据边界、外部依赖、支持环境与发布约束。不得因为“桌面软件通常具有某能力”而擅自加入自动更新、后台服务、登录或系统级集成。

可观察出口：目标、支持/排除范围、成功标准和高风险 Product Decision 已明确。

### P2 `Solution Design`

定义 Desktop System Model：进程与组件边界、数据流、持久化、外部依赖、权限边界、安装/升级/恢复策略以及可观察性。

对高不确定或高代价路径使用阶段内 `FEASIBILITY_PROBE`。Probe 必须写明要区分的假设、最小实验、停止条件、Evidence 上限和对 Design 的影响；它不是额外 Phase，也不自动授权扩大 Product Boundary。

可观察出口：关键 Architecture Assumption 有验证或降级路径；主要安全边界、失败模式与技术路线可解释。

### P3 `Execution Planning`

把设计转为可执行的 Usable Slice、依赖顺序、验证通道和交付计划。首个 Slice 应覆盖一个端到端用户结果，不以搭建所有基础设施为目标。

可观察出口：任务、依赖、完成条件、回滚/停止点、自动化与目标 Host 验证计划均可执行。

### P4 `Creation`

按计划创建 Project Artifact，持续校验 `Desktop System Model` 一致性，并在适用处完成两个桌面检查点。

`Desktop System Model` 一致性约束：实现仍符合 P2 确认的进程、数据、权限与外部依赖边界；发现偏离时不得把它误报为检查点已完成。

两个桌面检查点：

- `Usable Slice`：至少一个核心用户旅程端到端可观察；
- `Delivery Hardening`：打包、安装、升级、卸载、恢复和安全约束按当前范围落实或明确标为不适用。

若反例推翻局部模型，进入 P4 内部 `Creation Correction`：记录失效 Assumption，暂停同方向补丁，界定影响，修正设计/计划/实现并重放验证。Stage 保持 P4，不创建 `workflow_transition`。若影响 Product Boundary、Architecture Decision、Host 支持或 Runtime Invariant，提出 Maker Scope Review Requirement。

可观察出口：计划内 Artifact、模型一致性约束与两个检查点均有结论，已知反例和残余风险没有被隐藏。

### P5 `Validation`

按声明选择验证通道：

- `LOGIC_AUTOMATION` 证明确定性规则、解析、状态转换和失败恢复；
- Desktop Automation 证明指定桌面会话中的窗口、控件、进程和用户路径；
- `TARGET_HOST_VALIDATION` 绑定具体构建、Host 版本、架构、安装范围、权限模式和外部依赖，证明该环境中的观察结果。

逻辑自动化不能单独证明真实 Windows 会话、安装器、权限或安全软件行为。一次目标 Host 成功不能外推到未测试环境。

可观察出口：Validation Result 绑定 Claim、Artifact、环境、步骤、观察结果、失败与副作用；结论不超过 Evidence。

### P6 `Iteration`

根据完整 Validation Result 选择合法返回点：系统模型或 Architecture Assumption 调整到 P2；执行路线或验证计划调整到 P3；Artifact 调整到 P4；同一边界内补充验证到 P5。

若结果推翻 P0 Intent 或 P1 Project Definition，不能发明 P6→P0/P1 Transition，必须提出 Maker Review，由 Maker 决定是否重开边界、迁移或终止。

可观察出口：迭代理由、目标阶段、范围和授权要求清楚，且已走合法 P6→P2/P3/P4/P5 转换。

## Maker Authority

以下内容必须形成明确 Maker Authorization，不得由 Agent 或 Runtime 推断：Product Boundary、Architecture Decision、Host 选择或迁移、高风险系统行为、人工验证预算、发布边界，以及接受残余风险。

高风险系统行为包括但不限于管理员权限、系统范围写入、后台服务、开机启动、防火墙规则、自动执行下载内容、凭据处理和无人值守更新。Agent 可以提出选项、风险和 Evidence，但不能替 Maker 决策。

## 安全与 Evidence

- 网络响应、网页元数据、本地导入、下载内容、压缩包、文件名和清单均视为不可信。
- 下载内容和元数据均按不可信输入处理；记录来源、目标、完整性结论与临时文件处置。
- 解包限制条目路径、大小、数量与递归深度，防止路径穿越、链接绕过和资源耗尽。
- 下载、解包或导入内容不得自动获得执行权限。
- 安装、更新与卸载必须有明确前后状态、冲突策略、失败停止和回滚或恢复路径。
- 凭据、Cookie、令牌、隐私数据与日志遵循最小权限和最小保留。
- Evidence 使用 E0–E5 语义；低等级证据不得因通过自动化而被重命名为目标环境证明。

## Closure

每次受控推进后，确认 Project State 已持久化、revision 已递增、Receipt 与当前状态一致。`READY_FOR_TRANSITION` 不是 Transition 已执行；没有有效 Receipt 不得宣称变更完成。
