import shutil
import unittest
from pathlib import Path

from PROJECT_INCUBATOR.runtime.adapters.file_store import FileStore
from PROJECT_INCUBATOR.runtime.components.context_coordinator import (
    AccessTarget,
    AccessType,
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


if __name__ == "__main__":
    unittest.main()
