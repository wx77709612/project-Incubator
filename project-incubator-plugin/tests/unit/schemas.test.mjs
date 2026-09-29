import assert from "node:assert/strict";
import test from "node:test";

import {
  parseActivation,
  parseProjectState,
  parseReceipt,
} from "../../src/kernel/schemas.mjs";

const now = "2026-09-29T00:00:00.000Z";

function validActivation() {
  return {
    schema_version: "1.0",
    project_id: "project-1",
    plugin_id: "project-incubator-plugin",
    plugin_version: "0.1.0",
    status: "ACTIVE",
    project_type_id: "mod",
    child_skill_id: "mod-incubator",
    host_profile_id: "sims-4",
  };
}

function validState() {
  return {
    schema_version: "1.0",
    project_id: "project-1",
    revision: 0,
    boundary: {
      objective: "验证一个最小 Mod 产品点",
      supported: ["一个已确认产品点"],
      excluded: [],
    },
    workflow: {
      stage: "M0_BOUNDARY",
      status: "ACTIVE",
      completed: [],
      allowed_next: ["M1_RISK_MODEL"],
    },
    capabilities: [],
    decisions: { active: [], archive_ref: null },
    assumptions: [],
    plan: {
      current_action: "确认产品边界",
      next_action: "评估宿主风险",
      completion_conditions: ["Maker 确认 Product Point"],
    },
    gates: [],
    risks: [],
    pending_requests: [],
    baselines: [],
    human_validation: { limit: "UNSET", consumed: 0 },
    last_change: {
      operation: "INITIALIZE_PROJECT",
      changed_at: now,
      summary: "初始化项目",
    },
    archive_refs: [],
  };
}

function validReceipt() {
  return {
    schema_version: "1.0",
    receipt_id: "receipt-1",
    project_id: "project-1",
    operation: "INITIALIZE_PROJECT",
    previous_revision: null,
    new_revision: 0,
    previous_state_hash: null,
    new_state_hash: "a".repeat(64),
    authorization_ref: {
      authorization_id: "authorization-1",
      request_id: "request-1",
      prompt_digest: "b".repeat(64),
    },
    committed_at: now,
  };
}

test("parses the minimum complete authority documents", () => {
  assert.deepEqual(parseActivation(validActivation()), validActivation());
  assert.deepEqual(parseProjectState(validState()), validState());
  assert.deepEqual(parseReceipt(validReceipt()), validReceipt());
});

test("rejects encoded JSON strings instead of coercing them", () => {
  assert.throws(() => parseActivation(JSON.stringify(validActivation())));
  assert.throws(() => parseProjectState(JSON.stringify(validState())));
  assert.throws(() => parseReceipt(JSON.stringify(validReceipt())));
});

test("rejects incomplete state partitions and unsupported versions", () => {
  const { plan: _plan, ...withoutPlan } = validState();
  assert.throws(() => parseProjectState(withoutPlan));
  assert.throws(() =>
    parseProjectState({ ...validState(), schema_version: "2.0" }),
  );
});

test("rejects invalid revisions and unknown authority fields", () => {
  for (const revision of [-1, 1.5, null, "1"]) {
    assert.throws(() => parseProjectState({ ...validState(), revision }));
  }
  assert.throws(() =>
    parseProjectState({ ...validState(), shadow_authority: true }),
  );
});

test("bounds active collections and validates receipt hashes", () => {
  assert.throws(() =>
    parseProjectState({
      ...validState(),
      capabilities: Array.from({ length: 101 }, (_, index) => ({
        capability_id: `cap-${index}`,
        claim: "claim",
        evidence_level: "E0",
      })),
    }),
  );
  assert.throws(() =>
    parseReceipt({ ...validReceipt(), new_state_hash: "not-a-hash" }),
  );
});

