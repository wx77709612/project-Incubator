"""Validate deterministic context integrity evidence for Project Incubator V1."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from PROJECT_INCUBATOR.runtime.core.contracts import (
    ScriptExecutionStatus,
    ScriptValidationResult,
)


SCRIPT_IDENTITY = "VALIDATE_CONTEXT_INTEGRITY_EVIDENCE"


def validate_context_integrity_evidence(payload: Mapping[str, Any]) -> dict[str, Any]:
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

    required_context_type_set = payload.get(
        "required_context_type_set",
        input_mapping.get("required_context_type_set"),
    )
    context_derived_data = payload.get(
        "context_derived_data",
        input_mapping.get("context_derived_data"),
    )
    declared_context_identity = payload.get(
        "declared_context_identity",
        input_mapping.get("declared_context_identity"),
    )
    required_structural_item = payload.get(
        "required_structural_item",
        input_mapping.get("required_structural_item"),
    )

    required_contexts = normalize_context_type_set(required_context_type_set)
    if required_contexts is None or not required_contexts:
        return make_invalid_input(
            invocation_id,
            "required_context_type_set must be a non-empty list of strings",
            "required_context_type_set",
        )
    if not isinstance(context_derived_data, Mapping):
        return make_invalid_input(
            invocation_id,
            "context_derived_data must be an object provided by Runtime",
            "context_derived_data",
        )
    if not isinstance(declared_context_identity, Mapping):
        return make_invalid_input(
            invocation_id,
            "declared_context_identity must be an object",
            "declared_context_identity",
        )

    structural_requirements = normalize_structural_requirements(
        required_contexts,
        required_structural_item,
    )
    if structural_requirements is None:
        return make_invalid_input(
            invocation_id,
            "required_structural_item must be a string, list of strings, or object",
            "required_structural_item",
        )

    normalized_context_data = normalize_context_data(context_derived_data)
    normalized_declared_identity = normalize_declared_identity(declared_context_identity)
    if not all(context_type in normalized_declared_identity for context_type in required_contexts):
        return make_output(
            invocation_id=invocation_id,
            execution_status=ScriptExecutionStatus.COMPLETED,
            validation_result=ScriptValidationResult.VALIDATION_NOT_COMPLETED,
            evidence=[],
            diagnostic_information=[
                diagnostic(
                    "Validation Not Completed",
                    "declared context identity is missing for required context",
                ),
            ],
            error_information=None,
        )

    required_context_presence = {
        context_type: context_type in normalized_context_data
        for context_type in required_contexts
    }
    missing_context = [
        context_type
        for context_type, present in required_context_presence.items()
        if not present
    ]
    required_structural_item_presence = {
        context_type: {
            item: structural_item_present(
                normalized_context_data.get(context_type),
                item,
            )
            for item in structural_requirements[context_type]
        }
        for context_type in required_contexts
    }
    identity_conflict_evidence = identity_conflicts(
        required_contexts,
        normalized_declared_identity,
    )

    requirement_satisfied = (
        not missing_context
        and not identity_conflict_evidence
        and all(
            all(item_presence.values())
            for item_presence in required_structural_item_presence.values()
        )
    )
    validation_result = (
        ScriptValidationResult.REQUIREMENT_SATISFIED
        if requirement_satisfied
        else ScriptValidationResult.REQUIREMENT_UNSATISFIED
    )
    observed_fact = {
        "required_context_presence": required_context_presence,
        "missing_context": missing_context,
        "required_structural_item_presence": required_structural_item_presence,
        "identity_conflict_evidence": identity_conflict_evidence,
        "declared_context_identity": normalized_declared_identity,
    }

    diagnostics = []
    if missing_context:
        diagnostics.append(diagnostic("Missing Context", ", ".join(missing_context)))
    if identity_conflict_evidence:
        diagnostics.append(diagnostic("Context Identity Conflict", "declared identity mismatch"))
    missing_structural_items = [
        f"{context_type}:{item}"
        for context_type, item_presence in required_structural_item_presence.items()
        for item, present in item_presence.items()
        if not present
    ]
    if missing_structural_items:
        diagnostics.append(
            diagnostic("Missing Required Structural Item", ", ".join(missing_structural_items)),
        )

    return make_output(
        invocation_id=invocation_id,
        execution_status=ScriptExecutionStatus.COMPLETED,
        validation_result=validation_result,
        evidence=[
            evidence_item(
                requirement_id="Context Integrity Requirement",
                validation_target="Context-derived Data",
                observed_fact=observed_fact,
                expected_condition={
                    "required_context_type_set": required_contexts,
                    "required_structural_item": structural_requirements,
                },
                comparison_result=requirement_satisfied,
            ),
        ],
        diagnostic_information=diagnostics,
        error_information=None,
    )


def normalize_context_type_set(value: Any) -> list[str] | None:
    if not isinstance(value, list):
        return None
    normalized: list[str] = []
    for item in value:
        if not is_non_empty_string(item):
            return None
        normalized.append(normalize_context_type(item))
    return normalized


def normalize_context_data(context_derived_data: Mapping[str, Any]) -> dict[str, Any]:
    return {
        normalize_context_type(context_type): data
        for context_type, data in context_derived_data.items()
        if is_non_empty_string(context_type)
    }


def normalize_declared_identity(declared_context_identity: Mapping[str, Any]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for context_type, identity in declared_context_identity.items():
        if is_non_empty_string(context_type) and is_non_empty_string(identity):
            normalized[normalize_context_type(context_type)] = normalize_context_type(identity)
    return normalized


def normalize_structural_requirements(
    required_contexts: list[str],
    value: Any,
) -> dict[str, list[str]] | None:
    if is_non_empty_string(value):
        return {context_type: [value] for context_type in required_contexts}

    if is_string_sequence(value):
        return {context_type: list(value) for context_type in required_contexts}

    if not isinstance(value, Mapping):
        return None

    normalized: dict[str, list[str]] = {}
    for context_type in required_contexts:
        raw_items = value.get(context_type)
        if raw_items is None:
            raw_items = value.get(f"{context_type}.md")
        if raw_items is None:
            raw_items = value.get(context_type.lower())
        if is_non_empty_string(raw_items):
            normalized[context_type] = [raw_items]
        elif is_string_sequence(raw_items):
            normalized[context_type] = list(raw_items)
        else:
            return None
    return normalized


def structural_item_present(context_data: Any, item: str) -> bool:
    if context_data is None:
        return False

    if isinstance(context_data, Mapping):
        structural_items = context_data.get("structural_items")
        if isinstance(structural_items, Mapping):
            return bool(structural_items.get(item))
        if is_string_sequence(structural_items):
            return item in structural_items
        if item in context_data:
            return not is_empty_value(context_data[item])
        content = context_data.get("content")
        if is_non_empty_string(content):
            return item in content
        return False

    if is_non_empty_string(context_data):
        return item in context_data
    if is_string_sequence(context_data):
        return item in context_data
    return False


def identity_conflicts(
    required_contexts: list[str],
    declared_context_identity: Mapping[str, str],
) -> list[dict[str, str]]:
    conflicts: list[dict[str, str]] = []
    for context_type in required_contexts:
        declared_identity = declared_context_identity[context_type]
        if declared_identity != context_type:
            conflicts.append(
                {
                    "context_type": context_type,
                    "declared_context_identity": declared_identity,
                    "expected_context_identity": context_type,
                },
            )
    return conflicts


def normalize_context_type(value: str) -> str:
    normalized = value.strip()
    if normalized.upper().endswith(".MD"):
        normalized = normalized[:-3]
    return normalized.upper().replace("-", "_").replace(" ", "_")


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_string_sequence(value: Any) -> bool:
    return (
        isinstance(value, Sequence)
        and not isinstance(value, (str, bytes, bytearray))
        and all(is_non_empty_string(item) for item in value)
    )


def is_empty_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0
    return False


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
        output = validate_context_integrity_evidence(payload)
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
