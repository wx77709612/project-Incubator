# Project Incubator Design

> Phase 4 — Design 的完整流程设计

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 4 — Design |
| 文档状态 | Active |
| 权威范围 | Project Incubator Skill 1.0 的端到端孵化流程、设计面选择、角色协作、文档流、阶段门、分叉治理和验收关系 |
| 消费 Phase | Phase 4–9，按需读取 |
| 更新条件 | Maker 调整 Skill 1.0 流程、阶段关系、角色边界、文档流、阶段门或验收方式 |
| 依赖文档 | `DOCS/04-design/SCOPE.md`、`DOCS/01-intent/INTENT.md`、`DOCS/01-intent/PROJECT_PROFILE.md`、`DOCS/02-explore/PROBLEM.md`、`DOCS/02-explore/RESEARCH.md`、`DOCS/03-validate/VALIDATION_PLAN.md`、`DOCS/PROJECT_STATE.md` |
| 最后更新 | 2026-07-23 |

## 1. 文档职责

本文档定义 Project Incubator Skill 1.0 的完整项目孵化流程。

本文档不拆解具体 Build 任务，不定义 Skill 代码实现，也不替代 Phase 5 的 Roadmap、Milestones、Tickets 或 Verification Plan。

## 2. 设计目标

Project Incubator Skill 1.0 应帮助 Maker 将一个项目从想法推进到 Maker 认可的阶段性结果，并在过程中保持：

- 主线清楚；
- 阶段目标清楚；
- AI 角色清楚；
- 权威文档清楚；
- 新事项处理方式清楚；
- Git 与 Diff 验收边界清楚；
- 后续会话可恢复。

对当前项目而言，1.0 的可验收对象是一套完整 Skill 流程，而不是 MVP 片段。

Phase 4 的设计目标不是只写范围摘要，而是完成足以进入 Phase 5 拆解的方案设计。对当前 Skill 项目，这包括范围设计、端到端流程设计、Maker-AI 交互设计、Skill 形态设计和技术方案设计。

## 3. 核心流程总览

Skill 1.0 的主流程由十个 Phase 组成：

| Phase | 目标 | 主要输出 |
| --- | --- | --- |
| Phase 0 — Idea Capture | 捕获想法，不急于判断或实现 | `IDEA.md` |
| Phase 1 — Intent Discovery | 明确为什么做、为谁做、做到什么算成功 | `INTENT.md`、`PROJECT_PROFILE.md` |
| Phase 2 — Explore | 理解问题、现有方式、关键假设 | `PROBLEM.md`、`RESEARCH.md` |
| Phase 3 — Validate | 低成本验证最关键假设 | 按需 `VALIDATION_PLAN.md`、`VALIDATION_RESULTS.md` |
| Phase 4 — Design | 明确第一版完整设计和范围 | `SCOPE.md`、`DESIGN.md` 及按需设计文档 |
| Phase 5 — Planning | 拆成可执行、可验证任务 | `ROADMAP.md`、`MILESTONES.md`、`VERIFICATION_PLAN.md`、`TICKETS/` |
| Phase 6 — Build | 按任务执行并验证真实成果 | 代码、内容、资产、验证记录及状态回写 |
| Phase 7 — Launch | 将成果投入目标使用场景 | 按需发布、交付、使用入口与反馈入口 |
| Phase 8 — Iterate | 基于真实使用决定下一步 | `FEEDBACK.md`、`BACKLOG.md`、`ISSUES.md` 等 |
| Phase 9 — Archive | 结束周期并沉淀经验 | `RETROSPECTIVE.md`、`LESSONS_LEARNED.md` 等 |

Phase 可以轻量执行、跳过、返回或暂停，但每次变化都必须由 Maker 明确决定并写回状态。

## 4. 角色协作模型

Maker 始终是项目所有者和最终决策者。AI 在不同 Phase 中切换为对应的 AI Collaborator，必要时在 Planning 或 Build 中授权 AI Builder 执行明确任务。

AI Collaborator 的共同职责是：

- 恢复当前项目状态；
- 明确本轮 Phase、角色、目标、范围和预期交付物；
- 区分事实、假设、建议和待决问题；
- 提出方案和取舍；
- 帮助 Maker 形成阶段交付物；
- 在阶段门前检查 Exit Criteria；
- 保护 Maker 对方向、范围、验收和阶段切换的最终决定权。

AI Builder 的职责只在任务明确后出现。Builder 不重新定义方向，只完成授权范围内的修改、制作或验证。

## 5. 文档流设计

Skill 1.0 使用固定状态入口加 Phase 文档的结构：

- `DOCS/PROJECT_STATE.md` 是启动和恢复入口；
- `AGENTS.md` 是 Agent 执行协议；
- `SPECS/` 保存不可静默改变的架构决策；
- `FRAMEWORK/` 保存 Project Incubator 的通用规则；
- `DOCS/<phase>/` 保存具体项目阶段交付物；
- `TEMPLATES/` 保存经真实验证后可复用的模板。

文档设计原则是：

- 一个事实只维护一个权威来源；
- 后续 Phase 通过精确路径引用上游文档；
- `PROJECT_STATE.md` 保持轻量，不成为流水账；
- 按需创建文档，不为形式完整预建空文档；
- 推翻前序结论必须由 Maker 批准回退或受控变更。

## 6. 任务入口设计

Maker 发起新任务、新会话或阶段交接时，Skill 应区分两类输入：

- 项目状态输入：由 `AGENTS.md`、`PROJECT_STATE.md` 和当前权威文档集合自动恢复；
- 本轮任务输入：由 Maker 的本次指令或 `TEMPLATES/MAKER-TASK-PROMPT.template.md` 承载。

任务 Prompt 不应搬运完整项目状态，只应说明本轮新增目标、授权、限制、验收或特别注意事项。

## 7. 分叉治理设计

当出现新问题、新想法、上下文漂移、Git 异常或设计取舍时，AI 必须先分类，再行动。

分类包括：

- 立即处理：影响当前任务目标、状态入口、权威文档正确性、安全边界，或 Maker 明确要求现在处理；
- 记录后续：真实存在，但不影响当前主线继续；
- 视为阻塞：当前任务无法安全继续；
- 请求 Maker 决定：存在方向性取舍、授权边界变化或多种合理处理方式；
- 拒绝展开：与当前 Phase、项目类型或已确认非目标冲突。

AI 不应把所有新事项默认塞入待办，也不应把所有新想法默认纳入当前主线。

## 8. Phase 4 设计面适配

Phase 4 面对不同项目类型时，必须先校准设计深度。

通用判断是：

- 如果目标产物是 Skill 或完整流程，且核心价值来自端到端闭环，Phase 4 应设计完整流程；
- 如果目标产物是 App 或软件产品，Phase 4 应覆盖产品范围、用户流程、交互设计、技术架构、数据模型和验收方式，具体深度由 Maker 当前验收对象决定；
- 如果目标产物是内容作品，Phase 4 应设计受众、表达目标、内容结构、表达方式、成稿标准和制作边界；
- 如果目标产物是决策结果，Phase 4 应设计判断框架、输入来源和结论格式；
- 如果目标产物是个人工具，Phase 4 应优先设计真实使用流程和最小有用成果。

当前 Project Incubator 的校准结论是：Phase 4 应设计 Skill 1.0 完整端到端流程，并补齐协作交互设计和技术方案设计，让 Phase 5 按完整流程拆解任务。

## 9. 阶段特殊性与后续流程设计

Skill 1.0 应把当前 Phase 4 暴露出的分叉抽象为通用机制：每个 Phase 都可能需要根据项目类型和 Maker 验收对象调整深度、交付物和后续流程。

设计原则是：

- 当前 Phase 的标准规则提供默认路径；
- Maker 的项目类型和验收对象决定是否轻量、完整、跳过、返回或加深；
- AI 发现偏差时先请求 Maker 决定，不自行扩大或缩小范围；
- 特殊处理必须说明它如何服务下一 Phase；
- 特殊处理不能直接变成长期规则，除非 Maker 确认具有跨项目复用价值。

不同 Phase 的常见后续流程包括：

| Phase | 可能出现的特殊后续流程 |
| --- | --- |
| Phase 0 | 新项目继续进入 Intent；已有项目接入可能先做状态恢复或材料盘点 |
| Phase 1 | Personal Tool 走轻量路径；Business Product 可能要求更完整 Explore / Validate |
| Phase 2 | 问题仍不清楚时继续 Explore；已足够清楚时进入轻量 Validate 或 Design |
| Phase 3 | 验证足够时进入 Design；证据不足时继续验证；失败时调整、暂停或结束 |
| Phase 4 | 根据项目类型选择设计面和文档组合；设计不足不得交给 Planning |
| Phase 5 | 按完整流程拆任务、按里程碑拆任务，或先拆治理/准备任务 |
| Phase 6 | Builder 执行后回到 Collaborator 验收；失败时回到 Planning 或 Design |
| Phase 7 | 自用 Launch、公开发布、内容交付或商业上线采用不同验收方式 |
| Phase 8 | 继续迭代、返回 Design、维护、暂停、转向或归档 |
| Phase 9 | 归档结果、沉淀可复用资产，或保留未来恢复入口 |

## 10. Git 与验收设计

Skill 1.0 的 Git 治理用于保护 Maker 审阅权和任务边界。

基本设计是：

- 只读任务不创建分支；
- 写入任务前检查仓库、分支、工作区、暂存区、远端同步和未闭环任务；
- 新独立写入任务使用 Phase 感知工作分支；
- 同一任务续作继续使用同一工作范围；
- AI 完成修改后保留未提交 Diff；
- Maker 在 IDE Diff 中检查；
- Git 暂存、提交、推送、合并和分支清理由 Maker 手动执行，除非另有明确授权。

Git 规则不应成为普通协作的额外负担；它只在写入、分支、阶段切换或里程碑验收时发挥约束作用。

## 11. Phase 5 输入要求

Phase 5 应从本设计中获得以下输入：

- Skill 1.0 的完整范围和非目标；
- 十个 Phase 的端到端关系；
- 各 Phase 的输入、输出、Maker 决策点和 AI 角色；
- 文档系统、任务入口、分叉治理、Git 验收和阶段回写的设计；
- Maker-AI 交互方式、确认节点和异常处理边界；
- Skill 1.0 的技术方向、资产分工和权限边界；
- 哪些模块可以拆为独立任务；
- 哪些内容仍需 Maker 决定，不能交给 Builder 直接实现。

Phase 5 的拆解对象是完整 Skill 1.0，但拆解结果必须是多个可独立执行和验证的任务包。

## 12. 相关设计文档

本文件定义端到端主流程。当前 Phase 4 的其他设计面由以下文档维护：

- `DOCS/04-design/SCOPE.md`：范围、非目标、设计文档组合和进入 Planning 的边界；
- `DOCS/04-design/INTERACTION_DESIGN.md`：Maker 与 AI 的协作交互、确认节点、分叉对话和阶段切换；
- `DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md`：文档写回卫生、状态入口收敛、边界规则收敛和高权威文档候选写回；
- `DOCS/04-design/SKILL_DESIGN.md`：Skill 的职责、触发场景、输入输出和权限边界；
- `DOCS/04-design/TECHNICAL_DESIGN.md`：Skill 技术方向、资产分工、读写策略、工具和 Git 边界。

## 13. 当前未设计事项

以下事项不在 Phase 4 中完成：

- Skill 的具体代码结构；
- Skill 安装、发布、权限和版本分发机制；
- 每个模板的最终字段；
- 自动化能力的实现顺序；
- 未来对外分享或商业化策略；
- 隐私隔离和多项目工作区创建机制；
- Phase 3 `VALIDATION_RESULTS.md` 的详细内容。

这些事项应在 Phase 5 或后续 Phase 中按任务和证据继续处理。
