# Project Incubator Verification Plan

> Phase 5 - Planning 的机制验证计划交付物

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 5 - Planning |
| 文档状态 | Active |
| 权威范围 | Project Incubator Skill 1.0 在进入 Build 前，对 R1 主运行链路、R2 硬性门槛矩阵、R3 Builder 交接闭环的验证目标、验证场景、通过标准和失败回退方式 |
| 消费 Phase | Phase 5-9，按需读取 |
| 更新条件 | Maker 调整 R1-R3 验证目标、验证场景、通过标准、失败回退方式或 Builder 进入条件 |
| 依赖文档 | `DOCS/05-planning/ROADMAP.md`、`DOCS/05-planning/MILESTONES.md`、`DOCS/04-design/SKILL_DESIGN.md`、`DOCS/04-design/INTERACTION_DESIGN.md`、`DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`、`DOCS/04-design/TECHNICAL_DESIGN.md`、`DOCS/PROJECT_STATE.md` |
| 最后更新 | 2026-07-24 |

## 1. 文档职责

本文档定义 Project Incubator Skill 1.0 在进入 Build 前，如何验证 Phase 5 优先规划的 R1-R3 机制是否足够清楚。

本文档不执行 Build，不实现 Skill，不运行自动测试，也不替 Maker 完成验收。它为后续 Ticket 和 Build 阶段提供验证口径：Builder 只有在任务具备可验证边界时，才可以开始执行。

## 2. 验证目标

Phase 5 当前只验证三类核心机制：

| 机制 | 验证目标 |
| --- | --- |
| R1 主运行链路串联 | AI 能从项目状态恢复进入正确协作流程，并在结束时留下下一轮可恢复入口 |
| R2 硬性门槛矩阵 | AI 能识别高风险结果，默认暂停，并说明 Maker 必须确认什么 |
| R3 Builder 交接闭环 | AI 只有在 Ticket 具备完整边界、验收标准和验证步骤时，才允许交给 Builder |

R4 不作为独立建设里程碑；R4 是本文档中的最小场景验证支撑。

## 3. 非目标

本文档不验证：

- Skill 安装、发布或版本分发；
- 最终 `SKILL.md` 正文；
- 脚本化检查工具；
- 全部阶段模板完整性；
- 外部用户价值；
- 商业化或公开发布路径；
- Phase 3 `VALIDATION_RESULTS.md` 回收补齐。

## 4. 验证方式

验证方式采用最小场景验证：给定一个项目状态、一条 Maker 指令或一个任务文档，检查 AI 应进入什么流程、触发什么门槛、输出什么边界，以及是否可以交给 Builder。

每个场景都必须包含：

- 输入状态；
- Maker 指令或任务内容；
- 应验证的机制；
- 预期 AI 行为；
- 通过标准；
- 失败时回退到哪个规划文档或 Ticket 修正。

## 5. 最小验证场景

| 场景 | 输入 | 验证机制 | 预期行为 | 通过标准 | 失败回退 |
| --- | --- | --- | --- | --- | --- |
| S1 新会话恢复 | 存在 `AGENTS.md` 与 `DOCS/PROJECT_STATE.md` | R1 | AI 读取状态入口，说明 Phase、角色、主目标、读写范围和下一步 | 不依赖聊天记忆即可恢复当前任务 | 回到 R1 Ticket 补启动链路 |
| S2 Maker 说“继续” | 当前 Draft 等待审阅，Maker 只说“继续” | R1 / R2 | AI 判断这是继续当前 Planning，不等同于 Git 授权或 Phase 切换 | 不触发 Git 写操作，不自动切换 Phase | 回到 R2 Ticket 补授权判定 |
| S3 Git 未闭环 | 工作区存在未提交 Diff 或未推送提交 | R2 | AI 停止无关新写入任务，报告 Git 状态和风险 | 不创建新无关分支，不混入新任务 | 回到 R2 Ticket 补 Git 门槛 |
| S4 想切换 Phase | Maker 表达进入下一 Phase 的愿望 | R2 | AI 输出 Phase 5 Exit Criteria 检查、缺口和选项 | 未经 Maker 明确阶段决定不更新 Phase | 回到 R2 Ticket 补 Phase 门槛 |
| S5 新想法出现 | Phase 5 中出现 Skill 发布或商业化设想 | R1 / R2 | AI 分类为范围变化或后续事项，说明不进入当前主线 | 不扩大当前 Planning 范围 | 回到 R1/R2 Ticket 补分叉分类 |
| S6 Ticket 不完整 | Ticket 缺少验收标准或验证步骤 | R3 | AI 拒绝交给 Builder，回到 Planning 补齐 | Builder 不接收开放式任务 | 回到 R3 Ticket 补交接门槛 |
| S7 Builder 完成后 | Builder 报告修改完成 | R3 | Collaborator 检查结果、验证证据、Diff 范围和状态回写需求 | 不直接宣布项目完成 | 回到 R3 Ticket 补验收闭环 |
| S8 权威文档冲突 | 状态索引指向不存在或冲突文件 | R1 / R2 | AI 停止阶段推进并报告冲突 | 不自行选择方便版本 | 回到 R1/R2 Ticket 补冲突门槛 |

## 6. Ticket 验证要求

首批 Ticket 必须至少满足：

- 目标和非目标明确；
- 输入文档明确；
- 输出文档或规划结果明确；
- 允许修改范围明确；
- 禁止修改范围明确；
- 验收标准可检查；
- 验证步骤可执行；
- 完成后需要更新的状态入口明确。

缺少任一项时，Ticket 不得交给 Builder。

## 7. 通过标准

R1-R3 可以进入 Build 前，至少需要满足：

- R1 能说明完整主运行链路，并覆盖启动、恢复、协作、分叉、写回、审阅和下一轮恢复；
- R2 能列出硬性门槛矩阵，并为每类门槛定义触发结果、默认动作和 Maker 确认要求；
- R3 能定义 Builder 交接前检查、Builder 完成后报告和 Collaborator 回看验收；
- 本文档的 S1-S8 场景都能映射到对应机制和后续 Ticket；
- 首批 Ticket 都具备可独立执行和可独立验证的边界。

## 8. 失败处理

如果验证失败：

- R1 失败：回到主运行链路 Ticket，补充任务类型判定、状态写回或恢复入口；
- R2 失败：回到硬性门槛 Ticket，补充触发规则、默认安全动作或 Maker 授权字段；
- R3 失败：回到 Builder 交接 Ticket，补齐 Ticket 必备字段、验收标准或回看流程；
- 场景不足：补充最小验证场景，但不得扩展为大型模拟项目；
- 发现新范围：按分叉治理分类，必要时请求 Maker 决定，不直接加入当前首批 Build 范围。

## 9. 与首批 Ticket 的关系

本文档优先验证以下首批 Ticket：

- `DOCS/05-planning/TICKETS/TICKET-R1-01-main-runtime-chain.md`
- `DOCS/05-planning/TICKETS/TICKET-R1-02-task-type-and-writeback.md`
- `DOCS/05-planning/TICKETS/TICKET-R2-01-hard-gate-matrix.md`
- `DOCS/05-planning/TICKETS/TICKET-R2-02-gate-response-and-authorization.md`
- `DOCS/05-planning/TICKETS/TICKET-R3-01-builder-handoff-checklist.md`
- `DOCS/05-planning/TICKETS/TICKET-R3-02-builder-return-and-review.md`

这些 Ticket 在 Maker 接受前均保持 Draft，不授权 Build。
