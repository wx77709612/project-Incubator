# Project Incubator Research

> Phase 2 — Explore 的轻量研究草案

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 2 — Explore |
| 文档状态 | Active |
| 权威范围 | Project Incubator 当前替代方式、外部相似痛点、可借鉴实践、自行构建必要性与关键假设 |
| 消费 Phase | Phase 2–9，按需读取 |
| 更新条件 | Maker 补充替代方式、外部参考、关键假设、自行构建必要性或研究结论 |
| 依赖文档 | `DOCS/02-explore/PROBLEM.md`、`DOCS/01-intent/INTENT.md`、`DOCS/01-intent/PROJECT_PROFILE.md`、`DOCS/PROJECT_STATE.md` |
| 最后更新 | 2026-07-21 |

## 1. 文档职责

本文档记录 Phase 2 对 Project Incubator 当前替代方式和外部相似痛点的轻量研究。

本文档不做完整市场规模、竞品矩阵、商业验证或产品功能设计。外部资料只用于帮助 Maker 补漏：识别其他人在相似 AI 协作、项目孵化和点子推进过程中遇到的常见工作流问题，并判断这些问题是否也出现在 Maker 的真实体验中。

## 2. 当前替代方式

Maker 过去没有稳定方式管理 Prompt、项目状态、项目文档和 Git。

当前正在 Project Incubator 内部逐步建立替代方式：

- 使用 `TEMPLATES/` 管理未来可能复用的模板；
- 使用 `TEMPLATES/MAKER-TASK-PROMPT.template.md` 作为 Maker 新任务 Prompt 管理的候选入口；
- 使用 `DOCS/PROJECT_STATE.md` 作为项目状态恢复入口；
- 使用 Phase 目录保存阶段交付物；
- 使用 `AGENTS.md` 约束 AI Agent 的启动、执行、Git 和收尾行为；
- 使用 Git 管理项目变更，并采用 Phase 感知的工作分支与 Maker Diff 验收规则。

这些机制已经开始使用，但仍在真实验证中。尤其是 Maker 新任务 Prompt 模板尚未成为 Agent 的强制消费入口，仍可能出现 AI 自由扩写任务、重复状态或增加 Maker 负担的问题。

## 3. 外部相似痛点

### 3.1 上下文漂移

外部 AI 编程实践中，一个反复出现的问题是：长会话会让 AI 逐渐偏离项目特定上下文，开始给出泛化建议，忽略已有工具、规则或决定。

这与 Maker 当前体验高度一致：问题分叉越多，对话越长，AI 越容易丢失主线。

可借鉴方向包括：

- 为项目维护可重读的结构化说明；
- 切换无关任务时开启新会话或新任务；
- 让 AI 在关键节点重新读取权威文件；
- 压缩或清理不再相关的上下文；
- 把任务状态从聊天迁移到文档。

参考：

- VS Code Docs: [Best practices for using AI in VS Code](https://code.visualstudio.com/docs/agents/best-practices)
- GitHub Docs: [Optimizing your AI usage to maximize efficiency and reduce cost](https://docs.github.com/en/copilot/tutorials/optimize-ai-usage)

### 3.2 Prompt 被迫承担系统记录职责

一些 AI Agent 工作流经验指出，当 prompt 同时承担当前对话、任务说明、项目事实库和状态记录时，系统会变得脆弱。更稳的方式是把目标、范围、验收标准、状态、产物、阻塞项和交接记录放进可重读的结构化状态。

这与 Project Incubator 当前方向一致：`PROJECT_STATE.md`、Phase 文档、模板和 Git 分支不是额外形式，而是在替 prompt 分担长期记忆和治理职责。

参考：

- Agiflow: [Why AI Coding Agents Lose Context: The Durable State Fix](https://agiflow.io/blog/ai-coding-agents-losing-context)

### 3.3 Scope creep 与功能蔓延

AI 降低实现成本后，也降低了加入新功能、尝试新想法和临时改动的摩擦。对个人项目来说，这会让“顺手做一下”变得更频繁，也让主线更容易被新点子和局部问题拖偏。

这与 Maker 当前体验中的“原主流程叉出去很多内容”一致。

可借鉴方向包括：

- 每次写入前明确本轮范围；
- 把 AI 用于执行，而不是让 AI 自动决定方向；
- 新发现事项先分类，再决定是否立即处理；
- 用验收条件约束“做到什么算完成”。

参考：

- Frostbyte: [How AI coding tools can make scope creep worse](https://getfrostbyte.dev/articles/ai-tools-scope-creep)

### 3.4 任务粒度不适合 Agent

外部 Agentic Coding 实践普遍强调任务拆解：大而模糊的任务容易导致上下文膨胀、输出失焦、难以验证和审阅。更可靠的任务应有清楚边界、验收标准和可验证结果。

这与 Project Incubator 的 Phase、文档和 Git 里程碑机制一致。当前需要进一步确认的是：对于 Maker 的真实工作流，什么粒度的任务最适合交给 AI，什么粒度必须先停在讨论或设计阶段。

参考：

- AI Pattern Book: [Task Decomposition](https://aipatternbook.com/task-decomposition)
- VS Code Docs: [Best practices for using AI in VS Code](https://code.visualstudio.com/docs/agents/best-practices)

### 3.5 理解债

AI 可以快速生成代码和方案，但如果 Maker 没有机会理解关键决策和实现结果，后续调试和取舍会变得更困难。外部讨论中，这类风险有时被称为 comprehension debt。

这与 Maker 的“人肉测试后发现各种问题”有关：如果前序代码、设计和协作决策没有清晰记录，后续问题很难判断源头。

参考：

- TU Delft Research Portal: [Pair Programming With Generative AI](https://research.tudelft.nl/en/publications/pair-programming-with-generative-ai/)
- TechRadar: [The rise of comprehension debt in the age of AI coding](https://www.techradar.com/pro/the-rise-of-comprehension-debt-in-the-age-of-ai-coding)

## 4. 与 Maker 真实体验的对应关系

| 外部常见痛点 | Maker 是否已遇到 | 当前证据 |
| --- | --- | --- |
| 上下文漂移 | 是 | Maker 明确提到上下文越来越多后 AI 丢失上下文、跑偏 |
| Scope creep / 分叉过多 | 是 | Maker 明确提到解决问题时又发现新问题，主流程叉出很多内容 |
| Prompt 缺少治理 | 是 | Maker 过去没有 prompt 管理方式，当前才开始用模板治理 |
| 项目状态难恢复 | 是 | Maker 提到很难还原回最开始的主脉络 |
| Git 管理成本 | 已在 Phase 1 确认 | `INTENT.md` 已记录 Git 管理混乱曾造成追溯或丢失风险 |
| 理解债 | 可能存在 | Maker 提到人肉测试后发现代码、交互和协作问题；是否构成理解债仍需进一步确认 |
| 任务拆解不足 | 可能存在 | 当前流程中会直接从可行性讨论进入代码生成，任务边界可能不够稳定 |

## 5. 可借鉴但尚未设计的机制

以下只是研究观察，不是已批准方案：

- 任务开始前强制读取 Maker 新任务 Prompt 或等价任务入口；
- 每轮任务明确主目标、非目标、验收方式和允许写入范围；
- 将新发现问题分为：立即处理、阻塞主线、记录后续、需要 Maker 决定、拒绝处理；
- 长会话中定期回到 `PROJECT_STATE.md` 与当前 Phase 文档，重建主线；
- 切换无关问题时开新任务或新分支；
- 用 Git Diff 作为 Maker 审阅入口，而不是让聊天记录承担验收职责；
- 把“理解是否充分”也作为某些任务的验收要素，而不只看是否生成了文件或代码。

## 6. 自行构建必要性的当前判断

当前研究支持“有必要继续构建 Project Incubator 的自用工作流治理机制”，理由是：

- Maker 的痛点来自真实、高频、正在发生的 AI 协作过程；
- 现有通用 AI 工具提供上下文管理、会话管理或代码生成能力，但不会自动理解 Maker 当前项目的 Phase、文档权威、Git 验收门和个人协作偏好；
- 现有项目、Issue 或 Agent 协作平台更偏向团队协作场景，通常默认存在多人分工、issue 分配、reviewer、sprint、roadmap、组织权限与团队状态同步；Maker 当前场景更接近 indie developer / solo maker，需要解决的是个人主线保护、AI 启发的新想法分叉、上下文恢复和个人验收，而不是团队成员之间的协同缺位；
- Project Incubator 的目标是 Personal Tool，第一价值不是替代市场产品，而是把 Maker 自己的协作治理规则固定下来；
- 当前已有 `AGENTS.md`、`PROJECT_STATE.md`、Phase 文档、模板和 Git 规则，说明问题已经有一部分自建基础；
- 外部相似痛点验证了问题具有普遍性，但最终价值仍应由 Maker 的自用效果判断。

因此，Project Incubator 与市面团队协作工具的关键差异不是“是否管理任务”，而是“为谁治理任务”。市面工具多在解决团队如何协调任务与交付；Project Incubator 当前要解决的是个人 Maker 如何与 AI 稳定地把点子推进成结果。

## 7. 最重要假设

当前最重要的假设是：

> 如果 Project Incubator 能把主流程、问题分叉、任务入口、状态恢复和 Git 审阅统一进一个轻量治理流程，Maker 与 AI 的协作就能减少跑偏、降低重复上下文成本，并更容易从点子推进到 Maker 认可的阶段性结果。

该假设仍需后续通过真实使用验证。

## 8. 待进一步确认的问题

- Maker 对“问题分叉”的分类是否认可；
- 当前模板入口是否应成为所有新任务的强制入口，还是只在特定任务类型中使用；
- 是否需要独立文档记录问题分叉，还是放入 `PROJECT_STATE.md` / 当前 Phase 文档即可；
- token 和时间成本是否需要量化阈值；
- 对已有项目接入时，是否也使用同一套问题分叉治理；
- Phase 2 是否还需要补充一次更聚焦的外部实践研究，或当前轻量研究已足以进入后续设计。

## 9. Phase 2 退出相关性

本文档主要服务于 Phase 2 的以下退出条件：

- 已理解当前解决方式；
- 已确认自行构建的必要性；
- 已识别最重要的假设。

当前状态：已获 Maker 确认并转为 Active。
