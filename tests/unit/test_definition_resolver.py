import unittest
from pathlib import Path
import copy
import json

from PROJECT_INCUBATOR.runtime.components.definition_resolver import DefinitionResolver
from PROJECT_INCUBATOR.runtime.components.workflow_coordinator import (
    WorkflowCoordinator,
    WorkflowDefinitionError,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class DefinitionResolverTest(unittest.TestCase):
    root = Path(__file__).resolve().parents[2]

    def test_default_definitions_resolve(self):
        result = DefinitionResolver().resolve()

        self.assertIs(result.runtime_state, RuntimeExecutionState.COMPLETED)
        self.assertIsNotNone(result.frozen_definition_set)
        self.assertEqual(
            "PROJECT_INCUBATOR_V1_GATE_DEFINITIONS",
            result.frozen_definition_set.gate_definition["definition_id"],
        )

    def test_missing_definition_returns_failed_result(self):
        result = DefinitionResolver(
            config_data={
                "reference_locations": {},
                "definition_identity_mapping": {},
            },
        ).resolve()

        self.assertIs(result.runtime_state, RuntimeExecutionState.FAILED)
        self.assertIn("workflow_definition", result.missing_requirement)

    def test_project_plan_remains_core_context_lifecycle_plan(self):
        result = DefinitionResolver().resolve()
        self.assertIs(result.runtime_state, RuntimeExecutionState.COMPLETED)
        context_definition = result.frozen_definition_set.context_definition["context_model"]

        self.assertIn("PROJECT_PLAN", context_definition["core_context_types"])
        project_plan = next(
            context
            for context in context_definition["core_contexts"]
            if context["context_type"] == "PROJECT_PLAN"
        )

        self.assertEqual("PROJECT_PLAN.md", project_plan["file_name"])
        self.assertIn("项目生命周期规划", project_plan["responsibility"])
        plan_boundary = project_plan["lifecycle"]
        self.assertIn("Phase Goal", plan_boundary["records"])
        self.assertIn("Next Action", plan_boundary["records"])
        self.assertIn("High-level Dependency", plan_boundary["records"])
        self.assertIn("Implementation Task Breakdown Artifact", plan_boundary["does_not_record"])

    def test_phase_matrix_separates_artifact_output_and_context_mutation(self):
        result = DefinitionResolver().resolve()
        self.assertIs(result.runtime_state, RuntimeExecutionState.COMPLETED)
        phases = result.frozen_definition_set.workflow_definition["workflow"]["phases"]

        for phase in phases:
            self.assertIn("required_artifact", phase)
            self.assertIn("artifact_output", phase)
            self.assertIn("context_mutation", phase)
            self.assertIsInstance(phase["required_artifact"], list)
            self.assertIsInstance(phase["artifact_output"], list)
            self.assertIsInstance(phase["context_mutation"], list)
            self.assertFalse(
                set(phase["artifact_output"]).intersection(phase["context_mutation"]),
            )

    def test_p3_required_artifact_is_implementation_plan_not_project_plan_context(self):
        result = DefinitionResolver().resolve()
        self.assertIs(result.runtime_state, RuntimeExecutionState.COMPLETED)
        workflow_definition = result.frozen_definition_set.workflow_definition["workflow"]
        p3_definition = next(
            phase for phase in workflow_definition["phases"] if phase["phase_id"] == "P3"
        )

        self.assertEqual(["Implementation Plan"], p3_definition["artifact_output"])
        self.assertEqual(["Implementation Plan"], p3_definition["required_artifact"])
        self.assertEqual(["PROJECT_PLAN.md", "PROJECT_STATE.md"], p3_definition["context_mutation"])
        self.assertNotIn("PROJECT_PLAN.md", p3_definition["required_artifact"])
        self.assertNotIn("PROJECT_PLAN.md", p3_definition["artifact_output"])

    def test_p6_does_not_express_project_plan_as_an_artifact_output(self):
        result = DefinitionResolver().resolve()
        self.assertIs(result.runtime_state, RuntimeExecutionState.COMPLETED)
        workflow_definition = result.frozen_definition_set.workflow_definition["workflow"]
        p6_definition = next(
            phase for phase in workflow_definition["phases"] if phase["phase_id"] == "P6"
        )

        self.assertNotIn("PROJECT_PLAN.md", p6_definition["artifact_output"])
        self.assertNotIn("PROJECT_STATE.md", p6_definition["artifact_output"])
        self.assertEqual(["PROJECT_PLAN.md", "PROJECT_STATE.md"], p6_definition["context_mutation"])

    def test_implementation_plan_is_phase_artifact_not_core_context(self):
        result = DefinitionResolver().resolve()
        self.assertIs(result.runtime_state, RuntimeExecutionState.COMPLETED)
        workflow_definition = result.frozen_definition_set.workflow_definition["workflow"]
        artifact_definitions = workflow_definition["artifact_definitions"]

        implementation_plan = artifact_definitions["Implementation Plan"]
        self.assertEqual("Phase Artifact", implementation_plan["artifact_layer"])
        self.assertFalse(implementation_plan["is_core_context"])
        self.assertIn("Solution Design", implementation_plan["purpose"])
        self.assertIn("Project Type", implementation_plan["structure_rule"])

    def test_project_plan_template_excludes_implementation_task_breakdown(self):
        template_path = (
            Path(__file__).resolve().parents[2]
            / "PROJECT_INCUBATOR"
            / "templates"
            / "context"
            / "PROJECT_PLAN.template.md"
        )
        template = template_path.read_text(encoding="utf-8")

        self.assertIn("项目生命周期规划", template)
        self.assertIn("Next Action", template)
        self.assertIn("High-level Dependency", template)
        self.assertIn("不得记录 Implementation Task Breakdown Artifact", template)

    def test_implementation_plan_template_declares_phase_artifact_boundary(self):
        template_path = (
            Path(__file__).resolve().parents[2]
            / "PROJECT_INCUBATOR"
            / "templates"
            / "artifacts"
            / "IMPLEMENTATION_PLAN.template.md"
        )
        template = template_path.read_text(encoding="utf-8")

        self.assertIn("Implementation Plan 是 Phase Artifact", template)
        self.assertIn("将 Solution Design 转换为可执行实施方案", template)
        self.assertIn("不属于 Core Context", template)
        self.assertIn("不替代 `PROJECT_PLAN.md`", template)

    def test_active_source_documents_exist_and_never_reference_archives(self):
        for path in (self.root / "PROJECT_INCUBATOR/references").rglob("*.json"):
            definition = json.loads(path.read_text(encoding="utf-8"))
            source_documents = definition.get("source_document", ())
            if isinstance(source_documents, str):
                source_documents = (source_documents,)
            for source_document in source_documents:
                self.assertNotIn("/_V", source_document.replace("\\", "/"))
                self.assertTrue(
                    (self.root / source_document).is_file(),
                    f"missing active source_document: {source_document}",
                )

    def test_v1_1_versions_preserve_stable_definition_ids(self):
        definitions = DefinitionResolver().load_frozen_definition_set()
        expected_ids = {
            "workflow_definition": "PROJECT_INCUBATOR_V1_CORE_WORKFLOW",
            "gate_definition": "PROJECT_INCUBATOR_V1_GATE_DEFINITIONS",
            "context_definition": "PROJECT_INCUBATOR_V1_CONTEXT_MODEL",
            "advisory_definition": "PROJECT_INCUBATOR_V1_ADVISORY_MODEL",
        }
        for field_name, expected_id in expected_ids.items():
            definition = getattr(definitions, field_name)
            self.assertEqual(expected_id, definition["definition_id"])
            self.assertEqual("v1.1-implementation-projection", definition["definition_version"])

    def test_relaxed_correction_thresholds_are_rejected(self):
        workflow = copy.deepcopy(
            DefinitionResolver().load_frozen_definition_set().workflow_definition
        )
        p4 = next(phase for phase in workflow["workflow"]["phases"] if phase["phase_id"] == "P4")
        p4["correction_policy"]["advisory_threshold"] = 3
        p4["correction_policy"]["correction_threshold"] = 4

        with self.assertRaises(WorkflowDefinitionError):
            WorkflowCoordinator(workflow_definition=workflow)

    def test_runtime_config_exposes_optional_spiral_template(self):
        config = json.loads(
            (self.root / "PROJECT_INCUBATOR/runtime/config.json").read_text(encoding="utf-8")
        )
        self.assertEqual("1.1", config["package_version"])
        self.assertEqual(
            "templates/context/CAPABILITY_SPIRAL_RECORD.template.md",
            config["template_locations"]["capability_spiral_record_template"],
        )


if __name__ == "__main__":
    unittest.main()
