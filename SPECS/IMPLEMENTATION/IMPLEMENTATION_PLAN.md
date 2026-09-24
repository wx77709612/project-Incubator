# Project Incubator V1.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在保持 V1.0 Core Workflow 与 Authority 不变的前提下，实现 Capability Claim、Evidence E0–E5、P4 Creation Correction、Decision 有界历史、Known-Good Baseline、Drift 检查及按 Capability 启用的不透明能力扩展。

**Architecture:** 复用现有 Runtime Coordinator 与六个组件，通过新增纯领域类型和组件方法实现 V1.1；不新增 Phase、Transition、Gate Type 或 Runtime Execution State。高体积 Evidence 与 Correction 状态写入 Optional Context，`PROJECT_STATE.md` 只保留权威摘要和引用。

**Tech Stack:** Python 3、标准库 `dataclasses` / `enum` / `json` / `unittest`、Markdown Templates、JSON Definitions。

**Spec:** `SPECS/ARCHITECTURE/ARCHITECTURE_CHANGE_PROPOSAL.md`、`SPECS/DESIGN/EVIDENCE_MODEL_DESIGN.md`、`SPECS/EXTENSIONS/OPAQUE_CAPABILITY_EXTENSION.md`、`SPECS/RUNTIME/SKILL_RUNTIME_SPEC.md`

**Status:** IMPLEMENTED / ACCEPTANCE PASSED / RELEASE REVIEW REQUIRED

**Approved By:** Maker, 2026-09-23

**Execution Completed:** 2026-09-24

## Execution Evidence

- Task 1–10 已按 Native 路径完成，并分别登记到本地执行账本；
- 现有 `TESTS`：94 项通过；
- V1.0 Acceptance Stage A–E：40 项通过；
- V1.1 Acceptance Stage A–E：36 项通过；
- 合并直接测试矩阵：170 项通过，0 failure；
- V1.1 Stage E 另以独立进程重放现有 `TESTS` 与 V1.0 Acceptance；
- Core Phase、Transition、Gate Type、Script Purpose、Runtime Execution State 均保持原集合；
- 当前结论仅表示实施与验收完成，V1.1 发布归档仍需 Maker 最终审阅。

**Previous Baseline:** `SPECS/_V1.0/IMPLEMENTATION/IMPLEMENTATION_PLAN.md`

## Global Constraints

- 保持 P0–P6 Core Phase Set 和现有 Allowed Transition Matrix。
- 不新增 Gate Type、Script Invocation Purpose 或 Runtime Execution State。
- `PROJECT_STATE.md` 继续作为 Current Project State 唯一 Source of Truth。
- Runtime 不判断技术解释；Script 不裁决 Semantic Drift；Maker Authorization 只能来自 Maker。
- 默认重复失败阈值为 Advisory=2、Correction=3；Profile 只能配置更早触发的合法阈值。
- V1.0 Managed Project 不需要回填 Claim、Evidence 或 Baseline。
- 默认扫描、打包和 `source_document` 不得加载 `SPECS/_V*`。
- 所有行为修改先写失败测试，再写最小实现。

## Review Focus

- 同一 Failure Signature 在 Candidate Model 更新后必须开始新序列，旧 Evidence 不得丢失。
- 非 P4 Correction Request 必须暂停且不得产生 Transition 或 Context Mutation。
- Decision Archive 任一步失败时必须保留原 Active View，不能形成半归档。
- E0–E2 Claim 不得通过完整目标环境能力 Gate，E3 不得通过代表性稳定结论。
- 未启用 V1.1 的 V1.0 请求必须维持原 Result、Phase 与持久化行为。

## File Structure

| File | Responsibility |
| --- | --- |
| `PROJECT_INCUBATOR/runtime/core/evidence_types.py` | V1.1 Enum、Record 与纯验证规则 |
| `runtime/components/workflow_coordinator.py` | Correction Assessment、计数与 Activity State |
| `runtime/components/context_coordinator.py` | Optional Context、Decision Mutation 与原子归档 |
| `runtime/components/gate_coordinator.py` | Evidence Level、Scope、Baseline 与 Drift Gate Policy |
| `runtime/components/script_coordinator.py` | V1.1 Script Evidence 字段及越权拒绝 |
| `runtime/components/advisory_bridge.py` | V1.1 Reason Code 与 Context Packet |
| `runtime/core/coordinator.py` | Correction 请求编排、暂停、恢复和结果追踪 |
| `references/**/*.json` | V1.1 声明式定义，不改变既有 ID |
| `templates/**` | Claim、Evidence、Decision 和人工验证预算模板 |

## Task Dependencies

| Task | Depends On | Parallel Boundary |
| --- | --- | --- |
| 1 | 无 | 必须先完成 |
| 2 | 1 | 可与 3–6 并行 |
| 3 | 1 | 可与 2、4–6 并行 |
| 4 | 1 | 可与 2、3、5、6 并行 |
| 5 | 1 | 可与 2–4、6 并行 |
| 6 | 1 | 可与 2–5 并行 |
| 7 | 2–6 | 串联所有 Runtime 组件 |
| 8 | 1–6 | 与 7 可并行，完成后共同进入 9 |
| 9 | 7、8 | 必须串行 |
| 10 | 9 | 最终验收 |

---

### Task 1: Evidence Domain Types

**Files:**
- Create: `PROJECT_INCUBATOR/runtime/core/evidence_types.py`
- Modify: `PROJECT_INCUBATOR/runtime/core/__init__.py`
- Test: `TESTS/unit/test_evidence_types.py`

**Interfaces:**
- Produces: `EvidenceLevel`, `ClaimStatus`, `AssumptionStatus`, `BaselineStatus`, `OpacityLevel`, `CorrectionResult`, `CorrectionActivityState`, `FailureObservation`, `failure_signature()`, `validate_thresholds()`, `extension_recommended()`。

- [x] **Step 1: Write failing enum and signature tests**

```python
def test_failure_signature_ignores_hypothesized_cause():
    left = failure_signature("cap", "scene", "boundary", "missing")
    right = failure_signature("cap", "scene", "boundary", "missing")
    assert left == right

def test_relaxed_threshold_is_rejected():
    with self.assertRaises(ValueError):
        validate_thresholds(advisory=3, correction=4)

def test_two_elevated_dimensions_recommend_extension():
    assert extension_recommended([OpacityLevel.ELEVATED, OpacityLevel.ELEVATED])
```

- [x] **Step 2: Run `python TESTS/unit/test_evidence_types.py` and verify failure caused by missing module**
- [x] **Step 3: Implement frozen enums, immutable `FailureObservation`, SHA-256 signature over the four stable fields, threshold validation `1 <= advisory < correction`, `advisory <= 2`, `correction <= 3`, and Extension recommendation for any HIGH/UNKNOWN or at least two ELEVATED dimensions**
- [x] **Step 4: Run the test file and verify all tests pass**
- [x] **Step 5: Commit `feat: add evidence domain types`**

### Task 2: Workflow Correction Evaluation

**Files:**
- Modify: `PROJECT_INCUBATOR/runtime/components/workflow_coordinator.py`
- Modify: `PROJECT_INCUBATOR/references/workflow/core_workflow.json`
- Test: `TESTS/unit/test_workflow_coordinator.py`

**Interfaces:**
- Consumes: Task 1 `CorrectionResult`, `CorrectionActivityState`, `failure_signature()`。
- Produces: `CorrectionAssessmentRequest`, `CorrectionAssessmentResult`, `evaluate_correction()`。

- [x] **Step 1: Add failing tests for counts 1/2/3, invalid booleans, non-P4 rejection, model-version reset and Maker escalation**

```python
result = coordinator.evaluate_correction(request(count=3, current_phase="P4"))
self.assertEqual(CorrectionResult.P4_CORRECTION_REQUIRED, result.result)
self.assertEqual(CorrectionActivityState.CORRECTION_REVIEW, result.activity_state)
```

- [x] **Step 2: Run `python TESTS/unit/test_workflow_coordinator.py` and verify the new tests fail**
- [x] **Step 3: Implement strict request validation, nine-boolean Impact Assessment, deterministic result mapping and resume requirement validation**
- [x] **Step 4: Add P4 `correction_policy` to `core_workflow.json` without changing `core_phase_set` or `allowed_transitions`**
- [x] **Step 5: Run workflow unit tests and assert the serialized transition matrix equals its V1.0 fixture**
- [x] **Step 6: Commit `feat: add p4 correction evaluation`**

### Task 3: Context and Decision History

**Files:**
- Modify: `PROJECT_INCUBATOR/runtime/components/context_coordinator.py`
- Modify: `PROJECT_INCUBATOR/references/context/context_model.json`
- Test: `TESTS/unit/test_context_coordinator.py`

**Interfaces:**
- Produces: Optional `ContextType` values `CAPABILITY_SPIRAL_RECORD`、`PROJECT_DECISION_HISTORY`、`EVIDENCE_ARTIFACT`、`BASELINE_RECORD`，six Decision Mutation types, verified archive transaction helper。

- [x] **Step 1: Add failing tests for Optional Context targets, Assumption invalidation, supersession authorization and archive rollback**

```python
failing_store = FailingActiveViewFileStore()
coordinator = ContextCoordinator(failing_store)
result = coordinator.execute_decision_archive(active, history)
self.assertEqual(original_active, failing_store.read_file("PROJECT_DECISIONS.md"))
self.assertEqual(ContextAccessResultStatus.REJECTED, result.status)
```

- [x] **Step 2: Run context tests and verify failures**
- [x] **Step 3: Implement the four named access targets and mutation validation; keep Product/Architecture changes Maker-authorized while Assumption invalidation accepts Evidence basis**
- [x] **Step 4: Implement archive as write-history → verify stable IDs/ref → atomically update active view; restore original active content on failure**
- [x] **Step 5: Run context tests including existing V1.0 append/read cases**
- [x] **Step 6: Commit `feat: support bounded decision history and evidence contexts`**

### Task 4: Evidence-aware Gate Policy

**Files:**
- Modify: `PROJECT_INCUBATOR/runtime/components/gate_coordinator.py`
- Modify: `PROJECT_INCUBATOR/references/gates/gates.json`
- Test: `TESTS/unit/test_gate_coordinator.py`

**Interfaces:**
- Consumes: Task 1 `EvidenceLevel`。
- Produces: V1.1 reason codes while retaining existing `GateEvaluationResult`。

- [x] **Step 1: Add failing tests for level comparison, scope mismatch, E2 overclaim, E3 stability overclaim, Baseline regression, unresolved Drift, incomplete Ring Closure and missing human validation plan**

```python
output = coordinator.evaluate_gate(gate_input(current="E2", required="E3"))
self.assertEqual(GateEvaluationResult.EVIDENCE_INSUFFICIENT, output.evaluation_result)
self.assertIn("EVIDENCE_LEVEL_TOO_LOW", output.evaluation_reason)
```

- [x] **Step 2: Run gate tests and verify failure**
- [x] **Step 3: Implement policy as additional evidence checks; do not add IDs to `supported_gate_set`**
- [x] **Step 4: Run gate tests and compare the existing Gate ID set to the V1.0 expected set**
- [x] **Step 5: Commit `feat: enforce evidence claim boundaries`**

### Task 5: Script Evidence Boundary

**Files:**
- Modify: `PROJECT_INCUBATOR/runtime/components/script_coordinator.py`
- Modify: `PROJECT_INCUBATOR/scripts/validate_artifact_evidence.py`
- Test: `TESTS/unit/test_script_coordinator.py`

**Interfaces:**
- Produces: validated evidence fields, Structural Drift evidence and explicit boundary violations。

- [x] **Step 1: Add failing tests accepting Structural Drift evidence and rejecting Semantic Drift, Extension Activation, Maker Authorization and automatic level promotion**

```python
result = coordinator.consume_script_output(request, {"semantic_drift": True})
self.assertEqual(RuntimeExecutionState.SUSPENDED, result.runtime_state)
```

- [x] **Step 2: Run script tests and verify failure**
- [x] **Step 3: Implement field validation using existing Invocation Purpose values only**
- [x] **Step 4: Extend artifact validator output with evaluated scope, refs, limitations and delivery metadata**
- [x] **Step 5: Run script and existing deterministic capability tests**
- [x] **Step 6: Commit `feat: add structured runtime evidence`**

### Task 6: Advisory Reason Codes

**Files:**
- Modify: `PROJECT_INCUBATOR/runtime/components/advisory_bridge.py`
- Modify: `PROJECT_INCUBATOR/references/advisory/advisory.json`
- Test: `TESTS/unit/test_advisory_bridge.py`

**Interfaces:**
- Produces: seven approved Reason Codes through existing Trigger Types。

- [x] **Step 1: Add failing tests for repeated failure, regression, Drift, Extension recommendation, exhausted budget and Maker scope review**
- [x] **Step 2: Run advisory tests and verify failure**
- [x] **Step 3: Extend context packet with Claim/Evidence/Failure/Baseline refs and reject unknown reason codes**
- [x] **Step 4: Verify Advisory response still creates only `PendingRuntimeRequest` and never mutates Context**
- [x] **Step 5: Commit `feat: add evidence advisory reasons`**

### Task 7: Runtime Correction Orchestration

**Files:**
- Modify: `PROJECT_INCUBATOR/runtime/core/coordinator.py`
- Modify: `PROJECT_INCUBATOR/runtime/components/result_coordinator.py`
- Modify: `PROJECT_INCUBATOR/runtime/core/contracts.py`
- Test: `TESTS/unit/test_runtime_coordinator.py`
- Test: `TESTS/integration/test_runtime_execution_flow.py`

**Interfaces:**
- Consumes: Tasks 1–6 public types and component methods。
- Produces: Correction request routing, state mapping, pending Maker action and V1.1 trace fields。

- [x] **Step 1: Add failing unit tests for all five Correction Result mappings and prohibited transition execution**
- [x] **Step 2: Add failing integration tests for count 2 advisory, count 3 suspension, local correction resume and Maker scope wait/resume**
- [x] **Step 3: Run both files and verify failures**
- [x] **Step 4: Implement the V1.1 route before normal transition evaluation; preserve the existing normal request route unchanged**
- [x] **Step 5: Implement trace fields without treating them as Project State Authority**
- [x] **Step 6: Run unit and integration files and verify pass**
- [x] **Step 7: Commit `feat: orchestrate p4 correction loop`**

### Task 8: Templates and Skill Guidance

**Files:**
- Create: `PROJECT_INCUBATOR/templates/context/CAPABILITY_SPIRAL_RECORD.template.md`
- Modify: `PROJECT_INCUBATOR/templates/context/DECISION_RECORD.template.md`
- Modify: `PROJECT_INCUBATOR/templates/artifacts/IMPLEMENTATION_PLAN.template.md`
- Modify: `PROJECT_INCUBATOR/SKILL.md`
- Modify: `PROJECT_INCUBATOR/README.md`
- Test: `TESTS/unit/test_v1_1_templates.py`

**Interfaces:**
- Produces: Agent-facing Claim, Evidence, Baseline, Supersession, Validation Budget and Stop Condition guidance。

- [x] **Step 1: Write failing file-content tests for required headings and absence of mandatory Spiral Record language**
- [x] **Step 2: Run template tests and verify failure**
- [x] **Step 3: Add templates in简体中文 with stable English identifiers only for fields/enums; include Ring Closure、Compatibility Expansion、Human Validation Budget 与 Next Expansion Dimension**
- [x] **Step 4: Update Skill guidance so transparent Capability remains lightweight and P4 Correction never masquerades as P6/P2/P3**
- [x] **Step 5: Run template tests and manually inspect generated Markdown headings**
- [x] **Step 6: Commit `docs: add evidence-driven skill guidance`**

### Task 9: Definition and Backward Compatibility

**Files:**
- Modify: `PROJECT_INCUBATOR/runtime/config.json`
- Modify: `PROJECT_INCUBATOR/references/**/*.json`
- Modify: `TESTS/unit/test_definition_resolver.py`
- Modify: `TESTS/e2e/test_v1_core_workflow.py`

**Interfaces:**
- Produces: V1.1 definition version with stable definition IDs and V1.0-compatible defaults。

- [x] **Step 1: Add failing tests that all active `source_document` paths exist, exclude `_V*`, preserve IDs and reject relaxed thresholds**
- [x] **Step 2: Add a V1.0 request fixture without V1.1 fields and assert byte-equivalent phase/result semantics**
- [x] **Step 3: Run definition and E2E tests and verify failure**
- [x] **Step 4: Update definition versions and optional policies; do not require V1.1 fields on legacy routes**
- [x] **Step 5: Run the two files and the complete `TESTS` suite**
- [x] **Step 6: Commit `test: preserve v1 compatibility under v1.1 definitions`**

### Task 10: Acceptance Package

**Files:**
- Create: `ACCEPTANCE_TESTS/v1_1/stage_a/test_evidence_model_acceptance.py`
- Create: `ACCEPTANCE_TESTS/v1_1/stage_b/test_creation_correction_acceptance.py`
- Create: `ACCEPTANCE_TESTS/v1_1/stage_c/test_context_and_baseline_acceptance.py`
- Create: `ACCEPTANCE_TESTS/v1_1/stage_d/test_opaque_extension_acceptance.py`
- Create: `ACCEPTANCE_TESTS/v1_1/stage_e/test_v1_1_regression_package_acceptance.py`

**Interfaces:**
- Consumes: completed V1.1 product package。
- Produces: release-blocking acceptance evidence described in the Acceptance Test Plan。

- [x] **Step 1: Implement Stage A–E tests exactly against the acceptance IDs and expected results**
- [x] **Step 2: Run each stage independently with repository root in `PYTHONPATH`**
- [x] **Step 3: Run all existing V1.0 acceptance stages A–E**
- [x] **Step 4: Verify package isolation excludes `SPECS/_V*`, test temp files and development-only fixtures**
- [x] **Step 5: Run the full unit, integration, E2E and V1.1 acceptance suite with zero failures**
- [x] **Step 6: Commit `test: add v1.1 acceptance coverage`**

## Completion Criteria

- Tasks 1–10 individually pass their Validation Criteria；
- Existing 47 Core tests remain green；
- Existing V1.0 Acceptance Stage A–E remain green；
- V1.1 Acceptance Stage A–E pass；
- No new Phase、Transition、Gate Type、Script Purpose or Runtime State；
- No active `source_document` points to `_V*`；
- V1.0 legacy request requires no migration；
- Skill package documents and definitions agree with approved specs；
- Maker reviews final acceptance evidence before V1.1 release archive is created。
