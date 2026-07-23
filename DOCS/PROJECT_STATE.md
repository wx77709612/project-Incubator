# Project State

> Project Incubator 当前状态的唯一权威来源

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | 跨阶段状态文档 |
| 文档状态 | Active |
| 权威范围 | 当前项目状态、Phase、角色、目标、权威文档集合、阻塞项、阶段门与下一步 |
| 消费 Phase | Phase 0–9，启动时必读 |
| 更新条件 | 状态、Phase、角色、文档路径、决定、阻塞项或下一步发生变化 |
| 依赖文档 | `AGENTS.md`、`SPECS/ARCHITECTURE_DECISIONS.md`、当前 Phase 规则与交付物 |
| 最后更新 | 2026-07-23 |

## 1. 基本状态

| 字段 | 当前值 |
| --- | --- |
| 项目名称 | Project Incubator |
| Maker | 当前项目的人类所有者，即正在与 AI 协作的用户 |
| 项目状态 | Active |
| 当前 Phase | Phase 4 — Design |
| 当前 AI 角色 | Workflow Designer（流程设计顾问） |
| 当前主要目标 | 将已确认的意图、问题、研究与轻量验证判断转化为 Project Incubator Skill 1.0 的完整设计：明确范围、端到端流程、Maker-AI 交互、Agent 运行协议、高风险动作门禁、Skill 形态与技术方案。 |
| 当前阶段交付物 | Active：`DOCS/04-design/SKILL_DESIGN.md`、`DOCS/04-design/SCOPE.md`、`DOCS/04-design/DESIGN.md`、`DOCS/04-design/INTERACTION_DESIGN.md`、`DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`、`DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md`、`DOCS/04-design/PROJECT_STATE_DESIGN.md`、`DOCS/04-design/ARCHITECTURE_DECISION_DESIGN.md`、`DOCS/04-design/TEMPLATE_DEPOSITION_DESIGN.md`、`DOCS/04-design/TECHNICAL_DESIGN.md`；上游 Active：`DOCS/03-validate/VALIDATION_PLAN.md`、`DOCS/02-explore/PROBLEM.md`、`DOCS/02-explore/RESEARCH.md` |
| 当前任务状态 | Accepted（Maker 已接受 Phase 4 十份设计交付物；待处理 Architecture Decisions 重构后再进入 Phase 5） |
| 稳定分支 | `main` |
| 工作分支规则 | `p<当前Phase>/<type>-<topic>`；实际分支由 Git 状态确认 |
| 下一项决定 | 处理 `SPECS/ARCHITECTURE_DECISIONS.md` 的内容审计与结构重构；完成并经 Maker 接受后，再执行 Phase 4 到 Phase 5 的阶段切换检查。 |
| 最近更新时间 | 2026-07-23 |

## 2. 当前阶段说明

Project Incubator 本身是一个正在使用自身 Framework 孵化的项目。

项目已完成 Phase 0、Phase 1、Phase 2 与轻量 Phase 3 的退出判断。Maker 已于 2026-07-22 确认首轮自用验证已经足够支持 Phase 3 的退出判断，并决定进入 Phase 4 — Design。

Phase 3 仅验证自用价值，不接触外部用户，不进行市场、付费或重型商业验证。`VALIDATION_RESULTS.md` 暂不创建空文档；Maker 建议将其作为后续回收事项，在完成 Phase 7 后收束补齐。

Phase 4 已开始设计 Project Incubator Skill 1.0 的完整流程。当前设计方向是：本项目的可验收对象不是 v0.1/MVP 片段，而是可帮助 Maker 孵化其他项目的完整 Skill 1.0 流程；Phase 5 应基于完整 1.0 流程拆解为多个范围明确、可独立执行、可独立验证的任务包。

## 3. 当前 AI 协作契约

当前 AI 应以 Workflow Designer 身份工作：

- 基于已确认意图、问题定义、轻量研究与 Phase 3 判断，提出 Project Incubator Skill 1.0 的完整设计方案；
- 明确范围边界、非目标、关键流程、协作交互、技术方向与验收方式；
- 区分已确认设计决定、仍需 Maker 选择的取舍，以及后续才处理的实现细节；
- 只在确有长期消费价值时创建或更新 Phase 4 设计文档。

当前 AI 不应：

- 默认进入开发、代码实现或 Skill 固化；
- 扩大为公开产品、商业产品或团队协作平台设计；
- 修改已确认的项目类型、目标用户、成功标准或 Phase 路径；
- 为形式完整创建无人继续消费的文档。

## 4. 已完成内容（当前基线）

本节只维护恢复当前项目所需的有效基线，不作为历史流水账。详细经过、旧版本差异和里程碑时间线按需从对应权威文档与 Git 历史读取，不新增默认必读的历史文档或索引文档。

### 4.1 阶段与交付物基线

- Phase 0 — Idea Capture 已完成，`DOCS/00-idea/IDEA.md` 为 Active；
- Phase 1 — Intent Discovery 已完成，`DOCS/01-intent/INTENT.md` 与 `DOCS/01-intent/PROJECT_PROFILE.md` 为 Active；
- Phase 2 — Explore 的必需交付物已获 Maker 接受，`DOCS/02-explore/PROBLEM.md` 与 `DOCS/02-explore/RESEARCH.md` 为 Active；
- Phase 3 — Validate 已完成轻量退出判断，`DOCS/03-validate/VALIDATION_PLAN.md` 为 Active；`DOCS/03-validate/VALIDATION_RESULTS.md` 暂缓至 Phase 7 后回收补齐；
- Phase 4 — Design 的十份交付物已获 Maker 接受并转为 Active：`DOCS/04-design/SKILL_DESIGN.md`、`DOCS/04-design/SCOPE.md`、`DOCS/04-design/DESIGN.md`、`DOCS/04-design/INTERACTION_DESIGN.md`、`DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`、`DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md`、`DOCS/04-design/PROJECT_STATE_DESIGN.md`、`DOCS/04-design/ARCHITECTURE_DECISION_DESIGN.md`、`DOCS/04-design/TEMPLATE_DEPOSITION_DESIGN.md`、`DOCS/04-design/TECHNICAL_DESIGN.md`。其中 Agent 协议、交互设计和技术设计已纳入高风险结果导向门禁机制。

### 4.2 当前有效治理基线

- Project Incubator 采用固定状态入口 `DOCS/PROJECT_STATE.md` 与 Phase 目录结合的项目文档结构；
- 权威文档采用所有者 Phase、精确路径引用和受控更新机制，一个事实只维护一个权威来源；
- Agent 启动、恢复、Git 检查、工作分支、Diff 验收门、Maker 手动 Git 闭环和会话结束回写规则以 `AGENTS.md` 为准；
- Maker 任务 Prompt 生成必须先读取 `TEMPLATES/MAKER-TASK-PROMPT.template.md`，Prompt 只承载本次任务特有新增内容，不搬运项目状态；
- Maker Git 闭环完成回写优先于下一任务 Prompt、Phase 切换或无关新任务；
- 项目与任务采用自适应规划深度，简单、可逆、目标单一的任务不强制创建独立设计文档或实施计划；
- `SKILL/` 当前仅为未来实现预留说明，不是现阶段启动依赖。

### 4.3 当前项目理解基线

- Project Incubator 本身是首个真实孵化对象，当前主要类型与工作重心来自 Maker 的真实 AI 协作流程；
- 当前面向 indie developer / solo maker，重点是个人主线保护、AI 协作分叉治理、上下文恢复和个人验收；
- Phase 2 已确认的核心痛点是：新想法或问题解决过程持续分叉，导致上下文变长、token 与时间成本上升、AI 丢失主线并跑偏；
- Phase 2 外部轻量研究的目的不是完整产品或竞品研究，而是补充识别相似工作流中的普遍痛点；
- Project Incubator 与市面项目 / Issue / Agent 协作平台的关键差异在于：后者偏团队任务协作，本项目当前偏个人创造主线与 AI 协作状态治理。

### 4.4 历史追溯边界

- 阶段事实与 Maker 确认内容以对应 Phase 文档为权威来源；
- 治理规则以 `AGENTS.md`、`FRAMEWORK/Document-System.md` 和相关 `SPECS/` 文档为权威来源；
- 里程碑提交、分支闭环和旧版本差异以 Git 历史按需追溯；
- 本节不得继续按消息、任务或提交追加流水账；新增完成事实应先判断是否改变当前基线，再归入上方类别或更新对应权威文档。

## 5. 当前未确认事项

- token、时间和维护成本的具体阈值；
- 已有项目的接入流程、阶段推断依据、确认机制和文档补全规则；
- 自动识别阶段、生成草案和更新状态文档的具体权限分级；
- Project Incubator 的具体实现形态；
- 状态模型的完整字段、状态枚举与版本规则；
- 未来具体项目工作区的位置与创建方式；
- Framework 如何版本化、验证和批准变更；
- 未来 Codex Skill 的触发方式、权限、安装和发布机制；
- 空 `CHANGELOG.md` 应在什么阶段启用；
- 空 `.agents/` 目录应保留、定义用途还是移除。
- `DOCS/03-validate/VALIDATION_RESULTS.md` 在 Phase 7 后如何收束补齐，以及应记录到什么细度。
- Phase 4 设计交付物经 Maker 接受后，立即处理 `SPECS/ARCHITECTURE_DECISIONS.md` 的内容审计与结构重构：判断现有 Decision 是否符合低频、高权威、原则型边界，并整理为可定向读取的结构。
- Phase 4 设计交付物已接受；进入 Phase 5 前需先完成 `SPECS/ARCHITECTURE_DECISIONS.md` 内容审计与结构重构。

主要项目类型、第一目标用户、边界、非目标、成功标准和推荐流程路径已经在 Phase 1 中确认；其余事项应在适当的后续 Phase 中逐步确认，不在当前阶段一次性解决。

## 6. 当前阻塞项

当前没有执行层面阻塞。Phase 4 设计交付物已接受；进入 Phase 5 前需先完成 `SPECS/ARCHITECTURE_DECISIONS.md` 内容审计与结构重构。

## 7. 当前 Exit Criteria 状态

Phase 4 — Design 的 Exit Criteria 已由 Maker 接受：

| Exit Criteria | 当前状态 | 证据 |
| --- | --- | --- |
| 项目范围已明确 | 已接受 | `DOCS/04-design/SCOPE.md` |
| 第一版成果已定义 | 已接受 | `DOCS/04-design/SKILL_DESIGN.md`、`DOCS/04-design/DESIGN.md` |
| 核心流程已确定 | 已接受 | `DOCS/04-design/DESIGN.md`、`DOCS/04-design/INTERACTION_DESIGN.md` |
| 重要设计决策已记录 | 已接受 | Phase 4 十份 Active 设计文档 |
| 技术或制作方案足以支持任务拆解 | 已接受 | `DOCS/04-design/TECHNICAL_DESIGN.md`、`DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`、`DOCS/04-design/PROJECT_STATE_DESIGN.md`、`DOCS/04-design/TEMPLATE_DEPOSITION_DESIGN.md` |

Phase 4 设计已满足进入 Phase 5 的设计条件；阶段切换前仍需先完成 Architecture Decisions 重构与 Maker 接受。

## 8. 下一步

下一步优先处理 `SPECS/ARCHITECTURE_DECISIONS.md` 的内容审计与结构重构。该重构经 Maker 接受后，再执行 Phase 4 到 Phase 5 的阶段切换检查。

## 9. 当前权威文档集合

| 内容类别 | 权威路径 | 状态 | 本轮读取要求 |
| --- | --- | --- | --- |
| 项目入口 | `README.md` | Active | Maker 初次进入时读取 |
| Agent 启动协议 | `AGENTS.md` | Active | 启动时必读 |
| 当前项目状态 | `DOCS/PROJECT_STATE.md` | Active | 启动时必读 |
| 上游阶段想法 | `DOCS/00-idea/IDEA.md` | Active | Phase 4 按需读取 |
| Phase 1 项目意图 | `DOCS/01-intent/INTENT.md` | Active | Phase 4 必读 |
| Phase 1 项目画像 | `DOCS/01-intent/PROJECT_PROFILE.md` | Active | Phase 4 必读 |
| Phase 2 问题定义 | `DOCS/02-explore/PROBLEM.md` | Active | Phase 4 必读 |
| Phase 2 轻量研究 | `DOCS/02-explore/RESEARCH.md` | Active | Phase 4 必读 |
| Phase 3 轻量验证计划 | `DOCS/03-validate/VALIDATION_PLAN.md` | Active | Phase 4 必读 |
| Phase 4 范围设计 | `DOCS/04-design/SCOPE.md` | Active | Phase 4 必读 |
| Phase 4 流程设计 | `DOCS/04-design/DESIGN.md` | Active | Phase 4 必读 |
| Phase 4 协作交互设计 | `DOCS/04-design/INTERACTION_DESIGN.md` | Active | Phase 4 必读 |
| Phase 4 Agent 运行协议设计 | `DOCS/04-design/AGENT_PROTOCOL_DESIGN.md` | Active | Phase 4 必读 |
| Phase 4 文档写回设计 | `DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md` | Active | Phase 4 必读 |
| Phase 4 Skill 形态设计 | `DOCS/04-design/SKILL_DESIGN.md` | Active | Phase 4 必读 |
| Phase 4 项目状态入口设计 | `DOCS/04-design/PROJECT_STATE_DESIGN.md` | Active | Phase 4 必读 |
| Phase 4 技术方案设计 | `DOCS/04-design/TECHNICAL_DESIGN.md` | Active | Phase 4 必读 |
| Phase 4 架构决策文档设计 | `DOCS/04-design/ARCHITECTURE_DECISION_DESIGN.md` | Active | Phase 4 必读 |
| Phase 4 模板沉淀机制设计 | `DOCS/04-design/TEMPLATE_DEPOSITION_DESIGN.md` | Active | Phase 4 必读 |
| 架构决策 | `SPECS/ARCHITECTURE_DECISIONS.md` | Active | 启动时必读 |
| 设计背景 | `SPECS/PROJECT_INCUBATOR_DESIGN_SPEC.md` | Active | 修改 Framework 或设计输入时必读 |
| Phase 规则 | `FRAMEWORK/Phase-System.md` | Active | 读取当前 Phase 章节 |
| 角色规则 | `FRAMEWORK/Role-System.md` | Active | 读取当前角色章节 |
| 文档规则 | `FRAMEWORK/Document-System.md` | Active | 创建、移动或更新文档时必读 |
| Skill 规范 | `FRAMEWORK/Codex-Skill-Specification.md` | Draft | 讨论 Skill 化时必读 |
| Skill 目录状态 | `SKILL/README.md` | Active | 准备 Skill 实现前读取 |
| 通用文档元数据模板 | `TEMPLATES/DOCUMENT-METADATA.template.md` | Draft | 创建权威项目文档时读取 |
| Maker 任务启动 Prompt 模板 | `TEMPLATES/MAKER-TASK-PROMPT.template.md` | Draft | Maker 发起新任务时按需使用 |

## 10. 下一会话恢复入口

下一会话必须从 `AGENTS.md` 开始，随后读取本文件，再读取上表中标记为启动时必读、当前 Phase 必读或本轮按需读取的文档。

恢复后的第一项工作是以 Workflow Designer 身份，处理 `SPECS/ARCHITECTURE_DECISIONS.md` 的内容审计与结构重构，并对照 `DOCS/04-design/ARCHITECTURE_DECISION_DESIGN.md` 保持结构一致。不得直接进入 Phase 5、开发或 Skill 固化；Architecture Decisions 重构经 Maker 接受后，再执行 Phase 4 到 Phase 5 的阶段切换检查。`DOCS/03-validate/VALIDATION_RESULTS.md` 保留为 Phase 7 后的回收事项。

新会话在状态恢复和只读报告阶段不创建分支；如需写入，Agent 应先确认符合当前任务范围的工作分支，再进行文档修改。

如果新会话发现当前工作区、未推送提交或任务分支尚未闭环，必须先提醒 Maker 处理上一任务，不得直接开始新的写入任务。
