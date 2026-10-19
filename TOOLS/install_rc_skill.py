"""Legacy / 非现行：显式 V1.1 RC 兼容工具；现行安装使用 Plugin marketplace。"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
import shutil
import sys
import uuid

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from TOOLS.rc_skill_common import RC_SKILL_ID, tree_digest
from TOOLS.verify_rc_skill import verify_rc_skill


class RcInstallError(RuntimeError):
    pass


@dataclass(frozen=True)
class RcInstallResult:
    installed_path: Path
    stable_v1_digest_before: str | None
    stable_v1_digest_after: str | None
    verification_passed: bool


def _optional_digest(path: Path) -> str | None:
    return tree_digest(path) if path.is_dir() else None


def _remove_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def install_rc_skill(
    artifact_root: Path,
    codex_home: Path,
    replace: bool = False,
) -> RcInstallResult:
    artifact_root = Path(artifact_root).resolve()
    codex_home = Path(codex_home).resolve()
    artifact_report = verify_rc_skill(artifact_root)
    if not artifact_report.passed:
        raise RcInstallError("RC artifact verification failed")

    skills_root = codex_home / "skills"
    stable_v1 = skills_root / "project-incubator"
    target = skills_root / RC_SKILL_ID
    stable_before = _optional_digest(stable_v1)
    artifact_digest = tree_digest(artifact_root)

    if target.exists():
        if not target.is_dir():
            raise RcInstallError(f"RC target is not a directory: {target}")
        if tree_digest(target) == artifact_digest:
            installed_report = verify_rc_skill(target)
            if not installed_report.passed:
                raise RcInstallError("Existing identical RC failed verification")
            stable_after = _optional_digest(stable_v1)
            if stable_after != stable_before:
                raise RcInstallError("Stable V1 changed during RC verification")
            return RcInstallResult(target, stable_before, stable_after, True)
        if not replace:
            raise RcInstallError("A different RC is already installed; pass replace=True explicitly")

    skills_root.mkdir(parents=True, exist_ok=True)
    transaction_id = uuid.uuid4().hex
    staging = skills_root / f".{RC_SKILL_ID}.staging-{transaction_id}"
    rollback = skills_root / f".{RC_SKILL_ID}.rollback-{transaction_id}"
    old_rc_moved = False
    new_rc_installed = False

    try:
        shutil.copytree(artifact_root, staging)
        staging_report = verify_rc_skill(staging)
        if not staging_report.passed:
            raise RcInstallError("RC staging verification failed")

        if target.exists():
            target.rename(rollback)
            old_rc_moved = True
        staging.rename(target)
        new_rc_installed = True

        installed_report = verify_rc_skill(target)
        if not installed_report.passed:
            raise RcInstallError("Installed RC verification failed")

        stable_after = _optional_digest(stable_v1)
        if stable_after != stable_before:
            raise RcInstallError("Stable V1 changed during RC installation")

        _remove_directory(rollback)
        return RcInstallResult(target, stable_before, stable_after, True)
    except Exception as exc:
        if new_rc_installed:
            _remove_directory(target)
        _remove_directory(staging)
        if old_rc_moved and rollback.exists():
            rollback.rename(target)
        if isinstance(exc, RcInstallError):
            raise
        raise RcInstallError(f"RC installation failed: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Project Incubator V1.1 RC in parallel")
    parser.add_argument("artifact_root", type=Path)
    parser.add_argument("--codex-home", type=Path, required=True)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    try:
        result = install_rc_skill(args.artifact_root, args.codex_home, args.replace)
    except RcInstallError as exc:
        print(json.dumps({"passed": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    payload = asdict(result)
    payload["installed_path"] = str(result.installed_path)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
