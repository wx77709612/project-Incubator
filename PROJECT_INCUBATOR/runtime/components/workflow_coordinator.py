"""Workflow Contract consumer for Project Incubator V1 runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from PROJECT_INCUBATOR.runtime.components.definition_resolver import DefinitionResolver
from PROJECT_INCUBATOR.runtime.core.contracts import WorkflowResultStatus
from PROJECT_INCUBATOR.runtime.core.evidence_types import (
    CorrectionActivityState,
    CorrectionResult,
    failure_signature,
    validate_thresholds,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class WorkflowDefinitionError(Exception):
    """Raised when the frozen Workflow definition cannot support runtime use."""


@dataclass(frozen=True)
class CurrentPhaseReference:
    phase_id: str
    phase_name: str
    phase_state: str | None = None


@dataclass(frozen=True)
class PhaseInputPreparation:
    phase_id: str
    phase_name: str
    required_inputs: tuple[str, ...]


@dataclass(frozen=True)
class PhaseRequirementSet:
    phase_id: str
    required_artifacts: tuple[str, ...]
    state_change_required: bool
    gate_trigger_requirements: tuple[str, ...]
    allowed_next_phases: tuple[str, ...]


@dataclass(frozen=True)
class PhaseResult:
    current_phase: str
    requested_next_phase: str
    process_completed: bool
    required_artifact_requirement_satisfied: bool
    state_change_requirement_formed: bool
    gate_requirement_resolved: bool
    artifact_evidence: tuple[str, ...] = field(default_factory=tuple)
    state_change_reference: str | None = None
    gate_resolution_reference: str | None = None


@dataclass(frozen=True)
class PhaseResultValidation:
    phase_id: str
    requested_next_phase: str
    missing_requirements: tuple[str, ...]

    @property
    def satisfied(self) -> bool:
        return not self.missing_requirements


@dataclass(frozen=True)
class TransitionRequest:
    request_id: str
    current_phase: str
    requested_next_phase: str
    phase_result: PhaseResult


@dataclass(frozen=True)
class TransitionEligibilityResult:
    request_id: str
    current_phase: str
    requested_next_phase: str
    status: WorkflowResultStatus
    decision_reason: str
    missing_requirements: tuple[str, ...] = field(default_factory=tuple)


IMPACT_ASSESSMENT_FIELDS = (
    "changes_product_goal",
    "changes_success_criteria",
    "changes_maker_approved_scope",
    "changes_core_phase_model",
    "changes_context_authority",
    "changes_runtime_invariant",
    "crosses_current_work_package",
    "affected_scope_identified",
    "regression_set_identified",
)

MAKER_SCOPE_FIELDS = IMPACT_ASSESSMENT_FIELDS[:7]


@dataclass(frozen=True)
class CorrectionAssessmentRequest:
    request_id: str
    current_phase: str
    capability_id: str
    candidate_model_version: str
    scenario_id: str
    boundary_step: str
    observed_outcome: str
    failure_signature: str
    consecutive_failure_count: int
    evidence_refs: tuple[str, ...]
    affected_assumption_ids: tuple[str, ...]
    affected_artifacts: tuple[str, ...]
    impact_assessment: dict[str, Any]
    authorization_evidence: tuple[str, ...] = field(default_factory=tuple)

    @property
    def counter_key(self) -> tuple[str, str, str]:
        return (
            self.capability_id,
            self.candidate_model_version,
            self.failure_signature,
        )


@dataclass(frozen=True)
class CorrectionAssessmentResult:
    request_id: str
    current_phase: str
    result: CorrectionResult
    activity_state: CorrectionActivityState
    decision_reason: str
    counter_key: tuple[str, str, str] | None = None
    missing_requirements: tuple[str, ...] = field(default_factory=tuple)
    transition_request: None = None


class WorkflowCoordinator:
    """Evaluates Workflow transition eligibility from frozen definitions only."""

    def __init__(
        self,
        workflow_definition: dict[str, Any] | None = None,
        definition_resolver: DefinitionResolver | None = None,
    ) -> None:
        self.workflow_definition = workflow_definition or self._load_workflow_definition(
            definition_resolver,
        )
        self.workflow = self._require_mapping(self.workflow_definition, "workflow")
        self.phases_by_id = self._load_phase_map()
        self.allowed_transitions = frozenset(self._load_allowed_transitions())
        self.p6_iteration_transition_set = frozenset(
            self._require_string_list(self.workflow, "p6_iteration_transition_set"),
        )
        p4_policy = self.phases_by_id["P4"].get("correction_policy", {})
        if not isinstance(p4_policy, dict):
            raise WorkflowDefinitionError("P4 correction_policy must be an object")
        try:
            self.correction_thresholds = validate_thresholds(
                advisory=p4_policy.get("advisory_threshold", 2),
                correction=p4_policy.get("correction_threshold", 3),
            )
        except (TypeError, ValueError) as error:
            raise WorkflowDefinitionError(str(error)) from error

    def resolve_current_phase(self, project_state: dict[str, Any]) -> CurrentPhaseReference:
        phase_id = self._extract_current_phase_id(project_state)
        phase = self._phase(phase_id)
        phase_state = project_state.get("Current Phase State")
        if phase_state is None:
            phase_state = project_state.get("current_phase_state")
        if phase_state is not None and not isinstance(phase_state, str):
            raise WorkflowDefinitionError("Current Phase State must be a string when present")
        return CurrentPhaseReference(
            phase_id=phase_id,
            phase_name=self._require_string(phase, "phase_name"),
            phase_state=phase_state,
        )

    def prepare_phase_input(self, phase_id: str) -> PhaseInputPreparation:
        phase = self._phase(phase_id)
        return PhaseInputPreparation(
            phase_id=phase_id,
            phase_name=self._require_string(phase, "phase_name"),
            required_inputs=tuple(self._require_string_list(phase, "input")),
        )

    def phase_requirements(self, phase_id: str) -> PhaseRequirementSet:
        phase = self._phase(phase_id)
        state_change_requirement = self._require_mapping(
            phase,
            "state_change_requirement",
        )
        return PhaseRequirementSet(
            phase_id=phase_id,
            required_artifacts=tuple(self._require_string_list(phase, "required_artifact")),
            state_change_required=bool(state_change_requirement.get("required")),
            gate_trigger_requirements=tuple(
                self._require_string_list(phase, "gate_trigger_requirement"),
            ),
            allowed_next_phases=tuple(self._require_string_list(phase, "allowed_next_phase")),
        )

    def validate_phase_result(self, phase_result: PhaseResult) -> PhaseResultValidation:
        phase = self._phase(phase_result.current_phase)
        missing: list[str] = []

        if not phase_result.process_completed:
            missing.append("Process Completion")
        if not phase_result.requested_next_phase:
            missing.append("Requested Next Phase")
        if not phase_result.required_artifact_requirement_satisfied:
            missing.append("Required Artifact Requirement")

        state_change_requirement = self._require_mapping(
            phase,
            "state_change_requirement",
        )
        if state_change_requirement.get("required") and not phase_result.state_change_requirement_formed:
            missing.append("State Change Requirement")

        gate_requirements = self._require_string_list(phase, "gate_trigger_requirement")
        if gate_requirements and not phase_result.gate_requirement_resolved:
            missing.append("Gate Requirement")

        return PhaseResultValidation(
            phase_id=phase_result.current_phase,
            requested_next_phase=phase_result.requested_next_phase,
            missing_requirements=tuple(missing),
        )

    def create_transition_request(
        self,
        request_id: str,
        phase_result: PhaseResult,
    ) -> TransitionRequest:
        self._phase(phase_result.current_phase)
        return TransitionRequest(
            request_id=request_id,
            current_phase=phase_result.current_phase,
            requested_next_phase=phase_result.requested_next_phase,
            phase_result=phase_result,
        )

    def evaluate_transition(
        self,
        transition_request: TransitionRequest,
    ) -> TransitionEligibilityResult:
        current_phase = transition_request.current_phase
        requested_next_phase = transition_request.requested_next_phase
        transition_path = (current_phase, requested_next_phase)

        if current_phase not in self.phases_by_id:
            return self._transition_result(
                transition_request,
                WorkflowResultStatus.TRANSITION_NOT_ALLOWED,
                "current phase is not defined in frozen Workflow",
                ("Current Phase",),
            )
        if requested_next_phase not in self.phases_by_id:
            return self._transition_result(
                transition_request,
                WorkflowResultStatus.TRANSITION_NOT_ALLOWED,
                "requested next phase is not defined in frozen Workflow",
                ("Requested Next Phase",),
            )
        if transition_path not in self.allowed_transitions:
            return self._transition_result(
                transition_request,
                WorkflowResultStatus.TRANSITION_NOT_ALLOWED,
                "requested transition path is not allowed by Workflow Contract",
                ("Allowed Next Phase",),
            )
        if current_phase == "P6" and requested_next_phase not in self.p6_iteration_transition_set:
            return self._transition_result(
                transition_request,
                WorkflowResultStatus.TRANSITION_NOT_ALLOWED,
                "P6 iteration transition target is not allowed by Workflow Contract",
                ("P6 Iteration Transition",),
            )

        phase_result = transition_request.phase_result
        if phase_result.current_phase != current_phase:
            return self._transition_result(
                transition_request,
                WorkflowResultStatus.NOT_READY,
                "phase result current phase does not match transition request",
                ("Current Phase Match",),
            )
        if phase_result.requested_next_phase != requested_next_phase:
            return self._transition_result(
                transition_request,
                WorkflowResultStatus.NOT_READY,
                "phase result requested next phase does not match transition request",
                ("Requested Next Phase",),
            )

        validation = self.validate_phase_result(phase_result)
        if not validation.satisfied:
            return self._transition_result(
                transition_request,
                WorkflowResultStatus.NOT_READY,
                "phase transition requirements are not all satisfied",
                validation.missing_requirements,
            )

        return self._transition_result(
            transition_request,
            WorkflowResultStatus.READY_FOR_TRANSITION,
            "all Workflow Contract transition eligibility requirements are satisfied",
        )

    def is_transition_allowed(self, current_phase: str, requested_next_phase: str) -> bool:
        return (current_phase, requested_next_phase) in self.allowed_transitions

    def evaluate_correction(
        self,
        request: CorrectionAssessmentRequest,
    ) -> CorrectionAssessmentResult:
        missing = self._validate_correction_request(request)
        if missing:
            return self._correction_result(
                request,
                CorrectionResult.CORRECTION_ASSESSMENT_INVALID,
                CorrectionActivityState.CORRECTION_REVIEW,
                "correction assessment input is incomplete or invalid",
                missing,
            )

        impact = request.impact_assessment
        maker_scope_required = any(impact[field_name] for field_name in MAKER_SCOPE_FIELDS)
        maker_scope_required = maker_scope_required or not impact["affected_scope_identified"]
        maker_scope_required = maker_scope_required or not impact["regression_set_identified"]
        if maker_scope_required:
            return self._correction_result(
                request,
                CorrectionResult.MAKER_SCOPE_REVIEW_REQUIRED,
                CorrectionActivityState.AWAITING_MAKER_SCOPE_REVIEW,
                "impact crosses the approved local correction boundary",
            )

        advisory_threshold, correction_threshold = self.correction_thresholds
        if request.consecutive_failure_count >= correction_threshold:
            return self._correction_result(
                request,
                CorrectionResult.P4_CORRECTION_REQUIRED,
                CorrectionActivityState.CORRECTION_REVIEW,
                "repeated failure reached the correction threshold",
            )
        if request.consecutive_failure_count >= advisory_threshold:
            return self._correction_result(
                request,
                CorrectionResult.MODEL_REVIEW_ADVISORY,
                CorrectionActivityState.NORMAL_CREATION,
                "repeated failure reached the model review threshold",
            )
        return self._correction_result(
            request,
            CorrectionResult.NO_CORRECTION,
            CorrectionActivityState.NORMAL_CREATION,
            "correction threshold has not been reached",
        )

    @staticmethod
    def validate_correction_resume(resume_request: dict[str, Any]) -> tuple[str, ...]:
        required = (
            "affected_scope",
            "regression_set",
            "updated_model",
            "required_authorization",
            "resolved_drift",
            "evidence_change",
            "confidence_change",
            "baseline_change",
            "next_action",
        )
        if not isinstance(resume_request, dict):
            return required
        return tuple(
            key
            for key in required
            if key not in resume_request or resume_request[key] is None or resume_request[key] == ""
        )

    @staticmethod
    def _validate_correction_request(
        request: CorrectionAssessmentRequest,
    ) -> tuple[str, ...]:
        missing: list[str] = []
        if request.current_phase != "P4":
            missing.append("current_phase")
        for field_name in (
            "request_id",
            "capability_id",
            "candidate_model_version",
            "scenario_id",
            "boundary_step",
            "observed_outcome",
            "failure_signature",
        ):
            value = getattr(request, field_name)
            if not isinstance(value, str) or not value:
                missing.append(field_name)
        if (
            isinstance(request.consecutive_failure_count, bool)
            or not isinstance(request.consecutive_failure_count, int)
            or request.consecutive_failure_count < 1
        ):
            missing.append("consecutive_failure_count")
        expected_signature = failure_signature(
            request.capability_id,
            request.scenario_id,
            request.boundary_step,
            request.observed_outcome,
        )
        if request.failure_signature != expected_signature:
            missing.append("failure_signature_match")
        if not isinstance(request.impact_assessment, dict):
            missing.extend(IMPACT_ASSESSMENT_FIELDS)
        else:
            for field_name in IMPACT_ASSESSMENT_FIELDS:
                if type(request.impact_assessment.get(field_name)) is not bool:
                    missing.append(field_name)
        return tuple(dict.fromkeys(missing))

    @staticmethod
    def _correction_result(
        request: CorrectionAssessmentRequest,
        result: CorrectionResult,
        activity_state: CorrectionActivityState,
        decision_reason: str,
        missing_requirements: tuple[str, ...] = (),
    ) -> CorrectionAssessmentResult:
        return CorrectionAssessmentResult(
            request_id=request.request_id,
            current_phase=request.current_phase,
            result=result,
            activity_state=activity_state,
            decision_reason=decision_reason,
            counter_key=request.counter_key,
            missing_requirements=missing_requirements,
        )

    def _load_workflow_definition(
        self,
        definition_resolver: DefinitionResolver | None,
    ) -> dict[str, Any]:
        resolver = definition_resolver or DefinitionResolver()
        resolution = resolver.resolve()
        if (
            resolution.runtime_state is not RuntimeExecutionState.COMPLETED
            or resolution.frozen_definition_set is None
        ):
            missing = resolution.missing_requirement or "Workflow Definition"
            raise WorkflowDefinitionError(missing)
        return resolution.frozen_definition_set.workflow_definition

    def _load_phase_map(self) -> dict[str, dict[str, Any]]:
        phases = self.workflow.get("phases")
        if not isinstance(phases, list):
            raise WorkflowDefinitionError("workflow phases must be a list")

        phase_map: dict[str, dict[str, Any]] = {}
        for phase in phases:
            if not isinstance(phase, dict):
                raise WorkflowDefinitionError("workflow phase must be an object")
            phase_id = self._require_string(phase, "phase_id")
            phase_map[phase_id] = phase

        core_phase_set = set(self._require_string_list(self.workflow, "core_phase_set"))
        if set(phase_map) != core_phase_set:
            raise WorkflowDefinitionError("workflow phases do not match core phase set")
        return phase_map

    def _load_allowed_transitions(self) -> tuple[tuple[str, str], ...]:
        transitions = self.workflow.get("allowed_transitions")
        if not isinstance(transitions, list):
            raise WorkflowDefinitionError("allowed_transitions must be a list")

        allowed: list[tuple[str, str]] = []
        for transition in transitions:
            if not isinstance(transition, dict):
                raise WorkflowDefinitionError("allowed transition must be an object")
            current_phase = self._require_string(transition, "from")
            next_phase = self._require_string(transition, "to")
            if current_phase not in self.phases_by_id or next_phase not in self.phases_by_id:
                raise WorkflowDefinitionError("allowed transition references undefined phase")
            phase_allowed_next = set(
                self._require_string_list(self.phases_by_id[current_phase], "allowed_next_phase"),
            )
            if next_phase not in phase_allowed_next:
                raise WorkflowDefinitionError("allowed transition conflicts with phase definition")
            allowed.append((current_phase, next_phase))
        return tuple(allowed)

    def _extract_current_phase_id(self, project_state: dict[str, Any]) -> str:
        if not isinstance(project_state, dict):
            raise WorkflowDefinitionError("project state must be a mapping")

        phase_value = project_state.get("Current Phase")
        if phase_value is None:
            phase_value = project_state.get("current_phase")
        if isinstance(phase_value, dict):
            phase_value = phase_value.get("phase_id")
        if not isinstance(phase_value, str) or not phase_value:
            raise WorkflowDefinitionError("Current Phase is required")

        phase_id = phase_value.split()[0]
        if phase_id not in self.phases_by_id:
            raise WorkflowDefinitionError("Current Phase is not defined in frozen Workflow")
        return phase_id

    def _phase(self, phase_id: str) -> dict[str, Any]:
        phase = self.phases_by_id.get(phase_id)
        if phase is None:
            raise WorkflowDefinitionError(f"unknown phase: {phase_id}")
        return phase

    @staticmethod
    def _transition_result(
        transition_request: TransitionRequest,
        status: WorkflowResultStatus,
        decision_reason: str,
        missing_requirements: tuple[str, ...] = (),
    ) -> TransitionEligibilityResult:
        return TransitionEligibilityResult(
            request_id=transition_request.request_id,
            current_phase=transition_request.current_phase,
            requested_next_phase=transition_request.requested_next_phase,
            status=status,
            decision_reason=decision_reason,
            missing_requirements=missing_requirements,
        )

    @staticmethod
    def _require_mapping(mapping: dict[str, Any], key: str) -> dict[str, Any]:
        value = mapping.get(key)
        if not isinstance(value, dict):
            raise WorkflowDefinitionError(f"{key} must be an object")
        return value

    @staticmethod
    def _require_string(mapping: dict[str, Any], key: str) -> str:
        value = mapping.get(key)
        if not isinstance(value, str) or not value:
            raise WorkflowDefinitionError(f"{key} must be a non-empty string")
        return value

    @staticmethod
    def _require_string_list(mapping: dict[str, Any], key: str) -> tuple[str, ...]:
        value = mapping.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise WorkflowDefinitionError(f"{key} must be a list of strings")
        return tuple(value)


__all__ = [
    "CorrectionAssessmentRequest",
    "CorrectionAssessmentResult",
    "CurrentPhaseReference",
    "PhaseInputPreparation",
    "PhaseRequirementSet",
    "PhaseResult",
    "PhaseResultValidation",
    "TransitionEligibilityResult",
    "TransitionRequest",
    "WorkflowCoordinator",
    "WorkflowDefinitionError",
]
