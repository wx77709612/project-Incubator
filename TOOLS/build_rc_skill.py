from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from TOOLS.rc_skill_common import (
    BUILD_MANIFEST_NAME,
    PAYLOAD_EXCLUDED_DIRS,
    PAYLOAD_EXCLUDED_SUFFIXES,
    RC_PACKAGE_VERSION,
    RC_SKILL_ID,
    payload_manifest,
    rc_build_identity,
)


@dataclass(frozen=True)
class RcBuildResult:
    skill_root: Path
    manifest_path: Path
    build_identity: str


def _validate_source(source_root: Path) -> None:
    required = (
        source_root / "SKILL.md",
        source_root / "runtime" / "config.json",
        source_root / "references",
        source_root / "scripts",
        source_root / "templates",
    )
    missing = [str(path.relative_to(source_root)) for path in required if not path.exists()]
    if missing:
        raise ValueError(f"RC source is incomplete: {', '.join(missing)}")


def _is_source_payload(path: Path, source_root: Path) -> bool:
    relative = path.relative_to(source_root)
    if relative == Path("SKILL.md"):
        return False
    parts = relative.parts
    if any(part in PAYLOAD_EXCLUDED_DIRS for part in parts):
        return False
    if path.suffix in PAYLOAD_EXCLUDED_SUFFIXES:
        return False
    return not any(
        part == "SPECS" and index + 1 < len(parts) and parts[index + 1].startswith("_V")
        for index, part in enumerate(parts)
    )


def _copy_source_payload(source_root: Path, target_root: Path) -> None:
    for source_path in sorted(source_root.rglob("*"), key=lambda item: item.as_posix()):
        if not _is_source_payload(source_path, source_root):
            continue
        relative = source_path.relative_to(source_root)
        target_path = target_root / relative
        if source_path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
        elif source_path.is_file():
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target_path)


def _render_rc_skill(source_skill: Path) -> str:
    text = source_skill.read_text(encoding="utf-8")
    identity_line = "name: project-incubator\n"
    if identity_line not in text:
        raise ValueError("Source SKILL.md does not declare name: project-incubator")
    text = text.replace(identity_line, f"name: {RC_SKILL_ID}\n", 1)
    frontmatter_end = text.find("\n---", 4)
    if frontmatter_end < 0:
        raise ValueError("Source SKILL.md has invalid frontmatter")
    insert_at = frontmatter_end + len("\n---")
    rc_notice = (
        "\n\n## RC 身份约束\n\n"
        f"- Skill 标识：`{RC_SKILL_ID}`。\n"
        f"- Package Version：`{RC_PACKAGE_VERSION}`。\n"
        "- 本候选版本仅允许显式调用，不参与隐式路由。\n"
        "- 若任务要求的 Skill 标识或版本与上述值不一致，必须停止并向 Maker 报告。\n"
    )
    return text[:insert_at] + rc_notice + text[insert_at:]


def _render_openai_yaml() -> str:
    return (
        "interface:\n"
        "  display_name: Project Incubator V1.1 RC\n"
        "  short_description: 显式调用的 Project Incubator V1.1 发布候选包\n"
        f"  default_prompt: Use ${RC_SKILL_ID} to manage this project with the V1.1 RC workflow.\n"
        "policy:\n"
        "  allow_implicit_invocation: false\n"
    )


def _rewrite_runtime_version(config_path: Path) -> None:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["package_version"] = RC_PACKAGE_VERSION
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _rewrite_codex_integration_template(template_path: Path) -> None:
    text = template_path.read_text(encoding="utf-8")
    stable_trigger = "`project-incubator` Skill"
    if stable_trigger not in text:
        raise ValueError("Codex AGENTS template is missing the stable Skill trigger")
    text = text.replace(stable_trigger, f"`{RC_SKILL_ID}` Skill", 1)
    heading = "# AGENTS.md\n"
    if heading not in text:
        raise ValueError("Codex AGENTS template is missing its document heading")
    binding = (
        "\n## Required Skill Binding\n\n"
        f"Required Skill: {RC_SKILL_ID}\n\n"
        f"Required Package Version: {RC_PACKAGE_VERSION}\n\n"
        "Invocation Policy: explicit-only\n"
    )
    template_path.write_text(
        text.replace(heading, heading + binding, 1),
        encoding="utf-8",
    )


def build_rc_skill(
    source_root: Path,
    output_parent: Path,
    source_commit: str,
    built_at: str,
) -> RcBuildResult:
    source_root = Path(source_root).resolve()
    output_parent = Path(output_parent).resolve()
    _validate_source(source_root)

    try:
        output_parent.relative_to(source_root)
    except ValueError:
        pass
    else:
        raise ValueError("RC output must not be inside the source package")

    output_parent.mkdir(parents=True, exist_ok=True)
    final_root = output_parent / RC_SKILL_ID
    staging_root = output_parent / f".{RC_SKILL_ID}.staging"
    if final_root.exists():
        raise FileExistsError(f"RC output already exists: {final_root}")
    if staging_root.exists():
        shutil.rmtree(staging_root)

    nested_root = staging_root / "PROJECT_INCUBATOR"
    try:
        nested_root.mkdir(parents=True)
        _copy_source_payload(source_root, nested_root)
        _rewrite_runtime_version(nested_root / "runtime" / "config.json")
        _rewrite_codex_integration_template(
            nested_root / "templates" / "integrations" / "codex" / "AGENTS.template.md"
        )

        (staging_root / "SKILL.md").write_text(
            _render_rc_skill(source_root / "SKILL.md"),
            encoding="utf-8",
        )
        agents_dir = staging_root / "agents"
        agents_dir.mkdir()
        (agents_dir / "openai.yaml").write_text(_render_openai_yaml(), encoding="utf-8")

        files = payload_manifest(staging_root)
        build_identity = rc_build_identity(source_commit, built_at, files)
        manifest = {
            "skill_identity": RC_SKILL_ID,
            "package_version": RC_PACKAGE_VERSION,
            "rc_build_identity": build_identity,
            "source_commit": source_commit,
            "built_at": built_at,
            "files": files,
            "excluded_patterns": [
                ".git/",
                "__pycache__/",
                "*.pyc",
                "TESTS/",
                "ACCEPTANCE_TESTS/",
                "SPECS/_V*/",
            ],
        }
        manifest_path = staging_root / BUILD_MANIFEST_NAME
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        staging_root.rename(final_root)
    except Exception:
        if staging_root.exists():
            shutil.rmtree(staging_root)
        raise

    return RcBuildResult(
        skill_root=final_root,
        manifest_path=final_root / BUILD_MANIFEST_NAME,
        build_identity=build_identity,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an isolated Project Incubator V1.1 RC skill")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument(
        "--built-at",
        default=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    )
    args = parser.parse_args()
    result = build_rc_skill(args.source, args.output, args.source_commit, args.built_at)
    print(
        json.dumps(
            {
                "skill_root": str(result.skill_root),
                "manifest_path": str(result.manifest_path),
                "rc_build_identity": result.build_identity,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
