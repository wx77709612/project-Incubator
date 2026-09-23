import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from PROJECT_INCUBATOR.runtime.components.definition_resolver import DefinitionResolver
from PROJECT_INCUBATOR.runtime.components.gate_coordinator import GateCoordinator
from PROJECT_INCUBATOR.runtime.components.script_coordinator import ScriptCoordinator
from PROJECT_INCUBATOR.runtime.core.coordinator import RuntimeCoordinator, RuntimeRequest
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


ROOT = Path(__file__).resolve().parents[3]


class V11RegressionPackageAcceptance(unittest.TestCase):
    def run_files(self, files):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT)
        failures = []
        for path in files:
            completed = subprocess.run(
                [sys.executable, str(path)],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if completed.returncode:
                failures.append(f"{path}:\n{completed.stdout}\n{completed.stderr}")
        self.assertFalse(failures, "\n".join(failures))

    def test_e01_complete_existing_tests_have_zero_failures(self):
        files = sorted((ROOT / "TESTS").rglob("test_*.py"))
        self.assertTrue(files)
        self.run_files(files)

    def test_e02_v1_acceptance_stages_have_zero_failures(self):
        files = sorted((ROOT / "ACCEPTANCE_TESTS/layer2").glob("stage_*/test_*.py"))
        self.assertEqual(5, len(files))
        self.run_files(files)

    def test_e03_legacy_runtime_request_keeps_v1_phase_and_result_semantics(self):
        root = Path(__file__).parent / ".tmp_legacy_runtime"
        shutil.rmtree(root, ignore_errors=True)
        root.mkdir(parents=True)
        try:
            (root / "PROJECT_STATE.md").write_text("Current Phase: P4\n", encoding="utf-8")
            result = RuntimeCoordinator().execute(RuntimeRequest("e03", "contract check", root))
            core_result = json.dumps(
                {
                    "phase": result.current_phase_reference.phase_id,
                    "reason": result.runtime_reason,
                    "state": result.runtime_execution_state.value,
                    "workflow": result.workflow_result_reference,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            self.assertEqual(
                '{"phase":"P4","reason":"RUNTIME_COMPLETED","state":"COMPLETED","workflow":null}',
                core_result,
            )
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_e04_definition_ids_are_stable_and_versions_are_v1_1(self):
        definitions = DefinitionResolver().load_frozen_definition_set()
        expected = {
            "workflow_definition": "PROJECT_INCUBATOR_V1_CORE_WORKFLOW",
            "gate_definition": "PROJECT_INCUBATOR_V1_GATE_DEFINITIONS",
            "context_definition": "PROJECT_INCUBATOR_V1_CONTEXT_MODEL",
            "advisory_definition": "PROJECT_INCUBATOR_V1_ADVISORY_MODEL",
        }
        for field_name, definition_id in expected.items():
            definition = getattr(definitions, field_name)
            self.assertEqual(definition_id, definition["definition_id"])
            self.assertEqual("v1.1-implementation-projection", definition["definition_version"])

    def test_e05_active_source_paths_exist_and_exclude_archives(self):
        def source_paths(value):
            if isinstance(value, dict):
                for key, nested in value.items():
                    if key == "source_document":
                        yield from (nested if isinstance(nested, list) else (nested,))
                    else:
                        yield from source_paths(nested)
            elif isinstance(value, list):
                for nested in value:
                    yield from source_paths(nested)

        for definition_path in (ROOT / "PROJECT_INCUBATOR/references").rglob("*.json"):
            definition = json.loads(definition_path.read_text(encoding="utf-8"))
            for source_path in source_paths(definition):
                normalized = str(source_path).replace("\\", "/")
                self.assertNotIn("/_V", normalized)
                self.assertTrue((ROOT / source_path).is_file(), normalized)

    def test_e06_package_isolation_excludes_specs_temp_and_cache(self):
        destination = Path(__file__).parent / ".tmp_package_isolation" / "PROJECT_INCUBATOR"
        shutil.rmtree(destination.parent, ignore_errors=True)
        try:
            shutil.copytree(
                ROOT / "PROJECT_INCUBATOR",
                destination,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".tmp_*"),
            )
            names = [path.relative_to(destination).as_posix() for path in destination.rglob("*")]
            self.assertFalse(any("SPECS/_V" in name for name in names))
            self.assertFalse(any("__pycache__" in name for name in names))
            self.assertFalse(any("/.tmp_" in name for name in names))
        finally:
            shutil.rmtree(destination.parent, ignore_errors=True)

    def test_e07_runtime_invariant_sets_are_unchanged(self):
        definitions = DefinitionResolver().load_frozen_definition_set()
        workflow = definitions.workflow_definition["workflow"]
        expected_transitions = {
            ("P0", "P1"), ("P1", "P2"), ("P2", "P3"), ("P3", "P4"),
            ("P4", "P5"), ("P5", "P6"), ("P6", "P2"), ("P6", "P3"),
            ("P6", "P4"), ("P6", "P5"),
        }
        self.assertEqual([f"P{i}" for i in range(7)], workflow["core_phase_set"])
        self.assertEqual(expected_transitions, {(item["from"], item["to"]) for item in workflow["allowed_transitions"]})
        self.assertEqual(15, len(GateCoordinator().gates_by_id))
        self.assertEqual({"VALIDATION", "DETERMINISTIC_OPERATION"}, ScriptCoordinator.supported_invocation_purposes)
        self.assertEqual(
            {"EXECUTING", "WAITING_FOR_MAKER", "BLOCKED_BY_GATE", "SUSPENDED", "FAILED", "COMPLETED"},
            {state.value for state in RuntimeExecutionState},
        )


if __name__ == "__main__":
    unittest.main()
