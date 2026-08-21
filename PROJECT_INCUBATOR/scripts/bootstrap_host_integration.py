"""Bootstrap host-specific Project Incubator integration artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from PROJECT_INCUBATOR.runtime.core.contracts import (
    ScriptExecutionStatus,
    ScriptValidationResult,
)


SCRIPT_IDENTITY = "BOOTSTRAP_HOST_INTEGRATION"
INTEGRATION_MARKER = "<!-- project-incubator:codex-integration -->"

RESULT_CREATED = "CREATED"
RESULT_ALREADY_INTEGRATED = "ALREADY_INTEGRATED"
RESULT_INTEGRATION_REQUIRED = "INTEGRATION_REQUIRED"
RESULT_NOT_APPLICABLE = "NOT_APPLICABLE"
RESULT_HOST_UNKNOWN = "HOST_UNKNOWN"

SUPPORTED_HOST_RESULTS = {"CODEX", "OTHER", "UNKNOWN"}


def bootstrap_host_integration(payload: Mapping[str, Any]) -> dict[str, Any]:
    invocation_id = payload.get("invocation_id")
    if not is_non_empty_string(invocation_id):
        return invalid_input(None, "invocation_id is required", "invocation_id")

    if payload.get("invocation_purpose") != "DETERMINISTIC_OPERATION":
        return make_output(
            invocation_id=invocation_id,
            execution_status=ScriptExecutionStatus.UNSUPPORTED_INVOCATION,
            validation_result=ScriptValidationResult.VALIDATION_NOT_COMPLETED,
            diagnostic_information=[
                diagnostic(
                    "Unsupported Invocation",
                    "BOOTSTRAP_HOST_INTEGRATION only supports DETERMINISTIC_OPERATION",
                ),
            ],
            error_information=error_information(
                ScriptExecutionStatus.UNSUPPORTED_INVOCATION,
                "invocation_purpose is not supported",
                "invocation_purpose",
            ),
        )

    input_data = payload.get("input_data")
    if not isinstance(input_data, Mapping):
        return invalid_input(invocation_id, "input_data must be an object", "input_data")

    host_environment = input_data.get("host_environment")
    if not is_non_empty_string(host_environment):
        return invalid_input(
            invocation_id,
            "host_environment is required and must be CODEX, OTHER, or UNKNOWN",
            "input_data.host_environment",
        )

    host_result = host_environment.strip().upper()
    if host_result not in SUPPORTED_HOST_RESULTS:
        return invalid_input(
            invocation_id,
            "host_environment must be CODEX, OTHER, or UNKNOWN",
            "input_data.host_environment",
        )

    if host_result == "OTHER":
        return completed_operation(invocation_id, RESULT_NOT_APPLICABLE, "Host is not Codex")
    if host_result == "UNKNOWN":
        return completed_operation(invocation_id, RESULT_HOST_UNKNOWN, "Host is unknown")

    project_root_value = input_data.get("managed_project_root")
    if not is_non_empty_string(project_root_value):
        return invalid_input(
            invocation_id,
            "managed_project_root is required for CODEX host integration",
            "input_data.managed_project_root",
        )

    project_root = Path(project_root_value).expanduser().resolve()
    if not project_root.exists() or not project_root.is_dir():
        return invalid_input(
            invocation_id,
            "managed_project_root must be an existing directory",
            "input_data.managed_project_root",
        )

    agents_path = project_root / "AGENTS.md"
    if not agents_path.exists():
        template_content = template_path().read_text(encoding="utf-8")
        agents_path.write_text(template_content, encoding="utf-8")
        return completed_operation(invocation_id, RESULT_CREATED, "Codex AGENTS.md created")

    existing_content = agents_path.read_text(encoding="utf-8")
    if INTEGRATION_MARKER in existing_content:
        return completed_operation(
            invocation_id,
            RESULT_ALREADY_INTEGRATED,
            "Codex AGENTS.md already contains Project Incubator integration marker",
        )

    return completed_operation(
        invocation_id,
        RESULT_INTEGRATION_REQUIRED,
        "Existing AGENTS.md must be integrated manually without automatic overwrite",
    )


def template_path() -> Path:
    return (
        Path(__file__).resolve().parents[1]
        / "templates"
        / "integrations"
        / "codex"
        / "AGENTS.template.md"
    )


def completed_operation(invocation_id: str, result: str, detail: str) -> dict[str, Any]:
    return make_output(
        invocation_id=invocation_id,
        execution_status=ScriptExecutionStatus.COMPLETED,
        validation_result=None,
        evidence=[
            {
                "requirement_id": "Host Integration Bootstrap Result",
                "validation_target": "AGENTS.md",
                "observed_fact": result,
                "expected_condition": "deterministic host integration result",
                "comparison_result": "OBSERVED",
                "evidence_reference": SCRIPT_IDENTITY,
            },
        ],
        diagnostic_information=[diagnostic("Bootstrap Result", detail)],
        error_information=None,
    )


def invalid_input(
    invocation_id: str | None,
    reason: str,
    related_input_reference: str,
) -> dict[str, Any]:
    return make_output(
        invocation_id=invocation_id,
        execution_status=ScriptExecutionStatus.INVALID_INPUT,
        validation_result=ScriptValidationResult.VALIDATION_NOT_COMPLETED,
        diagnostic_information=[diagnostic("Invalid Input", reason)],
        error_information=error_information(
            ScriptExecutionStatus.INVALID_INPUT,
            reason,
            related_input_reference,
        ),
    )


def make_output(
    invocation_id: str | None,
    execution_status: ScriptExecutionStatus,
    validation_result: ScriptValidationResult | None,
    evidence: list[dict[str, Any]] | None = None,
    diagnostic_information: list[dict[str, str]] | None = None,
    error_information: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "invocation_id": invocation_id,
        "script_identity": SCRIPT_IDENTITY,
        "execution_status": execution_status.value,
        "validation_result": "" if validation_result is None else validation_result.value,
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


def diagnostic(condition: str, detail: str) -> dict[str, str]:
    return {
        "detected_condition": condition,
        "detail": detail,
    }


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


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
        output = bootstrap_host_integration(load_payload(read_raw_payload(args)))
    except json.JSONDecodeError as exc:
        output = invalid_input(None, "Input payload is not parseable JSON", "payload")
        output["diagnostic_information"] = [diagnostic("Invalid JSON", str(exc))]
    except ValueError as exc:
        output = invalid_input(None, str(exc), "payload")
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
