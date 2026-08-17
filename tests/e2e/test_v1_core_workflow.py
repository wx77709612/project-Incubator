import shutil
import unittest
from pathlib import Path
from types import SimpleNamespace

from PROJECT_INCUBATOR.runtime.adapters.file_store import FileStore
from PROJECT_INCUBATOR.runtime.components.advisory_bridge import (
    AdvisoryBridge,
    AdvisoryBridgeRequest,
    PHASE_ENTRY,
)
from PROJECT_INCUBATOR.runtime.components.context_coordinator import (
    AccessTarget,
    AccessType,
    AuthorizationEvidence,
    ContextCoordinator,
    ContextAccessRequest,
    ContextType,
    MutationIntent,
    MutationType,
    RequestSource,
)
from PROJECT_INCUBATOR.runtime.components.gate_coordinator import GATE_EVIDENCE_INSUFFICIENT
from PROJECT_INCUBATOR.runtime.components.script_coordinator import (
    EVIDENCE_READY,
    ScriptCoordinator,
    ScriptInvocationRequest,
)
from PROJECT_INCUBATOR.runtime.components.workflow_coordinator import PhaseResult
from PROJECT_INCUBATOR.runtime.core.contracts import (
    ContextAccessResultStatus,
    GateEvaluationResult,
    ScriptExecutionStatus,
    ScriptValidationResult,
    WorkflowResultStatus,
)
from PROJECT_INCUBATOR.runtime.core.coordinator import (
    RUNTIME_COMPLETED,
    RuntimeCoordinator,
    RuntimeRequest,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class RecordingScriptRunner:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.payloads = []

    def run(self, script_identity, payload):
        self.payloads.append((script_identity, payload))
        if not self.outputs:
            raise AssertionError("script runner output queue exhausted")
        return SimpleNamespace(output=self.outputs.pop(0))


class RecordingAdvisoryBridge(AdvisoryBridge):
    def __init__(self):
        super().__init__()
        self.results = []

    def prepare(self, request):
        result = super().prepare(request)
        self.results.append(result)
        return result


class V1CoreWorkflowE2ETest(unittest.TestCase):
    def setUp(self):
        self.base_root = Path(__file__).parent / ".tmp_v1_core_workflow"
        shutil.rmtree(self.base_root, ignore_errors=True)
        self.base_root.mkdir(parents=True)
        self.project_root = self.base_root / "managed_project"
        self.project_root.mkdir()
        self.script_runner = RecordingScriptRunner(
            (
                {
                    "execution_status": "COMPLETED",
                    "validation_result": "REQUIREMENT_SATISFIED",
                    "evidence": [
                        {
                            "evidence_id": "validation-result-evidence",
                            "evidence_type": "SCRIPT_VALIDATION",
                            "artifact": "PROJECT_ARTIFACT.md",
                        },
                    ],
                },
            ),
        )
        self.advisory_bridge = RecordingAdvisoryBridge()
        self.runtime = RuntimeCoordinator(
            script_coordinator=ScriptCoordinator(self.script_runner),
            advisory_bridge=self.advisory_bridge,
        )

    def tearDown(self):
        shutil.rmtree(self.base_root, ignore_errors=True)

    def test_v1_core_workflow_from_new_project_to_iteration(self):
        self.assertFalse((self.project_root / "PROJECT_STATE.md").exists())

        bootstrap_result = self.runtime.execute(
            RuntimeRequest(
                request_id="e2e-p0-bootstrap",
                requested_action="P0 Intent Discovery creates profile and initial state",
                project_root=self.project_root,
                existing_project=False,
                new_project_bootstrap=True,
                phase_result=self.phase_result("P0", "P1"),
                context_mutation_intents=(
                    self.profile_intent(),
                    self.state_intent("P1", MutationType.CREATE_CONTEXT),
                ),
            ),
        )
        self.assert_completed_transition(bootstrap_result, "P1")
        self.assert_context_mutations_accepted(bootstrap_result)
        self.assertTrue((self.project_root / "PROJECT_PROFILE.md").exists())

        gate_result = self.runtime.execute(
            RuntimeRequest(
                request_id="e2e-authorized-gate",
                requested_action="push",
                project_root=self.project_root,
                gate_trigger_event="push",
                requested_gate_ids=("GATE-GIT",),
                gate_evaluation_evidence=(
                    {
                        "gate_id": "GATE-GIT",
                        "gate_result": "REQUIREMENT_SATISFIED",
                        "requires_maker_authorization": True,
                    },
                ),
                maker_authorization_evidence=(
                    {
                        "gate_id": "GATE-GIT",
                        "authorizer": "MAKER",
                        "authorized_action_reference": "push",
                    },
                ),
            ),
        )
        self.assertIs(gate_result.runtime_execution_state, RuntimeExecutionState.COMPLETED)
        self.assertIsNotNone(gate_result.gate_output_reference)
        self.assertIs(
            gate_result.gate_output_reference.aggregate_gate_result,
            GateEvaluationResult.REQUIREMENT_SATISFIED,
        )
        self.assert_project_state_phase("P1")

        script_cannot_replace_gate = self.runtime.execute(
            RuntimeRequest(
                request_id="e2e-script-is-not-gate",
                requested_action="scope approval requires judgment gate",
                project_root=self.project_root,
                requested_gate_ids=("GATE-SCOPE",),
                gate_validation_evidence=(
                    {
                        "gate_id": "GATE-SCOPE",
                        "script_validation_result": "REQUIREMENT_SATISFIED",
                    },
                ),
            ),
        )
        self.assertIs(
            script_cannot_replace_gate.runtime_execution_state,
            RuntimeExecutionState.SUSPENDED,
        )
        self.assertEqual(GATE_EVIDENCE_INSUFFICIENT, script_cannot_replace_gate.runtime_reason)
        self.assertIs(
            script_cannot_replace_gate.gate_output_reference.aggregate_gate_result,
            GateEvaluationResult.EVIDENCE_INSUFFICIENT,
        )
        self.assert_project_state_phase("P1")

        p1_result = self.runtime.execute(
            RuntimeRequest(
                request_id="e2e-p1-definition",
                requested_action="P1 Project Definition completes state for design",
                project_root=self.project_root,
                phase_result=self.phase_result("P1", "P2"),
                context_mutation_intents=(self.state_intent("P2"),),
            ),
        )
        self.assert_completed_transition(p1_result, "P2")
        self.assert_context_mutations_accepted(p1_result)

        self.write_agent_artifact(
            "SOLUTION_DESIGN.md",
            "# Solution Design\n\nArtifact prepared by the Agent before Runtime transition.\n",
        )
        p2_result = self.runtime.execute(
            RuntimeRequest(
                request_id="e2e-p2-solution-design",
                requested_action="P2 Solution Design completes design artifact",
                project_root=self.project_root,
                phase_result=self.phase_result(
                    "P2",
                    "P3",
                    artifact_evidence=("SOLUTION_DESIGN.md",),
                ),
                context_mutation_intents=(self.state_intent("P3"),),
            ),
        )
        self.assert_completed_transition(p2_result, "P3")
        self.assert_context_mutations_accepted(p2_result)
        self.assertTrue((self.project_root / "SOLUTION_DESIGN.md").exists())

        p3_result = self.runtime.execute(
            RuntimeRequest(
                request_id="e2e-p3-execution-planning",
                requested_action="P3 Execution Planning creates plan and advances",
                project_root=self.project_root,
                phase_result=self.phase_result("P3", "P4"),
                context_mutation_intents=(
                    self.plan_intent(),
                    self.state_intent("P4"),
                ),
            ),
        )
        self.assert_completed_transition(p3_result, "P4")
        self.assert_context_mutations_accepted(p3_result)
        self.assertTrue((self.project_root / "PROJECT_PLAN.md").exists())

        self.write_agent_artifact(
            "PROJECT_ARTIFACT.md",
            "# Project Artifact\n\nCreated by Agent work before validation.\n",
        )
        p4_result = self.runtime.execute(
            RuntimeRequest(
                request_id="e2e-p4-creation",
                requested_action="P4 Creation produces project artifact",
                project_root=self.project_root,
                phase_result=self.phase_result(
                    "P4",
                    "P5",
                    artifact_evidence=("PROJECT_ARTIFACT.md",),
                ),
                context_mutation_intents=(self.state_intent("P5"),),
            ),
        )
        self.assert_completed_transition(p4_result, "P5")
        self.assert_context_mutations_accepted(p4_result)
        self.assertTrue((self.project_root / "PROJECT_ARTIFACT.md").exists())

        p5_result = self.runtime.execute(
            RuntimeRequest(
                request_id="e2e-p5-validation",
                requested_action="P5 Validation consumes script evidence",
                project_root=self.project_root,
                script_invocation_requests=(
                    ScriptInvocationRequest(
                        invocation_id="e2e-validation-script",
                        script_identity="artifact-validation",
                        invocation_purpose="VALIDATION",
                        artifact_reference={"path": "PROJECT_ARTIFACT.md"},
                        validation_requirement={
                            "requirement": "Project Artifact validation passes",
                        },
                    ),
                ),
                phase_result=self.phase_result(
                    "P5",
                    "P6",
                    artifact_evidence=("PROJECT_ARTIFACT.md",),
                ),
                context_mutation_intents=(self.state_intent("P6"),),
            ),
        )
        self.assert_completed_transition(p5_result, "P6")
        self.assert_context_mutations_accepted(p5_result)
        self.assertEqual(1, len(p5_result.script_output_reference))
        script_result = p5_result.script_output_reference[0]
        self.assertEqual(EVIDENCE_READY, script_result.result_reason)
        self.assertIs(script_result.execution_status, ScriptExecutionStatus.COMPLETED)
        self.assertIs(
            script_result.validation_result,
            ScriptValidationResult.REQUIREMENT_SATISFIED,
        )
        self.assertTrue(script_result.evidence)

        self.assertEqual(1, len(self.script_runner.payloads))
        _, script_payload = self.script_runner.payloads[0]
        self.assertIsNone(script_payload["context_reference"])

        advisory_result = self.runtime.execute(
            RuntimeRequest(
                request_id="e2e-p6-advisory",
                requested_action="prepare P6 phase entry advisory context",
                project_root=self.project_root,
                advisory_request=AdvisoryBridgeRequest(
                    request_id="e2e-p6-advisory-request",
                    event_type="Phase Entry",
                    current_phase={"phase_id": "P6"},
                    project_context={"source": "PROJECT_STATE.md"},
                    requested_trigger_ids=(PHASE_ENTRY,),
                    source_context_references=("PROJECT_STATE.md",),
                ),
            ),
        )
        self.assertIs(advisory_result.runtime_execution_state, RuntimeExecutionState.COMPLETED)
        self.assertEqual(1, len(self.advisory_bridge.results))
        self.assertEqual(
            (PHASE_ENTRY,),
            tuple(
                trigger.trigger_id
                for trigger in self.advisory_bridge.results[0].matched_triggers
            ),
        )
        self.assertFalse(self.advisory_bridge.results[0].runtime_state_changed)
        self.assert_project_state_phase("P6")

        p6_iteration_result = self.runtime.execute(
            RuntimeRequest(
                request_id="e2e-p6-iteration",
                requested_action="P6 Iteration returns to solution design",
                project_root=self.project_root,
                phase_result=self.phase_result("P6", "P2"),
                context_mutation_intents=(self.state_intent("P2"),),
            ),
        )
        self.assert_completed_transition(p6_iteration_result, "P2")
        self.assert_context_mutations_accepted(p6_iteration_result)

    def phase_result(self, current_phase, requested_next_phase, artifact_evidence=()):
        return PhaseResult(
            current_phase=current_phase,
            requested_next_phase=requested_next_phase,
            process_completed=True,
            required_artifact_requirement_satisfied=True,
            state_change_requirement_formed=True,
            gate_requirement_resolved=True,
            artifact_evidence=tuple(artifact_evidence),
            state_change_reference=f"PROJECT_STATE.md Current Phase {requested_next_phase}",
            gate_resolution_reference="No unresolved gate requirement",
        )

    def profile_intent(self):
        return MutationIntent(
            mutation_type=MutationType.CREATE_CONTEXT,
            target_context=AccessTarget(ContextType.PROJECT_PROFILE, "PROJECT_PROFILE.md"),
            change_purpose="Persist Maker confirmed project profile",
            change_basis="MAKER_CONFIRMED_CHANGE",
            proposed_content=(
                "# PROJECT_PROFILE\n\n"
                "## Project Intent / 项目意图\n\n"
                "- Build a Project Incubator managed project.\n"
            ),
            maker_authorization=AuthorizationEvidence(
                source=RequestSource.MAKER,
                confirmed=True,
                reference="Maker confirmed project profile",
            ),
            gate_evidence_reference="GATE-AUTHORITY-DOCUMENT satisfied",
        )

    def plan_intent(self):
        return MutationIntent(
            mutation_type=MutationType.CREATE_CONTEXT,
            target_context=AccessTarget(ContextType.PROJECT_PLAN, "PROJECT_PLAN.md"),
            change_purpose="Persist current future execution plan",
            change_basis="WORKFLOW_STATE_CHANGE_REQUIREMENT",
            proposed_content=(
                "# PROJECT_PLAN\n\n"
                "## Execution Order / 总体执行顺序\n\n"
                "1. P4 Creation\n"
                "2. P5 Validation\n"
            ),
        )

    def state_intent(self, phase, mutation_type=MutationType.UPDATE_CONTEXT):
        return MutationIntent(
            mutation_type=mutation_type,
            target_context=AccessTarget(ContextType.PROJECT_STATE, "PROJECT_STATE.md"),
            change_purpose=f"Persist workflow transition to {phase}",
            change_basis="WORKFLOW_STATE_CHANGE_REQUIREMENT",
            proposed_content=self.project_state_content(phase),
        )

    def project_state_content(self, phase):
        return (
            "# PROJECT_STATE\n\n"
            "## Current Phase / 当前 Phase\n\n"
            f"{phase}\n\n"
            "## Current Execution State / 当前执行状态\n\n"
            "READY\n\n"
            "## Current Gate State / 当前 Gate 状态\n\n"
            "- 无\n"
        )

    def write_agent_artifact(self, name, content):
        path = self.project_root / name
        path.write_text(content, encoding="utf-8")

    def assert_completed_transition(self, result, expected_phase):
        self.assertIs(result.runtime_execution_state, RuntimeExecutionState.COMPLETED)
        self.assertEqual(RUNTIME_COMPLETED, result.runtime_reason)
        self.assertIsNotNone(result.workflow_result_reference)
        self.assertIs(
            result.workflow_result_reference.status,
            WorkflowResultStatus.READY_FOR_TRANSITION,
        )
        self.assertEqual(expected_phase, result.current_phase_reference.phase_id)
        self.assert_project_state_phase(expected_phase)

    def assert_context_mutations_accepted(self, result):
        mutation_results = tuple(
            context_result
            for context_result in result.context_access_result_reference
            if context_result.requested_access_type
            in {AccessType.REQUEST_MUTATION, AccessType.EXECUTE_MUTATION}
        )
        self.assertTrue(mutation_results)
        self.assertTrue(
            all(
                context_result.status is ContextAccessResultStatus.ACCEPTED
                for context_result in mutation_results
            ),
        )
        executed_mutations = tuple(
            context_result
            for context_result in mutation_results
            if context_result.requested_access_type is AccessType.EXECUTE_MUTATION
        )
        self.assertTrue(executed_mutations)
        self.assertTrue(
            all(context_result.persisted_result_verified for context_result in executed_mutations),
        )

    def assert_project_state_phase(self, expected_phase):
        content = (self.project_root / "PROJECT_STATE.md").read_text(encoding="utf-8")
        self.assertIn("## Current Phase / 当前 Phase", content)
        self.assertIn(f"\n{expected_phase}\n", content)

    def test_script_source_direct_context_read_is_rejected(self):
        context_result = ContextCoordinator(FileStore(self.project_root)).handle(
            ContextAccessRequest(
                request_id="e2e-script-direct-read",
                access_target=AccessTarget(ContextType.PROJECT_STATE, "PROJECT_STATE.md"),
                access_type=AccessType.READ,
                request_source=RequestSource.SCRIPT,
                access_purpose="Script attempts direct context read",
            ),
        )

        self.assertIs(context_result.status, ContextAccessResultStatus.REJECTED)
        self.assertEqual(
            "Runtime-provided limited input",
            context_result.missing_requirement,
        )


if __name__ == "__main__":
    unittest.main()
