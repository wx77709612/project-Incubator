import dataclasses
import unittest

from PROJECT_INCUBATOR.runtime.core.evidence_types import (
    AssumptionStatus,
    BaselineStatus,
    ClaimStatus,
    CorrectionActivityState,
    CorrectionResult,
    EvidenceLevel,
    FailureObservation,
    OpacityLevel,
    extension_recommended,
    failure_signature,
    validate_thresholds,
)


class EvidenceTypesTest(unittest.TestCase):
    def test_enum_values_match_the_approved_contract(self):
        self.assertEqual([f"E{index}" for index in range(6)], [level.value for level in EvidenceLevel])
        self.assertIn(ClaimStatus.REPRESENTATIVE_BOUNDARY_VALIDATED, ClaimStatus)
        self.assertIn(AssumptionStatus.INVALIDATED, AssumptionStatus)
        self.assertIn(BaselineStatus.REGRESSED, BaselineStatus)
        self.assertIn(CorrectionResult.CORRECTION_ASSESSMENT_INVALID, CorrectionResult)
        self.assertIn(CorrectionActivityState.CORRECTION_ACTIVE, CorrectionActivityState)

    def test_failure_observation_is_immutable(self):
        observation = FailureObservation("cap", "scene", "boundary", "missing")

        with self.assertRaises(dataclasses.FrozenInstanceError):
            observation.observed_outcome = "changed"

    def test_failure_signature_is_deterministic_and_excludes_hypothesized_cause(self):
        observation = FailureObservation("cap", "scene", "boundary", "missing")

        left = failure_signature(observation)
        right = failure_signature("cap", "scene", "boundary", "missing")

        self.assertEqual(left, right)
        self.assertEqual(64, len(left))

    def test_failure_signature_changes_when_a_stable_field_changes(self):
        original = failure_signature("cap", "scene", "boundary", "missing")
        changed = failure_signature("cap", "scene", "boundary", "blocked")

        self.assertNotEqual(original, changed)

    def test_failure_signature_rejects_empty_stable_fields(self):
        with self.assertRaises(ValueError):
            failure_signature("cap", "", "boundary", "missing")

    def test_default_and_earlier_thresholds_are_valid(self):
        self.assertEqual((2, 3), validate_thresholds(advisory=2, correction=3))
        self.assertEqual((1, 2), validate_thresholds(advisory=1, correction=2))

    def test_relaxed_or_unordered_thresholds_are_rejected(self):
        invalid_pairs = ((3, 4), (2, 4), (2, 2), (0, 1), (True, 2))

        for advisory, correction in invalid_pairs:
            with self.subTest(advisory=advisory, correction=correction):
                with self.assertRaises((TypeError, ValueError)):
                    validate_thresholds(advisory=advisory, correction=correction)

    def test_high_or_unknown_dimension_recommends_extension(self):
        self.assertTrue(extension_recommended([OpacityLevel.LOW, OpacityLevel.HIGH]))
        self.assertTrue(extension_recommended([OpacityLevel.UNKNOWN]))

    def test_two_elevated_dimensions_recommend_extension(self):
        self.assertTrue(extension_recommended([OpacityLevel.ELEVATED, OpacityLevel.ELEVATED]))

    def test_low_or_single_elevated_dimension_keeps_core_path(self):
        self.assertFalse(extension_recommended([OpacityLevel.LOW]))
        self.assertFalse(extension_recommended([OpacityLevel.ELEVATED, OpacityLevel.LOW]))


if __name__ == "__main__":
    unittest.main()
