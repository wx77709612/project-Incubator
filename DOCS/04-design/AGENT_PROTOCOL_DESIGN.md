# Project Incubator Agent Protocol Design

> Phase 4 — Design 的 Agent 运行协议设计

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 4 — Design |
| 文档状态 | Active |
| 权威范围 | `AGENTS.md` 的职责、结构、模板关系、启动协议、读取边界、执行边界、高风险动作门禁、更新门槛与检查方式 |
| 消费 Phase | Phase 4–9，按需读取 |
| 更新条件 | Maker 调整 Agent 启动、恢复、执行、写回、Git 协议、高风险动作门禁、模板关系或与 Skill / Framework / 状态入口的边界 |
| 依赖文档 | `AGENTS.md`、`DOCS/04-design/SKILL_DESIGN.md`、`DOCS/04-design/PROJECT_STATE_DESIGN.md`、`DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md`、`DOCS/04-design/TEMPLATE_DEPOSITION_DESIGN.md`、`DOCS/PROJECT_STATE.md` |
| 最后更新 | 2026-07-23 |

## 1. 文档职责

本文档定义 Project Incubator Skill 1.0 中 Agent 运行协议应如何设计。

`AGENTS.md` 是每个被孵化项目的本地 Agent 运行协议。它负责规定 Agent 进入该项目后如何启动、恢复状态、读取权威文档、建立协作契约、执行修改、处理 Git、写回状态和结束会话。

本文档不直接替代当前仓库的 `AGENTS.md`，也不在 Phase 4 直接生成最终模板文件。最终生产模板应在 Phase 5 拆解并在 Phase 6 实现。

## 2. 定位

`AGENTS.md` 是高频读取、低频修改、高权威的运行协议。

它不是项目状态文档，不保存当前 Phase、当前任务进度、未确认事项或历史过程；这些内容由 `DOCS/PROJECT_STATE.md` 负责。

它不是完整 Framework，不维护所有 Phase、角色和文档规则的正文；这些内容由 `FRAMEWORK/` 或未来 Skill references 负责。

它不是 Skill 的最终 `SKILL.md`；`SKILL.md` 负责让 Codex 知道何时触发和如何使用 Project Incubator Skill，`AGENTS.md` 负责具体项目内的本地执行协议。

## 3. 与模板的关系

未来被 Project Incubator Skill 孵化出的项目应拥有自己的 `AGENTS.md` 和 `DOCS/PROJECT_STATE.md`。

因此，`AGENTS.md` 和 `PROJECT_STATE.md` 都需要生产模板：

- `AGENTS.md` 模板：用于生成新项目的本地 Agent 运行协议；
- `PROJECT_STATE.md` 模板：用于生成新项目的当前状态入口；
- 阶段交付物模板：用于按 Phase 生成项目文档；
- Maker 任务 Prompt 模板：用于 Maker 发起新任务时表达本轮 delta。

模板不是当前项目文档的副本。模板应保留跨项目稳定结构，并通过占位字段承载项目名、Maker、项目类型、目录策略、默认 Phase、默认权威文档集合和 Git 授权边界。

当前 Phase 4 只设计模板应承载的职责、字段和边界。模板文件的创建、命名、放置位置和实例化流程应进入 Phase 5 任务拆解。

## 4. 结构设计

生产版 `AGENTS.md` 应至少覆盖以下结构：

| 结构 | 职责 |
| --- | --- |
| 项目与角色定义 | 定义 Maker、AI Collaborator、AI Builder 和 Maker 决策权 |
| 权威目录 | 说明本项目的状态入口、阶段文档、模板、Skill 资产和架构边界在哪里 |
| 启动顺序 | 规定 Agent 进入项目后的最小必读顺序和停止条件 |
| 本轮协作契约 | 规定执行前必须向 Maker 说明的 Phase、角色、目标、读写范围和验证方式 |
| 文档创建与引用 | 规定权威来源、Phase 目录、模板使用和受控更新 |
| 分叉与冲突处理 | 规定新事项分类、冲突报告和 Maker 决策点 |
| 阶段切换 | 规定 Exit Criteria 检查、Maker 决定和状态回写 |
| 执行规则 | 规定授权范围、修改边界、验证和 Builder 交接 |
| 会话结束与回写 | 规定状态更新、Diff 审阅门和结束前检查 |
| Git 治理 | 规定分支、验收、手动闭环和危险操作边界 |
| 高风险动作门禁 | 规定哪些结果必须先暂停、说明风险、请求明确授权或改为人工执行 |

不同项目可以根据项目类型轻量化某些段落，但不得删除启动、状态恢复、Maker 决策权、写回、Git 安全和阶段切换的核心协议。

## 5. 读取策略

Agent 进入项目时必须先读取本地 `AGENTS.md`，再按该文件指向的状态入口和权威文档集合恢复项目。

读取策略应遵守：

- `AGENTS.md` 提供执行协议，不替代状态入口；
- `PROJECT_STATE.md` 提供当前事实，不替代执行协议；
- `FRAMEWORK/` 或 Skill references 提供通用 Phase / 角色 / 文档规则，不在 `AGENTS.md` 中复制全文；
- `SPECS/ARCHITECTURE_DECISIONS.md` 提供不可静默改变的长期边界；
- 本轮任务只读取当前 Phase 和当前问题需要的文档。

当 `AGENTS.md` 与 `PROJECT_STATE.md`、Framework 或 Architecture Decision 冲突时，Agent 应报告冲突并等待 Maker 决定，不得静默选择更方便的版本。

## 6. 高风险动作门禁

Agent 不应按 Maker 的具体措辞判断是否可以执行高风险动作，而应按该动作可能造成的结果判断是否触发门禁。

只要本轮行动可能造成以下结果之一，就必须进入门禁流程：

- 改变 Git 暂存区、提交历史、分支、远端状态或工作区保存边界；
- 改变项目 Phase、AI 角色、任务状态或 Exit Criteria 状态；
- 改变权威文档状态、权威路径、模板实例化规则或架构边界；
- 把 Maker 的临时表达、AI 建议、协作纠偏或单次限制写成长期规则；
- 扩大当前任务范围、项目类型、发布范围、商业化范围或实现深度；
- 执行破坏性、不可逆、难以审阅或会影响后续恢复的操作；
- 将本应由 Maker 手动完成的验收、Git 闭环或方向性取舍改为 AI 自动执行。

门禁流程如下：

1. 暂停执行；
2. 说明将触发的风险结果；
3. 说明默认安全处理方式，例如只读检查、提供方案、提供手动命令或记录后续；
4. 需要 AI 代为执行时，要求 Maker 明确授权具体动作、范围和目标；
5. 执行前再次检查当前 Phase、分支、Diff 范围、权威文档归属和回滚风险；
6. 执行后报告实际影响和剩余风险。

明确授权必须同时满足：

- Maker 明确要求 AI 代为执行，而不是只表达结果愿望；
- 授权中包含具体动作、目标对象和范围；
- 授权没有与当前 Phase、分支规则、文档权威或 Maker 手动验收边界冲突；
- 执行前检查未发现未闭环任务、无关 Diff、错误分支、状态冲突或不可接受的回滚风险。

里程碑接受、内容确认、继续下一步、建立检查点等表达，只能说明 Maker 对结果或方向的态度，不能自动转化为 AI 执行高风险动作的授权。

Git 写操作属于高风险动作。除非 Maker 明确授权 AI 执行具体 Git 命令，否则 Agent 默认只能提供 Maker 手动闭环命令清单。Agent 不得在 `main` 上为普通任务直接创建提交；需要提交时应按项目分支与 Maker 手动闭环规则处理。若当前分支是 `main` 且动作会产生普通任务提交，Agent 必须停止并转为分支治理或 Maker 手动闭环建议。

## 7. 写入与更新门槛

`AGENTS.md` 的更新门槛高于普通阶段文档。

只有当变化会长期影响以下事项时，才应考虑更新：

- Agent 启动或恢复顺序；
- 状态入口读取方式；
- Maker 决策权或 AI 角色边界；
- 文档创建、引用或写回协议；
- 阶段切换和 Exit Criteria 检查；
- Builder 执行边界；
- Git 分支、Diff 验收或手动闭环；
- 模板实例化后的项目级运行协议。

单次协作偏差、临时提醒、某次执行错误或低复用限制不应写入 `AGENTS.md`。这类事项应先由写回规则资产判断归属。

## 8. 模板实例化规则

未来 `AGENTS.md` 模板生成新项目实例时，应遵守：

- 实例文件必须位于被孵化项目根目录；
- 实例文件必须指向该项目自己的 `DOCS/PROJECT_STATE.md`；
- 实例文件必须说明该项目的文档目录、模板目录和 Skill 资产来源；
- 实例文件必须保留状态写回、文档写回、Diff 审阅和会话结束检查规则；
- 实例文件不得引用当前 Project Incubator 仓库作为默认项目状态来源；
- 实例文件应保留 Maker 决策权、阶段切换、状态回写和 Git 验收门；
- 实例文件应允许项目类型影响轻重，但不得省略安全边界；
- 实例化后，Agent 必须能只凭该项目根目录恢复上下文。

以下字段是模板实例化变量，不是生成后的 `AGENTS.md` 必须长期保留的字段表。实例化时，AI 应用这些变量生成一份可直接执行的本地 `AGENTS.md`，并删除模板说明。

模板实例化变量至少应包括：

| 字段 | 用途 |
| --- | --- |
| 项目名称 | 写入本地项目身份 |
| Maker 定义 | 明确人类所有者与验收者 |
| 项目类型 | 辅助 Phase 4 设计深度和阶段交付物选择 |
| 状态入口路径 | 默认 `DOCS/PROJECT_STATE.md` |
| Phase 文档根目录 | 默认 `DOCS/` |
| 模板来源 | 本地 `TEMPLATES/` 或 Skill assets |
| Skill / Framework 来源 | 说明规则由本地文件、Skill references 或二者共同提供 |
| Git 授权边界 | 说明分支、Diff、提交、推送和合并权限 |
| 写回规则来源 | 说明状态写回、文档写回和写后检查规则由本地协议、Framework 或 Skill references 承载 |

## 9. 与 `PROJECT_STATE.md` 的边界

`AGENTS.md` 决定 Agent 如何工作；`PROJECT_STATE.md` 说明项目现在是什么状态。

边界如下：

| 问题 | 归属 |
| --- | --- |
| Agent 进入项目先读什么 | `AGENTS.md` |
| 当前 Phase 是什么 | `PROJECT_STATE.md` |
| 当前主要目标是什么 | `PROJECT_STATE.md` |
| AI 如何判断是否能写入 | `AGENTS.md` |
| 哪些文档是当前权威文档集合 | `PROJECT_STATE.md` |
| 如何创建或更新文档 | `AGENTS.md` 和文档系统规则 |
| 本轮下一步是什么 | `PROJECT_STATE.md` |
| 会话结束前如何检查 | `AGENTS.md` |

`PROJECT_STATE_DESIGN.md` 应进一步设计状态入口的字段、更新条件、基线收敛和模板结构。

## 10. 与 Skill 实现承载的关系

未来 Skill 化后，`AGENTS.md` 不应无限膨胀为完整 Skill 说明书。

推荐承载关系是：

- `SKILL.md`：触发 Project Incubator Skill，并提供入口级工作流；
- Architecture Decision：保存不可静默改变的长期架构边界；
- Skill references：保存较长的 Phase、角色、文档、Agent 协议和模板规则；
- Skill assets 或项目 `TEMPLATES/`：保存可实例化模板；
- 项目根目录 `AGENTS.md`：保存该项目的本地运行协议；
- 项目 `DOCS/PROJECT_STATE.md`：保存该项目当前状态。

Phase 5 应判断哪些规则保留在项目实例文件中，哪些移动到 Skill references，哪些作为模板资产生成。

## 11. 写后检查

更新 `AGENTS.md` 或其模板设计后，应检查：

- 是否仍只维护 Agent 运行协议；
- 是否把项目状态写入协议文件；
- 是否复制了 Framework 或 Skill reference 的长正文；
- 是否新增了单次纠偏规则；
- 是否遗漏高风险动作门禁；
- 是否改变了 Maker 决策权或 Git 权限；
- 是否同步影响 `PROJECT_STATE.md`、模板设计或 Skill 实现承载设计；
- 新项目是否能通过实例化后的 `AGENTS.md` 和 `PROJECT_STATE.md` 独立恢复。

## 12. Phase 5 输入

Phase 5 可以基于本文档拆解以下任务：

- 设计并创建 `AGENTS.md` 生产模板；
- 设计 `PROJECT_STATE.md` 生产模板，并与 `PROJECT_STATE_DESIGN.md` 对齐；
- 定义新项目实例化流程；
- 拆分 `AGENTS.md` 中应保留在项目本地的内容和应进入 Skill references 的内容；
- 设计高风险动作门禁检查清单；
- 设计 Agent 协议一致性检查清单；
- 设计模板实例化后的最小恢复验证。
