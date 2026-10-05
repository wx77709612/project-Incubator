# Desktop Product Incubator Contract

> Specification Version: Plugin Desktop Product Iteration
> Status: DRAFT
> Depends On: `SPECS/ARCHITECTURE/ARCHITECTURE_DECISIONS.md` Decision 013；`SPECS/PROJECT_TYPES/DESKTOP_PRODUCT_PROFILE.md`
> Implementation Authorization: NOT GRANTED

## 1. Contract Scope

本文档把已批准的 `desktop-product` Design 转换为 Registry、Workflow Entry、Activation 与 Desktop Workflow 的交互契约。它不重新定义 P0–P6，不增加浏览器扩展语义，也不授权修改 Plugin 实现。

既有 Maker Authorization、MCP-only Mutation、Pending Request、Receipt、Hook、Evidence 与 Revision Contract 继续有效。

## 2. Registry Contract

每个 `project_types[]` 条目必须具有：

```text
id
child_skill_id
profile_path
workflow_module
host_profile_requirement: REQUIRED | OPTIONAL | FORBIDDEN
```

约束：

- `desktop-product.host_profile_requirement = REQUIRED`；
- `mod.host_profile_requirement = OPTIONAL`，保持现有可空 Host 行为；
- `REQUIRED` 且 `host_profile_id = null` 时拒绝路由和激活；
- `FORBIDDEN` 且 `host_profile_id != null` 时拒绝路由和激活；
- 非空 Host 必须存在且 `project_type_id` 匹配；
- Router 和 Kernel 不得自动填入 Host；`windows-desktop` 只是候选值。

Registry 格式存在新的必填字段，因此 Registry `schema_version` 从 `1.0` 升为 `1.1`。Registry 是随 Plugin 一起交付的内部配置，不对旧 Registry 文件做运行时迁移。

## 3. Workflow Evaluator Contract

每个 Project Type 的 Workflow Module 必须导出：

```text
evaluateEntry(initialState) -> EntryEvaluation
evaluateTransition(currentState, transitionRequest) -> TransitionEvaluation
```

`evaluateTransition` 保持现有语义。`evaluateEntry` 返回：

```text
allowed: boolean
code: string
workflow?: {
  stage: string
  allowed_next: string[]
  return_stage: string | null
}
```

Kernel 负责比较 evaluator 返回的 Workflow Shape 与 Initial State；不解释 Evidence 是否足以支持阶段判断。

## 4. Workflow Entry State Contract

新激活状态使用 Project State `schema_version = 1.1`，并在 `workflow` 内包含：

```text
entry: {
  mode: NEW_PROJECT | ADOPT_EXISTING
  initial_stage: string
  assessment_summary: string
  evidence_refs: string[]
  assessed_at: RFC 3339 timestamp
}
```

通用约束：

- `entry.initial_stage == workflow.stage`；
- `return_stage = null`；
- `assessment_summary` 非空且不超过既有 Short Text 上限；
- `evidence_refs` 使用既有 bounded text list 上限；
- Entry 在激活后不可修改；普通 `prepare_change` 必须拒绝任何 Entry 差异。

Mode 约束：

| Mode | Initial Stage | Evidence Refs |
| --- | --- | --- |
| `NEW_PROJECT` | 必须等于 Child Workflow 标准初始阶段 | 可为空 |
| `ADOPT_EXISTING` | 必须属于 Child Workflow 允许接管的正常阶段 | 至少一项 |

旧 Project State `schema_version = 1.0` 可没有 `workflow.entry`，继续按原 Contract 读取和变更；Runtime 不自动补写、不阻止正常阶段转换。所有新激活必须使用 `1.1`。

## 5. Entry Responsibility Boundary

- Maker：说明项目是新建还是已有项目，提供已有项目来源与背景，并确认完整激活请求；
- Agent：对已有 Artifact、实现、计划和 Evidence 作语义判断，给出 `initial_stage`、摘要和 Evidence 引用；
- Child Workflow：声明标准初始阶段与允许接管的正常阶段；
- Kernel：校验结构、枚举、Evidence 引用字段与非空性、阶段集合、Workflow Shape、Host Requirement 与 Maker Authorization。

Kernel 不验证“Evidence 是否真的足以证明 P3”，Maker 也不被要求替 Agent 完成阶段分析。

## 6. Desktop Entry Contract

Desktop Workflow 的阶段集合为 `P0` 至 `P6`：

- 标准初始阶段：`P0`；
- `ADOPT_EXISTING` 允许进入：`P0`、`P1`、`P2`、`P3`、`P4`、`P5`、`P6`；
- P4 Creation Correction 是 P4 内部活动，不是 Entry Stage；
- Desktop Workflow 不存在可直接进入的临时 Review Stage。

`evaluateEntry` 必须根据 Entry Mode 验证上述范围，并返回该阶段对应的正式 `allowed_next`。

## 7. Desktop Transition Contract

正式转换沿用 Core P0–P6：

| Current | Allowed Next |
| --- | --- |
| P0 | P1 |
| P1 | P2 |
| P2 | P3 |
| P3 | P4 |
| P4 | P5 |
| P5 | P6 |
| P6 | P2、P3、P4 或 P5 |

P4 Creation Correction 不改变 `workflow.stage`，因此不得提交 `workflow_transition`；其状态与 Evidence 通过普通受控 State Mutation 持久化。

每个状态变更继续走现有两步授权流程。`READY_FOR_TRANSITION` 仍不等于 Transition 已执行；只有授权后的 State Commit 和 Read-back 成功才完成转换。

## 8. Activation Contract

现有 Tool 形状保持：`propose_route`、`prepare_activation`、`initialize_project`。`workflow.entry` 作为 `prepare_activation.state.workflow.entry` 提交，不增加 Desktop 专用 Tool。

`prepare_activation` 必须：

1. 确认项目尚未激活；
2. 解析 Registry 1.1 并执行 Host Requirement；
3. 解析 Project State 1.1；
4. 调用所选 Project Type 的 `evaluateEntry`；
5. 比较 `stage`、`allowed_next` 与 `return_stage`；
6. 将 Route、Initial State、Product Decisions 与摘要纳入既有 `scope_digest`；
7. 创建待 Maker 授权的 Activation Request。

`initialize_project` 必须在写入前重复步骤 2–5。任何 Registry、Route、State 或 Entry 漂移都失败关闭，不得使用准备时的旧判断继续提交。

## 9. Host Profile Tightening Contract

`windows-desktop` Host Profile 可以增加 Windows 环境的 Gate、Evidence 和验证条件，但不得：

- 改写 P0–P6 或增加 Transition；
- 弱化 Kernel Authorization、Mutation 或 Receipt；
- 把 Desktop Delivery Surface 改写成 Host；
- 自动启用安装、更新、管理员权限或外部内容执行；
- 在激活后替换 `host_profile_id`。

首版没有 Host 迁移（Host Migration）Contract。确有需求时必须另提 Architecture Change。

## 10. Failure Codes

至少提供以下稳定错误语义：

| Code | Meaning |
| --- | --- |
| `HOST_PROFILE_REQUIRED` | REQUIRED 类型没有 Host |
| `HOST_PROFILE_FORBIDDEN` | FORBIDDEN 类型绑定了 Host |
| `HOST_PROFILE_PROJECT_TYPE_MISMATCH` | Host 与 Project Type 不匹配 |
| `WORKFLOW_ENTRY_REQUIRED` | 新激活缺少 Entry |
| `WORKFLOW_ENTRY_MODE_INVALID` | Entry Mode 非法 |
| `WORKFLOW_ENTRY_STAGE_INVALID` | Initial Stage 不符合 Child Workflow |
| `WORKFLOW_ENTRY_EVIDENCE_REQUIRED` | 接管已有项目但没有 Evidence 引用 |
| `WORKFLOW_ENTRY_STATE_MISMATCH` | Entry Stage 与 State Stage 不一致 |
| `WORKFLOW_ENTRY_IMMUTABLE` | 激活后尝试修改 Entry |
| `WORKFLOW_ALLOWED_NEXT_MISMATCH` | Initial State 的下一阶段集合不匹配 |
| `WORKFLOW_RETURN_STAGE_MISMATCH` | Initial State 含非法 Return Stage |

错误只阻止操作，不产生部分 Activation、State Mutation 或 Receipt。

## 11. Compatibility Contract

- 不迁移既有 Managed Project；
- 不修改 `mod-incubator` 与 `sims-4` 的领域语义；
- `mod` 新激活使用 `NEW_PROJECT -> M0`，或由其 evaluator 接受正常 M0–M5 的 `ADOPT_EXISTING`；`MODEL_REVIEW` 不可作为接管入口；
- 旧 Project State 1.0 无 Entry 时继续可用；
- Activation 文件仍使用现有结构，Host 仍写入唯一的 `host_profile_id`；
- 不新增权威 Markdown 状态文件。

## 12. Contract Acceptance

Contract 验收必须证明：

1. Host 的 REQUIRED、OPTIONAL、FORBIDDEN 三种行为均失败关闭或成功路由；
2. Desktop 新项目只能从 P0 激活；
3. 已有 Desktop 项目可按 Evidence 从 P0–P6 合法阶段接管；
4. 无 Evidence、临时阶段、错误 Workflow Shape 或默认 Host 均被拒绝；
5. Entry 被纳入授权摘要且激活后不可变；
6. Project State 1.0 继续工作；
7. 现有 Mod 路由、Workflow、Host Profile 与回归行为保持不变。

本文档为 DRAFT；Maker 批准前不进入 Runtime 实现或代码修改。
