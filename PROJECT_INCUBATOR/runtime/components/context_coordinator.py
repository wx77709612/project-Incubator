"""Context Access Contract execution for Project Incubator V1 runtime."""

from __future__ import annotations

from dataclasses import dataclass, replace
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
from PROJECT_INCUBATOR.runtime.core.mutation_orchestration_types import (
    AuthorityRequirement,
    AuthorizationProvenance,
    AuthorizationRequestRecord,
    ClosureAssertion,
    ClosureOperator,
    ContextMutationSet,
    MutationOrchestrationResult,
    MutationSetStatus,
    OrchestrationFailureCode,
    authorization_statement_digest,
)


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
        self._orchestration_results: dict[
            str, tuple[str, MutationOrchestrationResult]
        ] = {}

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

    def validate_authorization(
        self,
        pending_request: AuthorizationRequestRecord | None,
        evidence: AuthorizationProvenance | AuthorizationEvidence | None,
        mutation_set: ContextMutationSet,
    ) -> OrchestrationFailureCode | None:
        """Validate Maker authorization provenance for a protected mutation set."""

        if pending_request is None:
            return OrchestrationFailureCode.AUTHORIZATION_REQUIRED
        if not isinstance(evidence, AuthorizationProvenance):
            return OrchestrationFailureCode.AUTHORIZATION_INVALID
        if pending_request.status != "PENDING":
            return OrchestrationFailureCode.AUTHORIZATION_INVALID
        if evidence.authorization_request_id != pending_request.authorization_request_id:
            return OrchestrationFailureCode.AUTHORIZATION_INVALID
        if (
            evidence.source_actor != "MAKER"
            or evidence.source_message_role != "MAKER"
            or not evidence.source_message_ref
            or not evidence.maker_statement_excerpt
            or not evidence.confirmed_at
            or evidence.statement_digest
            != authorization_statement_digest(evidence.maker_statement_excerpt)
        ):
            return OrchestrationFailureCode.AUTHORIZATION_INVALID

        if (
            pending_request.event_type != mutation_set.event_type
            or pending_request.event_ref != mutation_set.event_ref
        ):
            return OrchestrationFailureCode.AUTHORIZATION_SCOPE_MISMATCH

        requested_scope = set(pending_request.requested_scope)
        authorized_scope = set(evidence.authorized_scope)
        target_types = {target.context_type for target in mutation_set.targets}
        requested_targets = set(pending_request.requested_context_targets)
        authorized_targets = set(evidence.authorized_context_targets)
        if (
            not requested_scope
            or not requested_scope.issubset(authorized_scope)
            or not target_types.issubset(requested_targets)
            or not target_types.issubset(authorized_targets)
        ):
            return OrchestrationFailureCode.AUTHORIZATION_SCOPE_MISMATCH
        return None

    def execute_mutation_set(
        self,
        mutation_set: ContextMutationSet,
        recipe: dict[str, Any],
    ) -> MutationOrchestrationResult:
        """Execute a recipe-bound Context Mutation Set as one recoverable unit."""

        cached = self._orchestration_results.get(mutation_set.idempotency_key)
        if cached is not None:
            cached_digest, cached_result = cached
            if cached_result.status is MutationSetStatus.VERIFIED:
                if cached_digest == mutation_set.payload_digest:
                    return cached_result
                return self._orchestration_result(
                    mutation_set,
                    MutationSetStatus.REJECTED,
                    OrchestrationFailureCode.IDEMPOTENCY_CONFLICT,
                )
            if (
                cached_result.status is not MutationSetStatus.AUTHORIZATION_PENDING
                and cached_digest != mutation_set.payload_digest
            ):
                return self._orchestration_result(
                    mutation_set,
                    MutationSetStatus.REJECTED,
                    OrchestrationFailureCode.IDEMPOTENCY_CONFLICT,
                )

        recipe_failure = self._validate_event_recipe(mutation_set, recipe)
        if recipe_failure is not None:
            return self._remember_orchestration(
                mutation_set,
                self._orchestration_result(
                    mutation_set,
                    MutationSetStatus.REJECTED,
                    recipe_failure,
                ),
            )

        if mutation_set.authority_requirement in {
            AuthorityRequirement.MAKER,
            AuthorityRequirement.MAKER_AND_EVIDENCE,
        }:
            if (
                mutation_set.authorization_request is None
                or mutation_set.authorization_provenance is None
            ):
                return self._remember_orchestration(
                    mutation_set,
                    self._orchestration_result(
                        mutation_set,
                        MutationSetStatus.AUTHORIZATION_PENDING,
                        OrchestrationFailureCode.AUTHORIZATION_REQUIRED,
                    ),
                )
            authorization_failure = self.validate_authorization(
                mutation_set.authorization_request,
                mutation_set.authorization_provenance,
                mutation_set,
            )
            if authorization_failure is not None:
                return self._remember_orchestration(
                    mutation_set,
                    self._orchestration_result(
                        mutation_set,
                        MutationSetStatus.REJECTED,
                        authorization_failure,
                    ),
                )

        prepared: list[tuple[Any, AccessTarget, Path]] = []
        snapshots: dict[str, Any] = {}
        try:
            for target_spec in mutation_set.ordered_targets:
                context_type = ContextType(target_spec.context_type)
                mutation_type = MutationType(target_spec.mutation_intent)
                access_target = AccessTarget(
                    context_type,
                    context_reference=target_spec.context_reference,
                )
                path = self._target_path(access_target)
                snapshot = self.file_store.snapshot(path)
                snapshots[target_spec.context_type] = snapshot
                if (
                    target_spec.expected_before_digest is not None
                    and snapshot.digest != target_spec.expected_before_digest
                ):
                    raise ValueError(f"before digest mismatch: {target_spec.context_type}")
                if mutation_type is MutationType.CREATE_CONTEXT and snapshot.existed:
                    raise ValueError(f"context already exists: {target_spec.context_type}")
                if mutation_type is MutationType.UPDATE_CONTEXT and not snapshot.existed:
                    raise ValueError(f"context does not exist: {target_spec.context_type}")
                maker_authorization = None
                if mutation_set.authorization_provenance is not None:
                    maker_authorization = AuthorizationEvidence(
                        source=RequestSource.MAKER,
                        confirmed=True,
                        reference=mutation_set.authorization_provenance.authorization_id,
                    )
                intent = MutationIntent(
                    mutation_type=mutation_type,
                    target_context=access_target,
                    change_purpose=f"execute {mutation_set.event_type}",
                    change_basis=(
                        "RUNTIME_CONFIRMED_EXECUTION_FACT"
                        if context_type is ContextType.PROJECT_STATE
                        else "MULTI_CONTEXT_EVENT_RECIPE"
                    ),
                    proposed_content=target_spec.proposed_content,
                    proposed_change_reference=mutation_set.event_ref,
                    maker_authorization=maker_authorization,
                )
                request = ContextAccessRequest(
                    request_id=f"{mutation_set.mutation_set_id}:{target_spec.context_type}:preflight",
                    access_target=access_target,
                    access_type=AccessType.REQUEST_MUTATION,
                    request_source=(
                        RequestSource.RUNTIME
                        if mutation_set.requested_by == "RUNTIME"
                        else RequestSource.AGENT
                    ),
                    access_purpose="preflight multi-context mutation",
                    mutation_intent=intent,
                    requirement_reference=mutation_set.event_type,
                )
                preflight = self.request_mutation(request)
                if preflight.status is not ContextAccessResultStatus.ACCEPTED:
                    raise ValueError(
                        preflight.missing_requirement or preflight.decision_reason
                    )
                prepared.append((target_spec, access_target, path))
        except (ValueError, FileStoreError):
            return self._remember_orchestration(
                mutation_set,
                self._orchestration_result(
                    mutation_set,
                    MutationSetStatus.REJECTED,
                    OrchestrationFailureCode.PRECONDITION_CONFLICT,
                ),
            )

        committed: list[str] = []
        failure_code: OrchestrationFailureCode | None = None
        failed_target: str | None = None
        verified_assertions: tuple[str, ...] = ()
        authorization_status: str | None = None
        try:
            for target_spec, _, path in prepared:
                self.file_store.atomic_write(path, target_spec.proposed_content)
                if self.file_store.read_file(path) != target_spec.proposed_content:
                    raise FileStoreError("context read-back mismatch")
                committed.append(target_spec.context_type)

            verified_assertions = self._evaluate_closure(
                mutation_set.closure_assertions,
                prepared,
                snapshots,
            )
            if len(verified_assertions) != len(mutation_set.closure_assertions):
                failure_code = OrchestrationFailureCode.CONTEXT_CLOSURE_FAILED
                raise FileStoreError("context closure failed")

            if mutation_set.authorization_request is not None:
                finalized = self._finalize_authorization_request(
                    mutation_set.authorization_request
                )
                authorization_status = finalized.status
        except FileStoreError:
            if failure_code is None:
                failure_code = OrchestrationFailureCode.COMMIT_FAILED
            if len(committed) < len(prepared):
                failed_target = prepared[len(committed)][0].context_type
            rollback_failed_target = self._rollback_mutation_set(prepared, snapshots)
            if rollback_failed_target is not None:
                return self._remember_orchestration(
                    mutation_set,
                    self._orchestration_result(
                        mutation_set,
                        MutationSetStatus.FAILED,
                        OrchestrationFailureCode.ROLLBACK_FAILED,
                        committed_targets=tuple(committed),
                        rollback_status="FAILED",
                        failed_target=rollback_failed_target,
                    ),
                )
            return self._remember_orchestration(
                mutation_set,
                self._orchestration_result(
                    mutation_set,
                    MutationSetStatus.ROLLED_BACK,
                    failure_code,
                    committed_targets=tuple(committed),
                    rollback_status="RESTORED",
                    failed_target=failed_target,
                ),
            )

        return self._remember_orchestration(
            mutation_set,
            self._orchestration_result(
                mutation_set,
                MutationSetStatus.VERIFIED,
                committed_targets=tuple(committed),
                verified_assertions=verified_assertions,
                authorization_request_status=authorization_status,
            ),
        )

    @staticmethod
    def _validate_event_recipe(
        mutation_set: ContextMutationSet,
        recipe: dict[str, Any],
    ) -> OrchestrationFailureCode | None:
        if recipe.get("authority_requirement") != mutation_set.authority_requirement.value:
            return OrchestrationFailureCode.EVENT_RECIPE_MISMATCH
        actual = [target.context_type for target in mutation_set.ordered_targets]
        required = set(recipe.get("required_targets", ()))
        allowed = set(recipe.get("allowed_targets", ()))
        expected_order = [item for item in recipe.get("commit_order", ()) if item in actual]
        if not required.issubset(actual) or not set(actual).issubset(allowed):
            return OrchestrationFailureCode.EVENT_RECIPE_MISMATCH
        if actual != expected_order:
            return OrchestrationFailureCode.EVENT_RECIPE_MISMATCH
        return None

    def _evaluate_closure(
        self,
        assertions: tuple[ClosureAssertion, ...],
        prepared: list[tuple[Any, AccessTarget, Path]],
        snapshots: dict[str, Any],
    ) -> tuple[str, ...]:
        contents = {
            target_spec.context_type: self.file_store.read_file(path)
            for target_spec, _, path in prepared
        }
        verified: list[str] = []
        for assertion in assertions:
            left = self._resolve_context_ref(assertion.left_ref, contents)
            right = assertion.right_value_or_ref
            if right and "." in right and right.split(".", 1)[0] in contents:
                right = self._resolve_context_ref(right, contents)
            passed = False
            if assertion.operator is ClosureOperator.EQUALS:
                passed = left == right
            elif assertion.operator is ClosureOperator.EXISTS:
                passed = left is not None and left != ""
            elif assertion.operator is ClosureOperator.ABSENT:
                passed = left is None or left == ""
            elif assertion.operator is ClosureOperator.COVERS:
                passed = self._as_value_set(left).issuperset(self._as_value_set(right))
            elif assertion.operator is ClosureOperator.UNCHANGED:
                context_type, field_name = assertion.left_ref.split(".", 1)
                snapshot = snapshots[context_type]
                before = self._field_value(snapshot.content or "", field_name)
                passed = left == before
            if passed:
                verified.append(assertion.assertion_id)
        return tuple(verified)

    @classmethod
    def _resolve_context_ref(cls, reference: str, contents: dict[str, str]) -> str | None:
        context_type, field_name = reference.split(".", 1)
        return cls._field_value(contents.get(context_type, ""), field_name)

    @staticmethod
    def _field_value(content: str, field_name: str) -> str | None:
        pattern = re.compile(
            rf"^\s*(?:[-*]\s*)?(?:\*\*)?{re.escape(field_name)}(?:\*\*)?\s*:\s*(.*?)\s*$",
            re.MULTILINE,
        )
        match = pattern.search(content)
        return match.group(1).strip() if match else None

    @staticmethod
    def _as_value_set(value: str | None) -> set[str]:
        if value is None:
            return set()
        return {item.strip() for item in value.split(",") if item.strip()}

    @staticmethod
    def _finalize_authorization_request(
        pending_request: AuthorizationRequestRecord,
    ) -> AuthorizationRequestRecord:
        return replace(pending_request, status="AUTHORIZED")

    def _rollback_mutation_set(
        self,
        prepared: list[tuple[Any, AccessTarget, Path]],
        snapshots: dict[str, Any],
    ) -> str | None:
        for target_spec, _, _ in reversed(prepared):
            try:
                self.file_store.restore(snapshots[target_spec.context_type])
            except FileStoreError:
                return target_spec.context_type
        return None

    def _remember_orchestration(
        self,
        mutation_set: ContextMutationSet,
        result: MutationOrchestrationResult,
    ) -> MutationOrchestrationResult:
        self._orchestration_results[mutation_set.idempotency_key] = (
            mutation_set.payload_digest,
            result,
        )
        return result

    @staticmethod
    def _orchestration_result(
        mutation_set: ContextMutationSet,
        status: MutationSetStatus,
        failure_code: OrchestrationFailureCode | None = None,
        **kwargs: Any,
    ) -> MutationOrchestrationResult:
        request = mutation_set.authorization_request
        provenance = mutation_set.authorization_provenance
        return MutationOrchestrationResult(
            mutation_set_id=mutation_set.mutation_set_id,
            attempt_id=mutation_set.attempt_id,
            status=status,
            authorization_request_ref=(
                request.authorization_request_id if request is not None else None
            ),
            authorization_evidence_ref=(
                provenance.authorization_id if provenance is not None else None
            ),
            failure_code=failure_code,
            payload_digest=mutation_set.payload_digest,
            **kwargs,
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
