import shutil
import unittest
import uuid
from pathlib import Path

from PROJECT_INCUBATOR.runtime.adapters.script_runner import ScriptRunner
from PROJECT_INCUBATOR.runtime.components.script_coordinator import (
    EVIDENCE_READY,
    ScriptCoordinator,
    ScriptInvocationRequest,
)
from PROJECT_INCUBATOR.runtime.core.contracts import ScriptExecutionStatus
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState
from PROJECT_INCUBATOR.scripts.bootstrap_host_integration import (
    INTEGRATION_MARKER,
    bootstrap_host_integration,
)


class BootstrapHostIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temp_root = Path(__file__).parent / ".tmp_bootstrap_host_integration" / uuid.uuid4().hex
        self.temp_root.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.temp_root.parent, ignore_errors=True)

    def test_codex_host_creates_agents_when_missing(self):
        result = bootstrap_host_integration(
            {
                "invocation_id": "case-1",
                "invocation_purpose": "DETERMINISTIC_OPERATION",
                "input_data": {
                    "host_environment": "CODEX",
                    "managed_project_root": str(self.temp_root),
                },
            },
        )

        agents_path = self.temp_root / "AGENTS.md"
        self.assertEqual("CREATED", result["evidence"][0]["observed_fact"])
        self.assertTrue(agents_path.exists())
        content = agents_path.read_text(encoding="utf-8")
        self.assertIn(INTEGRATION_MARKER, content)
        self.assertIn("PROJECT_STATE.md", content)
        self.assertIn("project-incubator", content)

    def test_codex_host_keeps_integrated_agents_unchanged(self):
        agents_path = self.temp_root / "AGENTS.md"
        original = f"{INTEGRATION_MARKER}\n已有入口\n"
        agents_path.write_text(original, encoding="utf-8")

        result = bootstrap_host_integration(
            {
                "invocation_id": "case-2",
                "invocation_purpose": "DETERMINISTIC_OPERATION",
                "input_data": {
                    "host_environment": "CODEX",
                    "managed_project_root": str(self.temp_root),
                },
            },
        )

        self.assertEqual("ALREADY_INTEGRATED", result["evidence"][0]["observed_fact"])
        self.assertEqual(original, agents_path.read_text(encoding="utf-8"))

    def test_codex_host_does_not_overwrite_existing_plain_agents(self):
        agents_path = self.temp_root / "AGENTS.md"
        original = "# Existing Rules\n\n保持原内容。\n"
        agents_path.write_text(original, encoding="utf-8")

        result = bootstrap_host_integration(
            {
                "invocation_id": "case-3",
                "invocation_purpose": "DETERMINISTIC_OPERATION",
                "input_data": {
                    "host_environment": "CODEX",
                    "managed_project_root": str(self.temp_root),
                },
            },
        )

        self.assertEqual("INTEGRATION_REQUIRED", result["evidence"][0]["observed_fact"])
        self.assertEqual(original, agents_path.read_text(encoding="utf-8"))

    def test_other_host_does_not_create_agents(self):
        result = bootstrap_host_integration(
            {
                "invocation_id": "case-4",
                "invocation_purpose": "DETERMINISTIC_OPERATION",
                "input_data": {
                    "host_environment": "OTHER",
                    "managed_project_root": str(self.temp_root),
                },
            },
        )

        self.assertEqual("NOT_APPLICABLE", result["evidence"][0]["observed_fact"])
        self.assertFalse((self.temp_root / "AGENTS.md").exists())

    def test_unknown_host_does_not_create_agents(self):
        result = bootstrap_host_integration(
            {
                "invocation_id": "case-5",
                "invocation_purpose": "DETERMINISTIC_OPERATION",
                "input_data": {
                    "host_environment": "UNKNOWN",
                    "managed_project_root": str(self.temp_root),
                },
            },
        )

        self.assertEqual("HOST_UNKNOWN", result["evidence"][0]["observed_fact"])
        self.assertFalse((self.temp_root / "AGENTS.md").exists())

    def test_bootstrap_does_not_modify_core_context(self):
        context_files = {
            "PROJECT_PROFILE.md": "# Profile\n",
            "PROJECT_STATE.md": "# State\n\nP0\n",
            "PROJECT_PLAN.md": "# Plan\n",
            "PROJECT_DECISIONS.md": "# Decisions\n",
        }
        for file_name, content in context_files.items():
            (self.temp_root / file_name).write_text(content, encoding="utf-8")

        bootstrap_host_integration(
            {
                "invocation_id": "case-6",
                "invocation_purpose": "DETERMINISTIC_OPERATION",
                "input_data": {
                    "host_environment": "CODEX",
                    "managed_project_root": str(self.temp_root),
                },
            },
        )

        for file_name, content in context_files.items():
            self.assertEqual(content, (self.temp_root / file_name).read_text(encoding="utf-8"))

    def test_bootstrap_runs_through_script_coordinator(self):
        coordinator = ScriptCoordinator(script_runner=ScriptRunner())

        result = coordinator.invoke(
            ScriptInvocationRequest(
                invocation_id="case-runtime",
                script_identity="BOOTSTRAP_HOST_INTEGRATION",
                invocation_purpose="DETERMINISTIC_OPERATION",
                input_data={
                    "host_environment": "CODEX",
                    "managed_project_root": str(self.temp_root),
                },
                validation_requirement={},
            ),
        )

        self.assertIs(result.runtime_state, RuntimeExecutionState.COMPLETED)
        self.assertIs(result.execution_status, ScriptExecutionStatus.COMPLETED)
        self.assertIsNone(result.validation_result)
        self.assertEqual(EVIDENCE_READY, result.result_reason)
        self.assertEqual("CREATED", result.evidence[0]["observed_fact"])

    def test_skill_entry_documents_host_bootstrap_boundary(self):
        skill_content = (Path(__file__).parents[2] / "PROJECT_INCUBATOR" / "SKILL.md").read_text(
            encoding="utf-8",
        )

        self.assertIn("Host Environment Bootstrap", skill_content)
        self.assertIn("BOOTSTRAP_HOST_INTEGRATION", skill_content)
        self.assertIn("UNKNOWN", skill_content)
        self.assertIn("不改变 Current Phase", skill_content)
        self.assertIn("不触发 Workflow Transition", skill_content)


if __name__ == "__main__":
    unittest.main()
