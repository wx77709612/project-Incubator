# Ticket R3-02 - Builder Return And Review

> Phase 5 - Planning 的 R3 Builder 返回与验收闭环 Ticket 交付物

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 5 - Planning |
| 文档状态 | Active |
| 权威范围 | Builder 完成任务后返回 Collaborator 视角、报告结果、验证证据、Diff 范围和 Maker 审阅入口的任务边界 |
| 消费 Phase | Phase 5-6，按需读取 |
| 更新条件 | Maker 调整 Builder 完成后报告方式、验证证据、Collaborator 回看、Diff 审阅或状态回写规则 |
| 依赖文档 | `DOCS/05-planning/ROADMAP.md`、`DOCS/05-planning/MILESTONES.md`、`DOCS/05-planning/VERIFICATION_PLAN.md`、`FRAMEWORK/Role-System.md`、`FRAMEWORK/Phase-System.md`、`DOCS/04-design/INTERACTION_DESIGN.md` |
| 最后更新 | 2026-07-24 |

## 1. 背景

Builder 完成任务不等于项目完成。Skill 需要定义 Builder 完成后如何返回 Collaborator 视角，由 Collaborator 检查结果是否符合 Ticket、设计边界和 Maker 验收要求。

## 2. 目标

定义 Builder 完成后的报告、回看、Maker 审阅和状态回写闭环。

## 3. 非目标

- 不执行 Build；
- 不替 Maker 接受 Diff；
- 不自动提交、推送或合并；
- 不宣布 Phase 完成。

## 4. 允许范围

- 定义 Builder 完成报告格式；
- 定义验证证据要求；
- 定义 Collaborator 回看清单；
- 定义 Maker Diff 审阅入口；
- 定义状态回写触发条件。

## 5. 禁止范围

- 不允许 Builder 完成后直接宣布项目完成；
- 不允许未经 Maker 审阅改变任务状态为 Accepted 或 Merged；
- 不允许自动执行 Git 闭环；
- 不允许遗漏失败、风险或未完成项。

## 6. 输入

- `FRAMEWORK/Role-System.md`
- `FRAMEWORK/Phase-System.md`
- `DOCS/04-design/INTERACTION_DESIGN.md`
- `DOCS/05-planning/VERIFICATION_PLAN.md`

## 7. 输出

后续 Build Ticket 应产出 Builder 返回与验收闭环规则，至少包含：

- Builder 实际修改报告；
- 验证命令或手工验证结果；
- 未完成项和风险；
- Diff 范围；
- Collaborator 回看：是否符合 Ticket、设计文档和 Phase 目标；
- Maker 审阅提示；
- 是否需要更新 `PROJECT_STATE.md`。

## 8. 验收标准

- Builder 完成后必须返回 Collaborator 视角；
- Maker 审阅前不得视为完成；
- 覆盖 `VERIFICATION_PLAN.md` 的 S7；
- 状态回写只记录影响恢复、阻塞、下一步或权威路径的变化；
- Git 闭环仍受 Maker 手动验收门约束。

## 9. 验证步骤

1. 用 S7 Builder 完成后场景检查是否回到 Collaborator；
2. 构造一个验证失败场景，检查是否报告失败并保持任务未完成；
3. 构造一个 Diff 等待审阅场景，检查是否不自动提交；
4. 检查状态回写是否没有流水账化。

## 10. 完成后更新

- 如 Maker 接受，后续 Build 协议和 Ticket 模板可消费该闭环；
- 如发现与 Git 手动闭环规则冲突，停止并回到 `AGENTS.md` / Architecture Decision 边界检查。
