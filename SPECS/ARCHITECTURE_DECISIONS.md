# Architecture Decisions

## 1. 文档职责

本文档只记录 Project Incubator 已由 Maker 确认、不可被 AI 静默改变的架构决定及其原因。

具体操作步骤不在本文重复维护：

- Agent 启动、Git 命令顺序和任务收尾见 `AGENTS.md`；
- Phase 规则见 `FRAMEWORK/Phase-System.md`；
- 角色规则见 `FRAMEWORK/Role-System.md`；
- 文档结构与生命周期见 `FRAMEWORK/Document-System.md`；
- 当前项目状态见 `DOCS/PROJECT_STATE.md`。

---

## Decision 001：Project Incubator 必须孵化自身

### 决定

Project Incubator 本身是一个真实项目，必须按照自身定义的流程推进，并作为 Framework 的首个验证对象。

### 原因

避免只设计方法论而不验证方法论。已有 Framework 文件属于自举骨架，不能作为项目已经完成前序 Phase 的证明。

---

## Decision 002：Framework 属于 Project Incubator

### 决定

Framework 是 Project Incubator 的核心资产，属于 Project Incubator，不属于未来被孵化的具体项目。

未来项目只消费 Framework 定义的流程、角色规则和模板，不复制 Framework，也不在本仓库建立集中保存未来项目的 `PROJECTS/` 目录。

### 原因

避免产生多套相互漂移的 Framework，并保持规则的唯一权威来源。

---

## Decision 003：Personal Tool 是第一优先级

### 决定

Project Incubator 首先服务 Maker 自己，第一目标是成为 Personal Tool，而不是优先成为公开产品或商业产品。

在 Framework 经真实使用验证后，未来可以考虑固化为 Codex Skill。

### 原因

先解决 Maker 的真实问题并降低自用工作流成本，再决定是否扩大使用范围。

---

## Decision 004：协作由 Phase 驱动，Maker 保留最终决定权

### 决定

- AI 不使用永久固定的 Assistant 身份；
- AI 角色、主要目标、Conversation Contract、Deliverables 和 Exit Criteria 由当前 Phase 决定；
- Maker 是项目的人类所有者和最终决策者；
- AI 不得未经 Maker 确认切换 Phase、改变项目方向、修改成功标准或扩大范围。

### 原因

让每个阶段的职责和边界可预测，减少 AI 在长周期项目中的角色混乱与方向漂移。

---

## Decision 005：项目采用文档与状态驱动

### 决定

- 项目不能依赖聊天记录作为唯一上下文；
- `DOCS/PROJECT_STATE.md` 是固定启动入口和当前项目状态的唯一权威来源；
- Agent 必须先读取根目录 `AGENTS.md` 和 `DOCS/PROJECT_STATE.md`，再加载当前 Phase 规则及状态文件列出的权威文档；
- Phase 交付物存放在对应的 `DOCS/<phase>/` 目录，目录按需创建；
- 文档保留在其所有者 Phase 的目录中，后续 Phase 通过准确路径引用；
- 同一事实只保留一个权威文档，不复制维护；
- 推翻前序结论时，必须由 Maker 批准回退或受控变更；
- `PROJECT_STATE.md` 必须维护当前权威文档集合和下一会话恢复入口。

### 原因

确保跨会话、跨 Agent 和未来 Skill 化后都能确定性恢复项目状态，同时避免重复文档和冲突版本。

---

## Decision 006：不同项目采用不同流程深度

### 决定

所有项目共享相同的 Phase 语言，但不要求走完全部 Phase，也不要求每个 Phase 使用相同深度。

Personal Tool 可以轻量执行 Explore，并通常不需要独立商业验证；Business Product 需要更完整的研究、验证和发布流程。

跳过、返回、暂停或带风险推进必须由 Maker 决定并记录到项目状态。

### 原因

避免把个人工具、内容项目、学习项目和商业产品强行套入同一种流程。

---

## Decision 007：Markdown 正文默认使用中文

### 决定

所有 Markdown 正文默认使用中文。文件名、代码、Git 标识和标准技术名词可以保留英文。

### 原因

Project Incubator 面向中文 Maker 使用，同时需要兼容 Codex、Git 和其他工程工具规范。

---

## Decision 008：Git 采用 Phase 感知的任务分支与人工验收闭环

### 决定

- `main` 只保存已经验证并由 Maker 接受的稳定检查点；
- 会修改仓库的独立任务使用 `p<当前Phase>/<type>-<topic>` 工作分支；
- Phase 前缀读取自 `DOCS/PROJECT_STATE.md`，一个分支对应一个可独立审阅和验收的任务；
- 只读任务不创建分支；同一任务续作继续使用原工作分支；
- 新任务开始前，Agent 必须检查工作区、暂存区、未推送提交、远端同步状态和未合并任务分支；
- 发现上一个任务未闭环时，Agent 必须提醒 Maker 先处理，不开始无关写入任务；
- Agent 完成修改、文档回写和验证后，保留未提交 IDE Diff，等待 Maker 检查；
- Maker 明确接受 Diff 后，Agent 才自动完成工作分支提交与推送、squash 合并、`main` 推送和已合并分支清理；
- force push、重写历史、删除未合并分支、丢弃改动、绕过分支保护和方向性冲突处理不属于自动授权；
- Phase 切换在当前分支完成阶段门与状态更新，经 Maker 接受并合并到 `main` 后，再创建下一 Phase 分支。

本次 Git 治理属于基线例外：规则直接保留在 `main` 的未提交 Diff 中，Maker 检查并确认后，由 Agent 创建一次合并后的基线治理提交。此后执行常规分支闭环。

### 原因

Phase 前缀保留项目阶段上下文，任务分支控制修改范围；启动检查防止新任务掩盖旧任务；IDE Diff 验收保护 Maker 的最终决定权；验收后的自动收尾避免任务停留在未提交、未推送或未合并状态。
