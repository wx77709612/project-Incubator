import unittest
from types import SimpleNamespace
from pathlib import Path
import shutil

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
from PROJECT_INCUBATOR.scripts.validate_artifact_evidence import validate_artifact_evidence


class FakeRunner:
    def __init__(self, output):
        self.output = output

    def run(self, script_identity, payload):
        return SimpleNamespace(output=self.output)


class ScriptCoordinatorTest(unittest.TestCase):
    def evidence_request(self):
        return ScriptInvocationRequest(
            invocation_id="evidence-boundary",
            script_identity="fake",
            invocation_purpose="VALIDATION",
            validation_requirement={"requirement_id": "artifact-check"},
        )

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

    def test_structural_drift_evidence_is_accepted(self):
        result = ScriptCoordinator().consume_script_output(
            self.evidence_request(),
            {
                "execution_status": "COMPLETED",
                "validation_result": "REQUIREMENT_SATISFIED",
                "evidence": [
                    {
                        "structural_drift": True,
                        "evaluated_scope": "artifact-package",
                        "artifact_refs": ["artifact-1"],
                        "limitations": ["semantic meaning not evaluated"],
                        "delivery_metadata": {"version": "1"},
                    }
                ],
            },
        )

        self.assertIs(RuntimeExecutionState.COMPLETED, result.runtime_state)
        self.assertTrue(result.evidence[0]["structural_drift"])

    def test_script_authority_claims_are_rejected(self):
        forbidden_outputs = (
            {"semantic_drift": True},
            {"extension_activation": "ENABLED"},
            {"maker_authorization": True},
            {"evidence_level": "E4"},
        )

        for forbidden in forbidden_outputs:
            with self.subTest(forbidden=forbidden):
                result = ScriptCoordinator().consume_script_output(
                    self.evidence_request(),
                    {
                        "execution_status": "COMPLETED",
                        "validation_result": "REQUIREMENT_SATISFIED",
                        **forbidden,
                    },
                )
                self.assertIs(RuntimeExecutionState.SUSPENDED, result.runtime_state)
                self.assertEqual("SCRIPT_EVIDENCE_BOUNDARY_VIOLATION", result.result_reason)

    def test_artifact_validator_emits_scoped_delivery_evidence(self):
        directory = Path(__file__).parent / ".tmp_script_evidence"
        shutil.rmtree(directory, ignore_errors=True)
        directory.mkdir(parents=True)
        try:
            artifact_path = directory / "artifact.bin"
            artifact_path.write_bytes(b"content")

            output = validate_artifact_evidence(
                {
                    "invocation_id": "artifact-evidence",
                    "artifact_reference": {"artifact_id": "artifact-1"},
                    "expected_requirement": {"requirement_id": "delivery-check"},
                    "artifact_path": str(artifact_path),
                    "evaluated_scope": "delivery-package",
                    "limitations": ["runtime semantics not evaluated"],
                    "delivery_metadata": {"package_version": "1.1"},
                }
            )
        finally:
            shutil.rmtree(directory, ignore_errors=True)

        evidence = output["evidence"][0]
        self.assertEqual("delivery-package", evidence["evaluated_scope"])
        self.assertEqual(["artifact-1"], evidence["artifact_refs"])
        self.assertEqual(["runtime semantics not evaluated"], evidence["limitations"])
        self.assertEqual("1.1", evidence["delivery_metadata"]["package_version"])
        self.assertEqual(7, evidence["delivery_metadata"]["size_bytes"])


if __name__ == "__main__":
    unittest.main()
