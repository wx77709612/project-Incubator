import json
import shutil
import unittest
from dataclasses import replace
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
from PROJECT_INCUBATOR.runtime.components.definition_resolver import DefinitionResolver
from PROJECT_INCUBATOR.runtime.core.contracts import ContextAccessResultStatus
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

    def activation_set(self):
        return ContextMutationSet(
            mutation_set_id="ms-activation",
            event_type="OPAQUE_EXTENSION_ACTIVATED",
            event_ref="capability:C-1",
            current_phase="P2",
            requested_by="AGENT",
            authority_requirement=AuthorityRequirement.MAKER,
            targets=(
                MutationTargetSpec(
                    context_type="CAPABILITY_SPIRAL_RECORD",
                    mutation_intent="CREATE_CONTEXT",
                    proposed_content="Extension Status: ACTIVE\n",
                    commit_order=10,
                ),
                MutationTargetSpec(
                    context_type="PROJECT_PLAN",
                    mutation_intent="UPDATE_CONTEXT",
                    proposed_content="Extension Status: ACTIVE\n",
                    commit_order=20,
                ),
                MutationTargetSpec(
                    context_type="PROJECT_STATE",
                    mutation_intent="UPDATE_CONTEXT",
                    proposed_content="Current Phase: P2\nExtension Status: ACTIVE\n",
                    commit_order=30,
                ),
            ),
            closure_assertions=(
                ClosureAssertion(
                    assertion_id="state-active",
                    left_ref="PROJECT_STATE.Extension Status",
                    operator=ClosureOperator.EQUALS,
                    right_value_or_ref="ACTIVE",
                ),
            ),
        )

    def pending_request(self):
        return AuthorizationRequestRecord(
            authorization_request_id="auth-request-1",
            event_type="OPAQUE_EXTENSION_ACTIVATED",
            event_ref="capability:C-1",
            requested_decision="Activate bounded opaque extension",
            requested_scope=("capability:C-1", "environment:windows11"),
            requested_context_targets=(
                "CAPABILITY_SPIRAL_RECORD",
                "PROJECT_PLAN",
                "PROJECT_STATE",
            ),
            cost_summary="four manual tests",
            risk_summary="runtime semantics remain E0",
            unsupported_boundary=("cross-platform",),
        )

    def provenance(self):
        excerpt = "确认，仅按请求范围启用该 Extension。"
        return AuthorizationProvenance(
            authorization_id="auth-1",
            authorization_request_id="auth-request-1",
            source_actor="MAKER",
            source_message_ref="maker-message-42",
            source_message_role="MAKER",
            maker_statement_excerpt=excerpt,
            authorized_scope=("capability:C-1", "environment:windows11"),
            authorized_context_targets=(
                "CAPABILITY_SPIRAL_RECORD",
                "PROJECT_PLAN",
                "PROJECT_STATE",
            ),
            confirmed_at="2026-09-24T21:00:00+08:00",
            statement_digest=authorization_statement_digest(excerpt),
        )

    def test_round_2_boolean_authorization_cannot_activate_without_pending_request(self):
        legacy = AuthorizationEvidence(
            source=RequestSource.MAKER,
            confirmed=True,
            reference="agent-summary",
        )

        failure = self.coordinator.validate_authorization(
            pending_request=None,
            evidence=legacy,
            mutation_set=self.activation_set(),
        )

        self.assertIs(OrchestrationFailureCode.AUTHORIZATION_REQUIRED, failure)

    def test_matching_pending_request_and_maker_provenance_are_accepted(self):
        failure = self.coordinator.validate_authorization(
            pending_request=self.pending_request(),
            evidence=self.provenance(),
            mutation_set=self.activation_set(),
        )

        self.assertIsNone(failure)

    def test_invalid_authorization_provenance_is_rejected(self):
        pending = self.pending_request()
        evidence = self.provenance()
        cases = {
            "wrong request id": replace(evidence, authorization_request_id="other"),
            "agent message role": replace(evidence, source_message_role="AGENT"),
            "agent source actor": replace(evidence, source_actor="AGENT"),
            "empty excerpt": replace(
                evidence,
                maker_statement_excerpt="",
                statement_digest=authorization_statement_digest(""),
            ),
            "digest mismatch": replace(evidence, statement_digest="0" * 64),
        }
        for name, invalid in cases.items():
            with self.subTest(name=name):
                failure = self.coordinator.validate_authorization(
                    pending_request=pending,
                    evidence=invalid,
                    mutation_set=self.activation_set(),
                )
                self.assertIs(OrchestrationFailureCode.AUTHORIZATION_INVALID, failure)

    def test_authorization_scope_event_and_targets_must_cover_mutation_set(self):
        mutation_set = self.activation_set()
        pending = self.pending_request()
        evidence = self.provenance()
        cases = {
            "capability mismatch": (
                replace(pending, event_ref="capability:C-2"),
                evidence,
            ),
            "event reuse": (
                replace(pending, event_type="OPAQUE_EXTENSION_SUSPENDED"),
                evidence,
            ),
            "scope too small": (
                pending,
                replace(evidence, authorized_scope=("capability:C-1",)),
            ),
            "scope broader than request": (
                pending,
                replace(
                    evidence,
                    authorized_scope=(
                        "capability:C-1",
                        "environment:windows11",
                        "environment:all",
                    ),
                ),
            ),
            "targets too small": (
                pending,
                replace(
                    evidence,
                    authorized_context_targets=("PROJECT_PLAN", "PROJECT_STATE"),
                ),
            ),
            "targets broader than request": (
                pending,
                replace(
                    evidence,
                    authorized_context_targets=(
                        "CAPABILITY_SPIRAL_RECORD",
                        "PROJECT_PLAN",
                        "PROJECT_STATE",
                        "PROJECT_PROFILE",
                    ),
                ),
            ),
        }
        for name, (candidate_request, candidate_evidence) in cases.items():
            with self.subTest(name=name):
                failure = self.coordinator.validate_authorization(
                    pending_request=candidate_request,
                    evidence=candidate_evidence,
                    mutation_set=mutation_set,
                )
                self.assertIs(OrchestrationFailureCode.AUTHORIZATION_SCOPE_MISMATCH, failure)

    def test_non_pending_authorization_request_is_invalid(self):
        for status in ("AUTHORIZED", "DECLINED", "EXPIRED", "SUPERSEDED"):
            with self.subTest(status=status):
                failure = self.coordinator.validate_authorization(
                    pending_request=replace(self.pending_request(), status=status),
                    evidence=self.provenance(),
                    mutation_set=self.activation_set(),
                )
                self.assertIs(OrchestrationFailureCode.AUTHORIZATION_INVALID, failure)

    def activation_transaction_set(self, *, include_authorization=True):
        recipe = DefinitionResolver().context_event_recipe("OPAQUE_EXTENSION_ACTIVATED")
        assertions = tuple(
            ClosureAssertion(
                assertion_id=item["assertion_id"],
                left_ref=item["left_ref"],
                operator=ClosureOperator(item["operator"]),
                right_value_or_ref=item.get("right_value_or_ref"),
            )
            for item in recipe["closure_assertions"]
        )
        base = ContextMutationSet(
            mutation_set_id="ms-transaction",
            event_type="OPAQUE_EXTENSION_ACTIVATED",
            event_ref="capability:C-1",
            current_phase="P2",
            requested_by="AGENT",
            authority_requirement=AuthorityRequirement.MAKER,
            targets=(
                MutationTargetSpec(
                    context_type="CAPABILITY_SPIRAL_RECORD",
                    mutation_intent="UPDATE_CONTEXT",
                    proposed_content=(
                        "Capability ID: C-1\nExtension Status: ACTIVE\n"
                        "Authorization Request Ref: auth-request-1\n"
                        "Human Validation Consumed: 0 / 4\n"
                    ),
                    commit_order=10,
                ),
                MutationTargetSpec(
                    context_type="PROJECT_PLAN",
                    mutation_intent="UPDATE_CONTEXT",
                    proposed_content=(
                        "Capability ID: C-1\nExtension Status: ACTIVE\n"
                        "Authorization Request Ref: auth-request-1\n"
                    ),
                    commit_order=20,
                ),
                MutationTargetSpec(
                    context_type="PROJECT_STATE",
                    mutation_intent="UPDATE_CONTEXT",
                    proposed_content=(
                        "Current Phase: P2\nCapability ID: C-1\n"
                        "Extension Status: ACTIVE\n"
                        "Authorization Request Ref: auth-request-1\n"
                    ),
                    commit_order=30,
                ),
            ),
            closure_assertions=assertions,
        )
        if not include_authorization:
            return base
        return replace(
            base,
            authorization_request=self.pending_request(),
            authorization_provenance=self.provenance(),
        )

    def seed_pending_activation(self, *, include_spiral=True):
        shutil.rmtree(self.root / ".project_incubator", ignore_errors=True)
        if include_spiral:
            (self.root / "CAPABILITY_SPIRAL_RECORD.md").write_text(
                "Capability ID: C-1\nExtension Status: PENDING_MAKER_AUTHORIZATION\n"
                "Human Validation Consumed: 0 / 4\n",
                encoding="utf-8",
            )
        (self.root / "PROJECT_PLAN.md").write_text(
            "Capability ID: C-1\nExtension Status: PENDING_MAKER_AUTHORIZATION\n",
            encoding="utf-8",
        )
        (self.root / "PROJECT_STATE.md").write_text(
            "Current Phase: P2\nCapability ID: C-1\n"
            "Extension Status: PENDING_MAKER_AUTHORIZATION\n",
            encoding="utf-8",
        )

    def test_mutation_set_preflights_all_targets_before_any_write(self):
        self.seed_pending_activation()
        store = RecordingFileStore(self.root)
        coordinator = ContextCoordinator(store)
        mutation_set = self.activation_transaction_set()
        invalid = replace(
            mutation_set,
            targets=(mutation_set.targets[0], replace(mutation_set.targets[1], mutation_intent="DELETE_CONTEXT"), mutation_set.targets[2]),
        )

        result = coordinator.execute_mutation_set(
            invalid,
            DefinitionResolver().context_event_recipe(invalid.event_type),
        )

        self.assertIs(MutationSetStatus.REJECTED, result.status)
        self.assertIs(OrchestrationFailureCode.PRECONDITION_CONFLICT, result.failure_code)
        self.assertEqual([], [name for name in store.writes if name.endswith(".md")])

    def test_mutation_set_commits_project_state_last_and_finalizes_authorization(self):
        self.seed_pending_activation()
        store = RecordingFileStore(self.root)
        coordinator = ContextCoordinator(store)
        mutation_set = self.activation_transaction_set()

        result = coordinator.execute_mutation_set(
            mutation_set,
            DefinitionResolver().context_event_recipe(mutation_set.event_type),
        )

        self.assertIs(MutationSetStatus.VERIFIED, result.status)
        self.assertEqual(
            ["CAPABILITY_SPIRAL_RECORD.md", "PROJECT_PLAN.md", "PROJECT_STATE.md"],
            [name for name in store.writes if name.endswith(".md")],
        )
        self.assertEqual("AUTHORIZED", result.authorization_request_status)

    def test_plan_and_state_commit_failures_restore_all_contexts(self):
        for file_name in ("PROJECT_PLAN.md", "PROJECT_STATE.md"):
            with self.subTest(file_name=file_name):
                self.seed_pending_activation()
                originals = self._context_contents()
                coordinator = ContextCoordinator(FailingTargetFileStore(self.root, file_name))
                mutation_set = self.activation_transaction_set()

                result = coordinator.execute_mutation_set(
                    mutation_set,
                    DefinitionResolver().context_event_recipe(mutation_set.event_type),
                )

                self.assertIs(MutationSetStatus.ROLLED_BACK, result.status)
                self.assertIs(OrchestrationFailureCode.COMMIT_FAILED, result.failure_code)
                self.assertEqual(originals, self._context_contents())

    def test_closure_or_authorization_finalization_failure_rolls_back(self):
        cases = ("closure", "authorization")
        for case in cases:
            with self.subTest(case=case):
                self.seed_pending_activation()
                originals = self._context_contents()
                mutation_set = self.activation_transaction_set()
                coordinator = ContextCoordinator(FileStore(self.root))
                if case == "closure":
                    mutation_set = replace(
                        mutation_set,
                        closure_assertions=(
                            ClosureAssertion(
                                assertion_id="wrong-value",
                                left_ref="PROJECT_STATE.Extension Status",
                                operator=ClosureOperator.EQUALS,
                                right_value_or_ref="WRONG",
                            ),
                        ),
                    )
                else:
                    coordinator = FailingFinalizationCoordinator(FileStore(self.root))

                if case == "closure":
                    mutation_set = self.activation_transaction_set()
                    coordinator = ContextCoordinator(ClosureMismatchFileStore(self.root))

                result = coordinator.execute_mutation_set(
                    mutation_set,
                    DefinitionResolver().context_event_recipe(mutation_set.event_type),
                )

                self.assertIs(MutationSetStatus.ROLLED_BACK, result.status)
                expected = (
                    OrchestrationFailureCode.CONTEXT_CLOSURE_FAILED
                    if case == "closure"
                    else OrchestrationFailureCode.COMMIT_FAILED
                )
                self.assertIs(expected, result.failure_code)
                self.assertEqual(originals, self._context_contents())

    def test_recipe_closure_cannot_be_removed_or_weakened(self):
        self.seed_pending_activation()
        store = RecordingFileStore(self.root)
        coordinator = ContextCoordinator(store)
        mutation_set = self.activation_transaction_set()
        weakened = replace(
            mutation_set,
            closure_assertions=(mutation_set.closure_assertions[0],),
        )

        result = coordinator.execute_mutation_set(
            weakened,
            DefinitionResolver().context_event_recipe(weakened.event_type),
        )

        self.assertIs(MutationSetStatus.REJECTED, result.status)
        self.assertIs(OrchestrationFailureCode.EVENT_RECIPE_MISMATCH, result.failure_code)
        self.assertEqual([], [name for name in store.writes if name.endswith(".md")])

    def test_recipe_status_transition_cannot_skip_pending_state(self):
        self.seed_pending_activation()
        for name in (
            "CAPABILITY_SPIRAL_RECORD.md",
            "PROJECT_PLAN.md",
            "PROJECT_STATE.md",
        ):
            path = self.root / name
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "PENDING_MAKER_AUTHORIZATION",
                    "PROPOSED",
                ),
                encoding="utf-8",
            )
        store = RecordingFileStore(self.root)
        mutation_set = self.activation_transaction_set()

        result = ContextCoordinator(store).execute_mutation_set(
            mutation_set,
            DefinitionResolver().context_event_recipe(mutation_set.event_type),
        )

        self.assertIs(MutationSetStatus.REJECTED, result.status)
        self.assertIs(OrchestrationFailureCode.PRECONDITION_CONFLICT, result.failure_code)
        self.assertEqual([], [name for name in store.writes if name.endswith(".md")])

    def test_mutation_set_phase_must_match_project_state_before_commit(self):
        self.seed_pending_activation()
        state = self.root / "PROJECT_STATE.md"
        state.write_text(
            state.read_text(encoding="utf-8").replace("Current Phase: P2", "Current Phase: P3"),
            encoding="utf-8",
        )
        store = RecordingFileStore(self.root)
        mutation_set = self.activation_transaction_set()

        result = ContextCoordinator(store).execute_mutation_set(
            mutation_set,
            DefinitionResolver().context_event_recipe(mutation_set.event_type),
        )

        self.assertIs(MutationSetStatus.REJECTED, result.status)
        self.assertIs(OrchestrationFailureCode.PRECONDITION_CONFLICT, result.failure_code)
        self.assertEqual([], [name for name in store.writes if name.endswith(".md")])

    def test_new_spiral_record_is_removed_when_later_commit_fails(self):
        self.seed_pending_activation(include_spiral=False)
        mutation_set = self.activation_transaction_set()
        mutation_set = replace(
            mutation_set,
            targets=(
                replace(mutation_set.targets[0], mutation_intent="CREATE_CONTEXT"),
            )
            + mutation_set.targets[1:],
            closure_assertions=tuple(
                item
                for item in mutation_set.closure_assertions
                if item.assertion_id != "budget-unchanged"
            ),
        )
        recipe = dict(
            DefinitionResolver().context_event_recipe(mutation_set.event_type)
        )
        recipe["allowed_status_transition"] = {
            "from": ["ABSENT", "PENDING_MAKER_AUTHORIZATION", "SUSPENDED"],
            "to": "ACTIVE",
        }
        recipe["closure_assertions"] = [
            item
            for item in recipe["closure_assertions"]
            if item["assertion_id"] != "budget-unchanged"
        ]
        coordinator = ContextCoordinator(FailingTargetFileStore(self.root, "PROJECT_PLAN.md"))

        result = coordinator.execute_mutation_set(
            mutation_set,
            recipe,
        )

        self.assertIs(MutationSetStatus.ROLLED_BACK, result.status)
        self.assertFalse((self.root / "CAPABILITY_SPIRAL_RECORD.md").exists())

    def test_rollback_failure_returns_failed_without_verified_status(self):
        self.seed_pending_activation()
        coordinator = ContextCoordinator(RollbackFailFileStore(self.root))
        mutation_set = self.activation_transaction_set()

        result = coordinator.execute_mutation_set(
            mutation_set,
            DefinitionResolver().context_event_recipe(mutation_set.event_type),
        )

        self.assertIs(MutationSetStatus.FAILED, result.status)
        self.assertIs(OrchestrationFailureCode.ROLLBACK_FAILED, result.failure_code)
        self.assertNotEqual(MutationSetStatus.VERIFIED, result.status)

    def test_verified_mutation_set_is_idempotent_and_rejects_payload_conflict(self):
        self.seed_pending_activation()
        store = RecordingFileStore(self.root)
        coordinator = ContextCoordinator(store)
        mutation_set = self.activation_transaction_set()
        recipe = DefinitionResolver().context_event_recipe(mutation_set.event_type)

        first = coordinator.execute_mutation_set(mutation_set, recipe)
        write_count = len(store.writes)
        repeated = coordinator.execute_mutation_set(mutation_set, recipe)
        changed = replace(
            mutation_set,
            targets=(replace(mutation_set.targets[0], proposed_content=mutation_set.targets[0].proposed_content + "Note: changed\n"),) + mutation_set.targets[1:],
        )
        conflict = coordinator.execute_mutation_set(changed, recipe)

        self.assertIs(MutationSetStatus.VERIFIED, first.status)
        self.assertEqual(first, repeated)
        self.assertEqual(write_count, len(store.writes))
        self.assertIs(MutationSetStatus.REJECTED, conflict.status)
        self.assertIs(OrchestrationFailureCode.IDEMPOTENCY_CONFLICT, conflict.failure_code)

    def test_authorization_pending_attempt_can_continue_after_maker_confirmation(self):
        self.seed_pending_activation()
        coordinator = ContextCoordinator(FileStore(self.root))
        pending_set = self.activation_transaction_set(include_authorization=False)
        recipe = DefinitionResolver().context_event_recipe(pending_set.event_type)

        pending = coordinator.execute_mutation_set(pending_set, recipe)
        authorized = coordinator.execute_mutation_set(
            replace(
                pending_set,
                authorization_request=self.pending_request(),
                authorization_provenance=self.provenance(),
                attempt_id="attempt-2",
            ),
            recipe,
        )

        self.assertIs(MutationSetStatus.AUTHORIZATION_PENDING, pending.status)
        self.assertIs(MutationSetStatus.VERIFIED, authorized.status)

    def test_verified_idempotency_survives_coordinator_restart(self):
        self.seed_pending_activation()
        mutation_set = self.activation_transaction_set()
        recipe = DefinitionResolver().context_event_recipe(mutation_set.event_type)
        first = ContextCoordinator(FileStore(self.root)).execute_mutation_set(
            mutation_set,
            recipe,
        )
        store = RecordingFileStore(self.root)

        repeated = ContextCoordinator(store).execute_mutation_set(mutation_set, recipe)

        self.assertIs(MutationSetStatus.VERIFIED, first.status)
        self.assertEqual(first, repeated)
        self.assertEqual([], [name for name in store.writes if name.endswith(".md")])

    def test_crash_after_state_commit_recovers_final_closure(self):
        self.seed_pending_activation()
        mutation_set = self.activation_transaction_set()
        recipe = DefinitionResolver().context_event_recipe(mutation_set.event_type)
        crashing = ContextCoordinator(
            CrashAfterTargetFileStore(self.root, "PROJECT_STATE.md")
        )

        with self.assertRaises(SimulatedCrash):
            crashing.execute_mutation_set(mutation_set, recipe)

        recovery_store = RecordingFileStore(self.root)
        recovered = ContextCoordinator(recovery_store).execute_mutation_set(
            mutation_set,
            recipe,
        )
        self.assertIs(MutationSetStatus.VERIFIED, recovered.status)
        self.assertEqual("AUTHORIZED", recovered.authorization_request_status)
        self.assertIn("Extension Status: ACTIVE", self._context_contents()["PROJECT_STATE.md"])
        self.assertEqual([], [name for name in recovery_store.writes if name.endswith(".md")])

    def test_crash_after_partial_commit_restores_snapshots_on_restart(self):
        self.seed_pending_activation()
        before = self._context_contents()
        mutation_set = self.activation_transaction_set()
        recipe = DefinitionResolver().context_event_recipe(mutation_set.event_type)
        crashing = ContextCoordinator(
            CrashAfterTargetFileStore(self.root, "PROJECT_PLAN.md")
        )

        with self.assertRaises(SimulatedCrash):
            crashing.execute_mutation_set(mutation_set, recipe)

        recovered = ContextCoordinator(FileStore(self.root)).execute_mutation_set(
            mutation_set,
            recipe,
        )
        self.assertIs(MutationSetStatus.ROLLED_BACK, recovered.status)
        self.assertEqual(before, self._context_contents())

    def test_execution_record_contains_required_recovery_and_audit_fields(self):
        self.seed_pending_activation()
        mutation_set = self.activation_transaction_set()
        coordinator = ContextCoordinator(FileStore(self.root))
        coordinator.execute_mutation_set(
            mutation_set,
            DefinitionResolver().context_event_recipe(mutation_set.event_type),
        )
        records = list(
            (self.root / ".project_incubator/runtime/mutation_sets").glob("*.json")
        )

        self.assertEqual(1, len(records))
        record = json.loads(records[0].read_text(encoding="utf-8"))
        for field_name in (
            "mutation_set_id",
            "attempt_id",
            "event_type",
            "target_refs",
            "authorization_refs",
            "before_digests",
            "staged_digests",
            "committed_targets",
            "closure_result",
            "rollback_result",
        ):
            self.assertIn(field_name, record)

    def test_corrupt_execution_record_fails_closed_without_context_rewrites(self):
        self.seed_pending_activation()
        mutation_set = self.activation_transaction_set()
        recipe = DefinitionResolver().context_event_recipe(mutation_set.event_type)
        with self.assertRaises(SimulatedCrash):
            ContextCoordinator(
                CrashAfterTargetFileStore(self.root, "PROJECT_PLAN.md")
            ).execute_mutation_set(mutation_set, recipe)
        record = next(
            (self.root / ".project_incubator/runtime/mutation_sets").glob("*.json")
        )
        record.write_text("{corrupt", encoding="utf-8")
        store = RecordingFileStore(self.root)

        result = ContextCoordinator(store).execute_mutation_set(mutation_set, recipe)

        self.assertIs(MutationSetStatus.FAILED, result.status)
        self.assertIs(OrchestrationFailureCode.STAGE_FAILED, result.failure_code)
        self.assertEqual([], [name for name in store.writes if name.endswith(".md")])

    def _context_contents(self):
        return {
            name: (self.root / name).read_text(encoding="utf-8")
            for name in (
                "CAPABILITY_SPIRAL_RECORD.md",
                "PROJECT_PLAN.md",
                "PROJECT_STATE.md",
            )
            if (self.root / name).exists()
        }


class FailingActiveViewFileStore(FileStore):
    def atomic_write(self, path, content):
        if Path(path).name == "PROJECT_DECISIONS.md":
            raise FileWriteError("injected active view failure")
        return super().atomic_write(path, content)


class RecordingFileStore(FileStore):
    def __init__(self, base_dir):
        super().__init__(base_dir)
        self.writes = []

    def atomic_write(self, path, content):
        self.writes.append(Path(path).name)
        return super().atomic_write(path, content)


class FailingTargetFileStore(FileStore):
    def __init__(self, base_dir, target_name):
        super().__init__(base_dir)
        self.target_name = target_name

    def atomic_write(self, path, content):
        if Path(path).name == self.target_name and "Extension Status: ACTIVE" in content:
            raise FileWriteError("injected target failure")
        return super().atomic_write(path, content)


class RollbackFailFileStore(FileStore):
    def atomic_write(self, path, content):
        name = Path(path).name
        if name == "PROJECT_PLAN.md" and "Extension Status: ACTIVE" in content:
            raise FileWriteError("injected commit failure")
        if name == "CAPABILITY_SPIRAL_RECORD.md" and "PENDING_MAKER_AUTHORIZATION" in content:
            raise FileWriteError("injected rollback failure")
        return super().atomic_write(path, content)


class FailingFinalizationCoordinator(ContextCoordinator):
    def _finalize_authorization_request(self, pending_request):
        raise FileWriteError("injected authorization finalization failure")


class SimulatedCrash(BaseException):
    pass


class CrashAfterTargetFileStore(FileStore):
    def __init__(self, base_dir, target_name):
        super().__init__(base_dir)
        self.target_name = target_name
        self.crashed = False

    def atomic_write(self, path, content):
        result = super().atomic_write(path, content)
        if (
            not self.crashed
            and Path(path).name == self.target_name
            and "Extension Status: ACTIVE" in content
        ):
            self.crashed = True
            raise SimulatedCrash("injected process crash")
        return result


class ClosureMismatchFileStore(FileStore):
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
