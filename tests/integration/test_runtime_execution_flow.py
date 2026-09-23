import shutil
import unittest
from pathlib import Path
from types import SimpleNamespace

from PROJECT_INCUBATOR.runtime.components.context_coordinator import (
    AccessTarget,
    ContextType,
    MutationIntent,
    MutationType,
)
from PROJECT_INCUBATOR.runtime.components.script_coordinator import (
    SCRIPT_EXECUTION_ERROR,
    VALIDATION_UNSATISFIED,
    ScriptCoordinator,
    ScriptInvocationRequest,
)
from PROJECT_INCUBATOR.runtime.components.workflow_coordinator import (
    CorrectionAssessmentRequest,
    PhaseResult,
)
from PROJECT_INCUBATOR.runtime.core.contracts import (
    ContextAccessResultStatus,
    WorkflowResultStatus,
)
from PROJECT_INCUBATOR.runtime.core.coordinator import (
    CONTEXT_CONFLICT,
    RUNTIME_COMPLETED,
    WORKFLOW_NOT_READY,
    RuntimeCoordinator,
    RuntimeRequest,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState
from PROJECT_INCUBATOR.runtime.core.evidence_types import CorrectionResult, failure_signature


class QueueScriptRunner:
    def __init__(self, outputs):
        self.outputs = list(outputs)

    def run(self, script_identity, payload):
        if not self.outputs:
            raise AssertionError("script runner output queue exhausted")
        return SimpleNamespace(output=self.outputs.pop(0))


class RuntimeExecutionFlowIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.base_root = Path(__file__).parent / ".tmp_runtime_execution_flow"
        shutil.rmtree(self.base_root, ignore_errors=True)
        self.base_root.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.base_root, ignore_errors=True)

    def test_scenario_a_legal_phase_transition(self):
        root = self.project_root("scenario_a", "P0")
        result = RuntimeCoordinator().execute(
            RuntimeRequest(
                request_id="scenario-a",
                requested_action="transition P0 to P1",
                project_root=root,
                phase_result=self.phase_result("P0", "P1"),
                context_mutation_intents=(self.state_intent("P1"),),
            ),
        )

        self.assertIs(result.runtime_execution_state, RuntimeExecutionState.COMPLETED)
        self.assertEqual(RUNTIME_COMPLETED, result.runtime_reason)
        self.assertEqual("P1", result.current_phase_reference.phase_id)
        self.assertIs(
            result.workflow_result_reference.status,
            WorkflowResultStatus.READY_FOR_TRANSITION,
        )
        self.assertTrue(
            any(
                context_result.requested_access_type.value == "EXECUTE_MUTATION"
                and context_result.status is ContextAccessResultStatus.ACCEPTED
                for context_result in result.context_access_result_reference
            ),
        )

    def test_scenario_b_required_artifact_missing(self):
        root = self.project_root("scenario_b", "P0")
        result = RuntimeCoordinator().execute(
            RuntimeRequest(
                request_id="scenario-b",
                requested_action="transition P0 to P1",
                project_root=root,
                phase_result=self.phase_result(
                    "P0",
                    "P1",
                    required_artifact_requirement_satisfied=False,
                ),
            ),
        )

        self.assertIs(result.runtime_execution_state, RuntimeExecutionState.SUSPENDED)
        self.assertEqual(WORKFLOW_NOT_READY, result.runtime_reason)
        self.assertIs(result.workflow_result_reference.status, WorkflowResultStatus.NOT_READY)
        self.assertIn("Required Artifact Requirement", result.pending_requirement)

    def test_scenario_c_gate_authorization_missing(self):
        root = self.project_root("scenario_c", "P0")
        result = RuntimeCoordinator().execute(
            RuntimeRequest(
                request_id="scenario-c",
                requested_action="push",
                project_root=root,
                gate_trigger_event="push",
                requested_gate_ids=("GATE-GIT",),
                gate_evaluation_evidence=(
                    {
                        "gate_id": "GATE-GIT",
                        "gate_result": "REQUIREMENT_SATISFIED",
                    },
                ),
                context_mutation_intents=(self.state_intent("P1"),),
            ),
        )

        self.assertIs(result.runtime_execution_state, RuntimeExecutionState.WAITING_FOR_MAKER)
        self.assertEqual("GATE_AUTHORIZATION_REQUIRED", result.runtime_reason)
        self.assertIn("Maker Authorization Evidence", result.required_maker_input)
        self.assert_project_state_phase(root, "P0")

    def test_scenario_d_context_conflict(self):
        root = self.project_root("scenario_d", "P0")
        result = RuntimeCoordinator().execute(
            RuntimeRequest(
                request_id="scenario-d",
                requested_action="prepare conflicting state mutation",
                project_root=root,
                context_mutation_intents=(
                    self.state_intent("P1", conflict_reference="PROJECT_STATE conflict"),
                ),
            ),
        )

        self.assertIs(result.runtime_execution_state, RuntimeExecutionState.SUSPENDED)
        self.assertEqual(CONTEXT_CONFLICT, result.runtime_reason)
        self.assertIn("PROJECT_STATE conflict", result.pending_requirement)
        self.assert_project_state_phase(root, "P0")

    def test_scenario_e_script_validation_failure(self):
        root = self.project_root("scenario_e", "P0")
        coordinator = RuntimeCoordinator(
            script_coordinator=ScriptCoordinator(
                QueueScriptRunner(
                    (
                        {
                            "execution_status": "COMPLETED",
                            "validation_result": "REQUIREMENT_UNSATISFIED",
                        },
                    ),
                ),
            ),
        )

        result = coordinator.execute(
            RuntimeRequest(
                request_id="scenario-e",
                requested_action="validate artifact",
                project_root=root,
                script_invocation_requests=(
                    ScriptInvocationRequest(
                        invocation_id="scenario-e-script",
                        script_identity="validation-script",
                        invocation_purpose="VALIDATION",
                    ),
                ),
            ),
        )

        self.assertIs(result.runtime_execution_state, RuntimeExecutionState.SUSPENDED)
        self.assertEqual(VALIDATION_UNSATISFIED, result.runtime_reason)
        self.assertEqual(1, len(result.script_output_reference))

    def test_scenario_f_script_execution_error(self):
        root = self.project_root("scenario_f", "P0")
        coordinator = RuntimeCoordinator(
            script_coordinator=ScriptCoordinator(
                QueueScriptRunner(
                    (
                        {
                            "execution_status": "EXECUTION_ERROR",
                            "validation_result": "",
                            "error_information": {
                                "error_type": "SCRIPT_EXECUTION_ERROR",
                                "error_reason": "script failed",
                            },
                        },
                    ),
                ),
            ),
        )

        result = coordinator.execute(
            RuntimeRequest(
                request_id="scenario-f",
                requested_action="run deterministic script",
                project_root=root,
                script_invocation_requests=(
                    ScriptInvocationRequest(
                        invocation_id="scenario-f-script",
                        script_identity="failing-script",
                        invocation_purpose="VALIDATION",
                    ),
                ),
            ),
        )

        self.assertIs(result.runtime_execution_state, RuntimeExecutionState.FAILED)
        self.assertEqual(SCRIPT_EXECUTION_ERROR, result.runtime_reason)

    def test_scenario_g_p6_iteration_returns_allowed_targets(self):
        for target_phase in ("P2", "P3", "P4", "P5"):
            with self.subTest(target_phase=target_phase):
                root = self.project_root(f"scenario_g_{target_phase}", "P6")
                result = RuntimeCoordinator().execute(
                    RuntimeRequest(
                        request_id=f"scenario-g-{target_phase}",
                        requested_action=f"iterate P6 to {target_phase}",
                        project_root=root,
                        phase_result=self.phase_result("P6", target_phase),
                        context_mutation_intents=(self.state_intent(target_phase),),
                    ),
                )

                self.assertIs(result.runtime_execution_state, RuntimeExecutionState.COMPLETED)
                self.assertEqual(RUNTIME_COMPLETED, result.runtime_reason)
                self.assertEqual(target_phase, result.current_phase_reference.phase_id)
                self.assertIs(
                    result.workflow_result_reference.status,
                    WorkflowResultStatus.READY_FOR_TRANSITION,
                )
                self.assert_project_state_phase(root, target_phase)

    def test_p4_repeated_failure_advises_then_suspends(self):
        root = self.project_root("p4_failure", "P4")

        advisory = RuntimeCoordinator().execute(
            RuntimeRequest(
                request_id="p4-count-2",
                requested_action="evaluate correction",
                project_root=root,
                correction_assessment_request=self.correction_request(2),
            )
        )
        correction = RuntimeCoordinator().execute(
            RuntimeRequest(
                request_id="p4-count-3",
                requested_action="evaluate correction",
                project_root=root,
                correction_assessment_request=self.correction_request(3),
            )
        )

        self.assertIs(RuntimeExecutionState.EXECUTING, advisory.runtime_execution_state)
        self.assertIs(CorrectionResult.MODEL_REVIEW_ADVISORY, advisory.correction_result_reference.result)
        self.assertIsNotNone(advisory.advisory_output_reference)
        self.assertIs(RuntimeExecutionState.SUSPENDED, correction.runtime_execution_state)
        self.assertIs(CorrectionResult.P4_CORRECTION_REQUIRED, correction.correction_result_reference.result)
        self.assert_project_state_phase(root, "P4")

    def test_local_correction_resume_stays_in_p4(self):
        root = self.project_root("p4_resume", "P4")
        result = RuntimeCoordinator().execute(
            RuntimeRequest(
                request_id="p4-resume",
                requested_action="resume local correction",
                project_root=root,
                correction_resume_request=self.correction_resume(),
            )
        )

        self.assertIs(RuntimeExecutionState.EXECUTING, result.runtime_execution_state)
        self.assertEqual("CORRECTION_RESUMED", result.runtime_reason)
        self.assertEqual("CORRECTION_ACTIVE", result.correction_activity_state.value)
        self.assert_project_state_phase(root, "P4")

    def test_maker_scope_wait_and_authorized_resume(self):
        root = self.project_root("maker_scope", "P4")
        waiting = RuntimeCoordinator().execute(
            RuntimeRequest(
                request_id="maker-wait",
                requested_action="evaluate correction",
                project_root=root,
                correction_assessment_request=self.correction_request(
                    1,
                    {"changes_maker_approved_scope": True},
                ),
            )
        )
        resume = self.correction_resume()
        resume.update(
            {
                "maker_scope_resolution": "EXPAND_LOCAL_CORRECTION",
                "authorization_evidence": "maker-confirmation-1",
            }
        )
        resumed = RuntimeCoordinator().execute(
            RuntimeRequest(
                request_id="maker-resume",
                requested_action="resume authorized correction",
                project_root=root,
                correction_resume_request=resume,
            )
        )

        self.assertIs(RuntimeExecutionState.WAITING_FOR_MAKER, waiting.runtime_execution_state)
        self.assertTrue(waiting.required_maker_input)
        self.assertIs(RuntimeExecutionState.EXECUTING, resumed.runtime_execution_state)
        self.assert_project_state_phase(root, "P4")

    def project_root(self, name, phase):
        root = self.base_root / name
        root.mkdir(parents=True)
        (root / "PROJECT_STATE.md").write_text(self.project_state_content(phase), encoding="utf-8")
        return root

    def project_state_content(self, phase):
        return (
            "# PROJECT_STATE\n\n"
            "## Current Phase / 当前 Phase\n\n"
            f"{phase}\n\n"
            "## Current Execution State / 当前执行状态\n\n"
            "进行中\n"
        )

    def state_intent(self, phase, conflict_reference=None):
        return MutationIntent(
            mutation_type=MutationType.UPDATE_CONTEXT,
            target_context=AccessTarget(ContextType.PROJECT_STATE, "PROJECT_STATE.md"),
            change_purpose="Persist workflow state change",
            change_basis="WORKFLOW_STATE_CHANGE_REQUIREMENT",
            proposed_content=self.project_state_content(phase),
            conflict_reference=conflict_reference,
        )

    def phase_result(
        self,
        current_phase,
        requested_next_phase,
        required_artifact_requirement_satisfied=True,
    ):
        return PhaseResult(
            current_phase=current_phase,
            requested_next_phase=requested_next_phase,
            process_completed=True,
            required_artifact_requirement_satisfied=required_artifact_requirement_satisfied,
            state_change_requirement_formed=True,
            gate_requirement_resolved=True,
        )

    def correction_request(self, count, impact_overrides=None):
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
        signature = failure_signature("cap-1", "scene-1", "boundary", "failed")
        return CorrectionAssessmentRequest(
            request_id=f"correction-{count}",
            current_phase="P4",
            capability_id="cap-1",
            candidate_model_version="model-1",
            scenario_id="scene-1",
            boundary_step="boundary",
            observed_outcome="failed",
            failure_signature=signature,
            consecutive_failure_count=count,
            evidence_refs=("evidence-1",),
            affected_assumption_ids=("assumption-1",),
            affected_artifacts=("design.md",),
            impact_assessment=impact,
        )

    def correction_resume(self):
        return {
            "affected_scope": ["cap-1"],
            "regression_set": ["test-1"],
            "updated_model": "model-2",
            "required_authorization": "NOT_REQUIRED",
            "resolved_drift": ["drift-1"],
            "evidence_change": ["evidence-2"],
            "confidence_change": "MEDIUM",
            "baseline_change": "STALE",
            "next_action": "continue bounded implementation",
        }

    def assert_project_state_phase(self, root, phase):
        self.assertIn(
            f"\n{phase}\n",
            (root / "PROJECT_STATE.md").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
