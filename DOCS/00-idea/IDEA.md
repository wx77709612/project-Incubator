# Project Incubator Idea

> Phase 0 — Idea Capture 的当前阶段交付物

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 0 — Idea Capture |
| 文档状态 | Draft |
| 权威范围 | Project Incubator 的原始想法、触发场景、当前问题、初步方案、预期价值与未确认假设 |
| 消费 Phase | Phase 0–9，按需读取 |
| 更新条件 | Maker 补充或修正想法、触发原因、真实场景与未确认假设 |
| 依赖文档 | `SPECS/PROJECT_INCUBATOR_DESIGN_SPEC.md`、`SPECS/ARCHITECTURE_DECISIONS.md` |
| 最后更新 | 2026-07-20 |

## 1. 文档职责

本文档记录 Project Incubator 最初要解决的问题、想法来源、初步方案、预期价值和未确认假设。

本文档属于 Project Incubator 项目自身，不属于 Framework。当前内容是 Phase 0 的想法记录，不代表产品边界、流程细节或最终方案已经确定。

## 2. 一句话想法

Project Incubator 是一个以自身为首个孵化对象，通过阶段化流程、结构化文档和随 Phase 切换的 AI 角色，帮助 Maker 把想法逐步转化为真实作品的 AI 驱动项目孵化系统。

## 3. 触发场景

Maker 经常会产生个人工具、自动化、内容、学习项目或其他创作想法，也会使用 AI 协助分析和执行，但从想法到真实作品的过程容易遇到以下情况：

- 有想法，却不清楚下一步应该做什么；
- 不同类型的项目被套入同一种流程；
- AI 在长周期协作中遗忘上下文、改变方向或过度发挥；
- 讨论、设计、任务和执行混在聊天记录中，无法稳定延续；
- Maker 与 AI 在不同阶段的职责不清晰；
- 项目容易停留在讨论或半成品状态，缺少发布、复盘与经验沉淀。

Maker 希望先为自己建立一套能够长期使用的创造者工作系统，并让 Project Incubator 按照自己定义的流程孵化自身，以验证这套方法是否真的能够服务未来项目。

当前第一个具体、真实的使用场景，就是 Maker 正在使用 Project Incubator 的阶段化流程和文档系统来孵化 Project Incubator 自身。它既是这套系统的首个项目，也是当前正在发生的真实实践，而不是预设的示例。

## 4. 当前问题

当前缺少一套经过真实使用验证的项目孵化机制，能够同时回答：

- 当前项目处于哪个阶段；
- 当前阶段只需要解决什么问题；
- Maker 此时需要提供或决定什么；
- AI 此时应该承担什么角色；
- 当前应当如何对话；
- 哪些内容需要沉淀为文档；
- 什么条件满足后才能进入下一阶段；
- 不同项目类型应当走多深的流程。

另一个核心问题是：如果 Project Incubator 只设计方法论，却不使用自身流程孵化自身，就无法证明这套方法能够在真实项目中工作。

## 5. 初步方案

初步设想是建立一套由以下部分协同工作的项目孵化系统：

- Phase：用阶段限定当前唯一主要目标和推进条件；
- Documents：用结构化文档保存状态、决策、范围和执行上下文；
- AI Roles：让 AI 根据当前 Phase 切换协作身份；
- Maker Decision：由 Maker 保留方向、取舍、阶段切换和验收的最终决定权；
- Project Self-Incubation：把 Project Incubator 自身作为首个孵化项目，边使用、边验证、边修正 Framework。

当前已经建立 SPECS、FRAMEWORK 和 AGENTS 等初始骨架。这些内容是支持自举的工作基础，不代表项目已经完成前序阶段或进入 Design。后续仍需从 Phase 0 开始，按 Framework 逐步明确意图、边界、验证方式和真实使用路径。

## 6. 预期价值

Project Incubator 预期帮助 Maker：

- 降低把想法变成项目的启动成本；
- 在每个阶段知道下一步应该处理什么；
- 减少 AI 协作中的上下文丢失和方向漂移；
- 控制项目复杂度，避免个人项目被过度设计；
- 提高真实完成、投入使用和发布的概率；
- 把项目经验沉淀为可复用资产；
- 逐步形成属于 Maker 自己的创造者工作系统。

第一优先级是成为服务 Maker 自己的 Personal Tool。未来是否固化为 Codex Skill，需要在 Framework 经真实项目验证后再决定。

## 7. 已确认事实

以下内容已经由 Maker 或 Architecture Decisions 明确确认：

- Project Incubator 本身是一个正在孵化中的项目；
- Project Incubator 当前处于 Phase 0 — Idea Capture；
- Framework 是 Project Incubator 的核心资产；
- 未来具体项目只消费 Framework，不复制 Framework；
- Personal Tool 是第一优先级；
- AI Role 必须绑定当前 Phase；
- 重要状态和决策必须文档化；
- 不同项目不必走完全部 Phase；
- Markdown 正文默认使用中文；
- 当前已有 Framework 文档属于自举骨架，不能作为已经进入 Phase 4 的证据。
- Maker 已确认本文的一句话想法准确表达了真实意图；
- Maker 已确认本文记录的产生原因来自正在进行的真实经历；
- Maker 已确认 Project Incubator 自身就是首个具体、真实的使用场景。

## 8. 未确认假设

以下内容仍需在后续对话和 Phase 中确认：

- Project Incubator 最核心、最高频的个人使用场景是什么；
- 第一目标用户是否只包括 Maker 自己，以及何时考虑其他使用者；
- Project Incubator 的明确边界和非目标是什么；
- 怎样判断 Project Incubator 已经产生真实价值；
- 哪些 Phase 对 Personal Tool 必需、哪些可轻量执行或跳过；
- 项目状态文档的正式字段、状态枚举和更新规则；
- 未来具体项目工作区的存放位置和创建方式；
- Framework 如何版本化、验证和批准变更；
- 哪些流程应由 AI 自动推动，哪些必须等待 Maker 明确操作；
- 未来 Codex Skill 的触发方式、权限、安装和发布机制。

这些内容当前只作为待澄清问题，不应被 AI 当作已经确认的需求。

## 9. Phase 0 退出条件

- [x] Maker 确认本文中的一句话想法准确；
- [x] Maker 确认本文对想法产生原因的描述准确；
- [x] Maker 确认 Project Incubator 自身作为首个真实使用场景已经被准确记录。

以上条件已经获得 Maker 明确确认。项目仍保持在 Phase 0，直到 Maker 决定是否进入 Phase 1。

## 10. 依据

- `SPECS/PROJECT_INCUBATOR_DESIGN_SPEC.md`；
- `SPECS/ARCHITECTURE_DECISIONS.md`；
- `FRAMEWORK/Phase-System.md`；
- `FRAMEWORK/Document-System.md`；
- `AGENTS.md`；
- Maker 对 Project Incubator 当前阶段与自我孵化原则的确认。
