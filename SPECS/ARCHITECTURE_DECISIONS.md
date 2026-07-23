# Architecture Decisions

## 1. 这个文档给 AI 的作用

本文档是 Project Incubator 的 AI 越界防护清单。AI 读取它不是为了了解历史，而是为了知道：

- 什么时候必须停下来；
- 什么事情不得静默执行；
- 如果要改变边界，必须让 Maker 明确确认什么。

本文档不保存当前项目状态，不替代执行步骤，不记录普通协作纠偏。当前状态看 `DOCS/PROJECT_STATE.md`；执行协议看 `AGENTS.md`；Phase、角色和文档规则看 `FRAMEWORK/`。

## 2. 写入门槛

一条内容只有同时满足以下条件，才适合进入本文档：

- 它会长期约束多个任务、多个 Phase 或未来项目；
- 它能让 AI 在某类任务中明确停下来、不得做某事，或必须请求 Maker 决定；
- 它不能更合适地放在 `AGENTS.md`、`FRAMEWORK/`、`DOCS/PROJECT_STATE.md` 或当前 Phase 文档中。

AI 不得自行新增、删除或修改本文档中的边界。需要调整时，必须先说明影响并等待 Maker 明确确认。

## 3. 快速索引

| 边界 | AI 何时必须检查 |
| --- | --- |
| Decision 001：Maker 决策权与 Phase 边界 | 涉及 Phase、AI 角色、项目方向、目标用户、成功标准、验收或范围变化 |
| Decision 002：文档与状态是唯一恢复依据 | 涉及状态恢复、权威文档、阶段完成判断、文档移动/替代/写回 |
| Decision 003：Framework 与项目实例分离 | 涉及 Framework、模板、Skill 资产、未来项目工作区或项目实例化 |
| Decision 004：流程深度必须按项目与任务自适应 | 涉及跳过/加深 Phase、任务规划深度、Personal Tool 是否需要重型验证 |
| Decision 005：Git 写操作必须受里程碑与 Maker 验收门约束 | 涉及分支、暂存、提交、推送、合并、Diff 验收或 Git 闭环 |

---

## Decision 001：Maker 决策权与 Phase 边界

### AI 什么时候必须停下来

- 想切换、跳过、返回、暂停或归档 Phase。
- 想改变当前 AI 角色、项目方向、目标用户、成功标准、当前主要目标或验收方式。
- 想把当前 Project Incubator 从 Personal Tool / 自用验证方向扩展为公开产品、商业产品、团队平台或增长项目。
- 想把 AI 的分析、建议、实现结果或测试结果当作 Maker 验收结论。

### AI 不得做什么

- 不得未经 Maker 确认切换 Phase。
- 不得未经 Maker 确认扩大项目范围、目标用户、公开程度或商业化目标。
- 不得以固定 Assistant 身份覆盖当前 Phase 规定的 AI 角色。
- 不得替 Maker 作出方向、范围、成功标准、阶段切换或最终验收决定。

### 改变这条边界需要 Maker 确认什么

- Maker 明确确认要改变项目方向、目标用户、公开程度、商业化目标或验收标准。
- Maker 明确确认要改变 Phase 切换规则、AI 角色边界或 Maker 最终决策权。

### 权威来源

- 当前 Phase 与目标：`DOCS/PROJECT_STATE.md`
- Phase 规则：`FRAMEWORK/Phase-System.md`
- 角色规则：`FRAMEWORK/Role-System.md`
- 当前项目类型与范围：`DOCS/01-intent/PROJECT_PROFILE.md`、`DOCS/04-design/SCOPE.md`

---

## Decision 002：文档与状态是唯一恢复依据

### AI 什么时候必须停下来

- 状态文档缺失、冲突、过期或无法读取。
- 权威文档索引指向不存在、Superseded、Archived 或多个 Active 来源。
- 想通过聊天记忆、目录扫描或 Framework 骨架判断当前项目状态。
- 想移动、替代、删除、合并或改变某个权威文档的职责。
- 想声明某个 Phase 已完成、可以跳过或可以进入下一 Phase。

### AI 不得做什么

- 不得依赖聊天记录作为唯一上下文。
- 不得通过递归扫描目录猜测当前权威文档集合。
- 不得复制同一事实到多个文档中分别维护。
- 不得把当前状态、阶段正文、执行协议和长期架构边界混写到同一个文档。
- 不得用已有 `FRAMEWORK/` 文件证明 Project Incubator 的前序 Phase 已完成。
- 不得在没有对应 Phase 文档和 Maker 验收的情况下声称阶段完成。

### 改变这条边界需要 Maker 确认什么

- Maker 明确确认状态入口、权威文档集合、目录结构或文档所有权发生变化。
- Maker 明确确认要推翻前序结论、替代权威文档或迁移某个事实的权威来源。
- Maker 明确确认某个 Phase 可以在证据不足时跳过、回退或带风险推进。

### 权威来源

- 状态入口：`DOCS/PROJECT_STATE.md`
- Agent 协议：`AGENTS.md`
- 文档规则：`FRAMEWORK/Document-System.md`
- 阶段文档：`DOCS/<phase>/`

---

## Decision 003：Framework 与项目实例分离

### AI 什么时候必须停下来

- 想为未来项目复制一整套 Framework。
- 想在本仓库建立集中保存未来项目的 `PROJECTS/` 目录。
- 想让未来具体项目拥有、修改或分叉自己的 Framework。
- 想改变 Framework、模板、Skill 资产和项目实例之间的归属关系。

### AI 不得做什么

- 不得把未来具体项目放进 Project Incubator 仓库的集中 `PROJECTS/` 目录。
- 不得让未来项目复制并维护私有 Framework 分叉。
- 不得把 Project Incubator 当前项目状态当作未来项目状态来源。
- 不得把模板实例文件和 Framework 源文件混为一谈。

### 改变这条边界需要 Maker 确认什么

- Maker 明确确认未来项目工作区位置或创建方式。
- Maker 明确确认 Framework 是否允许被复制、分叉或由具体项目拥有。
- Maker 明确确认模板、Skill 资产和项目实例之间的新归属关系。

### 权威来源

- Framework 规则：`FRAMEWORK/`
- 文档归属：`FRAMEWORK/Document-System.md`
- 模板资产：`TEMPLATES/`
- 当前 Skill 设计：`DOCS/04-design/SKILL_DESIGN.md`

---

## Decision 004：流程深度必须按项目与任务自适应

### AI 什么时候必须停下来

- 想要求所有项目完整走完 Phase 0–9。
- 想要求所有任务都创建独立设计文档或实施计划。
- 想为了形式完整创建无人继续消费的文档。
- 想把 Personal Tool 强制升级为 Business Product 式的市场、付费或增长验证。
- 想跳过、返回、加深、简化或带风险推进某个 Phase。

### AI 不得做什么

- 不得机械套用完整流程。
- 不得默认轻量任务需要长期设计记录或实施计划。
- 不得用形式完整替代真实决策价值。
- 不得把项目类型、风险、依赖关系和 Maker 验收对象之外的因素作为加重流程的理由。

### 改变这条边界需要 Maker 确认什么

- Maker 明确确认当前项目或任务需要更轻、更重、跳过、回退或带风险推进。
- Maker 明确确认 Personal Tool 要改走公开产品、商业产品或其他更重流程。
- Maker 明确确认某个临时任务规则具有长期复用价值，值得进入 Framework、模板或本边界清单。

### 权威来源

- Phase 规则：`FRAMEWORK/Phase-System.md`
- 执行规则：`AGENTS.md`
- 当前项目类型：`DOCS/01-intent/PROJECT_PROFILE.md`
- 当前状态：`DOCS/PROJECT_STATE.md`

---

## Decision 005：Git 写操作必须受里程碑与 Maker 验收门约束

### AI 什么时候必须停下来

- 想创建、切换、删除或清理分支。
- 想暂存、提交、推送、合并、变基、重写历史或修改远端状态。
- 当前工作区、暂存区、未推送提交、远端同步状态或未合并分支不清楚。
- 当前分支不属于本任务，或上一任务尚未闭环。
- Maker 接受内容方向，但尚未明确授权具体 Git 写操作。

### AI 不得做什么

- 不得在没有检查 Git 状态的情况下开始写入任务。
- 不得把普通 Diff 审阅、状态回写或补充事实单独升级为 Git 里程碑。
- 不得在 Maker 未明确授权具体 Git 操作时，代为暂存、提交、推送、合并或清理分支。
- 不得 force push、重写历史、删除未合并分支、丢弃改动、绕过分支保护或自行处理方向性冲突。
- 不得在远端未同步前启动无关任务、删除任务分支或完成依赖 `main` 稳定检查点的 Phase 切换。

### 改变这条边界需要 Maker 确认什么

- Maker 明确接受里程碑 Diff、要求稳定检查点或批准 Phase 切换。
- Maker 明确授权 AI 执行具体 Git 动作、目标对象和范围。
- Maker 明确确认在网络故障或远端未同步情况下继续同一范围内工作。

### 权威来源

- Git 执行协议：`AGENTS.md`
- 当前任务状态：`DOCS/PROJECT_STATE.md`
