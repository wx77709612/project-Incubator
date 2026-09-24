import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from TOOLS.build_rc_skill import build_rc_skill
from TOOLS.verify_rc_skill import verify_rc_skill


SOURCE_PACKAGE = REPOSITORY_ROOT / "PROJECT_INCUBATOR"
EXPECTED_CHECKS = {
    "package_structure",
    "identity_consistency",
    "manifest_integrity",
    "runtime_clean_room",
    "script:validate_contract_payload.py",
    "script:validate_artifact_evidence.py",
    "script:inspect_git_evidence.py",
    "script:validate_context_integrity_evidence.py",
    "script:bootstrap_host_integration.py",
}


def failed_check_names(report) -> set[str]:
    return {check.name for check in report.checks if not check.passed}


def clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    return environment


def run_script(
    skill_root: Path,
    script_name: str,
    payload: dict[str, object],
    *,
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    script_path = skill_root / "PROJECT_INCUBATOR" / "scripts" / script_name
    return subprocess.run(
        [sys.executable, "-B", str(script_path)],
        input=json.dumps(payload),
        cwd=cwd,
        text=True,
        capture_output=True,
        env=clean_environment(),
        check=False,
    )


class RcSkillIsolationTests(unittest.TestCase):
    def build_rc(self, parent: Path):
        return build_rc_skill(
            SOURCE_PACKAGE,
            parent,
            source_commit="verification-test",
            built_at="2026-09-24T00:00:00Z",
        )

    def test_flattened_install_cannot_resolve_project_incubator_package(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            flattened = root / "project-incubator"
            shutil.copytree(SOURCE_PACKAGE, flattened)
            unrelated = root / "unrelated"
            unrelated.mkdir()

            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(flattened / "scripts" / "validate_artifact_evidence.py"),
                ],
                input="{}",
                cwd=unrelated,
                text=True,
                capture_output=True,
                env=clean_environment(),
                check=False,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("No module named 'PROJECT_INCUBATOR'", result.stderr)

    def test_release_tool_cli_entrypoints_load_from_direct_script_execution(self):
        for tool_name in ("build_rc_skill.py", "verify_rc_skill.py", "install_rc_skill.py"):
            with self.subTest(tool_name=tool_name):
                result = subprocess.run(
                    [sys.executable, "-B", str(REPOSITORY_ROOT / "TOOLS" / tool_name), "--help"],
                    cwd=REPOSITORY_ROOT,
                    text=True,
                    capture_output=True,
                    env=clean_environment(),
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr)

    def test_nested_rc_layout_executes_script_outside_repository(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            skill_root = root / "project-incubator-v1-1-rc"
            shutil.copytree(SOURCE_PACKAGE, skill_root / "PROJECT_INCUBATOR")
            unrelated = root / "含空格的无关目录"
            unrelated.mkdir()

            result = run_script(
                skill_root,
                "validate_artifact_evidence.py",
                {
                    "invocation_id": "isolation",
                    "artifact_reference": "missing",
                },
                cwd=unrelated,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(
                "INVALID_INPUT",
                json.loads(result.stdout)["execution_status"],
            )

    def test_verifier_rejects_version_mismatch(self):
        with TemporaryDirectory() as temp:
            built = self.build_rc(Path(temp) / "含空格的构建目录")
            config_path = built.skill_root / "PROJECT_INCUBATOR" / "runtime" / "config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["package_version"] = "1.1"
            config_path.write_text(json.dumps(config), encoding="utf-8")

            report = verify_rc_skill(built.skill_root)

            self.assertFalse(report.passed)
            self.assertIn("identity_consistency", failed_check_names(report))

    def test_verifier_runs_runtime_and_all_scripts_from_unrelated_directory(self):
        with TemporaryDirectory() as temp:
            built = self.build_rc(Path(temp) / "含空格的构建目录")

            report = verify_rc_skill(built.skill_root)

            self.assertTrue(report.passed, report)
            self.assertEqual(EXPECTED_CHECKS, {check.name for check in report.checks})

    def test_verifier_rejects_manifest_tampering(self):
        with TemporaryDirectory() as temp:
            built = self.build_rc(Path(temp) / "dist")
            manifest = json.loads(built.manifest_path.read_text(encoding="utf-8"))
            first_path = next(iter(manifest["files"]))
            manifest["files"][first_path] = "0" * 64
            built.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            report = verify_rc_skill(built.skill_root)

            self.assertIn("manifest_integrity", failed_check_names(report))

    def test_verifier_rejects_implicit_policy(self):
        with TemporaryDirectory() as temp:
            built = self.build_rc(Path(temp) / "dist")
            policy_path = built.skill_root / "agents" / "openai.yaml"
            policy_path.write_text(
                policy_path.read_text(encoding="utf-8").replace(
                    "allow_implicit_invocation: false",
                    "allow_implicit_invocation: true",
                ),
                encoding="utf-8",
            )

            report = verify_rc_skill(built.skill_root)

            self.assertIn("identity_consistency", failed_check_names(report))

    def test_verifier_rejects_missing_nested_package(self):
        with TemporaryDirectory() as temp:
            built = self.build_rc(Path(temp) / "dist")
            shutil.rmtree(built.skill_root / "PROJECT_INCUBATOR")

            report = verify_rc_skill(built.skill_root)

            self.assertIn("package_structure", failed_check_names(report))

    def test_verifier_ignores_polluted_pythonpath(self):
        with TemporaryDirectory() as temp:
            built = self.build_rc(Path(temp) / "dist")
            polluted = str(REPOSITORY_ROOT / "PROJECT_INCUBATOR")
            with patch.dict(os.environ, {"PYTHONPATH": polluted}):
                report = verify_rc_skill(built.skill_root)

            self.assertTrue(report.passed, report)


if __name__ == "__main__":
    unittest.main()
