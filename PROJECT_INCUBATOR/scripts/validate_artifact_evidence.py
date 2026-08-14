"""Validate deterministic artifact evidence for Project Incubator V1."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from PROJECT_INCUBATOR.runtime.core.contracts import (
    ScriptExecutionStatus,
    ScriptValidationResult,
)


SCRIPT_IDENTITY = "VALIDATE_ARTIFACT_EVIDENCE"


def validate_artifact_evidence(payload: Mapping[str, Any]) -> dict[str, Any]:
    invocation_id = payload.get("invocation_id")
    if not is_non_empty_string(invocation_id):
        return make_output(
            invocation_id=None,
            execution_status=ScriptExecutionStatus.INVALID_INPUT,
            validation_result=ScriptValidationResult.VALIDATION_NOT_COMPLETED,
            diagnostic_information=[
                diagnostic("Missing Invocation ID", "invocation_id is required"),
            ],
            error_information=error_information(
                ScriptExecutionStatus.INVALID_INPUT,
                "invocation_id is required",
                "invocation_id",
            ),
        )

    input_data = payload.get("input_data")
    input_mapping = input_data if isinstance(input_data, Mapping) else {}

    artifact_reference = payload.get(
        "artifact_reference",
        input_mapping.get("artifact_reference"),
    )
    expected_requirement = payload.get(
        "expected_requirement",
        input_mapping.get("expected_requirement"),
    )
    artifact_path = first_non_empty_string(
        payload.get("artifact_path"),
        input_mapping.get("artifact_path"),
        input_mapping.get("path"),
        nested_value(input_mapping, "artifact_input_data", "path"),
        nested_value(payload, "artifact_input_data", "path"),
    )

    if not is_artifact_reference(artifact_reference):
        return make_invalid_input(
            invocation_id,
            "artifact_reference is required",
            "artifact_reference",
        )
    if not is_expected_requirement(expected_requirement):
        return make_invalid_input(
            invocation_id,
            "expected_requirement is required",
            "expected_requirement",
        )
    if artifact_path is None:
        return make_invalid_input(invocation_id, "artifact path is required", "artifact_path")

    path = Path(artifact_path).expanduser().resolve()
    declared_artifact_identity = declared_identity(artifact_reference)
    expected_conditions = normalize_expected_conditions(expected_requirement)

    try:
        artifact_exists = path.exists()
        artifact_readable = False
        artifact_non_empty = False
        size_bytes: int | None = None

        if artifact_exists:
            artifact_readable = can_read_file(path)
            if artifact_readable:
                size_bytes = path.stat().st_size
                artifact_non_empty = size_bytes > 0
    except OSError as exc:
        return make_execution_error(
            invocation_id,
            "artifact access failed",
            "artifact_path",
            str(exc),
        )

    observed_fact = {
        "artifact_exists": artifact_exists,
        "artifact_readable": artifact_readable,
        "artifact_non_empty": artifact_non_empty,
        "declared_artifact_identity": declared_artifact_identity,
        "artifact_path": str(path),
        "evidence": {
            "size_bytes": size_bytes,
            "expected_requirement": expected_requirement,
        },
    }

    checks = {
        "artifact_exists": artifact_exists if expected_conditions["must_exist"] else True,
        "artifact_readable": artifact_readable if expected_conditions["must_be_readable"] else True,
        "artifact_non_empty": artifact_non_empty if expected_conditions["must_be_non_empty"] else True,
    }
    requirement_satisfied = all(checks.values())
    validation_result = (
        ScriptValidationResult.REQUIREMENT_SATISFIED
        if requirement_satisfied
        else ScriptValidationResult.REQUIREMENT_UNSATISFIED
    )

    diagnostics = []
    if not requirement_satisfied:
        diagnostics.append(
            diagnostic(
                "Artifact Requirement Unsatisfied",
                ", ".join(name for name, matched in checks.items() if not matched),
            ),
        )

    return make_output(
        invocation_id=invocation_id,
        execution_status=ScriptExecutionStatus.COMPLETED,
        validation_result=validation_result,
        evidence=[
            evidence_item(
                requirement_id=requirement_id(expected_requirement),
                validation_target="Artifact",
                observed_fact=observed_fact,
                expected_condition=expected_conditions,
                comparison_result=requirement_satisfied,
            ),
        ],
        diagnostic_information=diagnostics,
        error_information=None,
    )


def can_read_file(path: Path) -> bool:
    if not path.is_file():
        return False
    with open(path, "rb") as file:
        file.read(1)
    return os.access(path, os.R_OK)


def normalize_expected_conditions(expected_requirement: Any) -> dict[str, bool]:
    defaults = {
        "must_exist": True,
        "must_be_readable": True,
        "must_be_non_empty": True,
    }
    if not isinstance(expected_requirement, Mapping):
        return defaults

    normalized = dict(defaults)
    for source_key, target_key in {
        "must_exist": "must_exist",
        "artifact_exists": "must_exist",
        "exists": "must_exist",
        "must_be_readable": "must_be_readable",
        "artifact_readable": "must_be_readable",
        "readable": "must_be_readable",
        "must_be_non_empty": "must_be_non_empty",
        "artifact_non_empty": "must_be_non_empty",
        "non_empty": "must_be_non_empty",
    }.items():
        value = expected_requirement.get(source_key)
        if isinstance(value, bool):
            normalized[target_key] = value
    return normalized


def declared_identity(artifact_reference: Any) -> Any:
    if isinstance(artifact_reference, Mapping):
        for key in ("artifact_id", "id", "name", "artifact_name"):
            value = artifact_reference.get(key)
            if is_non_empty_string(value):
                return value
        return dict(artifact_reference)
    return artifact_reference


def requirement_id(expected_requirement: Any) -> str:
    if isinstance(expected_requirement, Mapping):
        for key in ("requirement_id", "id", "name"):
            value = expected_requirement.get(key)
            if is_non_empty_string(value):
                return value
    if is_non_empty_string(expected_requirement):
        return expected_requirement
    return "Artifact Requirement"


def is_artifact_reference(value: Any) -> bool:
    if is_non_empty_string(value):
        return True
    return isinstance(value, Mapping) and len(value) > 0


def is_expected_requirement(value: Any) -> bool:
    if is_non_empty_string(value):
        return True
    return isinstance(value, Mapping) and len(value) > 0


def nested_value(mapping: Any, parent_key: str, child_key: str) -> Any:
    if not isinstance(mapping, Mapping):
        return None
    parent = mapping.get(parent_key)
    if not isinstance(parent, Mapping):
        return None
    return parent.get(child_key)


def first_non_empty_string(*values: Any) -> str | None:
    for value in values:
        if is_non_empty_string(value):
            return value
    return None


def make_invalid_input(invocation_id: str, reason: str, input_reference: str) -> dict[str, Any]:
    return make_output(
        invocation_id=invocation_id,
        execution_status=ScriptExecutionStatus.INVALID_INPUT,
        validation_result=ScriptValidationResult.VALIDATION_NOT_COMPLETED,
        diagnostic_information=[diagnostic("Invalid Input", reason)],
        error_information=error_information(
            ScriptExecutionStatus.INVALID_INPUT,
            reason,
            input_reference,
        ),
    )


def make_execution_error(
    invocation_id: str,
    reason: str,
    input_reference: str | None,
    detail: str | None = None,
) -> dict[str, Any]:
    diagnostic_detail = reason if detail is None else f"{reason}: {detail.strip()}"
    return make_output(
        invocation_id=invocation_id,
        execution_status=ScriptExecutionStatus.EXECUTION_ERROR,
        validation_result=ScriptValidationResult.VALIDATION_NOT_COMPLETED,
        diagnostic_information=[diagnostic("Execution Error", diagnostic_detail)],
        error_information=error_information(
            ScriptExecutionStatus.EXECUTION_ERROR,
            reason,
            input_reference,
        ),
    )


def make_output(
    invocation_id: str | None,
    execution_status: ScriptExecutionStatus,
    validation_result: ScriptValidationResult,
    evidence: list[dict[str, Any]] | None = None,
    diagnostic_information: list[dict[str, str]] | None = None,
    error_information: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "invocation_id": invocation_id,
        "script_identity": SCRIPT_IDENTITY,
        "execution_status": execution_status.value,
        "validation_result": validation_result.value,
        "evidence": evidence or [],
        "diagnostic_information": diagnostic_information or [],
        "error_information": error_information,
    }


def error_information(
    execution_status: ScriptExecutionStatus,
    reason: str,
    related_input_reference: str | None,
) -> dict[str, Any]:
    error_type = (
        "SCRIPT_EXECUTION_ERROR"
        if execution_status is ScriptExecutionStatus.EXECUTION_ERROR
        else execution_status.value
    )
    return {
        "error_type": error_type,
        "error_reason": reason,
        "related_input_reference": related_input_reference,
        "diagnostic_information": reason,
    }


def evidence_item(
    requirement_id: str,
    validation_target: str,
    observed_fact: Any,
    expected_condition: Any,
    comparison_result: bool,
) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "validation_target": validation_target,
        "observed_fact": observed_fact,
        "expected_condition": expected_condition,
        "comparison_result": "MATCHED" if comparison_result else "NOT_MATCHED",
        "evidence_reference": SCRIPT_IDENTITY,
    }


def diagnostic(condition: str, detail: str) -> dict[str, str]:
    return {
        "detected_condition": condition,
        "detail": detail,
    }


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_payload(raw_payload: str) -> dict[str, Any]:
    parsed = json.loads(raw_payload.lstrip("\ufeff"))
    if not isinstance(parsed, dict):
        raise ValueError("payload must be a JSON object")
    return parsed


def read_raw_payload(args: argparse.Namespace) -> str:
    if args.payload is not None:
        return args.payload
    if args.input_file is not None:
        with open(args.input_file, encoding="utf-8") as file:
            return file.read()
    return sys.stdin.read()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=SCRIPT_IDENTITY)
    parser.add_argument("payload", nargs="?", help="JSON payload string")
    parser.add_argument("--input-file", help="Path to a JSON payload file")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        payload = load_payload(read_raw_payload(args))
        output = validate_artifact_evidence(payload)
    except json.JSONDecodeError as exc:
        output = make_output(
            invocation_id=None,
            execution_status=ScriptExecutionStatus.INVALID_INPUT,
            validation_result=ScriptValidationResult.VALIDATION_NOT_COMPLETED,
            diagnostic_information=[diagnostic("Invalid JSON", str(exc))],
            error_information=error_information(
                ScriptExecutionStatus.INVALID_INPUT,
                "Input payload is not parseable JSON",
                "payload",
            ),
        )
    except ValueError as exc:
        output = make_output(
            invocation_id=None,
            execution_status=ScriptExecutionStatus.INVALID_INPUT,
            validation_result=ScriptValidationResult.VALIDATION_NOT_COMPLETED,
            diagnostic_information=[diagnostic("Invalid Input", str(exc))],
            error_information=error_information(
                ScriptExecutionStatus.INVALID_INPUT,
                str(exc),
                "payload",
            ),
        )
    except Exception as exc:  # pragma: no cover - defensive Script Contract boundary
        output = make_output(
            invocation_id=None,
            execution_status=ScriptExecutionStatus.EXECUTION_ERROR,
            validation_result=ScriptValidationResult.VALIDATION_NOT_COMPLETED,
            diagnostic_information=[diagnostic("Execution Error", str(exc))],
            error_information=error_information(
                ScriptExecutionStatus.EXECUTION_ERROR,
                str(exc),
                None,
            ),
        )

    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
