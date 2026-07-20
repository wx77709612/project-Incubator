# Project Incubator

> AI 驱动的创造者项目孵化系统

## 当前状态

Project Incubator 同时是一套项目孵化 Framework，也是一个正在使用自身 Framework 孵化的真实项目。

| 项目字段 | 当前值 |
| --- | --- |
| 当前 Phase | Phase 0 — Idea Capture |
| Maker | 当前项目的人类所有者 |
| 当前 AI 角色 | Idea Facilitator（创意引导者） |
| 当前目标 | 确认原始想法、触发原因和真实使用场景 |
| 当前状态来源 | `DOCS/PROJECT_STATE.md` |

现有 Framework 文件是用于自我孵化的初始骨架，不代表项目已经完成前序阶段，也不代表 Framework 已经最终定稿。

## 一句话介绍

Project Incubator 通过阶段化流程、结构化文档和随 Phase 切换的 AI 角色，帮助 Maker 把想法逐步转化为真实作品。

第一优先级是成为服务 Maker 自己的 Personal Tool。未来可能固化为 Codex Skill，但当前尚未进入 Skill 实现阶段。

## 如何开始

### Maker

先阅读：

1. `DOCS/PROJECT_STATE.md`，了解当前阶段、目标和下一项决定；
2. `DOCS/00-idea/IDEA.md`，审阅当前 Phase 0 想法草案；
3. `SPECS/ARCHITECTURE_DECISIONS.md`，了解已经确认的架构决策。

### AI Agent

必须从根目录 `AGENTS.md` 启动，并严格按照其中的状态驱动协议读取项目状态、当前 Phase 规则和权威文档。不得依赖聊天记录或自行推断阶段。

## 目录结构

| 路径 | 职责 |
| --- | --- |
| `AGENTS.md` | AI Agent 的启动、恢复、执行与回写协议 |
| `SPECS/` | 设计背景和已经确认的架构决策 |
| `FRAMEWORK/` | Phase、角色、文档和未来 Skill 规则 |
| `DOCS/PROJECT_STATE.md` | 当前项目状态的唯一权威来源 |
| `DOCS/<phase>/` | 按需创建的阶段交付物 |
| `TEMPLATES/` | 经过真实使用逐步验证的文档模板 |
| `SKILL/` | 未来 Codex Skill 实现的保留位置；当前未实现 |

未来具体项目拥有自己的独立工作区，只消费 Framework，不复制 Framework，也不集中存放在本仓库的 `PROJECTS/` 目录中。

## 当前权威入口

- 项目状态：`DOCS/PROJECT_STATE.md`；
- Phase 0 想法：`DOCS/00-idea/IDEA.md`；
- Agent 协议：`AGENTS.md`；
- 架构决策：`SPECS/ARCHITECTURE_DECISIONS.md`；
- Framework 总纲：`FRAMEWORK/Project-Incubator-Framework.md`；
- Phase 规则：`FRAMEWORK/Phase-System.md`；
- 文档规则：`FRAMEWORK/Document-System.md`。

## 当前下一步

由 Maker 审阅 `DOCS/00-idea/IDEA.md`，确认：

- 一句话想法是否准确；
- 想法产生原因是否准确；
- 是否已记录至少一个真实使用场景。

完成 Maker 确认前，项目保持在 Phase 0，不自动进入 Phase 1。

## Git 工作方式

- `main` 保存已经验证并由 Maker 接受的稳定检查点；
- 会修改仓库的独立任务使用 `p<当前Phase>/<type>-<topic>` 分支；
- 当前 Phase 读取自 `DOCS/PROJECT_STATE.md`；
- 只读任务不创建分支；
- Agent 在工作区安全时自动创建本地工作分支；
- 新任务开始前检查上一任务是否存在未提交、未推送或未合并状态；
- Agent 完成修改和验证后保留 IDE Diff，等待 Maker 检查；
- Maker 确认 Diff 后，Agent 自动完成工作分支提交与推送、squash 合并、`main` 推送和已合并分支清理；
- Maker 确认前不提交、不推送、不合并；
- Phase 切换经 Maker 接受并合并到 `main` 后，才创建下一 Phase 分支。

当前 Phase 0 的下一项工作分支建议为 `p0/docs-idea-review`。完整规则见 `AGENTS.md` 和 `SPECS/ARCHITECTURE_DECISIONS.md` 的 Decision 008。
