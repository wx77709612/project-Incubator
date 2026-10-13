# Web Product Incubator Contract

> Specification Version: Plugin Web Product V1.2
> Status: DRAFT
> Maker Review: PENDING
> Depends On: `SPECS/ARCHITECTURE/ARCHITECTURE_DECISIONS.md` Decision 014；`SPECS/PROJECT_TYPES/WEB_PRODUCT_PROFILE.md`
> Implementation Authorization: NOT GRANTED

## 1. Contract Scope

本文档把已批准的 `web-product` Design 转换为 Registry、Route、Workflow Entry、Activation、P0–P6、P4 Checkpoint、P5 Evidence、次级集成界面和部署挂起的交互契约。

本文档不重新定义 Core Phase、Maker Authority、Context Authority 或 Evidence Model，不新增 Web/MCP 专用权威状态，不授权修改 Plugin 实现。

既有 Maker Authorization、MCP-only Mutation、Pending Request、Receipt、Hook、Revision、Context Mutation 和 Project State 1.1 Contract 继续有效。

## 2. Registry Contract

`web-product` 的 Registry 条目必须满足：

```text
id = "web-product"
child_skill_id = "web-product-incubator"
profile_path = <active web product profile path>
workflow_module = <plugin-local workflow module path>
host_profile_requirement = "FORBIDDEN"
```

约束：

- `host_profile_id` 必须为 `null`；
- Router 和 Kernel 不得为浏览器、localhost、操作系统或本地运行环境创建或自动选择 Host；
- `profile_path`、`workflow_module` 与 `child_skill_id` 必须存在并留在 Plugin 允许边界内；
- Registry 继续使用已实现的 `schema_version = 1.1`，本 Contract 不提升版本；
- `deployment_capability = DEFERRED_CAPABILITY` 是 Architecture、Design 与 Planning 语义，不进入 Registry Schema；
- REST、GraphQL、WebSocket、Webhook、MCP 或其他次级界面不产生新的 Registry Project Type 条目。

Registry 缺失引用、绑定非空 Host 或使用未知 Project Type 时失败关闭。

## 3. Route Proposal Contract

`propose_route` 保持既有 Tool 形状。Router Skill 根据 Maker 提供的主要产品形态提议 `web-product`；Kernel 只校验提议的稳定 ID、Host Requirement 和 Registry 引用，不从自然语言自行分类。

Router Skill 只有在以下边界成立时才可提议 `web-product`：

- 通用浏览器是主要用户界面；
- 同时具有前端与后端逻辑职责；
- 至少一条核心旅程穿过浏览器与后端或数据边界；
- Product Boundary 把可重复构建与 localhost 运行作为目标完成条件；
- 核心结果计划在真实浏览器中观察。

浏览器扩展、纯后端服务、独立 MCP Service、无后端职责的静态前端、桌面、移动、CLI、SDK、库和 Mod 必须返回不支持或提议其他已注册类型，不得因使用 HTTP 或存在辅助网页而误路由到 `web-product`。

Route Proposal 不是激活，不写权威状态。Maker 明确确认完整 Activation Scope 后才能进入激活流程。

## 4. Workflow Evaluator Contract

Web Workflow Module 复用通用接口：

```text
evaluateEntry(initialState) -> EntryEvaluation
evaluateTransition(currentState, transitionRequest) -> TransitionEvaluation
```

`evaluateEntry` 返回既有结构：

```text
allowed: boolean
code: string
workflow?: {
  stage: string
  allowed_next: string[]
  return_stage: string | null
}
```

Kernel 比较 evaluator 返回的 Workflow Shape 与 Initial State，不判断 Web Product Model、Evidence 内容或阶段分析是否真实。

`evaluateTransition` 只处理正式 P0–P6 Stage、既有 Completion Conditions 和 Maker-owned Boundary Change，不把 Checkpoint、Validation Channel、Creation Correction 或次级界面写成 Stage。

## 5. Workflow Entry State Contract

Web Product 新激活继续使用 Project State `schema_version = 1.1` 与既有 `workflow.entry`：

```text
entry: {
  mode: NEW_PROJECT | ADOPT_EXISTING
  initial_stage: string
  assessment_summary: string
  evidence_refs: string[]
  assessed_at: RFC 3339 timestamp
}
```

通用约束保持：

- `entry.initial_stage == workflow.stage`；
- `return_stage = null`；
- `assessment_summary` 与 `evidence_refs` 满足既有长度和数量上限；
- Entry 纳入 Activation `scope_digest`；
- Entry 在激活后不可修改；
- 旧 Project State 1.0 继续兼容，不自动回填 Entry。

Mode 约束：

| Mode | Initial Stage | Evidence Refs |
| --- | --- | --- |
| `NEW_PROJECT` | 必须为 P0 | 可为空 |
| `ADOPT_EXISTING` | P0、P1、P2、P3、P4、P5 或 P6 | 至少一项 |

`ADOPT_EXISTING` Evidence 可以引用已有设计、计划、实现、构建、本地运行、浏览器、次级界面或人工验证材料。Kernel 只校验引用字段结构与非空性，不打开文件或评价 Evidence 强弱。

## 6. Entry Responsibility Boundary

- Maker：说明新建或接管模式、项目来源、主要产品形态、Product Boundary 和完整激活范围，并确认无 Host Profile；
- Agent：检查已有 Artifact 与 Evidence，判断 `initial_stage`，形成摘要和稳定引用；
- Router Skill：提议 Project Type，解释适用与排除依据；
- Web Child Workflow：声明标准初始阶段、接管阶段集合和正式 Transition；
- Kernel：校验结构、Registry、Host Forbidden、Workflow Shape、Authorization 与 Digest。

Maker 不替 Agent 完成阶段分析；Kernel 不把 Build 成功、localhost 存活或单一接口探测解释成 P5 成立。

## 7. Web Entry and Transition Contract

Web Workflow 的正式阶段集合为 P0–P6：

| Current | Allowed Next |
| --- | --- |
| P0 | P1 |
| P1 | P2 |
| P2 | P3 |
| P3 | P4 |
| P4 | P5 |
| P5 | P6 |
| P6 | P2、P3、P4 或 P5 |

约束：

- `NEW_PROJECT` 只能从 P0 激活；
- `ADOPT_EXISTING` 可以从 P0–P6 正常阶段激活；
- Usable Web Slice、Build Readiness、Local Product Validation 与 Creation Correction 不是 Stage；
- P4 Creation Correction 使用普通受控 State Mutation，不提交 `workflow_transition`；
- P6 不产生到 P0 或 P1 的 Transition；若 Intent、Product Boundary 或 Project Type 失效，输出 Maker Review Requirement；
- `READY_FOR_TRANSITION` 不等于 Transition 已执行，只有授权后的 Commit 和 Read-back 成功才完成转换。

## 8. Activation Contract

现有 `propose_route`、`prepare_activation` 与 `initialize_project` Tool 形状保持不变，不新增 Web 专用激活 Tool。

`prepare_activation` 必须：

1. 确认项目尚未激活；
2. 解析 Registry 1.1；
3. 确认 `web-product.host_profile_requirement = FORBIDDEN` 且请求 Host 为空；
4. 解析 Project State 1.1 与 `workflow.entry`；
5. 调用 Web `evaluateEntry`；
6. 比较 `stage`、`allowed_next` 与 `return_stage`；
7. 将 Route、Initial State、Product Decisions 和摘要纳入既有 `scope_digest`；
8. 创建待 Maker 授权的 Activation Request。

`initialize_project` 在 Commit 前重复 Registry、Host、State、Entry 和 Workflow Shape 校验。任一输入或引用漂移时失败关闭，不得使用准备阶段的旧结果继续提交。

## 9. P4 Checkpoint Contract

P4 包含两个 Design Checkpoint：

- `Usable Web Slice`；
- `Build Readiness`。

它们通过现有 `capabilities`、`assumptions`、`plan`、`gates`、`risks`、`baselines` 和 Evidence 引用表达，不新增 `workflow.stage`、State 顶层字段或第二份 Current Project State。

Agent 在请求 P4→P5 前必须为两个 Checkpoint 分别提供：

- Evidence Refs；
- Claim Scope；
- Known Limitations；
- 未满足时的 Failure Routing。

对于 Web Product，这两个 Checkpoint 均适用，不能用“不适用”绕过 Build 或核心浏览器切片。Gate 根据已批准规格分别返回现有 Gate Evaluation Result；只有两项均为 `REQUIREMENT_SATISFIED` 时，Checkpoint Contract 才不阻止 P4→P5。Script Validation Result 不能自动成为 Gate Result。

## 10. P5 Validation Contract

Web Validation Result 必须区分以下 Design Channel：

```text
LOGIC_AUTOMATION
BUILD_VALIDATION
LOCAL_INTEGRATION_VALIDATION
LOCAL_BROWSER_VALIDATION
SECONDARY_INTERFACE_VALIDATION
HUMAN_VALIDATION
```

这些标识用于 Artifact、Gate Input 和 Evidence 引用，不增加 Core Runtime 枚举。每项材料至少包含：

- Channel；
- 被测代码 Revision 与构建 Artifact；
- 依赖和关键工具名称与版本；
- 环境与关键配置摘要，敏感值只能记录来源类别或脱敏标识；
- 场景、步骤、观察结果和关键失败反馈；
- 前端、后端、数据、外部依赖和外部副作用的适用状态；
- Evidence Refs；
- Claim Scope 与 Known Limitations；
- 观察事实、Script Validation Result（仅适用确定性 Script 时）或未形成结论的 Reason；
- 适用性及其与 Product Boundary 一致的理由。

Channel-specific Binding：

- `LOCAL_INTEGRATION_VALIDATION` 必须绑定 localhost URL、端口、协议、启动配置摘要以及前端、后端、数据和适用外部依赖状态；
- `LOCAL_BROWSER_VALIDATION` 必须绑定目标浏览器名称与版本、localhost URL、端口、协议、入口、用户步骤、可见结果和对应后端或数据结果；
- `SECONDARY_INTERFACE_VALIDATION` 必须绑定真实 Client 名称与版本、Transport、Capability、非敏感授权上下文、输入、允许路径结果、未授权或越权拒绝路径、协议失败、业务失败、审计和外部副作用；
- `HUMAN_VALIDATION` 必须绑定观察者角色、被测场景、环境和明确观察，不得用无范围的口头结论替代 Evidence。

P5 最低要求：

- Build Requirement 的 Gate Evaluation Result 为 `REQUIREMENT_SATISFIED`；
- Local Integration Requirement 的 Gate Evaluation Result 为 `REQUIREMENT_SATISFIED`；
- Local Browser Requirement 的 Gate Evaluation Result 为 `REQUIREMENT_SATISFIED`，且 Evidence 至少覆盖一个真实浏览器核心旅程；
- 适用的关键失败路径有 Evidence；
- Product Boundary 包含次级界面时，对应 Secondary Interface Requirement 的 Gate Evaluation Result 为 `REQUIREMENT_SATISFIED`；
- 明确记录 Deployment 未验证，不能产生 Production Ready Claim。

条件通道不适用时必须记录与 Product Boundary 一致的理由。Build、Logic、Browser、Secondary Interface 和 Human Evidence 不能互相替代。任何 Script Validation Result、Observation 或 Human Judgment 都不能直接替代 Gate Evaluation Result。

## 11. Secondary Interface Contract

REST、GraphQL、WebSocket、Webhook、MCP 等次级界面只有在以下条件均成立时继续属于同一 Web Managed Project：

- 服务同一 Product Boundary 与主要用户结果；
- 复用同一业务模型、数据、身份、授权、审计和外部副作用政策；
- 共享主要版本与变更生命周期；
- 不是当前 Managed Project 的主要独立交付物。

每个次级 Capability 必须具有独立 Claim、Security Boundary 与 Evidence Ref。MCP Validation 必须绑定真实 Client、Transport、Tool/Resource 或等价能力、非敏感授权上下文、允许路径、未授权或越权拒绝路径、结果、协议失败、业务失败、审计和副作用，并证明观察到的授权行为与同一后端授权政策一致。

Transport、进程、包或部署单元变化不触发自动迁移。若独立产品条件成立，Agent 输出 Maker Project Type Review Requirement；Router 和 Kernel 不自动改写激活状态。

## 12. Deployment Deferral Contract

V1.2 不创建 Deployment Phase、Deployment Host、Deployment Gate Type 或 Runtime Schema 字段。

下列结果不得被命名为 Deployment Validated 或 Production Ready：

- build 成功；
- localhost 服务可访问；
- Local Browser Validation 通过；
- 既有线上 URL 可以打开但未按本版本验证；
- MCP 或其他次级 Client 调用成功。

计划、Gate Input、Risk 与 Validation Result 必须保留 `DEFERRED_CAPABILITY` 语义和结论上限。未来启用部署时另提 Architecture Change。

## 13. Failure Semantics

Registry、Entry、Host 和 Workflow Shape 继续使用既有稳定错误码，包括：

- `HOST_PROFILE_FORBIDDEN`；
- `WORKFLOW_ENTRY_REQUIRED`；
- `WORKFLOW_ENTRY_MODE_INVALID`；
- `WORKFLOW_ENTRY_STAGE_INVALID`；
- `WORKFLOW_ENTRY_EVIDENCE_REQUIRED`；
- `WORKFLOW_ENTRY_STATE_MISMATCH`；
- `WORKFLOW_ENTRY_IMMUTABLE`；
- `WORKFLOW_ALLOWED_NEXT_MISMATCH`；
- `WORKFLOW_RETURN_STAGE_MISMATCH`。

Web Checkpoint 或 Validation 缺失通过现有 Gate Evaluation Result 与 Reason 表达，不由 Script 直接发 Runtime Command，也不在本 Contract 中新增 Kernel Error Code。

所有失败只阻止当前操作，不产生部分 Activation、部分 State Mutation、伪造 Receipt 或隐式 Product Type 迁移。

## 14. Compatibility Contract

- 不迁移既有 Managed Project；
- 不修改 `mod`、`desktop-product`、`sims-4` 或 `windows-desktop` 的领域语义；
- 旧 Project State 1.0 无 Entry 时继续可用；所有新 Web 激活使用 State 1.1；
- Registry 保持 1.1，不新增 Host Profile；
- Activation 文件继续使用唯一 `host_profile_id`，Web 值必须为 `null`；
- 不新增 Web/MCP 专用权威 Markdown 或 JSON 状态文件；
- Candidate Package 必须保持 Plugin、Legacy、Mod 与 Desktop 回归；
- V1.2 发布前重新确认 V1.1 实际发布基线与 Package Version。

## 15. Contract Acceptance

Contract 验收必须证明：

1. `web-product` Registry 条目使用 `FORBIDDEN` Host 且非空 Host 失败关闭；
2. Web 新项目只能从 P0 激活，已有项目可从 P0–P6 基于 Evidence 接管；
3. Entry 纳入授权摘要且激活后不可变；
4. P0–P6 与 P6→P2–P5 保持既有语义；
5. P4 Checkpoint 不进入 Stage，且两项结论不能互相替代；
6. Build-only、Logic-only 或进程存活不能满足 P5；
7. 真实浏览器核心旅程是 P5 必要 Evidence；
8. 适用次级界面具有独立真实 Client Evidence，但不替代浏览器 Evidence；
9. MCP 等次级界面不自动改变 Project Type；
10. Deployment Deferred 不产生 Runtime 字段、Phase 或生产 Claim；
11. Kernel 不解释 Evidence 语义，Gate Result 不直接修改状态；
12. 现有 Project Type、State 1.0 和完整回归保持兼容。

## 16. Maker Review

Maker 需要确认第 1–15 节，尤其是 Host Forbidden、P4 Checkpoint 表达、P5 最低 Evidence、Secondary Interface 与 Deployment Deferral Contract。

本 Contract 当前为 `DRAFT`。Maker 批准后只授权将其作为 Runtime Specification 和后续 Implementation/Acceptance Planning 的上游依据；在 Runtime Specification、Implementation Plan 与 Acceptance Test Plan 分别获批前，不授权实现。
