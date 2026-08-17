import unittest

from PROJECT_INCUBATOR.runtime.core.contracts import (
    ContextAccessResultStatus,
    GateEvaluationResult,
    ScriptExecutionStatus,
    ScriptValidationResult,
    WorkflowResultStatus,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class ContractProjectionTest(unittest.TestCase):
    def test_runtime_execution_state_set_is_frozen(self):
        self.assertEqual(
            {
                "EXECUTING",
                "WAITING_FOR_MAKER",
                "BLOCKED_BY_GATE",
                "SUSPENDED",
                "FAILED",
                "COMPLETED",
            },
            {state.value for state in RuntimeExecutionState},
        )

    def test_contract_result_sets_are_frozen(self):
        self.assertEqual(
            {
                "ACCEPTED",
                "REJECTED",
                "AUTHORIZATION_REQUIRED",
                "GATE_REQUIREMENT_UNRESOLVED",
                "BOUNDARY_VIOLATION",
                "CONTEXT_CONFLICT",
            },
            {status.value for status in ContextAccessResultStatus},
        )
        self.assertEqual(
            {
                "NOT_READY",
                "READY_FOR_TRANSITION",
                "TRANSITION_NOT_ALLOWED",
            },
            {status.value for status in WorkflowResultStatus},
        )
        self.assertEqual(
            {
                "REQUIREMENT_SATISFIED",
                "REQUIREMENT_UNSATISFIED",
                "AUTHORIZATION_REQUIRED",
                "EVIDENCE_INSUFFICIENT",
                "ACTION_BLOCKED",
            },
            {result.value for result in GateEvaluationResult},
        )
        self.assertEqual(
            {
                "COMPLETED",
                "INVALID_INPUT",
                "UNSUPPORTED_INVOCATION",
                "EXECUTION_ERROR",
            },
            {status.value for status in ScriptExecutionStatus},
        )
        self.assertEqual(
            {
                "REQUIREMENT_SATISFIED",
                "REQUIREMENT_UNSATISFIED",
                "VALIDATION_NOT_COMPLETED",
            },
            {result.value for result in ScriptValidationResult},
        )


if __name__ == "__main__":
    unittest.main()
