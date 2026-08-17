"""Full Runtime Coordinator for Project Incubator V1."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable

from PROJECT_INCUBATOR.runtime.adapters.file_store import FileStore
from PROJECT_INCUBATOR.runtime.components.advisory_bridge import (
    AdvisoryBridge,
    AdvisoryBridgeRequest,
)
from PROJECT_INCUBATOR.runtime.components.context_coordinator import (
    AccessTarget,
    AccessType,
    ContextAccessRequest,
    ContextAccessResult,
    ContextCoordinator,
    ContextType,
    MutationIntent,
    RequestSource,
)
from PROJECT_INCUBATOR.runtime.components.definition_resolver import DefinitionResolver
from PROJECT_INCUBATOR.runtime.components.gate_coordinator import (
    GateCoordinationResult,
    GateCoordinator,
    GateInvocationRequest,
)
from PROJECT_INCUBATOR.runtime.components.result_coordinator import (
    RuntimeResult,
    RuntimeResultCoordinator,
)
from PROJECT_INCUBATOR.runtime.components.script_coordinator import (
    ScriptCoordinator,
    ScriptInvocationRequest,
    ScriptInvocationResult,
    VALIDATION_UNSATISFIED,
)
from PROJECT_INCUBATOR.runtime.components.workflow_coordinator import (
    CurrentPhaseReference,
    PhaseResult,
    TransitionEligibilityResult,
    WorkflowCoordinator,
    WorkflowDefinitionError,
)
from PROJECT_INCUBATOR.runtime.core.contracts import (
    ContextAccessResultStatus,
    ScriptExecutionStatus,
    ScriptValidationResult,
    WorkflowResultStatus,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


RUNTIME_COMPLETED = "RUNTIME_COMPLETED"
UNSUPPORTED_RUNTIME_CONDITION = "UNSUPPORTED_RUNTIME_CONDITION"
MISSING_CONTEXT = "MISSING_CONTEXT"
INVALID_WORKFLOW_STATE = "INVALID_WORKFLOW_STATE"
WORKFLOW_NOT_READY = "WORKFLOW_NOT_READY"
TRANSITION_NOT_ALLOWED = "TRANSITION_NOT_ALLOWED"
CONTEXT_ACCESS_NOT_ACCEPTED = "CONTEXT_ACCESS_NOT_ACCEPTED"
CONTEXT_CONFLICT = "CONTEXT_CONFLICT"
CONTEXT_PERSISTENCE_VERIFICATION_FAILED = "CONTEXT_PERSISTENCE_VERIFICATION_FAILED"
RUNTIME_DEPENDENCY_FAILURE = "RUNTIME_DEPENDENCY_FAILURE"
SCRIPT_EXECUTION_NOT_COMPLETED = "SCRIPT_EXECUTION_NOT_COMPLETED"


class RuntimeCoordinatorError(Exception):
    """Raised when Runtime Coordinator cannot execute within frozen runtime rules."""


@dataclass(frozen=True)
class RuntimeRequest:
    request_id: str
    requested_action: str
    project_root: str | Path
    request_kind: str = "RUNTIME_REQUEST"
    existing_project: bool = True
    new_project_bootstrap: bool = False
    project_state_reference: str | Path = "PROJECT_STATE.md"
    phase_result: PhaseResult | None = None
    context_mutation_intents: tuple[MutationIntent, ...] = field(default_factory=tuple)
    gate_trigger_event: str | None = None
    requested_gate_ids: tuple[str, ...] = field(default_factory=tuple)
    gate_evaluation_evidence: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    gate_validation_evidence: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    gate_judgment_evidence: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    maker_authorization_evidence: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    script_invocation_requests: tuple[ScriptInvocationRequest, ...] = field(default_factory=tuple)
    advisory_request: AdvisoryBridgeRequest | None = None
    completed_action_reference: Any | None = None
    next_allowed_action: tuple[Any, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RuntimeExecutionTrace:
    context_access_results: tuple[ContextAccessResult, ...] = field(default_factory=tuple)
    script_results: tuple[ScriptInvocationResult, ...] = field(default_factory=tuple)
    gate_result: GateCoordinationResult | None = None
    workflow_result: TransitionEligibilityResult | None = None
    advisory_result: Any | None = None


class RuntimeCoordinator:
    """Coordinates the fixed V1 runtime lifecycle without adding domain rules."""

    allowed_request_kinds = {
        "RUNTIME_REQUEST",
        "CONTRACT_CHECK",
        "CONTEXT_MUTATION",
        "PHASE_TRANSITION",
        "SCRIPT_INVOCATION",
        "GATE_EVALUATION",
        "ADVISORY_PREPARATION",
    }

    def __init__(
        self,
        definition_resolver: DefinitionResolver | None = None,
        workflow_coordinator: WorkflowCoordinator | None = None,
        gate_coordinator: GateCoordinator | None = None,
        script_coordinator: ScriptCoordinator | None = None,
        advisory_bridge: AdvisoryBridge | None = None,
        result_coordinator: RuntimeResultCoordinator | None = None,
        context_coordinator_factory: Callable[[FileStore], ContextCoordinator] | None = None,
    ) -> None:
        self.definition_resolver = definition_resolver or DefinitionResolver()
        self.workflow_coordinator = workflow_coordinator or WorkflowCoordinator(
            definition_resolver=self.definition_resolver,
        )
        self.gate_coordinator = gate_coordinator or GateCoordinator(
            definition_resolver=self.definition_resolver,
        )
        self.script_coordinator = script_coordinator or ScriptCoordinator()
        self.advisory_bridge = advisory_bridge or AdvisoryBridge(
            definition_resolver=self.definition_resolver,
        )
        self.result_coordinator = result_coordinator or RuntimeResultCoordinator(
            definition_resolver=self.definition_resolver,
        )
        self.context_coordinator_factory = (
            context_coordinator_factory or (lambda file_store: ContextCoordinator(file_store))
        )

    def invoke(self, request: RuntimeRequest) -> RuntimeResult:
        return self.execute(request)

    def execute(self, request: RuntimeRequest) -> RuntimeResult:
        trace = RuntimeExecutionTrace()
        current_phase: CurrentPhaseReference | None = None

        definition_check = self.definition_resolver.resolve()
        if definition_check.runtime_state is not RuntimeExecutionState.COMPLETED:
            return self._form_result(
                request=request,
                state=RuntimeExecutionState.FAILED,
                reason=RUNTIME_DEPENDENCY_FAILURE,
                trace=trace,
                pending_requirement=(definition_check.missing_requirement,),
            )

        unsupported_reason = self._validate_requested_action(request)
        if unsupported_reason is not None:
            return self._form_result(
                request=request,
                state=RuntimeExecutionState.SUSPENDED,
                reason=UNSUPPORTED_RUNTIME_CONDITION,
                trace=trace,
                pending_requirement=(unsupported_reason,),
            )

        file_store = FileStore(request.project_root)
        context_coordinator = self.context_coordinator_factory(file_store)
        project_state_exists = file_store.exists(request.project_state_reference)
        state_read = self._read_project_state(request, context_coordinator)
        trace = self._with_context_result(trace, state_read)

        if not project_state_exists and request.existing_project and not request.new_project_bootstrap:
            return self._form_result(
                request=request,
                state=RuntimeExecutionState.SUSPENDED,
                reason=MISSING_CONTEXT,
                trace=trace,
                pending_requirement=("PROJECT_STATE.md",),
            )

        if project_state_exists:
            try:
                current_phase = self._resolve_current_phase_from_project_state(
                    state_read.content or "",
                )
            except WorkflowDefinitionError as exc:
                return self._form_result(
                    request=request,
                    state=RuntimeExecutionState.SUSPENDED,
                    reason=INVALID_WORKFLOW_STATE,
                    trace=trace,
                    pending_requirement=(str(exc),),
                )
        elif request.new_project_bootstrap:
            current_phase = self._bootstrap_phase_reference()

        if request.advisory_request is not None:
            advisory_result = self.advisory_bridge.prepare(request.advisory_request)
            trace = replace(trace, advisory_result=advisory_result)

        phase_input = None
        if current_phase is not None:
            phase_input = self.workflow_coordinator.prepare_phase_input(current_phase.phase_id)

        script_results = self._invoke_scripts(request)
        trace = replace(trace, script_results=script_results)
        script_stop = self._script_stop_result(request, trace)
        if script_stop is not None:
            return script_stop

        gate_result = self._invoke_gate_if_required(request, current_phase, phase_input, script_results)
        if gate_result is not None:
            trace = replace(trace, gate_result=gate_result)
            if not gate_result.can_continue_contract_check:
                return self._form_result(
                    request=request,
                    state=gate_result.runtime_state,
                    reason=gate_result.result_reason,
                    current_phase_reference=current_phase,
                    trace=trace,
                    pending_requirement=self._gate_pending_requirements(gate_result),
                    required_maker_input=self._maker_input_for_gate(gate_result),
                )

        mutation_preflight_results = self._prepare_context_mutations(
            request,
            context_coordinator,
        )
        trace = replace(
            trace,
            context_access_results=trace.context_access_results + mutation_preflight_results,
        )
        context_stop = self._context_stop_result(request, current_phase, trace)
        if context_stop is not None:
            return context_stop

        if request.phase_result is not None:
            workflow_result = self._evaluate_workflow_transition(request)
            trace = replace(trace, workflow_result=workflow_result)
            if workflow_result.status is WorkflowResultStatus.NOT_READY:
                return self._form_result(
                    request=request,
                    state=RuntimeExecutionState.SUSPENDED,
                    reason=WORKFLOW_NOT_READY,
                    current_phase_reference=current_phase,
                    trace=trace,
                    pending_requirement=workflow_result.missing_requirements,
                )
            if workflow_result.status is WorkflowResultStatus.TRANSITION_NOT_ALLOWED:
                return self._form_result(
                    request=request,
                    state=RuntimeExecutionState.SUSPENDED,
                    reason=TRANSITION_NOT_ALLOWED,
                    current_phase_reference=current_phase,
                    trace=trace,
                    pending_requirement=workflow_result.missing_requirements,
                )

        execution_results = self._execute_context_mutations(
            request,
            context_coordinator,
        )
        trace = replace(
            trace,
            context_access_results=trace.context_access_results + execution_results,
        )
        context_stop = self._context_stop_result(request, current_phase, trace)
        if context_stop is not None:
            return context_stop

        verification_stop = self._verify_transition_commit(
            request,
            current_phase,
            trace,
            context_coordinator,
        )
        if verification_stop is not None:
            return verification_stop

        completed_action = request.completed_action_reference
        if execution_results:
            completed_action = tuple(result.persisted_result for result in execution_results)

        return self._form_result(
            request=request,
            state=RuntimeExecutionState.COMPLETED,
            reason=RUNTIME_COMPLETED,
            current_phase_reference=self._current_phase_after_execution(
                request,
                current_phase,
                context_coordinator,
            ),
            trace=trace,
            completed_action_reference=completed_action,
            next_allowed_action=request.next_allowed_action,
        )

    def _validate_requested_action(self, request: RuntimeRequest) -> str | None:
        if request.request_kind not in self.allowed_request_kinds:
            return f"unsupported request_kind: {request.request_kind}"
        if not request.request_id:
            return "Runtime Request requires request_id"
        if not request.requested_action:
            return "Runtime Request requires requested_action"
        return None

    def _read_project_state(
        self,
        request: RuntimeRequest,
        context_coordinator: ContextCoordinator,
    ) -> ContextAccessResult:
        return context_coordinator.handle(
            ContextAccessRequest(
                request_id=f"{request.request_id}:read-project-state",
                access_target=AccessTarget(
                    context_type=ContextType.PROJECT_STATE,
                    context_reference=request.project_state_reference,
                ),
                access_type=AccessType.READ,
                request_source=RequestSource.RUNTIME,
                access_purpose="Resolve Current Phase from PROJECT_STATE.md",
            ),
        )

    def _resolve_current_phase_from_project_state(self, content: str) -> CurrentPhaseReference:
        project_state = self._parse_project_state_content(content)
        return self.workflow_coordinator.resolve_current_phase(project_state)

    def _parse_project_state_content(self, content: str) -> dict[str, Any]:
        current_phase = self._heading_value(content, "Current Phase")
        current_phase_state = self._heading_value(content, "Current Phase State")
        if current_phase is None:
            current_phase = self._colon_value(content, "Current Phase")
        if current_phase_state is None:
            current_phase_state = self._colon_value(content, "Current Phase State")
        return {
            "Current Phase": current_phase,
            "Current Phase State": current_phase_state,
        }

    def _bootstrap_phase_reference(self) -> CurrentPhaseReference:
        phase_input = self.workflow_coordinator.prepare_phase_input("P0")
        return CurrentPhaseReference(
            phase_id=phase_input.phase_id,
            phase_name=phase_input.phase_name,
            phase_state="P0_BOOTSTRAP_RUNTIME_REFERENCE",
        )

    def _invoke_scripts(self, request: RuntimeRequest) -> tuple[ScriptInvocationResult, ...]:
        return tuple(
            self.script_coordinator.invoke(script_request)
            for script_request in request.script_invocation_requests
        )

    def _script_stop_result(
        self,
        request: RuntimeRequest,
        trace: RuntimeExecutionTrace,
    ) -> RuntimeResult | None:
        for script_result in trace.script_results:
            if script_result.runtime_state is RuntimeExecutionState.FAILED:
                return self._form_result(
                    request=request,
                    state=RuntimeExecutionState.FAILED,
                    reason=script_result.result_reason,
                    trace=trace,
                    pending_requirement=(script_result.error_information,),
                )
            if script_result.runtime_state is RuntimeExecutionState.SUSPENDED:
                if (
                    script_result.execution_status is ScriptExecutionStatus.COMPLETED
                    and script_result.validation_result
                    is ScriptValidationResult.REQUIREMENT_UNSATISFIED
                ):
                    return self._form_result(
                        request=request,
                        state=RuntimeExecutionState.SUSPENDED,
                        reason=VALIDATION_UNSATISFIED,
                        trace=trace,
                        pending_requirement=(script_result.result_reason,),
                    )
                return self._form_result(
                    request=request,
                    state=RuntimeExecutionState.SUSPENDED,
                    reason=SCRIPT_EXECUTION_NOT_COMPLETED,
                    trace=trace,
                    pending_requirement=(script_result.result_reason,),
                )
        return None

    def _invoke_gate_if_required(
        self,
        request: RuntimeRequest,
        current_phase: CurrentPhaseReference | None,
        phase_input: Any | None,
        script_results: tuple[ScriptInvocationResult, ...],
    ) -> GateCoordinationResult | None:
        if not (
            request.gate_trigger_event
            or request.requested_gate_ids
            or request.gate_evaluation_evidence
            or request.gate_validation_evidence
            or request.gate_judgment_evidence
        ):
            return None

        gate_request = GateInvocationRequest(
            invocation_id=f"{request.request_id}:gate",
            trigger_event=request.gate_trigger_event or request.requested_action,
            requested_action=request.requested_action,
            requested_gate_ids=request.requested_gate_ids,
            current_context_reference={"source": "PROJECT_STATE.md"},
            current_workflow_phase_reference=current_phase,
            workflow_requirement_reference=phase_input,
            evaluation_evidence=request.gate_evaluation_evidence,
            validation_evidence_reference=request.gate_validation_evidence,
            judgment_evidence=request.gate_judgment_evidence,
            maker_authorization_evidence=request.maker_authorization_evidence,
            script_invocation_results=script_results,
        )
        return self.gate_coordinator.invoke(gate_request)

    def _prepare_context_mutations(
        self,
        request: RuntimeRequest,
        context_coordinator: ContextCoordinator,
    ) -> tuple[ContextAccessResult, ...]:
        return tuple(
            context_coordinator.handle(
                ContextAccessRequest(
                    request_id=f"{request.request_id}:prepare-context:{index}",
                    access_target=intent.target_context,
                    access_type=AccessType.REQUEST_MUTATION,
                    request_source=RequestSource.RUNTIME,
                    access_purpose=intent.change_purpose,
                    mutation_intent=intent,
                ),
            )
            for index, intent in enumerate(self._state_last_intents(request.context_mutation_intents))
        )

    def _execute_context_mutations(
        self,
        request: RuntimeRequest,
        context_coordinator: ContextCoordinator,
    ) -> tuple[ContextAccessResult, ...]:
        return tuple(
            context_coordinator.handle(
                ContextAccessRequest(
                    request_id=f"{request.request_id}:execute-context:{index}",
                    access_target=intent.target_context,
                    access_type=AccessType.EXECUTE_MUTATION,
                    request_source=RequestSource.RUNTIME,
                    access_purpose=intent.change_purpose,
                    mutation_intent=replace(intent, execute_eligibility_granted=True),
                ),
            )
            for index, intent in enumerate(self._state_last_intents(request.context_mutation_intents))
        )

    def _context_stop_result(
        self,
        request: RuntimeRequest,
        current_phase: CurrentPhaseReference | None,
        trace: RuntimeExecutionTrace,
    ) -> RuntimeResult | None:
        for context_result in trace.context_access_results:
            if context_result.status is ContextAccessResultStatus.ACCEPTED:
                continue
            if context_result.status is ContextAccessResultStatus.AUTHORIZATION_REQUIRED:
                return self._form_result(
                    request=request,
                    state=RuntimeExecutionState.WAITING_FOR_MAKER,
                    reason=context_result.decision_reason,
                    current_phase_reference=current_phase,
                    trace=trace,
                    pending_requirement=(context_result.authorization_requirement,),
                    required_maker_input=(context_result.authorization_requirement,),
                )
            if context_result.status is ContextAccessResultStatus.GATE_REQUIREMENT_UNRESOLVED:
                return self._form_result(
                    request=request,
                    state=RuntimeExecutionState.BLOCKED_BY_GATE,
                    reason=context_result.decision_reason,
                    current_phase_reference=current_phase,
                    trace=trace,
                    pending_requirement=(context_result.gate_requirement_reference,),
                )
            if context_result.status is ContextAccessResultStatus.CONTEXT_CONFLICT:
                return self._form_result(
                    request=request,
                    state=RuntimeExecutionState.SUSPENDED,
                    reason=CONTEXT_CONFLICT,
                    current_phase_reference=current_phase,
                    trace=trace,
                    pending_requirement=(
                        context_result.conflict_reference
                        or context_result.decision_reason,
                    ),
                )
            return self._form_result(
                request=request,
                state=RuntimeExecutionState.SUSPENDED,
                reason=CONTEXT_ACCESS_NOT_ACCEPTED,
                current_phase_reference=current_phase,
                trace=trace,
                pending_requirement=(
                    context_result.missing_requirement
                    or context_result.boundary_reference
                    or context_result.conflict_reference
                    or context_result.decision_reason,
                ),
            )
        return None

    def _evaluate_workflow_transition(
        self,
        request: RuntimeRequest,
    ) -> TransitionEligibilityResult:
        assert request.phase_result is not None
        transition_request = self.workflow_coordinator.create_transition_request(
            f"{request.request_id}:workflow-transition",
            request.phase_result,
        )
        return self.workflow_coordinator.evaluate_transition(transition_request)

    def _verify_transition_commit(
        self,
        request: RuntimeRequest,
        current_phase: CurrentPhaseReference | None,
        trace: RuntimeExecutionTrace,
        context_coordinator: ContextCoordinator,
    ) -> RuntimeResult | None:
        if trace.workflow_result is None or request.phase_result is None:
            return None
        if trace.workflow_result.status is not WorkflowResultStatus.READY_FOR_TRANSITION:
            return None

        project_state_writes = tuple(
            result
            for result in trace.context_access_results
            if result.requested_access_type is AccessType.EXECUTE_MUTATION
            and result.access_target.context_type is ContextType.PROJECT_STATE
        )
        if not project_state_writes:
            return self._form_result(
                request=request,
                state=RuntimeExecutionState.SUSPENDED,
                reason=CONTEXT_PERSISTENCE_VERIFICATION_FAILED,
                current_phase_reference=current_phase,
                trace=trace,
                pending_requirement=("PROJECT_STATE.md transition commit",),
            )

        if not all(result.persisted_result_verified for result in project_state_writes):
            return self._form_result(
                request=request,
                state=RuntimeExecutionState.FAILED,
                reason=CONTEXT_PERSISTENCE_VERIFICATION_FAILED,
                current_phase_reference=current_phase,
                trace=trace,
                pending_requirement=("PROJECT_STATE.md persisted verification",),
            )

        state_read = self._read_project_state(request, context_coordinator)
        updated_trace = self._with_context_result(trace, state_read)
        try:
            persisted_phase = self._resolve_current_phase_from_project_state(
                state_read.content or "",
            )
        except WorkflowDefinitionError as exc:
            return self._form_result(
                request=request,
                state=RuntimeExecutionState.FAILED,
                reason=CONTEXT_PERSISTENCE_VERIFICATION_FAILED,
                current_phase_reference=current_phase,
                trace=updated_trace,
                pending_requirement=(str(exc),),
            )

        if persisted_phase.phase_id != request.phase_result.requested_next_phase:
            return self._form_result(
                request=request,
                state=RuntimeExecutionState.FAILED,
                reason=CONTEXT_PERSISTENCE_VERIFICATION_FAILED,
                current_phase_reference=persisted_phase,
                trace=updated_trace,
                pending_requirement=("Persisted Current Phase does not match Requested Next Phase",),
            )
        return None

    def _current_phase_after_execution(
        self,
        request: RuntimeRequest,
        fallback_phase: CurrentPhaseReference | None,
        context_coordinator: ContextCoordinator,
    ) -> CurrentPhaseReference | None:
        if not any(
            intent.target_context.context_type is ContextType.PROJECT_STATE
            for intent in request.context_mutation_intents
        ):
            return fallback_phase
        state_read = self._read_project_state(request, context_coordinator)
        if state_read.status is not ContextAccessResultStatus.ACCEPTED:
            return fallback_phase
        try:
            return self._resolve_current_phase_from_project_state(state_read.content or "")
        except WorkflowDefinitionError:
            return fallback_phase

    def _form_result(
        self,
        request: RuntimeRequest,
        state: RuntimeExecutionState,
        reason: str,
        trace: RuntimeExecutionTrace,
        current_phase_reference: CurrentPhaseReference | None = None,
        pending_requirement: tuple[Any, ...] = (),
        required_maker_input: tuple[Any, ...] = (),
        completed_action_reference: Any | None = None,
        next_allowed_action: tuple[Any, ...] = (),
    ) -> RuntimeResult:
        return self.result_coordinator.create_result(
            execution_reference=request.request_id,
            runtime_execution_state=state,
            runtime_reason=reason,
            current_phase_reference=current_phase_reference,
            workflow_result_reference=trace.workflow_result,
            context_access_result_reference=trace.context_access_results,
            gate_output_reference=trace.gate_result,
            script_output_reference=trace.script_results,
            pending_requirement=self._compact_tuple(pending_requirement),
            required_maker_input=self._compact_tuple(required_maker_input),
            completed_action_reference=completed_action_reference,
            next_allowed_action=tuple(next_allowed_action),
        )

    def _gate_pending_requirements(
        self,
        gate_result: GateCoordinationResult,
    ) -> tuple[Any, ...]:
        pending: list[Any] = []
        for output in gate_result.gate_outputs:
            pending.extend(output.unsatisfied_requirement)
        return tuple(pending)

    def _maker_input_for_gate(
        self,
        gate_result: GateCoordinationResult,
    ) -> tuple[Any, ...]:
        if gate_result.runtime_state is not RuntimeExecutionState.WAITING_FOR_MAKER:
            return ()
        return self._gate_pending_requirements(gate_result)

    @staticmethod
    def _with_context_result(
        trace: RuntimeExecutionTrace,
        context_result: ContextAccessResult,
    ) -> RuntimeExecutionTrace:
        return replace(
            trace,
            context_access_results=trace.context_access_results + (context_result,),
        )

    @staticmethod
    def _state_last_intents(
        intents: tuple[MutationIntent, ...],
    ) -> tuple[MutationIntent, ...]:
        return tuple(
            sorted(
                intents,
                key=lambda intent: intent.target_context.context_type is ContextType.PROJECT_STATE,
            ),
        )

    @staticmethod
    def _heading_value(content: str, heading_name: str) -> str | None:
        lines = content.splitlines()
        normalized_heading = heading_name.casefold()
        in_section = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                heading_text = stripped.lstrip("#").strip()
                if in_section:
                    return None
                in_section = heading_text.casefold().startswith(normalized_heading)
                continue
            if not in_section or not stripped or stripped.startswith("<!--"):
                continue
            if stripped.startswith("-"):
                continue
            return stripped
        return None

    @staticmethod
    def _colon_value(content: str, field_name: str) -> str | None:
        prefix = f"{field_name}:"
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.casefold().startswith(prefix.casefold()):
                value = stripped[len(prefix) :].strip()
                return value or None
        return None

    @staticmethod
    def _compact_tuple(values: tuple[Any, ...]) -> tuple[Any, ...]:
        return tuple(value for value in values if value is not None)


__all__ = [
    "CONTEXT_ACCESS_NOT_ACCEPTED",
    "CONTEXT_CONFLICT",
    "CONTEXT_PERSISTENCE_VERIFICATION_FAILED",
    "INVALID_WORKFLOW_STATE",
    "MISSING_CONTEXT",
    "RUNTIME_COMPLETED",
    "RUNTIME_DEPENDENCY_FAILURE",
    "SCRIPT_EXECUTION_NOT_COMPLETED",
    "TRANSITION_NOT_ALLOWED",
    "UNSUPPORTED_RUNTIME_CONDITION",
    "WORKFLOW_NOT_READY",
    "RuntimeCoordinator",
    "RuntimeCoordinatorError",
    "RuntimeExecutionTrace",
    "RuntimeRequest",
]
