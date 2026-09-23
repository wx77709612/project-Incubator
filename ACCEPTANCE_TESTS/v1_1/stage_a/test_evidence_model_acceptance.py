import shutil
import unittest
from pathlib import Path

from PROJECT_INCUBATOR.runtime.adapters.file_store import FileStore
from PROJECT_INCUBATOR.runtime.components.advisory_bridge import AdvisoryBridge, AdvisoryBridgeRequest
from PROJECT_INCUBATOR.runtime.components.context_coordinator import (
    AccessTarget,
    AccessType,
    ContextAccessRequest,
    ContextCoordinator,
    ContextType,
    MutationIntent,
    MutationType,
    RequestSource,
)
from PROJECT_INCUBATOR.runtime.components.gate_coordinator import (
    GateCoordinator,
    GateInput,
    GateInvocationReference,
)
from PROJECT_INCUBATOR.runtime.components.script_coordinator import (
    SCRIPT_EVIDENCE_BOUNDARY_VIOLATION,
    ScriptCoordinator,
    ScriptInvocationRequest,
)
from PROJECT_INCUBATOR.runtime.core.contracts import (
    ContextAccessResultStatus,
    GateEvaluationResult,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class EvidenceModelAcceptance(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent / ".tmp_evidence_model_acceptance"
        shutil.rmtree(self.root, ignore_errors=True)
        self.root.mkdir(parents=True)
        self.gate = GateCoordinator()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def gate_input(self, **evidence):
        return GateInput(
            invocation_reference=GateInvocationReference(
                "acceptance:GATE-ARTIFACT-BOUNDARY",
                "GATE-ARTIFACT-BOUNDARY",
                "claim review",
                "accept claim",
            ),
            gate_definition_reference="GATE-ARTIFACT-BOUNDARY",
            gate_name="Artifact Boundary Gate",
            evaluation_nature="Evidence-Based",
            trigger_event="claim review",
            risk_object=("Capability Claim",),
            requested_action="accept claim",
            evaluation_requirement=("Evidence Boundary",),
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

    def test_a01_e2_supports_local_mechanism_claim(self):
        output = self.gate.evaluate_gate(
            self.gate_input(
                evidence_level="E2",
                required_evidence_level="E2",
                evidence_scope=["local-helper"],
                claim_scope=["local-helper"],
                claim_strength="LOCAL_MECHANISM",
            )
        )
        self.assertIs(GateEvaluationResult.REQUIREMENT_SATISFIED, output.evaluation_result)

    def test_a02_e2_rejects_full_target_environment_claim(self):
        output = self.gate.evaluate_gate(
            self.gate_input(
                evidence_level="E2",
                required_evidence_level="E2",
                claim_strength="FULL_TARGET_ENVIRONMENT",
            )
        )
        self.assertIs(GateEvaluationResult.REQUIREMENT_UNSATISFIED, output.evaluation_result)
        self.assertIn("CLAIM_EXCEEDS_EVIDENCE", output.evaluation_reason)

    def test_a03_e3_rejects_representative_stability_claim(self):
        output = self.gate.evaluate_gate(
            self.gate_input(
                evidence_level="E3",
                required_evidence_level="E3",
                claim_strength="REPRESENTATIVE_STABILITY",
            )
        )
        self.assertIs(GateEvaluationResult.REQUIREMENT_UNSATISFIED, output.evaluation_result)
        self.assertIn("CLAIM_EXCEEDS_EVIDENCE", output.evaluation_reason)

    def test_a04_evidence_scope_must_cover_claim_scope(self):
        output = self.gate.evaluate_gate(
            self.gate_input(
                evidence_level="E3",
                required_evidence_level="E3",
                evidence_scope=["scene-a"],
                claim_scope=["scene-a", "scene-b"],
            )
        )
        self.assertIs(GateEvaluationResult.EVIDENCE_INSUFFICIENT, output.evaluation_result)
        self.assertIn("EVIDENCE_SCOPE_MISMATCH", output.evaluation_reason)

    def test_a05_counterevidence_can_lower_confidence_without_changing_decision(self):
        decisions = "# Decision D-1\nStatus: ACTIVE\n"
        (self.root / "PROJECT_DECISIONS.md").write_text(decisions, encoding="utf-8")
        target = AccessTarget(ContextType.CAPABILITY_SPIRAL_RECORD)
        result = ContextCoordinator(FileStore(self.root)).handle(
            ContextAccessRequest(
                request_id="a05",
                access_target=target,
                access_type=AccessType.EXECUTE_MUTATION,
                request_source=RequestSource.RUNTIME,
                access_purpose="persist confidence downgrade",
                mutation_intent=MutationIntent(
                    mutation_type=MutationType.UPDATE_CONTEXT,
                    target_context=target,
                    change_purpose="persist confidence downgrade",
                    change_basis="COUNTEREVIDENCE",
                    proposed_content="claim_id: claim-1\nconfidence: LOW\nevidence_ref: E-9\n",
                    execute_eligibility_granted=True,
                ),
            )
        )
        self.assertIs(ContextAccessResultStatus.ACCEPTED, result.status)
        self.assertIn("confidence: LOW", (self.root / "CAPABILITY_SPIRAL_RECORD.md").read_text(encoding="utf-8"))
        self.assertEqual(decisions, (self.root / "PROJECT_DECISIONS.md").read_text(encoding="utf-8"))

    def test_a06_script_reports_structural_not_semantic_drift(self):
        request = ScriptInvocationRequest("a06", "fixture", "VALIDATION")
        structural = ScriptCoordinator().consume_script_output(
            request,
            {
                "execution_status": "COMPLETED",
                "validation_result": "REQUIREMENT_SATISFIED",
                "evidence": [{
                    "structural_drift": True,
                    "evaluated_scope": "artifact",
                    "artifact_refs": ["artifact-1"],
                    "limitations": ["semantic drift requires Agent judgment"],
                    "delivery_metadata": {},
                }],
            },
        )
        semantic = ScriptCoordinator().consume_script_output(
            request,
            {
                "execution_status": "COMPLETED",
                "validation_result": "REQUIREMENT_SATISFIED",
                "semantic_drift": True,
            },
        )
        agent_fixture = AdvisoryBridge().prepare(
            AdvisoryBridgeRequest(
                request_id="a06-agent",
                event_type="evidence advisory",
                reason_code="SEMANTIC_DRIFT_DETECTED",
                drift_refs=("agent-semantic-drift-1",),
            )
        )
        self.assertIs(RuntimeExecutionState.COMPLETED, structural.runtime_state)
        self.assertEqual(SCRIPT_EVIDENCE_BOUNDARY_VIOLATION, semantic.result_reason)
        self.assertEqual(("agent-semantic-drift-1",), agent_fixture.advisory_context_packets[0].drift_refs)


if __name__ == "__main__":
    unittest.main()
