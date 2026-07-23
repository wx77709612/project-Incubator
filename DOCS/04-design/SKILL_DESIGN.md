# Project Incubator Skill Design

> Phase 4 — Design 的 Skill 1.0 总设计入口

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 4 — Design |
| 文档状态 | Active |
| 权威范围 | Project Incubator Skill 1.0 的目标形态、总交互过程、设计方法、设计资产架构、设计文档使用流程、触发场景、输入输出、阶段适配、权限边界与 Builder 交接 |
| 消费 Phase | Phase 4–9，按需读取 |
| 更新条件 | Maker 调整 Skill 目标形态、总交互过程、设计方法、设计资产架构、设计文档使用流程、触发方式、权限边界、阶段适配或 Builder 交接方式 |
| 依赖文档 | `DOCS/04-design/SCOPE.md`、`DOCS/04-design/DESIGN.md`、`DOCS/04-design/INTERACTION_DESIGN.md`、`DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`、`DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md`、`DOCS/04-design/PROJECT_STATE_DESIGN.md`、`DOCS/04-design/ARCHITECTURE_DECISION_DESIGN.md`、`DOCS/04-design/TEMPLATE_DEPOSITION_DESIGN.md`、`DOCS/04-design/TECHNICAL_DESIGN.md`、`DOCS/PROJECT_STATE.md` |
| 最后更新 | 2026-07-23 |

## 1. 文档职责

本文档是 Phase 4 设计交付物的总入口。它定义 Project Incubator 未来固化为 Codex Skill 1.0 时，应如何帮助 Maker 孵化项目，以及哪些支撑设计文档分别解决哪些问题。

本文档不定义最终 `SKILL.md` 正文、脚本实现、目录结构、安装方式或发布机制。这些内容属于后续 Phase 5 — Planning 与 Phase 6 — Build 的任务。本文档负责保证后续拆解前，Skill 的协作过程和设计资产架构已经清楚。

## 2. Skill 定位

Project Incubator Skill 是一个面向 Maker 的项目孵化与 AI 协作 Skill。

它的职责是帮助 Maker 从想法捕获开始，经过意图澄清、问题探索、验证、设计、规划、构建、发布、迭代与归档，持续保持主线、处理分叉、恢复上下文，并在每个阶段保留 Maker 的最终决定权。

它不是通用代码生成 Skill，也不是项目管理 SaaS、商业验证工具、自动发布系统或团队协作平台。

## 3. 通用设计方法

Project Incubator Skill 在 Phase 4 中采用 **使用过程导向的设计资产推导**。

含义是：AI 不应先套用固定文档清单，而应先理解目标产物的真实使用过程，再从使用过程倒推出需要哪些设计资产、运行资产、实现资产和沉淀资产。

通用步骤是：

1. 确认目标产物类型；
2. 识别真实使用者、参与者或消费对象；
3. 描述真实使用过程；
4. 沿使用过程找出关键决策点、输入输出、失败点、分叉点和验收点；
5. 判断是否需要补充技术、内容、数据、商业、合规、运营或权限设计面；
6. 推导本项目真正需要的设计文档；
7. 判断哪些内容应进入 Phase 5 拆解，哪些仍需 Maker 决策或后续验证。

该方法可复用于不同项目类型：

| 项目类型 | 真实使用过程 | 由此推导的常见设计资产 |
| --- | --- | --- |
| Skill / Agent 流程 | Maker 与 AI 如何协作完成任务或项目 | 交互流程、状态入口、写回规则、阶段协议、实现承载设计 |
| App / 软件产品 | 用户如何完成核心任务 | 产品范围、用户流程、交互设计、技术架构、数据模型 |
| 内容作品 | 受众如何接收、理解、被触动或采取行动 | 受众定义、内容结构、表达风格、素材方案、发布路径 |
| 工作流 / 方法论 | 参与者如何流转任务、决策和异常 | 角色、输入输出、步骤、交接边界、检查点 |
| 技术库 / 基础设施 | 使用者如何调用、集成、排错和维护 | API 设计、约束、兼容性、测试策略、运维边界 |
| 决策型项目 | Maker 如何基于证据做判断 | 判断框架、证据来源、比较维度、结论格式 |

如果某类项目的关键风险不能仅靠使用过程覆盖，AI 必须补充对应设计面，并向 Maker 说明原因。

## 4. 当前 Skill 的总交互过程

当前目标产物是 Project Incubator Skill 1.0。它的真实使用过程是：Maker 与 AI 围绕一个项目持续协作，逐步推进 Phase，并在每次恢复、分叉、写回、验收和切换时保持主线。

总交互过程如下：

1. 启动或恢复项目：读取项目入口、状态入口、架构边界、当前 Phase 规则和权威文档集合；
2. 建立本轮协作契约：说明当前 Phase、AI 角色、唯一主目标、读写范围、不处理事项、验证方式和 Maker 决策点；
3. Phase 内协作：AI 按当前 Phase 的角色和目标帮助 Maker 澄清、整理、设计、规划、执行或复盘；
4. 新事项分类：出现分叉时，先判断立即处理、记录后续、视为阻塞、请求 Maker 决定，还是拒绝展开；
5. 文档写回：只有当事实、决定、路径、状态、阻塞或下一步发生变化时，写入正确权威文档；
6. 文档审阅：交付物保持 Draft，直到 Maker 接受；
7. Builder 交接：只有当范围、输入、输出、验收和验证步骤明确时，才交给 Builder 执行；
8. 阶段门检查：对照当前 Phase 的 Exit Criteria 汇总证据、缺口和风险；
9. Maker 决定阶段走向：继续、推进、返回、跳过、暂停或归档；
10. 状态回写与下一轮恢复：更新状态入口和权威文档索引，保留可恢复的下一步。

完整交互细节由交互设计资产维护。

## 5. 设计资产架构

当前 Phase 4 的设计文档以本文档为入口，其他文档只承担无法在入口文档中清晰承载的专门职责。

| 设计资产 | 职责 | 设计作用 |
| --- | --- | --- |
| `DOCS/04-design/SKILL_DESIGN.md` | Skill 1.0 总设计入口 | 统一说明 Skill 是什么、如何协作、有哪些支撑设计资产 |
| `DOCS/04-design/SCOPE.md` | 范围与 Phase 5 边界 | 防止设计扩大为商业产品、团队平台或提前实现 |
| `DOCS/04-design/DESIGN.md` | 端到端孵化流程 | 说明 Phase 0–9 如何连接 |
| `DOCS/04-design/INTERACTION_DESIGN.md` | Maker-AI 协作交互 | 设计真实对话过程、确认节点和分叉处理 |
| `DOCS/04-design/AGENT_PROTOCOL_DESIGN.md` | Agent 运行协议 | 设计 `AGENTS.md` 的职责、结构、模板关系和执行边界 |
| `DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md` | 写回规则 | 约束何时写、写到哪里、写后如何检查 |
| `DOCS/04-design/PROJECT_STATE_DESIGN.md` | 状态入口结构 | 设计状态入口字段、更新条件、恢复索引和写后检查 |
| `DOCS/04-design/ARCHITECTURE_DECISION_DESIGN.md` | 架构边界文档结构 | 设计低频高权威边界文档的结构、门槛和读取方式 |
| `DOCS/04-design/TEMPLATE_DEPOSITION_DESIGN.md` | 模板沉淀机制 | 说明阶段交付物何时从项目文档沉淀为模板 |
| `DOCS/04-design/TECHNICAL_DESIGN.md` | Skill 实现承载设计 | 说明未来 Skill 化时的资源组织、定向读取和工具边界 |

Skill 1.0 的结构设计对象限于运行时关键资产。运行时关键资产指高频读写、高权威、跨阶段，并会影响状态恢复、阶段推进或执行安全的资产。

## 6. 设计文档使用流程

Skill 不应把所有 Phase 4 设计文档一次性全文读入上下文后自由发挥。它应以 `SKILL_DESIGN.md` 为入口，根据当前问题分派到对应支撑文档，完成局部判断或修改后返回主线。

推荐使用流程是：

1. 先读取 `SKILL_DESIGN.md`，确认 Skill 目标、总交互过程、设计资产架构和当前任务归属；
2. 根据任务类型选择一个主文档；
3. 只在需要具体规则时读取对应支撑文档；
4. 在支撑文档中完成判断、设计或写回；
5. 回到 `SKILL_DESIGN.md` 检查是否仍符合总交互过程、权限边界和 Phase 5 输入；
6. 如本轮改变了状态、路径、阻塞或下一步，再按写回规则更新状态入口。

常见分派关系如下：

| 当前问题 | 主文档 | 返回检查 |
| --- | --- | --- |
| Skill 是什么、如何协作、需要哪些设计资产 | `SKILL_DESIGN.md` | 不需要分派 |
| Phase 0–9 如何衔接 | `DESIGN.md` | 是否仍服务 Skill 总交互过程 |
| Maker 与 AI 如何对话、确认、处理分叉 | `INTERACTION_DESIGN.md` | 是否保护 Maker 决策权和主线 |
| Agent 如何启动、恢复、执行、回写和处理 Git | `AGENT_PROTOCOL_DESIGN.md` | 是否仍是项目本地运行协议 |
| 范围、非目标、进入 Phase 5 边界 | `SCOPE.md` | 是否避免扩大项目类型或提前实现 |
| 文档何时写、写到哪里、写后怎么检查 | `DOCUMENT_WRITEBACK_DESIGN.md` | 是否没有纠偏留痕或流水化 |
| `PROJECT_STATE.md` 结构和字段 | `PROJECT_STATE_DESIGN.md` | 是否仍是轻量状态入口 |
| `ARCHITECTURE_DECISIONS.md` 结构和门槛 | `ARCHITECTURE_DECISION_DESIGN.md` | 是否只承载长期架构边界 |
| 阶段交付物何时沉淀为模板 | `TEMPLATE_DEPOSITION_DESIGN.md` | 是否来自真实使用和 Maker 接受 |
| Skill 如何由文件、引用、模板、脚本承载 | `TECHNICAL_DESIGN.md` | 是否服务交互过程而不是主导流程 |

如果任务横跨多个支撑文档，AI 应先说明主文档和辅助文档，不应在多个文档之间来回扩散。

## 7. 触发场景

Skill 1.0 应支持以下触发场景：

- Maker 开始一个新项目；
- Maker 恢复一个已有 Project Incubator 项目；
- Maker 发起新任务、新会话或阶段交接；
- Maker 要求生成下一任务 Prompt；
- Maker 报告 Git 闭环完成，需要状态回写；
- 当前任务出现分叉、阻塞、方向性取舍或上下文漂移；
- 当前 Phase 可能满足退出条件，需要阶段门检查。

## 8. 输入与输出

Skill 启动时应优先消费结构化项目状态，而不是聊天记忆。

基本输入包括：

- 项目根目录的 `AGENTS.md`；
- `DOCS/PROJECT_STATE.md`；
- `SPECS/ARCHITECTURE_DECISIONS.md`；
- 当前 Phase 对应的 `FRAMEWORK/Phase-System.md` 章节；
- 当前角色对应的 `FRAMEWORK/Role-System.md` 章节；
- `FRAMEWORK/Document-System.md`；
- `PROJECT_STATE.md` 中列出的当前权威文档集合；
- Maker 本轮新增指令。

常见输出分为两类。

协作输出包括：

- 协作契约；
- 阶段文档草案或更新；
- 设计方案、规划方案或任务拆解；
- 新任务 Prompt；
- 分叉分类结果；
- 阶段门检查结果；
- Builder 任务边界；
- Maker Diff 审阅报告；
- 状态回写。

执行输出包括：

- 代码修改；
- 内容成稿；
- 视觉、音频、视频或其他资产；
- 配置、模板或脚本修改；
- 验证结果、测试记录或运行说明；
- 可供 Maker 检查的完整未提交 Diff。

Skill 不应把所有输出都写成文档。只有对后续恢复、决策、执行、验证或复盘有明确价值时才创建或更新文档。

## 9. 阶段适配

Skill 必须根据当前 Phase 调整 AI 角色、协作深度和交付物类型。

| Phase | Skill 行为 |
| --- | --- |
| Phase 0 | 帮助 Maker 捕获想法，不急于评估或实现 |
| Phase 1 | 澄清动机、目标用户、边界和成功标准 |
| Phase 2 | 理解问题、真实工作流、替代方式和关键假设 |
| Phase 3 | 设计低成本验证，并区分真实证据和积极表达 |
| Phase 4 | 用使用过程导向方法推导设计资产，形成足以进入 Planning 的设计 |
| Phase 5 | 把已确认设计拆为可执行、可验证任务 |
| Phase 6 | 约束 Builder 按任务执行，并完成验证与回写 |
| Phase 7 | 帮助成果进入真实使用或发布场景 |
| Phase 8 | 基于真实反馈判断下一步 |
| Phase 9 | 归档结果、经验和可复用资产 |

Skill 不得因为读取到后续 Phase 的文档或规则而自动推进阶段。

## 10. 权限边界

Skill 可以建议、整理、创建草案和执行授权范围内的文件修改，但必须保护 Maker 的最终决定权。

权限边界应按原则表达：

- 决策边界：项目方向、主要类型、目标用户、成功标准、范围取舍、阶段切换和验收由 Maker 决定；
- 权威边界：已确认事实、架构边界、Phase 规则、角色规则和文档规则只能通过受控变更修改；
- 执行边界：AI 只在本轮任务授权范围内读取、创建或更新文件，不把未确认假设写成事实；
- Git 边界：Git 写操作、远端操作、历史修改和破坏性操作必须遵守项目级授权与 Maker 验收门；
- 范围边界：公开、商业化、产品化或完整实现不能由 AI 根据“可能有用”自行扩大。

当出现新偏差时，Skill 应优先把它归入上述边界并修正行为；只有具有跨项目复用价值的新型风险，才应由 Maker 确认后扩展长期规则。

## 11. Builder 交接

Skill 必须遵守当前 Phase 和 Role-System 定义的角色边界。

当当前 Phase 规则允许 AI 承担 Builder 执行任务时，执行前必须具备：

- 背景与目标；
- 输入、输出和依赖；
- 范围与非目标；
- 允许和禁止修改的区域；
- 验收标准与验证步骤；
- 风险、阻塞项和完成后应更新的文档。

执行完成后，AI 应回到当前 Phase 的协作视角，协助 Maker 检查结果是否符合阶段目标、设计范围和验收标准，并判断是否需要 Maker 审阅或状态回写。

## 12. Phase 5 输入

Phase 5 应以本文档为入口，把 Skill 1.0 拆为范围明确、可独立执行、可独立验证的任务包。

Phase 5 至少应能从 Phase 4 设计中获得：

- Skill 1.0 的目标、范围和非目标；
- 使用过程导向的 Phase 4 通用设计方法；
- 当前 Skill 的完整交互过程；
- Phase 0–9 的端到端流程；
- 高频权威文档的结构设计；
- 文档写回、状态收敛和模板沉淀规则；
- 实现承载设计、定向读取和工具边界；
- Builder 交接条件和验收方式。
