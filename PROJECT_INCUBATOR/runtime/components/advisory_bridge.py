"""Advisory information bridge for Project Incubator V1 runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from PROJECT_INCUBATOR.runtime.components.definition_resolver import DefinitionResolver
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


ADVISORY_CONTEXT_READY = "ADVISORY_CONTEXT_READY"
NO_ADVISORY_TRIGGER = "NO_ADVISORY_TRIGGER"
RECOMMENDED_ACTION_REQUIRES_RUNTIME_REQUEST = (
    "RECOMMENDED_ACTION_REQUIRES_RUNTIME_REQUEST"
)
ADVISORY_RESPONSE_NO_RUNTIME_STATE_CHANGE = "ADVISORY_RESPONSE_NO_RUNTIME_STATE_CHANGE"

PHASE_ENTRY = "PHASE_ENTRY"
MAKER_GUIDANCE_REQUEST = "MAKER_GUIDANCE_REQUEST"
MISSING_INFORMATION = "MISSING_INFORMATION"
RISK_DETECTED = "RISK_DETECTED"
DECISION_REQUIRED = "DECISION_REQUIRED"
VALIDATION_FEEDBACK = "VALIDATION_FEEDBACK"
ITERATION_RE_ENTRY = "ITERATION_RE_ENTRY"


class AdvisoryDefinitionError(Exception):
    """Raised when frozen Advisory definitions cannot support runtime use."""


@dataclass(frozen=True)
class AdvisoryBridgeRequest:
    request_id: str
    event_type: str
    current_phase: dict[str, Any] | str | None = None
    project_context: dict[str, Any] = field(default_factory=dict)
    relevant_artifact: dict[str, Any] | str | None = None
    validation_result: dict[str, Any] | str | None = None
    risk: dict[str, Any] | str | None = None
    missing_information: tuple[str, ...] = field(default_factory=tuple)
    maker_guidance_request: str | None = None
    decision_required: dict[str, Any] | str | None = None
    iteration_reentry_target: str | None = None
    requested_trigger_ids: tuple[str, ...] = field(default_factory=tuple)
    source_context_references: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AdvisoryTriggerMatch:
    trigger_id: str
    trigger_name: str
    trigger_condition: str
    trigger_purpose: str


@dataclass(frozen=True)
class AdvisoryContextPacket:
    request_id: str
    trigger: AdvisoryTriggerMatch
    current_phase: dict[str, Any] | str | None
    project_context: dict[str, Any]
    relevant_artifact: dict[str, Any] | str | None
    validation_result: dict[str, Any] | str | None
    risk: dict[str, Any] | str | None
    missing_information: tuple[str, ...]
    decision_required: dict[str, Any] | str | None
    iteration_reentry_target: str | None
    source_context_references: tuple[str, ...]
    allowed_response_fields: tuple[str, ...]
    available_content_types: tuple[str, ...]
    advisory_boundary: tuple[str, ...]


@dataclass(frozen=True)
class AdvisoryBridgeResult:
    request_id: str
    matched_triggers: tuple[AdvisoryTriggerMatch, ...]
    advisory_context_packets: tuple[AdvisoryContextPacket, ...]
    result_reason: str
    runtime_state_changed: bool = False


@dataclass(frozen=True)
class AdvisoryResponse:
    request_id: str
    trigger_id: str
    advisory_summary: str | None = None
    identified_issue: tuple[str, ...] = field(default_factory=tuple)
    relevant_context: tuple[str, ...] = field(default_factory=tuple)
    missing_information: tuple[str, ...] = field(default_factory=tuple)
    risk_notice: tuple[str, ...] = field(default_factory=tuple)
    constraint_reminder: tuple[str, ...] = field(default_factory=tuple)
    decision_needed: tuple[str, ...] = field(default_factory=tuple)
    recommended_action: tuple[str, ...] = field(default_factory=tuple)
    required_clarification: tuple[str, ...] = field(default_factory=tuple)
    suggested_next_step: tuple[str, ...] = field(default_factory=tuple)
    project_type_guidance: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PendingRuntimeRequest:
    source_advisory_request_id: str
    trigger_id: str
    recommended_action_reference: str
    execution_requirement: str = RECOMMENDED_ACTION_REQUIRES_RUNTIME_REQUEST


@dataclass(frozen=True)
class AdvisoryResponseHandlingResult:
    request_id: str
    trigger_id: str
    runtime_state: RuntimeExecutionState
    runtime_state_changed: bool
    result_reason: str
    pending_runtime_requests: tuple[PendingRuntimeRequest, ...]


class AdvisoryBridge:
    """Exposes Advisory context without turning Advisory into runtime control."""

    frozen_core_trigger_ids = (
        PHASE_ENTRY,
        MAKER_GUIDANCE_REQUEST,
        MISSING_INFORMATION,
        RISK_DETECTED,
        DECISION_REQUIRED,
        VALIDATION_FEEDBACK,
        ITERATION_RE_ENTRY,
    )

    def __init__(
        self,
        advisory_definition: dict[str, Any] | None = None,
        definition_resolver: DefinitionResolver | None = None,
    ) -> None:
        self.advisory_definition = advisory_definition or self._load_advisory_definition(
            definition_resolver,
        )
        self.advisory_model = self._require_mapping(
            self.advisory_definition,
            "advisory_model",
        )
        self.triggers_by_id = self._load_trigger_map()
        self.content_types = self._load_content_types()
        self.response_fields = tuple(
            self._require_string_list(
                self._require_mapping(self.advisory_model, "response_model"),
                "possible_fields",
            ),
        )
        self.runtime_boundary = self._load_runtime_boundary()

    def prepare(self, request: AdvisoryBridgeRequest) -> AdvisoryBridgeResult:
        matched_triggers = self.identify_triggers(request)
        context_packets = tuple(
            self.prepare_advisory_context(request, trigger)
            for trigger in matched_triggers
        )
        result_reason = ADVISORY_CONTEXT_READY if context_packets else NO_ADVISORY_TRIGGER
        return AdvisoryBridgeResult(
            request_id=request.request_id,
            matched_triggers=matched_triggers,
            advisory_context_packets=context_packets,
            result_reason=result_reason,
            runtime_state_changed=False,
        )

    def identify_triggers(
        self,
        request: AdvisoryBridgeRequest,
    ) -> tuple[AdvisoryTriggerMatch, ...]:
        if request.requested_trigger_ids:
            return tuple(
                self._trigger_match(self.resolve_trigger_definition(trigger_id))
                for trigger_id in request.requested_trigger_ids
            )

        event_type = self._normalize_text(request.event_type)
        trigger_ids: list[str] = []
        if self._event_matches(event_type, PHASE_ENTRY, "phase entry") or (
            request.current_phase is not None and "phase" in event_type
        ):
            trigger_ids.append(PHASE_ENTRY)
        if self._event_matches(event_type, MAKER_GUIDANCE_REQUEST, "maker guidance") or (
            request.maker_guidance_request
        ):
            trigger_ids.append(MAKER_GUIDANCE_REQUEST)
        if self._event_matches(event_type, MISSING_INFORMATION, "missing information") or (
            request.missing_information
        ):
            trigger_ids.append(MISSING_INFORMATION)
        if self._event_matches(event_type, RISK_DETECTED, "risk detected") or (
            request.risk is not None
        ):
            trigger_ids.append(RISK_DETECTED)
        if self._event_matches(event_type, DECISION_REQUIRED, "decision required") or (
            request.decision_required is not None
        ):
            trigger_ids.append(DECISION_REQUIRED)
        if self._event_matches(event_type, VALIDATION_FEEDBACK, "validation feedback") or (
            request.validation_result is not None
        ):
            trigger_ids.append(VALIDATION_FEEDBACK)
        if self._event_matches(event_type, ITERATION_RE_ENTRY, "iteration re-entry") or (
            request.iteration_reentry_target is not None
        ):
            trigger_ids.append(ITERATION_RE_ENTRY)

        return tuple(
            self._trigger_match(self.resolve_trigger_definition(trigger_id))
            for trigger_id in self._dedupe(trigger_ids)
        )

    def resolve_trigger_definition(self, trigger_id: str) -> dict[str, Any]:
        trigger = self.triggers_by_id.get(trigger_id)
        if trigger is None:
            raise AdvisoryDefinitionError(f"unknown Advisory Trigger: {trigger_id}")
        return trigger

    def prepare_advisory_context(
        self,
        request: AdvisoryBridgeRequest,
        trigger: AdvisoryTriggerMatch,
    ) -> AdvisoryContextPacket:
        return AdvisoryContextPacket(
            request_id=request.request_id,
            trigger=trigger,
            current_phase=request.current_phase,
            project_context=dict(request.project_context),
            relevant_artifact=request.relevant_artifact,
            validation_result=request.validation_result,
            risk=request.risk,
            missing_information=tuple(request.missing_information),
            decision_required=request.decision_required,
            iteration_reentry_target=request.iteration_reentry_target,
            source_context_references=tuple(request.source_context_references),
            allowed_response_fields=self.response_fields,
            available_content_types=self.content_types,
            advisory_boundary=self.runtime_boundary,
        )

    def consume_advisory_response(
        self,
        response: AdvisoryResponse,
        current_runtime_state: RuntimeExecutionState,
    ) -> AdvisoryResponseHandlingResult:
        self.resolve_trigger_definition(response.trigger_id)
        pending_runtime_requests = self.pending_runtime_requests_for(response)
        result_reason = (
            RECOMMENDED_ACTION_REQUIRES_RUNTIME_REQUEST
            if pending_runtime_requests
            else ADVISORY_RESPONSE_NO_RUNTIME_STATE_CHANGE
        )
        return AdvisoryResponseHandlingResult(
            request_id=response.request_id,
            trigger_id=response.trigger_id,
            runtime_state=current_runtime_state,
            runtime_state_changed=False,
            result_reason=result_reason,
            pending_runtime_requests=pending_runtime_requests,
        )

    def pending_runtime_requests_for(
        self,
        response: AdvisoryResponse,
    ) -> tuple[PendingRuntimeRequest, ...]:
        action_references = response.recommended_action + response.suggested_next_step
        return tuple(
            PendingRuntimeRequest(
                source_advisory_request_id=response.request_id,
                trigger_id=response.trigger_id,
                recommended_action_reference=action_reference,
            )
            for action_reference in action_references
        )

    def _load_advisory_definition(
        self,
        definition_resolver: DefinitionResolver | None,
    ) -> dict[str, Any]:
        resolver = definition_resolver or DefinitionResolver()
        resolution = resolver.resolve()
        if (
            resolution.runtime_state is not RuntimeExecutionState.COMPLETED
            or resolution.frozen_definition_set is None
        ):
            missing = resolution.missing_requirement or "Advisory Definition"
            raise AdvisoryDefinitionError(missing)
        return resolution.frozen_definition_set.advisory_definition

    def _load_trigger_map(self) -> dict[str, dict[str, Any]]:
        triggers = self.advisory_model.get("core_triggers")
        if not isinstance(triggers, list):
            raise AdvisoryDefinitionError("core_triggers must be a list")

        trigger_map: dict[str, dict[str, Any]] = {}
        for trigger in triggers:
            if not isinstance(trigger, dict):
                raise AdvisoryDefinitionError("Advisory Trigger must be an object")
            trigger_id = self._require_string(trigger, "trigger_id")
            for required_key in (
                "trigger_name",
                "condition",
                "purpose",
            ):
                if required_key not in trigger:
                    raise AdvisoryDefinitionError(
                        f"Advisory Trigger missing field: {required_key}",
                    )
            trigger_map[trigger_id] = trigger

        if tuple(trigger_map) != self.frozen_core_trigger_ids:
            raise AdvisoryDefinitionError("Core Advisory Trigger set is not the frozen V1 set")
        return trigger_map

    def _load_content_types(self) -> tuple[str, ...]:
        content_types = self.advisory_model.get("content_types")
        if not isinstance(content_types, list):
            raise AdvisoryDefinitionError("content_types must be a list")

        loaded: list[str] = []
        for content_type in content_types:
            if not isinstance(content_type, dict):
                raise AdvisoryDefinitionError("Advisory Content Type must be an object")
            loaded.append(self._require_string(content_type, "content_type"))
        return tuple(loaded)

    def _load_runtime_boundary(self) -> tuple[str, ...]:
        runtime_boundary = self._require_mapping(self.advisory_model, "runtime_boundary")
        must_not = self._require_string_list(runtime_boundary, "must_not")
        if runtime_boundary.get("not_runtime_command") is not True:
            raise AdvisoryDefinitionError("Advisory runtime boundary must not be command-capable")
        return tuple(must_not)

    def _trigger_match(self, trigger: dict[str, Any]) -> AdvisoryTriggerMatch:
        return AdvisoryTriggerMatch(
            trigger_id=self._require_string(trigger, "trigger_id"),
            trigger_name=self._require_string(trigger, "trigger_name"),
            trigger_condition=self._require_string(trigger, "condition"),
            trigger_purpose=self._require_string(trigger, "purpose"),
        )

    @staticmethod
    def _event_matches(event_type: str, trigger_id: str, trigger_name: str) -> bool:
        normalized_trigger_id = AdvisoryBridge._normalize_text(trigger_id)
        normalized_trigger_name = AdvisoryBridge._normalize_text(trigger_name)
        return event_type in {normalized_trigger_id, normalized_trigger_name}

    @staticmethod
    def _dedupe(values: list[str]) -> tuple[str, ...]:
        deduped: list[str] = []
        for value in values:
            if value not in deduped:
                deduped.append(value)
        return tuple(deduped)

    @staticmethod
    def _require_mapping(mapping: dict[str, Any], key: str) -> dict[str, Any]:
        value = mapping.get(key)
        if not isinstance(value, dict):
            raise AdvisoryDefinitionError(f"{key} must be an object")
        return value

    @staticmethod
    def _require_string(mapping: dict[str, Any], key: str) -> str:
        value = mapping.get(key)
        if not isinstance(value, str) or not value:
            raise AdvisoryDefinitionError(f"{key} must be a non-empty string")
        return value

    @staticmethod
    def _require_string_list(mapping: dict[str, Any], key: str) -> tuple[str, ...]:
        value = mapping.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise AdvisoryDefinitionError(f"{key} must be a list of strings")
        return tuple(value)

    @staticmethod
    def _normalize_text(value: Any) -> str:
        return " ".join(str(value).replace("_", " ").replace("-", " ").casefold().split())


__all__ = [
    "ADVISORY_CONTEXT_READY",
    "ADVISORY_RESPONSE_NO_RUNTIME_STATE_CHANGE",
    "DECISION_REQUIRED",
    "ITERATION_RE_ENTRY",
    "MAKER_GUIDANCE_REQUEST",
    "MISSING_INFORMATION",
    "NO_ADVISORY_TRIGGER",
    "PHASE_ENTRY",
    "RECOMMENDED_ACTION_REQUIRES_RUNTIME_REQUEST",
    "RISK_DETECTED",
    "VALIDATION_FEEDBACK",
    "AdvisoryBridge",
    "AdvisoryBridgeRequest",
    "AdvisoryBridgeResult",
    "AdvisoryContextPacket",
    "AdvisoryDefinitionError",
    "AdvisoryResponse",
    "AdvisoryResponseHandlingResult",
    "AdvisoryTriggerMatch",
    "PendingRuntimeRequest",
]
