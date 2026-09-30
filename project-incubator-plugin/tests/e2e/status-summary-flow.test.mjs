import assert from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { createKernelService } from "../../src/server.mjs";
import { initializeProjectState } from "../../src/kernel/state-store.mjs";

test("three authority files restore a complete verified status summary", async (t) => {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-e2e-summary-"));
  const runtime = await mkdtemp(path.join(os.tmpdir(), "incubator-e2e-summary-runtime-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  t.after(() => rm(runtime, { recursive: true, force: true }));
  const at = "2026-09-29T12:00:00.000Z";
  const activation = { schema_version: "1.0", project_id: "summary-project", plugin_id: "project-incubator-plugin", plugin_version: "0.1.0", status: "ACTIVE", project_type_id: "mod", child_skill_id: "mod-incubator", host_profile_id: "sims-4" };
  const state = { schema_version: "1.0", project_id: "summary-project", revision: 0, boundary: { objective: "恢复摘要", supported: ["状态查询"], excluded: [] }, workflow: { stage: "M1_RISK_MODEL", status: "ACTIVE", completed: ["边界已确认"], allowed_next: ["M2_VERTICAL_SLICE"] }, capabilities: [], decisions: { active: [], archive_ref: null }, assumptions: [], plan: { current_action: "风险评估", next_action: "垂直切片", completion_conditions: ["风险可见"] }, gates: [], risks: [], pending_requests: [], baselines: [], human_validation: { limit: "UNSET", consumed: 0 }, last_change: { operation: "INITIALIZE_PROJECT", changed_at: at, summary: "恢复" }, archive_refs: [] };
  await initializeProjectState(root, activation, state, { authorization_id: "a", request_id: "r", prompt_digest: "c".repeat(64) });
  const service = await createKernelService({ pluginRoot: path.resolve(import.meta.dirname, "../.."), runtimeDataRoot: runtime });
  const result = await service.callTool("inspect_project", { project_root: root });
  assert.equal(result.structuredContent.summary.workflow.stage, "M1_RISK_MODEL");
  assert.match(result.structuredContent.markdown, /Receipt：已验证/);
});
