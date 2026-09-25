import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

from PROJECT_INCUBATOR.runtime.components.context_coordinator import (
    AccessTarget,
    ContextCoordinator,
    ContextType,
    MutationIntent,
    MutationType,
)
from PROJECT_INCUBATOR.runtime.components.workflow_coordinator import (
    CorrectionAssessmentRequest,
    PhaseResult,
)
from PROJECT_INCUBATOR.runtime.core.coordinator import (
    TRANSITION_NOT_ALLOWED,
    UNSUPPORTED_RUNTIME_CONDITION,
    RuntimeCoordinator,
    RuntimeRequest,
)
from PROJECT_INCUBATOR.runtime.core.mutation_orchestration_types import (
    AuthorityRequirement,
    ClosureAssertion,
    ClosureOperator,
    ContextMutationSet,
    MutationOrchestrationResult,
    MutationSetStatus,
    MutationTargetSpec,
    OrchestrationFailureCode,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState
from PROJECT_INCUBATOR.runtime.core.evidence_types import (
    CorrectionActivityState,
    CorrectionResult,
    failure_signature,
)


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

    def correction_request(self, count=1, impact_overrides=None, current_phase="P4"):
        impact = {
            "changes_product_goal": False,
            "changes_success_criteria": False,
            "changes_maker_approved_scope": False,
            "changes_core_phase_model": False,
            "changes_context_authority": False,
            "changes_runtime_invariant": False,
            "crosses_current_work_package": False,
            "affected_scope_identified": True,
            "regression_set_identified": True,
        }
        impact.update(impact_overrides or {})
        signature = failure_signature("cap-1", "scene-1", "boundary", "failed")
        return CorrectionAssessmentRequest(
            request_id="correction",
            current_phase=current_phase,
            capability_id="cap-1",
            candidate_model_version="model-1",
            scenario_id="scene-1",
            boundary_step="boundary",
            observed_outcome="failed",
            failure_signature=signature,
            consecutive_failure_count=count,
            evidence_refs=("evidence-1",),
            affected_assumption_ids=("assumption-1",),
            affected_artifacts=("design.md",),
            impact_assessment=impact,
        )

    def mutation_set(self):
        return ContextMutationSet(
            mutation_set_id="ms-runtime",
            event_type="OPAQUE_EXTENSION_ACTIVATED",
            event_ref="capability:C-1",
            current_phase="P2",
            requested_by="RUNTIME",
            authority_requirement=AuthorityRequirement.MAKER,
            targets=(
                MutationTargetSpec("CAPABILITY_SPIRAL_RECORD", "UPDATE_CONTEXT", "Extension Status: ACTIVE\n", 10),
                MutationTargetSpec("PROJECT_PLAN", "UPDATE_CONTEXT", "Extension Status: ACTIVE\n", 20),
                MutationTargetSpec("PROJECT_STATE", "UPDATE_CONTEXT", "Current Phase: P2\nExtension Status: ACTIVE\n", 30),
            ),
            closure_assertions=(
                ClosureAssertion(
                    "state-active",
                    "PROJECT_STATE.Extension Status",
                    ClosureOperator.EQUALS,
                    "ACTIVE",
                ),
            ),
        )

    def runtime_with_orchestration_status(self, status):
        failure = None
        if status in {MutationSetStatus.REJECTED, MutationSetStatus.ROLLED_BACK}:
            failure = OrchestrationFailureCode.CONTEXT_CLOSURE_FAILED
        elif status is MutationSetStatus.FAILED:
            failure = OrchestrationFailureCode.ROLLBACK_FAILED
        result = MutationOrchestrationResult(
            mutation_set_id="ms-runtime",
            attempt_id="attempt-1",
            status=status,
            committed_targets=("CAPABILITY_SPIRAL_RECORD", "PROJECT_PLAN", "PROJECT_STATE"),
            verified_assertions=("state-active",),
            authorization_request_ref="auth-request-1",
            authorization_evidence_ref="auth-1",
            authorization_request_status="AUTHORIZED" if status is MutationSetStatus.VERIFIED else None,
            rollback_status="RESTORED" if status is MutationSetStatus.ROLLED_BACK else None,
            failure_code=failure,
        )
        instances = []

        def factory(file_store):
            instance = StubOrchestrationCoordinator(file_store, result)
            instances.append(instance)
            return instance

        return RuntimeCoordinator(context_coordinator_factory=factory), result, instances

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

    def test_all_correction_results_map_to_existing_runtime_states(self):
        self.write_state("P4")
        cases = (
            (self.correction_request(1), CorrectionResult.NO_CORRECTION, RuntimeExecutionState.EXECUTING, CorrectionActivityState.NORMAL_CREATION),
            (self.correction_request(2), CorrectionResult.MODEL_REVIEW_ADVISORY, RuntimeExecutionState.EXECUTING, CorrectionActivityState.NORMAL_CREATION),
            (self.correction_request(3), CorrectionResult.P4_CORRECTION_REQUIRED, RuntimeExecutionState.SUSPENDED, CorrectionActivityState.CORRECTION_REVIEW),
            (
                self.correction_request(1, {"changes_product_goal": True}),
                CorrectionResult.MAKER_SCOPE_REVIEW_REQUIRED,
                RuntimeExecutionState.WAITING_FOR_MAKER,
                CorrectionActivityState.AWAITING_MAKER_SCOPE_REVIEW,
            ),
            (
                self.correction_request(1, current_phase="P3"),
                CorrectionResult.CORRECTION_ASSESSMENT_INVALID,
                RuntimeExecutionState.SUSPENDED,
                CorrectionActivityState.CORRECTION_REVIEW,
            ),
        )

        for correction, expected_result, expected_state, expected_activity in cases:
            with self.subTest(expected_result=expected_result):
                result = self.coordinator.execute(
                    RuntimeRequest(
                        request_id=f"runtime-{expected_result.value}",
                        requested_action="evaluate correction",
                        project_root=self.root,
                        correction_assessment_request=correction,
                    )
                )
                self.assertIs(expected_state, result.runtime_execution_state)
                self.assertIs(expected_result, result.correction_result_reference.result)
                self.assertIs(expected_activity, result.correction_activity_state)
                self.assertEqual("P4", result.current_phase_reference.phase_id)

    def test_correction_route_never_evaluates_transition_or_mutates_phase(self):
        self.write_state("P4")
        phase_intent = self.state_intent("P5")
        with patch.object(
            self.coordinator.workflow_coordinator,
            "evaluate_transition",
            side_effect=AssertionError("transition evaluation must not run"),
        ):
            result = self.coordinator.execute(
                RuntimeRequest(
                    request_id="correction-no-transition",
                    requested_action="evaluate correction",
                    project_root=self.root,
                    correction_assessment_request=self.correction_request(3),
                    phase_result=PhaseResult(
                        current_phase="P4",
                        requested_next_phase="P5",
                        process_completed=True,
                        required_artifact_requirement_satisfied=True,
                        state_change_requirement_formed=True,
                        gate_requirement_resolved=True,
                    ),
                    context_mutation_intents=(phase_intent,),
                )
            )

        self.assertIsNone(result.workflow_result_reference)
        self.assertIn("P4", (self.root / "PROJECT_STATE.md").read_text(encoding="utf-8"))
        self.assertNotIn("P5", (self.root / "PROJECT_STATE.md").read_text(encoding="utf-8"))

    def test_orchestration_results_map_to_frozen_runtime_states(self):
        self.write_state("P2")
        cases = {
            MutationSetStatus.AUTHORIZATION_PENDING: RuntimeExecutionState.WAITING_FOR_MAKER,
            MutationSetStatus.VERIFIED: RuntimeExecutionState.COMPLETED,
            MutationSetStatus.REJECTED: RuntimeExecutionState.SUSPENDED,
            MutationSetStatus.ROLLED_BACK: RuntimeExecutionState.SUSPENDED,
            MutationSetStatus.SUSPENDED: RuntimeExecutionState.SUSPENDED,
            MutationSetStatus.FAILED: RuntimeExecutionState.FAILED,
        }
        for status, expected_state in cases.items():
            with self.subTest(status=status):
                coordinator, orchestration_result, _ = self.runtime_with_orchestration_status(status)
                result = coordinator.execute(
                    RuntimeRequest(
                        request_id=f"route-{status.value}",
                        requested_action="mutate contexts",
                        project_root=self.root,
                        context_mutation_set=self.mutation_set(),
                    )
                )
                self.assertIs(expected_state, result.runtime_execution_state)
                self.assertIs(orchestration_result, result.mutation_orchestration_result_reference)
                self.assertEqual("ms-runtime", result.mutation_orchestration_result_reference.mutation_set_id)
                self.assertEqual("attempt-1", result.mutation_orchestration_result_reference.attempt_id)

    def test_orchestration_route_bypasses_legacy_mutation_and_workflow_transition(self):
        self.write_state("P2")
        coordinator, _, instances = self.runtime_with_orchestration_status(MutationSetStatus.VERIFIED)
        with patch.object(
            coordinator,
            "_prepare_context_mutations",
            side_effect=AssertionError("legacy mutation preparation must not run"),
        ), patch.object(
            coordinator.workflow_coordinator,
            "evaluate_transition",
            side_effect=AssertionError("workflow transition must not run"),
        ):
            result = coordinator.execute(
                RuntimeRequest(
                    request_id="orchestration-only",
                    requested_action="mutate contexts",
                    project_root=self.root,
                    context_mutation_set=self.mutation_set(),
                    phase_result=self.phase_result("P3"),
                )
            )

        self.assertIs(RuntimeExecutionState.COMPLETED, result.runtime_execution_state)
        self.assertEqual(1, instances[0].execute_calls)
        self.assertIsNone(result.workflow_result_reference)

    def test_overlapping_mutation_set_and_legacy_intent_are_rejected(self):
        self.write_state("P2")
        coordinator, _, instances = self.runtime_with_orchestration_status(MutationSetStatus.VERIFIED)

        result = coordinator.execute(
            RuntimeRequest(
                request_id="overlapping-routes",
                requested_action="mutate contexts",
                project_root=self.root,
                context_mutation_set=self.mutation_set(),
                context_mutation_intents=(self.state_intent("P3"),),
            )
        )

        self.assertIs(RuntimeExecutionState.SUSPENDED, result.runtime_execution_state)
        self.assertEqual(0, instances[0].execute_calls)

    def test_disjoint_legacy_intent_is_not_silently_ignored(self):
        self.write_state("P2")
        coordinator, _, instances = self.runtime_with_orchestration_status(MutationSetStatus.VERIFIED)
        independent = MutationIntent(
            mutation_type=MutationType.UPDATE_CONTEXT,
            target_context=AccessTarget(ContextType.PROJECT_DECISIONS),
            change_purpose="independent decision mutation",
            change_basis="MAKER_DECISION",
            proposed_content="Decision D-1: ACTIVE\n",
        )

        result = coordinator.execute(
            RuntimeRequest(
                request_id="disjoint-routes",
                requested_action="mutate contexts",
                project_root=self.root,
                context_mutation_set=self.mutation_set(),
                context_mutation_intents=(independent,),
            )
        )

        self.assertIs(RuntimeExecutionState.SUSPENDED, result.runtime_execution_state)
        self.assertEqual(0, instances[0].execute_calls)

    def test_interrupted_orchestration_attempts_are_suspended_for_recovery(self):
        self.write_state("P2")
        for status in (
            MutationSetStatus.AUTHORIZATION_PENDING,
            MutationSetStatus.COMMITTING,
            MutationSetStatus.FINALIZING_AUTHORIZATION,
        ):
            with self.subTest(status=status):
                coordinator, orchestration_result, _ = self.runtime_with_orchestration_status(status)
                result = coordinator.execute(
                    RuntimeRequest(
                        request_id=f"recover-{status.value}",
                        requested_action="recover mutation set",
                        project_root=self.root,
                        context_mutation_set=self.mutation_set(),
                    )
                )
                expected = (
                    RuntimeExecutionState.WAITING_FOR_MAKER
                    if status is MutationSetStatus.AUTHORIZATION_PENDING
                    else RuntimeExecutionState.SUSPENDED
                )
                self.assertIs(expected, result.runtime_execution_state)
                self.assertIs(orchestration_result, result.mutation_orchestration_result_reference)


class StubOrchestrationCoordinator(ContextCoordinator):
    def __init__(self, file_store, orchestration_result):
        super().__init__(file_store)
        self.orchestration_result = orchestration_result
        self.execute_calls = 0

    def execute_mutation_set(self, mutation_set, recipe):
        self.execute_calls += 1
        return self.orchestration_result


if __name__ == "__main__":
    unittest.main()
