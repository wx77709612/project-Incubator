"""Script process execution adapter for Project Incubator V1 runtime."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ScriptRunnerError(Exception):
    """Raised when the script runner cannot complete deterministic execution."""


class ScriptIdentityResolutionError(ScriptRunnerError):
    """Raised when Script Identity cannot be resolved to a script file."""


class ScriptOutputParseError(ScriptRunnerError):
    """Raised when Script Output cannot be parsed as a Script Contract object."""


@dataclass(frozen=True)
class ScriptProcessResult:
    script_identity: str
    script_path: Path
    process_return_code: int
    raw_stdout: str
    raw_stderr: str
    output: dict[str, Any]


class ScriptRunner:
    """Runs deterministic scripts and parses their JSON Script Output."""

    default_script_registry = {
        "VALIDATE_CONTRACT_PAYLOAD": "validate_contract_payload.py",
        "INSPECT_GIT_EVIDENCE": "inspect_git_evidence.py",
        "VALIDATE_ARTIFACT_EVIDENCE": "validate_artifact_evidence.py",
        "VALIDATE_CONTEXT_INTEGRITY_EVIDENCE": "validate_context_integrity_evidence.py",
        "BOOTSTRAP_HOST_INTEGRATION": "bootstrap_host_integration.py",
    }

    def __init__(
        self,
        script_root: str | Path | None = None,
        python_executable: str | Path | None = None,
        script_registry: dict[str, str | Path] | None = None,
    ) -> None:
        self.script_root = Path(script_root).resolve() if script_root else self.default_script_root()
        self.python_executable = str(python_executable or sys.executable)
        self.script_registry = dict(script_registry or self.default_script_registry)

    @staticmethod
    def default_script_root() -> Path:
        return Path(__file__).resolve().parents[2] / "scripts"

    def resolve_script_identity(self, script_identity: str) -> Path:
        if not isinstance(script_identity, str) or not script_identity.strip():
            raise ScriptIdentityResolutionError("script_identity is required")

        script_location = self.script_registry.get(script_identity.strip())
        if script_location is None:
            raise ScriptIdentityResolutionError(f"unsupported script identity: {script_identity}")

        script_path = Path(script_location)
        if not script_path.is_absolute():
            script_path = self.script_root / script_path
        script_path = script_path.resolve()
        if not script_path.exists() or not script_path.is_file():
            raise ScriptIdentityResolutionError(f"script file is missing: {script_identity}")
        return script_path

    def run(self, script_identity: str, payload: dict[str, Any]) -> ScriptProcessResult:
        script_path = self.resolve_script_identity(script_identity)
        raw_payload = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        process = subprocess.run(
            [self.python_executable, "-B", str(script_path)],
            input=raw_payload,
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )

        if process.returncode != 0:
            raise ScriptRunnerError(
                f"script process exited with code {process.returncode}: {script_identity}",
            )

        try:
            parsed = json.loads(process.stdout)
        except json.JSONDecodeError as exc:
            raise ScriptOutputParseError(f"script output is not JSON: {script_identity}") from exc
        if not isinstance(parsed, dict):
            raise ScriptOutputParseError(f"script output must be an object: {script_identity}")

        return ScriptProcessResult(
            script_identity=script_identity,
            script_path=script_path,
            process_return_code=process.returncode,
            raw_stdout=process.stdout,
            raw_stderr=process.stderr,
            output=parsed,
        )


__all__ = [
    "ScriptIdentityResolutionError",
    "ScriptOutputParseError",
    "ScriptProcessResult",
    "ScriptRunner",
    "ScriptRunnerError",
]
