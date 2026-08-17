import unittest

from PROJECT_INCUBATOR.runtime.components.advisory_bridge import (
    RECOMMENDED_ACTION_REQUIRES_RUNTIME_REQUEST,
    AdvisoryBridge,
    AdvisoryBridgeRequest,
    AdvisoryResponse,
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


if __name__ == "__main__":
    unittest.main()
