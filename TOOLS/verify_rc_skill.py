from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from TOOLS.rc_skill_common import (
    BUILD_MANIFEST_NAME,
    RC_PACKAGE_VERSION,
    RC_SKILL_ID,
    payload_manifest,
    rc_build_identity,
)


@dataclass(frozen=True)
class RcVerificationCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class RcVerificationReport:
    skill_root: Path
    checks: tuple[RcVerificationCheck, ...]
    passed: bool


SMOKE_PAYLOADS: dict[str, dict[str, Any]] = {
    "validate_contract_payload.py": {
        "invocation_id": "rc-contract",
        "contract_type": "WORKFLOW",
        "input_data": {"workflow_result": "READY_FOR_TRANSITION"},
        "required_field_set": ["workflow_result"],
        "allowed_value_set": {},
    },
    "validate_artifact_evidence.py": {
        "invocation_id": "rc-artifact",
        "artifact_reference": {"artifact_id": "rc-smoke-artifact"},
        "artifact_path": "__SMOKE_ARTIFACT__",
        "expected_requirement": {
            "requirement_id": "RC Artifact Mechanical Requirement",
            "must_exist": True,
            "must_be_readable": True,
            "must_be_non_empty": True,
        },
    },
    "inspect_git_evidence.py": {
        "invocation_id": "rc-git",
        "repository_path": "__SMOKE_GIT_REPOSITORY__",
        "requested_git_operation": "status",
    },
    "validate_context_integrity_evidence.py": {
        "invocation_id": "rc-context",
        "required_context_type_set": ["PROJECT_STATE"],
        "context_derived_data": {"PROJECT_STATE": {"Current Phase": "P4"}},
        "declared_context_identity": {"PROJECT_STATE": "PROJECT_STATE.md"},
        "required_structural_item": {"PROJECT_STATE": ["Current Phase"]},
    },
    "bootstrap_host_integration.py": {
        "invocation_id": "rc-bootstrap",
        "invocation_purpose": "DETERMINISTIC_OPERATION",
        "input_data": {"host_environment": "OTHER"},
    },
}


def _clean_environment() -> dict[str, str]:
    retained = (
        "COMSPEC",
        "HOMEDRIVE",
        "HOMEPATH",
        "LOCALAPPDATA",
        "PATH",
        "PATHEXT",
        "SYSTEMDRIVE",
        "SYSTEMROOT",
        "TEMP",
        "TMP",
        "USERPROFILE",
        "WINDIR",
    )
    environment = {name: os.environ[name] for name in retained if name in os.environ}
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONNOUSERSITE"] = "1"
    return environment


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(value, dict):
        return None, "JSON root must be an object"
    return value, None


def _frontmatter_name(path: Path) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, separator, value = line.partition(":")
        if separator and key.strip() == "name":
            return value.strip()
    return None


def _implicit_policy(path: Path) -> bool | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines:
        key, separator, value = line.strip().partition(":")
        if separator and key == "allow_implicit_invocation":
            normalized = value.strip().lower()
            if normalized in {"true", "false"}:
                return normalized == "true"
    return None


def _structure_check(skill_root: Path) -> RcVerificationCheck:
    required = (
        skill_root / "SKILL.md",
        skill_root / "agents" / "openai.yaml",
        skill_root / BUILD_MANIFEST_NAME,
        skill_root / "PROJECT_INCUBATOR" / "runtime" / "config.json",
        skill_root / "PROJECT_INCUBATOR" / "references",
        skill_root / "PROJECT_INCUBATOR" / "scripts",
        skill_root / "PROJECT_INCUBATOR" / "templates",
    )
    missing = [path.relative_to(skill_root).as_posix() for path in required if not path.exists()]
    skill_entries = sorted(
        path.relative_to(skill_root).as_posix()
        for path in skill_root.rglob("SKILL.md")
        if path.is_file()
    )
    unexpected_entries = [path for path in skill_entries if path != "SKILL.md"]
    problems: list[str] = []
    if missing:
        problems.append(f"missing: {', '.join(missing)}")
    if unexpected_entries:
        problems.append(f"unexpected Skill entries: {', '.join(unexpected_entries)}")
    return RcVerificationCheck(
        "package_structure",
        not problems,
        "complete" if not problems else "; ".join(problems),
    )


def _identity_check(skill_root: Path) -> RcVerificationCheck:
    failures: list[str] = []
    if _frontmatter_name(skill_root / "SKILL.md") != RC_SKILL_ID:
        failures.append("SKILL name")
    if _implicit_policy(skill_root / "agents" / "openai.yaml") is not False:
        failures.append("explicit-only policy")

    manifest, manifest_error = _read_json(skill_root / BUILD_MANIFEST_NAME)
    config, config_error = _read_json(
        skill_root / "PROJECT_INCUBATOR" / "runtime" / "config.json"
    )
    if manifest_error or manifest is None:
        failures.append("manifest JSON")
    else:
        if manifest.get("skill_identity") != RC_SKILL_ID:
            failures.append("manifest skill identity")
        if manifest.get("package_version") != RC_PACKAGE_VERSION:
            failures.append("manifest package version")
    if config_error or config is None:
        failures.append("runtime config JSON")
    elif config.get("package_version") != RC_PACKAGE_VERSION:
        failures.append("runtime package version")

    return RcVerificationCheck(
        "identity_consistency",
        not failures,
        "consistent" if not failures else f"invalid: {', '.join(failures)}",
    )


def _manifest_check(skill_root: Path) -> RcVerificationCheck:
    manifest, error = _read_json(skill_root / BUILD_MANIFEST_NAME)
    if error or manifest is None:
        return RcVerificationCheck("manifest_integrity", False, error or "missing manifest")
    actual_files = payload_manifest(skill_root)
    expected_files = manifest.get("files")
    if expected_files != actual_files:
        return RcVerificationCheck("manifest_integrity", False, "payload digest mismatch")
    required_strings = ("source_commit", "built_at", "rc_build_identity")
    if any(not isinstance(manifest.get(key), str) for key in required_strings):
        return RcVerificationCheck("manifest_integrity", False, "manifest metadata missing")
    expected_identity = rc_build_identity(
        manifest["source_commit"],
        manifest["built_at"],
        actual_files,
    )
    if manifest["rc_build_identity"] != expected_identity:
        return RcVerificationCheck("manifest_integrity", False, "build identity mismatch")
    return RcVerificationCheck("manifest_integrity", True, expected_identity)


def _runtime_check(skill_root: Path) -> RcVerificationCheck:
    code = """
import json
from pathlib import Path
import PROJECT_INCUBATOR.runtime.core.coordinator as coordinator_module
from PROJECT_INCUBATOR.runtime.components.definition_resolver import DefinitionResolver
from PROJECT_INCUBATOR.runtime.core.coordinator import RuntimeCoordinator
resolution = DefinitionResolver().resolve()
RuntimeCoordinator()
print(json.dumps({
    "package": str(Path(coordinator_module.__file__).resolve()),
    "resolved": resolution.frozen_definition_set is not None,
}))
"""
    try:
        result = subprocess.run(
            [sys.executable, "-B", "-c", code],
            cwd=skill_root,
            env=_clean_environment(),
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
        payload = json.loads(result.stdout) if result.returncode == 0 else {}
        module_path = Path(payload.get("package", "")).resolve()
        expected_root = (skill_root / "PROJECT_INCUBATOR").resolve()
        passed = (
            result.returncode == 0
            and payload.get("resolved") is True
            and module_path.is_relative_to(expected_root)
        )
        detail = str(module_path) if passed else (result.stderr.strip() or result.stdout.strip())
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        passed = False
        detail = str(exc)
    return RcVerificationCheck("runtime_clean_room", passed, detail)


def _script_checks(skill_root: Path) -> list[RcVerificationCheck]:
    checks: list[RcVerificationCheck] = []
    with TemporaryDirectory(prefix="rc-verifier-") as temp:
        root = Path(temp)
        unrelated = root / "含空格的无关目录"
        unrelated.mkdir()
        artifact = root / "artifact.txt"
        artifact.write_text("rc smoke", encoding="utf-8")
        git_root = root / "repository"
        git_root.mkdir()
        git_result = subprocess.run(
            ["git", "init", "--quiet"],
            cwd=git_root,
            env=_clean_environment(),
            text=True,
            capture_output=True,
            check=False,
        )

        for script_name, template in SMOKE_PAYLOADS.items():
            payload = json.loads(json.dumps(template))
            if payload.get("artifact_path") == "__SMOKE_ARTIFACT__":
                payload["artifact_path"] = str(artifact)
            if payload.get("repository_path") == "__SMOKE_GIT_REPOSITORY__":
                payload["repository_path"] = str(git_root)
            script_path = skill_root / "PROJECT_INCUBATOR" / "scripts" / script_name
            try:
                result = subprocess.run(
                    [sys.executable, "-B", str(script_path)],
                    input=json.dumps(payload),
                    cwd=unrelated,
                    env=_clean_environment(),
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=30,
                )
                output = json.loads(result.stdout) if result.returncode == 0 else {}
                passed = (
                    result.returncode == 0
                    and isinstance(output, dict)
                    and output.get("execution_status") != "EXECUTION_ERROR"
                )
                detail = output.get("execution_status", result.stderr.strip() or "invalid output")
            except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
                passed = False
                detail = str(exc)
            if script_name == "inspect_git_evidence.py" and git_result.returncode != 0:
                passed = False
                detail = git_result.stderr.strip() or "git init failed"
            checks.append(RcVerificationCheck(f"script:{script_name}", passed, str(detail)))
    return checks


def verify_rc_skill(skill_root: Path) -> RcVerificationReport:
    skill_root = Path(skill_root).resolve()
    checks = [
        _structure_check(skill_root),
        _identity_check(skill_root),
        _manifest_check(skill_root),
        _runtime_check(skill_root),
        *_script_checks(skill_root),
    ]
    return RcVerificationReport(
        skill_root=skill_root,
        checks=tuple(checks),
        passed=all(check.passed for check in checks),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a Project Incubator V1.1 RC skill")
    parser.add_argument("skill_root", type=Path)
    args = parser.parse_args()
    report = verify_rc_skill(args.skill_root)
    print(
        json.dumps(
            {
                "skill_root": str(report.skill_root),
                "passed": report.passed,
                "checks": [asdict(check) for check in report.checks],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
