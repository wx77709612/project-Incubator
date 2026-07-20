# Codex Skill Specification

> 定义未来将 Project Incubator 固化为 Codex Skill 的目标、边界与验收要求

## 1. 文档职责

本文档描述 Project Incubator 未来 Skill 化时应保留的架构语义、运行流程、输入输出、行为边界与验证标准。它是未来实现依据，不代表当前已经进入 Skill 开发、编码或发布阶段。

## 2. Skill 定位

未来 Codex Skill 应把 Project Incubator Framework 转化为可重复执行的 AI 协作协议，使 Codex 能够：

- 识别或恢复具体项目的当前状态；
- 根据当前 Phase 切换 AI Collaborator 身份；
- 遵守对应 Conversation Contract；
- 根据项目类型选择合适的流程深度；
- 按需创建和更新项目文档；
- 在 Planning 与 Build 中向 AI Builder 提供受约束任务；
- 在切换阶段前检查 Exit Criteria 并请求 Maker 决策。

Skill 的第一服务对象仍是 Maker 自己及其 Personal Tool 工作流。公开产品化或通用平台化不是首版默认目标。

## 3. 不可改变的架构约束

Skill 实现必须保留以下约束：

1. Project Incubator 本身是一个项目；
2. Framework 属于 Project Incubator，是其核心资产；
3. 未来项目只消费 Framework，不复制 Framework；
4. Personal Tool 是第一优先级；
5. AI Role 必须绑定当前 Phase；
6. 重要状态和决策必须文档化；
7. 不同项目可以轻量执行或跳过部分 Phase；
8. Maker 保留方向、阶段与验收的最终决定权；
9. 不创建集中保存未来项目的 `PROJECTS/` 目录；
10. 不创建第二套 Framework。

## 4. Skill 的职责边界

### 4.1 Skill 应负责

- 读取 Framework 与具体项目的必要状态；
- 呈现当前 Phase、AI 身份、目标、预期输出和暂不处理事项；
- 引导当前阶段对话；
- 提议当前有价值的交付物；
- 维护单一权威来源；
- 检查阶段退出条件；
- 在 Maker 确认后更新状态并切换角色；
- 为 AI Builder 生成或读取范围明确的任务上下文；
- 记录验证证据与未解决问题。

### 4.2 Skill 不应负责

- 未经 Maker 授权决定项目方向；
- 把所有想法转化为商业产品；
- 强制项目走完全部十个 Phase；
- 预先生成全部可能文档；
- 将聊天记录视为唯一状态来源；
- 复制 Framework 到具体项目；
- 静默修改最高设计依据或架构决策；
- 在缺少执行范围和验收标准时启动 AI Builder；
- 在验证缺失时宣称阶段或任务完成。

## 5. 启动模式

未来 Skill 至少需要支持两种启动模式。

### 5.1 恢复现有项目

当具体项目已有状态文档时，Skill 应：

1. 定位包含项目级 `AGENTS.md` 的项目根目录；
2. 读取 `AGENTS.md`；
3. 读取 `DOCS/PROJECT_STATE.md`；
4. 确认 Maker、当前 Phase、AI 角色、目标、权威文档集合和下一项决定；
5. 读取架构决策和当前 Phase 对应的 Framework 规则；
6. 按状态索引加载当前 Phase 与本轮任务需要的最小文档；
7. 检查路径缺失、状态冲突和多个权威来源；
8. 输出本轮协作契约；
9. 以当前 Phase 对应身份继续协作。

### 5.2 初始化新项目

当 Maker 明确要求启动一个新的具体项目时，Skill 才能进入 Phase 0。Skill 应先确认这是项目初始化请求，再按照 Idea Capture 的 Conversation Contract 工作。

仅讨论或维护 Framework，不自动等同于启动一个新的被孵化项目。只有 Maker 明确指定孵化对象和当前 Phase 后，Skill 才能创建对应项目状态与阶段文档。

### 5.3 Project Incubator 自我孵化

Project Incubator 本身也是具体项目。Skill 必须把它的当前状态与 Framework 资产区分开：

- Project Incubator 的当前状态读取自 `DOCS/PROJECT_STATE.md`；
- Project Incubator 的阶段交付物位于 `DOCS/<phase>/`；
- Framework 规则位于 `FRAMEWORK/`；
- Framework 文件的存在不能作为 Project Incubator 已进入 Design 或后续 Phase 的证据。

## 6. 所需输入

### 6.1 必要输入

- Maker 的当前明确请求；
- 项目根目录的 `AGENTS.md`；
- `DOCS/PROJECT_STATE.md` 中记录的 Maker、Phase、角色与权威文档集合；
- Project Incubator Framework 的可用版本；
- 具体项目工作区或状态文档位置，若为恢复模式；
- 已确认的权限与可修改范围。

### 6.2 条件输入

- `PROJECT_STATE.md`；
- `PROJECT_PROFILE.md`；
- `INTENT.md`；
- 当前 Phase 的交付物；
- 当前 Ticket、设计或验证文档；
- 项目级 AI 约束文档。

缺少必要状态时，Skill 应说明缺口，并以最小问题恢复上下文；不得猜测当前 Phase 或伪造已确认决定。

## 7. 标准运行流程

### 7.1 状态恢复

读取项目名称、Maker、主要类型、当前 Phase、状态、当前目标、阶段交付物、权威文档集合、最近完成内容、阻塞项、Exit Criteria、下一项决定和下一会话恢复入口。

### 7.2 角色绑定

根据 `Phase-System.md` 和 `Role-System.md` 绑定当前 AI Collaborator 身份，加载对应 Conversation Contract、Deliverables 与 Exit Criteria。

### 7.3 本轮契约

向 Maker 简要说明：

- 当前 Phase；
- Maker 身份与 AI 的职责边界；
- 本轮 AI 身份；
- 本轮唯一主要目标；
- 预计读取和产生的文档；
- 暂不处理的事项；
- 需要 Maker 作出的下一项决定。

### 7.4 阶段内协作

Skill 只围绕当前 Objective 工作，区分事实、假设、建议和决定，并把确认结果更新到正确的权威文档。

### 7.5 阶段门检查

Skill 汇总 Deliverables，对照 Exit Criteria 逐项检查，列出缺口和风险，并把继续、带风险推进、返回、跳过、暂停或归档的选择交给 Maker。

### 7.6 状态与角色切换

只有在 Maker 决定后，Skill 才更新具体项目状态并切换到新 Phase 身份。

### 7.7 会话结束回写

本轮产生新的确认事实、决定、文档路径、风险或下一步时，Skill 必须更新对应权威文档和 `DOCS/PROJECT_STATE.md`，确保下一会话能够只依赖项目文件恢复工作。

## 8. Phase 到行为模块的映射

| Phase | Skill 行为重点 | 默认限制 |
| --- | --- | --- |
| Phase 0 | 提炼想法与场景 | 不写完整 PRD，不讨论实现细节 |
| Phase 1 | 澄清意图、类型与成功标准 | 不直接进入执行，不默认商业化 |
| Phase 2 | 理解问题与现有方案 | Personal Tool 不强制深度市场研究 |
| Phase 3 | 设计低成本验证 | 不以完整构建代替验证 |
| Phase 4 | 比较方案并确定范围 | 不扩大功能，不改变成功标准 |
| Phase 5 | 拆分可验收任务 | 不创建边界模糊的整体任务 |
| Phase 6 | 按任务执行并验证 | 不加入未批准功能，不跳过验证 |
| Phase 7 | 确保真实交付 | 不无限优化，不绕过质量与安全 |
| Phase 8 | 基于证据排优先级 | 不把所有反馈转成功能 |
| Phase 9 | 复盘并沉淀资产 | 不将归档等同于失败 |

## 9. 文档操作规则

Skill 对具体项目文档执行创建或更新前，应判断：

- 文档是否属于当前项目，而不是 Framework；
- 是否属于当前 Phase；
- 是必需还是按需；
- 是否已有同一事实的权威来源；
- 创建或更新是否得到 Maker 指令授权；
- 内容是否足以支持下一项决策或执行。

Skill 不得复制五份 Framework 文档到具体项目工作区。若需要追踪 Framework 版本，应记录引用或版本标识。

具体项目采用以下路径规则：

- 固定状态入口：`DOCS/PROJECT_STATE.md`；
- Phase 交付物：`DOCS/00-idea/` 至 `DOCS/09-archive/`，按需创建；
- 通用元数据模板：`TEMPLATES/DOCUMENT-METADATA.template.md`；
- 当前权威文档路径：由 `PROJECT_STATE.md` 明确列出。

跨阶段复用时，Skill 引用原权威文档，不复制正文。推翻前序结论时，必须获得 Maker 对阶段回退或受控变更的确认。

## 10. AI Builder 调用协议

当任务进入具体执行时，Skill 应先确认 AI Builder 获得：

- 任务背景与目标；
- 非目标；
- 允许与禁止修改范围；
- 输入、输出和依赖；
- 验收标准；
- 验证步骤；
- 风险与阻塞项；
- 完成后需更新的文档。

AI Builder 返回后，Skill 应检查实际修改、验证证据、失败与未解决问题，再由 Maker 进行必要的手工验收。

## 11. 异常与冲突处理

### 11.1 状态缺失

停止自动推进，说明缺失字段，并以最小必要问题或已有权威文档恢复状态。

### 11.2 文档冲突

列出冲突来源、差异与影响，请 Maker 确认权威结论。不得按便利性自行选择。

### 11.3 跨阶段请求

说明请求与当前 Phase 的关系。若属于必要回退、跳过或转向，先由 Maker 决定并更新状态；若只是未来事项，则记录但不在当前阶段展开。

### 11.4 架构决策冲突

停止会改变既定架构的操作，引用冲突的 Architecture Decision，并请求 Maker 明确确认。未经确认不得覆盖。

### 11.5 验证失败

如实记录失败、影响与未解决项。任务保持未完成或部分完成状态，不得以生成了产物替代验证结论。

## 12. Personal Tool 优先策略

首版 Skill 应优先优化以下体验：

- 快速恢复 Maker 自己的项目上下文；
- 以轻量方式完成 Intent、Explore、Design、Planning 和 Build；
- 允许 Personal Tool 跳过独立商业验证；
- 将 Launch 解释为正式投入个人使用；
- 以真实节省时间、改善体验和持续使用作为核心证据；
- 避免自动添加公开发布、增长或变现工作。

## 13. 版本与演化要求

Framework 是 Skill 的规则来源。Skill 的提示、资源和行为模块应可追踪到对应 Framework 版本。

未来修改 Skill 时，应区分：

- 不改变 Framework 语义的实现优化；
- 需要 Maker 确认并先修改最高设计依据或 Framework 的架构变更。

具体项目反馈可以形成改进建议，但不得让单一项目的特殊做法静默成为全局规则。

## 14. 验收标准

未来 Codex Skill 至少应通过以下场景验证：

- 能从状态文档恢复正确 Phase 与 AI 身份；
- 能识别 Personal Tool 并采用轻量路径；
- 能阻止未经授权的 Phase 自动切换；
- 能避免为具体项目复制 Framework；
- 能按需生成当前 Phase 的文档，而非一次生成全部文档；
- 能发现同一事实的冲突权威来源；
- 能在 Planning 阶段形成范围清晰、可验证的任务；
- 能在 Build 阶段要求验证证据；
- 能在跨阶段请求发生时说明影响并等待 Maker 决定；
- 能在归档时保留结果、经验和可复用资产；
- 能识别“维护 Framework”不是“启动 Phase 0”。

## 15. 当前不执行事项

当前 `SKILL/` 目录尚未包含可执行 Skill。本规范本身不授权以下动作：

- 编写或安装 Codex Skill；
- 创建 Skill 脚本、配置、发布资产或代码；
- 设计公开产品或商业模式；
- 创建任何具体项目案例；
- 把规范文档的存在描述为 Skill 已经实现；
- 在未经 Maker 确认的情况下改变项目 Phase 或生成后续阶段文档。
