"""Context Access Contract execution for Project Incubator V1 runtime."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from PROJECT_INCUBATOR.runtime.adapters.file_store import (
    FileStore,
    FileStoreError,
    FileWriteResult,
)
from PROJECT_INCUBATOR.runtime.core.contracts import ContextAccessResultStatus


class AccessType(Enum):
    READ = "READ"
    REQUEST_MUTATION = "REQUEST_MUTATION"
    AUTHORIZE_MUTATION = "AUTHORIZE_MUTATION"
    EXECUTE_MUTATION = "EXECUTE_MUTATION"


class RequestSource(Enum):
    MAKER = "MAKER"
    AGENT = "AGENT"
    RUNTIME = "RUNTIME"
    WORKFLOW_RUNTIME_COMPONENT = "WORKFLOW_RUNTIME_COMPONENT"
    GATE_RUNTIME_COMPONENT = "GATE_RUNTIME_COMPONENT"
    SCRIPT = "SCRIPT"


class ContextType(Enum):
    PROJECT_PROFILE = "PROJECT_PROFILE"
    PROJECT_STATE = "PROJECT_STATE"
    PROJECT_PLAN = "PROJECT_PLAN"
    PROJECT_DECISIONS = "PROJECT_DECISIONS"
    OPTIONAL_CONTEXT = "OPTIONAL_CONTEXT"


class MutationType(Enum):
    CREATE_CONTEXT = "CREATE_CONTEXT"
    UPDATE_CONTEXT = "UPDATE_CONTEXT"
    APPEND_RECORD = "APPEND_RECORD"
    RETIRE_OPTIONAL_CONTEXT = "RETIRE_OPTIONAL_CONTEXT"


@dataclass(frozen=True)
class AccessTarget:
    context_type: ContextType
    context_reference: str | Path | None = None
    optional_context_identity: str | None = None


@dataclass(frozen=True)
class AuthorizationEvidence:
    source: RequestSource
    confirmed: bool
    reference: str | None = None


@dataclass(frozen=True)
class MutationIntent:
    mutation_type: MutationType
    target_context: AccessTarget
    change_purpose: str
    change_basis: str
    proposed_content: str
    proposed_change_reference: str | None = None
    maker_authorization: AuthorizationEvidence | None = None
    gate_evidence_reference: str | None = None
    conflict_reference: str | None = None
    overrides_core_context_authority: bool = False
    execute_eligibility_granted: bool = False


@dataclass(frozen=True)
class ContextAccessRequest:
    request_id: str
    access_target: AccessTarget
    access_type: AccessType
    request_source: RequestSource
    access_purpose: str
    mutation_intent: MutationIntent | None = None
    requirement_reference: str | None = None
    conflict_reference: str | None = None


@dataclass(frozen=True)
class ContextAccessResult:
    request_id: str
    status: ContextAccessResultStatus
    access_target: AccessTarget
    requested_access_type: AccessType
    decision_reason: str
    missing_requirement: str | None = None
    authorization_requirement: str | None = None
    gate_requirement_reference: str | None = None
    conflict_reference: str | None = None
    boundary_reference: str | None = None
    content: str | None = None
    persisted_result: FileWriteResult | None = None
    persisted_result_verified: bool = False


class ContextCoordinator:
    """Executes Context Access Contract checks before file interaction."""

    context_file_names = {
        ContextType.PROJECT_PROFILE: "PROJECT_PROFILE.md",
        ContextType.PROJECT_STATE: "PROJECT_STATE.md",
        ContextType.PROJECT_PLAN: "PROJECT_PLAN.md",
        ContextType.PROJECT_DECISIONS: "PROJECT_DECISIONS.md",
    }

    direct_read_sources = {
        RequestSource.MAKER,
        RequestSource.AGENT,
        RequestSource.RUNTIME,
    }

    conditional_read_sources = {
        RequestSource.WORKFLOW_RUNTIME_COMPONENT,
        RequestSource.GATE_RUNTIME_COMPONENT,
    }

    allowed_state_change_basis = {
        "WORKFLOW_STATE_CHANGE_REQUIREMENT",
        "WORKFLOW_COMPLETION_FACT",
        "GATE_HANDLED_FACT",
        "VALIDATED_EXECUTION_FACT",
        "MAKER_REQUESTED_CORRECTION",
        "RUNTIME_CONFIRMED_EXECUTION_FACT",
    }

    def __init__(self, file_store: FileStore) -> None:
        self.file_store = file_store

    def handle(self, request: ContextAccessRequest) -> ContextAccessResult:
        if request.conflict_reference:
            return self._result(
                request,
                ContextAccessResultStatus.CONTEXT_CONFLICT,
                "request conflicts with authority context",
                conflict_reference=request.conflict_reference,
            )

        if request.access_type is AccessType.READ:
            return self.read(request)
        if request.access_type is AccessType.REQUEST_MUTATION:
            return self.request_mutation(request)
        if request.access_type is AccessType.AUTHORIZE_MUTATION:
            return self.authorize_mutation(request)
        if request.access_type is AccessType.EXECUTE_MUTATION:
            return self.execute_mutation(request)

        return self._result(
            request,
            ContextAccessResultStatus.REJECTED,
            "unsupported access type",
            missing_requirement="valid access type",
        )

    def read(self, request: ContextAccessRequest) -> ContextAccessResult:
        read_check = self._check_read_permission(request)
        if read_check is not None:
            return read_check

        path = self._target_path(request.access_target)
        content = self.file_store.read_file(path) if self.file_store.exists(path) else ""
        return self._result(
            request,
            ContextAccessResultStatus.ACCEPTED,
            "read permission accepted",
            content=content,
        )

    def request_mutation(self, request: ContextAccessRequest) -> ContextAccessResult:
        intent = request.mutation_intent
        if intent is None:
            return self._result(
                request,
                ContextAccessResultStatus.REJECTED,
                "mutation intent is required",
                missing_requirement="Mutation Intent",
            )

        authority_check = self.check_mutation_authority(request, intent)
        if authority_check is not None:
            return authority_check

        gate_check = self._check_gate_requirement(request, intent)
        if gate_check is not None:
            return gate_check

        authorization_check = self._check_authorization_requirement(request, intent)
        if authorization_check is not None:
            return authorization_check

        return self._result(
            request,
            ContextAccessResultStatus.ACCEPTED,
            "mutation request accepted for controlled processing",
        )

    def authorize_mutation(self, request: ContextAccessRequest) -> ContextAccessResult:
        intent = request.mutation_intent
        if request.request_source is not RequestSource.MAKER:
            return self._result(
                request,
                ContextAccessResultStatus.REJECTED,
                "only Maker can provide Maker Authorization",
                missing_requirement="Maker Authorization Authority",
            )
        if intent is None or intent.maker_authorization is None:
            return self._result(
                request,
                ContextAccessResultStatus.AUTHORIZATION_REQUIRED,
                "maker authorization evidence is required",
                authorization_requirement="Maker Authorization Evidence",
            )
        if not self._has_maker_authorization(intent):
            return self._result(
                request,
                ContextAccessResultStatus.AUTHORIZATION_REQUIRED,
                "maker authorization evidence is not confirmed",
                authorization_requirement="Confirmed Maker Authorization",
            )
        return self._result(
            request,
            ContextAccessResultStatus.ACCEPTED,
            "maker authorization accepted",
        )

    def execute_mutation(self, request: ContextAccessRequest) -> ContextAccessResult:
        intent = request.mutation_intent
        if request.request_source is not RequestSource.RUNTIME:
            return self._result(
                request,
                ContextAccessResultStatus.REJECTED,
                "only Runtime can execute persisted context mutation",
                missing_requirement="Runtime Execution Authority",
            )
        if intent is None:
            return self._result(
                request,
                ContextAccessResultStatus.REJECTED,
                "mutation intent is required",
                missing_requirement="Mutation Intent",
            )

        eligibility_check = self.request_mutation(request)
        if eligibility_check.status is not ContextAccessResultStatus.ACCEPTED:
            return eligibility_check

        if not intent.execute_eligibility_granted:
            return self._result(
                request,
                ContextAccessResultStatus.REJECTED,
                "execute mutation eligibility is missing",
                missing_requirement="EXECUTE_MUTATION Eligibility",
            )

        path = self._target_path(intent.target_context)
        try:
            if intent.mutation_type is MutationType.APPEND_RECORD:
                persisted_result = self.file_store.append(path, intent.proposed_content)
            else:
                persisted_result = self.file_store.atomic_write(
                    path,
                    intent.proposed_content,
                )
        except FileStoreError as exc:
            return self._result(
                request,
                ContextAccessResultStatus.REJECTED,
                "context persistence failed",
                missing_requirement=str(exc),
            )

        return self._result(
            request,
            ContextAccessResultStatus.ACCEPTED,
            "context mutation persisted and verified",
            persisted_result=persisted_result,
            persisted_result_verified=persisted_result.verified,
        )

    def check_mutation_authority(
        self,
        request: ContextAccessRequest,
        intent: MutationIntent,
    ) -> ContextAccessResult | None:
        if intent.conflict_reference:
            return self._result(
                request,
                ContextAccessResultStatus.CONTEXT_CONFLICT,
                "mutation intent conflicts with authority context",
                conflict_reference=intent.conflict_reference,
            )

        if intent.target_context.context_type is not request.access_target.context_type:
            return self._result(
                request,
                ContextAccessResultStatus.BOUNDARY_VIOLATION,
                "mutation target does not match access target",
                boundary_reference="Target Context",
            )

        if request.request_source in {RequestSource.GATE_RUNTIME_COMPONENT, RequestSource.SCRIPT}:
            return self._result(
                request,
                ContextAccessResultStatus.REJECTED,
                "request source has no mutation proposal authority",
                missing_requirement="Mutation Proposal Authority",
            )

        if request.request_source is RequestSource.AGENT:
            if request.access_type is AccessType.EXECUTE_MUTATION:
                return self._result(
                    request,
                    ContextAccessResultStatus.REJECTED,
                    "agent cannot execute persisted context mutation",
                    missing_requirement="Runtime Execution Authority",
                )
            if intent.target_context.context_type is ContextType.PROJECT_STATE:
                if intent.change_basis not in self.allowed_state_change_basis:
                    return self._result(
                        request,
                        ContextAccessResultStatus.REJECTED,
                        "agent project state mutation request requires valid state change basis",
                        missing_requirement="State Change Basis",
                    )

        if request.request_source in {
            RequestSource.RUNTIME,
            RequestSource.WORKFLOW_RUNTIME_COMPONENT,
        }:
            if not intent.change_basis:
                return self._result(
                    request,
                    ContextAccessResultStatus.REJECTED,
                    "runtime or workflow mutation request requires upstream basis",
                    missing_requirement="Change Basis",
                )

        return self._check_context_boundary(request, intent)

    def _check_read_permission(
        self,
        request: ContextAccessRequest,
    ) -> ContextAccessResult | None:
        if request.request_source is RequestSource.SCRIPT:
            return self._result(
                request,
                ContextAccessResultStatus.REJECTED,
                "script direct context read is prohibited",
                missing_requirement="Runtime-provided limited input",
            )
        if request.request_source in self.direct_read_sources:
            return None
        if request.request_source in self.conditional_read_sources:
            if request.requirement_reference:
                return None
            return self._result(
                request,
                ContextAccessResultStatus.REJECTED,
                "conditional read requires upstream requirement reference",
                missing_requirement="Requirement-scoped Read Basis",
            )
        return self._result(
            request,
            ContextAccessResultStatus.REJECTED,
            "request source has no read permission",
            missing_requirement="Read Permission",
        )

    def _check_context_boundary(
        self,
        request: ContextAccessRequest,
        intent: MutationIntent,
    ) -> ContextAccessResult | None:
        target_type = intent.target_context.context_type
        mutation_type = intent.mutation_type

        if target_type is ContextType.PROJECT_PROFILE:
            if mutation_type not in {
                MutationType.CREATE_CONTEXT,
                MutationType.UPDATE_CONTEXT,
            }:
                return self._boundary_violation(request, "PROJECT_PROFILE allowed mutation intent")

        if target_type is ContextType.PROJECT_STATE:
            if mutation_type not in {
                MutationType.CREATE_CONTEXT,
                MutationType.UPDATE_CONTEXT,
            }:
                return self._boundary_violation(request, "PROJECT_STATE allowed mutation intent")
            if intent.change_basis == "RUNTIME_TEMPORARY_STATE":
                return self._boundary_violation(request, "PROJECT_STATE source of truth boundary")

        if target_type is ContextType.PROJECT_PLAN:
            if mutation_type not in {
                MutationType.CREATE_CONTEXT,
                MutationType.UPDATE_CONTEXT,
            }:
                return self._boundary_violation(request, "PROJECT_PLAN allowed mutation intent")
            if intent.change_basis == "CURRENT_ACTUAL_STATE":
                return self._boundary_violation(request, "PROJECT_PLAN and PROJECT_STATE boundary")

        if target_type is ContextType.PROJECT_DECISIONS:
            if mutation_type is not MutationType.APPEND_RECORD:
                return self._boundary_violation(request, "PROJECT_DECISIONS append-only rule")

        if target_type is ContextType.OPTIONAL_CONTEXT:
            if not intent.target_context.optional_context_identity:
                return self._boundary_violation(request, "Optional Context identity")
            if intent.overrides_core_context_authority:
                return self._boundary_violation(request, "Optional Context core authority boundary")
            if mutation_type not in {
                MutationType.CREATE_CONTEXT,
                MutationType.UPDATE_CONTEXT,
                MutationType.RETIRE_OPTIONAL_CONTEXT,
            }:
                return self._boundary_violation(request, "Optional Context allowed mutation intent")

        return None

    def _check_authorization_requirement(
        self,
        request: ContextAccessRequest,
        intent: MutationIntent,
    ) -> ContextAccessResult | None:
        target_type = intent.target_context.context_type
        if target_type in {ContextType.PROJECT_PROFILE, ContextType.PROJECT_DECISIONS}:
            if not self._has_maker_authorization(intent):
                return self._result(
                    request,
                    ContextAccessResultStatus.AUTHORIZATION_REQUIRED,
                    "maker authorization is required",
                    authorization_requirement="Maker Authorization",
                )
        return None

    def _check_gate_requirement(
        self,
        request: ContextAccessRequest,
        intent: MutationIntent,
    ) -> ContextAccessResult | None:
        if intent.gate_evidence_reference is None and intent.target_context.context_type in {
            ContextType.PROJECT_PROFILE,
            ContextType.PROJECT_DECISIONS,
        }:
            return self._result(
                request,
                ContextAccessResultStatus.GATE_REQUIREMENT_UNRESOLVED,
                "gate-protected context mutation requires gate evidence",
                gate_requirement_reference="Authority Document Gate",
            )
        return None

    @staticmethod
    def _has_maker_authorization(intent: MutationIntent) -> bool:
        evidence = intent.maker_authorization
        return (
            evidence is not None
            and evidence.source is RequestSource.MAKER
            and evidence.confirmed
        )

    def _target_path(self, target: AccessTarget) -> Path:
        if target.context_reference is not None:
            return Path(target.context_reference)
        if target.context_type is ContextType.OPTIONAL_CONTEXT:
            if target.optional_context_identity:
                return Path(f"{target.optional_context_identity}.md")
            return Path("OPTIONAL_CONTEXT.md")
        return Path(self.context_file_names[target.context_type])

    def _boundary_violation(
        self,
        request: ContextAccessRequest,
        boundary_reference: str,
    ) -> ContextAccessResult:
        return self._result(
            request,
            ContextAccessResultStatus.BOUNDARY_VIOLATION,
            "request violates context boundary",
            boundary_reference=boundary_reference,
        )

    @staticmethod
    def _result(
        request: ContextAccessRequest,
        status: ContextAccessResultStatus,
        decision_reason: str,
        **kwargs: Any,
    ) -> ContextAccessResult:
        return ContextAccessResult(
            request_id=request.request_id,
            status=status,
            access_target=request.access_target,
            requested_access_type=request.access_type,
            decision_reason=decision_reason,
            **kwargs,
        )


__all__ = [
    "AccessTarget",
    "AccessType",
    "AuthorizationEvidence",
    "ContextAccessRequest",
    "ContextAccessResult",
    "ContextCoordinator",
    "ContextType",
    "MutationIntent",
    "MutationType",
    "RequestSource",
]
