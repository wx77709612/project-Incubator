import shutil
import unittest
from pathlib import Path

from PROJECT_INCUBATOR.runtime.components.context_coordinator import (
    AccessTarget,
    ContextType,
    MutationIntent,
    MutationType,
)
from PROJECT_INCUBATOR.runtime.components.workflow_coordinator import (
    CorrectionAssessmentRequest,
    PhaseResult,
)
from PROJECT_INCUBATOR.runtime.core.coordinator import RuntimeCoordinator, RuntimeRequest
from PROJECT_INCUBATOR.runtime.core.evidence_types import (
    CorrectionActivityState,
    CorrectionResult,
    failure_signature,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class CreationCorrectionAcceptance(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent / ".tmp_creation_correction_acceptance"
        shutil.rmtree(self.root, ignore_errors=True)
        self.root.mkdir(parents=True)
        self.write_state("P4")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write_state(self, phase):
        (self.root / "PROJECT_STATE.md").write_text(
            f"# PROJECT_STATE\n\n## Current Phase / 当前 Phase\n\n{phase}\n",
            encoding="utf-8",
        )

    def correction(self, count, model="model-1", phase="P4", impact=None):
        assessment = {
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
        assessment.update(impact or {})
        signature = failure_signature("cap-1", "scene-1", "boundary", "failed")
        return CorrectionAssessmentRequest(
            request_id=f"correction-{count}",
            current_phase=phase,
            capability_id="cap-1",
            candidate_model_version=model,
            scenario_id="scene-1",
            boundary_step="boundary",
            observed_outcome="failed",
            failure_signature=signature,
            consecutive_failure_count=count,
            evidence_refs=(f"evidence-{count}",),
            affected_assumption_ids=("assumption-1",),
            affected_artifacts=("design.md",),
            impact_assessment=assessment,
        )

    def execute(self, correction):
        return RuntimeCoordinator().execute(
            RuntimeRequest(
                request_id=f"runtime-{correction.request_id}",
                requested_action="evaluate correction",
                project_root=self.root,
                correction_assessment_request=correction,
            )
        )

    def resume_record(self):
        return {
            "affected_scope": ["cap-1"],
            "regression_set": ["test-1"],
            "updated_model": "model-2",
            "required_authorization": "NOT_REQUIRED",
            "resolved_drift": ["drift-1"],
            "evidence_change": ["evidence-4"],
            "confidence_change": "MEDIUM",
            "baseline_change": "STALE",
            "next_action": "continue bounded creation",
        }

    def assert_phase_p4(self):
        self.assertIn("\nP4\n", (self.root / "PROJECT_STATE.md").read_text(encoding="utf-8"))

    def test_b01_first_failure_requires_no_correction(self):
        result = self.execute(self.correction(1))
        self.assertIs(CorrectionResult.NO_CORRECTION, result.correction_result_reference.result)
        self.assertIs(RuntimeExecutionState.EXECUTING, result.runtime_execution_state)
        self.assert_phase_p4()

    def test_b02_second_failure_produces_advisory_and_keeps_executing(self):
        result = self.execute(self.correction(2))
        self.assertIs(CorrectionResult.MODEL_REVIEW_ADVISORY, result.correction_result_reference.result)
        self.assertIs(RuntimeExecutionState.EXECUTING, result.runtime_execution_state)
        self.assertIsNotNone(result.advisory_output_reference)
        self.assert_phase_p4()

    def test_b03_third_failure_requires_correction_and_suspends(self):
        result = self.execute(self.correction(3))
        self.assertIs(CorrectionResult.P4_CORRECTION_REQUIRED, result.correction_result_reference.result)
        self.assertIs(RuntimeExecutionState.SUSPENDED, result.runtime_execution_state)
        self.assert_phase_p4()

    def test_b04_local_correction_resumes_as_correction_active(self):
        result = RuntimeCoordinator().execute(
            RuntimeRequest(
                request_id="b04",
                requested_action="resume correction",
                project_root=self.root,
                correction_resume_request=self.resume_record(),
            )
        )
        self.assertIs(RuntimeExecutionState.EXECUTING, result.runtime_execution_state)
        self.assertIs(CorrectionActivityState.CORRECTION_ACTIVE, result.correction_activity_state)
        self.assert_phase_p4()

    def test_b05_maker_scope_impact_waits_for_maker(self):
        result = self.execute(self.correction(1, impact={"changes_product_goal": True}))
        self.assertIs(CorrectionResult.MAKER_SCOPE_REVIEW_REQUIRED, result.correction_result_reference.result)
        self.assertIs(RuntimeExecutionState.WAITING_FOR_MAKER, result.runtime_execution_state)
        self.assertTrue(result.required_maker_input)
        self.assert_phase_p4()

    def test_b06_non_p4_correction_is_contract_violation(self):
        result = self.execute(self.correction(1, phase="P3"))
        self.assertIs(CorrectionResult.CORRECTION_ASSESSMENT_INVALID, result.correction_result_reference.result)
        self.assertIs(RuntimeExecutionState.SUSPENDED, result.runtime_execution_state)
        self.assert_phase_p4()

    def test_b07_model_version_starts_new_counter_key_and_preserves_evidence(self):
        old = self.correction(3, model="model-1")
        new = self.correction(1, model="model-2")
        evidence_history = old.evidence_refs + new.evidence_refs
        self.assertNotEqual(old.counter_key, new.counter_key)
        self.assertEqual(("evidence-3", "evidence-1"), evidence_history)
        self.assertIs(CorrectionResult.NO_CORRECTION, self.execute(new).correction_result_reference.result)

    def test_b08_correction_cannot_execute_transition(self):
        phase_result = PhaseResult("P4", "P5", True, True, True, True)
        phase_mutation = MutationIntent(
            mutation_type=MutationType.UPDATE_CONTEXT,
            target_context=AccessTarget(ContextType.PROJECT_STATE, "PROJECT_STATE.md"),
            change_purpose="attempt transition",
            change_basis="WORKFLOW_STATE_CHANGE_REQUIREMENT",
            proposed_content="# PROJECT_STATE\n\nCurrent Phase: P5\n",
        )
        result = RuntimeCoordinator().execute(
            RuntimeRequest(
                request_id="b08",
                requested_action="correction with prohibited transition",
                project_root=self.root,
                correction_assessment_request=self.correction(3),
                phase_result=phase_result,
                context_mutation_intents=(phase_mutation,),
            )
        )
        self.assertIsNone(result.workflow_result_reference)
        self.assert_phase_p4()


if __name__ == "__main__":
    unittest.main()
