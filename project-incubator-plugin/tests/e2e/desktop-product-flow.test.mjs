import assert from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { handleUserPromptSubmit } from "../../hooks/user-prompt-submit.mjs";
import { createKernelService } from "../../src/server.mjs";

const activatedAt = "2026-10-05T15:00:00.000Z";

function initialState(stage = "P0") {
  const next = { P0: ["P1"], P3: ["P4"] };
  return {
    schema_version: "1.1", project_id: "desktop-e2e", revision: 0,
    boundary: { objective: "交付一个 Windows 桌面产品", supported: ["桌面应用"], excluded: ["浏览器扩展"] },
    workflow: {
      stage, status: "ACTIVE", completed: [], allowed_next: next[stage],
      entry: {
        mode: "NEW_PROJECT", initial_stage: stage,
        assessment_summary: "Maker 确认创建新的 Desktop Managed Project。",
        evidence_refs: [], assessed_at: activatedAt,
      },
    },
    capabilities: [], decisions: { active: [], archive_ref: null }, assumptions: [],
    plan: { current_action: "确认产品意图", next_action: "定义项目", completion_conditions: ["Maker 确认意图"] },
    gates: [], risks: [], pending_requests: [], baselines: [],
    human_validation: { limit: "UNSET", consumed: 0 },
    last_change: { operation: "INITIALIZE_PROJECT", changed_at: activatedAt, summary: "初始化桌面项目" },
    archive_refs: [],
  };
}

async function fixture(t) {
  const root = await mkdtemp(path.join(os.tmpdir(), "desktop-e2e-project-"));
  const runtime = await mkdtemp(path.join(os.tmpdir(), "desktop-e2e-runtime-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  t.after(() => rm(runtime, { recursive: true, force: true }));
  const pluginRoot = path.resolve(import.meta.dirname, "../..");
  return { root, runtime, service: await createKernelService({ pluginRoot, runtimeDataRoot: runtime }) };
}

async function approve(runtime, root, request, turnId, at = activatedAt) {
  await handleUserPromptSubmit({
    cwd: root, session_id: "desktop-e2e-session", turn_id: turnId, timestamp: at,
    prompt: `我明确批准 ${request.request_id}，scope_digest: ${request.scope_digest}`,
  }, { runtimeDataRoot: runtime, now: new Date(at) });
}

test("desktop route, activation, receipt and P0-P1 transition close end to end", async (t) => {
  const { root, runtime, service } = await fixture(t);
  const route = await service.callTool("propose_route", {
    project_root: root, project_type_id: "desktop-product", host_profile_id: "windows-desktop",
  });
  assert.deepEqual(route.structuredContent.route, {
    project_type_id: "desktop-product", child_skill_id: "desktop-product-incubator",
    host_profile_id: "windows-desktop",
  });

  const prepared = (await service.callTool("prepare_activation", {
    project_root: root, project_id: "desktop-e2e", project_type_id: "desktop-product",
    host_profile_id: "windows-desktop", session_id: "desktop-e2e-session",
    summary: "激活 Desktop Product Incubator", state: initialState(),
    product_decisions: [{ decision_id: "desktop-boundary", statement: "批准 Windows 桌面产品边界。" }],
  }, { now: new Date(activatedAt) })).structuredContent;
  await approve(runtime, root, prepared, "activate");
  const initialized = await service.callTool("initialize_project", {
    project_root: root, request_id: prepared.request_id, scope_digest: prepared.scope_digest,
    session_id: "desktop-e2e-session", turn_id: "activate",
  }, { now: new Date(activatedAt) });
  assert.equal(initialized.isError, undefined);
  assert.equal(initialized.structuredContent.activation.plugin_version, "0.3.0");

  const initialSnapshot = await service.callTool("get_project_state", { project_root: root });
  assert.equal(initialSnapshot.structuredContent.activation.project_type_id, "desktop-product");
  assert.equal(initialSnapshot.structuredContent.activation.host_profile_id, "windows-desktop");
  assert.equal(initialSnapshot.structuredContent.state.workflow.stage, "P0");
  assert.equal(initialSnapshot.structuredContent.state.workflow.entry.mode, "NEW_PROJECT");
  const activationReceipt = await service.callTool("verify_receipt", {
    project_root: root, receipt_id: initialized.structuredContent.receipt.receipt_id,
  });
  assert.equal(activationReceipt.structuredContent.verified, true);

  const proposed = structuredClone(initialSnapshot.structuredContent.state);
  proposed.workflow.stage = "P1";
  proposed.workflow.allowed_next = ["P2"];
  proposed.plan.current_action = "定义桌面项目边界";
  const transitionAt = "2026-10-05T15:01:00.000Z";
  const transition = (await service.callTool("prepare_change", {
    project_root: root, operation: "ADVANCE_DESKTOP_STAGE", change_kind: "WORKFLOW_TRANSITION",
    session_id: "desktop-e2e-session", proposed_state: proposed,
    workflow_transition: { target_stage: "P1", completion_satisfied: true },
  }, { now: new Date(transitionAt) })).structuredContent;
  await approve(runtime, root, transition, "advance", transitionAt);
  const committed = await service.callTool("commit_change", {
    project_root: root, request_id: transition.request_id, scope_digest: transition.scope_digest,
    session_id: "desktop-e2e-session", turn_id: "advance",
  }, { now: new Date(transitionAt) });
  assert.equal(committed.isError, undefined);
  assert.equal(committed.structuredContent.receipt.authorization_ref.request_id, transition.request_id);

  const finalSnapshot = await service.callTool("get_project_state", { project_root: root });
  assert.equal(finalSnapshot.structuredContent.state.workflow.stage, "P1");
  assert.equal(finalSnapshot.structuredContent.state.workflow.entry.initial_stage, "P0");
  assert.deepEqual(finalSnapshot.structuredContent.state.pending_requests, []);
  const transitionReceipt = await service.callTool("verify_receipt", {
    project_root: root, receipt_id: committed.structuredContent.receipt.receipt_id,
  });
  assert.equal(transitionReceipt.structuredContent.verified, true);
});

test("desktop activation fails closed without an explicit host", async (t) => {
  const { root, service } = await fixture(t);
  const result = await service.callTool("prepare_activation", {
    project_root: root, project_id: "desktop-e2e", project_type_id: "desktop-product",
    session_id: "desktop-e2e-session", summary: "不得默认 Host", state: initialState(),
    product_decisions: [{ decision_id: "desktop-boundary", statement: "桌面边界。" }],
  });
  assert.equal(result.structuredContent.error.code, "HOST_PROFILE_REQUIRED");
});

test("desktop NEW_PROJECT rejects an illegal initial phase", async (t) => {
  const { root, service } = await fixture(t);
  const result = await service.callTool("prepare_activation", {
    project_root: root, project_id: "desktop-e2e", project_type_id: "desktop-product",
    host_profile_id: "windows-desktop", session_id: "desktop-e2e-session",
    summary: "非法初始阶段", state: initialState("P3"),
    product_decisions: [{ decision_id: "desktop-boundary", statement: "桌面边界。" }],
  });
  assert.equal(result.structuredContent.error.code, "WORKFLOW_ENTRY_STAGE_INVALID");
});

test("activated desktop entry cannot be altered", async (t) => {
  const { root, runtime, service } = await fixture(t);
  const prepared = (await service.callTool("prepare_activation", {
    project_root: root, project_id: "desktop-e2e", project_type_id: "desktop-product",
    host_profile_id: "windows-desktop", session_id: "desktop-e2e-session",
    summary: "激活", state: initialState(),
    product_decisions: [{ decision_id: "desktop-boundary", statement: "桌面边界。" }],
  }, { now: new Date(activatedAt) })).structuredContent;
  await approve(runtime, root, prepared, "activate-entry");
  await service.callTool("initialize_project", {
    project_root: root, request_id: prepared.request_id, scope_digest: prepared.scope_digest,
    session_id: "desktop-e2e-session", turn_id: "activate-entry",
  }, { now: new Date(activatedAt) });
  const snapshot = await service.callTool("get_project_state", { project_root: root });
  const proposed = structuredClone(snapshot.structuredContent.state);
  proposed.workflow.entry.assessment_summary = "事后改写";
  const result = await service.callTool("prepare_change", {
    project_root: root, operation: "ALTER_ENTRY", change_kind: "PRODUCT_DECISION",
    session_id: "desktop-e2e-session", proposed_state: proposed,
  });
  assert.equal(result.structuredContent.error.code, "WORKFLOW_ENTRY_IMMUTABLE");
});

test("browser-only scope is unsupported instead of routed to desktop", async (t) => {
  const { root, service } = await fixture(t);
  const result = await service.callTool("propose_route", {
    project_root: root, project_type_id: "browser-extension",
  });
  assert.equal(result.structuredContent.error.code, "PROJECT_TYPE_NOT_FOUND");
});
