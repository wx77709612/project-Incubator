"""Layer 2 Stage C Gate / Advisory / Runtime Result Acceptance Tests.

本文件是 Maker-driven Runtime Acceptance Test Code。
它只验证 TASK-021 至 TASK-023 已实现的 Gate、Advisory、Runtime Result 能力，
不修改 Product Runtime。
"""

from __future__ import annotations

import sys
import unittest
from types import SimpleNamespace
from typing import Any

from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


from PROJECT_INCUBATOR.runtime.components.advisory_bridge import (
    ADVISORY_RESPONSE_NO_RUNTIME_STATE_CHANGE,
    DECISION_REQUIRED,
    ITERATION_RE_ENTRY,
    MAKER_GUIDANCE_REQUEST,
    MISSING_INFORMATION,
    PHASE_ENTRY,
    RECOMMENDED_ACTION_REQUIRES_RUNTIME_REQUEST,
    RISK_DETECTED,
    VALIDATION_FEEDBACK,
    AdvisoryBridge,
    AdvisoryBridgeRequest,
    AdvisoryResponse,
)
from PROJECT_INCUBATOR.runtime.components.gate_coordinator import (
    AUTHORIZATION_PRESENT_VALID,
    AUTHORIZATION_REQUIRED_MISSING,
    GATE_ACTION_BLOCKED,
    GATE_AUTHORIZATION_REQUIRED,
    GATE_EVIDENCE_INSUFFICIENT,
    GATE_REQUIREMENT_SATISFIED,
    GATE_REQUIREMENT_UNSATISFIED,
    GateCoordinator,
    GateInvocationRequest,
)
from PROJECT_INCUBATOR.runtime.components.result_coordinator import (
    RUNTIME_RESULT_READY,
    RuntimeResultCoordinator,
    RuntimeResultInput,
)
from PROJECT_INCUBATOR.runtime.core.contracts import (
    GateEvaluationResult,
    ScriptValidationResult,
    WorkflowResultStatus,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class GateAdvisoryRuntimeResultAcceptanceTest(unittest.TestCase):
    """Stage C 验证 TASK-021 至 TASK-023 的 Gate / Advisory / Result Runtime 能力。"""

    maxDiff = None

    def _gate_coordinator(self) -> GateCoordinator:
        return GateCoordinator()

    def _advisory_bridge(self) -> AdvisoryBridge:
        return AdvisoryBridge()

    def _result_coordinator(self) -> RuntimeResultCoordinator:
        return RuntimeResultCoordinator()

    def _gate_definition_by_nature(
        self,
        coordinator: GateCoordinator,
        preferred_natures: tuple[str, ...],
    ) -> dict[str, Any]:
        for nature in preferred_natures:
            for gate in coordinator.gates_by_id.values():
                if gate["evaluation_nature"] == nature:
                    return gate
        return next(iter(coordinator.gates_by_id.values()))

    def _authorization_gate(self, coordinator: GateCoordinator) -> dict[str, Any]:
        for gate in coordinator.gates_by_id.values():
            if gate.get("required_authorization"):
                return gate
        self.fail("TEST_BLOCKED: no frozen Gate definition exposes required_authorization")

    def _sufficient_evidence_for_gate(
        self,
        gate: dict[str, Any],
        *,
        unsatisfied: bool = False,
        action_blocked: bool = False,
    ) -> tuple[dict[str, Any], ...]:
        gate_id = gate["gate_id"]
        base = {
            "gate_id": gate_id,
            "evidence_category": "DETERMINISTIC",
            "requirement_status": "UNSATISFIED" if unsatisfied else "SATISFIED",
        }
        if unsatisfied:
            base["requirement_unsatisfied"] = True
        if action_blocked:
            base["action_blocked"] = True

        nature = gate["evaluation_nature"]
        if nature == "Judgment-Based":
            return ({**base, "evidence_category": "JUDGMENT"},)
        if nature == "Mixed":
            return (
                base,
                {
                    "gate_id": gate_id,
                    "evidence_category": "JUDGMENT",
                    "judgment_evidence_present": True,
                },
            )
        return (base,)

    def _explicit_gate_result_evidence(
        self,
        gate_id: str,
        gate_result: GateEvaluationResult,
    ) -> dict[str, Any]:
        return {
            "gate_id": gate_id,
            "gate_result": gate_result.value,
            "evidence_category": "GATE_EVALUATION",
        }

    def test_l2_c01_gate_definition_resolution(self):
        """
        Test Case:
        L2-C01

        测试目标：
        Project Incubator 的 Gate Runtime 必须从冻结 Gate Definition 中识别全部 15 个 Gate。
        如果 Gate 数量、Gate ID、Required Authorization 或 Evaluation Nature 被实现层悄悄改变，
        后续 Gate Evaluation 会在错误保护边界上运行。

        真实运行场景：
        Runtime 发现某个受保护行为需要 Gate。
        ↓
        Gate Coordinator 从冻结 Definition 解析 Gate。
        ↓
        后续 Runtime 才能准备 Gate Input 并执行 Gate Evaluation。

        System Layer：
        Gate Runtime

        Runtime Flow Position：
        Gate Requirement Detected
        ↓
        [Gate Definition Resolution] ← 当前测试
        ↓
        Gate Input Preparation

        测试隔离边界：
        本测试假设 Agent 已正确解析 Maker 请求，Runtime 已进入 Gate 检查环节。
        本测试不执行完整 Runtime Coordinator，也不修改 Gate Definition。

        Semantic Input：
        从真实 GateCoordinator 加载冻结 Gate Definition Set。

        业务期望：
        Gate Coordinator 必须解析全部 15 个冻结 Gate，并保留每个 Gate 的核心定义字段。
        """
        coordinator = self._gate_coordinator()
        expected_gate_ids = {
            "GATE-GIT",
            "GATE-PHASE",
            "GATE-AUTHORITY-DOCUMENT",
            "GATE-SCOPE",
            "GATE-BUILDER",
            "GATE-UNCLOSED-TASK",
            "GATE-CONTEXT-INTEGRITY",
            "GATE-LOCAL-PROTOCOL",
            "GATE-ARTIFACT-BOUNDARY",
            "GATE-CHALLENGE-RESPONSE",
            "GATE-CORRECTION-PERSISTENCE",
            "GATE-ARCHITECTURE-DECISION",
            "GATE-FRAMEWORK-MODIFICATION",
            "GATE-PHASE-MODEL-MODIFICATION",
            "GATE-MATRIX-MODIFICATION",
        }
        self.assertEqual(15, len(coordinator.gates_by_id))
        self.assertEqual(15, coordinator.supported_gate_count)
        self.assertEqual(expected_gate_ids, set(coordinator.gates_by_id))
        for gate_id in expected_gate_ids:
            gate = coordinator.resolve_gate_definition(gate_id)
            frozen_gate = coordinator.gates_by_id[gate_id]
            self.assertEqual(gate_id, gate["gate_id"])
            self.assertIn("required_authorization", gate)
            self.assertIn("evaluation_nature", gate)
            self.assertEqual(frozen_gate["required_authorization"], gate["required_authorization"])
            self.assertEqual(frozen_gate["evaluation_nature"], gate["evaluation_nature"])
            self.assertIn(gate["evaluation_nature"], {"Evidence-Based", "Judgment-Based", "Mixed"})

    def test_l2_c02_gate_result_mapping(self):
        """
        Test Case:
        L2-C02

        测试目标：
        Gate Evaluation Result 必须被稳定映射到 Runtime State。
        如果映射错误，Runtime 可能在 Gate 未满足时继续执行，或在可以继续时错误暂停。

        真实运行场景：
        Gate Coordinator 已完成某个 Gate Evaluation。
        ↓
        Runtime 需要根据 Gate Result 决定是否继续 Contract Check、等待 Maker 或阻断行动。
        ↓
        Gate Result Mapping 形成 Runtime State / Reason。

        System Layer：
        Gate Runtime

        Runtime Flow Position：
        Gate Evaluation
        ↓
        [Gate Result Mapping] ← 当前测试
        ↓
        Runtime Result / 后续 Runtime Flow

        测试隔离边界：
        本测试直接构造 GateEvaluationResult，不测试 Evidence 收集细节。

        Semantic Input：
        REQUIREMENT_SATISFIED、REQUIREMENT_UNSATISFIED、AUTHORIZATION_REQUIRED、
        EVIDENCE_INSUFFICIENT、ACTION_BLOCKED。

        业务期望：
        Gate Result 不得被 Advisory、Script 或 Workflow Result 替代，必须按 Gate Contract 映射。
        """
        coordinator = self._gate_coordinator()
        expected = {
            GateEvaluationResult.REQUIREMENT_SATISFIED: (
                RuntimeExecutionState.EXECUTING,
                True,
                GATE_REQUIREMENT_SATISFIED,
            ),
            GateEvaluationResult.REQUIREMENT_UNSATISFIED: (
                RuntimeExecutionState.BLOCKED_BY_GATE,
                False,
                GATE_REQUIREMENT_UNSATISFIED,
            ),
            GateEvaluationResult.AUTHORIZATION_REQUIRED: (
                RuntimeExecutionState.WAITING_FOR_MAKER,
                False,
                GATE_AUTHORIZATION_REQUIRED,
            ),
            GateEvaluationResult.EVIDENCE_INSUFFICIENT: (
                RuntimeExecutionState.SUSPENDED,
                False,
                GATE_EVIDENCE_INSUFFICIENT,
            ),
            GateEvaluationResult.ACTION_BLOCKED: (
                RuntimeExecutionState.BLOCKED_BY_GATE,
                False,
                GATE_ACTION_BLOCKED,
            ),
        }
        for gate_result, expected_mapping in expected.items():
            with self.subTest(gate_result=gate_result.value):
                self.assertEqual(expected_mapping, coordinator.map_gate_result_to_runtime(gate_result))

    def test_l2_c03_maker_authorization(self):
        """
        Test Case:
        L2-C03

        测试目标：
        需要 Maker Authorization 的 Gate 不能由 Runtime、Agent 或 Script 自动补授权。
        只有 Maker 明确授权后，Gate Re-evaluation 才能继续。

        真实运行场景：
        Runtime 识别到受保护操作。
        ↓
        Gate Coordinator 判断该操作需要 Maker Authorization。
        ↓
        缺少授权时等待 Maker；收到 Maker 授权后重新评估。

        System Layer：
        Gate Runtime / Maker Authorization Boundary

        Runtime Flow Position：
        Gate Evaluation
        ↓
        [Maker Authorization Requirement] ← 当前测试
        ↓
        Gate Re-evaluation

        测试隔离边界：
        本测试直接构造 Maker Authorization Evidence，不测试自然语言理解或完整 Runtime Coordinator。

        Semantic Input：
        一个冻结定义中声明 required_authorization 的 Gate；先不提供授权，再提供 Maker 授权。

        业务期望：
        未授权时 WAITING_FOR_MAKER；Maker 授权后同一 Gate 可以重新评估为满足。
        """
        coordinator = self._gate_coordinator()
        gate = self._authorization_gate(coordinator)
        gate_id = gate["gate_id"]
        required_action = gate["required_authorization"][0]
        request = GateInvocationRequest(
            invocation_id="L2-C03",
            trigger_event="maker requests protected action",
            requested_action=required_action,
            requested_gate_ids=(gate_id,),
            evaluation_evidence=self._sufficient_evidence_for_gate(gate),
        )
        missing = coordinator.invoke(request)
        self.assertIs(missing.aggregate_gate_result, GateEvaluationResult.AUTHORIZATION_REQUIRED)
        self.assertIs(missing.runtime_state, RuntimeExecutionState.WAITING_FOR_MAKER)
        self.assertEqual(AUTHORIZATION_REQUIRED_MISSING, missing.gate_outputs[0].required_authorization_status)

        authorized = coordinator.reevaluate(
            request,
            additional_maker_authorization_evidence=(
                {
                    "authorization_id": "L2-C03-maker-authorization",
                    "gate_id": gate_id,
                    "authorizer": "MAKER",
                    "risk_object_reference": tuple(gate["risk_object"]),
                    "authorized_action_reference": required_action,
                    "authorization_scope": {
                        "gate_id": gate_id,
                        "risk_object_reference": tuple(gate["risk_object"]),
                        "authorized_action_reference": required_action,
                    },
                    "authorization_statement_reference": "Maker explicitly authorizes the protected action.",
                },
            ),
        )
        self.assertIs(authorized.aggregate_gate_result, GateEvaluationResult.REQUIREMENT_SATISFIED)
        self.assertEqual(AUTHORIZATION_PRESENT_VALID, authorized.gate_outputs[0].required_authorization_status)
        self.assertTrue(authorized.can_continue_contract_check)

    def test_l2_c04_multiple_gate_independence(self):
        """
        Test Case:
        L2-C04

        测试目标：
        当同一个 Requested Action 触发多个 Gate 时，每个 Gate 都必须独立满足。
        一个 Gate 满足不能覆盖另一个 Gate 未满足。

        真实运行场景：
        Runtime 发现一个高风险操作同时触发多个保护边界。
        ↓
        Gate Coordinator 为每个 Gate 形成独立 Gate Output。
        ↓
        只要任一 Gate 未满足，整体 Protected Action 不得继续。

        System Layer：
        Gate Runtime / Multiple Gate Coordination

        Runtime Flow Position：
        Gate Matching
        ↓
        [Multiple Gate Evaluation] ← 当前测试
        ↓
        Aggregate Gate Result

        测试隔离边界：
        本测试直接指定两个 Gate ID 和显式 Gate Evaluation Evidence，不测试 Trigger 文本匹配。

        Semantic Input：
        Gate A = REQUIREMENT_SATISFIED；Gate B = REQUIREMENT_UNSATISFIED。

        业务期望：
        Aggregate Result 必须阻断，不得因为 Gate A satisfied 而忽略 Gate B unsatisfied。
        """
        coordinator = self._gate_coordinator()
        gate_ids = tuple(coordinator.gates_by_id)[:2]
        self.assertEqual(2, len(gate_ids))
        result = coordinator.invoke(
            GateInvocationRequest(
                invocation_id="L2-C04",
                trigger_event="multi gate protected action",
                requested_action="perform protected action",
                requested_gate_ids=gate_ids,
                evaluation_evidence=(
                    self._explicit_gate_result_evidence(
                        gate_ids[0],
                        GateEvaluationResult.REQUIREMENT_SATISFIED,
                    ),
                    self._explicit_gate_result_evidence(
                        gate_ids[1],
                        GateEvaluationResult.REQUIREMENT_UNSATISFIED,
                    ),
                ),
            ),
        )
        per_gate_results = {output.gate_id: output.evaluation_result for output in result.gate_outputs}
        self.assertIs(per_gate_results[gate_ids[0]], GateEvaluationResult.REQUIREMENT_SATISFIED)
        self.assertIs(per_gate_results[gate_ids[1]], GateEvaluationResult.REQUIREMENT_UNSATISFIED)
        self.assertIs(result.aggregate_gate_result, GateEvaluationResult.REQUIREMENT_UNSATISFIED)
        self.assertIs(result.runtime_state, RuntimeExecutionState.BLOCKED_BY_GATE)
        self.assertFalse(result.can_continue_contract_check)

    def test_l2_c05_script_evidence_is_not_gate_result(self):
        """
        Test Case:
        L2-C05

        测试目标：
        Script Validation Result 只能成为 Gate 使用的 Validation Evidence，
        不能直接替代 Gate Evaluation Result。否则 Script 会越权批准 Gate。

        真实运行场景：
        Script Runtime 已收集机械 Evidence。
        ↓
        Gate Coordinator 消费 Script Evidence。
        ↓
        Gate 仍需检查 Judgment 或 Maker Authorization 等完整 Gate Requirement。

        System Layer：
        Gate Runtime / Script Evidence Boundary

        Runtime Flow Position：
        Script Evidence
        ↓
        [Gate Evidence Consumption] ← 当前测试
        ↓
        Gate Evaluation Result

        测试隔离边界：
        本测试构造 ScriptInvocationResult-like 对象，只提供 Evidence 和 Script Validation Result。
        本测试不直接执行 Script，也不执行完整 Gate Coordinator 之外的 Runtime Flow。

        Semantic Input：
        Script Validation Result = REQUIREMENT_SATISFIED，但 Gate 仍需要 Maker Authorization。

        业务期望：
        Gate Result 不能直接变成 REQUIREMENT_SATISFIED；应保持 Gate 自身 Authorization 判断。
        """
        coordinator = self._gate_coordinator()
        gate = self._authorization_gate(coordinator)
        gate_id = gate["gate_id"]
        required_action = gate["required_authorization"][0]
        script_result = SimpleNamespace(
            invocation_id="script-evidence-l2-c05",
            validation_result=ScriptValidationResult.REQUIREMENT_SATISFIED,
            evidence=(
                {
                    "gate_id": gate_id,
                    "evidence_category": "DETERMINISTIC",
                    "requirement_status": "SATISFIED",
                },
            ),
        )
        result = coordinator.invoke(
            GateInvocationRequest(
                invocation_id="L2-C05",
                trigger_event="script evidence boundary",
                requested_action=required_action,
                requested_gate_ids=(gate_id,),
                script_invocation_results=(script_result,),
            ),
        )
        self.assertIs(result.aggregate_gate_result, GateEvaluationResult.AUTHORIZATION_REQUIRED)
        self.assertIs(result.runtime_state, RuntimeExecutionState.WAITING_FOR_MAKER)
        self.assertNotEqual(GateEvaluationResult.REQUIREMENT_SATISFIED, result.aggregate_gate_result)
        self.assertEqual(
            ScriptValidationResult.REQUIREMENT_SATISFIED.value,
            result.gate_outputs[0].evidence_reference[0]["script_validation_result"],
        )

    def test_l2_c06_advisory_trigger_coverage(self):
        """
        Test Case:
        L2-C06

        测试目标：
        Advisory Bridge 必须覆盖冻结定义的 7 类 Advisory Trigger，
        让 Agent 获得可读上下文，但不把 Advisory 变成 Runtime Controller。

        真实运行场景：
        Runtime 发现当前流程需要提示、解释、风险提醒或决策协助。
        ↓
        Advisory Bridge 匹配 Trigger 并准备 Advisory Context Packet。
        ↓
        Agent 可基于 Packet 给 Maker 说明或建议。

        System Layer：
        Advisory Bridge

        Runtime Flow Position：
        Runtime Condition Observed
        ↓
        [Advisory Trigger Matching] ← 当前测试
        ↓
        Advisory Context Packet

        测试隔离边界：
        本测试直接构造 AdvisoryBridgeRequest，不测试 Agent 文案生成或 Runtime Coordinator。

        Semantic Input：
        Phase Entry、Maker Guidance Request、Missing Information、Risk Detected、
        Decision Required、Validation Feedback、Iteration Re-entry。

        业务期望：
        每个冻结 Trigger 都能被匹配并生成对应 Context Packet。
        """
        bridge = self._advisory_bridge()
        project_context = {"project": "Stage C fixture"}
        relevant_artifact = {"artifact_id": "stage-c-artifact"}
        cases = {
            PHASE_ENTRY: AdvisoryBridgeRequest(
                request_id="L2-C06-phase-entry",
                event_type=PHASE_ENTRY,
                current_phase={"phase": "P3"},
                project_context=project_context,
                relevant_artifact=relevant_artifact,
            ),
            MAKER_GUIDANCE_REQUEST: AdvisoryBridgeRequest(
                request_id="L2-C06-guidance",
                event_type=MAKER_GUIDANCE_REQUEST,
                maker_guidance_request="请解释下一步",
                project_context=project_context,
            ),
            MISSING_INFORMATION: AdvisoryBridgeRequest(
                request_id="L2-C06-missing",
                event_type=MISSING_INFORMATION,
                missing_information=("target user",),
                project_context=project_context,
            ),
            RISK_DETECTED: AdvisoryBridgeRequest(
                request_id="L2-C06-risk",
                event_type=RISK_DETECTED,
                risk={"risk": "scope drift"},
                project_context=project_context,
                relevant_artifact=relevant_artifact,
            ),
            DECISION_REQUIRED: AdvisoryBridgeRequest(
                request_id="L2-C06-decision",
                event_type=DECISION_REQUIRED,
                decision_required={"decision": "choose direction"},
                project_context=project_context,
            ),
            VALIDATION_FEEDBACK: AdvisoryBridgeRequest(
                request_id="L2-C06-validation",
                event_type=VALIDATION_FEEDBACK,
                validation_result={"result": "needs revision"},
                project_context=project_context,
                relevant_artifact=relevant_artifact,
            ),
            ITERATION_RE_ENTRY: AdvisoryBridgeRequest(
                request_id="L2-C06-iteration",
                event_type=ITERATION_RE_ENTRY,
                iteration_reentry_target="P3",
                project_context=project_context,
            ),
        }
        for trigger_id, request in cases.items():
            with self.subTest(trigger_id=trigger_id):
                result = bridge.prepare(request)
                self.assertEqual((trigger_id,), tuple(match.trigger_id for match in result.matched_triggers))
                self.assertEqual(1, len(result.advisory_context_packets))
                packet = result.advisory_context_packets[0]
                self.assertEqual(trigger_id, packet.trigger.trigger_id)
                self.assertFalse(result.runtime_state_changed)
                self.assertTrue(packet.allowed_response_fields)
                self.assertTrue(packet.available_content_types)
                self.assertEqual(request.project_context, packet.project_context)
                self.assertEqual(request.relevant_artifact, packet.relevant_artifact)
                if trigger_id == PHASE_ENTRY:
                    self.assertEqual(request.current_phase, packet.current_phase)
                if trigger_id == MISSING_INFORMATION:
                    self.assertEqual(request.missing_information, packet.missing_information)
                if trigger_id == RISK_DETECTED:
                    self.assertEqual(request.risk, packet.risk)
                if trigger_id == DECISION_REQUIRED:
                    self.assertEqual(request.decision_required, packet.decision_required)
                if trigger_id == VALIDATION_FEEDBACK:
                    self.assertEqual(request.validation_result, packet.validation_result)
                if trigger_id == ITERATION_RE_ENTRY:
                    self.assertEqual(request.iteration_reentry_target, packet.iteration_reentry_target)

    def test_l2_c07_advisory_boundary(self):
        """
        Test Case:
        L2-C07

        测试目标：
        Advisory Response 可以提出 Recommended Action，
        但不能直接修改 Runtime State、Context、Workflow、Gate 或执行 Transition。

        真实运行场景：
        Agent 根据 Advisory Context 给 Maker 提出建议。
        ↓
        Advisory Bridge 消费 Advisory Response。
        ↓
        Recommended Action 如需执行，必须转化为新的 Runtime Request。

        System Layer：
        Advisory Bridge / Runtime Boundary

        Runtime Flow Position：
        Advisory Context Packet
        ↓
        [Advisory Response Handling] ← 当前测试
        ↓
        Pending Runtime Request

        测试隔离边界：
        本测试不执行 Pending Runtime Request，只验证 Advisory 本身不改变 Runtime State。

        Semantic Input：
        Advisory Response 包含 recommended_action。

        业务期望：
        Runtime State 保持不变；Recommended Action 仅成为待处理 Runtime Request。
        """
        bridge = self._advisory_bridge()
        no_action = bridge.consume_advisory_response(
            AdvisoryResponse(
                request_id="L2-C07-no-action",
                trigger_id=MAKER_GUIDANCE_REQUEST,
                advisory_summary="仅说明当前情况",
            ),
            RuntimeExecutionState.SUSPENDED,
        )
        self.assertIs(no_action.runtime_state, RuntimeExecutionState.SUSPENDED)
        self.assertFalse(no_action.runtime_state_changed)
        self.assertEqual(ADVISORY_RESPONSE_NO_RUNTIME_STATE_CHANGE, no_action.result_reason)
        self.assertEqual((), no_action.pending_runtime_requests)

        with_action = bridge.consume_advisory_response(
            AdvisoryResponse(
                request_id="L2-C07-with-action",
                trigger_id=MAKER_GUIDANCE_REQUEST,
                recommended_action=("request-runtime-transition-review",),
            ),
            RuntimeExecutionState.WAITING_FOR_MAKER,
        )
        self.assertIs(with_action.runtime_state, RuntimeExecutionState.WAITING_FOR_MAKER)
        self.assertFalse(with_action.runtime_state_changed)
        self.assertEqual(RECOMMENDED_ACTION_REQUIRES_RUNTIME_REQUEST, with_action.result_reason)
        self.assertEqual(1, len(with_action.pending_runtime_requests))

    def test_l2_c08_runtime_result_coverage(self):
        """
        Test Case:
        L2-C08

        测试目标：
        Runtime Result Coordinator 必须能为所有 Runtime State 形成稳定结果，
        并承载 Workflow、Context、Gate、Script 等 Contract Result Reference，而不重新解释它们。

        真实运行场景：
        Runtime 完成一次执行片段。
        ↓
        Result Coordinator 汇总当前 Runtime State、Reason 和各 Component Result Reference。
        ↓
        Maker / Agent 读取稳定 Runtime Result。

        System Layer：
        Runtime Result

        Runtime Flow Position：
        Runtime Flow Component Results
        ↓
        [Runtime Result Formation] ← 当前测试
        ↓
        Runtime Result

        测试隔离边界：
        本测试直接构造 RuntimeResultInput，不执行完整 Runtime Coordinator。

        Semantic Input：
        EXECUTING、WAITING_FOR_MAKER、BLOCKED_BY_GATE、SUSPENDED、FAILED、COMPLETED。

        业务期望：
        每一种 Runtime State 均能形成合法 Runtime Result，并保留输入引用。
        """
        coordinator = self._result_coordinator()
        for runtime_state in RuntimeExecutionState:
            with self.subTest(runtime_state=runtime_state.value):
                result_input = RuntimeResultInput(
                    execution_reference=f"L2-C08-{runtime_state.value}",
                    runtime_execution_state=runtime_state,
                    runtime_reason=f"reason-{runtime_state.value}",
                    current_phase_reference={"phase": "P3"},
                    workflow_result_reference=WorkflowResultStatus.READY_FOR_TRANSITION,
                    context_access_result_reference={"context": "PROJECT_STATE"},
                    gate_output_reference={"gate_result": GateEvaluationResult.REQUIREMENT_SATISFIED.value},
                    script_output_reference={"script": "evidence"},
                    pending_requirement=("pending",),
                    required_maker_input=("maker input",),
                    completed_action_reference={"action": "completed"},
                    next_allowed_action=("continue",),
                )
                result = coordinator.form_result(result_input)
                self.assertTrue(coordinator.validate_result(result))
                self.assertEqual(result_input.execution_reference, result.execution_reference)
                self.assertIs(result.runtime_execution_state, runtime_state)
                self.assertEqual(result_input.runtime_reason, result.runtime_reason)
                self.assertEqual(result_input.current_phase_reference, result.current_phase_reference)
                self.assertEqual(result_input.workflow_result_reference, result.workflow_result_reference)
                self.assertEqual(
                    result_input.context_access_result_reference,
                    result.context_access_result_reference,
                )
                self.assertEqual(result_input.gate_output_reference, result.gate_output_reference)
                self.assertEqual(result_input.script_output_reference, result.script_output_reference)
                self.assertEqual(result_input.pending_requirement, result.pending_requirement)
                self.assertEqual(result_input.required_maker_input, result.required_maker_input)
                self.assertEqual(result_input.completed_action_reference, result.completed_action_reference)
                self.assertEqual(result_input.next_allowed_action, result.next_allowed_action)
                self.assertEqual(RUNTIME_RESULT_READY, result.result_reason)


if __name__ == "__main__":
    unittest.main()
