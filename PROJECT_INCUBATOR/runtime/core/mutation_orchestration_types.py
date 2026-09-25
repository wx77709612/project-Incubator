"""Frozen domain types for multi-context mutation orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any


class AuthorityRequirement(Enum):
    NONE = "NONE"
    MAKER = "MAKER"
    EVIDENCE = "EVIDENCE"
    MAKER_AND_EVIDENCE = "MAKER_AND_EVIDENCE"


class ExtensionStatus(Enum):
    PROPOSED = "PROPOSED"
    PENDING_MAKER_AUTHORIZATION = "PENDING_MAKER_AUTHORIZATION"
    ACTIVE = "ACTIVE"
    DECLINED = "DECLINED"
    SUSPENDED = "SUSPENDED"


class MutationSetStatus(Enum):
    DRAFT = "DRAFT"
    AUTHORIZATION_PENDING = "AUTHORIZATION_PENDING"
    READY = "READY"
    STAGED = "STAGED"
    COMMITTING = "COMMITTING"
    FINALIZING_AUTHORIZATION = "FINALIZING_AUTHORIZATION"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    ROLLED_BACK = "ROLLED_BACK"
    SUSPENDED = "SUSPENDED"
    FAILED = "FAILED"


class ClosureOperator(Enum):
    EQUALS = "EQUALS"
    EXISTS = "EXISTS"
    ABSENT = "ABSENT"
    COVERS = "COVERS"
    UNCHANGED = "UNCHANGED"


class OrchestrationFailureCode(Enum):
    MUTATION_SET_INVALID = "MUTATION_SET_INVALID"
    EVENT_RECIPE_MISMATCH = "EVENT_RECIPE_MISMATCH"
    AUTHORIZATION_REQUIRED = "AUTHORIZATION_REQUIRED"
    AUTHORIZATION_INVALID = "AUTHORIZATION_INVALID"
    AUTHORIZATION_SCOPE_MISMATCH = "AUTHORIZATION_SCOPE_MISMATCH"
    PRECONDITION_CONFLICT = "PRECONDITION_CONFLICT"
    STAGE_FAILED = "STAGE_FAILED"
    COMMIT_FAILED = "COMMIT_FAILED"
    CONTEXT_CLOSURE_FAILED = "CONTEXT_CLOSURE_FAILED"
    ROLLBACK_FAILED = "ROLLBACK_FAILED"
    IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"


@dataclass(frozen=True)
class AuthorizationRequestRecord:
    authorization_request_id: str
    event_type: str
    event_ref: str
    requested_decision: str
    requested_scope: tuple[str, ...]
    requested_context_targets: tuple[str, ...]
    cost_summary: str
    risk_summary: str
    unsupported_boundary: tuple[str, ...]
    status: str = "PENDING"


@dataclass(frozen=True)
class AuthorizationProvenance:
    authorization_id: str
    authorization_request_id: str
    source_actor: str
    source_message_ref: str
    source_message_role: str
    maker_statement_excerpt: str
    authorized_scope: tuple[str, ...]
    authorized_context_targets: tuple[str, ...]
    confirmed_at: str
    statement_digest: str


@dataclass(frozen=True)
class MutationTargetSpec:
    context_type: str
    mutation_intent: str
    proposed_content: str
    commit_order: int
    context_reference: str | None = None
    expected_before_digest: str | None = None
    required_refs: tuple[str, ...] = field(default_factory=tuple)

    @property
    def identity(self) -> tuple[str, str | None]:
        return self.context_type, self.context_reference


@dataclass(frozen=True)
class ClosureAssertion:
    assertion_id: str
    left_ref: str
    operator: ClosureOperator
    right_value_or_ref: str | None = None
    severity: str = "REQUIRED"


@dataclass(frozen=True)
class ContextMutationSet:
    mutation_set_id: str
    event_type: str
    event_ref: str
    current_phase: str
    requested_by: str
    authority_requirement: AuthorityRequirement
    targets: tuple[MutationTargetSpec, ...]
    closure_assertions: tuple[ClosureAssertion, ...]
    attempt_id: str = "attempt-1"
    authorization_request: AuthorizationRequestRecord | None = None
    authorization_provenance: AuthorizationProvenance | None = None
    rollback_policy: str = "RESTORE_ALL"

    def __post_init__(self) -> None:
        for name in (
            "mutation_set_id",
            "event_type",
            "event_ref",
            "current_phase",
            "requested_by",
            "attempt_id",
        ):
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ValueError(f"{name} is required")
        if self.requested_by not in {"AGENT", "RUNTIME"}:
            raise ValueError("requested_by must be AGENT or RUNTIME")
        if self.rollback_policy != "RESTORE_ALL":
            raise ValueError("rollback_policy must be RESTORE_ALL")
        if not self.targets:
            raise ValueError("at least one mutation target is required")
        identities = [target.identity for target in self.targets]
        if len(identities) != len(set(identities)):
            raise ValueError("duplicate mutation target")
        commit_orders = [target.commit_order for target in self.targets]
        if any(not isinstance(order, int) or order < 0 for order in commit_orders):
            raise ValueError("commit_order must be a non-negative integer")
        if len(commit_orders) != len(set(commit_orders)):
            raise ValueError("duplicate commit_order")
        state_targets = [
            target for target in self.targets if target.context_type == "PROJECT_STATE"
        ]
        if state_targets and state_targets[0].commit_order != max(commit_orders):
            raise ValueError("PROJECT_STATE must commit last")
        assertion_ids = [item.assertion_id for item in self.closure_assertions]
        if not assertion_ids or any(not item for item in assertion_ids):
            raise ValueError("closure assertion is required")
        if len(assertion_ids) != len(set(assertion_ids)):
            raise ValueError("duplicate closure assertion")

    @property
    def ordered_targets(self) -> tuple[MutationTargetSpec, ...]:
        return tuple(sorted(self.targets, key=lambda target: target.commit_order))

    @property
    def idempotency_key(self) -> str:
        return f"{self.mutation_set_id}:{self.event_type}:{self.event_ref}"

    @property
    def payload_digest(self) -> str:
        payload = _canonical(asdict(self))
        encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class MutationOrchestrationResult:
    mutation_set_id: str
    attempt_id: str
    status: MutationSetStatus
    committed_targets: tuple[str, ...] = field(default_factory=tuple)
    verified_assertions: tuple[str, ...] = field(default_factory=tuple)
    authorization_request_ref: str | None = None
    authorization_evidence_ref: str | None = None
    authorization_request_status: str | None = None
    rollback_status: str | None = None
    failure_code: OrchestrationFailureCode | None = None
    failed_target: str | None = None
    payload_digest: str | None = None


def normalize_authorization_statement(statement: str) -> str:
    """Normalize only transport-level differences without rewriting Maker meaning."""

    return statement.replace("\r\n", "\n").replace("\r", "\n").strip()


def authorization_statement_digest(statement: str) -> str:
    normalized = normalize_authorization_statement(statement)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _canonical(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


__all__ = [
    "AuthorityRequirement",
    "AuthorizationProvenance",
    "AuthorizationRequestRecord",
    "ClosureAssertion",
    "ClosureOperator",
    "ContextMutationSet",
    "ExtensionStatus",
    "MutationOrchestrationResult",
    "MutationSetStatus",
    "MutationTargetSpec",
    "OrchestrationFailureCode",
    "authorization_statement_digest",
    "normalize_authorization_statement",
]
