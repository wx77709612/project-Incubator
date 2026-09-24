# Context Mutation Orchestration Runtime Specification

> Specification Version: V1.1 RC Remediation
> Status: DRAFT / REVIEW REQUIRED
> Depends On: `SPECS/CONTRACTS/CONTEXT_MUTATION_ORCHESTRATION_CONTRACT.md`

## 1. Runtime Scope

本规格定义 Context Coordinator 如何执行 Multi-Context Mutation。它不新增 Runtime Component，由现有 Runtime Coordinator 负责路由、Context Coordinator 负责准备与持久化、Gate Coordinator 负责既有 Gate Requirement，Result Coordinator 负责最终结果。

## 2. Execution Flow

```text
Receive Multi-Context Event
→ Resolve Event Recipe
→ Build / Validate Mutation Set
→ Resolve Pending Authorization Request
→ Validate Authorization Provenance and Scope
→ Read All Preconditions
→ Stage All Proposed Targets
→ Validate Staged Targets
→ Commit Non-State Targets in Order
→ Commit PROJECT_STATE Last
→ Read Back All Targets
→ Evaluate Context Closure Assertions
→ Finalize Authorization Request Status
→ Read Back Authorization and Final Closure
→ Record VERIFIED Result
```

任一步失败进入对应 Failure Flow，不允许跳过中间步骤后补写。

## 3. Event Recipe Resolution

Definition Resolver 根据 `event_type` 返回：

```text
allowed_targets
required_targets
authority_requirement
allowed_status_transition
commit_order
closure_assertions
```

Definition 缺失、重复或互相冲突时返回 `EVENT_RECIPE_MISMATCH` 并进入 `SUSPENDED`。Runtime 不自行猜测目标集合。

## 4. Authorization Handling

Authority Requirement 包含 Maker 时，Runtime 必须：

1. 读取 `authorization_request_ref`；
2. 验证 Request 状态为 `PENDING`；
3. 验证 Evidence 引用该 Request；
4. 验证 Source Message Ref 的角色为 Maker；
5. 验证 Statement Digest；
6. 验证 Scope 与 Context Targets 覆盖本次 Set；
7. 把 Request 的 `PENDING → AUTHORIZED` 作为本次 Orchestration 的最终受保护步骤；
8. Request 更新后重新读取 Authorization 与全部 Context，再形成 `VERIFIED` Result。

如果当前 Host 不能提供可信 Message Role，则 Runtime 只能验证结构和引用，并必须要求 Agent 在 Skill 行为层展示 Maker 原文摘录；不得把该限制描述为密码学身份验证。

授权不足时返回 `AUTHORIZATION_PENDING` 或 `AUTHORIZATION_INVALID`，不 Stage、不写 Context。

## 5. Staging

Context Coordinator 为每个目标生成：

```text
before_digest
before_recovery_material
staged_content
staged_digest
validation_result
```

所有目标 Stage 成功后才能 Commit。Stage 文件不得位于 Managed Project 的权威路径，不得被 Context Reader 误认为当前状态。

## 6. Commit Order

Runtime 按 Recipe 的 `commit_order` 提交。涉及 `PROJECT_STATE.md` 时，它必须最后提交。

每个单文件 Commit 使用临时文件替换和 Read-back Digest 验证。前一目标验证成功后才能提交下一目标。

## 7. Closure Evaluation

全部目标提交后，Context Coordinator 重新从权威路径读取内容，禁止直接复用内存中的 staged value。Closure Engine 只执行 Contract 支持的确定性 Assertion。

Context Closure 通过后，Runtime 才把绑定 Request 更新为 `AUTHORIZED`，随后执行 Final Closure。Request 状态更新失败、Final Closure 失败或 Runtime 在二者之间中断时，本次 Orchestration 仍未完成；恢复流程必须完成 Final Closure，否则恢复 Context 前镜像并把 Request 恢复为 `PENDING`。

Extension Activation 至少验证：

- State、Plan 与 Spiral Record 的 `capability_id` 相同；
- 三者状态均为 `ACTIVE`；
- Authorization Request 与 Evidence Ref 相同；
- Scope 不超过授权 Scope；
- Current Phase 与 Mutation 前一致；
- Human Validation Budget 消耗值未因激活自动增加。

## 8. Failure Flow

### 8.1 Prepare 或 Authorization Failure

不产生 Context Write。Runtime 返回 `REJECTED` 或 `AUTHORIZATION_PENDING`。

### 8.2 Stage Failure

删除本次暂存对象，返回 `STAGE_FAILED`，Runtime 进入 `SUSPENDED`。

### 8.3 Commit、Authorization Finalization 或 Closure Failure

按已提交目标的逆序恢复前镜像，并逐项 Read-back；如果 Request 已被更新为 `AUTHORIZED`，同时恢复为 `PENDING`：

- 全部恢复成功：Result=`ROLLED_BACK`，Runtime=`SUSPENDED`；
- 任一恢复失败：Result=`FAILED`，Runtime=`FAILED`，记录未恢复目标。

不得在下一轮静默补齐后把原 Mutation Set 改写为成功。重试必须创建新 Attempt，并引用原 Set。

## 9. Idempotency

同一 `mutation_set_id + event_type + event_ref`：

- 已 `VERIFIED`：返回原结果，不重复写入；
- `AUTHORIZATION_PENDING`：允许绑定后续匹配授权后继续；
- `ROLLED_BACK` 或 `SUSPENDED`：新 Attempt 必须引用旧 Set，并重新读取 Preconditions；
- Payload Digest 不同：返回 `IDEMPOTENCY_CONFLICT`。

## 10. Recovery

Runtime 重启后只恢复非终态 Set：

- `AUTHORIZATION_PENDING`：重新验证 Pending Request；
- `STAGED`：丢弃旧暂存并重新 Prepare；
- `COMMITTING`：根据 Execution Record 和 Read-back 判断继续 Closure 或执行回滚；
- `FINALIZING_AUTHORIZATION`：验证 Request 与 Context 是否均已满足 Final Closure；不能闭合时恢复 Request 和 Context 前镜像；
- `FAILED`：不得自动恢复。

Runtime Execution Record 保存：

```text
mutation_set_id
attempt_id
event_type
target_refs
authorization_refs
before_digests
staged_digests
committed_targets
closure_result
rollback_result
```

## 11. Skill Guidance Integration

Skill 在识别 Multi-Context Trigger 后必须先形成 Mutation Set 摘要，再执行文件修改。完成报告必须列出：

- 触发事件；
- 使用的授权依据或 Pending 状态；
- 实际修改目标；
- Closure Check 结果；
- Phase 是否保持不变。

当 Agent 无法调用 Runtime Orchestration API 时，也必须按相同顺序执行并回读验证；这种行为级降级不能省略 Authorization Provenance 或 Closure Check。

## 12. Automated Acceptance Requirements

至少覆盖：

1. Round 2 原始语境停留在 `PENDING_MAKER_AUTHORIZATION`；
2. 伪造布尔授权被拒绝；
3. 无 Pending Request 的 Maker Evidence 被拒绝；
4. Scope 或 Target 不覆盖时被拒绝；
5. 合法授权使三个目标共同进入 `ACTIVE`；
6. 第二个目标 Commit 失败时全部恢复；
7. Closure 状态不一致时全部恢复；
8. `PROJECT_STATE` 在提交序列中最后；
9. 激活不改变 Phase 或消耗人工预算；
10. V1.0 单 Context Mutation 保持兼容。

## 13. Manual Acceptance Replay

重新安装 RC 后，继续使用现有 `ProjectSimulator`：

1. 保留 Round 2C 的 Pending 状态；
2. Maker 对现有正式请求给出明确、限定 Scope 的授权；
3. Agent 必须同步激活 State、Plan 和 Spiral Record；
4. Agent 必须报告 Authorization Request Ref 与 Closure 结果；
5. Maker 检查 Phase 仍为 P2、预算仍为 0/4；
6. 再进入原 Round 3。
