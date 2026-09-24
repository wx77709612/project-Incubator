import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PACKAGE = REPOSITORY_ROOT / "PROJECT_INCUBATOR"


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


if __name__ == "__main__":
    unittest.main()
