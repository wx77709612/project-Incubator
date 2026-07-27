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
| 最后更新 | 2026-07-27 |

## 1. 基本状态

| 字段 | 当前值 |
| --- | --- |
| 项目名称 | Project Incubator |
| Maker | 当前项目的人类所有者，即正在与 AI 协作的用户 |
| 项目状态 | Active |
| 当前 Phase | Phase 5 — Planning（基于 gate router 设计继续拆解） |
| 当前 AI 角色 | Delivery Planner / Engineering Lead（交付规划与工程拆解） |
| 当前主要目标 | 基于已接受的 `DOCS/04-design/GATE_EXECUTION_DESIGN.md` gate router 版本，重拆 Project Incubator Skill 1.0 的 R2 结构化 gate 执行机制与 R3 Builder 交接闭环，使后续 Build 任务具备明确输入、输出、阻断规则和验证样例。 |
| 当前阶段交付物 | Phase 4 设计输入：`DOCS/04-design/GATE_EXECUTION_DESIGN.md` 已转为 Active；当前 Phase 5 需继续拆解：`DOCS/05-planning/ROADMAP.md`、`DOCS/05-planning/MILESTONES.md`、`DOCS/05-planning/VERIFICATION_PLAN.md` 与 R2 / R3 Ticket；P6 可改进 Skill Draft 基线：`p6/skill-minimal-entry` 分支上的 `SKILL/SKILL.md`、`SKILL/references/`、`SKILL/assets/templates/` 等承载物，其主流程可复用，但 gate 执行机制必须升级。 |
| 当前任务状态 | Ready for Maker Review（Maker 已确认按当前 gate router 版本继续后续流程；本轮已把 Phase 5 Planning 从“待修订标记”推进为当前可执行拆解基线。Maker 审阅前不提交、不推送、不合并。） |
| 稳定分支 | `main` |
| 工作分支规则 | `p<当前Phase>/<type>-<topic>`；实际分支由 Git 状态确认 |
| 下一项决定 | Maker 审阅 Phase 5 拆解 Diff，并确认：R2 是否已正确拆成 gate router / gate schema / gate registry / gate case；R3 是否正确消费 `GATE_BUILDER_HANDOFF`；当前 Planning 是否足以进入下一轮 Build 任务。 |
| 最近更新时间 | 2026-07-27 |

## 2. 当前阶段说明

Project Incubator 本身是一个正在使用自身 Framework 孵化的项目。

项目已完成 Phase 0、Phase 1、Phase 2 与轻量 Phase 3 的退出判断。Maker 已于 2026-07-22 确认首轮自用验证已经足够支持 Phase 3 的退出判断，并决定进入 Phase 4 — Design。

Phase 3 仅验证自用价值，不接触外部用户，不进行市场、付费或重型商业验证。`VALIDATION_RESULTS.md` 暂不创建空文档；Maker 建议将其作为后续回收事项，在完成 Phase 7 后收束补齐。

Phase 4 已完成 Project Incubator Skill 1.0 的完整流程设计。Maker 已接受 Phase 4 十份设计交付物，并接受 `SPECS/ARCHITECTURE_DECISIONS.md` 从过程型 Decision 收敛为 AI 越界防护清单。Maker 已批准进入 Phase 5 — Planning。

Phase 5 的首批 Planning 交付物已经完成并经 Maker 接受，Git 里程碑闭环已同步到 `main` / `origin/main`。项目已进入 Phase 6 — Build。

Phase 6 的第一轮 Skill Draft 构建暴露出关键设计缺口：当前 Skill Draft 的主运行链路、入口分流、项目接入和文档写回方向有效，但其中的自然语言 gate references 只能描述门槛和流程，不能像代码 `if / else` 一样强制保证每一个关键门槛百分之百命中。Maker 已明确确认，Skill 1.0 必须让门槛命中 / 未命中具备非黑即白结果；因此当前 Phase 6 Build Draft 应视为可改进基线，而不是最终可验收版本。

项目已完成 Phase 4 — Design 的受控修订输入：新增 `DOCS/04-design/GATE_EXECUTION_DESIGN.md`，并将相关 Phase 4 设计文档挂接到结构化 gate 执行机制。Maker 已确认按当前 gate router 版本继续后续流程；因此当前工作回到 Phase 5 — Planning，将 R2 结构化 gate 执行机制与 R3 Builder 交接闭环重拆为可执行、可验证、可交接的 Build 任务。当前 `p6/skill-minimal-entry` 分支保留为 P6 可改进 Skill Draft 基线；下一轮 Build 应在保留其有效主流程的前提下增量加入结构化 gate 执行承载。

## 3. 当前 AI 协作契约

当前 AI 应以 Delivery Planner / Engineering Lead 身份工作：

- 基于 `DOCS/04-design/GATE_EXECUTION_DESIGN.md` 的 gate router 版本继续 Phase 5 拆解；
- 将 R2 从自然语言硬性门槛矩阵重拆为 gate router、gate schema、gate registry / config、gate case 和必要检查器判断；
- 将 R3 Builder 交接与返回复核改为消费结构化 gate 输出，而不是独立自然语言清单；
- 明确后续 Build 应在 P6 Skill Draft 有效主流程上增量实现当前 Planning 拆出的结构化 gate 承载；
- 保留当前 `p6/skill-minimal-entry` 作为可改进 Skill Draft 基线；是否直接续作该分支或另起 P6 gate 分支，应由 Maker 在 checkpoint 后确认。

当前 AI 不应：

- 把当前自然语言 gate references 视为 Skill 1.0 最终可验收的 gate 承载；
- 直接在当前 `p6/skill-minimal-entry` 分支上修改 Phase 4 / Phase 5 设计内容；
- 未经当前 Planning 拆解与 Maker 审阅，直接实现 gate 脚本、安装流程、发布流程或完整自动化；
- 改变 Maker 决策权、项目类型、公开发布或商业化边界；
- 删除当前 P6 Skill Draft 基线分支或执行未授权远端操作。

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
- R1-R3 闭环后的续作已补充 Maker 任务 Prompt 生成卫生规则：`SKILL/references/task-type-and-writeback.md` 定义 Prompt 外说明 / Prompt 正文拆分、正文白名单 / 黑名单和失败重写流程；`SKILL/references/gate-response-and-authorization.md` 定义 Prompt 搬运门槛、授权不足示例和验证场景。对应 Git 闭环已完成并同步到 `main` / `origin/main` 的稳定检查点。
- 当前已新增 Draft Skill 入口 `SKILL/SKILL.md`，负责自然语言触发描述、入口判断、启动分支、渐进路由和引用既有 references；其正文已按本地 `AGENTS.md` 的默认中文规则修正。入口已收敛为按目标项目状态选择四类入口：新想法或新项目孵化、既有非 Project Incubator 项目接入、已接入项目恢复或续作、Project Incubator 自身维护。
- 当前已新增 `SKILL/references/project-intake-and-initialization.md`，定义新项目启动、既有非 Project Incubator 项目接入、已接入项目恢复的入口判定、模板实例化、目录创建和停止条件。
- 当前已新增 Draft 生产启动模板 `SKILL/assets/templates/AGENTS.template.md`、`SKILL/assets/templates/PROJECT_STATE.template.md` 与 `SKILL/assets/templates/DOCUMENT-METADATA.template.md`，用于未来目标项目在 Maker 授权后生成本地 Agent 协议、状态入口和 `DOCS/<phase>/` 权威项目文档元数据；模板使用占位字段，不复制当前 Project Incubator 的状态事实。
- 当前已在 `SKILL/SKILL.md`、`SKILL/references/project-intake-and-initialization.md` 与 `SKILL/references/main-runtime-chain.md` 中澄清三类路径域：目标项目路径、Skill 资产路径、当前 Project Incubator 仓库路径；`SKILL/references/` 已去除项目文档式“文档状态”表或轻量元数据块，统一改为运行时 Skill reference 头部，并明确不实例化为目标项目文件；Maker 已认可 `SKILL/assets/templates/` 作为生产启动模板承载目录。会实例化到目标项目 `DOCS/` 下的模板必须保留或生成 `## 文档状态` 元数据表；不会实例化为目标项目 `DOCS/` 权威文档的 Skill 资产不得误套该结构。
- 当前已补入产物承载类型判定与承载类型错位门槛：写入前先判断产物属于项目 Phase 文档、项目状态入口、Skill runtime reference、Skill asset / template、目标项目实例文件、代码 / 脚本 / 配置或 Prompt 正文，再选择路径域和适用写法；不得把当前项目 Phase 文档结构、文档状态表或状态入口规则套到 Skill runtime reference、不会实例化为目标项目 `DOCS/` 权威文档的 Skill asset / template、代码、配置或 Prompt 正文。该规则已进入任务类型判定、硬性门槛矩阵、门槛回应授权、Builder 交接前检查和 Builder 返回复核。
- 当前已定点修正 `SKILL/references/main-runtime-chain.md` 与 `SKILL/references/hard-gate-matrix.md`，使主运行链路和门槛矩阵承认未接入项目应走初始化 / 接入流程，而不是读取不存在的本地协议。
- 当前已在 `SKILL/references/hard-gate-matrix.md` 与 `SKILL/references/gate-response-and-authorization.md` 中补入本地协议与输出约束硬性门槛，要求写入回复、Markdown 正文、Skill 入口、reference、模板、项目文档或其他交付物前，先确认本地协议中的语言、格式、内容承载、读写范围和工具边界。
- 当前已补入质疑回应与非迎合门槛：当 Maker 对方案、解释、规则或 Skill 设计提出质疑时，AI 必须先从“合理时如何改”和“不合理时为什么不改”两面判断，再决定是否修改；不得为了迎合质疑直接改写协作方式、门槛或长期规则。
- Maker 已在 2026-07-27 明确确认：Skill 1.0 的门槛机制不能只依赖自然语言描述；每一个关键门槛必须具备结构化、可验证、非黑即白的命中 / 未命中结果。当前 `p6/skill-minimal-entry` 分支上的 Skill Draft 主流程可复用，但 gate 执行机制需要升级；项目已完成 Phase 4 gate 执行设计输入，并按当前 gate router 版本继续 Phase 5 拆解。

### 4.2 当前有效治理基线

- Project Incubator 采用固定状态入口 `DOCS/PROJECT_STATE.md` 与 Phase 目录结合的项目文档结构；
- 权威文档采用所有者 Phase、精确路径引用和受控更新机制，一个事实只维护一个权威来源；
- Agent 启动、恢复、Git 检查、工作分支、Diff 验收门、Maker 手动 Git 闭环和会话结束回写规则以 `AGENTS.md` 为准；
- Maker 任务 Prompt 生成必须先读取 `TEMPLATES/MAKER-TASK-PROMPT.template.md`，Prompt 正文只承载本次任务特有新增内容，不搬运项目状态、已完成历史、权威文档集合或 Git 信息；
- Maker Git 闭环完成回写优先于下一任务 Prompt、Phase 切换或无关新任务；
- 项目与任务采用自适应规划深度，简单、可逆、目标单一的任务不强制创建独立设计文档或实施计划；
- `SKILL/` 当前保留 P6 可改进 Draft 入口、Draft references 和 Draft templates；这些文件的主运行链路、入口分流和项目接入方向可作为后续 Build 基线，但其中自然语言 gate references 需要升级为结构化 gate 执行承载后才可验收。

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
- 已有项目接入流程的后续真实项目验证、阶段推断准确性、文档补全深度和模板实例化体验；
- 自动识别阶段、生成草案和更新状态文档的具体权限分级；
- Project Incubator 的具体实现形态；
- 状态模型的完整字段、状态枚举与版本规则；
- 未来具体项目工作区的位置与创建方式；
- Framework 如何版本化、验证和批准变更；
- 未来 Codex Skill 的权限、安装和发布机制；
- 空 `CHANGELOG.md` 应在什么阶段启用；
- 空 `.agents/` 目录应保留、定义用途还是移除。
- `DOCS/03-validate/VALIDATION_RESULTS.md` 在 Phase 7 后如何收束补齐，以及应记录到什么细度。
- Phase 5 当前拆解是否已经足以支撑后续 Build：R2 是否正确拆成 gate router、gate schema、gate registry / config、gate case 和必要检查器判断；R3 是否正确消费 `GATE_BUILDER_HANDOFF` 与 Builder 返回后的候选 gate；
- gate 机制作为 token 节流机制的验证样例是否充分：是否覆盖短字段路由、跳过无关 gate、命中阻断后停止后续语义扩展和执行消耗；
- 当前 Phase 6 Draft Skill 资产中哪些主流程内容直接复用、哪些 gate reference 内容需要改写为结构化配置 / 检查器，应在下一轮 Build 任务开始前基于 Phase 5 Ticket 决定。

主要项目类型、第一目标用户、边界、非目标、成功标准和推荐流程路径已经在 Phase 1 中确认；其余事项应在适当的后续 Phase 中逐步确认，不在当前阶段一次性解决。

## 6. 当前阻塞项

当前阻塞已从设计缺口转为 Maker 审阅门：`DOCS/04-design/GATE_EXECUTION_DESIGN.md` 已作为 Active 设计输入，Phase 5 文档与 R2 / R3 Ticket 已按 gate router 版本重拆。Maker 审阅并确认 Phase 5 拆解 Diff 前，不进入下一轮 Build；`p6/skill-minimal-entry` 继续保留为可改进 Skill Draft 基线，不删除、不推送、不合并。

## 7. 当前 Exit Criteria 状态

Phase 6 — Build 的 Exit Criteria 不满足；当前 Phase 5 — Planning 正在根据 gate router 设计重拆后续 Build 任务：

| Exit Criteria | 当前状态 | 证据 |
| --- | --- | --- |
| 当前里程碑成果可运行、可查看或可体验 | 部分满足 | 当前 Skill Draft 主流程可查看并可作为后续 Build 基线，但 gate 执行机制尚不能保证百分之百命中 |
| 验收条件已通过 | 不满足 | 已接受的自然语言 reference 验证只证明可描述流程和门槛，不能证明 gate 具有非黑即白命中 / 未命中结果 |
| Maker 已完成必要的手工验证 | 需改进 | Maker 已确认当前主流程没有问题，但门槛机制必须升级为结构化 gate |
| 项目状态文档已更新 | 待 Maker 审阅 | 当前状态入口已记录 Phase 4 gate 设计输入、Phase 5 拆解方向、P6 可改进 Draft 基线处理方式和下一步 Maker 审阅入口 |
| 未解决问题已明确记录 | 待 Maker 审阅 | 当前未解决问题已收敛为 Phase 5 拆解是否充分、gate token 节流验证是否充分、Phase 6 Draft 资产后续取舍 |

Phase 5 — Planning 的既有 Exit Criteria 曾被 Maker 接受，但因 Skill gate 验收目标升级，当前需要重新检查 Phase 5 Planning 是否仍充分，并由 Maker 决定是否进入下一轮 Build。

## 8. 下一步

下一步是 Maker 在 IDE Diff 中审阅本轮 Phase 5 拆解修订。审阅重点是：R2 是否已拆成 gate router / gate schema / gate registry / gate case；gate 输出枚举与阻断规则是否足够非黑即白；router 是否能避免全量执行无关 gate 并减少 token 消耗；是否接受结构化 gate 配置与部分脚本 / 工具检查器作为后续承载；R3 Builder 交接与返回复核是否正确消费结构化 gate 输出。Maker 审阅前不提交、不推送、不合并。

## 9. 当前权威文档集合

| 内容类别 | 权威路径 | 状态 | 本轮读取要求 |
| --- | --- | --- | --- |
| 项目入口 | `README.md` | Active | Maker 初次进入时读取 |
| Agent 启动协议 | `AGENTS.md` | Active | 启动时必读 |
| 当前项目状态 | `DOCS/PROJECT_STATE.md` | Active | 启动时必读 |
| 上游阶段想法 | `DOCS/00-idea/IDEA.md` | Active | Phase 5 按需读取 |
| Phase 1 项目意图 | `DOCS/01-intent/INTENT.md` | Active | Phase 5 按需读取 |
| Phase 1 项目画像 | `DOCS/01-intent/PROJECT_PROFILE.md` | Active | Phase 5 按需读取 |
| Phase 2 问题定义 | `DOCS/02-explore/PROBLEM.md` | Active | Phase 5 按需读取 |
| Phase 2 轻量研究 | `DOCS/02-explore/RESEARCH.md` | Active | Phase 5 按需读取 |
| Phase 3 轻量验证计划 | `DOCS/03-validate/VALIDATION_PLAN.md` | Active | Phase 5 按需读取 |
| Phase 4 范围设计 | `DOCS/04-design/SCOPE.md` | Active | 当前 Phase 5 gate 拆解按需读取 |
| Phase 4 流程设计 | `DOCS/04-design/DESIGN.md` | Active | 当前 Phase 5 gate 拆解按需读取 |
| Phase 4 协作交互设计 | `DOCS/04-design/INTERACTION_DESIGN.md` | Active | 当前 Phase 5 gate 拆解必读 |
| Phase 4 Agent 运行协议设计 | `DOCS/04-design/AGENT_PROTOCOL_DESIGN.md` | Active | 当前 Phase 5 gate 拆解必读 |
| Phase 4 文档写回设计 | `DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md` | Active | 当前 Phase 5 gate 拆解按需读取 |
| Phase 4 Skill 形态设计 | `DOCS/04-design/SKILL_DESIGN.md` | Active | 当前 Phase 5 gate 拆解必读 |
| Phase 4 项目状态入口设计 | `DOCS/04-design/PROJECT_STATE_DESIGN.md` | Active | 当前 Phase 5 gate 拆解按需读取 |
| Phase 4 技术方案设计 | `DOCS/04-design/TECHNICAL_DESIGN.md` | Active | 当前 Phase 5 gate 拆解必读 |
| Phase 4 结构化 gate 执行设计 | `DOCS/04-design/GATE_EXECUTION_DESIGN.md` | Active | 当前 Phase 5 gate router / schema / case 拆解与后续 Phase 6 gate 实现前必读 |
| Phase 4 架构决策文档设计 | `DOCS/04-design/ARCHITECTURE_DECISION_DESIGN.md` | Active | 当前 Phase 5 gate 拆解按需读取 |
| Phase 4 模板沉淀机制设计 | `DOCS/04-design/TEMPLATE_DEPOSITION_DESIGN.md` | Active | 当前 Phase 5 gate 拆解按需读取 |
| Phase 5 路线图 | `DOCS/05-planning/ROADMAP.md` | Active | 当前 Phase 5 gate 拆解必读 |
| Phase 5 里程碑 | `DOCS/05-planning/MILESTONES.md` | Active | 当前 Phase 5 gate 拆解必读 |
| Phase 5 验证计划 | `DOCS/05-planning/VERIFICATION_PLAN.md` | Active | 当前 Phase 5 gate case 拆解必读 |
| Phase 5 任务包 | `DOCS/05-planning/TICKETS/` | Active | 当前 Phase 5 R2 / R3 Ticket 拆解必读 |
| 架构决策 | `SPECS/ARCHITECTURE_DECISIONS.md` | Active | 启动时必读 |
| 设计背景 | `SPECS/PROJECT_INCUBATOR_DESIGN_SPEC.md` | Active | 修改 Framework 或设计输入时必读 |
| Phase 规则 | `FRAMEWORK/Phase-System.md` | Active | 读取当前 Phase 章节 |
| 角色规则 | `FRAMEWORK/Role-System.md` | Active | 读取当前角色章节 |
| 文档规则 | `FRAMEWORK/Document-System.md` | Active | 创建、移动或更新文档时必读 |
| Skill 规范 | `FRAMEWORK/Codex-Skill-Specification.md` | Draft | 后续 Phase 6 准备 Skill 产物时必读 |
| Skill 目录状态 | `SKILL/README.md` | Active | 后续 Phase 6 准备 Skill 产物时必读 |
| Skill 入口正文 | `SKILL/SKILL.md` | Draft | P6 可改进 Draft 基线；后续 Build 前按需读取并增量接入结构化 gate |
| Skill 主运行链路 reference | `SKILL/references/main-runtime-chain.md` | Draft | P6 可改进 Draft 基线；后续 R1 / R2 / R3 Ticket 按需读取并保留有效主流程 |
| Skill 项目接入与初始化 reference | `SKILL/references/project-intake-and-initialization.md` | Draft | 新项目启动、既有非 Project Incubator 项目接入、目录创建或模板实例化任务必读 |
| Skill 任务类型与写回 reference | `SKILL/references/task-type-and-writeback.md` | Draft | R1-02 审阅与后续 R2 / R3 Ticket 按需读取 |
| Skill 硬性门槛矩阵 reference | `SKILL/references/hard-gate-matrix.md` | Draft | 当前本地协议输出约束门槛审阅与后续 R2 / R3 Ticket 按需读取 |
| Skill 门槛回应与授权 reference | `SKILL/references/gate-response-and-authorization.md` | Draft | 当前本地协议冲突回应审阅与后续 R3 Ticket 按需读取 |
| Skill Builder 交接前检查 reference | `SKILL/references/builder-handoff-checklist.md` | Draft | R3-01 审阅与后续 R3 Ticket 按需读取 |
| Skill Builder 返回与审阅 reference | `SKILL/references/builder-return-and-review.md` | Draft | R3-02 审阅与后续 Skill 实现任务按需读取 |
| Skill Agent 运行协议生产模板 | `SKILL/assets/templates/AGENTS.template.md` | Draft | 新项目启动或既有项目接入时按 Maker 授权实例化 |
| Skill 项目状态入口生产模板 | `SKILL/assets/templates/PROJECT_STATE.template.md` | Draft | 新项目启动、既有项目接入或状态入口修复时按 Maker 授权实例化 |
| Skill 项目文档元数据生产模板 | `SKILL/assets/templates/DOCUMENT-METADATA.template.md` | Draft | 目标项目 `DOCS/<phase>/` 权威文档创建或修复时按 Maker 授权实例化 |
| 通用文档元数据模板 | `TEMPLATES/DOCUMENT-METADATA.template.md` | Draft | 创建权威项目文档时读取 |
| Maker 任务启动 Prompt 模板 | `TEMPLATES/MAKER-TASK-PROMPT.template.md` | Draft | Maker 发起新任务时按需使用 |

## 10. 下一会话恢复入口

下一会话必须从 `AGENTS.md` 开始，随后读取本文件，再读取上表中标记为启动时必读、当前 Phase 必读或本轮按需读取的文档。

恢复后的第一项工作是以 Delivery Planner / Engineering Lead 身份继续 Phase 5 拆解审阅：检查当前 checkpoint 分支上的 Diff，重点审阅 `DOCS/05-planning/ROADMAP.md`、`DOCS/05-planning/MILESTONES.md`、`DOCS/05-planning/VERIFICATION_PLAN.md` 与 R2 / R3 Ticket 是否已经按 `DOCS/04-design/GATE_EXECUTION_DESIGN.md` 的 gate router 版本重拆，并确认 `DOCS/PROJECT_STATE.md` 回写是否一致。`p6/skill-minimal-entry` 作为 P6 可改进 Skill Draft 基线保留；后续 Build 可以基于其有效主流程增量接入结构化 gate，但不得把自然语言 gate references 当成最终验收承载。若新会话由上下文完整性门槛触发，必须重新读取权威文件，不得依赖旧聊天压缩摘要判断 Phase、任务范围、Git / Phase / 架构授权或门槛是否解除。`DOCS/03-validate/VALIDATION_RESULTS.md` 保留为 Phase 7 后的回收事项。

新会话在状态恢复和只读报告阶段不创建分支；如需写入，Agent 应先确认符合当前任务范围的工作分支，再进行文档修改。

如果新会话发现当前工作区仍在 `p6/skill-minimal-entry`，应先确认当前任务是继续 P6 gate Build 还是回到 Phase 5 checkpoint 审阅；不得把 Phase 5 拆解修订和 Phase 6 实现改动混在同一个无边界 Diff 中。若发现未提交 Diff、未推送提交或任务分支状态与本状态入口不一致，必须先报告 Maker 决定。
