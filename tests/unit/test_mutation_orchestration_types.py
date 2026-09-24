import unittest

from PROJECT_INCUBATOR.runtime.core.mutation_orchestration_types import (
    AuthorityRequirement,
    ClosureAssertion,
    ClosureOperator,
    ContextMutationSet,
    ExtensionStatus,
    MutationSetStatus,
    MutationTargetSpec,
    OrchestrationFailureCode,
)


def target(context_type, order, *, reference=None):
    return MutationTargetSpec(
        context_type=context_type,
        context_reference=reference,
        mutation_intent="UPDATE_CONTEXT",
        proposed_content=f"Extension Status: {ExtensionStatus.ACTIVE.value}\n",
        commit_order=order,
    )


def assertion(assertion_id="status"):
    return ClosureAssertion(
        assertion_id=assertion_id,
        left_ref="PROJECT_STATE.Extension Status",
        operator=ClosureOperator.EQUALS,
        right_value_or_ref=ExtensionStatus.ACTIVE.value,
    )


class MutationOrchestrationTypesTest(unittest.TestCase):
    def test_frozen_enum_values_match_contract(self):
        self.assertEqual("MAKER_AND_EVIDENCE", AuthorityRequirement.MAKER_AND_EVIDENCE.value)
        self.assertEqual("PENDING_MAKER_AUTHORIZATION", ExtensionStatus.PENDING_MAKER_AUTHORIZATION.value)
        self.assertEqual("FINALIZING_AUTHORIZATION", MutationSetStatus.FINALIZING_AUTHORIZATION.value)
        self.assertEqual("UNCHANGED", ClosureOperator.UNCHANGED.value)
        self.assertEqual("ROLLBACK_FAILED", OrchestrationFailureCode.ROLLBACK_FAILED.value)

    def test_targets_are_ordered_with_project_state_last(self):
        mutation_set = ContextMutationSet(
            mutation_set_id="ms-1",
            event_type="OPAQUE_EXTENSION_ACTIVATED",
            event_ref="capability:C-1",
            current_phase="P2",
            requested_by="AGENT",
            authority_requirement=AuthorityRequirement.MAKER,
            targets=(
                target("PROJECT_STATE", 30),
                target("CAPABILITY_SPIRAL_RECORD", 10),
                target("PROJECT_PLAN", 20),
            ),
            closure_assertions=(assertion(),),
        )

        self.assertEqual("PROJECT_STATE", mutation_set.ordered_targets[-1].context_type)
        self.assertEqual(
            ("CAPABILITY_SPIRAL_RECORD", "PROJECT_PLAN", "PROJECT_STATE"),
            tuple(item.context_type for item in mutation_set.ordered_targets),
        )

    def test_duplicate_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate mutation target"):
            ContextMutationSet(
                mutation_set_id="ms-duplicate",
                event_type="OPAQUE_EXTENSION_ACTIVATED",
                event_ref="capability:C-1",
                current_phase="P2",
                requested_by="AGENT",
                authority_requirement=AuthorityRequirement.MAKER,
                targets=(target("PROJECT_PLAN", 10), target("PROJECT_PLAN", 20)),
                closure_assertions=(assertion(),),
            )

    def test_project_state_must_have_highest_commit_order(self):
        with self.assertRaisesRegex(ValueError, "PROJECT_STATE must commit last"):
            ContextMutationSet(
                mutation_set_id="ms-order",
                event_type="OPAQUE_EXTENSION_ACTIVATED",
                event_ref="capability:C-1",
                current_phase="P2",
                requested_by="AGENT",
                authority_requirement=AuthorityRequirement.MAKER,
                targets=(target("PROJECT_STATE", 10), target("PROJECT_PLAN", 20)),
                closure_assertions=(assertion(),),
            )

    def test_idempotency_key_is_stable_and_payload_digest_detects_change(self):
        first = ContextMutationSet(
            mutation_set_id="ms-stable",
            event_type="OPAQUE_EXTENSION_ACTIVATED",
            event_ref="capability:C-1",
            current_phase="P2",
            requested_by="AGENT",
            authority_requirement=AuthorityRequirement.MAKER,
            targets=(target("PROJECT_PLAN", 10), target("PROJECT_STATE", 20)),
            closure_assertions=(assertion(),),
        )
        same = ContextMutationSet(
            mutation_set_id="ms-stable",
            event_type="OPAQUE_EXTENSION_ACTIVATED",
            event_ref="capability:C-1",
            current_phase="P2",
            requested_by="AGENT",
            authority_requirement=AuthorityRequirement.MAKER,
            targets=(target("PROJECT_PLAN", 10), target("PROJECT_STATE", 20)),
            closure_assertions=(assertion(),),
        )
        changed = ContextMutationSet(
            mutation_set_id="ms-stable",
            event_type="OPAQUE_EXTENSION_ACTIVATED",
            event_ref="capability:C-1",
            current_phase="P2",
            requested_by="AGENT",
            authority_requirement=AuthorityRequirement.MAKER,
            targets=(
                MutationTargetSpec(
                    context_type="PROJECT_PLAN",
                    mutation_intent="UPDATE_CONTEXT",
                    proposed_content="Extension Status: SUSPENDED\n",
                    commit_order=10,
                ),
                target("PROJECT_STATE", 20),
            ),
            closure_assertions=(assertion(),),
        )

        self.assertEqual(first.idempotency_key, same.idempotency_key)
        self.assertEqual(first.payload_digest, same.payload_digest)
        self.assertEqual(first.idempotency_key, changed.idempotency_key)
        self.assertNotEqual(first.payload_digest, changed.payload_digest)


if __name__ == "__main__":
    unittest.main()
