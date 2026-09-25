import shutil
import unittest
from dataclasses import replace
from pathlib import Path

from PROJECT_INCUBATOR.runtime.adapters.file_store import FileStore, FileWriteError
from PROJECT_INCUBATOR.runtime.components.context_coordinator import ContextCoordinator
from PROJECT_INCUBATOR.runtime.components.definition_resolver import DefinitionResolver
from PROJECT_INCUBATOR.runtime.core.coordinator import RuntimeCoordinator, RuntimeRequest
from PROJECT_INCUBATOR.runtime.core.mutation_orchestration_types import (
    AuthorityRequirement,
    AuthorizationProvenance,
    AuthorizationRequestRecord,
    ClosureAssertion,
    ClosureOperator,
    ContextMutationSet,
    MutationSetStatus,
    MutationTargetSpec,
    OrchestrationFailureCode,
    authorization_statement_digest,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


class MutationOrchestrationFlowTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent / ".tmp_mutation_orchestration_flow"
        shutil.rmtree(self.root, ignore_errors=True)
        self.root.mkdir(parents=True)
        self.seed_pending()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def seed_pending(self):
        shutil.rmtree(self.root / ".project_incubator", ignore_errors=True)
        (self.root / "CAPABILITY_SPIRAL_RECORD.md").write_text(
            "Capability ID: C-PERSIST\nExtension Status: PENDING_MAKER_AUTHORIZATION\n"
            "Authorization Request Ref: auth-request-persist\n"
            "Human Validation Consumed: 0 / 4\n",
            encoding="utf-8",
        )
        (self.root / "PROJECT_PLAN.md").write_text(
            "Capability ID: C-PERSIST\nExtension Status: PENDING_MAKER_AUTHORIZATION\n"
            "Authorization Request Ref: auth-request-persist\n",
            encoding="utf-8",
        )
        (self.root / "PROJECT_STATE.md").write_text(
            "Current Phase: P2\nCapability ID: C-PERSIST\n"
            "Extension Status: PENDING_MAKER_AUTHORIZATION\n"
            "Authorization Request Ref: auth-request-persist\n",
            encoding="utf-8",
        )

    def pending_request(self):
        return AuthorizationRequestRecord(
            authorization_request_id="auth-request-persist",
            event_type="OPAQUE_EXTENSION_ACTIVATED",
            event_ref="capability:C-PERSIST",
            requested_decision="启用持久通知不透明能力 Extension",
            requested_scope=("capability:C-PERSIST", "environment:windows11"),
            requested_context_targets=(
                "CAPABILITY_SPIRAL_RECORD",
                "PROJECT_PLAN",
                "PROJECT_STATE",
            ),
            cost_summary="人工目标环境测试上限 4 次",
            risk_summary="端到端语义仍为 E0",
            unsupported_boundary=("每日提醒实测", "跨版本稳定性"),
        )

    def provenance(self):
        excerpt = "批准只对持久通知 Capability 启用不透明能力 Extension。"
        return AuthorizationProvenance(
            authorization_id="auth-persist-1",
            authorization_request_id="auth-request-persist",
            source_actor="MAKER",
            source_message_ref="maker-round-2r",
            source_message_role="MAKER",
            maker_statement_excerpt=excerpt,
            authorized_scope=("capability:C-PERSIST", "environment:windows11"),
            authorized_context_targets=(
                "CAPABILITY_SPIRAL_RECORD",
                "PROJECT_PLAN",
                "PROJECT_STATE",
            ),
            confirmed_at="2026-09-25T12:00:00+08:00",
            statement_digest=authorization_statement_digest(excerpt),
        )

    def activation_set(self, *, authorized):
        recipe = DefinitionResolver().context_event_recipe("OPAQUE_EXTENSION_ACTIVATED")
        assertions = tuple(
            ClosureAssertion(
                item["assertion_id"],
                item["left_ref"],
                ClosureOperator(item["operator"]),
                item.get("right_value_or_ref"),
            )
            for item in recipe["closure_assertions"]
        )
        mutation_set = ContextMutationSet(
            mutation_set_id="ms-round-2r",
            event_type="OPAQUE_EXTENSION_ACTIVATED",
            event_ref="capability:C-PERSIST",
            current_phase="P2",
            requested_by="RUNTIME",
            authority_requirement=AuthorityRequirement.MAKER,
            targets=(
                MutationTargetSpec(
                    "CAPABILITY_SPIRAL_RECORD",
                    "UPDATE_CONTEXT",
                    "Capability ID: C-PERSIST\nExtension Status: ACTIVE\n"
                    "Authorization Request Ref: auth-request-persist\n"
                    "Authorization Evidence Ref: auth-persist-1\n"
                    "Human Validation Consumed: 0 / 4\n",
                    10,
                ),
                MutationTargetSpec(
                    "PROJECT_PLAN",
                    "UPDATE_CONTEXT",
                    "Capability ID: C-PERSIST\nExtension Status: ACTIVE\n"
                    "Authorization Request Ref: auth-request-persist\n"
                    "Authorization Evidence Ref: auth-persist-1\n",
                    20,
                ),
                MutationTargetSpec(
                    "PROJECT_STATE",
                    "UPDATE_CONTEXT",
                    "Current Phase: P2\nCapability ID: C-PERSIST\nExtension Status: ACTIVE\n"
                    "Authorization Request Ref: auth-request-persist\n"
                    "Authorization Evidence Ref: auth-persist-1\n",
                    30,
                ),
            ),
            closure_assertions=assertions,
        )
        if not authorized:
            return mutation_set
        return replace(
            mutation_set,
            authorization_request=self.pending_request(),
            authorization_provenance=self.provenance(),
        )

    def contents(self):
        return {
            name: (self.root / name).read_text(encoding="utf-8")
            for name in (
                "CAPABILITY_SPIRAL_RECORD.md",
                "PROJECT_PLAN.md",
                "PROJECT_STATE.md",
            )
        }

    def test_round_2_replay_stays_pending_without_explicit_authorization(self):
        before = self.contents()
        result = RuntimeCoordinator().execute(
            RuntimeRequest(
                request_id="round-2-replay",
                requested_action="evaluate and continue",
                project_root=self.root,
                context_mutation_set=self.activation_set(authorized=False),
            )
        )

        self.assertIs(RuntimeExecutionState.WAITING_FOR_MAKER, result.runtime_execution_state)
        self.assertIs(
            MutationSetStatus.AUTHORIZATION_PENDING,
            result.mutation_orchestration_result_reference.status,
        )
        self.assertEqual(before, self.contents())

    def test_round_2r_authorization_activates_all_targets_without_phase_or_budget_change(self):
        result = RuntimeCoordinator().execute(
            RuntimeRequest(
                request_id="round-2r-authorized",
                requested_action="activate authorized extension",
                project_root=self.root,
                context_mutation_set=self.activation_set(authorized=True),
            )
        )

        self.assertIs(RuntimeExecutionState.COMPLETED, result.runtime_execution_state)
        orchestration = result.mutation_orchestration_result_reference
        self.assertIs(MutationSetStatus.VERIFIED, orchestration.status)
        self.assertEqual("AUTHORIZED", orchestration.authorization_request_status)
        for content in self.contents().values():
            self.assertIn("Extension Status: ACTIVE", content)
        self.assertIn("Current Phase: P2", self.contents()["PROJECT_STATE.md"])
        self.assertIn("Human Validation Consumed: 0 / 4", self.contents()["CAPABILITY_SPIRAL_RECORD.md"])

    def test_commit_and_closure_failures_leave_no_partial_activation(self):
        recipe = DefinitionResolver().context_event_recipe("OPAQUE_EXTENSION_ACTIVATED")
        for failure in (
            "CAPABILITY_SPIRAL_RECORD.md",
            "PROJECT_PLAN.md",
            "PROJECT_STATE.md",
            "closure",
        ):
            with self.subTest(failure=failure):
                self.seed_pending()
                before = self.contents()
                mutation_set = self.activation_set(authorized=True)
                store = ActivationFailingStore(self.root, failure)
                if failure == "closure":
                    store = ClosureMismatchStore(self.root)
                result = ContextCoordinator(store).execute_mutation_set(mutation_set, recipe)
                self.assertIs(MutationSetStatus.ROLLED_BACK, result.status)
                self.assertIn(
                    result.failure_code,
                    {
                        OrchestrationFailureCode.COMMIT_FAILED,
                        OrchestrationFailureCode.CONTEXT_CLOSURE_FAILED,
                    },
                )
                self.assertEqual(before, self.contents())


class ActivationFailingStore(FileStore):
    def __init__(self, base_dir, failing_name):
        super().__init__(base_dir)
        self.failing_name = failing_name

    def atomic_write(self, path, content):
        if Path(path).name == self.failing_name and "Extension Status: ACTIVE" in content:
            raise FileWriteError("injected activation failure")
        return super().atomic_write(path, content)


class ClosureMismatchStore(FileStore):
    def __init__(self, base_dir):
        super().__init__(base_dir)
        self.state_reads = 0

    def read_file(self, path):
        content = super().read_file(path)
        if Path(path).name == "PROJECT_STATE.md":
            self.state_reads += 1
            if self.state_reads >= 3 and "Extension Status: ACTIVE" in content:
                return content.replace("Extension Status: ACTIVE", "Extension Status: WRONG")
        return content


if __name__ == "__main__":
    unittest.main()
