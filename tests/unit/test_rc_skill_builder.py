import json
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from TOOLS.build_rc_skill import build_rc_skill
from TOOLS.rc_skill_common import RC_PACKAGE_VERSION, RC_SKILL_ID, payload_manifest


SOURCE_PACKAGE = REPOSITORY_ROOT / "PROJECT_INCUBATOR"
BUILT_AT = "2026-09-24T00:00:00Z"
SOURCE_COMMIT = "abc123"


class RcSkillBuilderTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.source = self.root / "候选源码"
        shutil.copytree(SOURCE_PACKAGE, self.source)
        self._add_excluded_source_content()
        self.source_skill_before = (self.source / "SKILL.md").read_bytes()
        self.source_config_before = (self.source / "runtime" / "config.json").read_bytes()

    def tearDown(self):
        self.temp_directory.cleanup()

    def _add_excluded_source_content(self):
        excluded_files = (
            self.source / "__pycache__" / "junk.pyc",
            self.source / ".git" / "config",
            self.source / "TESTS" / "test_fixture.py",
            self.source / "ACCEPTANCE_TESTS" / "test_fixture.py",
            self.source / "SPECS" / "_V1.0" / "historical.md",
        )
        for path in excluded_files:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("excluded", encoding="utf-8")

    def _build(self, output_name: str):
        return build_rc_skill(
            self.source,
            self.root / output_name,
            source_commit=SOURCE_COMMIT,
            built_at=BUILT_AT,
        )

    def test_build_creates_nested_explicit_only_rc(self):
        result = self._build("包含 空格的输出")

        self.assertEqual(RC_SKILL_ID, result.skill_root.name)
        self.assertTrue(
            (
                result.skill_root
                / "PROJECT_INCUBATOR"
                / "runtime"
                / "config.json"
            ).is_file(),
        )
        skill_content = (result.skill_root / "SKILL.md").read_text(encoding="utf-8")
        policy_content = (result.skill_root / "agents" / "openai.yaml").read_text(
            encoding="utf-8",
        )
        self.assertIn(f"name: {RC_SKILL_ID}", skill_content)
        self.assertIn(RC_PACKAGE_VERSION, skill_content)
        self.assertIn("allow_implicit_invocation: false", policy_content)

    def test_build_rewrites_distribution_version_without_mutating_source(self):
        result = self._build("dist")

        built_config = json.loads(
            (
                result.skill_root
                / "PROJECT_INCUBATOR"
                / "runtime"
                / "config.json"
            ).read_text(encoding="utf-8"),
        )
        self.assertEqual(RC_PACKAGE_VERSION, built_config["package_version"])
        self.assertEqual(self.source_skill_before, (self.source / "SKILL.md").read_bytes())
        self.assertEqual(
            self.source_config_before,
            (self.source / "runtime" / "config.json").read_bytes(),
        )

    def test_manifest_covers_payload_and_is_deterministic(self):
        left = self._build("left")
        right = self._build("right")

        left_manifest = json.loads(left.manifest_path.read_text(encoding="utf-8"))
        right_manifest = json.loads(right.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(RC_SKILL_ID, left_manifest["skill_identity"])
        self.assertEqual(RC_PACKAGE_VERSION, left_manifest["package_version"])
        self.assertEqual(SOURCE_COMMIT, left_manifest["source_commit"])
        self.assertEqual(BUILT_AT, left_manifest["built_at"])
        self.assertEqual(left_manifest["files"], right_manifest["files"])
        self.assertEqual(left.build_identity, right.build_identity)
        self.assertNotIn("BUILD_MANIFEST.json", left_manifest["files"])
        self.assertEqual(payload_manifest(left.skill_root), left_manifest["files"])

    def test_build_excludes_development_and_historical_content(self):
        result = self._build("dist")
        relative_paths = {
            path.relative_to(result.skill_root).as_posix()
            for path in result.skill_root.rglob("*")
        }

        self.assertFalse(any("__pycache__" in path for path in relative_paths))
        self.assertFalse(any(path.endswith(".pyc") for path in relative_paths))
        self.assertFalse(any("/.git/" in f"/{path}/" for path in relative_paths))
        self.assertFalse(any("/TESTS/" in f"/{path}/" for path in relative_paths))
        self.assertFalse(any("/ACCEPTANCE_TESTS/" in f"/{path}/" for path in relative_paths))
        self.assertFalse(any("/SPECS/_V" in f"/{path}" for path in relative_paths))

    def test_build_contains_only_one_skill_discovery_entry(self):
        result = self._build("dist")

        skill_entries = sorted(
            path.relative_to(result.skill_root).as_posix()
            for path in result.skill_root.rglob("SKILL.md")
        )

        self.assertEqual(["SKILL.md"], skill_entries)


if __name__ == "__main__":
    unittest.main()
