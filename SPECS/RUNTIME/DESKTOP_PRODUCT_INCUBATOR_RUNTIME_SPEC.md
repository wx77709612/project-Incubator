# Desktop Product Incubator Runtime Specification

> Specification Version: Plugin Desktop Product Iteration
> Status: DRAFT
> Depends On: `SPECS/CONTRACTS/DESKTOP_PRODUCT_INCUBATOR_CONTRACT.md`
> Implementation Authorization: NOT GRANTED

## 1. Runtime Scope

本规格定义 Shared Kernel 如何加载新 Contract、准备并提交 Activation，以及如何执行 Desktop P0–P6。它不让 Runtime 判断产品阶段、不自动选择 Host，也不实现桌面业务功能。

## 2. Startup Loading

Plugin 启动时按以下顺序加载：

```text
Registry 1.1
→ Registry 引用与 Host Requirement 校验
→ 每个 Project Type 的 Workflow Module
→ evaluateEntry / evaluateTransition 接口校验
→ Host Profile 引用校验
```

任一 Project Type 缺少合法 `host_profile_requirement`，或 Workflow Module 缺少任一 evaluator，Plugin 启动失败；不得只禁用单个类型后继续运行。

## 3. Route Proposal

`propose_route` 的运行顺序：

1. 接收 Maker 与 Agent 已讨论出的 `project_type_id` 和候选 `host_profile_id`；
2. 查找 Project Type；
3. 按 Requirement 校验 Host 空值或非空值；
4. 对非空 Host 校验存在性和 Project Type 归属；
5. 返回 `ROUTE_PROPOSED`。

Runtime 不把 `windows-desktop` 或任何 Registry 中的第一个 Host 当作默认值。`desktop-product` 未提供 Host 时返回 `HOST_PROFILE_REQUIRED`。

| Requirement | Runtime Rule |
| --- | --- |
| `REQUIRED` | `host_profile_id` 必须非空且匹配 |
| `OPTIONAL` | 允许为空；非空时仍须匹配 |
| `FORBIDDEN` | 必须为空 |

## 4. Entry Assessment Preparation

在调用 Runtime 前：

- `NEW_PROJECT`：Agent 使用 Child Skill 的标准初始状态；
- `ADOPT_EXISTING`：Agent 读取已有项目材料，形成当前阶段判断、简短理由与 Evidence 引用；
- Maker 确认 Entry Mode、Project Type、Host、Product Decisions 和完整激活范围。

Runtime 只消费该结果，不执行内容调查，也不替 Agent 生成阶段结论。

## 5. Prepare Activation

`prepare_activation` 执行：

```text
Assert Uninitialized
→ Resolve Route and Host Requirement
→ Parse Project State
→ Require State 1.1 and workflow.entry
→ Call evaluateEntry
→ Compare Workflow Shape
→ Parse Product Decisions
→ Hash Full Activation Scope
→ Persist Pending Activation Request
```

`scope_digest` 继续覆盖完整 `initial_state`，因此自然覆盖 Entry Mode、Initial Stage、Assessment Summary、Evidence Refs 与评估时间，无需另建摘要文件。

准备成功只产生 Pending Request，不写 Activation、Project State 或 Receipt。

## 6. Initialize Project

`initialize_project` 在消费 Maker Prompt 前后必须保持既有 Session、Turn、Request、Digest 与过期校验，并在 Commit 前重新：

1. 使用当前进程启动时已经校验的 Registry 与 Workflow Module；
2. 解析待提交 Initial State；
3. 执行 Host Requirement；
4. 调用当前 Workflow Module 的 `evaluateEntry`；
5. 比较 Workflow Shape。

然后才可绑定 Product Decision Authorization、原子写入 Activation 与 Project State、写 Receipt，并消费 Pending Activation Request。

失败时不得留下部分 Activation 或部分 State；Pending Request 按既有失败与过期政策处理。

## 7. Entry Evaluation

### 7.1 `NEW_PROJECT`

Desktop evaluator 只接受 `initial_stage = P0`；Mod evaluator 只接受 `initial_stage = M0`。不匹配时返回 `WORKFLOW_ENTRY_STAGE_INVALID`。

### 7.2 `ADOPT_EXISTING`

Evaluator 校验：

- `evidence_refs.length >= 1`；
- `initial_stage` 属于本 Child Workflow 的正常阶段；
- `initial_stage == workflow.stage`；
- `return_stage = null`；
- `allowed_next` 与阶段映射一致。

Evaluator 不打开 Evidence 文件、不评估 Evidence 强弱、不推断更合适的阶段。该判断属于 Agent，Maker 通过完整 Activation 授权确认其被采用。

## 8. State Compatibility

Project State Parser 同时接受：

- `1.0`：既有结构，不含 `workflow.entry`；
- `1.1`：`workflow.entry` 必填。

规则：

- 新激活只接受 1.1；
- 既有 1.0 Managed Project 可继续 Inspect、Prepare Change、Commit Change 和阶段转换；
- Runtime 不自动把 1.0 升级为 1.1；
- 1.1 的 `workflow.entry` 在所有 State Mutation 前后必须深度相等，否则返回 `WORKFLOW_ENTRY_IMMUTABLE`。

## 9. Desktop Workflow Execution

Desktop evaluator 采用以下映射：

```text
P0 -> [P1]
P1 -> [P2]
P2 -> [P3]
P3 -> [P4]
P4 -> [P5]
P5 -> [P6]
P6 -> [P2, P3, P4, P5]
```

阶段变化时继续要求显式 `workflow_transition`、目标阶段一致、Completion Conditions 满足和 Maker Authorization。无阶段变化时若携带 `workflow_transition`，继续返回 `WORKFLOW_TRANSITION_UNEXPECTED`。

Desktop-specific 描述、P2 `FEASIBILITY_PROBE`、P4 `Desktop System Model` / `Usable Slice` / `Delivery Hardening` 与 P4 Correction 都由 Child Skill 指导，不进入 Runtime Stage 枚举。

## 10. P4 Creation Correction

P4 内出现模型反例时：

1. Agent 暂停受影响工作包；
2. 记录 Observation、Hypothesis、影响范围与 Evidence；
3. 在 P4 内修正设计、计划或实现；
4. 通过现有 `prepare_change` / `commit_change` 持久化；
5. 证据成立后继续 P4。

只要 `workflow.stage` 仍为 P4，Runtime 不创建额外 Transition 或 Review Stage。若影响产品边界或 Architecture Decision，继续由既有 Change Kind 和 Maker Authorization 处理。

## 11. Host Runtime Boundary

`windows-desktop` Profile 在激活后只向 Child Skill 与验证过程提供 Windows-specific 约束。Kernel 仍只保存一个 `host_profile_id`。

Runtime 不提供：

- Host 自动选择；
- 多 Host 同时激活；
- Activation 后 Host 迁移或替换；
- 将浏览器、Mod 网站、游戏安装环境登记为 Desktop Host。

## 12. Failure and Recovery

所有 Entry、Host、Workflow Shape 与 Schema 错误均为准备或提交前失败，遵循 fail-closed：

- 不修改三份权威状态；
- 不生成成功 Receipt；
- 不把错误输入规范化成可接受值；
- 修正输入后重新准备新的 Activation Request。

已过期、Digest 不匹配、Prompt Context 不匹配、Revision 冲突与文件写入失败继续使用既有 Kernel 错误和恢复流程。

## 13. Inspect and Status Summary

`inspect_project` 保持现有固定摘要结构，不因 Desktop 增加新的顶层摘要项。Entry 保存在 Project State 1.1 中，可在详细状态读取时恢复；1.0 State 没有 Entry 时不得推断其最初阶段。

## 14. Validation Obligations

实现阶段至少覆盖：

- Registry 1.1 结构、引用和三种 Host Requirement；
- 两个 Workflow Module 的 Entry evaluator；
- Desktop P0–P6 Entry 与 Transition；
- Mod M0–M5 Entry 及 `MODEL_REVIEW` 禁止接管；
- State 1.0/1.1 兼容与 Entry 不可变；
- prepare/initialize 双重校验与完整 Digest；
- REQUIRED Host 缺失、错误 Host、无 Evidence、错误 Shape 的失败关闭；
- Plugin、Legacy unit、Legacy integration 与 Legacy e2e 全量回归；
- Windows Profile 的自动化契约测试与后续真实 Windows 环境验收分层。

自动化只证明结构、路由、状态机和失败语义；桌面自动化证明受控 UI/进程路径；真实 Windows 环境证据才证明安装、升级、卸载、权限、安全软件和恢复行为。

## 15. Implementation Boundary

本文档批准前不得修改 Runtime、Schema、Registry 或 Skill。批准后仍须先完成 Implementation Plan 与 Acceptance Test Plan，并获得 Maker 明确批准，才能开始实现。
