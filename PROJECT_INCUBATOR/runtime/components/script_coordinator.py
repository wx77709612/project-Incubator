"""Script invocation coordination for Project Incubator V1 runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from PROJECT_INCUBATOR.runtime.adapters.script_runner import (
    ScriptIdentityResolutionError,
    ScriptOutputParseError,
    ScriptRunner,
    ScriptRunnerError,
)
from PROJECT_INCUBATOR.runtime.core.contracts import (
    ScriptExecutionStatus,
    ScriptValidationResult,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


VALIDATION_UNSATISFIED = "VALIDATION_UNSATISFIED"
VALIDATION_NOT_COMPLETED = "VALIDATION_NOT_COMPLETED"
INVALID_SCRIPT_INPUT = "INVALID_SCRIPT_INPUT"
UNSUPPORTED_SCRIPT_INVOCATION = "UNSUPPORTED_SCRIPT_INVOCATION"
SCRIPT_EXECUTION_ERROR = "SCRIPT_EXECUTION_ERROR"
EVIDENCE_READY = "EVIDENCE_READY"


@dataclass(frozen=True)
class ScriptInvocationRequest:
    invocation_id: str
    script_identity: str
    invocation_purpose: str
    input_data: dict[str, Any] = field(default_factory=dict)
    context_reference: dict[str, Any] | None = None
    artifact_reference: dict[str, Any] | str | None = None
    validation_requirement: dict[str, Any] | str | None = None
    execution_parameter: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScriptInvocationResult:
    invocation_id: str
    script_identity: str
    runtime_state: RuntimeExecutionState
    result_reason: str
    execution_status: ScriptExecutionStatus | None = None
    validation_result: ScriptValidationResult | None = None
    evidence: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    diagnostic_information: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    error_information: dict[str, Any] | None = None
    script_output: dict[str, Any] | None = None


class ScriptCoordinator:
    """Prepares Script Input, invokes scripts, and maps Script Result for Runtime use."""

    supported_invocation_purposes = {
        "VALIDATION",
        "DETERMINISTIC_OPERATION",
    }

    def __init__(self, script_runner: ScriptRunner | None = None) -> None:
        self.script_runner = script_runner or ScriptRunner()

    def invoke(self, request: ScriptInvocationRequest) -> ScriptInvocationResult:
        input_check = self._validate_invocation_request(request)
        if input_check is not None:
            return input_check

        payload = self.prepare_script_input(request)
        try:
            process_result = self.script_runner.run(request.script_identity, payload)
        except ScriptIdentityResolutionError as exc:
            return self._runtime_result(
                request=request,
                runtime_state=RuntimeExecutionState.SUSPENDED,
                result_reason=UNSUPPORTED_SCRIPT_INVOCATION,
                error_information=self._error_information(
                    "UNSUPPORTED_INVOCATION",
                    str(exc),
                    "script_identity",
                ),
            )
        except (ScriptOutputParseError, ScriptRunnerError) as exc:
            return self._runtime_result(
                request=request,
                runtime_state=RuntimeExecutionState.FAILED,
                result_reason=SCRIPT_EXECUTION_ERROR,
                error_information=self._error_information(
                    SCRIPT_EXECUTION_ERROR,
                    str(exc),
                    "script_output",
                ),
            )

        return self.consume_script_output(request, process_result.output)

    def prepare_script_input(self, request: ScriptInvocationRequest) -> dict[str, Any]:
        payload = {
            "invocation_id": request.invocation_id,
            "script_identity": request.script_identity,
            "invocation_purpose": request.invocation_purpose,
            "input_data": dict(request.input_data),
            "context_reference": request.context_reference,
            "artifact_reference": request.artifact_reference,
            "validation_requirement": request.validation_requirement,
            "execution_parameter": dict(request.execution_parameter),
        }

        # Compatibility surface for existing deterministic scripts in TASK-016 through TASK-019.
        payload.update(request.input_data)
        if request.artifact_reference is not None:
            payload["artifact_reference"] = request.artifact_reference
        if request.validation_requirement is not None:
            payload["expected_requirement"] = request.validation_requirement
        return payload

    def consume_script_output(
        self,
        request: ScriptInvocationRequest,
        script_output: dict[str, Any],
    ) -> ScriptInvocationResult:
        execution_status = self._parse_execution_status(script_output)
        validation_result = self._parse_validation_result(script_output)
        evidence = self._tuple_of_dicts(script_output.get("evidence"))
        diagnostic_information = self._tuple_of_dicts(
            script_output.get("diagnostic_information"),
        )
        error_information = script_output.get("error_information")
        if error_information is not None and not isinstance(error_information, dict):
            error_information = {
                "error_type": SCRIPT_EXECUTION_ERROR,
                "error_reason": "script error_information must be an object or null",
                "related_input_reference": "error_information",
                "diagnostic_information": "invalid script output shape",
            }

        if execution_status is ScriptExecutionStatus.COMPLETED:
            if validation_result is ScriptValidationResult.REQUIREMENT_SATISFIED:
                return self._runtime_result(
                    request,
                    RuntimeExecutionState.COMPLETED,
                    EVIDENCE_READY,
                    execution_status,
                    validation_result,
                    evidence,
                    diagnostic_information,
                    error_information,
                    script_output,
                )
            if validation_result is ScriptValidationResult.REQUIREMENT_UNSATISFIED:
                return self._runtime_result(
                    request,
                    RuntimeExecutionState.SUSPENDED,
                    VALIDATION_UNSATISFIED,
                    execution_status,
                    validation_result,
                    evidence,
                    diagnostic_information,
                    error_information,
                    script_output,
                )
            return self._runtime_result(
                request,
                RuntimeExecutionState.SUSPENDED,
                VALIDATION_NOT_COMPLETED,
                execution_status,
                validation_result,
                evidence,
                diagnostic_information,
                error_information,
                script_output,
            )

        if execution_status is ScriptExecutionStatus.INVALID_INPUT:
            return self._runtime_result(
                request,
                RuntimeExecutionState.SUSPENDED,
                INVALID_SCRIPT_INPUT,
                execution_status,
                validation_result,
                evidence,
                diagnostic_information,
                error_information,
                script_output,
            )
        if execution_status is ScriptExecutionStatus.UNSUPPORTED_INVOCATION:
            return self._runtime_result(
                request,
                RuntimeExecutionState.SUSPENDED,
                UNSUPPORTED_SCRIPT_INVOCATION,
                execution_status,
                validation_result,
                evidence,
                diagnostic_information,
                error_information,
                script_output,
            )
        return self._runtime_result(
            request,
            RuntimeExecutionState.FAILED,
            SCRIPT_EXECUTION_ERROR,
            execution_status,
            validation_result,
            evidence,
            diagnostic_information,
            error_information,
            script_output,
        )

    def _validate_invocation_request(
        self,
        request: ScriptInvocationRequest,
    ) -> ScriptInvocationResult | None:
        if not request.invocation_id:
            return self._runtime_result(
                request,
                RuntimeExecutionState.SUSPENDED,
                INVALID_SCRIPT_INPUT,
                error_information=self._error_information(
                    "INVALID_INPUT",
                    "invocation_id is required",
                    "invocation_id",
                ),
            )
        if not request.script_identity:
            return self._runtime_result(
                request,
                RuntimeExecutionState.SUSPENDED,
                INVALID_SCRIPT_INPUT,
                error_information=self._error_information(
                    "INVALID_INPUT",
                    "script_identity is required",
                    "script_identity",
                ),
            )
        if request.invocation_purpose not in self.supported_invocation_purposes:
            return self._runtime_result(
                request,
                RuntimeExecutionState.SUSPENDED,
                UNSUPPORTED_SCRIPT_INVOCATION,
                error_information=self._error_information(
                    "UNSUPPORTED_INVOCATION",
                    "invocation_purpose is not supported",
                    "invocation_purpose",
                ),
            )
        return None

    @staticmethod
    def _parse_execution_status(script_output: dict[str, Any]) -> ScriptExecutionStatus:
        value = script_output.get("execution_status")
        try:
            return ScriptExecutionStatus(value)
        except ValueError:
            return ScriptExecutionStatus.EXECUTION_ERROR

    @staticmethod
    def _parse_validation_result(script_output: dict[str, Any]) -> ScriptValidationResult:
        value = script_output.get("validation_result")
        try:
            return ScriptValidationResult(value)
        except ValueError:
            return ScriptValidationResult.VALIDATION_NOT_COMPLETED

    @staticmethod
    def _tuple_of_dicts(value: Any) -> tuple[dict[str, Any], ...]:
        if not isinstance(value, list):
            return ()
        return tuple(item for item in value if isinstance(item, dict))

    @staticmethod
    def _runtime_result(
        request: ScriptInvocationRequest,
        runtime_state: RuntimeExecutionState,
        result_reason: str,
        execution_status: ScriptExecutionStatus | None = None,
        validation_result: ScriptValidationResult | None = None,
        evidence: tuple[dict[str, Any], ...] = (),
        diagnostic_information: tuple[dict[str, Any], ...] = (),
        error_information: dict[str, Any] | None = None,
        script_output: dict[str, Any] | None = None,
    ) -> ScriptInvocationResult:
        return ScriptInvocationResult(
            invocation_id=request.invocation_id,
            script_identity=request.script_identity,
            runtime_state=runtime_state,
            result_reason=result_reason,
            execution_status=execution_status,
            validation_result=validation_result,
            evidence=evidence,
            diagnostic_information=diagnostic_information,
            error_information=error_information,
            script_output=script_output,
        )

    @staticmethod
    def _error_information(
        error_type: str,
        reason: str,
        related_input_reference: str | None,
    ) -> dict[str, Any]:
        return {
            "error_type": error_type,
            "error_reason": reason,
            "related_input_reference": related_input_reference,
            "diagnostic_information": reason,
        }


__all__ = [
    "EVIDENCE_READY",
    "INVALID_SCRIPT_INPUT",
    "SCRIPT_EXECUTION_ERROR",
    "UNSUPPORTED_SCRIPT_INVOCATION",
    "VALIDATION_NOT_COMPLETED",
    "VALIDATION_UNSATISFIED",
    "ScriptCoordinator",
    "ScriptInvocationRequest",
    "ScriptInvocationResult",
]
