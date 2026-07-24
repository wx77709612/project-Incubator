# Ticket R1-02 - Task Type And Writeback

> Phase 5 - Planning 的 R1 任务类型与写回 Ticket 交付物

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 5 - Planning |
| 文档状态 | Active |
| 权威范围 | Skill 1.0 的任务类型判定、写回触发条件、状态入口收敛和恢复入口检查的任务边界 |
| 消费 Phase | Phase 5-6，按需读取 |
| 更新条件 | Maker 调整任务类型、写回触发条件、状态入口收敛规则或恢复入口要求 |
| 依赖文档 | `DOCS/05-planning/ROADMAP.md`、`DOCS/05-planning/MILESTONES.md`、`DOCS/05-planning/VERIFICATION_PLAN.md`、`DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md`、`DOCS/04-design/PROJECT_STATE_DESIGN.md` |
| 最后更新 | 2026-07-24 |

## 1. 背景

Skill 运行链路需要判断本轮任务属于只读、规划、写入、Builder 执行、阶段门检查、Git 闭环回写或 Prompt 生成。不同类型任务的写回要求不同，不能把所有过程都写入 `PROJECT_STATE.md`。

## 2. 目标

定义任务类型判定与写回触发条件，确保状态入口只保存影响恢复和下一步的事实。

## 3. 非目标

- 不创建脚本；
- 不修改现有 `PROJECT_STATE.md` 模板；
- 不定义全部未来任务类型；
- 不把普通聊天过程写成状态事实。

## 4. 允许范围

- 定义首批任务类型；
- 定义每类任务是否允许写入；
- 定义写入哪些文档；
- 定义 `PROJECT_STATE.md` 收敛检查；
- 定义下一轮恢复入口检查。

## 5. 禁止范围

- 不把状态入口扩展为流水账；
- 不复制 Phase 文档正文到状态入口；
- 不将 Maker 未确认内容写成事实；
- 不改变文档系统规则。

## 6. 输入

- `DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md`
- `DOCS/04-design/PROJECT_STATE_DESIGN.md`
- `DOCS/05-planning/VERIFICATION_PLAN.md`

## 7. 输出

后续 Build Ticket 应产出任务类型与写回规则说明，至少包含：

- 只读任务；
- 文档规划任务；
- 文件写入任务；
- Builder 执行任务；
- 阶段门检查；
- Git 闭环回写；
- Maker 任务 Prompt 生成；
- 分叉处理。

每类任务应说明：是否写回、写回到哪里、何时不写回。

## 8. 验收标准

- 能区分至少 8 类任务；
- 每类任务都有写回规则；
- `PROJECT_STATE.md` 只保存状态、路径、阻塞、下一步或恢复入口变化；
- 覆盖 `VERIFICATION_PLAN.md` 的 S1、S2、S5；
- 不改变既有权威文档职责。

## 9. 验证步骤

1. 用 S2 检查“继续”是否会被正确判定为当前任务推进；
2. 用 S5 检查新想法是否会进入分叉分类而不是直接写入状态；
3. 构造一个文档写入完成场景，检查是否只更新必要状态；
4. 检查输出是否没有将过程细节写入 `PROJECT_STATE.md`。

## 10. 完成后更新

- 如果任务类型或写回规则改变下一步恢复方式，更新 `DOCS/PROJECT_STATE.md`；
- 如发现状态入口字段不足，记录为后续事项，不直接修改 Framework。
