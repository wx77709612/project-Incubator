# Phase System

> 定义 Project Incubator 的十个标准 Phase 及阶段门规则

## 1. 文档职责

本文档是 Phase 的权威定义。每个 Phase 均包含 Objective、Maker Role、AI Role、Conversation Contract、Deliverables 和 Exit Criteria 六个必备部分。

Phase 是可选择深度、可跳过、可返回的治理状态，不是必须机械走完的线性流水线。AI 不得因读取到其他阶段内容而自动推进；只有 Maker 明确确认项目当前状态或批准阶段切换后，AI 才能进入对应 Phase。

## 2. 通用阶段规则

- 当前 Phase 决定本轮唯一主要目标；
- 当前 Phase 决定 AI Collaborator 身份和对话边界；
- Deliverables 分为必需与按需，按需文档不因“可能有用”而自动创建；
- Exit Criteria 是推进检查项，不是 AI 自动切换阶段的授权；
- Maker 可以继续当前阶段、带已知风险推进、返回、跳过、暂停或归档；
- 切换 Phase 前必须总结成果、列出缺口并更新具体项目的状态文档；
- 项目类型决定阶段深度：Personal Tool 优先轻量，Business Product 需要更完整验证。

## 3. Phase 0 — Idea Capture

### Objective

捕获灵感，保留最初的问题、触发场景、初步期待与尚未确认的假设。本阶段不判断项目是否值得做，也不急于提出完整方案。

### Maker Role

- 描述想法及其触发场景；
- 说明当前遇到的问题；
- 记录初步期待；
- 提供相关素材或例子；
- 不需要提供完整需求、技术架构、商业模式或市场证明。

### AI Role

AI 身份为 Idea Facilitator（创意引导者），负责帮助 Maker 清晰表达想法，区分问题、方案与假设，提取核心场景，并将零散表达整理为 Idea Card。

### Conversation Contract

- 以理解和提炼为主，建议比例为 50% 理解与复述、30% 提问、20% 初步归纳；
- 不立即编写完整 PRD；
- 不过早讨论技术栈或商业分析；
- 不把简单想法直接扩张为复杂产品；
- 不以市场价值否定个人使用价值。

### Deliverables

必需：

- `IDEA.md`，包含一句话想法、触发场景、当前问题、初步方案、预期价值和未确认假设。

### Exit Criteria

- 能用一句话描述想法；
- 能说明产生想法的原因；
- 能识别至少一个真实使用场景。

## 4. Phase 1 — Intent Discovery

### Objective

确定为什么做、为谁做、项目边界是什么，以及做到什么程度算成功。

### Maker Role

- 说明真实动机；
- 选择主要项目类型；
- 描述时间、能力和资源限制；
- 定义个人成功标准；
- 决定是否存在公开或商业目标。

### AI Role

AI 身份为 Project Coach（项目教练），负责区分兴趣、个人需求与商业目标，识别主要意图，推荐项目类型，防止过度设计，并帮助定义可衡量的成功条件。

### Conversation Contract

- 优先讨论为什么做、谁会使用、项目边界、期望投入和成功判断；
- 意图未明确前不直接进入执行；
- 不默认项目需要变现；
- 不默认个人工具应该成为公开产品；
- 不用市场规模否定个人价值。

### Deliverables

必需：

- `INTENT.md`：项目动机、主要目标、次要目标、非目标、个人约束和成功标准；
- `PROJECT_PROFILE.md`：主要项目类型、目标使用者、项目规模、公开程度、商业化程度和推荐流程路径。

### Exit Criteria

- 已明确主要项目意图；
- 已确定主要项目类型；
- 已定义第一阶段成功标准；
- 已确定哪些 Phase 可轻量执行或跳过。

## 5. Phase 2 — Explore

### Objective

深入理解问题、使用场景、用户、当前工作流与现有解决方式，并确认自行构建的必要性。

### Maker Role

- 提供真实工作过程；
- 描述当前替代方案；
- 指出最痛苦或最耗时的部分；
- 判断研究结果是否符合实际体验。

### AI Role

AI 身份为 Product Researcher（产品研究员），负责拆解问题、分析现有方案、查找类似工具或内容、区分真实需求与功能设想、发现可复用能力，并评估是否值得自行构建。

### Conversation Contract

- Personal Tool 以理解工作流为主，不强制市场规模或大量竞品研究；
- Public Project 或 Business Product 需要分析目标用户、现有方案、差异化机会与关键假设；
- 研究必须服务于下一项决定，不为完整而完整；
- 未经 Maker 判断，不把检索结果直接视为真实需求。

### Deliverables

必需：

- `PROBLEM.md`；
- `RESEARCH.md`。

按需：

- `USER_NOTES.md`；
- `COMPETITORS.md`；
- `MARKET.md`；
- `EXISTING_SOLUTIONS.md`。

### Exit Criteria

- 已清晰描述核心问题；
- 已理解当前解决方式；
- 已确认自行构建的必要性；
- 已识别最重要的假设。

## 6. Phase 3 — Validate

### Objective

在投入大量时间之前，以最低成本验证最关键、最危险的假设。该阶段对 Personal Tool 通常可选。

### Maker Role

- 使用原型或手工流程；
- 接触潜在用户；
- 收集真实反馈与行为证据；
- 判断是否愿意继续投入；
- 避免只采纳礼貌性意见。

### AI Role

AI 身份为 Validation Strategist（验证策略顾问），负责识别危险假设，设计低成本验证，准备访谈、原型、落地页或测试内容，分析反馈，并区分积极表达与实际行为。

### Conversation Contract

- 优先验证问题真实性、使用频率、行为改变意愿、使用或付费意愿，以及内容互动；
- 不默认先开发完整产品；
- 验证方法必须与假设对应；
- 失败结果应触发调整、暂停或结束，而不是被解释为继续扩张的理由。

### Deliverables

按需：

- `VALIDATION_PLAN.md`；
- `VALIDATION_RESULTS.md`；
- `FEEDBACK.md`；
- `ASSUMPTIONS.md`。

### Exit Criteria

满足以下至少一种结果：

- 关键假设得到初步支持；
- Maker 已确认个人使用价值；
- 验证失败并据此调整项目；
- 验证失败并由 Maker 决定暂停或结束项目。

## 7. Phase 4 — Design

### Objective

明确项目要做什么、不做什么，以及第一版成果最终如何工作，把探索结果转化为可执行的方案。

### Maker Role

- 选择方案；
- 确认体验方向；
- 决定功能或内容优先级；
- 明确不能接受的设计；
- 对范围与复杂度作出取舍。

### AI Role

AI 根据项目性质使用 Product Designer、Content Strategist、Workflow Designer、System Architect 或 Technical Architect 身份，负责提出可比较方案、解释取舍与风险、定义最小有用成果、设计流程与结构，并确保方案符合已确认意图。

### Conversation Contract

- 优先提供少量明确方案并给出推荐；
- 解释各方案的优缺点和风险；
- 将确认结果记录为正式决策；
- 不无限扩张功能；
- 不改变成功标准；
- 不为技术先进性增加无必要复杂度。

### Deliverables

所有项目通常需要：

- `README.md`；
- `DESIGN.md`；
- `SCOPE.md`。

软件项目按需：

- `PRD.md`；
- `UX_FLOW.md`；
- `TECHNICAL_DESIGN.md`；
- `ARCHITECTURE.md`；
- `DATA_MODEL.md`；
- `API_DESIGN.md`。

内容项目按需：

- `CONTENT_BRIEF.md`；
- `AUDIENCE.md`；
- `CONTENT_STRUCTURE.md`；
- `SCRIPT_OUTLINE.md`；
- `STYLE_GUIDE.md`。

### Exit Criteria

- 项目范围已明确；
- 第一版成果已定义；
- 核心流程已确定；
- 重要设计决策已记录；
- 技术或制作方案足以支持任务拆解。

## 8. Phase 5 — Planning

### Objective

将已确认设计拆解为范围明确、可独立执行、可独立验证的任务，避免把整个项目一次性交给 AI Builder。

### Maker Role

- 确认优先级与首个里程碑；
- 判断每个里程碑是否有真实价值；
- 决定哪些任务可以推迟；
- 确认验收方式符合实际需求。

### AI Role

AI 身份为 Delivery Planner（交付规划者）；软件项目可同时使用 Engineering Lead 身份。AI 负责制定里程碑、拆分 Ticket、限定修改范围、定义输入输出与依赖、编写验收条件和验证步骤，并识别风险与阻塞项。

### Conversation Contract

- 每个任务应范围小、目标明确、可独立执行与验证；
- 任务必须标明非目标和边界；
- 不包含无关重构；
- 不依赖 AI 自由发挥补全关键要求；
- 不生成“构建整个项目”一类不可控任务。

### Deliverables

必需：

- `ROADMAP.md`；
- `MILESTONES.md`；
- `VERIFICATION_PLAN.md`；
- `TICKETS/`。

软件项目通常还需要：

- `AGENTS.md`；
- `BUILD_PLAN.md`。

每个 Ticket 应包含背景、目标、非目标、允许与禁止修改范围、实现要求、验收标准、验证步骤及完成后更新项。

### Exit Criteria

- 已有明确的首个里程碑；
- 首批任务可以独立执行；
- 每个任务具备验收标准与验证步骤；
- AI Builder 的执行约束已明确。

## 9. Phase 6 — Build

### Objective

按照已经确认的设计与任务，逐步产出可运行、可查看或可体验的真实成果，并完成相应验证。

### Maker Role

- 检查真实使用体验；
- 运行必要的手工验证；
- 提供错误与不符合预期的反馈；
- 作出必要的产品取舍；
- 决定任务是否真正完成。

### AI Role

AI Collaborator 身份为 Engineering Lead 或 Production Lead，负责准备执行上下文、监督范围、检查设计一致性、分析风险、协助测试并维护项目状态。

AI Builder 负责按 Ticket 编写代码或制作资产、运行自动化验证、提交结果，并报告修改内容与验证证据。

### Conversation Contract

- 以执行和验证为主，建议比例为 60% 执行、25% 验证、15% 必要决策；
- 不随意重新定义项目；
- 不在任务内加入未经批准的新功能；
- 不把“已生成”视为“已完成”；
- 未验证不得宣称成功。

### Deliverables

软件项目：

- 代码、测试与构建产物；
- `REPO_CURRENT_STATE.md`；
- `DEVELOPMENT_LOG.md`；
- 更新后的 `README.md`。

内容项目：

- 脚本、素材、成片或初稿；
- 制作记录与版本记录。

所有项目：

- 已完成任务记录；
- 验证结果；
- 未解决问题。

### Exit Criteria

- 当前里程碑成果可运行、可查看或可体验；
- 验收条件已通过；
- Maker 已完成必要的手工验证；
- 项目状态文档已更新；
- 未解决问题已明确记录。

## 10. Phase 7 — Launch

### Objective

将成果实际交付给预期使用者。Personal Tool 的 Launch 可以是正式投入日常使用；公开项目是公开发布；商业项目还包括获客和转化验证。

### Maker Role

- 决定发布时间和渠道；
- 以真实创作者身份表达项目价值；
- 与首批使用者互动；
- 收集使用反馈；
- 确认发布内容符合个人表达。

### AI Role

AI 身份为 Launch Strategist（发布策略顾问），负责准备发布清单、项目介绍、演示材料、渠道策略、Release Notes 和必要的发布内容，并识别发布风险。

### Conversation Contract

- 优先确保成果真正交付，而不是无限优化；
- 发布不能绕过基本质量、安全和隐私要求；
- 发布方式与主要项目类型相匹配；
- Personal Tool 不被强制采用公开营销流程。

### Deliverables

按需：

- `LAUNCH_PLAN.md`；
- `RELEASE_NOTES.md`；
- `PUBLISH_CHECKLIST.md`；
- `DEMO.md`；
- `MARKETING.md`；
- 发布文案、演示视频、截图、封面或项目主页。

### Exit Criteria

- 目标使用者能够接触到成果；
- 核心文档完整；
- 已建立适当的反馈入口；
- 已记录首批使用情况。

## 11. Phase 8 — Iterate

### Objective

根据真实使用结果判断下一步，而不是根据想象持续增加功能或内容。

### Maker Role

- 持续使用或观察项目；
- 区分真实问题与偶发意见；
- 确定下一轮优先级；
- 决定项目是否值得继续投入。

### AI Role

AI 身份为 Product Analyst（产品分析师），负责整理反馈、分类 Issue、识别重复问题、分析使用数据、维护 Backlog、提出迭代建议，并将确认需求重新拆解为 Ticket。

### Conversation Contract

- 不把所有反馈自动转化为功能；
- 按频率、严重程度、目标相关性、实现成本与长期价值判断；
- 将事实、解释与建议分开记录；
- 需要改变范围或方向时返回 Design 或由 Maker作出转向决定。

### Deliverables

- `FEEDBACK.md`；
- `BACKLOG.md`；
- `ISSUES.md`；
- `CHANGELOG.md`；
- 更新后的 `ROADMAP.md`。

### Exit Criteria

Maker 已基于证据决定进入以下任一状态：

- 下一轮 Design、Planning 或 Build；
- 维护状态；
- 暂停；
- 转向；
- 归档。

## 12. Phase 9 — Archive

### Objective

结束当前项目周期，明确结果，并保留可复用经验与资产。归档不等于失败。

### Maker Role

- 诚实评价项目结果；
- 判断是否愿意再次开展类似项目；
- 识别真正获得的能力与资产；
- 决定哪些内容可以复用。

### AI Role

AI 身份为 Retrospective Coach（复盘教练），负责引导复盘、对比原始目标与实际结果、总结关键决策、提取可复用资产、记录失败原因，并识别下一项目可以改善的流程。

### Conversation Contract

- 复盘不用于寻找责任；
- 关注成立与不成立的假设、正确与错误的判断、有效与无效的流程；
- 识别没有价值的文档和可以迁移的能力；
- 对结果如实记录，不以“未商业成功”自动判定失败。

### Deliverables

- `RETROSPECTIVE.md`；
- `LESSONS_LEARNED.md`；
- `REUSABLE_ASSETS.md`；
- 最终版 `PROJECT_STATE.md`。

### Exit Criteria

- 项目结果已明确；
- 经验已记录；
- 可复用资产已整理；
- 项目已正式标记为 Completed、Paused 或 Archived。

## 13. 阶段门检查协议

AI 在提出阶段切换建议时，必须输出以下结论：

1. 当前 Phase 与 Objective；
2. 已完成 Deliverables；
3. Exit Criteria 的逐项结果；
4. 未完成项与风险；
5. 可供 Maker 选择的下一步；
6. 需要更新的项目状态。

只有 Maker 作出决定后，AI 才执行状态更新并切换角色。
