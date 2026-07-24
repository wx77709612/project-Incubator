# Ticket R1-01 - Main Runtime Chain

> Phase 5 - Planning 的 R1 主运行链路 Ticket 交付物

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 5 - Planning |
| 文档状态 | Active |
| 权威范围 | Skill 1.0 主运行链路的任务边界、输入输出、验收标准和验证步骤 |
| 消费 Phase | Phase 5-6，按需读取 |
| 更新条件 | Maker 调整主运行链路、启动恢复顺序、协作契约、审阅回写或 Ticket 边界 |
| 依赖文档 | `DOCS/05-planning/ROADMAP.md`、`DOCS/05-planning/MILESTONES.md`、`DOCS/05-planning/VERIFICATION_PLAN.md`、`DOCS/04-design/SKILL_DESIGN.md`、`DOCS/04-design/INTERACTION_DESIGN.md`、`DOCS/04-design/TECHNICAL_DESIGN.md` |
| 最后更新 | 2026-07-24 |

## 1. 背景

R1 需要先定义 Skill 1.0 的主运行链路。当前项目已经在真实协作中使用了状态恢复、协作契约、分叉处理、文档写回和 Maker Diff 审阅，但这些步骤需要被串成未来 Skill 可执行的稳定链路。

## 2. 目标

定义从 Skill 启动或项目恢复，到下一轮可恢复入口形成之间的完整主运行链路。

## 3. 非目标

- 不编写最终 `SKILL.md`；
- 不实现脚本；
- 不创建模板文件；
- 不修改 `FRAMEWORK/` 或 `AGENTS.md`；
- 不进入 Build。

## 4. 允许范围

- 设计主运行链路步骤；
- 定义每一步的输入、输出和停止条件；
- 明确哪些步骤依赖 `AGENTS.md`、`PROJECT_STATE.md`、Phase 规则、角色规则和权威文档集合；
- 定义链路结束时需要留下的恢复入口。

## 5. 禁止范围

- 不新增 Phase；
- 不改变 Maker 决策权；
- 不把 Git 写操作纳入默认自动流程；
- 不把模板或脚本作为本 Ticket 的实现结果。

## 6. 输入

- `DOCS/05-planning/ROADMAP.md`
- `DOCS/05-planning/MILESTONES.md`
- `DOCS/05-planning/VERIFICATION_PLAN.md`
- `DOCS/04-design/SKILL_DESIGN.md`
- `DOCS/04-design/INTERACTION_DESIGN.md`
- `DOCS/04-design/TECHNICAL_DESIGN.md`

## 7. 输出

后续 Build Ticket 应产出一份主运行链路说明或等价 Skill reference，至少包含：

- 启动或恢复；
- 读取本地协议与状态入口；
- 定位 Phase、角色、主目标和权威文档集合；
- 建立本轮协作契约；
- 判断任务类型；
- Phase 内协作；
- 新事项分类；
- 触发硬性门槛；
- 文档写回；
- Maker 审阅；
- 状态入口收敛；
- 下一轮恢复。

## 8. 验收标准

- 每一步都有输入、输出和继续条件；
- 每一步都能说明何时应停止并请求 Maker 决定；
- 主链路覆盖 `VERIFICATION_PLAN.md` 的 S1、S2、S5、S8；
- 不依赖聊天记忆作为唯一上下文；
- 不授权 Build 或 Git 写操作。

## 9. 验证步骤

1. 用 S1 新会话恢复场景检查链路能否恢复 Phase、角色和下一步；
2. 用 S2 Maker 说“继续”场景检查链路能否判断任务类型；
3. 用 S5 新想法出现检查链路能否进入分叉分类；
4. 用 S8 权威文档冲突检查链路能否停止推进；
5. 检查输出是否没有包含 Skill 实现细节。

## 10. 完成后更新

- 如 Maker 接受该 Ticket，后续在 `DOCS/PROJECT_STATE.md` 中将其标记为首批 Ticket 候选；
- 如果验证暴露链路缺口，回写 `VERIFICATION_PLAN.md` 或本 Ticket。
