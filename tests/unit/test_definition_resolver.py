import unittest

from PROJECT_INCUBATOR.runtime.components.definition_resolver import DefinitionResolver
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class DefinitionResolverTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
