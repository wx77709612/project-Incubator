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
| 最后更新 | 2026-07-20 |

## 1. 基本状态

| 字段 | 当前值 |
| --- | --- |
| 项目名称 | Project Incubator |
| Maker | 当前项目的人类所有者，即正在与 AI 协作的用户 |
| 项目状态 | Active |
| 当前 Phase | Phase 1 — Intent Discovery |
| 当前 AI 角色 | Project Coach（项目教练） |
| 当前主要目标 | 明确为什么做、为谁做、项目边界以及第一阶段成功标准 |
| 当前阶段交付物 | 待创建：`DOCS/01-intent/INTENT.md`、`DOCS/01-intent/PROJECT_PROFILE.md` |
| 稳定分支 | `main` |
| 工作分支规则 | `p<当前Phase>/<type>-<topic>`；实际分支由 Git 状态确认 |
| 下一项决定 | Maker 对主要项目意图、主要项目类型与第一目标使用者的确认 |
| 最近更新时间 | 2026-07-20 |

## 2. 当前阶段说明

Project Incubator 本身是一个正在使用自身 Framework 孵化的项目。

项目已完成 Phase 0 的三项 Exit Criteria，并由 Maker 明确批准进入 Phase 1。已有设计输入和 Framework 文件仍只是自举所需的初始骨架，不代表 Intent、Explore、Validate 或 Design 已经完成，也不能作为跳过当前阶段工作的依据。

## 3. 当前 AI 协作契约

当前 AI 应以 Project Coach 身份工作：

- 澄清 Maker 为什么做、为谁做以及希望获得什么价值；
- 区分兴趣、个人需求与商业目标；
- 协助确认主要项目类型、边界、非目标和现实约束；
- 帮助 Maker 定义可衡量的第一阶段成功标准；
- 形成 `INTENT.md` 与 `PROJECT_PROFILE.md`，并区分已确认事实与未确认假设。

当前 AI 不应：

- 默认项目需要公开、商业化或市场验证；
- 用市场规模否定 Personal Tool 的个人价值；
- 在意图、边界和成功标准明确前进入设计或开发；
- 未经 Maker 确认自动切换到 Phase 2；
- 把未确认假设写成正式范围或成功标准。

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

## 5. 当前未确认事项

- 主要项目类型的正式确认，以及第一目标用户、边界与非目标；
- Project Incubator 自身的成功标准；
- Personal Tool 的具体形态；
- 状态模型的完整字段、状态枚举与版本规则；
- 未来具体项目工作区的位置与创建方式；
- Framework 如何版本化、验证和批准变更；
- 未来 Codex Skill 的触发方式、权限、安装和发布机制；
- 空 `CHANGELOG.md` 应在什么阶段启用；
- 空 `.agents/` 目录应保留、定义用途还是移除。

主要项目类型、第一目标用户、边界、非目标与成功标准应在 Phase 1 澄清；其余事项应在适当的后续 Phase 中逐步确认，不在当前阶段一次性解决。

## 6. 当前阻塞项

当前没有执行层面或阶段门层面的阻塞。Phase 1 的意图澄清与交付物尚未开始。

## 7. Phase 1 退出检查

| Exit Criteria | 当前状态 | 证据 |
| --- | --- | --- |
| 已明确主要项目意图 | 待澄清 | 待形成 `DOCS/01-intent/INTENT.md` |
| 已确定主要项目类型 | 待 Maker 确认 | 待形成 `DOCS/01-intent/PROJECT_PROFILE.md` |
| 已定义第一阶段成功标准 | 待澄清 | 待形成 `DOCS/01-intent/INTENT.md` |
| 已确定哪些 Phase 可轻量执行或跳过 | 待 Maker 确认 | 待形成 `DOCS/01-intent/PROJECT_PROFILE.md` |

## 8. 下一步

以 Project Coach 身份与 Maker 开展意图澄清，确认主要项目类型、第一目标用户、边界、约束和成功标准，并按需创建 Phase 1 的两份必需交付物。

在 Phase 1 Exit Criteria 获得 Maker 明确确认前，不进入 Phase 2，也不提前开始产品设计或开发。

## 9. 当前权威文档集合

| 内容类别 | 权威路径 | 状态 | 本轮读取要求 |
| --- | --- | --- | --- |
| 项目入口 | `README.md` | Active | Maker 初次进入时读取 |
| Agent 启动协议 | `AGENTS.md` | Active | 启动时必读 |
| 当前项目状态 | `DOCS/PROJECT_STATE.md` | Active | 启动时必读 |
| 上游阶段想法 | `DOCS/00-idea/IDEA.md` | Active | Phase 1 必读 |
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

恢复后的第一项工作是以 Project Coach 身份协助 Maker 澄清主要意图、项目类型、第一目标用户、边界、约束与成功标准，不得提前进入 Phase 2。

新会话在状态恢复和只读报告阶段不创建分支；Maker 确认开始写入后，Agent 应自动创建或确认 `p1/docs-intent-discovery` 工作分支，再进行文档修改。

如果新会话发现当前工作区、未推送提交或任务分支尚未闭环，必须先提醒 Maker 处理上一任务，不得直接开始新的写入任务。
