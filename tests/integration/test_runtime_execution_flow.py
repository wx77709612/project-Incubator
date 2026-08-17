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
from PROJECT_INCUBATOR.runtime.components.workflow_coordinator import PhaseResult
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

    def assert_project_state_phase(self, root, phase):
        self.assertIn(
            f"\n{phase}\n",
            (root / "PROJECT_STATE.md").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
