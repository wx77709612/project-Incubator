import shutil
import unittest
from pathlib import Path

from PROJECT_INCUBATOR.runtime.components.context_coordinator import (
    AccessTarget,
    ContextType,
    MutationIntent,
    MutationType,
)
from PROJECT_INCUBATOR.runtime.components.workflow_coordinator import PhaseResult
from PROJECT_INCUBATOR.runtime.core.coordinator import (
    TRANSITION_NOT_ALLOWED,
    UNSUPPORTED_RUNTIME_CONDITION,
    RuntimeCoordinator,
    RuntimeRequest,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class RuntimeCoordinatorTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent / ".tmp_runtime_coordinator"
        shutil.rmtree(self.root, ignore_errors=True)
        self.root.mkdir(parents=True)
        self.coordinator = RuntimeCoordinator()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write_state(self, phase):
        (self.root / "PROJECT_STATE.md").write_text(
            (
                "# PROJECT_STATE\n\n"
                "## Current Phase / 当前 Phase\n\n"
                f"{phase}\n\n"
                "## Current Execution State / 当前执行状态\n\n"
                "进行中\n"
            ),
            encoding="utf-8",
        )

    def state_intent(self, phase):
        return MutationIntent(
            mutation_type=MutationType.UPDATE_CONTEXT,
            target_context=AccessTarget(ContextType.PROJECT_STATE, "PROJECT_STATE.md"),
            change_purpose="Persist workflow state change",
            change_basis="WORKFLOW_STATE_CHANGE_REQUIREMENT",
            proposed_content=(
                "# PROJECT_STATE\n\n"
                "## Current Phase / 当前 Phase\n\n"
                f"{phase}\n"
            ),
        )

    def phase_result(self, next_phase):
        return PhaseResult(
            current_phase="P0",
            requested_next_phase=next_phase,
            process_completed=True,
            required_artifact_requirement_satisfied=True,
            state_change_requirement_formed=True,
            gate_requirement_resolved=True,
        )

    def test_project_state_is_source_of_truth(self):
        self.write_state("P0")
        (self.root / "PROJECT_PLAN.md").write_text("Current Phase: P6", encoding="utf-8")

        result = self.coordinator.execute(
            RuntimeRequest(
                request_id="state-source",
                requested_action="contract check",
                project_root=self.root,
            ),
        )

        self.assertIs(result.runtime_execution_state, RuntimeExecutionState.COMPLETED)
        self.assertEqual("P0", result.current_phase_reference.phase_id)

    def test_gate_block_prevents_protected_mutation(self):
        self.write_state("P0")

        result = self.coordinator.execute(
            RuntimeRequest(
                request_id="gate-block",
                requested_action="commit",
                project_root=self.root,
                requested_gate_ids=("GATE-GIT",),
                gate_trigger_event="commit",
                gate_evaluation_evidence=(
                    {
                        "gate_id": "GATE-GIT",
                        "gate_result": "REQUIREMENT_UNSATISFIED",
                    },
                ),
                context_mutation_intents=(self.state_intent("P1"),),
            ),
        )

        self.assertIs(result.runtime_execution_state, RuntimeExecutionState.BLOCKED_BY_GATE)
        self.assertIn("P0", (self.root / "PROJECT_STATE.md").read_text(encoding="utf-8"))
        self.assertNotIn("P1", (self.root / "PROJECT_STATE.md").read_text(encoding="utf-8"))

    def test_unsupported_condition_returns_suspended(self):
        self.write_state("P0")

        result = self.coordinator.execute(
            RuntimeRequest(
                request_id="unsupported",
                requested_action="unknown",
                project_root=self.root,
                request_kind="NOT_DEFINED",
            ),
        )

        self.assertIs(result.runtime_execution_state, RuntimeExecutionState.SUSPENDED)
        self.assertEqual(UNSUPPORTED_RUNTIME_CONDITION, result.runtime_reason)

    def test_runtime_does_not_extend_workflow(self):
        self.write_state("P0")

        result = self.coordinator.execute(
            RuntimeRequest(
                request_id="invalid-transition",
                requested_action="transition",
                project_root=self.root,
                phase_result=self.phase_result("P3"),
                context_mutation_intents=(self.state_intent("P3"),),
            ),
        )

        self.assertIs(result.runtime_execution_state, RuntimeExecutionState.SUSPENDED)
        self.assertEqual(TRANSITION_NOT_ALLOWED, result.runtime_reason)
        self.assertIn("P0", (self.root / "PROJECT_STATE.md").read_text(encoding="utf-8"))
        self.assertNotIn("P3", (self.root / "PROJECT_STATE.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
