import unittest

from PROJECT_INCUBATOR.runtime.components.advisory_bridge import (
    RECOMMENDED_ACTION_REQUIRES_RUNTIME_REQUEST,
    AdvisoryBridge,
    AdvisoryBridgeRequest,
    AdvisoryResponse,
    AdvisoryDefinitionError,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class AdvisoryBridgeTest(unittest.TestCase):
    def setUp(self):
        self.bridge = AdvisoryBridge()

    def test_all_core_triggers_are_loaded(self):
        self.assertEqual(
            (
                "PHASE_ENTRY",
                "MAKER_GUIDANCE_REQUEST",
                "MISSING_INFORMATION",
                "RISK_DETECTED",
                "DECISION_REQUIRED",
                "VALIDATION_FEEDBACK",
                "ITERATION_RE_ENTRY",
            ),
            tuple(self.bridge.triggers_by_id),
        )

    def test_prepares_context_for_trigger(self):
        result = self.bridge.prepare(
            AdvisoryBridgeRequest(
                request_id="advisory",
                event_type="Validation Feedback",
                current_phase={"phase_id": "P5"},
                project_context={"Project Type": "tool"},
                validation_result={"status": "gap"},
                missing_information=("acceptance evidence",),
            ),
        )

        self.assertFalse(result.runtime_state_changed)
        self.assertIn(
            "VALIDATION_FEEDBACK",
            tuple(trigger.trigger_id for trigger in result.matched_triggers),
        )
        self.assertEqual(
            {"Project Type": "tool"},
            result.advisory_context_packets[-1].project_context,
        )

    def test_recommended_action_requires_new_runtime_request(self):
        handled = self.bridge.consume_advisory_response(
            AdvisoryResponse(
                request_id="response",
                trigger_id="VALIDATION_FEEDBACK",
                recommended_action=("revise artifact",),
            ),
            RuntimeExecutionState.SUSPENDED,
        )

        self.assertIs(handled.runtime_state, RuntimeExecutionState.SUSPENDED)
        self.assertFalse(handled.runtime_state_changed)
        self.assertEqual(
            RECOMMENDED_ACTION_REQUIRES_RUNTIME_REQUEST,
            handled.result_reason,
        )
        self.assertEqual(1, len(handled.pending_runtime_requests))

    def test_v1_1_reason_codes_use_existing_triggers(self):
        expected_triggers = {
            "REPEATED_FAILURE_WARNING": "RISK_DETECTED",
            "MODEL_REVIEW_REQUIRED": "RISK_DETECTED",
            "KNOWN_GOOD_REGRESSION": "VALIDATION_FEEDBACK",
            "SEMANTIC_DRIFT_DETECTED": "RISK_DETECTED",
            "OPAQUE_EXTENSION_RECOMMENDED": "RISK_DETECTED",
            "HUMAN_VALIDATION_BUDGET_EXHAUSTED": "MISSING_INFORMATION",
            "MAKER_SCOPE_REVIEW_REQUIRED": "DECISION_REQUIRED",
        }

        for reason_code, trigger_id in expected_triggers.items():
            with self.subTest(reason_code=reason_code):
                result = self.bridge.prepare(
                    AdvisoryBridgeRequest(
                        request_id=reason_code,
                        event_type="evidence advisory",
                        reason_code=reason_code,
                    )
                )
                self.assertEqual((trigger_id,), tuple(t.trigger_id for t in result.matched_triggers))

    def test_context_packet_contains_bounded_evidence_references(self):
        result = self.bridge.prepare(
            AdvisoryBridgeRequest(
                request_id="bounded-context",
                event_type="evidence advisory",
                reason_code="KNOWN_GOOD_REGRESSION",
                claim_refs=("claim-1",),
                evidence_refs=("evidence-3",),
                failure_refs=("failure-2",),
                baseline_refs=("baseline-1",),
                drift_refs=("drift-1",),
                human_validation_budget_refs=("budget-1",),
            )
        )

        packet = result.advisory_context_packets[0]
        self.assertEqual(("claim-1",), packet.claim_refs)
        self.assertEqual(("evidence-3",), packet.evidence_refs)
        self.assertEqual(("failure-2",), packet.failure_refs)
        self.assertEqual(("baseline-1",), packet.baseline_refs)
        self.assertEqual(("drift-1",), packet.drift_refs)
        self.assertEqual(("budget-1",), packet.human_validation_budget_refs)

    def test_unknown_reason_code_is_rejected(self):
        with self.assertRaises(AdvisoryDefinitionError):
            self.bridge.prepare(
                AdvisoryBridgeRequest(
                    request_id="unknown",
                    event_type="evidence advisory",
                    reason_code="NOT_APPROVED",
                )
            )


if __name__ == "__main__":
    unittest.main()
