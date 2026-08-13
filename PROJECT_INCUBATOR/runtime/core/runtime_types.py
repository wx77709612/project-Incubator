"""Project Incubator V1 runtime execution types."""

from __future__ import annotations

from enum import Enum


class RuntimeExecutionState(Enum):
    """Runtime Specification execution state."""

    EXECUTING = "EXECUTING"
    WAITING_FOR_MAKER = "WAITING_FOR_MAKER"
    BLOCKED_BY_GATE = "BLOCKED_BY_GATE"
    SUSPENDED = "SUSPENDED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


__all__ = ["RuntimeExecutionState"]
