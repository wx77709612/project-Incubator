import unittest
from types import SimpleNamespace

from PROJECT_INCUBATOR.runtime.components.script_coordinator import (
    EVIDENCE_READY,
    VALIDATION_NOT_COMPLETED,
    VALIDATION_UNSATISFIED,
    ScriptCoordinator,
    ScriptInvocationRequest,
)
from PROJECT_INCUBATOR.runtime.core.contracts import (
    ScriptExecutionStatus,
    ScriptValidationResult,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class FakeRunner:
    def __init__(self, output):
        self.output = output

    def run(self, script_identity, payload):
        return SimpleNamespace(output=self.output)


class ScriptCoordinatorTest(unittest.TestCase):
    def test_invalid_script_result_becomes_validation_not_completed(self):
        coordinator = ScriptCoordinator(
            script_runner=FakeRunner(
                {
                    "execution_status": "COMPLETED",
                    "validation_result": "NOT_A_VALID_RESULT",
                },
            ),
        )

        result = coordinator.invoke(
            ScriptInvocationRequest(
                invocation_id="invalid-result",
                script_identity="fake",
                invocation_purpose="VALIDATION",
            ),
        )

        self.assertIs(result.runtime_state, RuntimeExecutionState.SUSPENDED)
        self.assertIs(
            result.validation_result,
            ScriptValidationResult.VALIDATION_NOT_COMPLETED,
        )
        self.assertEqual(VALIDATION_NOT_COMPLETED, result.result_reason)

    def test_validation_unsatisfied_is_suspended_not_execution_error(self):
        coordinator = ScriptCoordinator(
            script_runner=FakeRunner(
                {
                    "execution_status": "COMPLETED",
                    "validation_result": "REQUIREMENT_UNSATISFIED",
                },
            ),
        )

        result = coordinator.invoke(
            ScriptInvocationRequest(
                invocation_id="validation-unsatisfied",
                script_identity="fake",
                invocation_purpose="VALIDATION",
            ),
        )

        self.assertIs(result.execution_status, ScriptExecutionStatus.COMPLETED)
        self.assertIs(
            result.validation_result,
            ScriptValidationResult.REQUIREMENT_UNSATISFIED,
        )
        self.assertIs(result.runtime_state, RuntimeExecutionState.SUSPENDED)
        self.assertEqual(VALIDATION_UNSATISFIED, result.result_reason)

    def test_pure_deterministic_operation_keeps_empty_validation_result(self):
        coordinator = ScriptCoordinator(
            script_runner=FakeRunner(
                {
                    "execution_status": "COMPLETED",
                    "validation_result": "",
                    "evidence": [{"operation": "done"}],
                },
            ),
        )

        result = coordinator.invoke(
            ScriptInvocationRequest(
                invocation_id="pure-operation",
                script_identity="fake",
                invocation_purpose="DETERMINISTIC_OPERATION",
                validation_requirement={},
            ),
        )

        self.assertIs(result.runtime_state, RuntimeExecutionState.COMPLETED)
        self.assertIsNone(result.validation_result)
        self.assertEqual(EVIDENCE_READY, result.result_reason)


if __name__ == "__main__":
    unittest.main()
