from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable


RC_SKILL_ID = "project-incubator-v1-1-rc"
RC_PACKAGE_VERSION = "1.1.0-rc.1"
PAYLOAD_EXCLUDED_DIRS = {"__pycache__", ".git", "TESTS", "ACCEPTANCE_TESTS"}
PAYLOAD_EXCLUDED_SUFFIXES = {".pyc"}
BUILD_MANIFEST_NAME = "BUILD_MANIFEST.json"


def _is_excluded(path: Path, root: Path, excluded_names: set[str]) -> bool:
    relative = path.relative_to(root)
    parts = relative.parts
    if any(part in excluded_names for part in parts):
        return True
    if path.suffix in PAYLOAD_EXCLUDED_SUFFIXES:
        return True
    return any(
        part == "SPECS" and index + 1 < len(parts) and parts[index + 1].startswith("_V")
        for index, part in enumerate(parts)
    )


def payload_manifest(root: Path) -> dict[str, str]:
    root = Path(root).resolve()
    files: dict[str, str] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or path.name == BUILD_MANIFEST_NAME:
            continue
        relative = path.relative_to(root).as_posix()
        files[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def tree_digest(root: Path, excluded_names: Iterable[str] = ()) -> str:
    root = Path(root).resolve()
    excluded = set(excluded_names)
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or _is_excluded(path, root, excluded):
            continue
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        content = path.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()
