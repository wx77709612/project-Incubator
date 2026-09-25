import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class ContextMutationOrchestrationAcceptance(unittest.TestCase):
    def test_f01_round_2_and_round_2r_replay_passes(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tests/integration/test_mutation_orchestration_flow.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def test_f02_manual_protocol_contains_round_2r_and_evidence_fields(self):
        manual_root = ROOT / "ACCEPTANCE_TESTS/manual/v1_1_rc"
        prompts = (manual_root / "AGENT_PROMPTS.md").read_text(encoding="utf-8")
        answers = (manual_root / "MAKER_ANSWER_KEY.md").read_text(encoding="utf-8")
        readme = (manual_root / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Round 2R", prompts)
        self.assertIn("## Round 2R", answers)
        for field_name in (
            "Authorization Basis",
            "Changed Targets",
            "Closure Result",
            "Unchanged Phase",
        ):
            self.assertIn(field_name, readme)


if __name__ == "__main__":
    unittest.main()
