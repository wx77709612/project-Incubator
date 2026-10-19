> 作用域（2026-10-19）：本文保留 V1.x Legacy 兼容设计/回归语义，不定义 Plugin 0.3.x 的状态权威、入口或执行机制。现行 Kernel 规则由 [Kernel Alignment ACP](../ARCHITECTURE/KERNEL_ALIGNMENT_CHANGE_PROPOSAL.md) 及其 Design、Contract、Runtime 和两份 Plan 约束；冲突条款已被 Decision 015 明确替代。非冲突的 Maker Authority、Evidence 和领域方法可作为参考。

# Context Mutation Orchestration Design

> Specification Version: V1.1 RC Remediation
> Status: APPROVED
> Approved By: Maker, 2026-09-24
> Depends On: `SPECS/ARCHITECTURE/CONTEXT_MUTATION_ORCHESTRATION_CHANGE_PROPOSAL.md`

## 1. 设计目的

本设计定义一次业务事件需要同步修改多个 Context 时，Agent 与 Runtime 如何先声明完整变化、验证授权、执行有序提交并证明最终闭合。

它解决“每个文件单独看都可写，但组合后表达了未经授权或彼此冲突的项目状态”的问题。

## 2. Domain Model

### 2.1 Context Mutation Set

最小字段：

```text
mutation_set_id
event_type
event_ref
current_phase
requested_by
authority_requirement
authorization_request_ref
authorization_evidence_ref
targets[]
closure_assertions[]
rollback_policy
```

每个 `target` 包含：

```text
context_type
context_ref
mutation_intent
expected_before
proposed_after
required_refs
commit_order
```

Mutation Set 描述“本次事件完成时必须共同成立什么”，不保存完整文件正文。

### 2.2 Mutation Set Lifecycle

```text
DRAFT
→ AUTHORIZATION_PENDING
→ READY
→ STAGED
→ COMMITTING
→ FINALIZING_AUTHORIZATION
→ VERIFIED
```

异常出口：

```text
REJECTED
ROLLED_BACK
SUSPENDED
FAILED
```

- `AUTHORIZATION_PENDING`：结构已完整，但需要的授权尚未满足；
- `READY`：结构、Authority、Scope 和 Preconditions 已满足；
- `STAGED`：所有目标内容已准备，尚未改变权威 Context；
- `FINALIZING_AUTHORIZATION`：Context Closure 已通过，正在完成绑定 Authorization Request 并执行最终回读；
- `VERIFIED`：全部目标 Read-back 与 Closure Assertions 通过；
- `ROLLED_BACK`：提交后失败，但所有前镜像恢复成功；
- `FAILED`：回滚或恢复不能完成，需要人工处理。

### 2.3 Authorization Request

Pending Request 必须先于 Authorization Evidence 存在：

```text
authorization_request_id
requested_decision
requested_scope
requested_context_targets
cost_summary
risk_summary
unsupported_boundary
created_at
status
```

状态：

```text
PENDING
AUTHORIZED
DECLINED
EXPIRED
SUPERSEDED
```

### 2.4 Authorization Provenance

```text
authorization_id
authorization_request_id
source_actor
source_message_ref
maker_statement_excerpt
authorized_scope
authorized_context_targets
confirmed_at
statement_digest
```

有效授权必须同时满足：

1. `source_actor = MAKER`；
2. Pending Request 存在且状态为 `PENDING`；
3. Maker 陈述明确回答该请求，而不是要求 Agent 发起请求；
4. Authorized Scope 覆盖全部受保护 Mutation；
5. Authorized Context Targets 覆盖本次受保护目标；
6. Authorization 没有过期、撤销或被替代。

Runtime 能验证结构、引用、Scope 和状态绑定。自然语言是否明确授权仍由 Agent 提取并以 Maker 输入为依据；Agent 不得用自己的总结替代 Maker 原文摘录。

## 3. Extension Activation Lifecycle

| Current | Event | Required Authority | Next |
| --- | --- | --- | --- |
| 无 | Recommendation Accepted for Review | 无 | `PROPOSED` |
| `PROPOSED` | Formal Authorization Requested | 无 | `PENDING_MAKER_AUTHORIZATION` |
| `PENDING_MAKER_AUTHORIZATION` | Maker Explicitly Authorizes Matching Request | Maker | `ACTIVE` |
| `PENDING_MAKER_AUTHORIZATION` | Maker Declines | Maker | `DECLINED` |
| `ACTIVE` | Evidence or Authority Requires Pause | Evidence 或 Maker，按影响范围 | `SUSPENDED` |
| `SUSPENDED` | Matching Resume Conditions Satisfied | 原 Authority Requirement | `ACTIVE` |

禁止迁移：

- `PROPOSED → ACTIVE`；
- 没有 Pending Request 的任意状态到 `ACTIVE`；
- 用 Agent Recommendation、Opacity Assessment 或 API Evidence 触发 `ACTIVE`；
- 用一个 Capability 的授权激活另一个 Capability。

## 4. Closure Check

Closure Check 只比较事件 Recipe 声明的结构化事实：

- Extension Status；
- Capability ID 与 Scope；
- Authorization Request / Evidence Ref；
- Current Phase；
- Evidence Level 与 Claim 边界；
- Human Validation Budget；
- Baseline、Decision、Assumption 或 Ring Ref；
- Artifact 的存在性和版本。

它不比较全文措辞，不把同义词匹配当作授权，也不判断候选模型技术上是否正确。

### 4.1 Extension Pending Recipe

```text
PROJECT_STATE.extension_status = PENDING_MAKER_AUTHORIZATION
PROJECT_PLAN.extension_status = PENDING_MAKER_AUTHORIZATION
authorization_request.status = PENDING
CAPABILITY_SPIRAL_RECORD is absent or INACTIVE_DRAFT
current_phase remains unchanged
human_validation_budget.consumed remains unchanged
```

允许保留人工验收现场中的 `INACTIVE_DRAFT`，但它必须明确非权威、不得被 Runtime 当作启用记录，也不得声称 Maker 接受成本或风险。正常生产路径默认不创建。

### 4.2 Extension Active Recipe

```text
authorization_request.status = AUTHORIZED
authorization_evidence.request_ref matches request
PROJECT_STATE.extension_status = ACTIVE
PROJECT_PLAN.extension_status = ACTIVE
CAPABILITY_SPIRAL_RECORD.status = ACTIVE
all capability_id and scope values match
current_phase remains unchanged
```

## 5. 提交顺序

默认顺序：

```text
1. Optional Context / Extension Artifact
2. PROJECT_PLAN.md
3. PROJECT_DECISIONS.md（仅事件需要时）
4. PROJECT_PROFILE.md（仅事件需要时）
5. PROJECT_STATE.md
6. Read-back Closure Check
```

`PROJECT_STATE.md` 最后提交。事件 Recipe 可以减少目标，但不得把它提前到从属 Context 之前。

## 6. 回滚与恢复

Runtime 在 Commit 前保存目标文件的前镜像摘要和恢复材料。Closure 失败时按逆序恢复；恢复后再次 Read-back。

恢复成功返回 `ROLLED_BACK`，项目继续保持事件发生前状态。恢复失败返回 `FAILED`，Runtime 必须列出未恢复目标并阻止继续执行。

Mutation Set 不允许通过“下一轮再补另一个文档”宣称本轮成功。

上述 Lifecycle 是 Mutation Set 的内部执行状态，不新增 Runtime Execution State，也不得写入 `PROJECT_STATE.md` 的 Current Phase。

## 7. Agent 行为要求

Agent 在多 Context 事件中必须：

1. 先识别业务事件和 Authority Requirement；
2. 列出全部目标 Context 与共同后置条件；
3. 缺少 Maker Authorization 时只写入 Pending 状态并正式请求决定；
4. 不从任务措辞、历史认可或“继续”推导授权 Scope；
5. Mutation 后回读全部目标；
6. 只在 Closure 通过后报告完成。

## 8. 轻量性边界

以下情况不强制创建 Mutation Set：

- 单文件、无受保护 Authority、无跨 Context 后置条件的内容修正；
- 只读分析；
- 不持久化的 Advisory；
- Script 产生但尚未被接受为 Context Mutation 的 Evidence。

只要一个事件要求两个或以上 Context 表达同一受保护状态，或涉及 Maker Authorization，即进入该设计。
