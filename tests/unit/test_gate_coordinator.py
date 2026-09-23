import unittest

from PROJECT_INCUBATOR.runtime.components.gate_coordinator import (
    GateCoordinator,
    GateInput,
    GateInvocationReference,
    GateInvocationRequest,
)
from PROJECT_INCUBATOR.runtime.core.contracts import GateEvaluationResult
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class GateCoordinatorTest(unittest.TestCase):
    def setUp(self):
        self.coordinator = GateCoordinator()

    def test_gate_block_maps_to_blocked_by_gate(self):
        result = self.coordinator.invoke(
            GateInvocationRequest(
                invocation_id="gate-block",
                trigger_event="commit",
                requested_action="commit",
                requested_gate_ids=("GATE-GIT",),
                evaluation_evidence=(
                    {
                        "gate_id": "GATE-GIT",
                        "gate_result": "REQUIREMENT_UNSATISFIED",
                    },
                ),
            ),
        )

        self.assertIs(
            result.aggregate_gate_result,
            GateEvaluationResult.REQUIREMENT_UNSATISFIED,
        )
        self.assertIs(result.runtime_state, RuntimeExecutionState.BLOCKED_BY_GATE)
        self.assertFalse(result.can_continue_contract_check)

    def test_maker_authorization_is_not_auto_supplied(self):
        result = self.coordinator.invoke(
            GateInvocationRequest(
                invocation_id="auth-missing",
                trigger_event="push",
                requested_action="push",
                requested_gate_ids=("GATE-GIT",),
                evaluation_evidence=(
                    {
                        "gate_id": "GATE-GIT",
                        "gate_result": "REQUIREMENT_SATISFIED",
                    },
                ),
            ),
        )

        self.assertIs(
            result.aggregate_gate_result,
            GateEvaluationResult.AUTHORIZATION_REQUIRED,
        )
        self.assertIs(result.runtime_state, RuntimeExecutionState.WAITING_FOR_MAKER)

    def test_script_validation_evidence_does_not_replace_gate_result(self):
        result = self.coordinator.invoke(
            GateInvocationRequest(
                invocation_id="judgment-gate",
                trigger_event="scope change",
                requested_gate_ids=("GATE-SCOPE",),
                validation_evidence_reference=(
                    {
                        "gate_id": "GATE-SCOPE",
                        "script_validation_result": "REQUIREMENT_SATISFIED",
                    },
                ),
            ),
        )

        self.assertIs(
            result.aggregate_gate_result,
            GateEvaluationResult.EVIDENCE_INSUFFICIENT,
        )

    def evidence_gate_input(self, **evidence):
        return GateInput(
            invocation_reference=GateInvocationReference(
                invocation_id="evidence:GATE-ARTIFACT-BOUNDARY",
                gate_id="GATE-ARTIFACT-BOUNDARY",
                trigger_event="evidence review",
                requested_action="accept capability claim",
            ),
            gate_definition_reference="GATE-ARTIFACT-BOUNDARY",
            gate_name="Artifact Boundary Gate",
            evaluation_nature="Evidence-Based",
            trigger_event="evidence review",
            risk_object=("Capability Claim",),
            requested_action="accept capability claim",
            evaluation_requirement=("Evidence boundary",),
            current_context_reference=None,
            current_workflow_phase_reference={"phase_id": "P4"},
            relevant_artifact_reference=None,
            evidence_set=(evidence,),
            maker_authorization_evidence=(),
            validation_evidence_reference=(),
            judgment_evidence=(),
            required_authorization=(),
            allowed_action="continue",
            blocked_action="accept claim",
            workflow_requirement_reference=None,
        )

    def assert_policy_result(self, expected_result, expected_reason, **evidence):
        output = self.coordinator.evaluate_gate(self.evidence_gate_input(**evidence))
        self.assertIs(expected_result, output.evaluation_result)
        self.assertIn(expected_reason, output.evaluation_reason)

    def test_evidence_level_and_scope_must_cover_claim(self):
        self.assert_policy_result(
            GateEvaluationResult.EVIDENCE_INSUFFICIENT,
            "EVIDENCE_LEVEL_TOO_LOW",
            evidence_level="E2",
            required_evidence_level="E3",
        )
        self.assert_policy_result(
            GateEvaluationResult.EVIDENCE_INSUFFICIENT,
            "EVIDENCE_SCOPE_MISMATCH",
            evidence_level="E3",
            required_evidence_level="E3",
            evidence_scope=["scene-a"],
            claim_scope=["scene-a", "scene-b"],
        )

    def test_e2_and_e3_cannot_overclaim_product_semantics(self):
        self.assert_policy_result(
            GateEvaluationResult.REQUIREMENT_UNSATISFIED,
            "CLAIM_EXCEEDS_EVIDENCE",
            evidence_level="E2",
            required_evidence_level="E2",
            claim_strength="FULL_TARGET_ENVIRONMENT",
        )
        self.assert_policy_result(
            GateEvaluationResult.REQUIREMENT_UNSATISFIED,
            "CLAIM_EXCEEDS_EVIDENCE",
            evidence_level="E3",
            required_evidence_level="E3",
            claim_strength="REPRESENTATIVE_STABILITY",
        )

    def test_baseline_regression_and_unresolved_drift_block_action(self):
        self.assert_policy_result(
            GateEvaluationResult.ACTION_BLOCKED,
            "BASELINE_REGRESSION",
            baseline_previous_result="PASS",
            baseline_current_result="FAIL",
        )
        self.assert_policy_result(
            GateEvaluationResult.ACTION_BLOCKED,
            "DRIFT_UNRESOLVED",
            unresolved_drift=True,
        )

    def test_ring_closure_and_human_validation_require_complete_records(self):
        self.assert_policy_result(
            GateEvaluationResult.REQUIREMENT_UNSATISFIED,
            "RING_CLOSURE_INCOMPLETE",
            ring_closure_required=True,
            ring_closure_complete=False,
        )
        self.assert_policy_result(
            GateEvaluationResult.EVIDENCE_INSUFFICIENT,
            "HUMAN_VALIDATION_PLAN_MISSING",
            human_validation_required=True,
            human_validation_plan_present=False,
        )

    def test_v1_gate_id_set_remains_unchanged(self):
        expected = {
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

        self.assertEqual(expected, set(self.coordinator.gates_by_id))


if __name__ == "__main__":
    unittest.main()
