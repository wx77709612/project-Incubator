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
| 最后更新 | 2026-07-25 |

## 1. 基本状态

| 字段 | 当前值 |
| --- | --- |
| 项目名称 | Project Incubator |
| Maker | 当前项目的人类所有者，即正在与 AI 协作的用户 |
| 项目状态 | Active |
| 当前 Phase | Phase 6 — Build |
| 当前 AI 角色 | Engineering Lead（工程负责人） |
| 当前主要目标 | 完成 R1-R3 Git 闭环后的状态回写，并修正 Maker 任务 Prompt 生成卫生规则，确保下一任务 Prompt 正文只承载任务 delta、不搬运项目状态。 |
| 当前阶段交付物 | Draft：`SKILL/references/main-runtime-chain.md`、`SKILL/references/task-type-and-writeback.md`、`SKILL/references/hard-gate-matrix.md`、`SKILL/references/gate-response-and-authorization.md`、`SKILL/references/builder-handoff-checklist.md`、`SKILL/references/builder-return-and-review.md`；上游 Active：Phase 5 首批 Planning 文档、Phase 4 十份设计文档、`SPECS/ARCHITECTURE_DECISIONS.md` |
| 当前任务状态 | Ready for Maker Review（R1-R3 首批 Build reference 里程碑已由 Maker 完成手工 Git 闭环；当前 Diff 为闭环状态回写与 Maker 任务 Prompt 生成卫生规则修正） |
| 稳定分支 | `main` |
| 工作分支规则 | `p<当前Phase>/<type>-<topic>`；实际分支由 Git 状态确认 |
| 下一项决定 | Maker 审阅当前 Prompt 生成卫生规则修正 Diff；接受后再启动 Phase 6 下一项 Build 任务，决定是否产出最小 `SKILL.md` 入口正文或等价 Skill 1.0 最小承载物。 |
| 最近更新时间 | 2026-07-25 |

## 2. 当前阶段说明

Project Incubator 本身是一个正在使用自身 Framework 孵化的项目。

项目已完成 Phase 0、Phase 1、Phase 2 与轻量 Phase 3 的退出判断。Maker 已于 2026-07-22 确认首轮自用验证已经足够支持 Phase 3 的退出判断，并决定进入 Phase 4 — Design。

Phase 3 仅验证自用价值，不接触外部用户，不进行市场、付费或重型商业验证。`VALIDATION_RESULTS.md` 暂不创建空文档；Maker 建议将其作为后续回收事项，在完成 Phase 7 后收束补齐。

Phase 4 已完成 Project Incubator Skill 1.0 的完整流程设计。Maker 已接受 Phase 4 十份设计交付物，并接受 `SPECS/ARCHITECTURE_DECISIONS.md` 从过程型 Decision 收敛为 AI 越界防护清单。Maker 已批准进入 Phase 5 — Planning。

Phase 5 的首批 Planning 交付物已经完成并经 Maker 接受，Git 里程碑闭环已同步到 `main` / `origin/main`。项目已进入 Phase 6 — Build。

Phase 6 的工作不是重新设计 Skill，也不是一次性实现完整 Skill 1.0，而是严格按 Phase 5 已接受的 Ticket 逐步构建真实成果。R1-R3 首批 Build reference 里程碑已完成并合并到 `main` / `origin/main`。当前已形成六份 Draft Skill references：`SKILL/references/main-runtime-chain.md` 定义 Skill 1.0 主运行链路并补入上下文完整性检查，`SKILL/references/task-type-and-writeback.md` 定义任务类型判定、读取粒度、上下文恢复任务、写回触发规则和 Maker 任务 Prompt 生成卫生检查，`SKILL/references/hard-gate-matrix.md` 定义硬性门槛矩阵并补入上下文完整性门槛，`SKILL/references/gate-response-and-authorization.md` 定义门槛触发后的回应结构、Maker 明确授权字段、Prompt 搬运门槛和最小恢复胶囊，`SKILL/references/builder-handoff-checklist.md` 定义 AI Builder 启动前的字段完整性、交接门槛和拒绝交接流程，`SKILL/references/builder-return-and-review.md` 定义 Builder 完成后的报告、Collaborator 回看、Maker Diff 审阅和状态回写判断。

## 3. 当前 AI 协作契约

当前 AI 应以 Engineering Lead 身份工作：

- 按 Phase 5 已接受 Ticket 准备执行上下文，监督 AI Builder 不越过任务边界；
- 检查当前 Draft Skill references 是否符合对应 Ticket、Phase 4 设计和 Phase 5 验证计划；
- 如 Maker 要求修改，在当前工作分支和对应 Ticket 边界内继续；
- 修正 Maker 任务 Prompt 生成卫生规则，防止可复制 Prompt 正文搬运项目状态、Git 历史或权威文档集合；
- 保留 Diff 供 Maker 审阅，并按需更新状态入口。

当前 AI 不应：

- 重新定义项目方向、Phase 目标、成功标准或 Maker 决策权；
- 将完整 Skill 一次性交给 AI Builder；
- 在首个 Build 任务中编写最终 `SKILL.md`、实现脚本或创建模板文件，除非 Ticket 边界经 Maker 明确调整；
- 添加未获 Maker 确认的新功能、公开发布目标、商业化目标或团队协作范围；
- 执行未授权 Git 闭环或跳过 Maker Diff 审阅。

## 4. 已完成内容（当前基线）

本节只维护恢复当前项目所需的有效基线，不作为历史流水账。详细经过、旧版本差异和里程碑时间线按需从对应权威文档与 Git 历史读取，不新增默认必读的历史文档或索引文档。

### 4.1 阶段与交付物基线

- Phase 0 — Idea Capture 已完成，`DOCS/00-idea/IDEA.md` 为 Active；
- Phase 1 — Intent Discovery 已完成，`DOCS/01-intent/INTENT.md` 与 `DOCS/01-intent/PROJECT_PROFILE.md` 为 Active；
- Phase 2 — Explore 的必需交付物已获 Maker 接受，`DOCS/02-explore/PROBLEM.md` 与 `DOCS/02-explore/RESEARCH.md` 为 Active；
- Phase 3 — Validate 已完成轻量退出判断，`DOCS/03-validate/VALIDATION_PLAN.md` 为 Active；`DOCS/03-validate/VALIDATION_RESULTS.md` 暂缓至 Phase 7 后回收补齐；
- Phase 4 — Design 的十份交付物已获 Maker 接受并转为 Active：`DOCS/04-design/SKILL_DESIGN.md`、`DOCS/04-design/SCOPE.md`、`DOCS/04-design/DESIGN.md`、`DOCS/04-design/INTERACTION_DESIGN.md`、`DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`、`DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md`、`DOCS/04-design/PROJECT_STATE_DESIGN.md`、`DOCS/04-design/ARCHITECTURE_DECISION_DESIGN.md`、`DOCS/04-design/TEMPLATE_DEPOSITION_DESIGN.md`、`DOCS/04-design/TECHNICAL_DESIGN.md`。其中 Agent 协议、交互设计和技术设计已纳入高风险结果导向门禁机制；对应 Git 闭环已完成并同步到 `main` / `origin/main` 的稳定检查点。
- `SPECS/ARCHITECTURE_DECISIONS.md` 已获 Maker 接受并从 8 条过程型 Decision 收敛为 5 条 AI 越界防护边界：Maker 决策权与 Phase 边界、文档与状态恢复依据、Framework 与项目实例分离、流程深度自适应、Git 写操作与 Maker 验收门。
- Phase 5 — Planning 的首批交付物已获 Maker 接受并转为 Active：`DOCS/05-planning/ROADMAP.md`、`DOCS/05-planning/MILESTONES.md`、`DOCS/05-planning/VERIFICATION_PLAN.md` 与 6 个 R1-R3 Ticket。对应 Git 闭环已完成并同步到 `main` / `origin/main` 的稳定检查点。
- Maker 已批准从 Phase 5 — Planning 进入 Phase 6 — Build。
- Phase 6 已形成六份 Draft Skill references：`SKILL/references/main-runtime-chain.md` 覆盖启动或恢复、读取本地协议与状态入口、定位 Phase / 角色 / 主目标 / 权威文档集合、上下文完整性检查、协作契约、任务类型判断、Phase 内协作、新事项分类、硬性门槛、文档写回、Maker 审阅、状态入口收敛和下一轮恢复；`SKILL/references/task-type-and-writeback.md` 覆盖任务类型判定、读取粒度、上下文恢复任务、写回触发条件、状态入口收敛和最小恢复胶囊；`SKILL/references/hard-gate-matrix.md` 覆盖 Phase、Git、权威文档、范围、Builder、未闭环任务、上下文完整性、纠偏沉淀和 Architecture Decision 候选写回门槛；`SKILL/references/gate-response-and-authorization.md` 覆盖门槛触发后的标准回应结构、明确授权字段、不足授权示例、安全替代动作、执行前复核和最小恢复胶囊回应；`SKILL/references/builder-handoff-checklist.md` 覆盖 AI Builder 启动前检查清单、可执行边界格式、拒绝交接回应和 R3-01 验证场景；`SKILL/references/builder-return-and-review.md` 覆盖 Builder 返回报告、Collaborator 回看清单、Maker 审阅入口、状态回写判断和 R3-02 验证场景。
- R1-R3 首批 Build reference 里程碑已获 Maker 接受，并由 Maker 完成手工 Git 闭环；稳定检查点为 `5006792 skill: add phase 6 r1-r3 runtime references`，已同步到 `main` / `origin/main`。
- R1-R3 闭环后的续作已补充 Maker 任务 Prompt 生成卫生规则草案：`SKILL/references/task-type-and-writeback.md` 定义 Prompt 外说明 / Prompt 正文拆分、正文白名单 / 黑名单和失败重写流程；`SKILL/references/gate-response-and-authorization.md` 定义 Prompt 搬运门槛、授权不足示例和验证场景。

### 4.2 当前有效治理基线

- Project Incubator 采用固定状态入口 `DOCS/PROJECT_STATE.md` 与 Phase 目录结合的项目文档结构；
- 权威文档采用所有者 Phase、精确路径引用和受控更新机制，一个事实只维护一个权威来源；
- Agent 启动、恢复、Git 检查、工作分支、Diff 验收门、Maker 手动 Git 闭环和会话结束回写规则以 `AGENTS.md` 为准；
- Maker 任务 Prompt 生成必须先读取 `TEMPLATES/MAKER-TASK-PROMPT.template.md`，Prompt 正文只承载本次任务特有新增内容，不搬运项目状态、已完成历史、权威文档集合或 Git 信息；
- Maker Git 闭环完成回写优先于下一任务 Prompt、Phase 切换或无关新任务；
- 项目与任务采用自适应规划深度，简单、可逆、目标单一的任务不强制创建独立设计文档或实施计划；
- `SKILL/` 当前开始承载未来 Skill 1.0 的 Draft reference，但仍不是已实现、已安装或已发布的可执行 Skill。

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
- 下一项 Skill 1.0 最小实现承载任务的精确边界，包括是否创建最终 `SKILL.md` 入口正文、是否仅引用现有 references、以及是否仍禁止脚本和模板实现。

主要项目类型、第一目标用户、边界、非目标、成功标准和推荐流程路径已经在 Phase 1 中确认；其余事项应在适当的后续 Phase 中逐步确认，不在当前阶段一次性解决。

## 6. 当前阻塞项

当前没有设计或阶段层面的阻塞。当前工作分支 `p6/skill-prompt-hygiene` 保留闭环状态回写与 Prompt 生成卫生规则修正 Diff，等待 Maker 审阅；在该 Diff 被接受并完成闭环前，不启动无关新任务。

## 7. 当前 Exit Criteria 状态

Phase 6 — Build 的 Exit Criteria 尚未满足：

| Exit Criteria | 当前状态 | 证据 |
| --- | --- | --- |
| 当前里程碑成果可运行、可查看或可体验 | 部分满足 | R1-R3 六份 Draft Skill references 可查看，并已合并到 `main` / `origin/main` |
| 验收条件已通过 | 部分满足 | R1-01 已检查 S1、S2、S5、S8、S9 映射与非实现边界；R1-02 已检查 S2、S5、文档写入完成、上下文恢复场景与非实现边界；R2-01 已检查 S2、S3、S4、S6、S8、上下文完整性、纠偏沉淀场景与非实现边界；R2-02 已检查 S2、“帮我合并”、“进入下一阶段”、“把这个写进架构决策”、上下文过载场景与非实现边界；R3-01 已检查 S6、缺少验证步骤、范围扩大和可执行 Ticket 场景与非实现边界；R3-02 已检查 S7、验证失败、Diff 等待审阅和状态回写卫生场景与非实现边界；Maker 已接受该里程碑 Diff 并完成 Git 闭环 |
| Maker 已完成必要的手工验证 | 未开始 | 待 Build 产物形成后由 Maker 验收 |
| 项目状态文档已更新 | 部分满足 | R1-R3 里程碑闭环事实与 Prompt 生成卫生规则修正状态已回写到状态入口；当前 Diff 尚未提交 |
| 未解决问题已明确记录 | 部分满足 | 当前未解决问题为下一项最小 Skill 实现承载任务的精确边界 |

Phase 5 — Planning 的 Exit Criteria 已满足并由 Maker 接受，作为 Phase 6 的上游输入继续读取。

## 8. 下一步

下一步由 Maker 审阅当前 Diff。若接受，则先完成本次小修正的 Git 闭环；闭环后再启动 Phase 6 的下一项 Build 任务：产出 Project Incubator Skill 1.0 的最小 `SKILL.md` 入口正文或等价最小承载物；不得重新设计 Phase 5，不得实现脚本或模板，除非 Maker 明确调整任务边界。

## 9. 当前权威文档集合

| 内容类别 | 权威路径 | 状态 | 本轮读取要求 |
| --- | --- | --- | --- |
| 项目入口 | `README.md` | Active | Maker 初次进入时读取 |
| Agent 启动协议 | `AGENTS.md` | Active | 启动时必读 |
| 当前项目状态 | `DOCS/PROJECT_STATE.md` | Active | 启动时必读 |
| 上游阶段想法 | `DOCS/00-idea/IDEA.md` | Active | Phase 4 按需读取 |
| Phase 1 项目意图 | `DOCS/01-intent/INTENT.md` | Active | Phase 6 按需读取 |
| Phase 1 项目画像 | `DOCS/01-intent/PROJECT_PROFILE.md` | Active | Phase 6 按需读取 |
| Phase 2 问题定义 | `DOCS/02-explore/PROBLEM.md` | Active | Phase 6 按需读取 |
| Phase 2 轻量研究 | `DOCS/02-explore/RESEARCH.md` | Active | Phase 6 按需读取 |
| Phase 3 轻量验证计划 | `DOCS/03-validate/VALIDATION_PLAN.md` | Active | Phase 6 按需读取 |
| Phase 4 范围设计 | `DOCS/04-design/SCOPE.md` | Active | Phase 6 按需读取 |
| Phase 4 流程设计 | `DOCS/04-design/DESIGN.md` | Active | Phase 6 必读 |
| Phase 4 协作交互设计 | `DOCS/04-design/INTERACTION_DESIGN.md` | Active | Phase 6 必读 |
| Phase 4 Agent 运行协议设计 | `DOCS/04-design/AGENT_PROTOCOL_DESIGN.md` | Active | Phase 6 必读 |
| Phase 4 文档写回设计 | `DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md` | Active | Phase 6 必读 |
| Phase 4 Skill 形态设计 | `DOCS/04-design/SKILL_DESIGN.md` | Active | Phase 6 必读 |
| Phase 4 项目状态入口设计 | `DOCS/04-design/PROJECT_STATE_DESIGN.md` | Active | Phase 6 按需读取 |
| Phase 4 技术方案设计 | `DOCS/04-design/TECHNICAL_DESIGN.md` | Active | Phase 6 必读 |
| Phase 4 架构决策文档设计 | `DOCS/04-design/ARCHITECTURE_DECISION_DESIGN.md` | Active | Phase 6 按需读取 |
| Phase 4 模板沉淀机制设计 | `DOCS/04-design/TEMPLATE_DEPOSITION_DESIGN.md` | Active | Phase 6 按需读取 |
| Phase 5 路线图 | `DOCS/05-planning/ROADMAP.md` | Active | Phase 6 必读 |
| Phase 5 里程碑 | `DOCS/05-planning/MILESTONES.md` | Active | Phase 6 必读 |
| Phase 5 验证计划 | `DOCS/05-planning/VERIFICATION_PLAN.md` | Active | Phase 6 必读 |
| Phase 5 任务包 | `DOCS/05-planning/TICKETS/` | Active | Phase 6 按需读取；首个任务读取 `TICKET-R1-01-main-runtime-chain.md` |
| 架构决策 | `SPECS/ARCHITECTURE_DECISIONS.md` | Active | 启动时必读 |
| 设计背景 | `SPECS/PROJECT_INCUBATOR_DESIGN_SPEC.md` | Active | 修改 Framework 或设计输入时必读 |
| Phase 规则 | `FRAMEWORK/Phase-System.md` | Active | 读取当前 Phase 章节 |
| 角色规则 | `FRAMEWORK/Role-System.md` | Active | 读取当前角色章节 |
| 文档规则 | `FRAMEWORK/Document-System.md` | Active | 创建、移动或更新文档时必读 |
| Skill 规范 | `FRAMEWORK/Codex-Skill-Specification.md` | Draft | Phase 6 准备 Skill 产物时必读 |
| Skill 目录状态 | `SKILL/README.md` | Active | Phase 6 准备 Skill 产物时必读 |
| Skill 主运行链路 reference | `SKILL/references/main-runtime-chain.md` | Draft | R1-01 审阅与后续 R1 / R2 / R3 Ticket 按需读取 |
| Skill 任务类型与写回 reference | `SKILL/references/task-type-and-writeback.md` | Draft | R1-02 审阅与后续 R2 / R3 Ticket 按需读取 |
| Skill 硬性门槛矩阵 reference | `SKILL/references/hard-gate-matrix.md` | Draft | R2-01 审阅与后续 R2 / R3 Ticket 按需读取 |
| Skill 门槛回应与授权 reference | `SKILL/references/gate-response-and-authorization.md` | Draft | R2-02 审阅与后续 R3 Ticket 按需读取 |
| Skill Builder 交接前检查 reference | `SKILL/references/builder-handoff-checklist.md` | Draft | R3-01 审阅与后续 R3 Ticket 按需读取 |
| Skill Builder 返回与审阅 reference | `SKILL/references/builder-return-and-review.md` | Draft | R3-02 审阅与后续 Skill 实现任务按需读取 |
| 通用文档元数据模板 | `TEMPLATES/DOCUMENT-METADATA.template.md` | Draft | 创建权威项目文档时读取 |
| Maker 任务启动 Prompt 模板 | `TEMPLATES/MAKER-TASK-PROMPT.template.md` | Draft | Maker 发起新任务时按需使用 |

## 10. 下一会话恢复入口

下一会话必须从 `AGENTS.md` 开始，随后读取本文件，再读取上表中标记为启动时必读、当前 Phase 必读或本轮按需读取的文档。

恢复后的第一项工作是以 Engineering Lead 身份审阅或继续当前 `p6/skill-prompt-hygiene` 分支上的 Prompt 生成卫生规则修正 Diff。该 Diff 被 Maker 接受并闭环后，才从干净且同步的 `main` 启动 Phase 6 下一项 Build 任务，确认最小 `SKILL.md` 入口正文或等价最小承载物的任务边界。不得重新设计 Phase 5，不得一次性实现完整 Skill 1.0，不得实现脚本、模板或修改 Architecture Decisions，除非 Maker 明确调整任务边界。若新会话由上下文完整性门槛触发，必须重新读取权威文件，不得依赖旧聊天压缩摘要判断 Phase、任务范围、Git / Phase / 架构授权或门槛是否解除。`DOCS/03-validate/VALIDATION_RESULTS.md` 保留为 Phase 7 后的回收事项。

新会话在状态恢复和只读报告阶段不创建分支；如需写入，Agent 应先确认符合当前任务范围的工作分支，再进行文档修改。

如果新会话发现当前工作区、未推送提交或任务分支尚未闭环，必须先提醒 Maker 处理上一任务，不得直接开始新的写入任务。
