# Web Product Incubator Runtime Specification

> Specification Version: Plugin Web Product V1.2
> Status: DRAFT
> Maker Review: PENDING
> Depends On: `SPECS/CONTRACTS/WEB_PRODUCT_INCUBATOR_CONTRACT.md`
> Implementation Authorization: NOT GRANTED

## 1. Runtime Scope

本规格定义现有 Plugin Runtime 如何加载 `web-product` 配置、校验 Route 与 Entry、准备并提交 Activation、执行 P0–P6、协调 P4/P5 Evidence，并保持次级界面与部署挂起边界。

Runtime 不判断 Web 架构优劣，不选择技术栈，不运行创造性设计，不从 HTTP/MCP Transport 推断 Project Type，不把 build、localhost 或浏览器结果自动解释成 Gate 通过。

## 2. Startup Loading

Plugin 启动时沿用现有顺序：

```text
Registry 1.1
→ Registry 引用与 Host Requirement 校验
→ 每个 Project Type 的 Profile 与 Workflow Module
→ evaluateEntry / evaluateTransition 接口校验
→ Host Profile 引用校验
```

`web-product` 必须解析为：

```text
child_skill_id = "web-product-incubator"
host_profile_requirement = "FORBIDDEN"
```

启动时不加载浏览器驱动、启动 Managed Project、访问 localhost 或探测外部服务。任一 Registry 引用、Workflow Module 或 Requirement 非法时，Plugin 整体启动失败关闭，不静默禁用 Web 类型后继续。

## 3. Route Proposal

`propose_route` 的运行顺序：

1. 接收已讨论出的 `project_type_id` 和候选 `host_profile_id`；
2. 查找 Registry Project Type；
3. 执行 Host Requirement；
4. 校验引用与可用 Child Skill；
5. 返回 `ROUTE_PROPOSED` 或稳定错误。

对于 `web-product`：

- `host_profile_id` 必须为 `null`；
- 非空时返回 `HOST_PROFILE_FORBIDDEN`；
- Runtime 不创建 browser、localhost 或 operating-system Host；
- Runtime 不检查自然语言描述是否真正符合 Web Product，语义分类由 Router Skill 与 Agent 负责；
- Route Proposal 不写权威状态。

## 4. Entry Assessment Preparation

调用 Runtime 前：

- `NEW_PROJECT`：Agent 使用 Web Child Skill 的标准 P0 初始状态；
- `ADOPT_EXISTING`：Agent 读取已有设计、计划、实现、构建、本地运行、浏览器和适用次级界面 Evidence，判断 P0–P6 当前阶段；
- Maker 确认 Entry Mode、Project Type、Product Boundary、无 Host Profile 和完整 Activation Scope。

Runtime 只消费结构化结果，不打开项目文件调查内容，不运行 build 或 browser，不替 Agent 生成阶段结论。

## 5. Prepare Activation

`prepare_activation` 执行：

```text
Assert Uninitialized
→ Resolve web-product Route
→ Enforce FORBIDDEN Host
→ Parse Project State 1.1 and workflow.entry
→ Call Web evaluateEntry
→ Compare Workflow Shape
→ Parse Product Decisions
→ Hash Full Activation Scope
→ Persist Pending Activation Request
```

`scope_digest` 覆盖完整 Initial State，因此覆盖 Entry Mode、Initial Stage、Assessment Summary、Evidence Refs 与 Assessed At，不创建 Web 专用摘要文件。

准备成功只产生 Pending Request，不写 Activation、Project State 或 Receipt。

## 6. Initialize Project

`initialize_project` 保持既有 Session、Turn、Pending Request、Digest、Maker Prompt 和过期校验，并在 Commit 前重新：

1. 解析当前 Registry 与 Web Workflow Module；
2. 确认 Host 仍为空；
3. 解析待提交 Project State 1.1；
4. 调用当前 `evaluateEntry`；
5. 比较 Stage、Allowed Next 与 Return Stage；
6. 验证完整 Activation Scope 未漂移。

通过后才可绑定 Product Decision Authorization、原子写入 Activation 与 Project State、写 Receipt，并消费 Pending Request。

任一步失败不得留下部分 Activation、State 或成功 Receipt。修正输入后必须重新 Prepare，不能重用旧 Digest。

## 7. Entry Evaluation

### 7.1 `NEW_PROJECT`

Web evaluator 只接受：

```text
initial_stage = P0
workflow.stage = P0
workflow.allowed_next = [P1]
workflow.return_stage = null
```

不匹配时返回既有 Workflow Entry 错误。

### 7.2 `ADOPT_EXISTING`

Evaluator 校验：

- `evidence_refs.length >= 1`；
- `initial_stage` 属于 P0–P6；
- `initial_stage == workflow.stage`；
- `return_stage = null`；
- `allowed_next` 与正式阶段映射一致。

Evaluator 不打开 Evidence，不判断已有项目是否真的完成 Build、Browser 或 P5，也不根据文件数量推断阶段。语义判断属于 Agent，Maker 确认完整 Activation Request。

## 8. State Compatibility

Project State Parser 继续接受：

- 1.0：既有结构，可无 `workflow.entry`；
- 1.1：`workflow.entry` 必填。

规则：

- 新 Web 激活只接受 1.1；
- 既有 1.0 Managed Project 继续 Inspect、Prepare Change、Commit Change 与阶段转换；
- Runtime 不自动迁移 1.0 或把既有项目改为 Web；
- 1.1 Entry 在所有 State Mutation 前后深度相等，否则返回 `WORKFLOW_ENTRY_IMMUTABLE`；
- Web 不新增 State Schema Version 或顶层状态分区。

## 9. Web Workflow Execution

Web evaluator 使用：

```text
P0 -> [P1]
P1 -> [P2]
P2 -> [P3]
P3 -> [P4]
P4 -> [P5]
P5 -> [P6]
P6 -> [P2, P3, P4, P5]
```

阶段变化继续要求显式 `workflow_transition`、目标一致、Completion Conditions 满足和必要 Maker Authorization。无阶段变化时携带 `workflow_transition` 继续失败。

Web System Model、Feasibility Probe、Usable Web Slice、Build Readiness、Local Product Validation、Validation Channel、Secondary Interface 与 Creation Correction 都不进入 Runtime Stage 枚举。

## 10. P4 Checkpoint Coordination

Runtime 不创建 Checkpoint Engine。Agent 与 Child Skill在 P4 中准备 Usable Web Slice 与 Build Readiness 材料，Gate 根据已批准 Contract 形成 Evaluation Result，State Mutation 仍通过现有 `prepare_change` / `commit_change`。

Runtime 只负责：

- 维持 `workflow.stage = P4`；
- 校验 Mutation、Revision、Authorization 与 Receipt；
- 在请求 P4→P5 时执行既有 Transition Contract；
- 持久化已获授权的现有状态分区与 Evidence 引用。

Runtime 不负责：

- 把 Script Validation Result 转为 Gate Result；
- 判断 build 日志、浏览器截图或用户观察是否真实；
- 自动把两个 Checkpoint 标记为通过；
- 因 Checkpoint 失败跳转到 P6 或创建新 Stage。

## 11. P5 Evidence Coordination

Build、Logic、Local Integration、Local Browser、Secondary Interface 和 Human Validation 由 Agent、Script、浏览器、Client 或人工过程产生 Evidence，由 Gate 评估其是否满足 P5。

Runtime 对这些通道不增加顶层枚举或专用命令。它继续处理：

- Evidence 引用的结构边界；
- Gate Evaluation Result 的持久化请求；
- P5 Completion Conditions；
- P5→P6 的授权、Commit 与 Read-back。

Runtime 不允许：

- 仅因构建进程退出码为零就提交 P5 通过；
- 仅因端口打开或 HTTP 200 就推断真实浏览器旅程成立；
- 使用 MCP Client 成功替代 Browser Evidence；
- 使用 Browser Evidence 替代适用的 Secondary Interface Evidence；
- 把 localhost 结果升级成 Deployment 或 Production Ready Claim。

## 12. Secondary Interface Runtime Boundary

Runtime 不枚举 REST、GraphQL、WebSocket、Webhook、MCP Transport，也不根据进程、包或端口数量改变 Project Type。

次级界面的设计、实现和验证通过同一 Web Managed Project 的现有 `capabilities`、`assumptions`、`plan`、`gates`、`risks`、`baselines` 与 Evidence 引用协调。

当 Agent 判断次级界面可能成为独立产品时，Runtime 只允许记录 Maker Review Requirement；不得自动迁移 Activation、改写 `project_type_id` 或创建新 Project Type。

## 13. Deployment Deferral Runtime Boundary

Runtime 不实现：

- Deployment Stage 或 Transition；
- Deployment Host Profile；
- 生产环境探测、域名、TLS、CDN 或托管编排；
- Production Ready 自动结论；
- `deployment_capability` State 或 Registry 字段。

Deployment Deferred 由 Child Skill、Plan、Gate、Risk 和 Validation Claim 保持。若请求触及公开部署或生产环境，Runtime 不推断授权；Agent 必须提出新的 Scope 与 Maker Authorization，架构变化仍走 Change Control。

## 14. P4 Creation Correction

P4 出现模型反例或重复失败时：

1. Agent 暂停受影响工作包；
2. 记录 Observation、Hypothesis、失效 Assumption、影响范围与 Evidence；
3. 在已批准边界内修正 Design、Plan 或 Artifact；
4. 通过现有 Context Mutation 流程持久化；
5. 重放受影响的 Build、Integration、Browser 或 Secondary Interface 验证；
6. Evidence 成立后继续 P4。

Runtime 不创建 `MODEL_REVIEW`、Checkpoint Stage 或额外 Transition。超出工作包、Product Boundary、Architecture Decision、Project Type、Deployment Boundary 或 Runtime Invariant 时，输出 Maker Scope Review Requirement 并停止受影响变化。

## 15. Failure and Recovery

Registry、Host、Entry、Workflow Shape、Schema、Digest、Authorization 与 Revision 错误遵循 fail-closed：

- 不修改权威状态；
- 不生成成功 Receipt；
- 不把错误输入规范化成可接受值；
- 不部分激活 Web Project；
- 不把失败改写为其他 Project Type；
- 修正输入后重新 Prepare。

Build、localhost、Browser 或 Secondary Interface 验证失败是 Evidence / Gate 输入，不由 Runtime伪装成 Kernel 成功，也不自动触发 State Mutation。

## 16. Inspect and Status Summary

`inspect_project` 保持现有固定摘要结构，不因 Web Product、MCP、Checkpoint 或 Deployment Deferred 增加新的顶层摘要项。

详细状态可以从 Project State、Profile 与稳定 Evidence 引用恢复。旧 State 1.0 无 Entry 时不得推断其来源阶段；缺少 Evidence 时不得以聊天历史补齐。

## 17. Validation Obligations

实现阶段至少覆盖：

- `web-product` Registry 引用与 `FORBIDDEN` Host；
- Web Child Skill 与 Workflow Module 可发现性；
- NEW_PROJECT P0 与 ADOPT_EXISTING P0–P6；
- P0–P6 顺序、P6→P2–P5 和非法转换；
- prepare/initialize 双重校验、完整 Digest 与 Entry 不可变；
- State 1.0/1.1 兼容；
- P4 Checkpoint 不形成 Stage；
- Build-only、localhost-only、Browser-only 和 Secondary Interface-only 的结论上限；
- 含 MCP Server 的 Web Product 保持 Web 路由，独立 MCP Service 不被误路由；
- Browser 与真实 MCP Client Evidence 不互相替代；
- Deployment Deferred 不产生 Runtime 字段或生产结论；
- Plugin、Legacy、Mod、Desktop、Host、Hook、Receipt 和受保护文件完整回归；
- 候选包安装后能加载 Web Profile、Skill、Workflow 与 Registry；
- 首个已有 Web 项目的真实 `ADOPT_EXISTING` Field Validation。

自动化证明结构、路由、状态机和失败语义；构建证明被测环境的 Artifact 结果；本地集成证明受控服务协作；真实浏览器证明绑定环境中的用户旅程；真实次级 Client 证明对应 Capability。任何通道都不得越过其 Claim 上限。

## 18. Implementation Boundary

Implementation Plan 与 Acceptance Test Plan 获得 Maker 明确批准前，不得修改 Runtime、Schema、Registry、Router、Skill、Profile、Manifest、Template、Hook 或测试。

## 19. Maker Review

Maker 需要确认第 1–18 节，尤其是 Runtime 不解释 Evidence 语义、P4/P5 只复用现有控制面、Secondary Interface 不改变类型，以及 Deployment Deferred 不进入 Runtime Schema。

本 Runtime Specification 当前为 `DRAFT`。Maker 批准后只授权编写 Implementation Plan 与 Acceptance Test Plan；在两份 Plan 获得明确批准前，不授权实现。
