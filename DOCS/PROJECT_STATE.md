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
| 当前 Phase | Phase 0 — Idea Capture |
| 当前 AI 角色 | Idea Facilitator（创意引导者） |
| 当前主要目标 | 捕获并确认 Project Incubator 的原始想法、触发原因和真实使用场景 |
| 当前阶段交付物 | `DOCS/00-idea/IDEA.md` |
| 下一项决定 | Maker 是否确认 `IDEA.md` 已准确表达一句话想法、产生原因和至少一个真实场景 |
| 最近更新时间 | 2026-07-20 |

## 2. 当前阶段说明

Project Incubator 本身是一个正在使用自身 Framework 孵化的项目。

项目当前正式处于 Phase 0，而不是 Phase 4。已有设计输入和 Framework 文件是自举所需的初始骨架，不代表 Intent、Explore、Validate 或 Design 已经完成，也不能作为跳过前序阶段的依据。

## 3. 当前 AI 协作契约

当前 AI 应以 Idea Facilitator 身份工作：

- 帮助 Maker 描述并提炼想法；
- 区分已确认事实、初步方案和未确认假设；
- 识别真实触发场景；
- 将零散信息同步到 `DOCS/00-idea/IDEA.md`；
- 以理解、复述和澄清为主。

当前 AI 不应：

- 把 Framework 骨架视为最终定稿；
- 直接进入产品设计、任务规划、开发或 Skill 实现；
- 过早确定技术栈、商业模式或完整功能范围；
- 未经 Maker 确认自动切换到 Phase 1；
- 把未确认假设写成正式需求或架构决策。

## 4. 已完成内容

- 已建立 Project Incubator 的总体设计输入；
- 已记录 Architecture Decisions 001–009；
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
- 已为保留的 `SKILL/` 目录创建状态说明，当前没有实现 Skill。

## 5. 当前未确认事项

- 一句话想法是否准确表达 Maker 的真实意图；
- 最初触发 Project Incubator 的具体个人经历或高频场景；
- 第一目标用户、边界与非目标；
- Project Incubator 自身的成功标准；
- Personal Tool 的具体形态；
- 首个用于验证孵化流程的真实场景；
- 状态模型的完整字段、状态枚举与版本规则；
- 未来具体项目工作区的位置与创建方式；
- Framework 如何版本化、验证和批准变更；
- 未来 Codex Skill 的触发方式、权限、安装和发布机制；
- 空 `CHANGELOG.md` 应在什么阶段启用；
- 空 `.agents/` 目录应保留、定义用途还是移除。

前三项与 Phase 0 退出及 Phase 1 启动直接相关；其余事项应在适当的后续 Phase 中逐步确认，不在 Phase 0 一次性解决。

## 6. 当前阻塞项

当前没有执行层面的技术阻塞。

阶段推进的唯一阻塞是 Maker 尚未确认 `DOCS/00-idea/IDEA.md` 是否准确反映原始想法、触发原因和真实使用场景。

## 7. Phase 0 退出检查

| Exit Criteria | 当前状态 | 证据 |
| --- | --- | --- |
| 能用一句话描述想法 | 待 Maker 确认 | `DOCS/00-idea/IDEA.md` 第 2 节 |
| 能说明为什么产生这个想法 | 待 Maker 确认 | `DOCS/00-idea/IDEA.md` 第 3、4 节 |
| 能识别至少一个真实使用场景 | 待 Maker 确认 | `DOCS/00-idea/IDEA.md` 第 3 节 |

## 8. 下一步

由 Maker 审阅 `DOCS/00-idea/IDEA.md`，指出不准确、缺失或需要删除的内容。

如果三项 Exit Criteria 均获得 Maker 明确确认，则更新本文件并由 Maker 决定进入 Phase 1 — Intent Discovery。确认前继续保持 Phase 0。

## 9. 当前权威文档集合

| 内容类别 | 权威路径 | 状态 | 本轮读取要求 |
| --- | --- | --- | --- |
| 项目入口 | `README.md` | Active | Maker 初次进入时读取 |
| Agent 启动协议 | `AGENTS.md` | Active | 启动时必读 |
| 当前项目状态 | `DOCS/PROJECT_STATE.md` | Active | 启动时必读 |
| 当前阶段想法 | `DOCS/00-idea/IDEA.md` | Draft | Phase 0 必读 |
| 架构决策 | `SPECS/ARCHITECTURE_DECISIONS.md` | Active | 启动时必读 |
| 设计背景 | `SPECS/PROJECT_INCUBATOR_DESIGN_SPEC.md` | Active | 修改 Framework 或设计输入时必读 |
| Phase 规则 | `FRAMEWORK/Phase-System.md` | Active | 读取当前 Phase 章节 |
| 角色规则 | `FRAMEWORK/Role-System.md` | Active | 读取当前角色章节 |
| 文档规则 | `FRAMEWORK/Document-System.md` | Active | 创建、移动或更新文档时必读 |
| Skill 规范 | `FRAMEWORK/Codex-Skill-Specification.md` | Draft | 讨论 Skill 化时必读 |
| Skill 目录状态 | `SKILL/README.md` | Active | 准备 Skill 实现前读取 |
| 通用文档元数据模板 | `TEMPLATES/DOCUMENT-METADATA.template.md` | Draft | 创建权威项目文档时读取 |

## 10. 下一会话恢复入口

下一会话必须从 `AGENTS.md` 开始，随后读取本文件，再读取上表中标记为启动时必读或 Phase 0 必读的文档。

恢复后的第一项工作是继续以 Idea Facilitator 身份协助 Maker 审阅 `DOCS/00-idea/IDEA.md`，不得自动进入 Phase 1。
