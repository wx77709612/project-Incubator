# Project Incubator Scope

> Phase 4 — Design 的范围定义

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 4 — Design |
| 文档状态 | Active |
| 权威范围 | Project Incubator Skill 1.0 的完整范围、非目标、Phase 4 设计深度与设计文档组合规则、进入 Phase 5 的边界 |
| 消费 Phase | Phase 4–9，按需读取 |
| 更新条件 | Maker 调整 Skill 1.0 范围、非目标、设计深度、设计文档组合、规划边界或 Phase 5 输入要求 |
| 依赖文档 | `DOCS/01-intent/INTENT.md`、`DOCS/01-intent/PROJECT_PROFILE.md`、`DOCS/02-explore/PROBLEM.md`、`DOCS/02-explore/RESEARCH.md`、`DOCS/03-validate/VALIDATION_PLAN.md`、`DOCS/PROJECT_STATE.md` |
| 最后更新 | 2026-07-23 |

## 1. 文档职责

本文档定义 Project Incubator 在当前 Design 阶段的范围边界、设计深度和设计交付物组合。

Phase 4 — Design 负责把项目设计到足以规划和执行的程度。它可以包含产品设计、流程设计、交互设计、内容结构设计、技术方案设计、系统架构设计、Skill 形态设计等，具体包含哪些取决于项目类型。

本文档不执行代码实现、内容制作、资产生成、Skill 安装发布或任务拆解。它可以定义实现方案设计、技术方向、系统边界、组件职责、数据或文档流、验收方式；Phase 5 — Planning 再将这些已确认设计拆解为任务，Phase 6 — Build 再执行具体实现。

## 2. 当前目标产物

Project Incubator 当前目标产物是一个可用于 Maker 自用项目孵化的 **Codex Skill 1.0 完整流程**。

该 Skill 的目标不是单独解决某一个 Phase，也不是只提供一组文档模板，而是帮助 Maker 在未来孵化不同类型项目时，从想法捕获开始，经过意图澄清、问题探索、验证、设计、规划、构建、发布、迭代与归档，持续保持主线、治理分叉、恢复上下文并完成阶段验收。

当前项目本身正在使用这套流程孵化自身，因此本阶段设计既要服务 Project Incubator 自身，也要为未来 Skill 化保留通用规则。

## 3. Phase 4 设计深度校准规则

未来 Project Incubator Skill 进入任意项目的 Phase 4 — Design 时，AI 不应默认把设计收缩为 MVP，也不应默认设计完整 1.0。AI 必须先与 Maker 校准设计深度。

校准时至少判断：

- 目标产物类型是什么：Skill、App、内容作品、个人工具、工作流、模板、决策结果或其他类型；
- Maker 当前要验收的是完整流程、首个版本、原型、内容成稿，还是某个阶段性方案；
- Phase 5 需要哪些设计输入，才能拆解为范围明确、可独立执行、可独立验证的任务；
- 如果只做 MVP，是否会破坏项目核心价值；
- 如果设计完整 1.0，是否会造成过度执行范围；
- 哪些取舍必须由 Maker 决定，哪些可以由 AI 提出方案和推荐。

对当前 Project Incubator 项目，校准结果是：本项目的可验收对象必须是 Skill 1.0 的完整孵化流程。只设计 v0.1 或 MVP 片段会切碎跨阶段价值，无法验证 Skill 是否真的能帮助 Maker 完成完整项目孵化。

## 4. 不同项目类型的 Phase 4 设计文档组合

Project Incubator Skill 进入其他项目的 Phase 4 时，应根据目标产物类型选择设计文档组合，而不是机械创建同一组文档。

| 项目类型 | Phase 4 应覆盖的设计面 | 常见设计文档 |
| --- | --- | --- |
| App / 软件产品 | 产品范围、用户流程、交互设计、技术架构、数据模型、验收方式 | `SCOPE.md`、`DESIGN.md`、`UX_FLOW.md`、`TECHNICAL_DESIGN.md`、按需 `DATA_MODEL.md` |
| 内容作品 | 受众、表达目标、内容结构、风格、制作流程、成稿标准 | `CONTENT_BRIEF.md`、`AUDIENCE.md`、`CONTENT_STRUCTURE.md`、`STYLE_GUIDE.md`、按需 `SCRIPT_OUTLINE.md` |
| Skill / Agent 流程 | 协作流程、阶段协议、Agent 运行协议、状态入口、文档系统、写回规则、模板沉淀、触发场景、权限边界、实现承载设计 | `SKILL_DESIGN.md`、`SCOPE.md`、`DESIGN.md`、`INTERACTION_DESIGN.md`、`AGENT_PROTOCOL_DESIGN.md`、`PROJECT_STATE_DESIGN.md`、`DOCUMENT_WRITEBACK_DESIGN.md`、`TEMPLATE_DEPOSITION_DESIGN.md`、`TECHNICAL_DESIGN.md` |
| 工作流 / 方法论 | 角色、输入输出、步骤、异常处理、交接边界、验收标准 | `SCOPE.md`、`DESIGN.md`、按需 `INTERACTION_DESIGN.md` |
| 决策型项目 | 判断框架、证据来源、比较维度、结论格式、风险边界 | `SCOPE.md`、`DECISION_FRAMEWORK.md` 或 `DESIGN.md` |
| 个人工具 | 真实使用流程、最小有用成果、约束、验收方式、必要技术方向 | `SCOPE.md`、`DESIGN.md`、按需 `TECHNICAL_DESIGN.md` |

上表是选择规则，不是强制清单。AI 必须说明当前项目需要哪些设计文档，以及这些文档如何支持后续 Planning。

## 5. Skill 1.0 范围

Project Incubator Skill 1.0 应覆盖以下能力范围：

- 项目启动与状态恢复：按 `AGENTS.md`、`DOCS/PROJECT_STATE.md` 和权威文档集合恢复项目状态；
- Phase 驱动协作：根据当前 Phase 切换 AI 角色、目标、交付物和边界；
- Maker 决策保护：阶段切换、范围变化、成功标准、验收和关键取舍由 Maker 决定；
- 文档状态管理：使用固定状态入口、Phase 目录和单一权威来源，确保项目事实可恢复、可审阅且不重复维护；
- 任务入口管理：新任务只记录本轮新增目标、授权、限制和验收要求；项目背景由状态文档和权威文档自动恢复；
- 分叉任务管理：出现新问题、新想法或上下文漂移时，先判断立即处理、记录后续、视为阻塞，还是请求 Maker 决定；
- Git 安全与验收：执行前检查分支、工作区、远端同步和未闭环任务，完成后保留 Diff 给 Maker 审阅；
- Builder 交接：在 Planning 和 Build 阶段把任务拆为范围明确、可执行、可验证的工作单元；
- 阶段回写：阶段事实、文档路径、阻塞项、下一步和恢复入口变化时，更新对应权威文档；
- 多项目类型适配：支持 Personal Tool、App、内容作品、工作流等不同目标产物采用不同设计深度和交付物组合。

## 6. 非目标与边界原则

Skill 1.0 的非目标不应维护为一次次纠偏后的单一禁止事项清单，而应以可复用边界原则表达。这样可以防止规则膨胀，也避免把单次协作偏差写成长期限制。

本项目的非目标应以可复用的边界原则表达：

- 不替代 Maker 决策：项目方向、目标用户、范围、成功标准、阶段切换、验收和取舍仍由 Maker 决定；
- 不越过当前 Phase：AI 只能在当前 Phase 的目标、角色和交付物边界内协作，跨 Phase 请求必须先说明影响并获得 Maker 决定；
- 不默认扩大项目类型：是否公开、商业化、产品化、Skill 化或进入完整实现，必须来自项目意图和 Maker 确认；
- 不把建议当事实：AI 的推断、方案、礼貌性肯定和外部参考必须与 Maker 确认事实分开；
- 不把流程变成负担：文档、模板、检查和 Git 规则只在能帮助恢复、决策、执行、验证或复盘时引入；
- 不执行未授权写入或 Git 闭环：文件写入、分支、提交、推送、合并和破坏性操作必须遵守项目授权和验收门。

后续如果 AI 在某次协作中出现新的偏差，应先判断它属于哪条边界原则，优先修正现有原则或交互流程；只有当现有原则无法覆盖，并且 Maker 确认它具有跨项目复用价值时，才新增长期非目标。

## 7. 当前 Phase 4 应创建的设计交付物

当前项目类型是 Skill / Agent 流程。Phase 4 应创建以下设计交付物：

- `DOCS/04-design/SCOPE.md`：定义 Skill 1.0 的范围、非目标、设计深度校准和进入 Planning 的边界；
- `DOCS/04-design/DESIGN.md`：定义 Skill 1.0 的端到端项目孵化流程；
- `DOCS/04-design/INTERACTION_DESIGN.md`：定义 Maker 与 AI 在 Skill 中的协作交互、确认节点、分叉处理和阶段切换对话边界；
- `DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`：定义 `AGENTS.md` 的职责、结构、模板关系、启动协议、执行边界和更新门槛；
- `DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md`：定义文档写回卫生、纠偏处理、状态入口收敛、边界规则收敛和高权威文档候选写回；
- `DOCS/04-design/PROJECT_STATE_DESIGN.md`：定义 `PROJECT_STATE.md` 的职责、结构、字段、模板关系、更新条件和写后检查；
- `DOCS/04-design/SKILL_DESIGN.md`：定义未来 Codex Skill 形态下的职责、触发、输入输出、权限边界和执行约束；
- `DOCS/04-design/TECHNICAL_DESIGN.md`：定义 Skill 1.0 的技术方向、系统边界、资产分工、运行时读取与写入策略、Git 和工具权限边界；
- `DOCS/04-design/ARCHITECTURE_DECISION_DESIGN.md`：定义 `ARCHITECTURE_DECISIONS.md` 的职责、结构、写入门槛和读取方式；
- `DOCS/04-design/TEMPLATE_DEPOSITION_DESIGN.md`：定义运行入口、状态入口和阶段交付物如何沉淀为生产模板。


## 8. 进入 Phase 5 的边界

Phase 4 完成后，Phase 5 应基于 Skill 1.0 的完整流程拆解任务，而不是基于 MVP 片段拆任务。

但 Phase 5 仍必须把完整流程拆成多个范围明确、可独立执行、可独立验证的任务包。完整 1.0 是规划对象，不代表一次性交给 AI Builder 无边界实现。

进入 Phase 5 前，至少需要确认：

- Skill 1.0 的完整范围和非目标；
- 端到端流程的 Phase、角色、文档、状态和阶段门关系；
- 不同项目类型在 Phase 4 设计深度上的适配规则；
- 当前 Skill 项目的协作交互设计、Agent 运行协议设计与技术方案设计；
- 文档写回卫生、状态入口收敛和边界规则收敛；
- `AGENTS.md` 与 `PROJECT_STATE.md` 的生产模板关系；
- Architecture Decision 的用途、结构、写入门槛和定向读取方式；
- 哪些内容属于 Planning 可拆解任务，哪些仍是 Maker 决策或后续实现细节；
- Phase 3 的 `VALIDATION_RESULTS.md` 暂缓到 Phase 7 后回收，不阻塞当前 Design。

当前 Phase 4 还应确认以下协作规则设计面：

| 设计面 | 设计归属 |
| --- | --- |
| 文档纠偏处理 | `DOCUMENT_WRITEBACK_DESIGN.md` |
| 状态入口收敛 | `PROJECT_STATE_DESIGN.md`、`DOCUMENT_WRITEBACK_DESIGN.md` |
| 边界原则收敛 | `SCOPE.md`、`DOCUMENT_WRITEBACK_DESIGN.md` |
| 阶段特殊性校准 | `DESIGN.md`、`SKILL_DESIGN.md`、`INTERACTION_DESIGN.md` |
| Agent 运行协议 | `AGENT_PROTOCOL_DESIGN.md` |
| Architecture Decision 文档设计归属 | `ARCHITECTURE_DECISION_DESIGN.md` |
| Architecture Decision 写回行为 | `DOCUMENT_WRITEBACK_DESIGN.md` |
| 定向读取保障 | `TECHNICAL_DESIGN.md` |
| 模板沉淀机制 | `TEMPLATE_DEPOSITION_DESIGN.md` |
