# Project Incubator v1.0

## AI 共创项目孵化器设计思路文档

---

# 1. 文档目的

本文档用于定义一套可重复使用的 AI 共创项目孵化框架。

这套框架帮助创造者把一个模糊想法逐步转化为真实作品。作品可以是：

- 一个供自己使用的小工具
- 一个 AI Skill
- 一个 Apple Shortcut
- 一个自动化流程
- 一个开源项目
- 一个视频或内容系列
- 一个浏览器扩展
- 一个桌面或移动 App
- 一个 SaaS 产品
- 一个具有商业目标的完整项目

本框架不要求所有项目都以商业化为目标，也不要求所有想法都经过完整的市场验证流程。

它的核心目标是：

> 根据项目意图，为不同类型的想法自动选择合适的创作路径，并明确每个阶段中用户与 AI 的职责、对话方式、交付物和推进条件。

---

# 2. 系统定位

Project Incubator 不是单纯的项目管理工具，也不是只面向软件开发的工程流程。

它是一套：

> AI 驱动的创造者工作系统。

它主要解决以下问题：

1. 有想法，但不知道下一步应该做什么。
2. 不同项目需要不同流程，却经常被套入同一种开发模式。
3. AI 在长周期项目中容易遗忘上下文、改变方向或过度发挥。
4. 项目讨论、设计、任务和执行混杂在聊天记录中，难以持续。
5. 用户与 AI 在不同阶段中的职责不清晰。
6. 项目做完之后缺少发布、复盘和经验沉淀。

---

# 3. 核心角色

## 3.1 用户：Maker

用户的长期身份是 Maker，即创造者。

Maker 的核心职责是：

- 提出真实问题和想法
- 描述自己的使用场景
- 提供偏好和限制条件
- 做关键选择
- 判断方案是否符合实际需求
- 亲自体验和验收成果
- 决定项目继续、暂停、转向或结束

Maker 不需要负责记住全部流程，也不需要独自完成所有分析、设计和执行工作。

---

## 3.2 AI：阶段化协作者

AI 没有一个永久不变的固定角色。

AI 的角色由当前项目阶段决定。

例如：

- 在灵感阶段，AI 是创意引导者。
- 在意图阶段，AI 是项目教练。
- 在研究阶段，AI 是研究员。
- 在设计阶段，AI 是产品设计者或系统架构师。
- 在开发阶段，AI 是技术负责人。
- 在发布阶段，AI 是发布与增长顾问。
- 在复盘阶段，AI 是复盘教练。

因此：

> AI 的角色是 Phase 的属性，而不是独立于流程之外的静态身份。

---

## 3.3 AI Builder

当项目进入具体执行阶段时，可以引入 Codex、Cursor、Claude Code 或其他执行型 AI。

AI Builder 主要负责：

- 编写代码
- 修改文件
- 运行测试
- 修复问题
- 生成资产
- 完成明确范围内的任务

AI Builder 不负责决定项目方向。

项目方向由 Maker 决定，阶段型 AI 协作者负责整理和推动。

---

# 4. 核心设计原则

## 4.1 Intent Before Process

系统在启动项目时，首先判断项目意图，而不是立刻进行市场分析、产品设计或编码。

第一个核心问题是：

> 为什么要做这个项目？

常见项目意图包括：

- 解决自己的问题
- 提高个人效率
- 学习某项技术
- 完成一次创作实验
- 积累 GitHub 作品
- 建立个人品牌
- 服务一部分公开用户
- 验证商业机会
- 获得收入

项目意图决定后续流程的深度。

---

## 4.2 Different Projects, Different Paths

所有项目从同一个入口进入，但不需要经过同样的阶段。

系统需要支持以下主要项目类型：

### Personal Tool

为 Maker 自己解决问题。

主要成功标准：

- 是否真实可用
- 是否节省时间
- 是否改善体验
- Maker 是否愿意持续使用

不强制进行市场研究或商业验证。

### Public Project

主要面向公开用户或开源社区。

主要成功标准：

- 别人是否能够理解和使用
- 是否具备清晰的文档
- 是否有人采用、反馈或贡献
- 是否形成公开作品和能力背书

### Business Product

以市场、用户和收入为目标。

主要成功标准：

- 是否存在真实需求
- 用户是否愿意使用或付费
- 是否具备差异化
- 是否能够持续获取用户

必须包含更完整的研究、验证和商业设计。

### Content Project

以视频、文章、课程、系列内容或媒体作品为输出。

主要成功标准：

- 是否清晰表达主题
- 是否完成并发布
- 是否触达目标观众
- 是否形成可持续内容方向

### Learning Project

主要目的是学习技术、工具或方法。

主要成功标准：

- 是否掌握目标能力
- 是否形成可展示成果
- 是否留下可复用笔记或示例
- 是否完成预定学习闭环

一个项目可以同时拥有多个类型，但必须指定一个主要类型。

---

## 4.3 Documents Drive the Project

项目不能依赖聊天记录作为唯一上下文。

每个关键阶段都必须生成结构化文档。

这些文档用于：

- 保存项目状态
- 约束 AI 行为
- 支持跨会话持续工作
- 向 Codex 或其他执行工具传递任务
- 避免重复讨论
- 记录决策和变更
- 支持项目复盘和复用

---

## 4.4 Smallest Useful Outcome

第一版不追求完整。

系统应该优先寻找：

> 最小有用成果，而不仅仅是最小可行产品。

对于个人工具，最小成果可能只是一个能够稳定运行的快捷指令。

对于内容项目，可能只是发布第一期视频。

对于商业项目，可能只是一个可验证需求的落地页。

---

## 4.5 Phase-Gated Collaboration

项目按照阶段推进。

每个阶段必须定义：

1. Objective：阶段目标
2. Maker Role：用户职责
3. AI Role：AI 当前身份
4. Conversation Contract：对话契约
5. Deliverables：阶段交付物
6. Exit Criteria：退出条件

项目只有在满足退出条件后，才默认进入下一阶段。

Maker 可以主动跳过、返回或暂停某个阶段。

---

## 4.6 One Phase, One Primary Goal

在某一阶段中，不应同时解决所有问题。

例如：

- Idea 阶段不急于设计技术架构。
- Design 阶段不随意重新定义项目意图。
- Build 阶段不应持续扩张产品范围。
- Launch 阶段不应重新实现整个系统。

这可以降低认知负担，并减少 AI 在长项目中的方向漂移。

---

# 5. 项目状态模型

每个项目都有一个明确的当前状态。

示例：

```yaml
project_name: Example Project
project_type: Personal Tool
current_phase: Phase 4 - Design
status: Active
primary_goal: Reduce repeated manual work
next_decision: Select the preferred workflow design
```

AI 在开始工作前，应先读取当前状态。

当前 Phase 决定：

- AI 以什么角色交流
- 当前主要问题是什么
- 应该读取哪些文档
- 可以生成哪些交付物
- 哪些话题暂时不应展开
- 满足什么条件才能进入下一阶段

---

# 6. 项目生命周期

项目生命周期由十个阶段组成。

并非所有项目都需要完整走完十个阶段。

---

# Phase 0：Idea Capture

## Objective

捕获灵感，保留最初的问题、场景和触发原因。

这一阶段不判断项目是否值得做，也不急于提出完整方案。

## Maker Role

Maker 负责：

- 描述想法
- 描述触发这个想法的场景
- 说明当前遇到的问题
- 记录初步期待
- 提供相关素材或例子

Maker 不需要：

- 提供完整需求
- 考虑技术架构
- 设计商业模式
- 证明市场规模

## AI Role

AI 身份：

> Idea Facilitator，创意引导者。

AI 负责：

- 帮助 Maker 清晰表达想法
- 区分问题、方案和假设
- 提取核心使用场景
- 发现模糊或隐含需求
- 将零散表达整理成 Idea Card

## Conversation Contract

AI 应以理解和提炼为主。

建议比例：

- 50% 理解和复述
- 30% 提问
- 20% 初步归纳

AI 不应：

- 立刻写完整 PRD
- 过早讨论技术栈
- 过早进行商业分析
- 直接把一个简单想法扩大成复杂产品

## Deliverables

必需：

- `IDEA.md`

主要内容：

- 一句话想法
- 触发场景
- 当前问题
- 初步方案
- 预期价值
- 未确认假设

## Exit Criteria

满足以下条件即可进入下一阶段：

- 能用一句话描述这个想法
- 能说明为什么产生这个想法
- 能识别至少一个真实使用场景

---

# Phase 1：Intent Discovery

## Objective

确定为什么做、为谁做、做到什么程度就算成功。

## Maker Role

Maker 负责：

- 说明真实动机
- 选择主要项目类型
- 描述时间、能力和资源限制
- 定义个人成功标准
- 决定是否存在公开或商业目标

## AI Role

AI 身份：

> Project Coach，项目教练。

AI 负责：

- 帮助 Maker 区分兴趣、需求和商业目标
- 识别主要项目意图
- 推荐合适的项目类型
- 防止简单项目被过度设计
- 帮助定义可衡量的成功条件

## Conversation Contract

AI 应优先讨论：

- 为什么做
- 谁会使用
- 项目边界
- 期望投入
- 成功和失败如何判断

AI 不应：

- 在意图未明确前直接进入执行
- 默认所有项目都需要变现
- 默认所有个人工具都应成为产品
- 用市场规模否定个人价值

## Deliverables

必需：

- `INTENT.md`
- `PROJECT_PROFILE.md`

`INTENT.md` 包含：

- 项目动机
- 主要目标
- 次要目标
- 非目标
- 个人约束
- 成功标准

`PROJECT_PROFILE.md` 包含：

- 项目类型
- 目标使用者
- 项目规模
- 公开程度
- 商业化程度
- 推荐流程路径

## Exit Criteria

- 已明确主要项目意图
- 已确定主要项目类型
- 已定义第一阶段成功标准
- 已确定哪些流程可以跳过

---

# Phase 2：Explore

## Objective

深入理解问题、场景、用户和现有解决方式。

对于 Personal Tool，本阶段可以非常轻量。

对于 Business Product，本阶段需要更系统。

## Maker Role

Maker 负责：

- 提供自己的真实工作过程
- 描述当前替代方案
- 指出最痛苦或最浪费时间的部分
- 反馈研究结果是否符合实际体验

## AI Role

AI 身份：

> Product Researcher，产品研究员。

AI 负责：

- 拆解问题
- 分析现有解决方案
- 查找类似工具或内容
- 区分真实需求与功能设想
- 发现可复用的现有能力
- 评估是否值得自己构建

## Conversation Contract

对于个人工具：

- 重点是理解工作流
- 不强制分析市场规模
- 不强制研究大量竞争对手

对于公开或商业项目：

- 需要分析目标用户
- 需要调查现有方案
- 需要识别差异化机会
- 需要明确关键假设

## Deliverables

必需：

- `PROBLEM.md`
- `RESEARCH.md`

按需：

- `USER_NOTES.md`
- `COMPETITORS.md`
- `MARKET.md`
- `EXISTING_SOLUTIONS.md`

## Exit Criteria

- 已清晰描述核心问题
- 已知道当前用户如何解决问题
- 已确认自行构建的必要性
- 已识别项目最重要的假设

---

# Phase 3：Validate

## Objective

在投入大量时间之前，验证关键假设。

该阶段对于 Personal Tool 通常是可选的。

## Maker Role

Maker 负责：

- 使用原型或手工流程
- 接触潜在用户
- 收集真实反馈
- 判断是否愿意继续投入
- 避免只听取礼貌性意见

## AI Role

AI 身份：

> Validation Strategist，验证策略顾问。

AI 负责：

- 识别最危险的假设
- 设计低成本验证方式
- 编写访谈问题
- 设计落地页、原型或测试内容
- 分析反馈
- 区分积极反馈与实际行为

## Conversation Contract

AI 应推动最低成本验证，而不是默认开发完整产品。

优先验证：

- 问题是否真实
- 使用频率是否足够
- 用户是否愿意改变原有行为
- 用户是否愿意使用或付费
- 内容是否有人观看或互动

## Deliverables

按需：

- `VALIDATION_PLAN.md`
- `VALIDATION_RESULTS.md`
- `FEEDBACK.md`
- `ASSUMPTIONS.md`

## Exit Criteria

项目满足以下一种情况即可：

- 关键假设得到初步支持
- Maker 自己已确认个人使用价值
- 验证失败，项目被调整
- 验证失败，项目被暂停或结束

---

# Phase 4：Design

## Objective

明确项目要做什么、不做什么，以及最终如何工作。

这是从探索进入具体方案的阶段。

## Maker Role

Maker 负责：

- 选择方案
- 确认体验方向
- 决定功能优先级
- 明确不能接受的设计
- 对复杂度和范围进行取舍

## AI Role

AI 根据项目性质切换为：

- Product Designer
- Content Strategist
- Workflow Designer
- System Architect
- Technical Architect

AI 负责：

- 将需求转化为结构化设计
- 提供可比较的方案
- 说明取舍和风险
- 定义 MVP 或最小有用成果
- 设计用户流程
- 设计系统或内容结构
- 确保方案符合项目意图

## Conversation Contract

AI 应：

- 优先提供少量明确方案
- 解释每种方案的优缺点
- 给出推荐方案
- 将讨论结果记录为正式决策

AI 不应：

- 无限扩张功能
- 偷偷改变成功标准
- 为了技术先进而增加复杂度
- 在没有必要时设计完整平台

## Deliverables

所有项目通常需要：

- `README.md`
- `DESIGN.md`
- `SCOPE.md`

软件项目按需需要：

- `PRD.md`
- `UX_FLOW.md`
- `TECHNICAL_DESIGN.md`
- `ARCHITECTURE.md`
- `DATA_MODEL.md`
- `API_DESIGN.md`

内容项目按需需要：

- `CONTENT_BRIEF.md`
- `AUDIENCE.md`
- `CONTENT_STRUCTURE.md`
- `SCRIPT_OUTLINE.md`
- `STYLE_GUIDE.md`

## Exit Criteria

- 项目范围已明确
- 第一版成果已定义
- 核心流程已确定
- 重要设计决策已记录
- 技术或制作方案足以支持任务拆解

---

# Phase 5：Planning

## Objective

将设计拆解为可执行、可验证、范围明确的任务。

本阶段吸收规格驱动开发的核心思想：

> 不把整个项目一次性交给 AI，而是将其拆成可控任务。

## Maker Role

Maker 负责：

- 确认优先级
- 确认每个里程碑是否有价值
- 决定哪些任务可以推迟
- 确认验收方式是否符合真实需求

## AI Role

AI 身份：

> Delivery Planner，交付规划者。

对于软件项目，也可以同时作为：

> Engineering Lead，技术负责人。

AI 负责：

- 制定里程碑
- 拆分 Ticket
- 限定每个任务的修改范围
- 定义输入、输出和依赖
- 编写验收条件
- 编写验证步骤
- 识别风险和阻塞项

## Conversation Contract

每个任务必须尽量满足：

- 范围小
- 目标明确
- 可独立执行
- 可独立验证
- 不包含无关重构
- 不依赖 AI 自由发挥

AI 不应生成类似：

> Build the whole app.

而应生成类似：

> Implement Ticket 0001，并严格遵守允许修改的文件范围和验收条件。

## Deliverables

必需：

- `ROADMAP.md`
- `MILESTONES.md`
- `VERIFICATION_PLAN.md`
- `TICKETS/`

软件项目通常还需要：

- `AGENTS.md`
- `BUILD_PLAN.md`

每个 Ticket 建议包括：

- 背景
- 目标
- 非目标
- 允许修改范围
- 禁止修改范围
- 实现要求
- 验收标准
- 验证步骤
- 完成后需要更新的文档

## Exit Criteria

- 已有明确的首个里程碑
- 首批任务可以独立执行
- 每个任务都具备验收标准
- 已明确 AI Builder 的执行约束

---

# Phase 6：Build

## Objective

按照任务和设计逐步产出项目成果。

## Maker Role

Maker 负责：

- 检查真实使用体验
- 运行手工验证
- 提供错误和不符合预期的反馈
- 做产品取舍
- 决定任务是否真正完成

## AI Role

AI 身份：

> Engineering Lead 或 Production Lead。

AI 负责：

- 为 AI Builder 准备任务上下文
- 监督任务范围
- 检查实现与设计是否一致
- 分析错误和风险
- 协助测试
- 维护项目当前状态
- 防止任务过程中出现范围扩张

AI Builder 负责：

- 按 Ticket 执行
- 编写代码或制作资产
- 运行自动化测试
- 提交实现结果
- 报告修改内容和验证结果

## Conversation Contract

Build 阶段以执行和验证为主。

建议比例：

- 60% 执行
- 25% 验证
- 15% 必要决策

AI 不应：

- 随意重新定义产品
- 在任务中加入未经批准的新功能
- 将“代码已生成”等同于“任务已完成”
- 未验证就宣称成功

## Deliverables

软件项目：

- 代码
- 测试
- 构建产物
- `REPO_CURRENT_STATE.md`
- `DEVELOPMENT_LOG.md`
- 更新后的 `README.md`

内容项目：

- 脚本
- 素材
- 成片或初稿
- 制作记录
- 版本记录

所有项目：

- 已完成任务记录
- 验证结果
- 未解决问题

## Exit Criteria

- 当前里程碑成果可运行、可查看或可体验
- 验收条件已通过
- Maker 已完成必要的手工验证
- 项目状态文档已更新
- 未解决问题已明确记录

---

# Phase 7：Launch

## Objective

将成果交付给预期使用者。

对于个人工具，Launch 可以只是正式投入日常使用。

对于公开项目，Launch 是公开发布。

对于商业项目，Launch 还包括获客和转化验证。

## Maker Role

Maker 负责：

- 决定发布时间和渠道
- 以真实创作者身份表达项目价值
- 与首批用户互动
- 收集使用反馈
- 确认发布内容符合个人表达

## AI Role

AI 身份：

> Launch Strategist，发布策略顾问。

AI 负责：

- 准备发布清单
- 编写项目介绍
- 准备演示材料
- 设计渠道策略
- 编写 Release Notes
- 准备 GitHub、社交媒体、视频或产品页内容
- 识别发布风险

## Conversation Contract

AI 应优先确保项目真正发布，而不是无限优化。

遵循：

> Published is better than permanently almost finished.

但发布不能绕过基本质量和安全要求。

## Deliverables

按需：

- `LAUNCH_PLAN.md`
- `RELEASE_NOTES.md`
- `PUBLISH_CHECKLIST.md`
- `DEMO.md`
- `MARKETING.md`
- 发布文案
- 演示视频
- 截图和封面
- 项目主页

## Exit Criteria

- 目标使用者能够接触到成果
- 核心文档完整
- 已建立反馈入口
- 已记录首批使用情况

---

# Phase 8：Iterate

## Objective

根据真实使用结果决定下一步，而不是根据想象持续增加功能。

## Maker Role

Maker 负责：

- 持续使用或观察项目
- 区分真实问题和偶发意见
- 确定下一轮优先级
- 决定项目是否值得继续投入

## AI Role

AI 身份：

> Product Analyst，产品分析师。

AI 负责：

- 整理反馈
- 分类 Issue
- 识别重复问题
- 分析使用数据
- 维护 Backlog
- 提出下一轮迭代建议
- 将需求重新拆解为 Ticket

## Conversation Contract

AI 不应把所有反馈都转化为功能。

反馈需要经过：

- 频率
- 严重程度
- 与项目目标的相关性
- 实现成本
- 长期价值

等维度判断。

## Deliverables

- `FEEDBACK.md`
- `BACKLOG.md`
- `ISSUES.md`
- `CHANGELOG.md`
- 更新后的 `ROADMAP.md`

## Exit Criteria

项目可以进入以下任一状态：

- 进入下一轮 Design / Planning / Build
- 进入维护状态
- 暂停
- 转向
- 归档

---

# Phase 9：Archive and Retrospective

## Objective

结束当前项目周期，并保留可复用经验。

归档不等于失败。

项目可能因为以下原因归档：

- 已经解决个人问题
- 达到预期目标
- 不值得继续投入
- 技术或市场条件不合适
- 兴趣发生变化
- 项目被其他方案替代

## Maker Role

Maker 负责：

- 诚实评价项目结果
- 说明是否愿意再次做类似项目
- 识别真正获得的能力和资产
- 决定哪些内容可以复用

## AI Role

AI 身份：

> Retrospective Coach，复盘教练。

AI 负责：

- 引导复盘
- 对比原始目标与实际结果
- 总结关键决策
- 提取可复用资产
- 记录失败原因
- 识别下一项目可以改善的流程

## Conversation Contract

复盘不用于寻找责任。

重点是：

- 哪些假设成立
- 哪些判断错误
- 哪些流程有效
- 哪些文档没有价值
- 哪些能力可以迁移
- 下次应该如何更快

## Deliverables

- `RETROSPECTIVE.md`
- `LESSONS_LEARNED.md`
- `REUSABLE_ASSETS.md`
- 最终版 `PROJECT_STATE.md`

## Exit Criteria

- 项目结果已明确
- 经验已记录
- 可复用资产已整理
- 项目被正式标记为 Completed、Paused 或 Archived

---

# 7. 不同项目类型的推荐路径

## 7.1 Personal Tool

推荐路径：

```text
Idea
→ Intent
→ Light Explore
→ Design
→ Planning
→ Build
→ Personal Use
→ Iterate or Done
```

通常可跳过：

- 深度市场研究
- 商业验证
- 营销计划
- 完整发布流程

核心文档：

- `IDEA.md`
- `INTENT.md`
- `DESIGN.md`
- `TICKETS/`
- `REPO_CURRENT_STATE.md`
- `VERIFICATION_PLAN.md`

---

## 7.2 Public Project

推荐路径：

```text
Idea
→ Intent
→ Explore
→ Light Validate
→ Design
→ Planning
→ Build
→ Public Launch
→ Iterate
```

核心文档：

- `README.md`
- `PROJECT_PROFILE.md`
- `RESEARCH.md`
- `DESIGN.md`
- `AGENTS.md`
- `TICKETS/`
- `PUBLISH_CHECKLIST.md`
- `CHANGELOG.md`

---

## 7.3 Business Product

推荐路径：

```text
Idea
→ Intent
→ Explore
→ Validate
→ Design
→ Planning
→ Build
→ Launch
→ Iterate
→ Scale or Archive
```

核心文档：

- `PROBLEM.md`
- `USER_NOTES.md`
- `COMPETITORS.md`
- `VALIDATION_PLAN.md`
- `VALIDATION_RESULTS.md`
- `PRD.md`
- `BUSINESS_MODEL.md`
- `ROADMAP.md`
- `LAUNCH_PLAN.md`
- `METRICS.md`

---

## 7.4 Content Project

推荐路径：

```text
Idea
→ Intent
→ Audience Explore
→ Content Design
→ Production Planning
→ Produce
→ Publish
→ Analyze
→ Continue or Archive
```

核心文档：

- `CONTENT_BRIEF.md`
- `AUDIENCE.md`
- `CONTENT_STRUCTURE.md`
- `SCRIPT.md`
- `PRODUCTION_PLAN.md`
- `PUBLISH_CHECKLIST.md`
- `PERFORMANCE_REVIEW.md`

---

## 7.5 Learning Project

推荐路径：

```text
Idea
→ Learning Intent
→ Scope
→ Learning Plan
→ Practice
→ Build Demonstration
→ Review
```

核心文档：

- `LEARNING_GOAL.md`
- `CURRICULUM.md`
- `PRACTICE_LOG.md`
- `DEMO_PROJECT.md`
- `LESSONS_LEARNED.md`

---

# 8. 文档体系

系统采用两层文档结构。

---

## 8.1 Framework Layer

Framework Layer 用于描述项目孵化器本身。

建议结构：

```text
Project-Incubator/
├── README.md
├── VISION.md
├── PRINCIPLES.md
├── WORKFLOW.md
├── PHASES.md
├── ROLES_AND_CONTRACTS.md
├── PROJECT_TYPES.md
├── DOCUMENT_SYSTEM.md
├── STATE_MODEL.md
├── TEMPLATES/
├── PLAYBOOKS/
└── PROJECTS/
```

各文档职责：

### `README.md`

说明这套系统是什么、适合谁、如何开始。

### `VISION.md`

说明为什么需要这套系统，以及长期希望形成什么能力。

### `PRINCIPLES.md`

定义系统不可轻易改变的设计原则。

### `WORKFLOW.md`

描述整体生命周期和阶段之间的关系。

### `PHASES.md`

完整定义每个 Phase 的目标、角色、对话契约、交付物和退出条件。

### `ROLES_AND_CONTRACTS.md`

集中说明 Maker、阶段型 AI、AI Builder 的关系，以及通用协作规范。

### `PROJECT_TYPES.md`

定义项目分类和不同项目的推荐路径。

### `DOCUMENT_SYSTEM.md`

定义所有文档的用途、关系、创建条件和更新规则。

### `STATE_MODEL.md`

定义项目状态、阶段切换和项目元数据。

### `TEMPLATES/`

保存所有标准文档模板。

### `PLAYBOOKS/`

保存不同类型项目的执行指南。

### `PROJECTS/`

保存具体项目工作区。

---

## 8.2 Project Workspace Layer

每个具体项目拥有独立工作区。

建议结构：

```text
PROJECTS/
└── project-name/
    ├── README.md
    ├── PROJECT_STATE.md
    ├── 00-idea/
    ├── 01-intent/
    ├── 02-explore/
    ├── 03-validate/
    ├── 04-design/
    ├── 05-planning/
    ├── 06-build/
    ├── 07-launch/
    ├── 08-iterate/
    └── 09-archive/
```

实际项目不需要预先创建所有文档。

系统应根据项目类型和当前阶段，按需生成。

---

# 9. 文档生成原则

## 9.1 不为完整而完整

不是所有项目都需要：

- PRD
- 市场分析
- 技术架构
- 商业模型
- 发布策略

文档只在它能够帮助决策、协作、执行或复盘时才创建。

---

## 9.2 一个事实只保留一个权威来源

例如：

- 当前阶段只记录在 `PROJECT_STATE.md`
- 产品范围只记录在 `SCOPE.md`
- 技术原则只记录在 `AGENTS.md`
- 当前代码状态只记录在 `REPO_CURRENT_STATE.md`

其他文档可以引用，但不应重复维护不同版本。

---

## 9.3 文档必须持续更新

文档不是项目启动时一次性生成的材料。

每完成一个阶段或 Ticket，应更新：

- 项目状态
- 已完成内容
- 当前风险
- 下一步
- 相关决策
- 验证结果

---

## 9.4 文档必须服务于 AI 执行

文档内容需要明确、可操作。

避免只有愿景、口号和抽象描述。

尤其是执行文档，应包含：

- 明确目标
- 输入和输出
- 范围限制
- 验收标准
- 验证方法
- 依赖和风险

---

# 10. 阶段切换机制

项目默认由当前 Phase 推动。

阶段切换需要满足以下规则：

1. AI 总结当前阶段成果。
2. AI 对照 Exit Criteria 检查完成情况。
3. 未完成项被明确列出。
4. Maker 决定：
   - 继续当前阶段
   - 带着已知风险进入下一阶段
   - 返回前一阶段
   - 跳过某一阶段
   - 暂停项目
   - 归档项目
5. 更新 `PROJECT_STATE.md`。
6. AI 切换到新阶段对应的角色和对话契约。

AI 不应在未经说明的情况下私自切换阶段。

---

# 11. 项目共创会话规范

每次恢复一个项目时，AI 应优先确认：

- 项目名称
- 项目类型
- 当前 Phase
- 当前目标
- 最近完成内容
- 当前阻塞项
- 下一项决策

建议每次会话开始时形成简短状态摘要：

```text
当前项目：Podcast Learning Shortcut
项目类型：Personal Tool
当前阶段：Phase 4 — Design
当前目标：确定文本输入与总结输出流程
本轮 AI 身份：Workflow Designer
本轮不处理：商业化、公开发布、视觉品牌
本轮预期输出：DESIGN.md v1
```

这样，AI 可以在每次交流中自动进入正确角色。

---

# 12. 与规格驱动开发流程的关系

本框架吸收规格驱动开发的以下优点：

- 先设计，再实现
- 使用 `AGENTS.md` 约束 AI
- 将工作拆解为小 Ticket
- 限制每个任务的修改范围
- 为每个任务定义验收标准
- 保留 `REPO_CURRENT_STATE.md`
- 执行完成后进行人工验证
- 不让 AI 一次实现整个项目

但本框架将其扩展到了完整的项目生命周期：

```text
Idea
→ Intent
→ Explore
→ Validate
→ Design
→ Planning
→ Build
→ Launch
→ Iterate
→ Archive
```

因此，规格驱动开发主要存在于：

```text
Design
→ Planning
→ Build
```

它是项目孵化器的重要组成部分，但不是整个项目孵化流程的全部。

---

# 13. 系统的核心创新

Project Incubator 不只是规定项目应该产生哪些文档。

它同时规定：

- 项目当前处于哪个阶段
- Maker 在当前阶段负责什么
- AI 当前应扮演什么角色
- 当前阶段应该如何对话
- 哪些问题现在不应讨论
- 必须完成哪些交付物
- 满足什么条件才能继续

因此，本系统中的 Phase 可以表达为：

```text
Phase
=
Objective
+
Maker Role
+
AI Role
+
Conversation Contract
+
Deliverables
+
Exit Criteria
```

这是整套系统最核心的结构。

---

# 14. 最终愿景

Project Incubator 的目标，不是让每个想法都变成创业项目。

它也不是要求 Maker 成为全职产品经理、开发者或市场人员。

它希望帮助 Maker 建立一种长期能力：

> 能够持续发现问题、表达想法、组织 AI、做出取舍，并把想法变成真实作品。

这些作品可能很小，只解决 Maker 自己的问题。

也可能逐步扩展为开源项目、内容品牌或商业产品。

无论规模如何，系统都应帮助 Maker：

- 降低启动成本
- 减少流程混乱
- 控制项目复杂度
- 保持 AI 协作稳定
- 提高完成和发布概率
- 沉淀可以复用的经验

Project Incubator 最终要构建的，不只是一个项目流程。

而是一套属于 Maker 自己的创造者操作系统。
