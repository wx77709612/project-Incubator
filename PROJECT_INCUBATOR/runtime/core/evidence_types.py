"""Shared V1.1 evidence and correction domain types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Iterable


class _StringEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class EvidenceLevel(_StringEnum):
    E0 = "E0"
    E1 = "E1"
    E2 = "E2"
    E3 = "E3"
    E4 = "E4"
    E5 = "E5"


class ClaimStatus(_StringEnum):
    HYPOTHESIZED = "HYPOTHESIZED"
    LOCALLY_VERIFIED = "LOCALLY_VERIFIED"
    OBSERVED_WORKING = "OBSERVED_WORKING"
    MECHANISM_SUPPORTED = "MECHANISM_SUPPORTED"
    REPRESENTATIVE_BOUNDARY_VALIDATED = "REPRESENTATIVE_BOUNDARY_VALIDATED"
    PENDING_LONG_TERM_VALIDATION = "PENDING_LONG_TERM_VALIDATION"
    INVALIDATED = "INVALIDATED"


class AssumptionStatus(_StringEnum):
    UNTESTED = "UNTESTED"
    SUPPORTED = "SUPPORTED"
    WEAKENED = "WEAKENED"
    INVALIDATED = "INVALIDATED"
    RETIRED = "RETIRED"


class BaselineStatus(_StringEnum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    REGRESSED = "REGRESSED"
    SUPERSEDED = "SUPERSEDED"


class OpacityLevel(_StringEnum):
    LOW = "LOW"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class CorrectionResult(_StringEnum):
    NO_CORRECTION = "NO_CORRECTION"
    MODEL_REVIEW_ADVISORY = "MODEL_REVIEW_ADVISORY"
    P4_CORRECTION_REQUIRED = "P4_CORRECTION_REQUIRED"
    MAKER_SCOPE_REVIEW_REQUIRED = "MAKER_SCOPE_REVIEW_REQUIRED"
    CORRECTION_ASSESSMENT_INVALID = "CORRECTION_ASSESSMENT_INVALID"


class CorrectionActivityState(_StringEnum):
    NORMAL_CREATION = "NORMAL_CREATION"
    CORRECTION_REVIEW = "CORRECTION_REVIEW"
    CORRECTION_ACTIVE = "CORRECTION_ACTIVE"
    AWAITING_MAKER_SCOPE_REVIEW = "AWAITING_MAKER_SCOPE_REVIEW"


@dataclass(frozen=True)
class FailureObservation:
    capability_id: str
    scenario_id: str
    boundary_step: str
    observed_outcome: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("capability_id", self.capability_id),
            ("scenario_id", self.scenario_id),
            ("boundary_step", self.boundary_step),
            ("observed_outcome", self.observed_outcome),
        ):
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string")
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty")


def failure_signature(
    observation_or_capability_id: FailureObservation | str,
    scenario_id: str | None = None,
    boundary_step: str | None = None,
    observed_outcome: str | None = None,
) -> str:
    """Return a stable signature containing observations, never causal guesses."""
    if isinstance(observation_or_capability_id, FailureObservation):
        if any(value is not None for value in (scenario_id, boundary_step, observed_outcome)):
            raise TypeError("individual fields cannot accompany FailureObservation")
        observation = observation_or_capability_id
    else:
        if scenario_id is None or boundary_step is None or observed_outcome is None:
            raise TypeError("all four stable failure fields are required")
        observation = FailureObservation(
            capability_id=observation_or_capability_id,
            scenario_id=scenario_id,
            boundary_step=boundary_step,
            observed_outcome=observed_outcome,
        )

    payload = json.dumps(
        [
            observation.capability_id,
            observation.scenario_id,
            observation.boundary_step,
            observation.observed_outcome,
        ],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_thresholds(*, advisory: int, correction: int) -> tuple[int, int]:
    """Validate defaults or stricter profile thresholds."""
    if isinstance(advisory, bool) or not isinstance(advisory, int):
        raise TypeError("advisory must be an integer")
    if isinstance(correction, bool) or not isinstance(correction, int):
        raise TypeError("correction must be an integer")
    if not 1 <= advisory < correction:
        raise ValueError("thresholds must satisfy 1 <= advisory < correction")
    if advisory > 2 or correction > 3:
        raise ValueError("profiles may trigger correction earlier, not later")
    return advisory, correction


def extension_recommended(levels: Iterable[OpacityLevel]) -> bool:
    """Apply the structural opacity recommendation rule."""
    elevated_count = 0
    for level in levels:
        if not isinstance(level, OpacityLevel):
            raise TypeError("opacity dimensions must use OpacityLevel")
        if level in {OpacityLevel.HIGH, OpacityLevel.UNKNOWN}:
            return True
        if level is OpacityLevel.ELEVATED:
            elevated_count += 1
    return elevated_count >= 2
