# Builder Handoff Checklist Reference

> Project Incubator Skill 1.0 的 Builder 交接前检查 reference

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 6 - Build |
| 文档状态 | Draft |
| 权威范围 | Project Incubator Skill 1.0 在启动 AI Builder 前必须检查的任务字段、交接门槛、允许与禁止范围、拒绝交接流程和验证场景 |
| 消费 Phase | Phase 6-9，后续 R3 与 Skill 实现任务按需读取 |
| 更新条件 | Maker 调整 Builder 交接条件、Ticket 必备字段、拒绝交接流程、验证步骤或 R3 任务边界 |
| 依赖文档 | `DOCS/05-planning/TICKETS/TICKET-R3-01-builder-handoff-checklist.md`、`DOCS/05-planning/VERIFICATION_PLAN.md`、`FRAMEWORK/Role-System.md`、`FRAMEWORK/Phase-System.md`、`DOCS/04-design/SKILL_DESIGN.md`、`DOCS/04-design/INTERACTION_DESIGN.md`、`SKILL/references/task-type-and-writeback.md`、`SKILL/references/hard-gate-matrix.md`、`SKILL/references/gate-response-and-authorization.md` |
| 最后更新 | 2026-07-25 |

## 1. 文档职责

本文档承载 R3-01 的 Build 输出：定义 Project Incubator Skill 1.0 在把任务交给 AI Builder 执行前，必须检查哪些字段、哪些缺口会拒绝交接，以及如何把缺口回到 Planning 或当前 Ticket。

本文档不启动 Builder，不执行 Build，不创建代码，不修改 Ticket 模板，不替 Maker 判断 Phase 是否完成，也不授权任何 Git 写操作。

## 2. 交接原则

Builder 只能执行范围明确、可验证、不会重新定义项目方向的任务。

当任务缺少目标、非目标、输入、输出、依赖、允许范围、禁止范围、验收标准、验证步骤、风险或完成后更新项时，AI Collaborator 必须拒绝交给 Builder，并说明缺口应回到哪里补齐。

Maker 的“继续”“可以”“交给 Builder 做”只能触发交接检查，不能绕过字段完整性、范围门槛、Git 门槛或 Maker 验收门。

## 3. Builder 启动前检查清单

| 检查项 | 必须能回答的问题 | 缺失时默认动作 |
| --- | --- | --- |
| 背景 | 为什么需要这个任务，来自哪个 Phase / Ticket / 设计输入 | 回到当前 Ticket 补背景 |
| 目标 | Builder 本轮要完成什么唯一目标 | 拒绝交接，要求补目标 |
| 非目标 | 本轮明确不做什么 | 拒绝交接，防止范围扩张 |
| 输入 | Builder 必须读取或使用哪些文档、文件、素材或状态 | 补齐精确路径或等价输入 |
| 输出 | Builder 完成后应产生什么文件、文档、代码、资产或报告 | 补齐输出物和承载位置 |
| 依赖 | 任务依赖哪些上游设计、规则、Ticket 或验证计划 | 补齐依赖或说明无依赖 |
| 允许修改范围 | Builder 可以修改哪些文件、目录或文档段落 | 未明确则不允许写入 |
| 禁止修改范围 | Builder 不得修改哪些项目方向、Phase、规则、文档或 Git 状态 | 未明确则拒绝交接 |
| 验收标准 | 什么证据说明任务达到要求 | 缺失则回到 Planning |
| 验证步骤 | Builder 应运行或执行哪些检查 | 缺失则回到 Planning |
| 风险和阻塞项 | 哪些情况会停止执行或需要 Maker 决定 | 补齐停止条件 |
| 完成后更新 | Builder 完成后哪些文档或状态入口需要更新 | 补齐回写对象或说明不需要 |

## 4. 交接判断流程

AI Collaborator 准备交给 Builder 前按以下顺序判断：

1. 确认当前 Phase 允许 Builder 执行或准备执行上下文。
2. 确认任务属于当前 `DOCS/PROJECT_STATE.md` 指向的主目标或 Maker 明确授权的同一里程碑范围。
3. 读取当前 Ticket 或等价执行文档。
4. 对照 Builder 启动前检查清单逐项检查字段。
5. 判断是否触发硬性门槛：Builder 交接、范围、Git、Phase、权威文档、未闭环任务或上下文完整性门槛。
6. 字段完整且未触发阻断门槛时，输出 Builder 可执行边界。
7. 字段不完整或门槛未解除时，拒绝交接并说明缺口、风险和回退位置。

## 5. Builder 可执行边界格式

只有检查通过时，AI Collaborator 才能输出以下交接边界：

```text
Builder 任务边界：
- 目标：
- 非目标：
- 输入：
- 输出：
- 依赖：
- 允许修改范围：
- 禁止修改范围：
- 验收标准：
- 验证步骤：
- 风险和停止条件：
- 完成后更新：
```

该边界是 Builder 的执行约束。Builder 不得用实现便利性改写边界，不得自行扩大输出，不得把验证失败解释为任务完成。

## 6. 拒绝交接回应

当检查失败时，AI 使用简短回应：

```text
这个任务暂时不能交给 Builder，因为缺少：[缺失字段或触发门槛]。
默认不进入执行。
我可以先把缺口补回 [当前 Ticket / Planning 文档 / Maker 决策点]。
补齐后再重新做 Builder 交接检查。
```

如果缺口涉及高风险动作，转入 `SKILL/references/gate-response-and-authorization.md` 的标准门槛回应。

## 7. 常见拒绝交接场景

| 场景 | 触发原因 | AI 行为 |
| --- | --- | --- |
| 缺少验收标准 | Builder 无法判断完成标准 | 拒绝交接，回到 Planning 或当前 Ticket 补验收 |
| 缺少验证步骤 | Builder 无法提供验证证据 | 拒绝交接，补验证步骤 |
| 只有开放目标 | 例如“实现完整 Skill” | 触发范围门槛，拒绝当前 Ticket 内执行 |
| 要求修改 Phase 或成功标准 | Builder 会改变 Maker 决策边界 | 触发 Phase / 范围门槛 |
| 要求 Git 闭环 | Builder 会改变历史或远端 | 触发 Git 门槛，不授权执行 |
| 当前 Diff 未闭环且任务无关 | 会混入无关修改 | 触发未闭环任务门槛 |
| 上下文不可靠 | AI 无法确认当前任务边界 | 触发上下文完整性门槛 |

## 8. 验证场景映射

### S6 Ticket 不完整

**输入场景**

- Ticket 缺少验收标准或验证步骤；
- Maker 想让 Builder 执行。

**预期行为**

- AI 明确拒绝交给 Builder；
- 输出缺失字段；
- 指向当前 Ticket 或 Planning 文档补齐；
- 不进入执行。

### 缺少验证步骤的 Ticket

**输入场景**

- Ticket 有目标、非目标和范围；
- 但没有验证步骤。

**预期行为**

- AI 判断字段不完整；
- 拒绝 Builder 交接；
- 回到 Planning 补验证步骤。

### 范围扩大 Ticket

**输入场景**

- Ticket 要求 Builder 在当前任务中实现完整 Skill、修改 Phase 规则、改变项目范围或顺手完成 R4。

**预期行为**

- AI 触发范围门槛；
- 不交给 Builder；
- 将越界内容分类为后续、阻塞或 Maker 决策点。

### 可执行 Ticket

**输入场景**

- Ticket 包含完整字段；
- 当前 Phase 允许执行；
- 未触发 Git、Phase、范围、权威文档、未闭环任务或上下文完整性门槛。

**预期行为**

- AI 输出 Builder 可执行边界；
- 不替 Builder 执行；
- 不授权 Git 写操作；
- 后续由 R3-02 定义 Builder 返回后的审阅闭环。

## 9. R3-01 边界检查

本文档满足 R3-01 的输出要求：

- 定义 Ticket 必备字段；
- 定义 Builder 启动前检查；
- 定义缺失字段时的拒绝交接流程；
- 定义允许修改和禁止修改范围；
- 定义验证步骤要求；
- 覆盖 S6、缺少验证步骤、范围扩大和可执行 Ticket 场景；
- 不执行 Build；
- 不创建代码；
- 不把完整 Skill 一次性交给 Builder；
- 不让 Builder 判断 Phase 是否完成；
- 不授权 Builder 改变 Phase、范围或 Git 历史。

## 10. 后续消费关系

R3-02 可基于本文档定义 Builder 完成后的返回报告、Collaborator 回看和 Maker 审阅闭环。最终 `SKILL.md` 应只保留交接前检查的短入口，并按需引用本文档。
