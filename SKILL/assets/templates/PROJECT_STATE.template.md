# {{PROJECT_NAME}} Project State

> {{PROJECT_NAME}} 当前状态的唯一权威来源。由 Project Incubator Skill 实例化生成。

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | {{PROJECT_NAME}} |
| 所有者 Phase | 跨阶段状态文档 |
| 文档状态 | Draft |
| 权威范围 | 当前项目状态、Phase、角色、目标、权威文档集合、阻塞项、阶段门与下一步 |
| 消费 Phase | Phase 0-9，启动时必读 |
| 更新条件 | 状态、Phase、角色、文档路径、决定、阻塞项或下一步发生变化 |
| 依赖文档 | `AGENTS.md` |
| 最后更新 | {{DATE}} |

## 1. 基本状态

| 字段 | 当前值 |
| --- | --- |
| 项目名称 | {{PROJECT_NAME}} |
| Maker | {{MAKER_DEFINITION}} |
| 项目类型 | {{PROJECT_TYPE}} |
| 项目状态 | Draft |
| 当前 Phase | {{CURRENT_PHASE}} |
| 当前 AI 角色 | {{CURRENT_AI_ROLE}} |
| 当前主要目标 | {{CURRENT_PRIMARY_GOAL}} |
| 当前阶段交付物 | {{CURRENT_DELIVERABLES}} |
| 当前任务状态 | Working |
| 下一项决定 | {{NEXT_MAKER_DECISION}} |
| 最近更新时间 | {{DATE}} |

## 2. 当前阶段说明

{{CURRENT_PHASE_SUMMARY}}

## 3. 当前 AI 协作契约

当前 AI 应：

- 在当前 Phase 和当前主要目标内协作；
- 区分 Maker 确认事实、AI 推断和待确认假设；
- 只读取和更新本轮任务需要的最小权威文档集合；
- 在写入、阶段切换、范围扩大或 Git 高风险动作前请求 Maker 确认。

当前 AI 不应：

- 替 Maker 决定项目方向、成功标准、阶段切换或最终验收；
- 默认公开化、商业化、产品化或扩大实现深度；
- 把未确认假设写成事实；
- 预建所有 Phase 文档或目录。

## 4. 当前基线

### 4.1 阶段与交付物基线

{{PHASE_AND_DELIVERABLE_BASELINE}}

### 4.2 当前有效治理基线

- 本项目使用 `AGENTS.md` 作为本地 Agent 启动协议；
- 本项目使用 `DOCS/PROJECT_STATE.md` 作为当前状态入口；
- 阶段文档按需存放在 `DOCS/<phase>/`；
- Maker 保留方向、范围、阶段切换和验收决定权。

### 4.3 当前项目理解基线

{{PROJECT_UNDERSTANDING_BASELINE}}

## 5. 当前未确认事项

{{OPEN_QUESTIONS}}

## 6. 当前阻塞项

{{BLOCKERS}}

## 7. 当前 Exit Criteria 状态

{{EXIT_CRITERIA_STATUS}}

## 8. 下一步

{{NEXT_STEP}}

## 9. 当前权威文档集合

| 内容类别 | 权威路径 | 状态 | 本轮读取要求 |
| --- | --- | --- | --- |
| Agent 启动协议 | `AGENTS.md` | Draft | 启动时必读 |
| 当前项目状态 | `DOCS/PROJECT_STATE.md` | Draft | 启动时必读 |

## 10. 下一会话恢复入口

下一会话必须从项目根目录 `AGENTS.md` 开始，随后读取 `DOCS/PROJECT_STATE.md`，再按上表读取本轮需要的权威文档。

恢复后的第一项工作是：{{RECOVERY_ENTRY}}。
