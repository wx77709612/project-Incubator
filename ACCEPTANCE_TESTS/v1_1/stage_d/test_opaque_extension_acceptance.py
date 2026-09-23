import copy
import shutil
import unittest
from pathlib import Path

from PROJECT_INCUBATOR.runtime.adapters.file_store import FileStore
from PROJECT_INCUBATOR.runtime.components.advisory_bridge import AdvisoryBridge, AdvisoryBridgeRequest
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
from PROJECT_INCUBATOR.runtime.components.definition_resolver import DefinitionResolver
from PROJECT_INCUBATOR.runtime.components.workflow_coordinator import (
    WorkflowCoordinator,
    WorkflowDefinitionError,
)
from PROJECT_INCUBATOR.runtime.core.contracts import ContextAccessResultStatus
from PROJECT_INCUBATOR.runtime.core.evidence_types import OpacityLevel, extension_recommended


class OpaqueExtensionAcceptance(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent / ".tmp_opaque_extension_acceptance"
        shutil.rmtree(self.root, ignore_errors=True)
        self.root.mkdir(parents=True)
        (self.root / "PROJECT_STATE.md").write_text("Current Phase: P4\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def workflow_with_thresholds(self, advisory, correction):
        definition = copy.deepcopy(
            DefinitionResolver().load_frozen_definition_set().workflow_definition
        )
        p4 = next(p for p in definition["workflow"]["phases"] if p["phase_id"] == "P4")
        p4["correction_policy"]["advisory_threshold"] = advisory
        p4["correction_policy"]["correction_threshold"] = correction
        return definition

    def test_d01_any_high_dimension_recommends_but_does_not_enable_extension(self):
        recommended = extension_recommended([OpacityLevel.LOW, OpacityLevel.HIGH])
        advisory = AdvisoryBridge().prepare(
            AdvisoryBridgeRequest(
                request_id="d01",
                event_type="evidence advisory",
                reason_code="OPAQUE_EXTENSION_RECOMMENDED",
            )
        )
        self.assertTrue(recommended)
        self.assertTrue(advisory.advisory_context_packets)
        self.assertFalse((self.root / "CAPABILITY_SPIRAL_RECORD.md").exists())

    def test_d02_two_elevated_dimensions_recommend_extension(self):
        self.assertTrue(
            extension_recommended([OpacityLevel.ELEVATED, OpacityLevel.ELEVATED])
        )

    def test_d03_missing_maker_cost_confirmation_does_not_create_spiral_record(self):
        target = AccessTarget(ContextType.CAPABILITY_SPIRAL_RECORD)
        intent = MutationIntent(
            mutation_type=MutationType.CREATE_CONTEXT,
            target_context=target,
            change_purpose="enable opaque capability extension",
            change_basis="OPAQUE_EXTENSION_RECOMMENDATION",
            proposed_content="capability_id: cap-1\n",
            execute_eligibility_granted=True,
        )
        result = ContextCoordinator(FileStore(self.root)).handle(
            ContextAccessRequest(
                request_id="d03",
                access_target=target,
                access_type=AccessType.EXECUTE_MUTATION,
                request_source=RequestSource.RUNTIME,
                access_purpose="enable extension",
                mutation_intent=intent,
            )
        )
        self.assertIs(ContextAccessResultStatus.AUTHORIZATION_REQUIRED, result.status)
        self.assertFalse((self.root / "CAPABILITY_SPIRAL_RECORD.md").exists())

    def test_d04_maker_confirmation_creates_optional_record_without_phase_change(self):
        target = AccessTarget(ContextType.CAPABILITY_SPIRAL_RECORD)
        result = ContextCoordinator(FileStore(self.root)).handle(
            ContextAccessRequest(
                request_id="d04",
                access_target=target,
                access_type=AccessType.EXECUTE_MUTATION,
                request_source=RequestSource.RUNTIME,
                access_purpose="enable extension",
                mutation_intent=MutationIntent(
                    mutation_type=MutationType.CREATE_CONTEXT,
                    target_context=target,
                    change_purpose="enable opaque capability extension",
                    change_basis="MAKER_CONFIRMED_EXTENSION_COST",
                    proposed_content="capability_id: cap-1\nclaim_status: HYPOTHESIZED\n",
                    maker_authorization=AuthorizationEvidence(
                        RequestSource.MAKER,
                        True,
                        "maker-confirmed-cost-boundary",
                    ),
                    execute_eligibility_granted=True,
                ),
            )
        )
        self.assertIs(ContextAccessResultStatus.ACCEPTED, result.status)
        self.assertTrue((self.root / "CAPABILITY_SPIRAL_RECORD.md").exists())
        self.assertIn("Current Phase: P4", (self.root / "PROJECT_STATE.md").read_text(encoding="utf-8"))

    def test_d05_relaxed_three_four_thresholds_fail_definition_loading(self):
        with self.assertRaises(WorkflowDefinitionError):
            WorkflowCoordinator(self.workflow_with_thresholds(3, 4))

    def test_d06_stricter_one_two_thresholds_are_accepted(self):
        coordinator = WorkflowCoordinator(self.workflow_with_thresholds(1, 2))
        self.assertEqual((1, 2), coordinator.correction_thresholds)

    def test_d07_exhausted_budget_stops_repeating_same_test(self):
        result = AdvisoryBridge().prepare(
            AdvisoryBridgeRequest(
                request_id="d07",
                event_type="evidence advisory",
                reason_code="HUMAN_VALIDATION_BUDGET_EXHAUSTED",
                human_validation_budget_refs=("budget-exhausted-no-new-evidence",),
            )
        )
        packet = result.advisory_context_packets[0]
        self.assertEqual("MISSING_INFORMATION", packet.trigger.trigger_id)
        self.assertEqual(("budget-exhausted-no-new-evidence",), packet.human_validation_budget_refs)
        self.assertFalse(result.runtime_state_changed)

    def test_d08_transparent_capability_does_not_require_extension_artifact(self):
        self.assertFalse(extension_recommended([OpacityLevel.LOW] * 8))
        self.assertFalse((self.root / "CAPABILITY_SPIRAL_RECORD.md").exists())


if __name__ == "__main__":
    unittest.main()
