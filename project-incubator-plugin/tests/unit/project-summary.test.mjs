import assert from "node:assert/strict";
import test from "node:test";

import { buildProjectSummary, renderProjectSummary } from "../../src/kernel/project-summary.mjs";

function snapshot() {
  return {
    activation: {
      project_id: "project-1", project_type_id: "mod", child_skill_id: "mod-incubator",
      host_profile_id: "sims-4",
    },
    state: {
      project_id: "project-1", revision: 7,
      boundary: { objective: "让玩家获得一个可靠交互", supported: ["交互 A"], excluded: ["多人模式"] },
      workflow: {
        stage: "M2_VERTICAL_SLICE", status: "ACTIVE",
        completed: ["已确认产品边界"], allowed_next: ["M3_BUILD_PACKAGE", "MODEL_REVIEW"],
      },
      capabilities: [{
        capability_id: "cap-1", claim: "交互 A 可完成", evidence_level: "E3",
        status: "ACTIVE", confidence: "MEDIUM", evidence_refs: ["trace:1"], baseline_id: null,
      }],
      decisions: { active: [], archive_ref: null },
      assumptions: [],
      plan: { current_action: "验证生命周期", next_action: "检查构建包", completion_conditions: ["完整路径可观察"] },
      gates: [{ gate_id: "gate-1", status: "BLOCKED", reason: "等待宿主观察" }],
      risks: [{ risk_id: "risk-1", summary: "宿主状态隐藏", severity: "HIGH", status: "OPEN" }],
      pending_requests: [{ request_id: "request-1", operation: "CHANGE_BOUNDARY", status: "PENDING" }],
      baselines: [], human_validation: { limit: "UNSET", consumed: 0 },
      last_change: {
        operation: "ADVANCE", changed_at: "2026-09-29T10:00:00.000Z",
        summary: "进入垂直切片", receipt_id: "receipt-7",
      },
    },
  };
}

test("summary contains the complete fixed status contract", () => {
  const summary = buildProjectSummary(snapshot(), { verified: true, reason: null });
  assert.deepEqual(Object.keys(summary), [
    "project", "boundary", "routing", "workflow", "recent_completed", "evidence_ceiling",
    "actions", "blockers", "risks", "maker_decisions", "capabilities", "baselines",
    "human_validation", "last_change", "integrity",
  ]);
  assert.equal(summary.project.revision, 7);
  assert.equal(summary.routing.host_profile_id, "sims-4");
  assert.equal(summary.evidence_ceiling, "E3");
  assert.equal(summary.blockers[0].reason, "等待宿主观察");
  assert.equal(summary.maker_decisions[0].request_id, "request-1");
  assert.equal(summary.integrity.receipt_verified, true);
});

test("rendered Chinese summary has deterministic sections and honest empty values", () => {
  const text = renderProjectSummary(buildProjectSummary(snapshot(), { verified: true, reason: null }));
  const headings = [
    "项目与边界", "路由与阶段", "最近完成与证据上限", "当前行动", "阻塞与风险",
    "待 Maker 决策", "能力、基线与人工验证", "最近变更与完整性",
  ];
  let cursor = -1;
  for (const heading of headings) {
    const next = text.indexOf(heading);
    assert.ok(next > cursor, `${heading} 顺序错误`);
    cursor = next;
  }
  assert.match(text, /Known-Good Baseline：未建立/);
  assert.match(text, /人工验证预算：未由 Maker 设置/);
});
