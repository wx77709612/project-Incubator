"""Context Access Contract execution for Project Incubator V1 runtime."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re
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
    CAPABILITY_SPIRAL_RECORD = "CAPABILITY_SPIRAL_RECORD"
    PROJECT_DECISION_HISTORY = "PROJECT_DECISION_HISTORY"
    EVIDENCE_ARTIFACT = "EVIDENCE_ARTIFACT"
    BASELINE_RECORD = "BASELINE_RECORD"


class MutationType(Enum):
    CREATE_CONTEXT = "CREATE_CONTEXT"
    UPDATE_CONTEXT = "UPDATE_CONTEXT"
    APPEND_RECORD = "APPEND_RECORD"
    RETIRE_OPTIONAL_CONTEXT = "RETIRE_OPTIONAL_CONTEXT"
    CREATE_DECISION = "CREATE_DECISION"
    UPDATE_DECISION_STATUS = "UPDATE_DECISION_STATUS"
    PARTIALLY_SUPERSEDE_DECISION = "PARTIALLY_SUPERSEDE_DECISION"
    SUPERSEDE_DECISION = "SUPERSEDE_DECISION"
    REVOKE_DECISION = "REVOKE_DECISION"
    ARCHIVE_DECISION_CHANGELOG = "ARCHIVE_DECISION_CHANGELOG"
    UPDATE_ASSUMPTION_STATUS = "UPDATE_ASSUMPTION_STATUS"


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
    decision_id: str | None = None
    assumption_id: str | None = None
    target_status: str | None = None
    effective_scope: str | None = None
    affected_decision_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    dependent_artifact_refs: tuple[str, ...] = ()


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


@dataclass(frozen=True)
class DecisionArchiveResult:
    status: ContextAccessResultStatus
    decision_reason: str
    history_result: FileWriteResult | None = None
    active_view_result: FileWriteResult | None = None


class ContextCoordinator:
    """Executes Context Access Contract checks before file interaction."""

    context_file_names = {
        ContextType.PROJECT_PROFILE: "PROJECT_PROFILE.md",
        ContextType.PROJECT_STATE: "PROJECT_STATE.md",
        ContextType.PROJECT_PLAN: "PROJECT_PLAN.md",
        ContextType.PROJECT_DECISIONS: "PROJECT_DECISIONS.md",
        ContextType.CAPABILITY_SPIRAL_RECORD: "CAPABILITY_SPIRAL_RECORD.md",
        ContextType.PROJECT_DECISION_HISTORY: "PROJECT_DECISION_HISTORY.md",
        ContextType.EVIDENCE_ARTIFACT: "EVIDENCE_ARTIFACT.md",
        ContextType.BASELINE_RECORD: "BASELINE_RECORD.md",
    }

    optional_context_types = {
        ContextType.OPTIONAL_CONTEXT,
        ContextType.CAPABILITY_SPIRAL_RECORD,
        ContextType.PROJECT_DECISION_HISTORY,
        ContextType.EVIDENCE_ARTIFACT,
        ContextType.BASELINE_RECORD,
    }

    decision_mutation_types = {
        MutationType.CREATE_DECISION,
        MutationType.UPDATE_DECISION_STATUS,
        MutationType.PARTIALLY_SUPERSEDE_DECISION,
        MutationType.SUPERSEDE_DECISION,
        MutationType.REVOKE_DECISION,
        MutationType.ARCHIVE_DECISION_CHANGELOG,
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

    def execute_decision_archive(
        self,
        active_view_content: str,
        history_content: str,
        *,
        active_view_path: str | Path = "PROJECT_DECISIONS.md",
        history_path: str | Path = "PROJECT_DECISION_HISTORY.md",
    ) -> DecisionArchiveResult:
        active_ids = self._decision_ids(active_view_content)
        history_ids = self._decision_ids(history_content)
        history_name = Path(history_path).name
        if not active_ids or not history_ids or not active_ids.intersection(history_ids):
            return DecisionArchiveResult(
                ContextAccessResultStatus.REJECTED,
                "archive must preserve at least one stable Decision ID",
            )
        if history_name not in active_view_content:
            return DecisionArchiveResult(
                ContextAccessResultStatus.REJECTED,
                "active view must contain the verified Archive Ref",
            )

        active_existed = self.file_store.exists(active_view_path)
        history_existed = self.file_store.exists(history_path)
        original_active = self.file_store.read_file(active_view_path) if active_existed else ""
        original_history = self.file_store.read_file(history_path) if history_existed else ""
        history_result: FileWriteResult | None = None
        try:
            history_result = self.file_store.atomic_write(history_path, history_content)
            verified_history = self.file_store.read_file(history_path)
            if self._decision_ids(verified_history) != history_ids:
                raise FileStoreError("archived Decision IDs failed read-back verification")
            active_result = self.file_store.atomic_write(active_view_path, active_view_content)
            if self.file_store.read_file(active_view_path) != active_view_content:
                raise FileStoreError("active Decision view failed read-back verification")
        except FileStoreError as error:
            self._restore_archive_content(active_view_path, original_active, active_existed)
            self._restore_archive_content(history_path, original_history, history_existed)
            return DecisionArchiveResult(
                ContextAccessResultStatus.REJECTED,
                f"decision archive transaction failed: {error}",
                history_result=history_result,
            )

        return DecisionArchiveResult(
            ContextAccessResultStatus.ACCEPTED,
            "decision history and active view persisted and verified",
            history_result=history_result,
            active_view_result=active_result,
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

        semantic_check = self._check_v1_1_mutation_fields(request, intent)
        if semantic_check is not None:
            return semantic_check

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
            if mutation_type not in self.decision_mutation_types | {MutationType.APPEND_RECORD}:
                return self._boundary_violation(request, "PROJECT_DECISIONS mutation intent")

        if target_type in self.optional_context_types:
            if target_type is ContextType.OPTIONAL_CONTEXT and not intent.target_context.optional_context_identity:
                return self._boundary_violation(request, "Optional Context identity")
            if intent.overrides_core_context_authority:
                return self._boundary_violation(request, "Optional Context core authority boundary")
            if mutation_type not in {
                MutationType.CREATE_CONTEXT,
                MutationType.UPDATE_CONTEXT,
                MutationType.RETIRE_OPTIONAL_CONTEXT,
                MutationType.UPDATE_ASSUMPTION_STATUS,
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
        if (
            target_type is ContextType.CAPABILITY_SPIRAL_RECORD
            and intent.mutation_type
            in {MutationType.CREATE_CONTEXT, MutationType.RETIRE_OPTIONAL_CONTEXT}
            and not self._has_maker_authorization(intent)
        ):
            return self._result(
                request,
                ContextAccessResultStatus.AUTHORIZATION_REQUIRED,
                "creating or retiring a Capability Spiral Record requires Maker cost and boundary confirmation",
                authorization_requirement="Maker Extension Cost and Boundary Authorization",
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

    def _check_v1_1_mutation_fields(
        self,
        request: ContextAccessRequest,
        intent: MutationIntent,
    ) -> ContextAccessResult | None:
        if intent.mutation_type in self.decision_mutation_types:
            missing = [
                name
                for name, value in (
                    ("Decision ID", intent.decision_id),
                    ("Target Status", intent.target_status),
                    ("Effective Scope", intent.effective_scope),
                )
                if not isinstance(value, str) or not value
            ]
            if not intent.change_basis:
                missing.append("Change Basis")
            if missing:
                return self._result(
                    request,
                    ContextAccessResultStatus.REJECTED,
                    "decision mutation fields are incomplete",
                    missing_requirement=", ".join(missing),
                )

        if intent.mutation_type is MutationType.UPDATE_ASSUMPTION_STATUS:
            valid_statuses = {"WEAKENED", "INVALIDATED", "RETIRED"}
            complete = (
                isinstance(intent.assumption_id, str)
                and bool(intent.assumption_id)
                and intent.target_status in valid_statuses
                and isinstance(intent.effective_scope, str)
                and bool(intent.effective_scope)
                and bool(intent.evidence_refs)
                and bool(intent.dependent_artifact_refs)
            )
            if not complete:
                return self._result(
                    request,
                    ContextAccessResultStatus.REJECTED,
                    "assumption status mutation requires Evidence and affected scope",
                    missing_requirement="Assumption ID, Evidence Ref, Effective Scope, Dependent Artifact Ref",
                )
        return None

    @staticmethod
    def _decision_ids(content: str) -> set[str]:
        return set(re.findall(r"(?:^|\n)#+\s+Decision\s+([A-Za-z0-9_.-]+)", content))

    def _restore_archive_content(
        self,
        path: str | Path,
        original_content: str,
        existed: bool,
    ) -> None:
        if not existed:
            return
        try:
            if self.file_store.read_file(path) != original_content:
                self.file_store.atomic_write(path, original_content)
        except FileStoreError:
            pass

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
    "DecisionArchiveResult",
    "MutationIntent",
    "MutationType",
    "RequestSource",
]
