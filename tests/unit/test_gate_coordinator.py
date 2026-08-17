import unittest

from PROJECT_INCUBATOR.runtime.components.gate_coordinator import (
    GateCoordinator,
    GateInvocationRequest,
)
from PROJECT_INCUBATOR.runtime.core.contracts import GateEvaluationResult
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class GateCoordinatorTest(unittest.TestCase):
    def setUp(self):
        self.coordinator = GateCoordinator()

    def test_gate_block_maps_to_blocked_by_gate(self):
        result = self.coordinator.invoke(
            GateInvocationRequest(
                invocation_id="gate-block",
                trigger_event="commit",
                requested_action="commit",
                requested_gate_ids=("GATE-GIT",),
                evaluation_evidence=(
                    {
                        "gate_id": "GATE-GIT",
                        "gate_result": "REQUIREMENT_UNSATISFIED",
                    },
                ),
            ),
        )

        self.assertIs(
            result.aggregate_gate_result,
            GateEvaluationResult.REQUIREMENT_UNSATISFIED,
        )
        self.assertIs(result.runtime_state, RuntimeExecutionState.BLOCKED_BY_GATE)
        self.assertFalse(result.can_continue_contract_check)

    def test_maker_authorization_is_not_auto_supplied(self):
        result = self.coordinator.invoke(
            GateInvocationRequest(
                invocation_id="auth-missing",
                trigger_event="push",
                requested_action="push",
                requested_gate_ids=("GATE-GIT",),
                evaluation_evidence=(
                    {
                        "gate_id": "GATE-GIT",
                        "gate_result": "REQUIREMENT_SATISFIED",
                    },
                ),
            ),
        )

        self.assertIs(
            result.aggregate_gate_result,
            GateEvaluationResult.AUTHORIZATION_REQUIRED,
        )
        self.assertIs(result.runtime_state, RuntimeExecutionState.WAITING_FOR_MAKER)

    def test_script_validation_evidence_does_not_replace_gate_result(self):
        result = self.coordinator.invoke(
            GateInvocationRequest(
                invocation_id="judgment-gate",
                trigger_event="scope change",
                requested_gate_ids=("GATE-SCOPE",),
                validation_evidence_reference=(
                    {
                        "gate_id": "GATE-SCOPE",
                        "script_validation_result": "REQUIREMENT_SATISFIED",
                    },
                ),
            ),
        )

        self.assertIs(
            result.aggregate_gate_result,
            GateEvaluationResult.EVIDENCE_INSUFFICIENT,
        )


if __name__ == "__main__":
    unittest.main()
