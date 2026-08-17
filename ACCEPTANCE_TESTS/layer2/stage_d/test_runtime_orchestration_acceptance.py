"""Layer 2 Stage D Runtime Orchestration Acceptance Tests.

本文件是 Maker-driven Runtime Acceptance Test Code。
它只验证 TASK-024 已实现的 Runtime Coordinator 编排能力，不修改 Product Runtime。
"""

from __future__ import annotations

import shutil
import sys
import unittest
import uuid
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from typing import Iterator


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


ACCEPTANCE_TEMP_ROOT = (
    REPOSITORY_ROOT
    / "ACCEPTANCE_TESTS"
    / "layer2"
    / "stage_d"
    / ".tmp_runtime_orchestration_acceptance"
)


from PROJECT_INCUBATOR.runtime.components.context_coordinator import (
    AccessTarget,
    AuthorizationEvidence,
    ContextType,
    MutationIntent,
    MutationType,
    RequestSource,
)
from PROJECT_INCUBATOR.runtime.components.gate_coordinator import GATE_ACTION_BLOCKED
from PROJECT_INCUBATOR.runtime.components.script_coordinator import (
    SCRIPT_EXECUTION_ERROR,
    VALIDATION_UNSATISFIED,
    ScriptInvocationRequest,
    ScriptInvocationResult,
)
from PROJECT_INCUBATOR.runtime.components.workflow_coordinator import PhaseResult
from PROJECT_INCUBATOR.runtime.core.contracts import (
    ScriptExecutionStatus,
    ScriptValidationResult,
    WorkflowResultStatus,
)
from PROJECT_INCUBATOR.runtime.core.coordinator import (
    RUNTIME_COMPLETED,
    TRANSITION_NOT_ALLOWED,
    RuntimeCoordinator,
    RuntimeRequest,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class FixedScriptCoordinator:
    """Test fixture: RuntimeCoordinator still invokes this through its public dependency slot."""

    def __init__(self, result: ScriptInvocationResult) -> None:
        self.result = result
        self.invocations: list[ScriptInvocationRequest] = []

    def invoke(self, request: ScriptInvocationRequest) -> ScriptInvocationResult:
        self.invocations.append(request)
        return replace(
            self.result,
            invocation_id=request.invocation_id,
            script_identity=request.script_identity,
        )


class RuntimeOrchestrationAcceptanceTest(unittest.TestCase):
    """Stage D 验证 TASK-024 的完整 Runtime Coordinator 编排边界。"""

    maxDiff = None

    @contextmanager
    def _temporary_managed_project(self, current_phase: str) -> Iterator[Path]:
        temp_root = ACCEPTANCE_TEMP_ROOT.resolve()
        temp_root.mkdir(parents=True, exist_ok=True)
        project_root = (temp_root / f"run_{uuid.uuid4().hex}").resolve()
        if not str(project_root).startswith(str(temp_root)):
            raise RuntimeError("acceptance temp workspace escaped temp root")
        project_root.mkdir(mode=0o777, exist_ok=False)
        try:
            self._write_core_context(project_root, current_phase)
            yield project_root
        finally:
            shutil.rmtree(project_root, ignore_errors=True)
            try:
                temp_root.rmdir()
            except OSError:
                pass

    def _write_core_context(self, project_root: Path, current_phase: str) -> None:
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "PROJECT_PROFILE.md").write_text(
            "# Project Profile\n\nStage D temporary project\n",
            encoding="utf-8",
        )
        (project_root / "PROJECT_STATE.md").write_text(
            self._project_state_content(current_phase),
            encoding="utf-8",
        )
        (project_root / "PROJECT_PLAN.md").write_text(
            "# Project Plan\n\n- Temporary plan item\n",
            encoding="utf-8",
        )
        (project_root / "PROJECT_DECISIONS.md").write_text(
            "# Project Decisions\n\n- Decision ID: temporary\n",
            encoding="utf-8",
        )

    def _project_state_content(self, phase: str) -> str:
        return f"# Project State\n\nCurrent Phase: {phase}\nCurrent Phase State: {phase}_READY\n"

    def _phase_result(self, current_phase: str, requested_next_phase: str) -> PhaseResult:
        return PhaseResult(
            current_phase=current_phase,
            requested_next_phase=requested_next_phase,
            process_completed=True,
            required_artifact_requirement_satisfied=True,
            state_change_requirement_formed=True,
            gate_requirement_resolved=True,
            artifact_evidence=("temporary artifact evidence",),
            state_change_reference="temporary state change requirement",
            gate_resolution_reference="temporary gate resolution",
        )

    def _state_transition_intent(self, next_phase: str) -> MutationIntent:
        return MutationIntent(
            mutation_type=MutationType.UPDATE_CONTEXT,
            target_context=AccessTarget(ContextType.PROJECT_STATE),
            change_purpose=f"Persist transition to {next_phase}",
            change_basis="WORKFLOW_STATE_CHANGE_REQUIREMENT",
            proposed_content=self._project_state_content(next_phase),
            proposed_change_reference=f"transition-to-{next_phase}",
        )

    def _plan_intent(self) -> MutationIntent:
        return MutationIntent(
            mutation_type=MutationType.UPDATE_CONTEXT,
            target_context=AccessTarget(ContextType.PROJECT_PLAN),
            change_purpose="Persist execution plan update",
            change_basis="RUNTIME_CONFIRMED_EXECUTION_FACT",
            proposed_content="# Project Plan\n\n- Plan mutation executed before state commit\n",
            proposed_change_reference="plan-update-before-state",
        )

    def _profile_intent_requiring_maker(self) -> MutationIntent:
        return MutationIntent(
            mutation_type=MutationType.UPDATE_CONTEXT,
            target_context=AccessTarget(ContextType.PROJECT_PROFILE),
            change_purpose="Protected profile update",
            change_basis="MAKER_REQUESTED_CORRECTION",
            proposed_content="# Project Profile\n\nProtected mutation should wait for Maker.\n",
            proposed_change_reference="profile-protected-mutation",
            gate_evidence_reference="Authority Document Gate handled",
        )

    def _context_conflict_intent(self) -> MutationIntent:
        return MutationIntent(
            mutation_type=MutationType.UPDATE_CONTEXT,
            target_context=AccessTarget(ContextType.PROJECT_STATE),
            change_purpose="Conflicting state mutation",
            change_basis="WORKFLOW_STATE_CHANGE_REQUIREMENT",
            proposed_content=self._project_state_content("P4"),
            proposed_change_reference="conflicting-state-mutation",
            conflict_reference="Authority Context Conflict",
        )

    def _runtime(self, script_result: ScriptInvocationResult | None = None) -> RuntimeCoordinator:
        if script_result is None:
            return RuntimeCoordinator()
        return RuntimeCoordinator(script_coordinator=FixedScriptCoordinator(script_result))

    def _script_result(
        self,
        runtime_state: RuntimeExecutionState,
        result_reason: str,
        execution_status: ScriptExecutionStatus | None,
        validation_result: ScriptValidationResult | None,
    ) -> ScriptInvocationResult:
        return ScriptInvocationResult(
            invocation_id="script-fixture",
            script_identity="SCRIPT_FIXTURE",
            runtime_state=runtime_state,
            result_reason=result_reason,
            execution_status=execution_status,
            validation_result=validation_result,
            evidence=(),
            error_information={"error": result_reason} if runtime_state is RuntimeExecutionState.FAILED else None,
        )

    def _script_request(self, invocation_id: str) -> ScriptInvocationRequest:
        return ScriptInvocationRequest(
            invocation_id=invocation_id,
            script_identity="SCRIPT_FIXTURE",
            invocation_purpose="VALIDATION",
        )

    def test_l2_d01_legal_transition(self):
        """
        Test Case:
        L2-D01

        测试目标：
        验证 P3 → P4 合法 Transition 必须经过 Runtime Coordinator 的完整编排，
        并且只有 PROJECT_STATE.md 成功持久化且 Read-back Verification 后才算完成。

        真实运行场景：
        Agent 已解析 Maker 想从 P3 推进到 P4。
        ↓
        RuntimeCoordinator 读取 PROJECT_STATE，解析当前 Phase，评估 Workflow，
        执行 Context Mutation，最后验证 PROJECT_STATE 已写回目标 Phase。

        System Layer：
        Runtime Orchestration

        Runtime Flow Position：
        Runtime Request
        ↓
        [Runtime Coordinator Full Transition Flow] ← 当前测试
        ↓
        Runtime Result

        测试隔离边界：
        本测试使用 Temporary Managed Project，不测试自然语言理解，不直接调用 Workflow 或 Context
        Component 形成最终结果。

        Semantic Input：
        Current Phase = P3；Requested Transition = P3 → P4；状态变更写入 PROJECT_STATE.md。

        业务期望：
        Runtime Result = COMPLETED，PROJECT_STATE.md 磁盘内容经读回确认为 P4。
        """
        with self._temporary_managed_project("P3") as project_root:
            result = self._runtime().execute(
                RuntimeRequest(
                    request_id="L2-D01",
                    requested_action="transition P3 to P4",
                    project_root=project_root,
                    phase_result=self._phase_result("P3", "P4"),
                    context_mutation_intents=(self._state_transition_intent("P4"),),
                ),
            )
            persisted = (project_root / "PROJECT_STATE.md").read_text(encoding="utf-8")
            self.assertIs(result.runtime_execution_state, RuntimeExecutionState.COMPLETED)
            self.assertEqual(RUNTIME_COMPLETED, result.runtime_reason)
            self.assertIn("Current Phase: P4", persisted)
            project_state_persist_results = tuple(
                context_result
                for context_result in result.context_access_result_reference
                if context_result.access_target.context_type is ContextType.PROJECT_STATE
                and context_result.persisted_result is not None
                and context_result.persisted_result.path.name == "PROJECT_STATE.md"
            )
            self.assertTrue(project_state_persist_results)
            project_state_persist_result = project_state_persist_results[-1]
            self.assertEqual(
                "PROJECT_STATE.md",
                project_state_persist_result.persisted_result.path.name,
            )
            self.assertTrue(project_state_persist_result.persisted_result.verified)
            self.assertTrue(project_state_persist_result.persisted_result_verified)
            self.assertEqual("P4", result.current_phase_reference.phase_id)

    def test_l2_d02_illegal_transition(self):
        """
        Test Case:
        L2-D02

        测试目标：
        验证 P0 → P2 不属于冻结 Workflow 允许 Transition 时，
        Runtime Coordinator 不得写入新 Phase。

        真实运行场景：
        Agent 已解析一个跳阶段推进请求。
        ↓
        RuntimeCoordinator 从 PROJECT_STATE 得到 P0，并评估 P0 → P2。
        ↓
        Workflow 返回 TRANSITION_NOT_ALLOWED，Runtime 停止。

        System Layer：
        Runtime Orchestration / Workflow Boundary

        Runtime Flow Position：
        Current Phase Resolution
        ↓
        [Workflow Evaluation] ← 当前测试
        ↓
        Context Mutation Eligibility

        测试隔离边界：
        本测试直接构造结构化 RuntimeRequest，不测试 Agent Intent Understanding。

        Semantic Input：
        Current Phase = P0；Requested Transition = P0 → P2。

        业务期望：
        Runtime State = SUSPENDED；Reason = TRANSITION_NOT_ALLOWED；PROJECT_STATE.md 仍是 P0。
        """
        with self._temporary_managed_project("P0") as project_root:
            before = (project_root / "PROJECT_STATE.md").read_text(encoding="utf-8")
            result = self._runtime().execute(
                RuntimeRequest(
                    request_id="L2-D02",
                    requested_action="transition P0 to P2",
                    project_root=project_root,
                    phase_result=self._phase_result("P0", "P2"),
                    context_mutation_intents=(self._state_transition_intent("P2"),),
                ),
            )
            after = (project_root / "PROJECT_STATE.md").read_text(encoding="utf-8")
            self.assertIs(result.runtime_execution_state, RuntimeExecutionState.SUSPENDED)
            self.assertEqual(TRANSITION_NOT_ALLOWED, result.runtime_reason)
            self.assertIs(result.workflow_result_reference.status, WorkflowResultStatus.TRANSITION_NOT_ALLOWED)
            self.assertEqual(before, after)

    def test_l2_d03_missing_maker_authorization(self):
        """
        Test Case:
        L2-D03

        测试目标：
        验证需要 Maker Authorization 的 Runtime Request 在缺少 Maker 授权时必须等待 Maker，
        不得自动执行受保护 Context Mutation。

        真实运行场景：
        Maker 表达修改 PROJECT_PROFILE 的意图，但尚未给出明确授权。
        ↓
        RuntimeCoordinator 准备 Context Mutation。
        ↓
        Context Contract 要求 Maker Authorization，Runtime 返回 WAITING_FOR_MAKER。

        System Layer：
        Runtime Orchestration / Maker Authorization Boundary

        Runtime Flow Position：
        Maker Requirement
        ↓
        [Context Mutation Authorization] ← 当前测试
        ↓
        Runtime Result

        测试隔离边界：
        本测试不伪造 Maker Authorization，不直接调用 ContextCoordinator 得出最终结果。

        Semantic Input：
        PROJECT_PROFILE protected mutation；maker_authorization = None。

        业务期望：
        Runtime State = WAITING_FOR_MAKER；PROJECT_PROFILE.md 不被修改。
        """
        with self._temporary_managed_project("P3") as project_root:
            profile_path = project_root / "PROJECT_PROFILE.md"
            before = profile_path.read_text(encoding="utf-8")
            result = self._runtime().execute(
                RuntimeRequest(
                    request_id="L2-D03",
                    requested_action="protected profile update",
                    project_root=project_root,
                    context_mutation_intents=(self._profile_intent_requiring_maker(),),
                ),
            )
            after = profile_path.read_text(encoding="utf-8")
            self.assertIs(result.runtime_execution_state, RuntimeExecutionState.WAITING_FOR_MAKER)
            self.assertEqual(before, after)
            self.assertTrue(result.required_maker_input)

    def test_l2_d04_gate_block(self):
        """
        Test Case:
        L2-D04

        测试目标：
        验证 Gate Result = ACTION_BLOCKED 时，Runtime Coordinator 必须阻断受保护 Action，
        且 PROJECT_STATE 不得推进。

        真实运行场景：
        Runtime 检测到 Gate Requirement，并收到表明保护边界冲突的 Gate Evidence。
        ↓
        Gate Coordinator 返回 ACTION_BLOCKED。
        ↓
        Runtime 形成 BLOCKED_BY_GATE Result，停止 Context Mutation。

        System Layer：
        Runtime Orchestration / Gate Boundary

        Runtime Flow Position：
        Gate Evaluation
        ↓
        [Gate Block Handling] ← 当前测试
        ↓
        Context Mutation

        测试隔离边界：
        本测试通过 RuntimeRequest 提供 Gate Evidence，不直接调用 GateCoordinator 形成最终 Result。

        Semantic Input：
        Gate Evidence: action_blocked = True；Requested Transition = P3 → P4。

        业务期望：
        Runtime State = BLOCKED_BY_GATE；PROJECT_STATE.md 仍为 P3。
        """
        with self._temporary_managed_project("P3") as project_root:
            before = (project_root / "PROJECT_STATE.md").read_text(encoding="utf-8")
            result = self._runtime().execute(
                RuntimeRequest(
                    request_id="L2-D04",
                    requested_action="transition P3 to P4 with blocked gate",
                    project_root=project_root,
                    phase_result=self._phase_result("P3", "P4"),
                    context_mutation_intents=(self._state_transition_intent("P4"),),
                    requested_gate_ids=("GATE-GIT",),
                    gate_evaluation_evidence=(
                        {
                            "gate_id": "GATE-GIT",
                            "action_blocked": True,
                            "evidence_category": "DETERMINISTIC",
                        },
                    ),
                ),
            )
            after = (project_root / "PROJECT_STATE.md").read_text(encoding="utf-8")
            self.assertIs(result.runtime_execution_state, RuntimeExecutionState.BLOCKED_BY_GATE)
            self.assertEqual(GATE_ACTION_BLOCKED, result.runtime_reason)
            self.assertEqual(before, after)

    def test_l2_d05_context_conflict(self):
        """
        Test Case:
        L2-D05

        测试目标：
        验证 Context Conflict 出现时 Runtime Coordinator 必须暂停，
        且不得自动覆盖 PROJECT_STATE。

        真实运行场景：
        Runtime 收到一个与 Authority Context 冲突的状态修改请求。
        ↓
        Context Contract 返回 CONTEXT_CONFLICT。
        ↓
        Runtime 不得擅自选择覆盖策略。

        System Layer：
        Runtime Orchestration / Context Conflict Boundary

        Runtime Flow Position：
        Context Mutation Request
        ↓
        [Context Conflict Handling] ← 当前测试
        ↓
        Runtime Result

        测试隔离边界：
        本测试直接构造 conflict_reference，不测试冲突检测算法或 Agent 推理。

        Semantic Input：
        PROJECT_STATE mutation intent 带 Authority Context Conflict。

        业务期望：
        Runtime State = SUSPENDED；Reason = CONTEXT_CONFLICT；PROJECT_STATE.md 不被覆盖。
        """
        with self._temporary_managed_project("P3") as project_root:
            before = (project_root / "PROJECT_STATE.md").read_text(encoding="utf-8")
            result = self._runtime().execute(
                RuntimeRequest(
                    request_id="L2-D05",
                    requested_action="conflicting state mutation",
                    project_root=project_root,
                    context_mutation_intents=(self._context_conflict_intent(),),
                ),
            )
            after = (project_root / "PROJECT_STATE.md").read_text(encoding="utf-8")
            self.assertIs(result.runtime_execution_state, RuntimeExecutionState.SUSPENDED)
            self.assertEqual("CONTEXT_CONFLICT", result.runtime_reason)
            self.assertEqual(before, after)

    def test_l2_d06_script_validation_failure(self):
        """
        Test Case:
        L2-D06

        测试目标：
        验证 Script 正常执行但 Validation Result = REQUIREMENT_UNSATISFIED 时，
        Runtime 不得把它误判为 SCRIPT_EXECUTION_ERROR。

        真实运行场景：
        Runtime 调用确定性 Script 收集 Evidence。
        ↓
        Script 正常完成并证明 Requirement 未满足。
        ↓
        Runtime 应暂停等待后续处理，而不是视作 Script 崩溃。

        System Layer：
        Runtime Orchestration / Script Result Handling

        Runtime Flow Position：
        Script Evidence
        ↓
        [Script Result Mapping in RuntimeCoordinator] ← 当前测试
        ↓
        Runtime Result

        测试隔离边界：
        本测试通过 RuntimeCoordinator 公开依赖入口注入临时 ScriptCoordinator fixture，
        不直接调用 Product Script 形成最终 Result。

        Semantic Input：
        Execution Status = COMPLETED；Validation Result = REQUIREMENT_UNSATISFIED。

        业务期望：
        Runtime State = SUSPENDED；Reason = VALIDATION_UNSATISFIED；不是 SCRIPT_EXECUTION_ERROR。
        """
        with self._temporary_managed_project("P3") as project_root:
            result = self._runtime(
                self._script_result(
                    RuntimeExecutionState.SUSPENDED,
                    VALIDATION_UNSATISFIED,
                    ScriptExecutionStatus.COMPLETED,
                    ScriptValidationResult.REQUIREMENT_UNSATISFIED,
                ),
            ).execute(
                RuntimeRequest(
                    request_id="L2-D06",
                    requested_action="script validation failure",
                    project_root=project_root,
                    script_invocation_requests=(self._script_request("L2-D06-script"),),
                ),
            )
            self.assertIs(result.runtime_execution_state, RuntimeExecutionState.SUSPENDED)
            self.assertEqual(VALIDATION_UNSATISFIED, result.runtime_reason)
            self.assertNotEqual(SCRIPT_EXECUTION_ERROR, result.runtime_reason)

    def test_l2_d07_script_execution_error(self):
        """
        Test Case:
        L2-D07

        测试目标：
        验证 Script EXECUTION_ERROR 必须映射为 Runtime FAILED + SCRIPT_EXECUTION_ERROR，
        不得被当成 Validation Failure。

        真实运行场景：
        Runtime 调用 Script，但 Script 执行失败。
        ↓
        Runtime Coordinator 接收 Script Runtime Result。
        ↓
        Runtime 进入 FAILED，并保留 Script Execution Error Reason。

        System Layer：
        Runtime Orchestration / Script Failure Handling

        Runtime Flow Position：
        Script Invocation
        ↓
        [Script Execution Error Handling] ← 当前测试
        ↓
        Runtime Result

        测试隔离边界：
        本测试通过 RuntimeCoordinator 公开依赖入口注入临时 ScriptCoordinator fixture。

        Semantic Input：
        Script Runtime State = FAILED；Reason = SCRIPT_EXECUTION_ERROR。

        业务期望：
        Runtime State = FAILED；Reason = SCRIPT_EXECUTION_ERROR；不是 VALIDATION_UNSATISFIED。
        """
        with self._temporary_managed_project("P3") as project_root:
            result = self._runtime(
                self._script_result(
                    RuntimeExecutionState.FAILED,
                    SCRIPT_EXECUTION_ERROR,
                    ScriptExecutionStatus.EXECUTION_ERROR,
                    ScriptValidationResult.VALIDATION_NOT_COMPLETED,
                ),
            ).execute(
                RuntimeRequest(
                    request_id="L2-D07",
                    requested_action="script execution error",
                    project_root=project_root,
                    script_invocation_requests=(self._script_request("L2-D07-script"),),
                ),
            )
            self.assertIs(result.runtime_execution_state, RuntimeExecutionState.FAILED)
            self.assertEqual(SCRIPT_EXECUTION_ERROR, result.runtime_reason)
            self.assertNotEqual(VALIDATION_UNSATISFIED, result.runtime_reason)

    def test_l2_d08_p6_iteration_matrix(self):
        """
        Test Case:
        L2-D08

        测试目标：
        验证 P6 iteration matrix 只允许回到 P2/P3/P4/P5，
        不允许 P6 → P0、P6 → P1 或 P6 → P6。

        真实运行场景：
        Project 已在 P6，Maker 希望进入下一轮迭代。
        ↓
        Agent 已解析目标 Phase。
        ↓
        RuntimeCoordinator 通过 Workflow 规则判断目标是否合法。

        System Layer：
        Runtime Orchestration / Workflow Iteration Matrix

        Runtime Flow Position：
        Current Phase Resolution
        ↓
        [P6 Transition Eligibility] ← 当前测试
        ↓
        Runtime Result

        测试隔离边界：
        本测试逐个构造 RuntimeRequest，不测试 Agent 如何选择目标 Phase。

        Semantic Input：
        Current Phase = P6；合法目标 P2/P3/P4/P5；非法目标 P0/P1/P6。

        业务期望：
        合法目标进入正常 Transition Eligibility 并完成；非法目标拒绝且 PROJECT_STATE 不改变。
        """
        legal_targets = ("P2", "P3", "P4", "P5")
        illegal_targets = ("P0", "P1", "P6")

        for target in legal_targets:
            with self.subTest(target=target):
                with self._temporary_managed_project("P6") as project_root:
                    result = self._runtime().execute(
                        RuntimeRequest(
                            request_id=f"L2-D08-legal-{target}",
                            requested_action=f"iterate P6 to {target}",
                            project_root=project_root,
                            phase_result=self._phase_result("P6", target),
                            context_mutation_intents=(self._state_transition_intent(target),),
                        ),
                    )
                    persisted = (project_root / "PROJECT_STATE.md").read_text(encoding="utf-8")
                    self.assertIs(result.workflow_result_reference.status, WorkflowResultStatus.READY_FOR_TRANSITION)
                    self.assertIs(result.runtime_execution_state, RuntimeExecutionState.COMPLETED)
                    self.assertIn(f"Current Phase: {target}", persisted)

        for target in illegal_targets:
            with self.subTest(target=target):
                with self._temporary_managed_project("P6") as project_root:
                    before = (project_root / "PROJECT_STATE.md").read_text(encoding="utf-8")
                    result = self._runtime().execute(
                        RuntimeRequest(
                            request_id=f"L2-D08-illegal-{target}",
                            requested_action=f"iterate P6 to {target}",
                            project_root=project_root,
                            phase_result=self._phase_result("P6", target),
                            context_mutation_intents=(self._state_transition_intent(target),),
                        ),
                    )
                    after = (project_root / "PROJECT_STATE.md").read_text(encoding="utf-8")
                    self.assertIs(
                        result.workflow_result_reference.status,
                        WorkflowResultStatus.TRANSITION_NOT_ALLOWED,
                    )
                    self.assertIs(result.runtime_execution_state, RuntimeExecutionState.SUSPENDED)
                    self.assertEqual(before, after)

    def test_l2_d09_project_state_commit_last(self):
        """
        Test Case:
        L2-D09

        测试目标：
        验证实际 Context Mutation Transition 中 PROJECT_STATE Mutation 必须最后执行，
        并且只有 Persist + Read-back Verification 成功后 Transition 才完成。

        真实运行场景：
        Runtime 同时需要更新普通 Context 与 PROJECT_STATE。
        ↓
        RuntimeCoordinator 必须先处理其他 Context Mutation，最后 Commit PROJECT_STATE。
        ↓
        读回 PROJECT_STATE 确认目标 Phase 后才形成完成结果。

        System Layer：
        Runtime Orchestration / PROJECT_STATE Commit Boundary

        Runtime Flow Position：
        Context Mutation
        ↓
        [PROJECT_STATE Commit Last] ← 当前测试
        ↓
        Persisted State Verification

        测试隔离边界：
        本测试使用 Temporary Managed Project。当前 RuntimeCoordinator 公开接口不暴露安全的
        persistence failure 注入点，因此 D09 Persistence Failure sub-case = TEST_BLOCKED。

        Semantic Input：
        PROJECT_PLAN mutation + PROJECT_STATE transition mutation。

        业务期望：
        completed_action_reference 中 PROJECT_STATE write 位于最后；PROJECT_STATE read-back 为 P4；
        无法通过公开接口安全构造 Persistence Failure 时不新增 Product Interface。
        """
        with self._temporary_managed_project("P3") as project_root:
            result = self._runtime().execute(
                RuntimeRequest(
                    request_id="L2-D09",
                    requested_action="transition P3 to P4 with plan update first",
                    project_root=project_root,
                    phase_result=self._phase_result("P3", "P4"),
                    context_mutation_intents=(
                        self._state_transition_intent("P4"),
                        self._plan_intent(),
                    ),
                ),
            )
            persisted_state = (project_root / "PROJECT_STATE.md").read_text(encoding="utf-8")
            persisted_plan = (project_root / "PROJECT_PLAN.md").read_text(encoding="utf-8")
            completed_writes = result.completed_action_reference
            self.assertIs(result.runtime_execution_state, RuntimeExecutionState.COMPLETED)
            self.assertIn("Plan mutation executed before state commit", persisted_plan)
            self.assertIn("Current Phase: P4", persisted_state)
            self.assertIsNotNone(completed_writes)
            write_names = tuple(write.path.name for write in completed_writes)
            self.assertIn("PROJECT_PLAN.md", write_names)
            self.assertIn("PROJECT_STATE.md", write_names)
            plan_write_index = write_names.index("PROJECT_PLAN.md")
            state_write_index = write_names.index("PROJECT_STATE.md")
            plan_write = completed_writes[plan_write_index]
            state_write = completed_writes[state_write_index]
            self.assertTrue(plan_write.verified)
            self.assertTrue(state_write.verified)
            self.assertLess(plan_write_index, state_write_index)
            self.assertEqual(len(completed_writes) - 1, state_write_index)
            self.assertEqual("PROJECT_STATE.md", completed_writes[-1].path.name)


if __name__ == "__main__":
    unittest.main()
