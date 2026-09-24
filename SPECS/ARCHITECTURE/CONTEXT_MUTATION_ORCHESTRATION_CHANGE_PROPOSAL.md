# Context Mutation Orchestration Architecture Change Proposal

> Specification Version: V1.1 RC Remediation
> Status: DRAFT / REVIEW REQUIRED
> Finding: `MULTI_CONTEXT_MUTATION_ORCHESTRATION_GAP`
> Evidence Date: 2026-09-24

## 1. 变更动机

“雾港提醒器”人工验收 Round 2 中，Agent 正确识别了不透明 Capability、Evidence Level 和人工验证预算，但把“要求评估并提出启用请求”误判为“Maker 已授权启用”。该错误随后被同时写入 `PROJECT_STATE.md`、`PROJECT_PLAN.md` 和 `CAPABILITY_SPIRAL_RECORD.md`，而 `SOLUTION_DESIGN.md` 仍明确写着“需要 Maker 授权”。

Round 2C 在明确纠正 Prompt 下恢复了 `PENDING_MAKER_AUTHORIZATION`，证明单个 Context 的 Mutation 能力存在，但当前架构没有保证一次业务事件涉及的多个 Context 共同满足同一授权事实和最终状态。

本提案把该缺口定义为 Release Blocking：

```text
局部 Mutation 合法
不等于
跨 Context 的业务状态闭合
```

## 2. 目标

Core 增加以下治理能力：

- 用显式 Extension Lifecycle 区分建议、待授权、已启用、拒绝和暂停；
- 用 `Context Mutation Set` 描述一次业务事件要求的全部 Context 变化；
- 用 `Authorization Provenance` 把授权绑定到具体 Maker 输入、请求和 Scope；
- 在提交后执行跨 Context `Closure Check`；
- 任一目标写入或闭合失败时，不得报告业务事件完成；
- 保存低体积执行摘要，不新增长期重复 Source of Truth。

## 3. 架构决策提案

### 3.1 Mutation Set 是执行对象，不是 Project Context

`Context Mutation Set` 是 Runtime 为一次业务事件建立的有界执行对象。它声明触发事件、所需 Authority、目标 Context、预期变化、提交顺序和闭合断言。

它不得成为新的 Core Context，不得复制完整项目状态，也不得由 Managed Project 长期全文维护。Runtime Execution Record 只保存其 ID、摘要、结果和 Evidence Ref。

### 3.2 PROJECT_STATE 最后提交

涉及 `PROJECT_STATE.md` 的多 Context Mutation 必须先完成从属 Context 的暂存和验证，再最后提交 `PROJECT_STATE.md`。该文件继续是 Current Project State 的唯一 Source of Truth，也是本次业务事件完成的最终持久化标志。

### 3.3 Runtime 验证闭合，不创作语义内容

Agent 仍负责提出语义内容和目标变化；Runtime 只验证：

- Mutation Set 结构完整；
- Authority Requirement 已满足；
- 目标 Context 与事件 Recipe 匹配；
- 提交前置条件成立；
- Read-back 后的结构化状态一致。

Runtime 不决定是否应启用 Extension，不把 Recommendation 提升为 Authorization，也不替 Agent撰写设计。

### 3.4 Maker Authorization 必须绑定 Pending Request

Maker Authorization 不能只由 `source = MAKER` 与 `confirmed = true` 表示。它必须引用一个此前已存在的 Pending Authorization Request，并记录 Maker 输入引用、授权陈述摘要、有效 Scope 和允许的 Mutation Targets。

请求评估、要求提出授权请求、继续分析或认可风险说明，均不自动构成启用授权。无法验证绑定关系时，状态保持 `PENDING_MAKER_AUTHORIZATION`。

### 3.5 Extension 生命周期属于 Core 治理

Core 定义通用状态：

```text
PROPOSED
PENDING_MAKER_AUTHORIZATION
ACTIVE
DECLINED
SUSPENDED
```

Opaque Capability Extension 使用该状态，但不得改变 Core Phase。`ACTIVE` 只能由与 Pending Request 匹配的 Maker Authorization 触发。

## 4. Core 与 Extension 边界

Core 负责：

- Mutation Set、Authorization Provenance 和 Closure Result 的通用模型；
- 权威来源、目标集合、提交顺序、回滚与恢复规则；
- 生命周期状态的合法迁移；
- 事件 Recipe 的注册与确定性校验。

Opaque Capability Extension 负责：

- 启用请求需要说明的 Capability Scope、验证成本、风险和不支持边界；
- Capability Spiral Record 在 `ACTIVE` 或后续状态中的 Extension 特有内容；
- Extension 事件对应的 Context Recipe。

## 5. 首批事件 Recipe

V1.1 RC 修复至少定义：

| Event | 必须保持的闭合关系 |
| --- | --- |
| `OPAQUE_EXTENSION_RECOMMENDED` | 只能形成建议，不得出现 `ACTIVE` 或 Maker 已接受成本的陈述 |
| `OPAQUE_EXTENSION_AUTHORIZATION_REQUESTED` | State 与 Plan 均为 `PENDING_MAKER_AUTHORIZATION`；不得创建 Active Spiral Record |
| `OPAQUE_EXTENSION_ACTIVATED` | Authorization 与 Pending Request 匹配；State、Plan、Spiral Record 均为 `ACTIVE` |
| `OPAQUE_EXTENSION_DECLINED` | State 与 Plan 均为 `DECLINED`；不得保留 Active Spiral Record |
| `OPAQUE_EXTENSION_SUSPENDED` | State、Plan 与现有 Spiral Record 均为 `SUSPENDED` |
| `ASSUMPTION_INVALIDATED` | Evidence Ref、受影响 Scope 和依赖 Artifact 引用闭合，不伪造 Maker Decision Authorization |
| `P4_CORRECTION_UPDATED` | Current Phase 保持 P4；Correction Activity、Plan 与受影响 Artifact 引用一致 |
| `BASELINE_UPDATED` | Claim、Baseline、Evidence 与 State 摘要引用一致 |
| `RING_CLOSED` | Ring Closure Result、Evidence Level、Baseline 与 Capability Claim 不互相越界 |

首个实现和 Release Blocking 验收聚焦前三个 Extension 事件。其余 Recipe 可以复用同一机制，但不得扩大为新的 Phase 或自动技术判断。

## 6. 失败与恢复原则

- Prepare 失败：不写入任何 Context；
- Stage 失败：丢弃暂存内容；
- Commit 失败：恢复本次已提交目标的前镜像；
- Read-back 或 Closure 失败：回滚并进入 `SUSPENDED`；
- 回滚失败：进入 `FAILED`，保留恢复清单，不得继续同一业务事件；
- 任何失败都不得生成“已启用”“已完成”或等价成功结论。

## 7. 非目标

- 不新增 Core Phase、Transition、Gate Type 或 Runtime Execution State；
- 不把全部普通单文件编辑强制升级为 Mutation Set；
- 不由 Runtime 判断自然语言技术结论是否正确；
- 不声称结构校验可以密码学证明消息作者身份；
- 不把完整 Maker 对话复制进长期 Context；
- 不要求重建当前模拟项目。

## 8. 兼容性

单文件、无跨 Context 后置条件且不涉及 Maker Authority 的 V1.0/V1.1 Mutation 保持原路径。只有注册为 Multi-Context Event、涉及 Maker Authorization，或声明跨 Context Closure Requirement 时，才必须使用 Mutation Set。

旧 Managed Project 不需要回填历史 Authorization Provenance。下一次触发受保护事件时，先建立新的 Pending Request。

## 9. 验收标准

- Round 2 原始输入不能产生 `ACTIVE`；
- Agent 构造的 `source = MAKER` 与 `confirmed = true` 不能单独激活 Extension；
- 没有匹配 Pending Request 的 Authorization 被拒绝；
- Authorization Scope 小于 Mutation Scope 时被拒绝；
- State、Plan、Spiral Record 任一状态不一致时 Closure 失败；
- 任一提交失败时不留下部分激活；
- `PROJECT_STATE.md` 只在其他目标验证后提交；
- Round 2C 的等待授权状态可被一致重建；
- 合法 Maker 授权可以一次性闭合为 `ACTIVE`，且不改变 Phase；
- V1.0 单文件 Mutation 回归保持通过。

## 10. 审批影响

本提案获批后，需要：

1. 在 `ARCHITECTURE_DECISIONS.md` 登记 Decision 012；
2. 将 Design、Contract 和 Runtime Delta 合并为活动规格；
3. 更新 Implementation Plan 与 Acceptance Test Plan；
4. 按 TDD 修改 Skill、Runtime、Definitions、Templates 与 Tests；
5. 重新构建和安装 RC；
6. 使用现有 `ProjectSimulator` 从 Extension Authorization Request 处重放。
