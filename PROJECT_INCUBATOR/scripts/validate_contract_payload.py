"""Validate deterministic Project Incubator V1 contract payload structure."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Mapping
from enum import Enum
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from PROJECT_INCUBATOR.runtime.core.contracts import (
    GateEvaluationResult,
    ScriptExecutionStatus,
    ScriptValidationResult,
    WorkflowResultStatus,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


SCRIPT_IDENTITY = "VALIDATE_CONTRACT_PAYLOAD"

SUPPORTED_CONTRACT_TYPES = {
    "GATE",
    "GATE_CONTRACT",
    "RUNTIME",
    "RUNTIME_CONTRACT",
    "SCRIPT",
    "SCRIPT_CONTRACT",
    "WORKFLOW",
    "WORKFLOW_CONTRACT",
}

TYPE_CHECKS = {
    "array": list,
    "boolean": bool,
    "integer": int,
    "number": (int, float),
    "object": dict,
    "string": str,
}


def enum_values(enum_type: type[Enum]) -> list[str]:
    return [member.value for member in enum_type]


DEFAULT_ALLOWED_VALUE_SET = {
    "GATE": {
        "evaluation_result": enum_values(GateEvaluationResult),
        "gate_evaluation_result": enum_values(GateEvaluationResult),
        "gate_result": enum_values(GateEvaluationResult),
    },
    "RUNTIME": {
        "runtime_execution_state": enum_values(RuntimeExecutionState),
        "runtime_state": enum_values(RuntimeExecutionState),
    },
    "SCRIPT": {
        "execution_status": enum_values(ScriptExecutionStatus),
        "script_execution_status": enum_values(ScriptExecutionStatus),
        "script_status": enum_values(ScriptExecutionStatus),
        "script_validation_result": enum_values(ScriptValidationResult),
        "validation_result": enum_values(ScriptValidationResult),
    },
    "WORKFLOW": {
        "transition_eligibility_result": enum_values(WorkflowResultStatus),
        "transition_result": enum_values(WorkflowResultStatus),
        "workflow_result": enum_values(WorkflowResultStatus),
        "workflow_result_status": enum_values(WorkflowResultStatus),
    },
}


def validate_contract_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
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
                "Missing Invocation ID",
                "invocation_id",
            ),
        )

    contract_type = payload.get("contract_type")
    if not is_non_empty_string(contract_type):
        return make_invalid_input(invocation_id, "Missing Contract Type", "contract_type")

    normalized_contract_type = normalize_contract_type(contract_type)
    if normalized_contract_type not in SUPPORTED_CONTRACT_TYPES:
        return make_output(
            invocation_id=invocation_id,
            execution_status=ScriptExecutionStatus.UNSUPPORTED_INVOCATION,
            validation_result=ScriptValidationResult.VALIDATION_NOT_COMPLETED,
            diagnostic_information=[
                diagnostic("Unsupported Contract Type", contract_type),
            ],
            error_information=error_information(
                ScriptExecutionStatus.UNSUPPORTED_INVOCATION,
                f"unsupported contract_type: {contract_type}",
                "contract_type",
            ),
        )

    input_data = payload.get("input_data")
    if not isinstance(input_data, Mapping):
        return make_invalid_input(invocation_id, "Input Data must be an object", "input_data")

    required_field_set = payload.get("required_field_set")
    if not is_string_iterable(required_field_set):
        return make_invalid_input(
            invocation_id,
            "Required Field Set must be a list of strings",
            "required_field_set",
        )

    allowed_value_set = payload.get("allowed_value_set")
    if not isinstance(allowed_value_set, Mapping):
        return make_invalid_input(
            invocation_id,
            "Allowed Value Set must be an object",
            "allowed_value_set",
        )

    required_type_set = payload.get("required_type_set", {})
    if not isinstance(required_type_set, Mapping):
        return make_invalid_input(
            invocation_id,
            "Required Type Set must be an object when present",
            "required_type_set",
        )

    contract_family = normalized_contract_type.replace("_CONTRACT", "")
    combined_allowed_value_set = merge_allowed_value_sets(
        DEFAULT_ALLOWED_VALUE_SET.get(contract_family, {}),
        allowed_value_set,
    )

    evidence: list[dict[str, Any]] = []
    diagnostics: list[dict[str, str]] = []
    requirement_satisfied = True

    for field_name in required_field_set:
        field_present = field_name in input_data
        field_non_empty = field_present and not is_empty_required_value(input_data[field_name])
        comparison_result = field_present and field_non_empty
        if not comparison_result:
            requirement_satisfied = False
            reason = "missing required field" if not field_present else "required value is empty"
            diagnostics.append(diagnostic("Required Field Presence", f"{field_name}: {reason}"))
        evidence.append(
            evidence_item(
                requirement_id="Required Field Presence",
                validation_target=field_name,
                observed_fact="present and non-empty" if comparison_result else "missing or empty",
                expected_condition="required field exists and required value is not empty",
                comparison_result=comparison_result,
            ),
        )

    for field_name, expected_type_name in required_type_set.items():
        if field_name not in input_data:
            continue
        type_result = matches_type(input_data[field_name], expected_type_name)
        if not type_result:
            requirement_satisfied = False
            diagnostics.append(
                diagnostic("Basic Data Type", f"{field_name}: expected {expected_type_name}"),
            )
        evidence.append(
            evidence_item(
                requirement_id="Basic Data Type",
                validation_target=field_name,
                observed_fact=type(input_data[field_name]).__name__,
                expected_condition=str(expected_type_name),
                comparison_result=type_result,
            ),
        )

    for field_name, allowed_values in combined_allowed_value_set.items():
        if field_name not in input_data:
            continue
        if not is_string_iterable(allowed_values):
            return make_invalid_input(
                invocation_id,
                f"Allowed values for {field_name} must be a list of strings",
                "allowed_value_set",
            )
        observed_value = input_data[field_name]
        enum_result = isinstance(observed_value, str) and observed_value in set(allowed_values)
        if not enum_result:
            requirement_satisfied = False
            diagnostics.append(
                diagnostic(
                    "Enum Membership",
                    f"{field_name}: {observed_value!r} is not in allowed value set",
                ),
            )
        evidence.append(
            evidence_item(
                requirement_id="Enum Membership",
                validation_target=field_name,
                observed_fact=observed_value,
                expected_condition=tuple(allowed_values),
                comparison_result=enum_result,
            ),
        )

    validation_result = (
        ScriptValidationResult.REQUIREMENT_SATISFIED
        if requirement_satisfied
        else ScriptValidationResult.REQUIREMENT_UNSATISFIED
    )
    return make_output(
        invocation_id=invocation_id,
        execution_status=ScriptExecutionStatus.COMPLETED,
        validation_result=validation_result,
        evidence=evidence,
        diagnostic_information=diagnostics,
        error_information=None,
    )


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


def merge_allowed_value_sets(
    default_allowed_value_set: Mapping[str, Iterable[str]],
    provided_allowed_value_set: Mapping[str, Any],
) -> dict[str, Any]:
    merged = dict(default_allowed_value_set)
    merged.update(provided_allowed_value_set)
    return merged


def normalize_contract_type(contract_type: str) -> str:
    return contract_type.strip().upper().replace(" ", "_").replace("-", "_")


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_string_iterable(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def is_empty_required_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0
    return False


def matches_type(value: Any, expected_type_name: Any) -> bool:
    if not isinstance(expected_type_name, str):
        return False
    normalized_type = expected_type_name.strip().lower()
    if normalized_type == "null":
        return value is None
    expected_type = TYPE_CHECKS.get(normalized_type)
    if expected_type is None:
        return False
    if normalized_type in {"integer", "number"} and isinstance(value, bool):
        return False
    return isinstance(value, expected_type)


def load_payload(raw_payload: str) -> dict[str, Any]:
    parsed = json.loads(raw_payload)
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
        output = validate_contract_payload(payload)
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
