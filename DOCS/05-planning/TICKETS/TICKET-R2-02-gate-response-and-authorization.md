# Ticket R2-02 - Gate Response And Authorization

> Phase 5 - Planning 的 R2 门槛回应与授权 Ticket 交付物

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 5 - Planning |
| 文档状态 | Active |
| 权威范围 | 结构化 gate router 与候选 gate 输出后的标准回应结构、Maker 明确授权字段、默认安全处理方式和不可接受授权的任务边界 |
| 消费 Phase | Phase 5-6，按需读取 |
| 更新条件 | Maker 调整 gate 输出枚举、门槛交互方式、授权要求、默认安全处理方式或不可接受授权边界 |
| 依赖文档 | `DOCS/05-planning/TICKETS/TICKET-R2-01-hard-gate-matrix.md`、`DOCS/05-planning/VERIFICATION_PLAN.md`、`DOCS/04-design/INTERACTION_DESIGN.md`、`DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`、`DOCS/04-design/GATE_EXECUTION_DESIGN.md` |
| 最后更新 | 2026-07-27 |

## 1. 背景

硬性门槛不能只列风险，还必须定义触发后 AI 应如何回应。否则 Build 阶段仍可能把 Maker 的口语化确认误解为授权，或在门槛触发后继续推进。

2026-07-27 设计修订：门槛回应必须消费结构化 gate router 与候选 gate 输出，不能独立凭自然语言判断。回应结构应呈现必要的 gate id、输出枚举、阻断状态、允许的安全替代动作和缺失授权字段；不应展开被 router 跳过的无关 gate。

## 2. 目标

定义结构化 gate 输出后的标准回应结构和 Maker 明确授权字段。

## 3. 非目标

- 不编写 UI；
- 不实现命令解析；
- 不替 Maker 执行 Git 闭环；
- 不把含糊表达解释为授权。

## 4. 允许范围

- 定义门槛回应格式；
- 定义 gate id、输出枚举和阻断状态的呈现方式；
- 定义被 router 跳过 gate 的最小呈现方式；
- 定义明确授权必须包含的字段；
- 定义默认安全处理方式；
- 定义不可接受授权示例；
- 定义继续前复核步骤。

## 5. 禁止范围

- 不允许把“好的”“继续”“确认”“没问题”自动解释为 Git 或 Phase 授权；
- 不允许在授权对象不明确时执行；
- 不允许在 Git 或状态异常时绕过检查；
- 不允许把门槛回应写成长篇解释负担。

## 6. 输入

- `DOCS/04-design/INTERACTION_DESIGN.md`
- `DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`
- `DOCS/05-planning/TICKETS/TICKET-R2-01-hard-gate-matrix.md`
- `DOCS/05-planning/VERIFICATION_PLAN.md`

## 7. 输出

后续 Build Ticket 应产出门槛回应与授权规则，至少包含：

- gate id；
- router 选出的候选 gate；
- gate 输出枚举；
- 是否阻断；
- 风险结果说明；
- 默认不执行边界；
- 可提供的安全替代动作；
- Maker 若要 AI 执行，必须确认的动作、对象和范围；
- 执行前复核项；
- 授权不足时的回应。

## 8. 验收标准

- 能处理 Git、Phase、权威文档、范围和 Builder 交接门槛；
- 能避免把 router 跳过的无关 gate 写成长篇解释；
- 能处理 `MISS`、`HIT_BLOCK`、`HIT_NEEDS_AUTH`、`HIT_SAFE_ALTERNATIVE`、`INPUT_INCOMPLETE` 和 `CONFIG_INVALID`；
- 明确授权必须包含动作、对象和范围；
- 能识别“继续”不是具体授权；
- 覆盖 `VERIFICATION_PLAN.md` 的 S2、S3、S4；
- 回应格式简短、可复用、不会替 Maker 做决定。

## 9. 验证步骤

1. 用 S2 gate case 检查“继续”是否由 `GATE_GIT_WRITE` 判定为 `HIT_NEEDS_AUTH`，并在回应中请求缺失授权字段；
2. 用一个“帮我合并”gate case 检查是否要求具体 Git 动作、对象、范围和停止条件；
3. 用一个“进入下一阶段”gate case 检查是否先输出阶段门检查；
4. 用一个“把这个写进架构决策”gate case 检查是否要求 Maker 确认长期边界。

## 10. 完成后更新

- 如门槛回应格式影响 `AGENTS.md` 或 Skill references，记录为后续 Build Ticket；
- 如发现授权规则与 Architecture Decision 冲突，停止并请求 Maker 决定。
