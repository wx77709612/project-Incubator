import unittest
import json
from pathlib import Path

from PROJECT_INCUBATOR.runtime.components.workflow_coordinator import (
    CorrectionAssessmentRequest,
    PhaseResult,
    WorkflowCoordinator,
)
from PROJECT_INCUBATOR.runtime.core.contracts import WorkflowResultStatus
from PROJECT_INCUBATOR.runtime.core.evidence_types import (
    CorrectionActivityState,
    CorrectionResult,
    failure_signature,
)


ROOT = Path(__file__).resolve().parents[2]


def correction_request(
    count=1,
    current_phase="P4",
    model_version="model-1",
    impact_overrides=None,
):
    impact = {
        "changes_product_goal": False,
        "changes_success_criteria": False,
        "changes_maker_approved_scope": False,
        "changes_core_phase_model": False,
        "changes_context_authority": False,
        "changes_runtime_invariant": False,
        "crosses_current_work_package": False,
        "affected_scope_identified": True,
        "regression_set_identified": True,
    }
    impact.update(impact_overrides or {})
    signature = failure_signature("cap-1", "scene-1", "host-call", "missing")
    return CorrectionAssessmentRequest(
        request_id="correction-1",
        current_phase=current_phase,
        capability_id="cap-1",
        candidate_model_version=model_version,
        scenario_id="scene-1",
        boundary_step="host-call",
        observed_outcome="missing",
        failure_signature=signature,
        consecutive_failure_count=count,
        evidence_refs=("evidence-1",),
        affected_assumption_ids=("assumption-1",),
        affected_artifacts=("design.md",),
        impact_assessment=impact,
        authorization_evidence=(),
    )


class WorkflowCoordinatorTest(unittest.TestCase):
    def setUp(self):
        self.coordinator = WorkflowCoordinator()

    def test_resolves_current_phase_from_project_state(self):
        current_phase = self.coordinator.resolve_current_phase({"Current Phase": "P1"})

        self.assertEqual("P1", current_phase.phase_id)
        self.assertEqual("Project Definition", current_phase.phase_name)

    def test_invalid_transition_is_not_allowed(self):
        phase_result = PhaseResult(
            current_phase="P0",
            requested_next_phase="P3",
            process_completed=True,
            required_artifact_requirement_satisfied=True,
            state_change_requirement_formed=True,
            gate_requirement_resolved=True,
        )
        transition = self.coordinator.create_transition_request("invalid", phase_result)

        result = self.coordinator.evaluate_transition(transition)

        self.assertIs(result.status, WorkflowResultStatus.TRANSITION_NOT_ALLOWED)
        self.assertIn("Allowed Next Phase", result.missing_requirements)

    def test_incomplete_phase_result_is_not_ready(self):
        phase_result = PhaseResult(
            current_phase="P0",
            requested_next_phase="P1",
            process_completed=False,
            required_artifact_requirement_satisfied=True,
            state_change_requirement_formed=True,
            gate_requirement_resolved=True,
        )
        transition = self.coordinator.create_transition_request("not-ready", phase_result)

        result = self.coordinator.evaluate_transition(transition)

        self.assertIs(result.status, WorkflowResultStatus.NOT_READY)
        self.assertIn("Process Completion", result.missing_requirements)

    def test_failure_counts_map_to_correction_results(self):
        expected = {
            1: (CorrectionResult.NO_CORRECTION, CorrectionActivityState.NORMAL_CREATION),
            2: (CorrectionResult.MODEL_REVIEW_ADVISORY, CorrectionActivityState.NORMAL_CREATION),
            3: (CorrectionResult.P4_CORRECTION_REQUIRED, CorrectionActivityState.CORRECTION_REVIEW),
        }

        for count, expected_values in expected.items():
            with self.subTest(count=count):
                result = self.coordinator.evaluate_correction(correction_request(count=count))
                self.assertEqual(expected_values, (result.result, result.activity_state))
                self.assertIsNone(result.transition_request)

    def test_invalid_impact_boolean_is_rejected_without_guessing(self):
        request = correction_request(impact_overrides={"changes_product_goal": "no"})

        result = self.coordinator.evaluate_correction(request)

        self.assertIs(CorrectionResult.CORRECTION_ASSESSMENT_INVALID, result.result)
        self.assertIn("changes_product_goal", result.missing_requirements)

    def test_non_p4_correction_is_rejected(self):
        result = self.coordinator.evaluate_correction(correction_request(current_phase="P3"))

        self.assertIs(CorrectionResult.CORRECTION_ASSESSMENT_INVALID, result.result)
        self.assertEqual("P3", result.current_phase)
        self.assertIsNone(result.transition_request)

    def test_candidate_model_version_changes_counter_key(self):
        first = correction_request(model_version="model-1")
        updated = correction_request(model_version="model-2")

        self.assertNotEqual(first.counter_key, updated.counter_key)
        self.assertEqual(first.failure_signature, updated.failure_signature)

    def test_maker_scope_impact_takes_precedence_over_failure_count(self):
        request = correction_request(
            count=1,
            impact_overrides={"changes_product_goal": True},
        )

        result = self.coordinator.evaluate_correction(request)

        self.assertIs(CorrectionResult.MAKER_SCOPE_REVIEW_REQUIRED, result.result)
        self.assertIs(
            CorrectionActivityState.AWAITING_MAKER_SCOPE_REVIEW,
            result.activity_state,
        )

    def test_resume_requires_every_contract_reference(self):
        missing = self.coordinator.validate_correction_resume(
            {
                "affected_scope": ["cap-1"],
                "regression_set": ["test-1"],
            }
        )

        self.assertIn("updated_model", missing)
        self.assertIn("next_action", missing)

    def test_correction_policy_does_not_change_v1_transition_matrix(self):
        active = json.loads(
            (ROOT / "PROJECT_INCUBATOR/references/workflow/core_workflow.json").read_text(
                encoding="utf-8"
            )
        )["workflow"]
        v1_transition_fixture = [
            {"from": "P0", "to": "P1"},
            {"from": "P1", "to": "P2"},
            {"from": "P2", "to": "P3"},
            {"from": "P3", "to": "P4"},
            {"from": "P4", "to": "P5"},
            {"from": "P5", "to": "P6"},
            {"from": "P6", "to": "P2"},
            {"from": "P6", "to": "P3"},
            {"from": "P6", "to": "P4"},
            {"from": "P6", "to": "P5"},
        ]

        self.assertEqual([f"P{index}" for index in range(7)], active["core_phase_set"])
        self.assertEqual(v1_transition_fixture, active["allowed_transitions"])
        self.assertIn("correction_policy", next(p for p in active["phases"] if p["phase_id"] == "P4"))


if __name__ == "__main__":
    unittest.main()
