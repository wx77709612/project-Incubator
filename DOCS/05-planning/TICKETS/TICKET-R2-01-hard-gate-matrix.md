# Ticket R2-01 - Hard Gate Matrix

> Phase 5 - Planning 的 R2 硬性门槛矩阵 Ticket 交付物

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 5 - Planning |
| 文档状态 | Active |
| 权威范围 | Skill 1.0 硬性门槛矩阵的任务边界、门槛类型、触发结果、默认动作、Maker 确认要求和验证步骤 |
| 消费 Phase | Phase 5-6，按需读取 |
| 更新条件 | Maker 调整硬性门槛类型、触发规则、默认动作、确认要求或验证方式 |
| 依赖文档 | `DOCS/05-planning/ROADMAP.md`、`DOCS/05-planning/MILESTONES.md`、`DOCS/05-planning/VERIFICATION_PLAN.md`、`DOCS/04-design/INTERACTION_DESIGN.md`、`DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`、`DOCS/04-design/TECHNICAL_DESIGN.md`、`SPECS/ARCHITECTURE_DECISIONS.md` |
| 最后更新 | 2026-07-24 |

## 1. 背景

Project Incubator 的核心风险之一是 AI 把 Maker 的继续推进、内容接受或模糊表达误解为可以执行 Git、Phase、文档状态、范围或 Builder 交接等高风险动作。R2 需要把这些风险整理为硬性门槛矩阵。

## 2. 目标

定义 Skill 1.0 的硬性门槛矩阵，明确哪些结果必须暂停、默认动作是什么，以及 Maker 必须确认什么。

## 3. 非目标

- 不脚本化门槛检查；
- 不替 Maker 作方向决定；
- 不把普通提醒升级为门槛；
- 不修改 `SPECS/ARCHITECTURE_DECISIONS.md`。

## 4. 允许范围

- 定义 Phase 门槛；
- 定义 Git 门槛；
- 定义权威文档门槛；
- 定义范围门槛；
- 定义 Builder 交接门槛；
- 定义未闭环任务门槛；
- 定义 Architecture Decision 候选写回门槛。

## 5. 禁止范围

- 不允许 AI 自动执行高风险动作；
- 不允许把 Maker 的结果确认当作具体 Git 授权；
- 不允许绕过状态入口冲突；
- 不允许把商业化、公开发布或团队协作纳入默认范围。

## 6. 输入

- `DOCS/04-design/INTERACTION_DESIGN.md`
- `DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`
- `DOCS/04-design/TECHNICAL_DESIGN.md`
- `SPECS/ARCHITECTURE_DECISIONS.md`
- `DOCS/05-planning/VERIFICATION_PLAN.md`

## 7. 输出

后续 Build Ticket 应产出硬性门槛矩阵，至少包含：

- 门槛类型；
- 触发结果；
- 默认安全动作；
- Maker 必须确认的内容；
- 允许继续的条件；
- 失败或冲突时的处理方式。

## 8. 验收标准

- 覆盖 Phase、Git、权威文档、范围、Builder、未闭环任务和 Architecture Decision 候选写回；
- 每类门槛都能说明默认不会做什么；
- 每类门槛都能说明 Maker 需要确认什么；
- 覆盖 `VERIFICATION_PLAN.md` 的 S2、S3、S4、S6、S8；
- 不新增未经 Maker 确认的长期架构规则。

## 9. 验证步骤

1. 用 S2 检查“继续”不会被当作 Git 授权；
2. 用 S3 检查 Git 未闭环时是否停止新写入任务；
3. 用 S4 检查 Phase 切换是否触发阶段门；
4. 用 S6 检查 Builder 信息不足是否触发交接门槛；
5. 用 S8 检查权威文档冲突是否停止推进。

## 10. 完成后更新

- 如果门槛矩阵改变首批 Ticket 边界，更新 `MILESTONES.md`；
- 如果发现现有 Architecture Decision 不足，提出候选写回，不直接修改。
