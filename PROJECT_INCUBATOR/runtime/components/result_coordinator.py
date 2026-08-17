"""Runtime Result formation for Project Incubator V1 runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from PROJECT_INCUBATOR.runtime.components.definition_resolver import DefinitionResolver
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


RUNTIME_RESULT_READY = "RUNTIME_RESULT_READY"
INVALID_RUNTIME_RESULT_INPUT = "INVALID_RUNTIME_RESULT_INPUT"


class RuntimeResultError(Exception):
    """Raised when a Runtime Result cannot be formed from valid runtime input."""


@dataclass(frozen=True)
class RuntimeResultInput:
    execution_reference: str
    runtime_execution_state: RuntimeExecutionState
    runtime_reason: str
    current_phase_reference: Any | None = None
    workflow_result_reference: Any | None = None
    context_access_result_reference: Any | None = None
    gate_output_reference: Any | None = None
    script_output_reference: Any | None = None
    pending_requirement: tuple[Any, ...] = field(default_factory=tuple)
    required_maker_input: tuple[Any, ...] = field(default_factory=tuple)
    completed_action_reference: Any | None = None
    next_allowed_action: tuple[Any, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RuntimeResult:
    execution_reference: str
    runtime_execution_state: RuntimeExecutionState
    runtime_reason: str
    current_phase_reference: Any | None
    workflow_result_reference: Any | None
    context_access_result_reference: Any | None
    gate_output_reference: Any | None
    script_output_reference: Any | None
    pending_requirement: tuple[Any, ...]
    required_maker_input: tuple[Any, ...]
    completed_action_reference: Any | None
    next_allowed_action: tuple[Any, ...]
    result_reason: str = RUNTIME_RESULT_READY


class RuntimeResultCoordinator:
    """Builds stable Runtime Result summaries without reinterpreting Contract Results."""

    def __init__(
        self,
        definition_resolver: DefinitionResolver | None = None,
    ) -> None:
        self.runtime_state_type = self._load_runtime_state_type(definition_resolver)
        self._validate_runtime_state_set()

    def form_result(self, result_input: RuntimeResultInput) -> RuntimeResult:
        self._validate_result_input(result_input)
        return RuntimeResult(
            execution_reference=result_input.execution_reference,
            runtime_execution_state=result_input.runtime_execution_state,
            runtime_reason=result_input.runtime_reason,
            current_phase_reference=result_input.current_phase_reference,
            workflow_result_reference=result_input.workflow_result_reference,
            context_access_result_reference=result_input.context_access_result_reference,
            gate_output_reference=result_input.gate_output_reference,
            script_output_reference=result_input.script_output_reference,
            pending_requirement=tuple(result_input.pending_requirement),
            required_maker_input=tuple(result_input.required_maker_input),
            completed_action_reference=result_input.completed_action_reference,
            next_allowed_action=tuple(result_input.next_allowed_action),
        )

    def create_result(
        self,
        execution_reference: str,
        runtime_execution_state: RuntimeExecutionState,
        runtime_reason: str,
        current_phase_reference: Any | None = None,
        workflow_result_reference: Any | None = None,
        context_access_result_reference: Any | None = None,
        gate_output_reference: Any | None = None,
        script_output_reference: Any | None = None,
        pending_requirement: tuple[Any, ...] = (),
        required_maker_input: tuple[Any, ...] = (),
        completed_action_reference: Any | None = None,
        next_allowed_action: tuple[Any, ...] = (),
    ) -> RuntimeResult:
        return self.form_result(
            RuntimeResultInput(
                execution_reference=execution_reference,
                runtime_execution_state=runtime_execution_state,
                runtime_reason=runtime_reason,
                current_phase_reference=current_phase_reference,
                workflow_result_reference=workflow_result_reference,
                context_access_result_reference=context_access_result_reference,
                gate_output_reference=gate_output_reference,
                script_output_reference=script_output_reference,
                pending_requirement=tuple(pending_requirement),
                required_maker_input=tuple(required_maker_input),
                completed_action_reference=completed_action_reference,
                next_allowed_action=tuple(next_allowed_action),
            ),
        )

    def validate_result(self, runtime_result: RuntimeResult) -> bool:
        return (
            isinstance(runtime_result.execution_reference, str)
            and bool(runtime_result.execution_reference)
            and isinstance(runtime_result.runtime_execution_state, self.runtime_state_type)
            and isinstance(runtime_result.runtime_reason, str)
            and bool(runtime_result.runtime_reason)
            and isinstance(runtime_result.pending_requirement, tuple)
            and isinstance(runtime_result.required_maker_input, tuple)
            and isinstance(runtime_result.next_allowed_action, tuple)
        )

    def _load_runtime_state_type(
        self,
        definition_resolver: DefinitionResolver | None,
    ) -> type[RuntimeExecutionState]:
        resolver = definition_resolver or DefinitionResolver()
        resolution = resolver.resolve()
        if (
            resolution.runtime_state is not RuntimeExecutionState.COMPLETED
            or resolution.frozen_definition_set is None
        ):
            missing = resolution.missing_requirement or "Runtime Contract Types"
            raise RuntimeResultError(missing)
        return resolution.frozen_definition_set.runtime_contract_types.runtime_execution_state

    def _validate_runtime_state_set(self) -> None:
        loaded_state_set = {state.value for state in self.runtime_state_type}
        implementation_state_set = {state.value for state in RuntimeExecutionState}
        if loaded_state_set != implementation_state_set:
            raise RuntimeResultError("Runtime Execution State set is not the frozen V1 set")

    def _validate_result_input(self, result_input: RuntimeResultInput) -> None:
        if not isinstance(result_input.execution_reference, str) or not result_input.execution_reference:
            raise RuntimeResultError("Execution Reference is required")
        if not isinstance(result_input.runtime_execution_state, self.runtime_state_type):
            raise RuntimeResultError("Runtime Execution State must use frozen runtime type")
        if not isinstance(result_input.runtime_reason, str) or not result_input.runtime_reason:
            raise RuntimeResultError("Runtime Reason is required")
        for field_name in (
            "pending_requirement",
            "required_maker_input",
            "next_allowed_action",
        ):
            value = getattr(result_input, field_name)
            if not isinstance(value, tuple):
                raise RuntimeResultError(f"{field_name} must be a tuple")


__all__ = [
    "INVALID_RUNTIME_RESULT_INPUT",
    "RUNTIME_RESULT_READY",
    "RuntimeResult",
    "RuntimeResultCoordinator",
    "RuntimeResultError",
    "RuntimeResultInput",
]
