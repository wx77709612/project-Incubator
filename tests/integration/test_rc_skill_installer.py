from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from TOOLS.build_rc_skill import build_rc_skill
from TOOLS.install_rc_skill import RcInstallError, install_rc_skill
from TOOLS.rc_skill_common import RC_SKILL_ID, tree_digest
from TOOLS.verify_rc_skill import RcVerificationReport


SOURCE_PACKAGE = REPOSITORY_ROOT / "PROJECT_INCUBATOR"


def failed_report(path: Path) -> RcVerificationReport:
    return RcVerificationReport(skill_root=Path(path), checks=(), passed=False)


class RcSkillInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.codex_home = self.root / "Codex Home"
        self.skills = self.codex_home / "skills"
        self.artifact = build_rc_skill(
            SOURCE_PACKAGE,
            self.root / "构建输出",
            source_commit="installer-test",
            built_at="2026-09-24T00:00:00Z",
        ).skill_root

    def tearDown(self):
        self.temp_directory.cleanup()

    def _stable_v1(self) -> Path:
        stable = self.skills / "project-incubator"
        stable.mkdir(parents=True)
        (stable / "SKILL.md").write_text("stable-v1", encoding="utf-8")
        return stable

    def _existing_rc(self, content: str = "keep") -> Path:
        target = self.skills / RC_SKILL_ID
        target.mkdir(parents=True, exist_ok=True)
        (target / "sentinel.txt").write_text(content, encoding="utf-8")
        return target

    def test_parallel_install_preserves_stable_v1(self):
        stable = self._stable_v1()
        before = tree_digest(stable)

        result = install_rc_skill(self.artifact, self.codex_home)

        self.assertEqual(before, result.stable_v1_digest_after)
        self.assertTrue(result.verification_passed)
        self.assertTrue((self.skills / RC_SKILL_ID / "BUILD_MANIFEST.json").is_file())

    def test_existing_different_rc_is_not_overwritten_without_replace(self):
        target = self._existing_rc()

        with self.assertRaises(RcInstallError):
            install_rc_skill(self.artifact, self.codex_home)

        self.assertEqual("keep", (target / "sentinel.txt").read_text(encoding="utf-8"))

    def test_invalid_artifact_is_rejected_before_install(self):
        with patch("TOOLS.install_rc_skill.verify_rc_skill", return_value=failed_report(self.artifact)):
            with self.assertRaises(RcInstallError):
                install_rc_skill(self.artifact, self.codex_home)

        self.assertFalse((self.skills / RC_SKILL_ID).exists())

    def test_staging_copy_failure_does_not_change_existing_rc(self):
        target = self._existing_rc()
        with patch("TOOLS.install_rc_skill.shutil.copytree", side_effect=OSError("copy failed")):
            with self.assertRaises(RcInstallError):
                install_rc_skill(self.artifact, self.codex_home, replace=True)

        self.assertEqual("keep", (target / "sentinel.txt").read_text(encoding="utf-8"))

    def test_replace_still_requires_valid_artifact(self):
        target = self._existing_rc()
        with patch("TOOLS.install_rc_skill.verify_rc_skill", return_value=failed_report(self.artifact)):
            with self.assertRaises(RcInstallError):
                install_rc_skill(self.artifact, self.codex_home, replace=True)

        self.assertEqual("keep", (target / "sentinel.txt").read_text(encoding="utf-8"))

    def test_staging_verification_failure_does_not_change_existing_rc(self):
        target = self._existing_rc()
        real_verify = __import__("TOOLS.verify_rc_skill", fromlist=["verify_rc_skill"]).verify_rc_skill

        def verify(path):
            path = Path(path)
            if ".staging-" in path.name:
                return failed_report(path)
            return real_verify(path)

        with patch("TOOLS.install_rc_skill.verify_rc_skill", side_effect=verify):
            with self.assertRaises(RcInstallError):
                install_rc_skill(self.artifact, self.codex_home, replace=True)

        self.assertEqual("keep", (target / "sentinel.txt").read_text(encoding="utf-8"))

    def test_post_install_verification_failure_restores_old_rc(self):
        target = self._existing_rc("old-rc")
        real_verify = __import__("TOOLS.verify_rc_skill", fromlist=["verify_rc_skill"]).verify_rc_skill

        def verify(path):
            path = Path(path)
            if path.resolve() == target.resolve():
                return failed_report(path)
            return real_verify(path)

        with patch("TOOLS.install_rc_skill.verify_rc_skill", side_effect=verify):
            with self.assertRaises(RcInstallError):
                install_rc_skill(self.artifact, self.codex_home, replace=True)

        self.assertEqual("old-rc", (target / "sentinel.txt").read_text(encoding="utf-8"))

    def test_missing_stable_v1_reports_no_digest(self):
        result = install_rc_skill(self.artifact, self.codex_home)

        self.assertIsNone(result.stable_v1_digest_before)
        self.assertIsNone(result.stable_v1_digest_after)


if __name__ == "__main__":
    unittest.main()
