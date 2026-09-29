import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { initializeProjectState, verifyLatestReceipt } from "../../src/kernel/state-store.mjs";

const authorizationRef = {
  authorization_id: "authorization-1", request_id: "request-1", prompt_digest: "b".repeat(64),
};
const activation = {
  schema_version: "1.0", project_id: "project-1", plugin_id: "project-incubator-plugin",
  plugin_version: "0.1.0", status: "ACTIVE", project_type_id: "mod",
  child_skill_id: "mod-incubator", host_profile_id: "sims-4",
};
const state = {
  schema_version: "1.0", project_id: "project-1", revision: 0,
  boundary: { objective: "最小 Mod", supported: [], excluded: [] },
  workflow: { stage: "M0_BOUNDARY", status: "ACTIVE", completed: [], allowed_next: [] },
  capabilities: [], decisions: { active: [], archive_ref: null }, assumptions: [],
  plan: { current_action: "确认", next_action: "继续", completion_conditions: [] },
  gates: [], risks: [], pending_requests: [], baselines: [],
  human_validation: { limit: "UNSET", consumed: 0 },
  last_change: { operation: "INITIALIZE_PROJECT", changed_at: "2026-09-29T00:00:00.000Z", summary: "初始化" },
  archive_refs: [],
};

async function initialized(t) {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-receipt-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  const receipt = await initializeProjectState(root, activation, state, authorizationRef);
  return { root, receipt };
}

test("verifies receipt id, state hash, revision, project, operation, and authorization", async (t) => {
  const { root, receipt } = await initialized(t);
  const result = await verifyLatestReceipt(root, receipt.receipt_id);
  assert.equal(result.verified, true);
  assert.equal(result.receipt.authorization_ref.authorization_id, "authorization-1");
  assert.equal(result.receipt.operation, "INITIALIZE_PROJECT");
});

test("matching receipt id cannot hide a state hash mismatch", async (t) => {
  const { root, receipt } = await initialized(t);
  const statePath = path.join(root, ".project-incubator", "state.json");
  const value = JSON.parse(await readFile(statePath, "utf8"));
  value.plan.next_action = "tampered";
  await writeFile(statePath, JSON.stringify(value));
  const result = await verifyLatestReceipt(root, receipt.receipt_id);
  assert.equal(result.verified, false);
  assert.equal(result.reason, "STATE_HASH_MISMATCH");
});

test("matching receipt id cannot hide a revision mismatch", async (t) => {
  const { root, receipt } = await initialized(t);
  const receiptPath = path.join(root, ".project-incubator", "latest-receipt.json");
  const value = JSON.parse(await readFile(receiptPath, "utf8"));
  value.new_revision = 1;
  await writeFile(receiptPath, JSON.stringify(value));
  const result = await verifyLatestReceipt(root, receipt.receipt_id);
  assert.equal(result.verified, false);
  assert.equal(result.reason, "REVISION_MISMATCH");
});
