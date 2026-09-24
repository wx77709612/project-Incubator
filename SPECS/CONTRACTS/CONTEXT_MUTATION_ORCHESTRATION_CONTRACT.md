# Context Mutation Orchestration Contract

> Specification Version: V1.1 RC Remediation
> Status: APPROVED
> Approved By: Maker, 2026-09-24
> Depends On: `SPECS/DESIGN/CONTEXT_MUTATION_ORCHESTRATION_DESIGN.md`

## 1. Contract Purpose

本 Contract 定义 Multi-Context Event、Mutation Set、Authorization Request、Authorization Evidence、Closure Result 和错误语义。它增量约束 `CONTEXT_ACCESS_CONTRACT.md`，不替代原有单 Context Access Contract。

## 2. Multi-Context Event Trigger

满足任一条件时必须使用本 Contract：

- 同一业务事件需要修改两个或以上 Context；
- Mutation 涉及 Maker Authorization；
- 一个 Context 的合法状态依赖另一个 Context 的状态或引用；
- Event Recipe 明确要求 Closure Check。

## 3. Mutation Set Request

```text
mutation_set_id: string
event_type: enum
event_ref: string
current_phase: string
requested_by: AGENT | RUNTIME
authority_requirement: NONE | MAKER | EVIDENCE | MAKER_AND_EVIDENCE
authorization_request_ref: string | null
authorization_evidence_ref: string | null
targets: MutationTarget[1..n]
closure_assertions: ClosureAssertion[1..n]
rollback_policy: RESTORE_ALL
```

`mutation_set_id`、`event_type` 和 `event_ref` 构成幂等键。相同幂等键不得重复提交已验证事件。

## 4. Mutation Target

```text
context_type: ContextType
context_ref: string
mutation_intent: string
expected_before: map
proposed_after: map
required_refs: string[]
commit_order: integer
```

约束：

- 同一 Context Target 在一个 Set 中只能出现一次；
- `expected_before` 必须与 Read-back 当前状态匹配；
- `proposed_after` 只包含允许由 Contract 校验的结构化字段；
- `PROJECT_STATE` 的 `commit_order` 必须大于其他目标；
- Target 不得超出 Event Recipe 允许集合。

## 5. Authorization Request Contract

```text
authorization_request_id: string
event_type: string
requested_decision: string
requested_scope: string[]
requested_context_targets: ContextType[]
cost_summary: string
risk_summary: string
unsupported_boundary: string[]
status: PENDING | AUTHORIZED | DECLINED | EXPIRED | SUPERSEDED
```

Request 在 Maker 回答前必须已持久化于 Runtime Pending Request / Execution Record。Agent 输出的一段请求文字本身不等于授权。

## 6. Authorization Evidence Contract

```text
authorization_id: string
authorization_request_id: string
source_actor: MAKER
source_message_ref: string
maker_statement_excerpt: string
authorized_scope: string[]
authorized_context_targets: ContextType[]
confirmed_at: timestamp
statement_digest: sha256
```

有效性要求：

- `authorization_request_id` 必须解析到状态为 `PENDING` 的 Request；
- `source_message_ref` 不得引用 Agent 输出；
- `maker_statement_excerpt` 不得为空；
- Statement Digest 必须与规范化摘录匹配；
- Authorized Scope 和 Targets 必须覆盖所有受保护 Mutation Target；
- 一个 Authorization 只能完成其绑定 Request，不得跨 Capability 或 Event 复用。

仅有以下字段不足以构成授权：

```text
source_actor = MAKER
confirmed = true
```

## 7. Extension Status Contract

```text
PROPOSED
PENDING_MAKER_AUTHORIZATION
ACTIVE
DECLINED
SUSPENDED
```

`ACTIVE` 的必要条件：

```text
matching pending request
+ valid maker authorization evidence
+ complete mutation target set
+ successful closure result
```

缺少任一条件，Result 必须为 `AUTHORIZATION_REQUIRED`、`AUTHORIZATION_INVALID` 或 `CONTEXT_CLOSURE_FAILED`，不得降级为普通成功。

## 8. Closure Assertion

```text
assertion_id: string
left_ref: context.field
operator: EQUALS | EXISTS | ABSENT | COVERS | UNCHANGED
right_value_or_ref: scalar | context.field
severity: REQUIRED
```

V1.1 RC 只支持确定性 Operator。自然语言语义等价不属于 Closure Assertion。

## 9. Orchestration Result

```text
mutation_set_id
status
committed_targets
verified_assertions
authorization_request_ref
authorization_evidence_ref
rollback_status
failure_code
failed_target
```

Status：

```text
AUTHORIZATION_PENDING
VERIFIED
REJECTED
ROLLED_BACK
SUSPENDED
FAILED
```

Failure Code：

```text
MUTATION_SET_INVALID
EVENT_RECIPE_MISMATCH
AUTHORIZATION_REQUIRED
AUTHORIZATION_INVALID
AUTHORIZATION_SCOPE_MISMATCH
PRECONDITION_CONFLICT
STAGE_FAILED
COMMIT_FAILED
CONTEXT_CLOSURE_FAILED
ROLLBACK_FAILED
IDEMPOTENCY_CONFLICT
```

## 10. Atomicity Semantics

本 Contract 的“原子”表示业务可见结果原子：

- 全部目标和 Closure 通过后，Result 才能为 `VERIFIED`；
- 失败时恢复全部已提交目标；
- 回滚成功不等于业务事件成功；
- 回滚失败必须显式返回 `FAILED`。

不要求文件系统提供跨文件原生事务。

## 11. Backward Compatibility

不满足 Multi-Context Trigger 的现有 `ContextAccessRequest` 保持原 Contract。旧请求不得因为缺少 Mutation Set 字段而失败。
