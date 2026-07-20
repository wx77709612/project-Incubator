# Project Incubator Framework

> 面向 Maker 与未来 AI Agent 的 Framework 自举草案

## 1. 文档职责

本文档定义 Project Incubator 的系统定位、边界、核心理念与整体生命周期，是 Framework 的总入口。

详细规则分别由以下文档定义：

- `Phase-System.md`：十个 Phase 的阶段规范；
- `Role-System.md`：Maker、AI Collaborator、AI Builder 的职责与切换规则；
- `Document-System.md`：文档分类、用途、生命周期与归属；
- `Codex-Skill-Specification.md`：未来固化为 Codex Skill 的要求。

## 2. 权威依据与资产归属

Project Incubator 本身是一个项目，并以项目方式持续孵化和验证自身方法。

Framework 是 Project Incubator 的核心资产，属于 Project Incubator，不属于未来被孵化的具体项目。未来项目只读取并使用 Framework 定义的流程、角色规则和模板，不复制 Framework，也不在本项目中建立用于集中存放未来项目的 `PROJECTS/` 目录。

当 Framework 内容与设计输入冲突时，以 `SPECS/PROJECT_INCUBATOR_DESIGN_SPEC.md` 和 `SPECS/ARCHITECTURE_DECISIONS.md` 为准。已经确定的架构决策不得由 AI Agent 静默修改。

## 3. 系统定位

Project Incubator 是一套 AI 驱动的创造者工作系统。它帮助 Maker 从一个模糊想法出发，通过阶段化流程、结构化文档和随 Phase 切换的 AI 角色，逐步形成真实作品。

作品可以是个人工具、AI Skill、自动化流程、公开项目、内容作品、学习成果或商业产品。系统不要求每个想法都商业化，也不要求每个项目执行同样完整的流程。

Project Incubator 不是：

- 单纯的项目管理工具；
- 只适用于软件开发的工程流程；
- 强制所有项目接受市场验证的创业模板；
- 以文档数量衡量项目成熟度的文档工厂；
- 替代 Maker 作出方向性决定的自动决策系统。

## 4. 第一目标与未来方向

Project Incubator 的第一目标是 Personal Tool：首先服务 Maker 自己，降低从想法到真实作品的启动成本、协调成本和完成难度。

在 Framework 经真实使用验证并趋于稳定后，未来可以固化为 Codex Skill。Skill 化是可能的演化方向，不改变 Personal Tool 的第一优先级，也不代表当前 Framework 已进入 Skill 实现阶段。

## 5. 核心理念

### 5.1 Intent Before Process

先明确为什么做、为谁做、做到什么程度算成功，再选择流程深度。AI 不应在意图未明确时直接进入市场分析、产品设计或执行。

### 5.2 Different Projects, Different Paths

所有项目共享一套 Phase 语言，但不必走完全部 Phase。项目必须指定一个主要类型；主要类型、项目意图与风险共同决定哪些阶段需要完整执行、轻量执行或跳过。

### 5.3 Documents Drive Projects

聊天用于交流，文档用于保存权威状态。重要状态、范围、决策、任务和验证结果必须文档化，以支持跨会话、跨 Agent 和长期协作。

### 5.4 Smallest Useful Outcome

第一版优先寻找“最小有用成果”，即能够真实解决问题、完成表达或验证假设的最小成果，而不是为了形式完整扩大范围。

### 5.5 Phase-Gated Collaboration

每个 Phase 都由 Objective、Maker Role、AI Role、Conversation Contract、Deliverables 和 Exit Criteria 六部分构成。满足退出条件后才默认建议推进；Maker 可以决定继续、带风险前进、返回、跳过、暂停或归档。

### 5.6 One Phase, One Primary Goal

一个阶段只处理一个主要目标。当前 Phase 决定本轮协作重点、AI 身份、允许生成的交付物和暂不展开的话题，以减少认知负担与方向漂移。

### 5.7 Maker 保留最终决定权

AI 可以澄清、分析、建议、执行和验证，但项目方向、范围取舍、阶段切换、成果验收及项目状态由 Maker 决定。

## 6. 支持的项目类型

| 主要类型 | 首要目的 | 流程特点 | 主要成功标准 |
| --- | --- | --- | --- |
| Personal Tool | 解决 Maker 自己的问题 | Explore 可轻量，Validate 通常可选，不强制市场或商业流程 | 真实可用、节省时间、改善体验、Maker 愿意持续使用 |
| Public Project | 服务公开用户或开源社区 | 需要可理解性、文档和外部反馈 | 他人能够理解、使用、反馈或贡献 |
| Business Product | 服务市场、用户和收入目标 | 需要更完整的研究、验证和商业设计 | 真实需求、采用或付费、差异化与持续获客 |
| Content Project | 产出并发布内容作品 | 围绕受众、表达、制作、发布和效果复盘 | 完成发布、清晰表达并触达目标观众 |
| Learning Project | 学习并沉淀能力 | 围绕目标、练习、示范成果和复盘 | 掌握能力并留下可展示、可复用成果 |

一个项目可以同时具有多个类型属性，但必须指定一个主要类型，作为流程选择的首要依据。

## 7. 整体生命周期

| Phase | 名称 | 唯一主要目标 |
| --- | --- | --- |
| Phase 0 | Idea Capture | 捕获想法、触发场景与原始问题 |
| Phase 1 | Intent Discovery | 明确动机、对象、边界与成功标准 |
| Phase 2 | Explore | 理解问题、工作流、用户与现有方案 |
| Phase 3 | Validate | 以最低成本验证关键假设 |
| Phase 4 | Design | 定义做什么、不做什么以及如何工作 |
| Phase 5 | Planning | 将设计拆成范围明确、可验证的任务 |
| Phase 6 | Build | 按任务产出并验证真实成果 |
| Phase 7 | Launch | 将成果交付给预期使用者 |
| Phase 8 | Iterate | 根据真实使用结果决定下一步 |
| Phase 9 | Archive | 结束当前周期并沉淀经验与资产 |

十个 Phase 构成完整阶段语言，不构成强制线性流水线。Personal Tool 通常使用轻量 Explore，可跳过独立 Validate，并可将 Launch 定义为正式投入个人日常使用；Business Product 通常需要更完整的 Explore、Validate 与 Launch。

## 8. 阶段切换机制

阶段切换必须遵循以下顺序：

1. AI 总结当前阶段成果；
2. AI 对照 Exit Criteria 检查满足项与缺口；
3. AI 明确未完成项和带风险推进的影响；
4. Maker 决定继续、带风险推进、返回、跳过、暂停或归档；
5. 更新具体项目的权威状态文档；
6. AI 才切换到新 Phase 对应的身份与 Conversation Contract。

AI 不得未经说明私自切换阶段，不得把文档已经生成等同于阶段已经完成。

## 9. Framework 的运行边界

Framework 负责定义可复用规则，不负责保存未来具体项目的实例状态。具体项目应在其自身独立工作区内按需创建项目文档，并引用 Framework。

Framework 不要求实际项目预先创建全部阶段文档，也不要求所有项目生成 PRD、市场分析、技术架构、商业模型或发布策略。文档只有在能够帮助决策、协作、执行、验证或复盘时才创建。

## 10. Framework 的有效性标准

当这套 Framework 能稳定帮助 Maker 和 AI Agent 完成以下行为时，才可视为有效：

- 从项目状态中识别当前 Phase；
- 选择与意图和主要类型相匹配的流程深度；
- 让 AI 使用正确角色并遵守当前阶段边界；
- 只生成当前有价值的文档；
- 保持关键事实、决策和状态的单一权威来源；
- 将设计拆成可执行、可验收、可验证的任务；
- 在跨会话协作中保持方向一致；
- 从完成、暂停、转向或终止的项目中沉淀可复用经验。
