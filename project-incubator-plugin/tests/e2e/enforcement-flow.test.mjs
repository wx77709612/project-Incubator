import assert from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { handlePreToolUse } from "../../hooks/pre-tool-use.mjs";
import { handleStop } from "../../hooks/stop.mjs";
import { handleUserPromptSubmit } from "../../hooks/user-prompt-submit.mjs";
import { createKernelService } from "../../src/server.mjs";

const now = "2026-09-29T12:00:00.000Z";
const initialState = () => ({
  schema_version: "1.0", project_id: "e2e-project", revision: 0,
  boundary: { objective: "端到端 Mod", supported: ["单一产品点"], excluded: [] },
  workflow: { stage: "M0_BOUNDARY", status: "ACTIVE", completed: [], allowed_next: ["M1_RISK_MODEL"] },
  capabilities: [], decisions: { active: [], archive_ref: null }, assumptions: [],
  plan: { current_action: "确认边界", next_action: "风险建模", completion_conditions: ["Maker 确认"] },
  gates: [], risks: [], pending_requests: [], baselines: [], human_validation: { limit: "UNSET", consumed: 0 },
  last_change: { operation: "INITIALIZE_PROJECT", changed_at: now, summary: "初始化" }, archive_refs: [],
});

test("Maker-approved activation, protected writes, Receipt and Stop close end to end", async (t) => {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-e2e-flow-"));
  const runtime = await mkdtemp(path.join(os.tmpdir(), "incubator-e2e-runtime-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  t.after(() => rm(runtime, { recursive: true, force: true }));
  const service = await createKernelService({ pluginRoot: path.resolve(import.meta.dirname, "../.."), runtimeDataRoot: runtime });
  const prepared = (await service.callTool("prepare_activation", {
    project_root: root, project_id: "e2e-project", project_type_id: "mod", host_profile_id: "sims-4",
    session_id: "s1", summary: "激活", state: initialState(),
    product_decisions: [{ decision_id: "e2e-boundary", statement: "批准端到端 Mod 产品边界。" }],
  }, { now: new Date(now) })).structuredContent;
  await handleUserPromptSubmit({
    cwd: root, session_id: "s1", turn_id: "t1", timestamp: now,
    prompt: `我明确批准 ${prepared.request_id}，scope_digest: ${prepared.scope_digest}`,
  }, { runtimeDataRoot: runtime, now: new Date(now) });
  const initialized = await service.callTool("initialize_project", {
    project_root: root, request_id: prepared.request_id, scope_digest: prepared.scope_digest,
    session_id: "s1", turn_id: "t1",
  }, { now: new Date(now) });
  assert.equal(initialized.isError, undefined);
  const receiptId = initialized.structuredContent.receipt.receipt_id;
  const state = await service.callTool("get_project_state", { project_root: root });
  assert.equal(state.structuredContent.state.decisions.active.length, 1);
  const summary = await service.callTool("inspect_project", { project_root: root });
  assert.equal(summary.structuredContent.summary.actions.current, "确认边界");
  assert.equal(summary.structuredContent.summary.last_change.operation, "INITIALIZE_PROJECT");
  const denied = await handlePreToolUse({
    cwd: root, tool_name: "apply_patch", tool_input: { patch: "*** Update File: .project-incubator/state.json" },
  });
  assert.equal(denied.hookSpecificOutput.permissionDecision, "deny");
  await handleUserPromptSubmit({ cwd: root, session_id: "s1", turn_id: "t2", timestamp: "2026-09-29T12:01:00.000Z", prompt: "查询" }, { runtimeDataRoot: runtime, now: new Date("2026-09-29T12:01:00.000Z") });
  assert.deepEqual(await handleStop({ cwd: root, session_id: "s1", turn_id: "t2", last_assistant_message: `receipt_id: ${receiptId}` }, { runtimeDataRoot: runtime }), { continue: true });
});
