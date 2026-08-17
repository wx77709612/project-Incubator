import unittest

from PROJECT_INCUBATOR.runtime.components.workflow_coordinator import (
    PhaseResult,
    WorkflowCoordinator,
)
from PROJECT_INCUBATOR.runtime.core.contracts import WorkflowResultStatus


class WorkflowCoordinatorTest(unittest.TestCase):
    def setUp(self):
        self.coordinator = WorkflowCoordinator()

    def test_resolves_current_phase_from_project_state(self):
        current_phase = self.coordinator.resolve_current_phase({"Current Phase": "P1"})

        self.assertEqual("P1", current_phase.phase_id)
        self.assertEqual("Project Definition", current_phase.phase_name)

    def test_invalid_transition_is_not_allowed(self):
        phase_result = PhaseResult(
            current_phase="P0",
            requested_next_phase="P3",
            process_completed=True,
            required_artifact_requirement_satisfied=True,
            state_change_requirement_formed=True,
            gate_requirement_resolved=True,
        )
        transition = self.coordinator.create_transition_request("invalid", phase_result)

        result = self.coordinator.evaluate_transition(transition)

        self.assertIs(result.status, WorkflowResultStatus.TRANSITION_NOT_ALLOWED)
        self.assertIn("Allowed Next Phase", result.missing_requirements)

    def test_incomplete_phase_result_is_not_ready(self):
        phase_result = PhaseResult(
            current_phase="P0",
            requested_next_phase="P1",
            process_completed=False,
            required_artifact_requirement_satisfied=True,
            state_change_requirement_formed=True,
            gate_requirement_resolved=True,
        )
        transition = self.coordinator.create_transition_request("not-ready", phase_result)

        result = self.coordinator.evaluate_transition(transition)

        self.assertIs(result.status, WorkflowResultStatus.NOT_READY)
        self.assertIn("Process Completion", result.missing_requirements)


if __name__ == "__main__":
    unittest.main()
