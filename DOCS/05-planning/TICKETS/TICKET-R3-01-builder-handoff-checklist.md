# Ticket R3-01 - Builder Handoff Checklist

> Phase 5 - Planning 的 R3 Builder 交接前检查 Ticket 交付物

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 5 - Planning |
| 文档状态 | Active |
| 权威范围 | AI Builder 启动前的结构化 `GATE_BUILDER_HANDOFF` 输入字段、Ticket 必备字段、交接门槛、允许与禁止范围、验收标准和验证步骤 |
| 消费 Phase | Phase 5-6，按需读取 |
| 更新条件 | Maker 调整 Builder 交接条件、`GATE_BUILDER_HANDOFF` 输入字段、Ticket 必备字段、验收标准、验证步骤或执行边界 |
| 依赖文档 | `DOCS/05-planning/ROADMAP.md`、`DOCS/05-planning/MILESTONES.md`、`DOCS/05-planning/VERIFICATION_PLAN.md`、`FRAMEWORK/Role-System.md`、`FRAMEWORK/Phase-System.md`、`DOCS/04-design/SKILL_DESIGN.md`、`DOCS/04-design/INTERACTION_DESIGN.md`、`DOCS/04-design/GATE_EXECUTION_DESIGN.md` |
| 最后更新 | 2026-07-27 |

## 1. 背景

Phase 5 之后将进入 Build。Build 前必须确保 Builder 拿到的是范围明确、可验证、不允许重新定义项目方向的任务，而不是开放式“实现整个 Skill”。

2026-07-27 设计修订：Builder 交接检查清单必须升级为 `GATE_BUILDER_HANDOFF` 的结构化输入和判定。只有当 gate router 判断本轮准备进入 Builder / 执行型任务时才展开该 gate；字段缺失时应输出 `HIT_BLOCK` 或 `INPUT_INCOMPLETE`，不得只靠自然语言提醒 Builder 谨慎执行。

## 2. 目标

定义 AI Builder 启动前的 `GATE_BUILDER_HANDOFF` 结构化交接检查。

## 3. 非目标

- 不执行 Build；
- 不创建代码；
- 不把完整 Skill 一次性交给 Builder；
- 不让 Builder 判断 Phase 是否完成。

## 4. 允许范围

- 定义 Ticket 必备字段；
- 定义 Builder 启动前检查；
- 定义 router 何时选中 `GATE_BUILDER_HANDOFF`；
- 定义 gate 输入字段、输出枚举和阻断规则；
- 定义缺失字段时的拒绝交接流程；
- 定义允许修改和禁止修改范围；
- 定义验证步骤要求。

## 5. 禁止范围

- 不允许缺少目标、非目标、范围、验收标准或验证步骤的任务进入 Build；
- 不允许 Builder 修改项目方向、Phase、成功标准或 Maker 决策权；
- 不允许 Builder 代替 Maker 完成最终验收；
- 不允许 Builder 执行未授权 Git 闭环。

## 6. 输入

- `FRAMEWORK/Role-System.md`
- `FRAMEWORK/Phase-System.md`
- `DOCS/04-design/SKILL_DESIGN.md`
- `DOCS/04-design/INTERACTION_DESIGN.md`
- `DOCS/04-design/GATE_EXECUTION_DESIGN.md`
- `DOCS/05-planning/VERIFICATION_PLAN.md`

## 7. 输出

后续 Build Ticket 应产出 Builder 交接前检查清单，至少包含：

- gate id：`GATE_BUILDER_HANDOFF`；
- gate 输出枚举；
- 背景；
- 目标；
- 非目标；
- 输入；
- 输出；
- 依赖；
- 允许修改范围；
- 禁止修改范围；
- 验收标准；
- 验证步骤；
- 风险和阻塞项；
- 完成后需要更新的文档。

## 8. 验收标准

- Ticket 必备字段完整；
- 任一必备字段缺失时，AI 明确拒绝交给 Builder；
- 任一必备字段缺失时，gate 输出为 `HIT_BLOCK` 或 `INPUT_INCOMPLETE`；
- gate 输出为阻断结果时，只允许回到 Planning 补齐 Ticket；
- 覆盖 `VERIFICATION_PLAN.md` 的 S6；
- 不授权 Builder 改变 Phase、范围或 Git 历史；
- 能用于后续首批 Build Ticket。

## 9. 验证步骤

1. 用 S6 的不完整 Ticket gate case 检查是否输出阻断枚举并拒绝交接；
2. 构造一个缺少验证步骤的 Ticket，检查 `GATE_BUILDER_HANDOFF` 是否输出 `HIT_BLOCK` 或 `INPUT_INCOMPLETE`；
3. 构造一个包含范围扩大要求的 Ticket，检查是否同时触发 `GATE_SCOPE_EXPANSION`；
4. 检查输出是否能作为 Build 前检查清单使用。

## 10. 完成后更新

- 如 Maker 接受，后续 Ticket 模板或 Skill references 可消费该清单；
- 如发现字段过重，回到本 Ticket 收敛字段，不直接进入 Build。
