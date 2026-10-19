> 作用域（2026-10-19）：本文保留 V1.x Legacy 兼容设计/回归语义，不定义 Plugin 0.3.x 的状态权威、入口或执行机制。现行 Kernel 规则由 [Kernel Alignment ACP](../ARCHITECTURE/KERNEL_ALIGNMENT_CHANGE_PROPOSAL.md) 及其 Design、Contract、Runtime 和两份 Plan 约束；冲突条款已被 Decision 015 明确替代。非冲突的 Maker Authority、Evidence 和领域方法可作为参考。

# Context Mutation Orchestration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** IMPLEMENTED / AUTOMATED ACCEPTANCE PASSED / MANUAL ROUND 2R PENDING

**Goal:** 阻止未经验证的 Maker Authorization 和部分完成的多 Context Mutation 被报告为成功，并使 Opaque Extension Activation 在失败时可整体回滚。

**Architecture:** 保留现有单 Context Mutation 路径；新增由 `ContextMutationSet` 显式触发的受保护路径。Definition Resolver 提供 Event Recipe，Context Coordinator 执行授权绑定、Preflight、Snapshot、按序 Commit、两段 Closure 和 Rollback，Runtime Coordinator 负责路由并映射到既有 Runtime Execution State。

**Tech Stack:** Python 3 标准库、冻结 dataclass / Enum、JSON Definitions、unittest、Markdown Templates、现有 RC Build / Install 工具。

**Spec:** `SPECS/ARCHITECTURE/CONTEXT_MUTATION_ORCHESTRATION_CHANGE_PROPOSAL.md`、`SPECS/DESIGN/CONTEXT_MUTATION_ORCHESTRATION_DESIGN.md`、`SPECS/CONTRACTS/CONTEXT_MUTATION_ORCHESTRATION_CONTRACT.md`、`SPECS/RUNTIME/CONTEXT_MUTATION_ORCHESTRATION_RUNTIME_SPEC.md`

## Global Constraints

- 不新增 Core Phase、Transition、Gate Type 或 `RuntimeExecutionState`。
- `PROJECT_STATE.md` 继续是 Current Project State 唯一 Source of Truth，并在多 Context Commit 中最后写入。
- Maker Authorization 必须绑定既有 Pending Request、Maker Message Ref、Statement Excerpt、Scope 与 Context Targets。
- `source=MAKER` 与 `confirmed=true` 不能单独激活 Opaque Extension。
- Runtime 只验证结构化授权与 Closure，不裁决技术解释或自然语言产品语义。
- 单文件、无受保护 Authority 且无跨 Context 后置条件的旧请求保持原行为。
- 任何 Commit、Authorization Finalization 或 Closure 失败都不得留下部分激活。
- 当前 `ProjectSimulator` 不重建；重新安装 RC 后从 Round 2C Pending 状态重放。
- 修复后的候选包版本固定为 `1.1.0-rc.2`，Skill Identity 继续为 `project-incubator-v1-1-rc` 且保持 explicit-only。

## Review Focus

- Maker 明确说“请提出授权请求”时，不能被解析为已经授权；由 Task 2 和 Task 7 覆盖。
- 同一个 Authorization Request 被另一个 Capability 或更大 Scope 复用时必须拒绝；由 Task 2 和 Task 5 覆盖。
- 新建 Optional Context 后续 Commit 失败时必须删除新文件，而不是留下孤立 Spiral Record；由 Task 3 和 Task 4 覆盖。
- Runtime 在 `PROJECT_STATE` 写入后崩溃时必须能够根据 Execution Record 完成 Final Closure 或整体恢复；由 Task 4 和 Task 5 覆盖。
- 不含 Mutation Set 的 V1.0/V1.1 请求必须保持 195 项既有行为；由 Task 8 覆盖。

---

## File Structure

| File | Responsibility |
| --- | --- |
| `PROJECT_INCUBATOR/runtime/core/mutation_orchestration_types.py` | Mutation Set、Authorization Request、Closure、Result 的冻结类型与纯校验 |
| `PROJECT_INCUBATOR/references/context/context_model.json` | Multi-Context Event Recipe 和 Source Document 引用 |
| `PROJECT_INCUBATOR/runtime/components/definition_resolver.py` | 加载并验证 Event Recipe 的唯一性与合法性 |
| `PROJECT_INCUBATOR/runtime/adapters/file_store.py` | Snapshot、Restore 与新文件回滚删除 |
| `PROJECT_INCUBATOR/runtime/components/context_coordinator.py` | 严格授权校验、Mutation Set 执行、Closure、Rollback |
| `PROJECT_INCUBATOR/runtime/core/coordinator.py` | Mutation Set Runtime 路由和既有状态映射 |
| `PROJECT_INCUBATOR/runtime/components/result_coordinator.py` | 暴露 Orchestration Result 引用，不改变 Runtime State Set |
| `PROJECT_INCUBATOR/SKILL.md` | Agent 多 Context 识别、授权请求和完成报告规则 |
| `PROJECT_INCUBATOR/templates/context/*.template.md` | Extension Status、Request Ref 与 Closure Ref 的条件字段 |
| `TESTS/`、`ACCEPTANCE_TESTS/` | Unit、Integration、Acceptance、Regression 与人工重放协议 |

### Task 1: Domain Types and Event Recipes

**Files:**
- Create: `PROJECT_INCUBATOR/runtime/core/mutation_orchestration_types.py`
- Modify: `PROJECT_INCUBATOR/references/context/context_model.json`
- Modify: `PROJECT_INCUBATOR/runtime/components/definition_resolver.py`
- Create: `TESTS/unit/test_mutation_orchestration_types.py`
- Modify: `TESTS/unit/test_definition_resolver.py`

**Interfaces:**
- Produces: `AuthorityRequirement`、`ExtensionStatus`、`MutationSetStatus`、`ClosureOperator`、`OrchestrationFailureCode`。
- Produces: `AuthorizationRequestRecord`、`AuthorizationProvenance`、`MutationTargetSpec`、`ClosureAssertion`、`ContextMutationSet`、`MutationOrchestrationResult`。Core 类型中的 `context_type` 使用稳定字符串，Context Coordinator 在边界处转换为 `ContextType`，避免 Core 反向依赖 Component。
- Produces: `DefinitionResolver.context_event_recipe(event_type: str) -> dict[str, Any]`。

- [ ] **Step 1: Write failing tests for frozen enum values, duplicate targets, PROJECT_STATE-last ordering, idempotency key and unknown recipe rejection**

```python
mutation_set = ContextMutationSet(
    mutation_set_id="ms-1",
    event_type="OPAQUE_EXTENSION_ACTIVATED",
    event_ref="capability:C-1",
    current_phase="P2",
    requested_by="AGENT",
    authority_requirement=AuthorityRequirement.MAKER,
    targets=(spiral_target, plan_target, state_target),
    closure_assertions=(status_assertion,),
)
self.assertEqual(ContextType.PROJECT_STATE, mutation_set.ordered_targets[-1].context_type)
```

- [ ] **Step 2: Run the two test files and verify failures are caused by missing types and recipes**
- [ ] **Step 3: Implement immutable types and pure structural validation; do not perform file I/O or semantic authorization inference**
- [ ] **Step 4: Add JSON recipes for `OPAQUE_EXTENSION_RECOMMENDED`、`OPAQUE_EXTENSION_AUTHORIZATION_REQUESTED`、`OPAQUE_EXTENSION_ACTIVATED`、`OPAQUE_EXTENSION_DECLINED`、`OPAQUE_EXTENSION_SUSPENDED` and register the three approved source documents**
- [ ] **Step 5: Validate recipes require unique targets, legal operators, valid authority values and PROJECT_STATE-last ordering**
- [ ] **Step 6: Run tests and commit `feat: add mutation orchestration domain types`**

### Task 2: Authorization Provenance Validation

**Files:**
- Modify: `PROJECT_INCUBATOR/runtime/components/context_coordinator.py`
- Modify: `PROJECT_INCUBATOR/runtime/core/mutation_orchestration_types.py`
- Modify: `TESTS/unit/test_context_coordinator.py`
- Modify: `TESTS/unit/test_mutation_orchestration_types.py`

**Interfaces:**
- Consumes: Task 1 `AuthorizationRequestRecord` and `AuthorizationProvenance`。
- Produces: `ContextCoordinator.validate_authorization(request, evidence, mutation_set) -> OrchestrationFailureCode | None`。
- Compatibility: existing `AuthorizationEvidence(source, confirmed, reference)` remains valid only for legacy single-context paths that do not activate Extension。

- [ ] **Step 1: Add the Round 2 failure fixture showing `source=MAKER, confirmed=True` without a Pending Request is rejected**

```python
failure = coordinator.validate_authorization(
    pending_request=None,
    evidence=legacy_boolean_authorization,
    mutation_set=activation_set,
)
self.assertIs(OrchestrationFailureCode.AUTHORIZATION_REQUIRED, failure)
```

- [ ] **Step 2: Add failing tests for wrong Request ID, Agent Message Ref, empty excerpt, digest mismatch, Capability mismatch, Scope mismatch, Target mismatch, expired request and cross-event reuse**
- [ ] **Step 3: Add passing tests for one exact Maker response bound to one PENDING Request with equal or narrower Mutation Scope**
- [ ] **Step 4: Implement SHA-256 statement digest normalization and strict reference / scope validation without changing legacy `_has_maker_authorization()` behavior outside Mutation Set routing**
- [ ] **Step 5: Run context and orchestration type tests and commit `feat: bind maker authorization to pending requests`**

### Task 3: Reversible File Persistence

**Files:**
- Modify: `PROJECT_INCUBATOR/runtime/adapters/file_store.py`
- Create: `TESTS/unit/test_file_store.py`

**Interfaces:**
- Produces: `FileSnapshot(path, existed, content, digest)`。
- Produces: `FileStore.snapshot(path) -> FileSnapshot`。
- Produces: `FileStore.restore(snapshot) -> FileWriteResult | None`，其中原文件不存在时删除本次新建文件并验证缺失。

- [ ] **Step 1: Write failing tests for restoring an existing file, removing a newly created file, digest mismatch and injected restore failure**
- [ ] **Step 2: Run the file store tests and verify failures**
- [ ] **Step 3: Implement snapshot and restore using the existing resolved-path and atomic-write boundaries; expose no unrestricted delete API**
- [ ] **Step 4: Verify restore always performs read-back or absence verification**
- [ ] **Step 5: Run tests and commit `feat: add reversible context persistence`**

### Task 4: Context Mutation Set Transaction

**Files:**
- Modify: `PROJECT_INCUBATOR/runtime/components/context_coordinator.py`
- Modify: `PROJECT_INCUBATOR/runtime/core/mutation_orchestration_types.py`
- Modify: `TESTS/unit/test_context_coordinator.py`

**Interfaces:**
- Consumes: Task 1 recipes/types、Task 2 authorization validation、Task 3 snapshots。
- Produces: `ContextCoordinator.execute_mutation_set(mutation_set, recipe) -> MutationOrchestrationResult`。
- Produces: deterministic `ClosureAssertion` evaluation for `EQUALS`、`EXISTS`、`ABSENT`、`COVERS`、`UNCHANGED`。

- [ ] **Step 1: Add failing tests proving all targets preflight before any write and PROJECT_STATE commits last**
- [ ] **Step 2: Add failing tests for PLAN commit failure, STATE commit failure, Closure mismatch, Authorization Finalization failure, rollback success and rollback failure**
- [ ] **Step 3: Add a failing test where a newly created Spiral Record is removed after later failure**
- [ ] **Step 4: Implement Prepare → Snapshot → Stage Validation → ordered Commit → Context Closure → Authorization Finalization → Final Closure**
- [ ] **Step 5: Implement reverse-order restore and distinct `ROLLED_BACK` / `FAILED` results; never return `VERIFIED` after rollback**
- [ ] **Step 6: Implement idempotency behavior for verified, pending, retry and payload-conflict attempts**
- [ ] **Step 7: Run context tests and commit `feat: execute atomic multi-context mutation sets`**

### Task 5: Runtime Routing and Result Traceability

**Files:**
- Modify: `PROJECT_INCUBATOR/runtime/core/coordinator.py`
- Modify: `PROJECT_INCUBATOR/runtime/components/result_coordinator.py`
- Modify: `TESTS/unit/test_runtime_coordinator.py`
- Modify: `TESTS/unit/test_contracts.py`

**Interfaces:**
- Adds: `RuntimeRequest.context_mutation_set: ContextMutationSet | None`。
- Adds: `RuntimeExecutionTrace.mutation_orchestration_result` and `RuntimeResult.mutation_orchestration_result_reference`。
- Maps: `AUTHORIZATION_PENDING → WAITING_FOR_MAKER`、`VERIFIED → COMPLETED`、`REJECTED/ROLLED_BACK/SUSPENDED → SUSPENDED`、`FAILED → FAILED`。

- [ ] **Step 1: Write failing routing tests for every Orchestration Result mapping and confirm the Runtime State enum is unchanged**
- [ ] **Step 2: Add failing tests proving Mutation Set routing bypasses legacy per-file execution and never invokes Workflow Transition**
- [ ] **Step 3: Add recovery tests for `AUTHORIZATION_PENDING`、`COMMITTING` and `FINALIZING_AUTHORIZATION` attempts**
- [ ] **Step 4: Implement the route before legacy mutation preparation; reject a request that supplies both Mutation Set and independent intents for the same targets**
- [ ] **Step 5: Include Mutation Set ID、Attempt ID、Authorization Refs、Closure and Rollback Result in Runtime Result traceability**
- [ ] **Step 6: Run runtime and contract tests and commit `feat: route multi-context mutation orchestration`**

### Task 6: Skill Guidance and Conditional Templates

**Files:**
- Modify: `PROJECT_INCUBATOR/SKILL.md`
- Modify: `PROJECT_INCUBATOR/templates/context/PROJECT_STATE.template.md`
- Modify: `PROJECT_INCUBATOR/templates/context/PROJECT_PLAN.template.md`
- Modify: `PROJECT_INCUBATOR/templates/context/CAPABILITY_SPIRAL_RECORD.template.md`
- Modify: `PROJECT_INCUBATOR/templates/integrations/codex/AGENTS.template.md`
- Modify: `TESTS/unit/test_v1_1_templates.py`

**Interfaces:**
- Produces: Agent rule for detecting Multi-Context Trigger before writing files。
- Produces: conditional fields `Extension Status`、`Authorization Request Ref`、`Authorization Evidence Ref`、`Mutation Set Ref`、`Closure Result Ref`。

- [ ] **Step 1: Add failing behavior/content tests for Pending versus Active wording, exact Maker excerpt requirement, target list and completion report**
- [ ] **Step 2: Add guidance that an Agent first forms a Mutation Set summary and cannot infer Authorization from “评估”“提出请求”“继续” or risk acknowledgement**
- [ ] **Step 3: Add conditional template sections; state clearly that transparent capabilities and unrelated projects omit them**
- [ ] **Step 4: Require completion reports to name Event、Authorization Basis or Pending Status、Changed Targets、Closure Result and unchanged Phase**
- [ ] **Step 5: Run template tests and commit `docs: guide multi-context closure behavior`**

### Task 7: Integration and V1.1 Acceptance Tests

**Files:**
- Create: `TESTS/integration/test_mutation_orchestration_flow.py`
- Create: `ACCEPTANCE_TESTS/v1_1/stage_f/test_context_mutation_orchestration_acceptance.py`
- Modify: `ACCEPTANCE_TESTS/v1_1/stage_e/test_v1_1_regression_package_acceptance.py`
- Modify: `ACCEPTANCE_TESTS/manual/v1_1_rc/README.md`
- Modify: `ACCEPTANCE_TESTS/manual/v1_1_rc/AGENT_PROMPTS.md`
- Modify: `ACCEPTANCE_TESTS/manual/v1_1_rc/MAKER_ANSWER_KEY.md`

**Interfaces:**
- Consumes: Tasks 1–6 public API。
- Produces: automated replay of Round 2 failure and Round 2C Pending state。
- Produces: manual `Round 2R` between correction and the original Round 3。

- [ ] **Step 1: Write the Round 2 fixture and prove it remains Pending with zero file writes beyond the authorized Pending recipe**
- [ ] **Step 2: Write a valid Maker Authorization fixture and prove State、Plan、Spiral jointly become Active while Phase remains P2 and budget remains 0/4**
- [ ] **Step 3: Inject each commit/closure failure and verify no partial activation remains**
- [ ] **Step 4: Add manual Round 2R Prompt, Maker answer, PASS/FAIL signals and evidence-record template**
- [ ] **Step 5: Run Integration and Stage F independently and commit `test: cover mutation orchestration acceptance`**

### Task 8: Full Regression, RC Rebuild and Installed Verification

**Files:**
- Modify: `PROJECT_INCUBATOR/runtime/config.json`
- Verify only: `TOOLS/build_rc_skill.py`
- Verify only: `TOOLS/install_rc_skill.py`
- Modify: `SPECS/README.md`
- Modify: `SPECS/IMPLEMENTATION/CONTEXT_MUTATION_ORCHESTRATION_IMPLEMENTATION_PLAN.md`
- Modify: `SPECS/IMPLEMENTATION/CONTEXT_MUTATION_ORCHESTRATION_ACCEPTANCE_TEST_PLAN.md`
- Test: `TESTS/unit/test_rc_skill_builder.py`
- Test: `TESTS/integration/test_rc_skill_installer.py`
- Test: all existing Unit / Integration / E2E / Acceptance suites

**Interfaces:**
- Produces: self-contained RC package containing Mutation Orchestration implementation and guidance。
- Preserves: global stable V1.0 package digest and explicit-only RC identity。

- [ ] **Step 1: Run all repository tests, V1.0 acceptance, V1.1 A–F acceptance and Layer 2 acceptance; record exact totals**
- [ ] **Step 2: Set Package Version to `1.1.0-rc.2`, build the RC distribution and verify manifest, unique top-level `SKILL.md`, nested Runtime import and source isolation**
- [ ] **Step 3: Install the RC in parallel without modifying global V1.0; verify installed digest and nine installed checks**
- [ ] **Step 4: Run installed-package smoke tests from an unrelated directory with repository paths removed from `PYTHONPATH`**
- [ ] **Step 5: Update plan status and evidence only from actual outputs; do not mark manual acceptance complete**
- [ ] **Step 6: Commit `build: refresh v1.1 rc with mutation closure`**

## Plan Acceptance Criteria

- Tasks 1–8 each complete their stated tests and commits；
- automated acceptance blocks the exact Round 2 fabricated-authorization behavior；
- valid bounded Maker Authorization reaches `VERIFIED` without Phase or budget drift；
- rollback tests prove no partial State / Plan / Spiral activation；
- legacy single-context requests and the previous 195-test baseline remain compatible；
- rebuilt Installed RC is self-contained and V1.0 remains unchanged；
- manual Round 2R is ready for Maker execution before original Round 3 resumes。

## Execution Evidence

执行日期：2026-09-25。

- Tasks 1–8 均已按 TDD 与任务级验证完成；实现与审查修复提交范围为 `ce2e809` 至 `303be90`。
- 仓库测试：167 / 167 通过，其中 Unit 132、Integration 32、E2E 3。
- V1.1 Stage A–F：39 / 39 通过，其中 A=6、B=8、C=7、D=8、E=8、F=2。
- Layer 2：40 / 40 通过，其中 A=15、B=5、C=8、D=9、E=3。
- 合计执行 246 项自动化检查，0 失败；Stage E 内部回归重放不作为额外能力结论。
- RC Package Version：`1.1.0-rc.2`；Build Identity：`bb51b0fa19f62a0000ba24e3a88ccfee4c55af5b76c67a1a400c9760ed7e6e19`。
- 构建包九项验证与安装后九项验证均通过；安装前后 Stable V1.0 Digest 均为 `c01fe91e476e52b3f590e37b04f6bbd1208eeec3eded30a771f0bdaac6b41cf5`。
- 从仓库外临时目录导入 Installed Runtime 成功，Definition Resolution=`COMPLETED`，仓库路径未出现在 `sys.path`。
- 整分支审查修复了持久 Execution Record、跨 Runtime 恢复、Recipe Closure 防弱化、授权 Scope/Targets 防扩张、状态转换前置条件、Phase 前置条件与混合路由静默忽略问题；相关测试均先失败后通过。
- Manual Round 2R 尚未执行，因此本计划不声明人工验收完成，也不解除 Round 3 的人工流程暂停。
