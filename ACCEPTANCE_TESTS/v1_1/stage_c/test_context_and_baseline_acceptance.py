import shutil
import unittest
from pathlib import Path

from PROJECT_INCUBATOR.runtime.adapters.file_store import FileStore, FileWriteError
from PROJECT_INCUBATOR.runtime.components.context_coordinator import (
    AccessTarget,
    AccessType,
    AuthorizationEvidence,
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
from PROJECT_INCUBATOR.runtime.core.contracts import (
    ContextAccessResultStatus,
    GateEvaluationResult,
)
from PROJECT_INCUBATOR.runtime.core.coordinator import RuntimeCoordinator, RuntimeRequest
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class FailingActiveViewFileStore(FileStore):
    def atomic_write(self, path, content):
        if Path(path).name == "PROJECT_DECISIONS.md":
            raise FileWriteError("injected active view failure")
        return super().atomic_write(path, content)


class ContextAndBaselineAcceptance(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent / ".tmp_context_baseline_acceptance"
        shutil.rmtree(self.root, ignore_errors=True)
        self.root.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def request_mutation(self, intent, source=RequestSource.AGENT):
        return ContextCoordinator(FileStore(self.root)).handle(
            ContextAccessRequest(
                request_id="context-acceptance",
                access_target=intent.target_context,
                access_type=AccessType.REQUEST_MUTATION,
                request_source=source,
                access_purpose=intent.change_purpose,
                mutation_intent=intent,
            )
        )

    def test_c01_evidence_invalidates_assumption_without_fake_maker_authorization(self):
        target = AccessTarget(ContextType.CAPABILITY_SPIRAL_RECORD)
        result = self.request_mutation(
            MutationIntent(
                mutation_type=MutationType.UPDATE_ASSUMPTION_STATUS,
                target_context=target,
                change_purpose="invalidate assumption",
                change_basis="EVIDENCE_ASSUMPTION_INVALIDATION",
                proposed_content="Assumption A-1: INVALIDATED",
                assumption_id="A-1",
                target_status="INVALIDATED",
                effective_scope="cap-1",
                evidence_refs=("E-4",),
                dependent_artifact_refs=("design.md",),
            )
        )
        self.assertIs(ContextAccessResultStatus.ACCEPTED, result.status)

    def test_c02_product_decision_supersession_requires_maker_authorization(self):
        target = AccessTarget(ContextType.PROJECT_DECISIONS)
        intent = MutationIntent(
            mutation_type=MutationType.SUPERSEDE_DECISION,
            target_context=target,
            change_purpose="supersede product decision",
            change_basis="NEW_EVIDENCE",
            proposed_content="Decision D-2 supersedes D-1",
            decision_id="D-2",
            target_status="ACTIVE",
            effective_scope="product",
            affected_decision_refs=("D-1",),
            gate_evidence_reference="authority-gate",
        )
        rejected = self.request_mutation(intent)
        accepted = self.request_mutation(
            MutationIntent(
                **{
                    **intent.__dict__,
                    "maker_authorization": AuthorizationEvidence(RequestSource.MAKER, True, "maker-1"),
                }
            )
        )
        self.assertIs(ContextAccessResultStatus.AUTHORIZATION_REQUIRED, rejected.status)
        self.assertIs(ContextAccessResultStatus.ACCEPTED, accepted.status)

    def test_c03_decision_archive_is_verified_before_active_view_changes(self):
        original = "# Decision D-1\nStatus: ACTIVE\n"
        active = "# Decision D-1\nStatus: SUPERSEDED\nArchive Ref: PROJECT_DECISION_HISTORY.md\n"
        history = "# Decision D-1\nStatus: SUPERSEDED\nNew Evidence: E-7\n"
        (self.root / "PROJECT_DECISIONS.md").write_text(original, encoding="utf-8")
        result = ContextCoordinator(FileStore(self.root)).execute_decision_archive(active, history)
        self.assertIs(ContextAccessResultStatus.ACCEPTED, result.status)
        self.assertEqual(history, (self.root / "PROJECT_DECISION_HISTORY.md").read_text(encoding="utf-8"))
        self.assertEqual(active, (self.root / "PROJECT_DECISIONS.md").read_text(encoding="utf-8"))

    def test_c04_archive_failure_preserves_original_active_view(self):
        original = "# Decision D-1\nStatus: ACTIVE\n"
        active = "# Decision D-1\nStatus: SUPERSEDED\nArchive Ref: PROJECT_DECISION_HISTORY.md\n"
        history = "# Decision D-1\nStatus: SUPERSEDED\n"
        (self.root / "PROJECT_DECISIONS.md").write_text(original, encoding="utf-8")
        result = ContextCoordinator(FailingActiveViewFileStore(self.root)).execute_decision_archive(active, history)
        self.assertIs(ContextAccessResultStatus.REJECTED, result.status)
        self.assertEqual(original, (self.root / "PROJECT_DECISIONS.md").read_text(encoding="utf-8"))

    def test_c05_baseline_pass_to_fail_is_regressed_and_action_blocked(self):
        evidence = {
            "baseline_status": "REGRESSED",
            "baseline_previous_result": "PASS",
            "baseline_current_result": "FAIL",
        }
        gate_input = GateInput(
            GateInvocationReference("c05", "GATE-ARTIFACT-BOUNDARY", "baseline", "continue"),
            "GATE-ARTIFACT-BOUNDARY",
            "Artifact Boundary Gate",
            "Evidence-Based",
            "baseline",
            ("Baseline",),
            "continue",
            ("No regression",),
            None,
            {"phase_id": "P4"},
            None,
            (evidence,),
            (),
            (),
            (),
            (),
            "continue",
            "continue",
            None,
        )
        output = GateCoordinator().evaluate_gate(gate_input)
        self.assertEqual("REGRESSED", evidence["baseline_status"])
        self.assertIs(GateEvaluationResult.ACTION_BLOCKED, output.evaluation_result)
        self.assertIn("BASELINE_REGRESSION", output.evaluation_reason)

    def test_c06_missing_optional_context_does_not_break_legacy_route(self):
        (self.root / "PROJECT_STATE.md").write_text("Current Phase: P1\n", encoding="utf-8")
        result = RuntimeCoordinator().execute(
            RuntimeRequest("c06", "contract check", self.root)
        )
        self.assertIs(RuntimeExecutionState.COMPLETED, result.runtime_execution_state)
        self.assertFalse((self.root / "CAPABILITY_SPIRAL_RECORD.md").exists())

    def test_c07_optional_context_cannot_override_core_authority(self):
        target = AccessTarget(ContextType.CAPABILITY_SPIRAL_RECORD)
        result = self.request_mutation(
            MutationIntent(
                mutation_type=MutationType.UPDATE_CONTEXT,
                target_context=target,
                change_purpose="override current phase",
                change_basis="EXTENSION_UPDATE",
                proposed_content="Current Phase: P6",
                overrides_core_context_authority=True,
            )
        )
        self.assertIs(ContextAccessResultStatus.BOUNDARY_VIOLATION, result.status)


if __name__ == "__main__":
    unittest.main()
