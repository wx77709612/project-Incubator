# Architecture Decisions

## Decision 001
### Project Incubator 本身是一个项目

决定：

Project Incubator 自己也按照项目方式孵化。

原因：

避免只设计方法论，不验证方法论。

---

## Decision 002
### Framework 属于 Project Incubator 系统

决定：

Framework 是 Project Incubator 的核心资产。

未来被孵化项目：

不复制 Framework。

它们只是消费 Framework。

---

## Decision 003
### Personal Tool 是第一优先级

决定：

Project Incubator 第一目标：

服务未来的自己。

不是优先做公开产品。

未来可能：

Skill 化。

---

## Decision 004
### AI Role 必须绑定 Phase

决定：

AI 不使用固定 Assistant 身份。

AI 根据当前 Phase 切换角色。

例如：

Phase 0:
Idea Facilitator

Phase 4:
Architect

Phase 6:
Engineering Lead

---

## Decision 005
### Documents Drive Projects

决定：

项目不能依赖聊天记录。

重要状态和决策必须文档化。

---

## Decision 006
### 不追求所有项目完整流程

决定：

不同项目类型可以跳过部分 Phase。

Personal Tool 不一定需要商业验证。

Business Product 需要更完整验证。

---

## Decision 007
### 项目文档语言规范

决定：

所有 Markdown 正文默认使用中文。

文件名、代码、标准技术文件名可以保留英文。

原因：

Project Incubator 面向中文 Maker 使用，
同时需要兼容 Codex 等工程工具规范。

---

## Decision 008
### 项目文档采用状态入口与 Phase 目录相结合的结构

决定：

- `DOCS/PROJECT_STATE.md` 是固定状态入口和当前项目状态的唯一权威来源；
- 各 Phase 交付物存放在对应的 `DOCS/<phase>/` 目录；
- Phase 目录按需创建，不预先创建全部空目录；
- 文档保留在其所有者 Phase 的目录中，后续 Phase 通过引用复用；
- 同一事实只保留一个权威文档，不在后续阶段复制维护；
- 推翻前序结论时，必须显式回退或执行经 Maker 确认的受控变更；
- `PROJECT_STATE.md` 维护当前权威文档集合和准确路径。

原因：

兼顾固定恢复入口、阶段归属、跨阶段复用和长期可维护性，避免 AI 依赖目录扫描或聊天记忆猜测上下文。

---

## Decision 009
### Agent 启动采用状态驱动协议

决定：

任何 AI Agent 开始或恢复项目工作时，必须先读取根目录 `AGENTS.md` 和 `DOCS/PROJECT_STATE.md`，再读取架构决策、当前 Phase 规则及状态文件列出的权威文档。

Maker 是项目的人类所有者和最终决策者。AI 的当前角色由 `PROJECT_STATE.md` 中记录的 Phase 决定，并受 `FRAMEWORK/Role-System.md` 与 `FRAMEWORK/Phase-System.md` 约束。

AI 不得依赖聊天记录、模糊搜索或自行推断来替代项目状态，不得未经 Maker 确认切换 Phase。

原因：

确保跨会话、跨 Agent 和未来 Skill 化后仍能确定性恢复项目上下文、角色、文档输入和下一步。
