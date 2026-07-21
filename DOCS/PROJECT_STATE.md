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
| 当前任务状态 | Accepted（Phase 2 里程碑 Diff 已获 Maker 接受，等待 Maker 手动 Git 闭环） |
| 稳定分支 | `main` |
| 工作分支规则 | `p<当前Phase>/<type>-<topic>`；实际分支由 Git 状态确认 |
| 下一项决定 | Maker 先完成当前 `p2/docs-explore-workflow` 里程碑的手动 Git 闭环；闭环后再决定是否进入轻量 Phase 3 — Validate |
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

## 4. 已完成内容

- 已建立 Project Incubator 的总体设计输入；
- 已将同类架构决定合并整理为 Architecture Decisions 001–008；
- 已建立五份 Framework 初始骨架文档；
- 已建立项目级 `AGENTS.md`；
- Maker 已明确 Project Incubator 本身是首个孵化对象；
- Maker 已明确当前处于 Phase 0；
- 已确认项目文档采用固定状态入口与 Phase 目录相结合的结构；
- 已确认权威文档采用所有者 Phase、跨阶段引用和受控更新机制；
- 已建立状态驱动的 Agent 启动协议；
- 已创建 Phase 0 的 `DOCS/00-idea/IDEA.md` 草案；
- 已创建通用文档元数据模板；
- 已创建根目录项目入口 `README.md`；
- 已为保留的 `SKILL/` 目录创建状态说明，当前没有实现 Skill；
- 已将当前 Phase 0 自举文档提交为 Git 基线，提交为 `5b9ff60`，远端为 `origin`；
- 已确认 Git 分支采用 `p<当前Phase>/<type>-<topic>`，并授权 Agent 为后续写入任务自动创建本地工作分支；
- 已确认 Git 任务采用“新任务启动检查 + IDE Diff 人工验收”的双重保证；
- 已确认 Maker 接受 Diff 后，由 Agent 自动完成提交、推送、squash 合并、`main` 推送和已合并分支清理；
- 已将分支规则与任务闭环规则合并为基线治理提交 `3a16a6d`，并推送至 `origin/main`；
- 已确认项目与任务均采用自适应规划深度，简单任务不强制创建设计文档或实施计划；
- 已创建跨 Phase 复用的 Maker 任务启动 Prompt Draft，进入 Phase 0 真实任务验证，尚未提升为稳定模板。
- Maker 已确认 `DOCS/00-idea/IDEA.md` 中的一句话想法准确；
- Maker 已确认想法产生原因来自当前正在进行的真实经历；
- Maker 已确认 Project Incubator 自身是首个具体、真实的使用场景。
- Phase 0 的三项 Exit Criteria 已全部满足；
- Maker 已明确批准进入 Phase 1 — Intent Discovery；
- `DOCS/00-idea/IDEA.md` 已完成 Phase 0 审核并转为 Active。
- Maker 已确认：验收 IDE Diff 后，暂存、提交、推送、合并和分支清理由 Maker 本人执行；Agent 负责重新验证并提供当前任务专用的手动 Git 闭环命令。
- 已完成 Phase 1 意图澄清；Maker 已接受 `DOCS/01-intent/INTENT.md` 与 `DOCS/01-intent/PROJECT_PROFILE.md`，两份文档现为 Active。
- Phase 1 的四项退出条件已满足；Maker 已明确批准进入 Phase 2 — Explore。
- Maker 已确认：Maker 新任务 Prompt 模板未被 Agent 强制消费，是需要在 Phase 2 研究的真实工作流治理问题；当前只记录问题，不提前决定解决机制。
- Maker 已确认：Git 闭环以 Phase 内有意义的里程碑为单位，而非每次消息或状态更新；对应治理规则已更新并进入当前基线。
- Maker 已描述 Phase 2 真实工作流痛点：从新想法到 AI 协作通常会经历实现讨论、现有方案讨论、可行性讨论、AI 代码生成、人肉测试、发现问题、解决问题并继续分叉出新问题；分叉也可能来自 Maker 在与 AI 对话过程中受到启发而产生的新想法；最痛苦和最耗时的是问题解决或新想法展开过程不断分叉，导致上下文变长、token 与时间成本上涨、AI 丢失主线并跑偏。
- Maker 已确认 Phase 2 外部轻量研究的目的不是完整产品或竞品研究，而是补充识别其他人在相似项目孵化、点子推进和 AI 协作工作流中遇到的普遍痛点，以判断 Maker 是否也遇到但尚未提及。
- Maker 已确认 Phase 2 当前写入重点应先钉住问题，而不是提前设计解决方案。
- Maker 已审阅并确认：`DOCS/02-explore/PROBLEM.md` 中的核心问题描述准确；`DOCS/02-explore/RESEARCH.md` 中外部痛点与 Maker 真实体验的对应关系准确；当前最重要假设没有明显过早、过窄或遗漏的问题。
- Maker 已确认 Phase 2 两份草案不需要继续修改；`DOCS/02-explore/PROBLEM.md` 与 `DOCS/02-explore/RESEARCH.md` 已转为 Active。
- Maker 已确认 Project Incubator 与市面项目 / Issue / Agent 协作平台的关键差异：后者更偏团队协作，通常围绕多人任务分配、评审、路线图和组织状态同步；Project Incubator 当前面向 indie developer / solo maker，重点是个人主线保护、AI 协作分叉治理、上下文恢复和个人验收。
- Maker 已批准 Phase 2 完成，并确认当前 `p2/docs-explore-workflow` Diff 作为 Phase 2 里程碑闭环。

## 5. 当前未确认事项

- Maker 新任务 Prompt 模板如何成为 Agent 的强制消费入口，避免 AI 自由扩写 Prompt、重复项目状态或增加 Maker 负担；
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

当前没有执行层面或阶段门层面的阻塞。Phase 2 的两份必需交付物已获 Maker 接受并转为 Active，等待 Maker 作出下一步阶段决定。

## 7. Phase 2 退出检查

| Exit Criteria | 当前状态 | 证据 |
| --- | --- | --- |
| 已清晰描述核心问题 | 已满足 | `DOCS/02-explore/PROBLEM.md` 已获 Maker 确认并转为 Active |
| 已理解当前解决方式 | 已满足 | `DOCS/02-explore/RESEARCH.md` 已获 Maker 确认并转为 Active |
| 已确认自行构建的必要性 | 已满足 | `DOCS/02-explore/RESEARCH.md` 已获 Maker 确认并转为 Active |
| 已识别最重要的假设 | 已满足 | `DOCS/02-explore/RESEARCH.md` 已获 Maker 确认并转为 Active |

## 8. 下一步

以 Product Researcher 身份，协助 Maker 完成当前 `p2/docs-explore-workflow` 里程碑的手动 Git 闭环；闭环完成并回到同步干净的 `main` 后，再决定是否进入轻量 Phase 3 — Validate。

在当前里程碑完成 Git 闭环前，不进入 Phase 3，也不提前开始产品设计或开发。

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

下一会话必须从 `AGENTS.md` 开始，随后读取本文件，再读取上表中标记为启动时必读或 Phase 1 必读的文档。

恢复后的第一项工作是以 Product Researcher 身份，协助 Maker 完成 `p2/docs-explore-workflow` 里程碑的手动 Git 闭环；闭环完成并回到同步干净的 `main` 后，再决定是否进入轻量 Phase 3 — Validate。

新会话在状态恢复和只读报告阶段不创建分支；Maker 确认开始写入后，Agent 应自动创建或确认符合当前任务范围的 `p2/<type>-<topic>` 工作分支，再进行文档修改。

如果新会话发现当前工作区、未推送提交或任务分支尚未闭环，必须先提醒 Maker 处理上一任务，不得直接开始新的写入任务。
