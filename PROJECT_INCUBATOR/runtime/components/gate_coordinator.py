"""Gate invocation coordination for Project Incubator V1 runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from PROJECT_INCUBATOR.runtime.components.definition_resolver import DefinitionResolver
from PROJECT_INCUBATOR.runtime.core.contracts import GateEvaluationResult
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


GATE_REQUIREMENT_SATISFIED = "GATE_REQUIREMENT_SATISFIED"
GATE_REQUIREMENT_UNSATISFIED = "GATE_REQUIREMENT_UNSATISFIED"
GATE_AUTHORIZATION_REQUIRED = "GATE_AUTHORIZATION_REQUIRED"
GATE_EVIDENCE_INSUFFICIENT = "GATE_EVIDENCE_INSUFFICIENT"
GATE_ACTION_BLOCKED = "GATE_ACTION_BLOCKED"
NO_GATE_TRIGGERED = "NO_GATE_TRIGGERED"

AUTHORIZATION_NOT_REQUIRED = "NOT_REQUIRED"
AUTHORIZATION_REQUIRED_MISSING = "REQUIRED_MISSING"
AUTHORIZATION_PRESENT_VALID = "PRESENT_VALID"
AUTHORIZATION_PRESENT_INVALID = "PRESENT_INVALID"


class GateDefinitionError(Exception):
    """Raised when frozen Gate definitions cannot support runtime use."""


@dataclass(frozen=True)
class GateInvocationRequest:
    invocation_id: str
    trigger_event: str
    requested_action: str | None = None
    requested_gate_ids: tuple[str, ...] = field(default_factory=tuple)
    risk_object_reference: dict[str, Any] | str | None = None
    current_context_reference: dict[str, Any] | str | None = None
    current_workflow_phase_reference: dict[str, Any] | str | None = None
    relevant_artifact_reference: dict[str, Any] | str | None = None
    workflow_requirement_reference: dict[str, Any] | str | None = None
    evaluation_evidence: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    validation_evidence_reference: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    judgment_evidence: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    maker_authorization_evidence: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    script_invocation_results: tuple[Any, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class GateInvocationReference:
    invocation_id: str
    gate_id: str
    trigger_event: str
    requested_action: str | None


@dataclass(frozen=True)
class GateInput:
    invocation_reference: GateInvocationReference
    gate_definition_reference: str
    gate_name: str
    evaluation_nature: str
    trigger_event: str
    risk_object: tuple[str, ...]
    requested_action: str | None
    evaluation_requirement: tuple[str, ...]
    current_context_reference: dict[str, Any] | str | None
    current_workflow_phase_reference: dict[str, Any] | str | None
    relevant_artifact_reference: dict[str, Any] | str | None
    evidence_set: tuple[dict[str, Any], ...]
    maker_authorization_evidence: tuple[dict[str, Any], ...]
    validation_evidence_reference: tuple[dict[str, Any], ...]
    judgment_evidence: tuple[dict[str, Any], ...]
    required_authorization: tuple[str, ...]
    allowed_action: str | None
    blocked_action: str | None
    workflow_requirement_reference: dict[str, Any] | str | None


@dataclass(frozen=True)
class GateOutput:
    invocation_id: str
    gate_id: str
    evaluation_result: GateEvaluationResult
    evaluation_reason: str
    unsatisfied_requirement: tuple[str, ...]
    required_authorization_status: str
    relevant_risk: tuple[str, ...]
    evidence_reference: tuple[dict[str, Any], ...]
    permitted_action_reference: str | None
    blocked_action_reference: str | None
    workflow_requirement_reference: dict[str, Any] | str | None
    context_reference: dict[str, Any] | str | None
    runtime_state: RuntimeExecutionState
    can_continue_contract_check: bool


@dataclass(frozen=True)
class GateCoordinationResult:
    invocation_id: str
    triggered_gate_ids: tuple[str, ...]
    gate_inputs: tuple[GateInput, ...]
    gate_outputs: tuple[GateOutput, ...]
    aggregate_gate_result: GateEvaluationResult
    runtime_state: RuntimeExecutionState
    result_reason: str
    can_continue_contract_check: bool


class GateCoordinator:
    """Coordinates frozen Gate invocation and maps Gate Result for Runtime use."""

    supported_gate_count = 15

    def __init__(
        self,
        gate_definition: dict[str, Any] | None = None,
        definition_resolver: DefinitionResolver | None = None,
    ) -> None:
        self.gate_definition = gate_definition or self._load_gate_definition(definition_resolver)
        self.gate_definition_set = self._require_mapping(
            self.gate_definition,
            "gate_definitions",
        )
        self.gates_by_id = self._load_gate_map()

    def invoke(self, request: GateInvocationRequest) -> GateCoordinationResult:
        return self.coordinate(request)

    def coordinate(self, request: GateInvocationRequest) -> GateCoordinationResult:
        gate_definitions = self.match_triggers(request)
        gate_inputs = tuple(self.prepare_gate_input(request, gate) for gate in gate_definitions)
        gate_outputs = tuple(self.evaluate_gate(gate_input) for gate_input in gate_inputs)
        return self._coordination_result(request, gate_inputs, gate_outputs)

    def reevaluate(
        self,
        request: GateInvocationRequest,
        additional_evidence: tuple[dict[str, Any], ...] = (),
        additional_validation_evidence: tuple[dict[str, Any], ...] = (),
        additional_judgment_evidence: tuple[dict[str, Any], ...] = (),
        additional_maker_authorization_evidence: tuple[dict[str, Any], ...] = (),
    ) -> GateCoordinationResult:
        updated_request = GateInvocationRequest(
            invocation_id=request.invocation_id,
            trigger_event=request.trigger_event,
            requested_action=request.requested_action,
            requested_gate_ids=request.requested_gate_ids,
            risk_object_reference=request.risk_object_reference,
            current_context_reference=request.current_context_reference,
            current_workflow_phase_reference=request.current_workflow_phase_reference,
            relevant_artifact_reference=request.relevant_artifact_reference,
            workflow_requirement_reference=request.workflow_requirement_reference,
            evaluation_evidence=request.evaluation_evidence
            + self._tuple_of_dicts(additional_evidence),
            validation_evidence_reference=request.validation_evidence_reference
            + self._tuple_of_dicts(additional_validation_evidence),
            judgment_evidence=request.judgment_evidence
            + self._tuple_of_dicts(additional_judgment_evidence),
            maker_authorization_evidence=request.maker_authorization_evidence
            + self._tuple_of_dicts(additional_maker_authorization_evidence),
            script_invocation_results=request.script_invocation_results,
        )
        return self.coordinate(updated_request)

    def match_triggers(self, request: GateInvocationRequest) -> tuple[dict[str, Any], ...]:
        if request.requested_gate_ids:
            return tuple(self.resolve_gate_definition(gate_id) for gate_id in request.requested_gate_ids)

        trigger_text = self._normalize_text(
            " ".join(
                item
                for item in (request.trigger_event, request.requested_action or "")
                if item
            ),
        )
        if not trigger_text:
            return ()

        matched: list[dict[str, Any]] = []
        for gate in self.gates_by_id.values():
            for trigger_condition in self._require_string_list(gate, "trigger_condition"):
                normalized_condition = self._normalize_text(trigger_condition)
                if normalized_condition and (
                    normalized_condition in trigger_text
                    or trigger_text in normalized_condition
                ):
                    matched.append(gate)
                    break
        return tuple(matched)

    def resolve_gate_definition(self, gate_id: str) -> dict[str, Any]:
        gate = self.gates_by_id.get(gate_id)
        if gate is None:
            raise GateDefinitionError(f"unknown gate definition: {gate_id}")
        return gate

    def prepare_gate_input(
        self,
        request: GateInvocationRequest,
        gate_definition: dict[str, Any],
    ) -> GateInput:
        gate_id = self._require_string(gate_definition, "gate_id")
        invocation_reference = GateInvocationReference(
            invocation_id=f"{request.invocation_id}:{gate_id}",
            gate_id=gate_id,
            trigger_event=request.trigger_event,
            requested_action=request.requested_action,
        )
        validation_evidence = (
            self._filter_evidence_for_gate(request.validation_evidence_reference, gate_id)
            + self._validation_evidence_from_script_results(
                request.script_invocation_results,
                gate_id,
            )
        )
        return GateInput(
            invocation_reference=invocation_reference,
            gate_definition_reference=gate_id,
            gate_name=self._require_string(gate_definition, "gate_name"),
            evaluation_nature=self._require_string(gate_definition, "evaluation_nature"),
            trigger_event=request.trigger_event,
            risk_object=tuple(self._require_string_list(gate_definition, "risk_object")),
            requested_action=request.requested_action,
            evaluation_requirement=tuple(
                self._require_string_list(gate_definition, "evaluation_requirement"),
            ),
            current_context_reference=request.current_context_reference,
            current_workflow_phase_reference=request.current_workflow_phase_reference,
            relevant_artifact_reference=request.relevant_artifact_reference,
            evidence_set=self._filter_evidence_for_gate(request.evaluation_evidence, gate_id),
            maker_authorization_evidence=self._filter_evidence_for_gate(
                request.maker_authorization_evidence,
                gate_id,
            ),
            validation_evidence_reference=validation_evidence,
            judgment_evidence=self._filter_evidence_for_gate(request.judgment_evidence, gate_id),
            required_authorization=tuple(
                self._require_string_list(gate_definition, "required_authorization"),
            ),
            allowed_action=self._optional_string(gate_definition, "allowed_action"),
            blocked_action=self._optional_string(gate_definition, "blocked_action"),
            workflow_requirement_reference=request.workflow_requirement_reference,
        )

    def evaluate_gate(self, gate_input: GateInput) -> GateOutput:
        evidence_reference = self.collect_evidence(gate_input)
        required_authorization_status = self._authorization_status(gate_input)

        if self._has_action_blocked_evidence(evidence_reference):
            return self._gate_output(
                gate_input,
                GateEvaluationResult.ACTION_BLOCKED,
                "Gate Evidence confirms the requested action conflicts with the frozen protection boundary.",
                ("Requested Action conflicts with Blocked Action / Protection Boundary",),
                required_authorization_status,
                evidence_reference,
            )

        if not self._has_required_evidence(gate_input):
            return self._gate_output(
                gate_input,
                GateEvaluationResult.EVIDENCE_INSUFFICIENT,
                "Gate Input does not contain enough Evidence for the Gate Evaluation Requirement.",
                gate_input.evaluation_requirement,
                required_authorization_status,
                evidence_reference,
            )

        if required_authorization_status in {
            AUTHORIZATION_REQUIRED_MISSING,
            AUTHORIZATION_PRESENT_INVALID,
        }:
            return self._gate_output(
                gate_input,
                GateEvaluationResult.AUTHORIZATION_REQUIRED,
                "The requested action requires valid Maker Authorization Evidence for this Gate.",
                ("Maker Authorization Evidence",),
                required_authorization_status,
                evidence_reference,
            )

        explicit_result = self._explicit_gate_result(
            gate_input.evidence_set + gate_input.judgment_evidence,
        )
        if explicit_result is not None:
            return self._gate_output(
                gate_input,
                explicit_result,
                f"Gate Evaluation Evidence explicitly reports {explicit_result.value}.",
                self._unsatisfied_requirement_for(explicit_result, gate_input),
                required_authorization_status,
                evidence_reference,
            )

        if self._has_requirement_unsatisfied_evidence(evidence_reference):
            return self._gate_output(
                gate_input,
                GateEvaluationResult.REQUIREMENT_UNSATISFIED,
                "Gate Evidence is sufficient and reports an unsatisfied Evaluation Requirement.",
                gate_input.evaluation_requirement,
                required_authorization_status,
                evidence_reference,
            )

        return self._gate_output(
            gate_input,
            GateEvaluationResult.REQUIREMENT_SATISFIED,
            "All necessary Gate Evaluation Requirements and Authorization Requirements are satisfied.",
            (),
            required_authorization_status,
            evidence_reference,
        )

    def collect_evidence(self, gate_input: GateInput) -> tuple[dict[str, Any], ...]:
        return (
            gate_input.evidence_set
            + gate_input.validation_evidence_reference
            + gate_input.judgment_evidence
            + gate_input.maker_authorization_evidence
        )

    def map_gate_result_to_runtime(
        self,
        gate_result: GateEvaluationResult,
    ) -> tuple[RuntimeExecutionState, bool, str]:
        if gate_result is GateEvaluationResult.REQUIREMENT_SATISFIED:
            return RuntimeExecutionState.EXECUTING, True, GATE_REQUIREMENT_SATISFIED
        if gate_result is GateEvaluationResult.REQUIREMENT_UNSATISFIED:
            return RuntimeExecutionState.BLOCKED_BY_GATE, False, GATE_REQUIREMENT_UNSATISFIED
        if gate_result is GateEvaluationResult.AUTHORIZATION_REQUIRED:
            return RuntimeExecutionState.WAITING_FOR_MAKER, False, GATE_AUTHORIZATION_REQUIRED
        if gate_result is GateEvaluationResult.EVIDENCE_INSUFFICIENT:
            return RuntimeExecutionState.SUSPENDED, False, GATE_EVIDENCE_INSUFFICIENT
        if gate_result is GateEvaluationResult.ACTION_BLOCKED:
            return RuntimeExecutionState.BLOCKED_BY_GATE, False, GATE_ACTION_BLOCKED
        raise GateDefinitionError(f"unsupported gate result: {gate_result}")

    def _load_gate_definition(
        self,
        definition_resolver: DefinitionResolver | None,
    ) -> dict[str, Any]:
        resolver = definition_resolver or DefinitionResolver()
        resolution = resolver.resolve()
        if (
            resolution.runtime_state is not RuntimeExecutionState.COMPLETED
            or resolution.frozen_definition_set is None
        ):
            missing = resolution.missing_requirement or "Gate Definition"
            raise GateDefinitionError(missing)
        return resolution.frozen_definition_set.gate_definition

    def _load_gate_map(self) -> dict[str, dict[str, Any]]:
        supported_gate_set = set(
            self._require_string_list(self.gate_definition_set, "supported_gate_set"),
        )
        result_set = set(
            self._require_string_list(self.gate_definition_set, "evaluation_result_set"),
        )
        contract_result_set = {result.value for result in GateEvaluationResult}
        if result_set != contract_result_set:
            raise GateDefinitionError("gate result set conflicts with runtime contract types")

        gates = self.gate_definition_set.get("gates")
        if not isinstance(gates, list):
            raise GateDefinitionError("gate definitions must be a list")

        gate_map: dict[str, dict[str, Any]] = {}
        for gate in gates:
            if not isinstance(gate, dict):
                raise GateDefinitionError("gate definition must be an object")
            gate_id = self._require_string(gate, "gate_id")
            for required_key in (
                "gate_name",
                "scope",
                "purpose",
                "trigger_condition",
                "risk_object",
                "evaluation_nature",
                "evaluation_requirement",
                "required_authorization",
                "allowed_action",
                "blocked_action",
            ):
                if required_key not in gate:
                    raise GateDefinitionError(f"gate definition missing field: {required_key}")
            gate_map[gate_id] = gate

        if len(gate_map) != self.supported_gate_count:
            raise GateDefinitionError("gate definition count is not the frozen V1 gate count")
        if set(gate_map) != supported_gate_set:
            raise GateDefinitionError("gate definitions do not match supported gate set")
        return gate_map

    def _coordination_result(
        self,
        request: GateInvocationRequest,
        gate_inputs: tuple[GateInput, ...],
        gate_outputs: tuple[GateOutput, ...],
    ) -> GateCoordinationResult:
        if not gate_outputs:
            return GateCoordinationResult(
                invocation_id=request.invocation_id,
                triggered_gate_ids=(),
                gate_inputs=gate_inputs,
                gate_outputs=gate_outputs,
                aggregate_gate_result=GateEvaluationResult.REQUIREMENT_SATISFIED,
                runtime_state=RuntimeExecutionState.EXECUTING,
                result_reason=NO_GATE_TRIGGERED,
                can_continue_contract_check=True,
            )

        aggregate_gate_result = self._aggregate_gate_result(gate_outputs)
        runtime_state, can_continue, result_reason = self.map_gate_result_to_runtime(
            aggregate_gate_result,
        )
        return GateCoordinationResult(
            invocation_id=request.invocation_id,
            triggered_gate_ids=tuple(output.gate_id for output in gate_outputs),
            gate_inputs=gate_inputs,
            gate_outputs=gate_outputs,
            aggregate_gate_result=aggregate_gate_result,
            runtime_state=runtime_state,
            result_reason=result_reason,
            can_continue_contract_check=can_continue,
        )

    def _aggregate_gate_result(
        self,
        gate_outputs: tuple[GateOutput, ...],
    ) -> GateEvaluationResult:
        gate_results = tuple(output.evaluation_result for output in gate_outputs)
        for candidate in (
            GateEvaluationResult.ACTION_BLOCKED,
            GateEvaluationResult.REQUIREMENT_UNSATISFIED,
            GateEvaluationResult.AUTHORIZATION_REQUIRED,
            GateEvaluationResult.EVIDENCE_INSUFFICIENT,
        ):
            if candidate in gate_results:
                return candidate
        return GateEvaluationResult.REQUIREMENT_SATISFIED

    def _gate_output(
        self,
        gate_input: GateInput,
        evaluation_result: GateEvaluationResult,
        evaluation_reason: str,
        unsatisfied_requirement: tuple[str, ...],
        required_authorization_status: str,
        evidence_reference: tuple[dict[str, Any], ...],
    ) -> GateOutput:
        runtime_state, can_continue, _ = self.map_gate_result_to_runtime(evaluation_result)
        permitted_action_reference = (
            gate_input.allowed_action
            if evaluation_result is GateEvaluationResult.REQUIREMENT_SATISFIED
            else None
        )
        blocked_action_reference = (
            None
            if evaluation_result is GateEvaluationResult.REQUIREMENT_SATISFIED
            else gate_input.blocked_action
        )
        return GateOutput(
            invocation_id=gate_input.invocation_reference.invocation_id,
            gate_id=gate_input.gate_definition_reference,
            evaluation_result=evaluation_result,
            evaluation_reason=evaluation_reason,
            unsatisfied_requirement=unsatisfied_requirement,
            required_authorization_status=required_authorization_status,
            relevant_risk=gate_input.risk_object,
            evidence_reference=evidence_reference,
            permitted_action_reference=permitted_action_reference,
            blocked_action_reference=blocked_action_reference,
            workflow_requirement_reference=gate_input.workflow_requirement_reference,
            context_reference=gate_input.current_context_reference,
            runtime_state=runtime_state,
            can_continue_contract_check=can_continue,
        )

    def _authorization_status(self, gate_input: GateInput) -> str:
        if not self._requested_action_requires_authorization(gate_input):
            return AUTHORIZATION_NOT_REQUIRED

        if not gate_input.maker_authorization_evidence:
            return AUTHORIZATION_REQUIRED_MISSING

        if self._has_valid_authorization(gate_input):
            return AUTHORIZATION_PRESENT_VALID
        return AUTHORIZATION_PRESENT_INVALID

    def _requested_action_requires_authorization(self, gate_input: GateInput) -> bool:
        explicit_requirement = self._any_truthy_flag(
            self.collect_evidence(gate_input),
            ("requires_maker_authorization", "authorization_required"),
        )
        if explicit_requirement:
            return True

        requested_action = self._normalize_text(gate_input.requested_action or "")
        if not requested_action:
            return False
        for required_action in gate_input.required_authorization:
            normalized_required = self._normalize_text(required_action)
            if normalized_required and (
                normalized_required in requested_action
                or requested_action in normalized_required
            ):
                return True
        return False

    def _has_valid_authorization(self, gate_input: GateInput) -> bool:
        requested_action = self._normalize_text(gate_input.requested_action or "")
        for evidence in gate_input.maker_authorization_evidence:
            authorizer = evidence.get("authorizer", evidence.get("Authorizer"))
            if authorizer != "MAKER":
                continue

            gate_reference = evidence.get("gate_id", evidence.get("Gate ID"))
            if gate_reference is not None and not self._references_gate(
                gate_reference,
                gate_input.gate_definition_reference,
            ):
                continue

            action_reference = evidence.get(
                "authorized_action_reference",
                evidence.get("Authorized Action Reference"),
            )
            if action_reference is not None and requested_action:
                normalized_action = self._normalize_text(action_reference)
                if normalized_action and (
                    requested_action not in normalized_action
                    and normalized_action not in requested_action
                ):
                    continue

            return True
        return False

    def _has_required_evidence(self, gate_input: GateInput) -> bool:
        if self._explicit_gate_result(gate_input.evidence_set + gate_input.judgment_evidence):
            return True

        deterministic_evidence = bool(
            gate_input.evidence_set or gate_input.validation_evidence_reference
        )
        judgment_evidence = bool(gate_input.judgment_evidence) or self._has_category_evidence(
            gate_input.evidence_set,
            {"JUDGMENT", "JUDGMENT_EVIDENCE", "MAKER_STATEMENT", "MAKER_STATEMENT_EVIDENCE"},
        )
        nature = gate_input.evaluation_nature
        if nature == "Evidence-Based":
            return deterministic_evidence
        if nature == "Judgment-Based":
            return judgment_evidence
        if nature == "Mixed":
            return deterministic_evidence and judgment_evidence
        return False

    def _explicit_gate_result(
        self,
        evidence_set: tuple[dict[str, Any], ...],
    ) -> GateEvaluationResult | None:
        for evidence in evidence_set:
            for key in ("gate_result", "evaluation_result", "Gate Result"):
                raw_value = evidence.get(key)
                if raw_value is None:
                    continue
                try:
                    return GateEvaluationResult(raw_value)
                except ValueError as exc:
                    raise GateDefinitionError(f"invalid Gate Evaluation Result: {raw_value}") from exc
        return None

    def _has_action_blocked_evidence(
        self,
        evidence_set: tuple[dict[str, Any], ...],
    ) -> bool:
        return self._any_truthy_flag(
            evidence_set,
            ("action_blocked", "blocked_action_matched", "protection_boundary_conflict"),
        )

    def _has_requirement_unsatisfied_evidence(
        self,
        evidence_set: tuple[dict[str, Any], ...],
    ) -> bool:
        if self._any_truthy_flag(
            evidence_set,
            ("requirement_unsatisfied", "requirement_missing", "validation_failed"),
        ):
            return True
        for evidence in evidence_set:
            status = evidence.get("requirement_status")
            if isinstance(status, str) and status.upper() in {
                "UNSATISFIED",
                "REQUIREMENT_UNSATISFIED",
            }:
                return True
        return False

    def _unsatisfied_requirement_for(
        self,
        gate_result: GateEvaluationResult,
        gate_input: GateInput,
    ) -> tuple[str, ...]:
        if gate_result is GateEvaluationResult.REQUIREMENT_SATISFIED:
            return ()
        if gate_result is GateEvaluationResult.AUTHORIZATION_REQUIRED:
            return ("Maker Authorization Evidence",)
        if gate_result is GateEvaluationResult.ACTION_BLOCKED:
            return ("Requested Action conflicts with Blocked Action / Protection Boundary",)
        return gate_input.evaluation_requirement

    def _validation_evidence_from_script_results(
        self,
        script_invocation_results: tuple[Any, ...],
        gate_id: str,
    ) -> tuple[dict[str, Any], ...]:
        evidence_items: list[dict[str, Any]] = []
        for result in script_invocation_results:
            result_evidence = getattr(result, "evidence", ())
            if not isinstance(result_evidence, tuple):
                result_evidence = self._tuple_of_dicts(result_evidence)
            for evidence in result_evidence:
                if self._evidence_applies_to_gate(evidence, gate_id):
                    evidence_items.append(
                        {
                            **evidence,
                            "script_invocation_id": getattr(result, "invocation_id", None),
                            "script_validation_result": self._enum_value(
                                getattr(result, "validation_result", None),
                            ),
                        },
                    )
        return tuple(evidence_items)

    def _filter_evidence_for_gate(
        self,
        evidence_set: tuple[dict[str, Any], ...],
        gate_id: str,
    ) -> tuple[dict[str, Any], ...]:
        return tuple(
            evidence
            for evidence in self._tuple_of_dicts(evidence_set)
            if self._evidence_applies_to_gate(evidence, gate_id)
        )

    @staticmethod
    def _evidence_applies_to_gate(evidence: dict[str, Any], gate_id: str) -> bool:
        gate_reference = evidence.get("gate_id", evidence.get("Gate ID", evidence.get("gate_ids")))
        if gate_reference is None:
            return True
        return GateCoordinator._references_gate(gate_reference, gate_id)

    @staticmethod
    def _references_gate(gate_reference: Any, gate_id: str) -> bool:
        if isinstance(gate_reference, str):
            return gate_reference == gate_id
        if isinstance(gate_reference, (list, tuple, set)):
            return gate_id in gate_reference
        return False

    @staticmethod
    def _has_category_evidence(
        evidence_set: tuple[dict[str, Any], ...],
        accepted_categories: set[str],
    ) -> bool:
        for evidence in evidence_set:
            category = evidence.get("evidence_category", evidence.get("category"))
            if isinstance(category, str) and category.upper() in accepted_categories:
                return True
        return False

    @staticmethod
    def _any_truthy_flag(
        evidence_set: tuple[dict[str, Any], ...],
        keys: tuple[str, ...],
    ) -> bool:
        for evidence in evidence_set:
            for key in keys:
                if evidence.get(key) is True:
                    return True
        return False

    @staticmethod
    def _require_mapping(mapping: dict[str, Any], key: str) -> dict[str, Any]:
        value = mapping.get(key)
        if not isinstance(value, dict):
            raise GateDefinitionError(f"{key} must be an object")
        return value

    @staticmethod
    def _require_string(mapping: dict[str, Any], key: str) -> str:
        value = mapping.get(key)
        if not isinstance(value, str) or not value:
            raise GateDefinitionError(f"{key} must be a non-empty string")
        return value

    @staticmethod
    def _optional_string(mapping: dict[str, Any], key: str) -> str | None:
        value = mapping.get(key)
        if value is None:
            return None
        if not isinstance(value, str) or not value:
            raise GateDefinitionError(f"{key} must be a non-empty string when present")
        return value

    @staticmethod
    def _require_string_list(mapping: dict[str, Any], key: str) -> tuple[str, ...]:
        value = mapping.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise GateDefinitionError(f"{key} must be a list of strings")
        return tuple(value)

    @staticmethod
    def _tuple_of_dicts(value: Any) -> tuple[dict[str, Any], ...]:
        if not isinstance(value, (list, tuple)):
            return ()
        return tuple(item for item in value if isinstance(item, dict))

    @staticmethod
    def _normalize_text(value: Any) -> str:
        return " ".join(str(value).casefold().split())

    @staticmethod
    def _enum_value(value: Any) -> str | None:
        return getattr(value, "value", value) if value is not None else None


__all__ = [
    "AUTHORIZATION_NOT_REQUIRED",
    "AUTHORIZATION_PRESENT_INVALID",
    "AUTHORIZATION_PRESENT_VALID",
    "AUTHORIZATION_REQUIRED_MISSING",
    "GATE_ACTION_BLOCKED",
    "GATE_AUTHORIZATION_REQUIRED",
    "GATE_EVIDENCE_INSUFFICIENT",
    "GATE_REQUIREMENT_SATISFIED",
    "GATE_REQUIREMENT_UNSATISFIED",
    "NO_GATE_TRIGGERED",
    "GateCoordinationResult",
    "GateCoordinator",
    "GateDefinitionError",
    "GateInput",
    "GateInvocationReference",
    "GateInvocationRequest",
    "GateOutput",
]
