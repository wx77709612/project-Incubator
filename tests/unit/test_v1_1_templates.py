import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "PROJECT_INCUBATOR"


class V11TemplateTest(unittest.TestCase):
    def read(self, relative_path):
        return (PACKAGE / relative_path).read_text(encoding="utf-8")

    def test_capability_spiral_record_is_optional_and_complete(self):
        content = self.read("templates/context/CAPABILITY_SPIRAL_RECORD.template.md")
        required_headings = (
            "## 能力声明",
            "## 不透明度评估",
            "## 当前验证轮",
            "## 支持边界",
            "## 排除边界",
            "## 候选模型",
            "## 已观察事实",
            "## 运行时假设",
            "## 竞争假设",
            "## 证据等级",
            "## 可重复验证",
            "## 目标环境证据",
            "## 已知可用基线",
            "## 失效信号",
            "## 单圈闭合",
            "## 兼容性扩圈",
            "## 人工验证预算",
            "## 下一扩展维度",
        )
        for heading in required_headings:
            self.assertIn(heading, content)
        self.assertIn("仅为高不透明 Capability 创建", content)
        self.assertNotIn("所有项目必须创建", content)
        self.assertNotIn("替代 `PROJECT_STATE.md`", content)

    def test_decision_record_supports_active_view_and_bounded_history(self):
        content = self.read("templates/context/DECISION_RECORD.template.md")
        for field_name in (
            "Status",
            "Supersedes",
            "Affected Decisions",
            "New Evidence",
            "Effective Scope",
            "Migration Impact",
            "Bounded Changelog",
            "Archive Ref",
        ):
            self.assertIn(field_name, content)
        self.assertNotIn("历史 Decision 不覆盖、不改写", content)

    def test_implementation_plan_scales_validation_with_capability_risk(self):
        content = self.read("templates/artifacts/IMPLEMENTATION_PLAN.template.md")
        for heading in (
            "## Capability Risk",
            "## Representative Vertical Slice",
            "## Evidence Target",
            "## Human Validation Budget",
            "## Failure Stop Condition",
        ):
            self.assertIn(heading, content)
        self.assertIn("仅对高不透明 Capability", content)

    def test_skill_keeps_transparent_path_lightweight_and_correction_inside_p4(self):
        skill = self.read("SKILL.md")
        self.assertIn("透明 Capability", skill)
        self.assertIn("E0", skill)
        self.assertIn("E5", skill)
        self.assertIn("P4 内部", skill)
        self.assertIn("不得把 P4 Correction 表述为进入 P6、P2 或 P3", skill)
        self.assertIn("Capability 级", skill)
        self.assertNotIn("所有 Managed Project 必须创建 `CAPABILITY_SPIRAL_RECORD.md`", skill)

    def test_skill_requires_explicit_authorization_and_multi_context_closure(self):
        skill = self.read("SKILL.md")
        for phrase in (
            "Multi-Context Trigger",
            "Mutation Set Summary",
            "maker_statement_excerpt",
            "Changed Targets",
            "Closure Result",
            "Unchanged Phase",
        ):
            self.assertIn(phrase, skill)
        for ambiguous_phrase in ("评估", "提出请求", "继续", "风险确认"):
            self.assertIn(f"`{ambiguous_phrase}`", skill)
        self.assertIn("不得推断为 Maker Authorization", skill)
        self.assertIn("PENDING_MAKER_AUTHORIZATION", skill)
        self.assertIn("闭合验证通过后", skill)

    def test_extension_fields_are_conditional_and_trace_authorization(self):
        fields = (
            "Extension Status",
            "Authorization Request Ref",
            "Authorization Evidence Ref",
            "Mutation Set Ref",
            "Closure Result Ref",
        )
        for template in (
            "templates/context/PROJECT_STATE.template.md",
            "templates/context/PROJECT_PLAN.template.md",
            "templates/context/CAPABILITY_SPIRAL_RECORD.template.md",
        ):
            content = self.read(template)
            with self.subTest(template=template):
                for field_name in fields:
                    self.assertIn(field_name, content)
                self.assertIn("条件区块", content)
                self.assertIn("透明", content)
                self.assertIn("省略", content)

    def test_codex_entry_requires_runtime_owned_multi_context_completion_report(self):
        agents = self.read("templates/integrations/codex/AGENTS.template.md")
        for phrase in (
            "Multi-Context Trigger",
            "Mutation Set Summary",
            "Authorization Basis",
            "Pending Status",
            "Changed Targets",
            "Closure Result",
            "Unchanged Phase",
        ):
            self.assertIn(phrase, agents)
        self.assertIn("Maker", agents)
        self.assertIn("Runtime", agents)


if __name__ == "__main__":
    unittest.main()
