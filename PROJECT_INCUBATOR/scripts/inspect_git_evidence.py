"""Collect deterministic Git evidence for Project Incubator V1 GATE-GIT."""

from __future__ import annotations

import argparse
import json
import subprocess
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


SCRIPT_IDENTITY = "INSPECT_GIT_EVIDENCE"


def inspect_git_evidence(payload: Mapping[str, Any]) -> dict[str, Any]:
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
    repository_path = payload.get("repository_path", input_mapping.get("repository_path"))
    requested_git_operation = payload.get(
        "requested_git_operation",
        input_mapping.get("requested_git_operation"),
    )

    if not is_non_empty_string(repository_path):
        return make_invalid_input(invocation_id, "repository_path is required", "repository_path")
    if not is_non_empty_string(requested_git_operation):
        return make_invalid_input(
            invocation_id,
            "requested_git_operation is required",
            "requested_git_operation",
        )

    repository = Path(repository_path).expanduser().resolve()
    if not repository.exists() or not repository.is_dir():
        return make_execution_error(
            invocation_id,
            "repository_path does not identify an existing directory",
            "repository_path",
        )

    inside_work_tree = run_git(repository, ["rev-parse", "--is-inside-work-tree"])
    if inside_work_tree.returncode != 0 or inside_work_tree.stdout.strip() != "true":
        return make_execution_error(
            invocation_id,
            "repository_path is not a Git repository work tree",
            "repository_path",
            inside_work_tree.stderr,
        )

    branch_result = current_branch(repository)
    if branch_result["error"] is not None:
        return make_execution_error(
            invocation_id,
            branch_result["error"],
            "repository_path",
        )

    status_result = run_git(repository, ["status", "--porcelain=v1"])
    if status_result.returncode != 0:
        return make_execution_error(
            invocation_id,
            "git status evidence collection failed",
            "repository_path",
            status_result.stderr,
        )

    status_lines = status_result.stdout.splitlines()
    git_facts = parse_porcelain_status(status_lines)
    observed_fact = {
        "current_branch": branch_result["branch"],
        "working_tree_change_presence": git_facts["working_tree_change_presence"],
        "untracked_change_presence": git_facts["untracked_change_presence"],
        "staged_change_presence": git_facts["staged_change_presence"],
        "target_operation_reference": requested_git_operation,
        "relevant_git_evidence": {
            "repository_path": str(repository),
            "status_porcelain_v1": status_lines,
            "tracked_change_entries": git_facts["tracked_change_entries"],
            "untracked_change_entries": git_facts["untracked_change_entries"],
        },
    }

    return make_output(
        invocation_id=invocation_id,
        execution_status=ScriptExecutionStatus.COMPLETED,
        validation_result=ScriptValidationResult.REQUIREMENT_SATISFIED,
        evidence=[
            evidence_item(
                requirement_id="GATE-GIT Evidence",
                validation_target="Git repository state",
                observed_fact=observed_fact,
                expected_condition="deterministic Git facts collected",
                comparison_result=True,
            ),
        ],
        diagnostic_information=[],
        error_information=None,
    )


def current_branch(repository: Path) -> dict[str, str | None]:
    branch = run_git(repository, ["branch", "--show-current"])
    if branch.returncode != 0:
        return {"branch": None, "error": "current branch evidence collection failed"}
    branch_name = branch.stdout.strip()
    if branch_name:
        return {"branch": branch_name, "error": None}

    commit = run_git(repository, ["rev-parse", "--short", "HEAD"])
    if commit.returncode != 0:
        return {"branch": None, "error": "detached HEAD evidence collection failed"}
    return {"branch": f"DETACHED:{commit.stdout.strip()}", "error": None}


def parse_porcelain_status(status_lines: list[str]) -> dict[str, Any]:
    tracked_change_entries: list[str] = []
    untracked_change_entries: list[str] = []
    working_tree_change_presence = False
    staged_change_presence = False
    untracked_change_presence = False

    for line in status_lines:
        if line.startswith("??"):
            untracked_change_presence = True
            untracked_change_entries.append(line)
            continue
        if len(line) < 2:
            continue

        index_status = line[0]
        working_tree_status = line[1]
        if index_status not in {" ", "?"}:
            staged_change_presence = True
        if working_tree_status != " ":
            working_tree_change_presence = True
        tracked_change_entries.append(line)

    return {
        "working_tree_change_presence": working_tree_change_presence,
        "untracked_change_presence": untracked_change_presence,
        "staged_change_presence": staged_change_presence,
        "tracked_change_entries": tracked_change_entries,
        "untracked_change_entries": untracked_change_entries,
    }


def run_git(repository: Path, arguments: list[str]) -> subprocess.CompletedProcess[str]:
    safe_repository = str(repository)
    return subprocess.run(
        ["git", "-c", f"safe.directory={safe_repository}", "-C", safe_repository, *arguments],
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
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
        output = inspect_git_evidence(payload)
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
