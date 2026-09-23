import shutil
import unittest
from pathlib import Path

from PROJECT_INCUBATOR.runtime.adapters.file_store import FileStore, FileWriteError
from PROJECT_INCUBATOR.runtime.components.context_coordinator import (
    AccessTarget,
    AccessType,
    AuthorizationEvidence,
    ContextAccessRequest,
    ContextCoordinator,
    ContextType,
    MutationIntent,
    MutationType,
    RequestSource,
)
from PROJECT_INCUBATOR.runtime.core.contracts import ContextAccessResultStatus


class ContextCoordinatorTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent / ".tmp_context_coordinator"
        shutil.rmtree(self.root, ignore_errors=True)
        self.root.mkdir(parents=True)
        self.coordinator = ContextCoordinator(FileStore(self.root))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_read_project_state_is_accepted(self):
        (self.root / "PROJECT_STATE.md").write_text("Current Phase: P1", encoding="utf-8")

        result = self.coordinator.handle(
            ContextAccessRequest(
                request_id="read-state",
                access_target=AccessTarget(ContextType.PROJECT_STATE),
                access_type=AccessType.READ,
                request_source=RequestSource.RUNTIME,
                access_purpose="read state",
            ),
        )

        self.assertIs(result.status, ContextAccessResultStatus.ACCEPTED)
        self.assertEqual("Current Phase: P1", result.content)

    def test_unauthorized_mutation_is_rejected(self):
        intent = MutationIntent(
            mutation_type=MutationType.UPDATE_CONTEXT,
            target_context=AccessTarget(ContextType.PROJECT_STATE),
            change_purpose="agent attempts direct execution",
            change_basis="WORKFLOW_STATE_CHANGE_REQUIREMENT",
            proposed_content="Current Phase: P2",
        )

        result = self.coordinator.handle(
            ContextAccessRequest(
                request_id="unauthorized-mutation",
                access_target=AccessTarget(ContextType.PROJECT_STATE),
                access_type=AccessType.EXECUTE_MUTATION,
                request_source=RequestSource.AGENT,
                access_purpose="execute mutation",
                mutation_intent=intent,
            ),
        )

        self.assertIs(result.status, ContextAccessResultStatus.REJECTED)
        self.assertEqual("Runtime Execution Authority", result.missing_requirement)

    def test_context_conflict_is_preserved(self):
        result = self.coordinator.handle(
            ContextAccessRequest(
                request_id="conflict",
                access_target=AccessTarget(ContextType.PROJECT_STATE),
                access_type=AccessType.REQUEST_MUTATION,
                request_source=RequestSource.RUNTIME,
                access_purpose="conflicting request",
                conflict_reference="PROJECT_STATE conflict",
            ),
        )

        self.assertIs(result.status, ContextAccessResultStatus.CONTEXT_CONFLICT)
        self.assertEqual("PROJECT_STATE conflict", result.conflict_reference)

    def test_named_optional_context_targets_resolve_to_separate_files(self):
        expected = {
            ContextType.CAPABILITY_SPIRAL_RECORD: "CAPABILITY_SPIRAL_RECORD.md",
            ContextType.PROJECT_DECISION_HISTORY: "PROJECT_DECISION_HISTORY.md",
            ContextType.EVIDENCE_ARTIFACT: "EVIDENCE_ARTIFACT.md",
            ContextType.BASELINE_RECORD: "BASELINE_RECORD.md",
        }

        for context_type, file_name in expected.items():
            with self.subTest(context_type=context_type):
                (self.root / file_name).write_text(context_type.value, encoding="utf-8")
                result = self.coordinator.handle(
                    ContextAccessRequest(
                        request_id=f"read-{context_type.value}",
                        access_target=AccessTarget(context_type),
                        access_type=AccessType.READ,
                        request_source=RequestSource.RUNTIME,
                        access_purpose="read optional evidence context",
                    )
                )
                self.assertIs(ContextAccessResultStatus.ACCEPTED, result.status)
                self.assertEqual(context_type.value, result.content)

    def test_assumption_invalidation_accepts_evidence_without_maker_authorization(self):
        target = AccessTarget(ContextType.CAPABILITY_SPIRAL_RECORD)
        intent = MutationIntent(
            mutation_type=MutationType.UPDATE_ASSUMPTION_STATUS,
            target_context=target,
            change_purpose="invalidate runtime assumption",
            change_basis="EVIDENCE_ASSUMPTION_INVALIDATION",
            proposed_content="Assumption A-1: INVALIDATED",
            assumption_id="A-1",
            target_status="INVALIDATED",
            effective_scope="capability-1",
            evidence_refs=("E-3",),
            dependent_artifact_refs=("design.md",),
        )

        result = self.coordinator.handle(
            ContextAccessRequest(
                request_id="invalidate-assumption",
                access_target=target,
                access_type=AccessType.REQUEST_MUTATION,
                request_source=RequestSource.AGENT,
                access_purpose="record evidence-backed invalidation",
                mutation_intent=intent,
            )
        )

        self.assertIs(ContextAccessResultStatus.ACCEPTED, result.status)

    def test_decision_supersession_requires_maker_authorization(self):
        target = AccessTarget(ContextType.PROJECT_DECISIONS)
        intent = MutationIntent(
            mutation_type=MutationType.SUPERSEDE_DECISION,
            target_context=target,
            change_purpose="replace architecture decision",
            change_basis="NEW_EVIDENCE",
            proposed_content="Decision D-2 supersedes D-1",
            decision_id="D-2",
            target_status="ACTIVE",
            effective_scope="architecture",
            affected_decision_refs=("D-1",),
            gate_evidence_reference="gate-1",
        )

        result = self.coordinator.handle(
            ContextAccessRequest(
                request_id="supersede-decision",
                access_target=target,
                access_type=AccessType.REQUEST_MUTATION,
                request_source=RequestSource.AGENT,
                access_purpose="request decision supersession",
                mutation_intent=intent,
            )
        )

        self.assertIs(ContextAccessResultStatus.AUTHORIZATION_REQUIRED, result.status)

    def test_decision_archive_writes_history_then_updates_active_view(self):
        original = "# Decision D-1\nStatus: ACTIVE\n"
        active = "# Decision D-1\nStatus: SUPERSEDED\nArchive Ref: PROJECT_DECISION_HISTORY.md\n"
        history = "# Decision D-1\nStatus: SUPERSEDED\n"
        (self.root / "PROJECT_DECISIONS.md").write_text(original, encoding="utf-8")

        result = self.coordinator.execute_decision_archive(active, history)

        self.assertIs(ContextAccessResultStatus.ACCEPTED, result.status)
        self.assertEqual(active, (self.root / "PROJECT_DECISIONS.md").read_text(encoding="utf-8"))
        self.assertEqual(
            history,
            (self.root / "PROJECT_DECISION_HISTORY.md").read_text(encoding="utf-8"),
        )

    def test_decision_archive_failure_preserves_original_active_view(self):
        original = "# Decision D-1\nStatus: ACTIVE\n"
        (self.root / "PROJECT_DECISIONS.md").write_text(original, encoding="utf-8")
        coordinator = ContextCoordinator(FailingActiveViewFileStore(self.root))
        active = "# Decision D-1\nStatus: SUPERSEDED\nArchive Ref: PROJECT_DECISION_HISTORY.md\n"
        history = "# Decision D-1\nStatus: SUPERSEDED\n"

        result = coordinator.execute_decision_archive(active, history)

        self.assertIs(ContextAccessResultStatus.REJECTED, result.status)
        self.assertEqual(
            original,
            (self.root / "PROJECT_DECISIONS.md").read_text(encoding="utf-8"),
        )


class FailingActiveViewFileStore(FileStore):
    def atomic_write(self, path, content):
        if Path(path).name == "PROJECT_DECISIONS.md":
            raise FileWriteError("injected active view failure")
        return super().atomic_write(path, content)


if __name__ == "__main__":
    unittest.main()
