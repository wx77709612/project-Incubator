"""Frozen Project Incubator V1 contract status types."""

from __future__ import annotations

from enum import Enum


class ContextAccessResultStatus(Enum):
    """Context Access Contract result status."""

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    AUTHORIZATION_REQUIRED = "AUTHORIZATION_REQUIRED"
    GATE_REQUIREMENT_UNRESOLVED = "GATE_REQUIREMENT_UNRESOLVED"
    BOUNDARY_VIOLATION = "BOUNDARY_VIOLATION"
    CONTEXT_CONFLICT = "CONTEXT_CONFLICT"


class WorkflowResultStatus(Enum):
    """Workflow Contract transition eligibility result."""

    NOT_READY = "NOT_READY"
    READY_FOR_TRANSITION = "READY_FOR_TRANSITION"
    TRANSITION_NOT_ALLOWED = "TRANSITION_NOT_ALLOWED"


class GateEvaluationResult(Enum):
    """Gate Contract evaluation result."""

    REQUIREMENT_SATISFIED = "REQUIREMENT_SATISFIED"
    REQUIREMENT_UNSATISFIED = "REQUIREMENT_UNSATISFIED"
    AUTHORIZATION_REQUIRED = "AUTHORIZATION_REQUIRED"
    EVIDENCE_INSUFFICIENT = "EVIDENCE_INSUFFICIENT"
    ACTION_BLOCKED = "ACTION_BLOCKED"


class ScriptExecutionStatus(Enum):
    """Script Contract execution status."""

    COMPLETED = "COMPLETED"
    INVALID_INPUT = "INVALID_INPUT"
    UNSUPPORTED_INVOCATION = "UNSUPPORTED_INVOCATION"
    EXECUTION_ERROR = "EXECUTION_ERROR"


class ScriptValidationResult(Enum):
    """Script Contract validation result."""

    REQUIREMENT_SATISFIED = "REQUIREMENT_SATISFIED"
    REQUIREMENT_UNSATISFIED = "REQUIREMENT_UNSATISFIED"
    VALIDATION_NOT_COMPLETED = "VALIDATION_NOT_COMPLETED"


__all__ = [
    "ContextAccessResultStatus",
    "GateEvaluationResult",
    "ScriptExecutionStatus",
    "ScriptValidationResult",
    "WorkflowResultStatus",
]
