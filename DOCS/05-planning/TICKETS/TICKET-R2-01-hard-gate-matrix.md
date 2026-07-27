# Ticket R2-01 - Hard Gate Matrix

> Phase 5 - Planning 的 R2 硬性门槛矩阵 Ticket 交付物

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 5 - Planning |
| 文档状态 | Active |
| 权威范围 | Skill 1.0 结构化 gate 执行机制的任务边界、低成本 gate router、关键 gate 集合、gate schema、触发结果、输出枚举、阻断规则、默认动作、Maker 确认要求和验证步骤 |
| 消费 Phase | Phase 5-6，按需读取 |
| 更新条件 | Maker 调整 gate router、关键 gate 集合、gate schema、输出枚举、阻断规则、默认动作、确认要求或验证方式 |
| 依赖文档 | `DOCS/05-planning/ROADMAP.md`、`DOCS/05-planning/MILESTONES.md`、`DOCS/05-planning/VERIFICATION_PLAN.md`、`DOCS/04-design/INTERACTION_DESIGN.md`、`DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`、`DOCS/04-design/TECHNICAL_DESIGN.md`、`DOCS/04-design/GATE_EXECUTION_DESIGN.md`、`SPECS/ARCHITECTURE_DECISIONS.md` |
| 最后更新 | 2026-07-27 |

## 1. 背景

Project Incubator 的核心风险之一是 AI 把 Maker 的继续推进、内容接受或模糊表达误解为可以执行 Git、Phase、文档状态、范围或 Builder 交接等高风险动作。原 R2 计划把这些风险整理为硬性门槛矩阵。

2026-07-27 当前 Ticket 方向：Maker 已确认按 gate router 版本继续后续流程。本 Ticket 当前负责把原自然语言门槛矩阵重拆为结构化 gate 执行机制任务，不能继续作为自然语言矩阵 Build Ticket 使用。

## 2. 目标

定义 Skill 1.0 的结构化 gate 执行机制，明确低成本 gate router、关键 gate 集合、gate schema、输入字段、输出枚举、阻断规则、默认安全动作、Maker 必须确认什么，以及哪些 gate 需要脚本 / 工具检查器承载。

## 3. 非目标

- 不直接实现完整脚本化门槛检查；
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
- 定义 gate router；
- 定义 gate schema；
- 定义 gate registry / config 的最小字段；
- 定义 gate 输出枚举和阻断规则；
- 定义 gate case 验证样例；
- 判断哪些 gate 需要脚本 / 工具检查器承载。

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

后续 Build Ticket 应产出结构化 gate 执行机制，至少包含：

- router 触发域；
- router 选出的候选 gate 与跳过 gate；
- 稳定 gate id；
- 门槛类型；
- gate 输入字段；
- gate 输出枚举；
- 触发结果；
- 是否阻断；
- 默认安全动作；
- Maker 必须确认的内容；
- 允许继续的条件；
- 失败或冲突时的处理方式。

## 8. 验收标准

- 覆盖 Phase、Git、权威文档、范围、Builder、未闭环任务和 Architecture Decision 候选写回；
- 每类门槛都能说明默认不会做什么；
- 每类门槛都能说明 Maker 需要确认什么；
- router 能跳过无关 gate，避免全量展开所有 gate；
- 每类关键 gate 都能输出封闭枚举；
- 每个阻断输出都能说明 Agent 可继续动作；
- 覆盖 `DOCS/04-design/GATE_EXECUTION_DESIGN.md` 的关键 gate 集合；
- 覆盖 `VERIFICATION_PLAN.md` 的 S2、S3、S4、S6、S8；
- 不新增未经 Maker 确认的长期架构规则。

## 9. 验证步骤

1. 用 S2 gate case 检查 router 只选出 Git / 未闭环相关候选 gate，`GATE_GIT_WRITE` 输出 `HIT_NEEDS_AUTH`，且“继续”不会被当作 Git 授权；
2. 用 S3 gate case 检查 router 选出 `GATE_UNCLOSED_WORK`，输出阻断枚举，且 Git 未闭环时停止新写入任务；
3. 用 S4 gate case 检查 router 选出 `GATE_PHASE_TRANSITION`，输出阻断枚举，且 Phase 切换先触发阶段门；
4. 用 S6 gate case 检查 router 选出 `GATE_BUILDER_HANDOFF`，输出阻断枚举，且 Builder 信息不足时拒绝交接；
5. 用 S8 gate case 检查 router 选出 `GATE_AUTHORITY_SOURCE`，输出阻断枚举，且权威文档冲突时停止推进。

## 10. 完成后更新

- 如果门槛矩阵改变首批 Ticket 边界，更新 `MILESTONES.md`；
- 如果 gate router、gate schema、输出枚举或检查器判断改变 Planning 边界，更新 `ROADMAP.md`、`MILESTONES.md` 和 `VERIFICATION_PLAN.md`；
- 如果发现现有 Architecture Decision 不足，提出候选写回，不直接修改。
