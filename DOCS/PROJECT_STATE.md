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
| 最后更新 | 2026-07-21 |

## 1. 基本状态

| 字段 | 当前值 |
| --- | --- |
| 项目名称 | Project Incubator |
| Maker | 当前项目的人类所有者，即正在与 AI 协作的用户 |
| 项目状态 | Active |
| 当前 Phase | Phase 2 — Explore |
| 当前 AI 角色 | Product Researcher（产品研究员） |
| 当前主要目标 | 基于 Maker 的真实工作流，理解核心问题、当前解决方式与最重要的假设，并确认自行构建的必要性 |
| 当前阶段交付物 | Active：`DOCS/02-explore/PROBLEM.md`、`DOCS/02-explore/RESEARCH.md` |
| 当前任务状态 | Accepted（`p2/governance-state-convergence` Diff 已获 Maker 接受，等待 Maker 手动 Git 闭环） |
| 稳定分支 | `main` |
| 工作分支规则 | `p<当前Phase>/<type>-<topic>`；实际分支由 Git 状态确认 |
| 下一项决定 | Maker 手动闭环 `p2/governance-state-convergence`；闭环完成并回写状态后，再新开任务进入轻量 Phase 3 — Validate |
| 最近更新时间 | 2026-07-21 |

## 2. 当前阶段说明

Project Incubator 本身是一个正在使用自身 Framework 孵化的项目。

项目已完成 Phase 0 与 Phase 1 的退出条件，并由 Maker 明确批准进入 Phase 2。已有设计输入和 Framework 文件仍只是自举所需的初始骨架，不代表 Explore、Validate 或 Design 已经完成，也不能作为跳过当前阶段工作的依据。

## 3. 当前 AI 协作契约

当前 AI 应以 Product Researcher 身份工作：

- 理解 Maker 从点子到结果的真实工作流、使用场景与当前替代方式；
- 区分已被证据支持的问题、Maker 的判断与仍待验证的假设；
- 识别最痛苦或最耗时的环节，以及自行构建的必要性；
- 形成 `PROBLEM.md` 与 `RESEARCH.md`，只开展服务于下一项决定的轻量研究。

当前 AI 不应：

- 对 Personal Tool 强制进行市场规模、竞品或商业验证；
- 未经 Maker 判断，把检索或推断结果当作真实需求；
- 在核心问题、当前解决方式与关键假设未明确前进入设计或开发；
- 因为读取到后续 Phase 内容而自动推进。

## 4. 已完成内容（当前基线）

本节只维护恢复当前项目所需的有效基线，不作为历史流水账。详细经过、旧版本差异和里程碑时间线按需从对应权威文档与 Git 历史读取，不新增默认必读的历史文档或索引文档。

### 4.1 阶段与交付物基线

- Phase 0 — Idea Capture 已完成，`DOCS/00-idea/IDEA.md` 为 Active；
- Phase 1 — Intent Discovery 已完成，`DOCS/01-intent/INTENT.md` 与 `DOCS/01-intent/PROJECT_PROFILE.md` 为 Active；
- Phase 2 — Explore 的必需交付物已获 Maker 接受，`DOCS/02-explore/PROBLEM.md` 与 `DOCS/02-explore/RESEARCH.md` 为 Active；
- Phase 2 的四项 Exit Criteria 均已满足，但 Maker 决定在进入 Phase 3 前先完成状态收敛治理。

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

主要项目类型、第一目标用户、边界、非目标、成功标准和推荐流程路径已经在 Phase 1 中确认；其余事项应在适当的后续 Phase 中逐步确认，不在当前阶段一次性解决。

## 6. 当前阻塞项

当前没有执行层面或阶段门层面的阻塞。Phase 2 的两份必需交付物已获 Maker 接受并转为 Active；Prompt 生成路由规则与 Git 闭环完成回写规则均已完成治理修正并闭环。

进入 Phase 3 前，状态收敛治理 Diff 已获 Maker 接受，等待 Maker 手动 Git 闭环。

## 7. Phase 2 退出检查

| Exit Criteria | 当前状态 | 证据 |
| --- | --- | --- |
| 已清晰描述核心问题 | 已满足 | `DOCS/02-explore/PROBLEM.md` 已获 Maker 确认并转为 Active |
| 已理解当前解决方式 | 已满足 | `DOCS/02-explore/RESEARCH.md` 已获 Maker 确认并转为 Active |
| 已确认自行构建的必要性 | 已满足 | `DOCS/02-explore/RESEARCH.md` 已获 Maker 确认并转为 Active |
| 已识别最重要的假设 | 已满足 | `DOCS/02-explore/RESEARCH.md` 已获 Maker 确认并转为 Active |

## 8. 下一步

等待 Maker 手动闭环 `p2/governance-state-convergence`。闭环完成并回写状态后，再新开任务进入轻量 Phase 3 — Validate。

## 9. 当前权威文档集合

| 内容类别 | 权威路径 | 状态 | 本轮读取要求 |
| --- | --- | --- | --- |
| 项目入口 | `README.md` | Active | Maker 初次进入时读取 |
| Agent 启动协议 | `AGENTS.md` | Active | 启动时必读 |
| 当前项目状态 | `DOCS/PROJECT_STATE.md` | Active | 启动时必读 |
| 上游阶段想法 | `DOCS/00-idea/IDEA.md` | Active | Phase 2 按需读取 |
| Phase 1 项目意图 | `DOCS/01-intent/INTENT.md` | Active | Phase 2 必读 |
| Phase 1 项目画像 | `DOCS/01-intent/PROJECT_PROFILE.md` | Active | Phase 2 必读 |
| Phase 2 问题定义 | `DOCS/02-explore/PROBLEM.md` | Active | Phase 2 必读 |
| Phase 2 轻量研究 | `DOCS/02-explore/RESEARCH.md` | Active | Phase 2 必读 |
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

恢复后的第一项工作是检查 `p2/governance-state-convergence` 是否已完成手动 Git 闭环；若尚未闭环，先协助 Maker 闭环并回写状态。闭环完成后，再新开任务进入轻量 Phase 3 — Validate。

新会话在状态恢复和只读报告阶段不创建分支；Maker 确认开始写入后，Agent 应自动创建或确认符合当前任务范围的 `p2/<type>-<topic>` 工作分支，再进行文档修改。

如果新会话发现当前工作区、未推送提交或任务分支尚未闭环，必须先提醒 Maker 处理上一任务，不得直接开始新的写入任务。
