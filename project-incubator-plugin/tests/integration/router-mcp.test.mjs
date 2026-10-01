import assert from "node:assert/strict";
import { access, mkdir, mkdtemp, readdir, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { handleUserPromptSubmit } from "../../hooks/user-prompt-submit.mjs";
import { createKernelService } from "../../src/server.mjs";
import { initializeProjectState } from "../../src/kernel/state-store.mjs";

const approvalTime = "2026-09-29T09:01:00.000Z";

function initialState() {
  return {
    schema_version: "1.0", project_id: "project-1", revision: 0,
    boundary: { objective: "验证一个 Mod 产品点", supported: ["单一能力"], excluded: [] },
    workflow: { stage: "M0_BOUNDARY", status: "ACTIVE", completed: [], allowed_next: ["M1_RISK_MODEL"] },
    capabilities: [], decisions: { active: [], archive_ref: null }, assumptions: [],
    plan: { current_action: "确认边界", next_action: "风险建模", completion_conditions: ["Maker 确认"] },
    gates: [], risks: [], pending_requests: [], baselines: [],
    human_validation: { limit: "UNSET", consumed: 0 },
    last_change: { operation: "INITIALIZE_PROJECT", changed_at: approvalTime, summary: "首次激活" },
    archive_refs: [],
  };
}

function productDecisions() {
  return [{
    decision_id: "product-boundary-1",
    statement: "仅孵化一个由 Maker 确认的 Mod 产品点。",
  }];
}

async function fixture(t) {
  const projectRoot = await mkdtemp(path.join(os.tmpdir(), "incubator-router-project-"));
  const runtimeDataRoot = await mkdtemp(path.join(os.tmpdir(), "incubator-router-runtime-"));
  const codexHome = path.dirname(path.dirname(runtimeDataRoot));
  t.after(() => rm(projectRoot, { recursive: true, force: true }));
  t.after(() => rm(runtimeDataRoot, { recursive: true, force: true }));
  const pluginRoot = path.resolve(import.meta.dirname, "../..");
  return {
    projectRoot, runtimeDataRoot, codexHome,
    service: await createKernelService({ pluginRoot, runtimeDataRoot }),
  };
}

async function activatedFixture(t) {
  const value = await fixture(t);
  await initializeProjectState(value.projectRoot, {
    schema_version: "1.0", project_id: "project-1",
    plugin_id: "project-incubator-plugin", plugin_version: "0.1.0", status: "ACTIVE",
    project_type_id: "mod", child_skill_id: "mod-incubator", host_profile_id: "sims-4",
  }, initialState(), {
    authorization_id: "authorization-existing", request_id: "activation-existing",
    prompt_digest: "a".repeat(64),
  });
  return value;
}

test("propose_route is read-only and MCP failures use stable error codes", async (t) => {
  const { projectRoot, service } = await fixture(t);
  const proposal = await service.callTool("propose_route", {
    project_root: projectRoot, project_type_id: "mod",
  });
  assert.equal(proposal.isError, undefined);
  assert.equal(proposal.structuredContent.event, "ROUTE_PROPOSED");
  await assert.rejects(() => access(path.join(projectRoot, ".project-incubator")), /ENOENT/);

  const failure = await service.callTool("propose_route", {
    project_root: projectRoot, project_type_id: "unknown",
  });
  assert.equal(failure.isError, true);
  assert.equal(failure.structuredContent.error.code, "PROJECT_TYPE_NOT_FOUND");
});

test("initialization is denied without a verified Maker prompt", async (t) => {
  const { projectRoot, service } = await fixture(t);
  const prepared = await service.callTool("prepare_activation", {
    project_root: projectRoot, project_id: "project-1", project_type_id: "mod",
    session_id: "session-1", summary: "激活 Mod 孵化器", state: initialState(),
    product_decisions: productDecisions(),
  });
  const request = prepared.structuredContent;
  const result = await service.callTool("initialize_project", {
    project_root: projectRoot, request_id: request.request_id,
    scope_digest: request.scope_digest, session_id: "session-1", turn_id: "turn-2",
    state: initialState(),
  });
  assert.equal(result.isError, true);
  assert.equal(result.structuredContent.error.code, "PROMPT_NOT_FOUND");
  await assert.rejects(() => access(path.join(projectRoot, ".project-incubator")), /ENOENT/);
});

test("pending activation captures one scoped Maker approval and initializes atomically", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await fixture(t);
  const prepared = await service.callTool("prepare_activation", {
    project_root: projectRoot, project_id: "project-1", project_type_id: "mod",
    session_id: "session-1", summary: "激活 Mod 孵化器", state: initialState(),
    product_decisions: productDecisions(),
  });
  const request = prepared.structuredContent;
  const hook = await handleUserPromptSubmit({
    cwd: projectRoot, session_id: "session-1", turn_id: "turn-2", timestamp: approvalTime,
    prompt: `我明确批准 ${request.request_id}，scope_digest: ${request.scope_digest}`,
  }, { runtimeDataRoot, now: new Date(approvalTime) });
  assert.deepEqual(hook, { continue: true });

  const initialized = await service.callTool("initialize_project", {
    project_root: projectRoot, request_id: request.request_id,
    scope_digest: request.scope_digest, session_id: "session-1", turn_id: "turn-2",
    state: initialState(),
  }, { now: new Date(approvalTime) });
  assert.equal(initialized.isError, undefined);
  assert.equal(initialized.structuredContent.receipt.new_revision, 0);
  const state = await service.callTool("get_project_state", { project_root: projectRoot });
  assert.equal(state.structuredContent.state.project_id, "project-1");
  assert.equal(state.structuredContent.activation.project_type_id, "mod");
  assert.deepEqual(state.structuredContent.state.decisions.active.map((decision) => ({
    decision_id: decision.decision_id,
    kind: decision.kind,
    status: decision.status,
    statement: decision.statement,
  })), [{
    decision_id: "product-boundary-1",
    kind: "PRODUCT",
    status: "ACTIVE",
    statement: "仅孵化一个由 Maker 确认的 Mod 产品点。",
  }]);
  assert.match(state.structuredContent.state.decisions.active[0].authorization_ref, /^authorization-/);
  assert.equal(state.structuredContent.state.decisions.active[0].confirmed_at, approvalTime);
  assert.equal(state.structuredContent.state.last_change.operation, "INITIALIZE_PROJECT");
  assert.equal(state.structuredContent.state.plan.current_action, "确认边界");
  assert.deepEqual(await readdir(runtimeDataRoot), []);
});

test("prepare_activation rejects an activation-draft narrative as authoritative initial state", async (t) => {
  const { projectRoot, service } = await fixture(t);
  const stale = initialState();
  stale.plan.current_action = "等待 Maker 对 Activation Request 作出明确授权。";
  stale.plan.completion_conditions = ["随后调用 initialize_project 完成激活"];
  stale.last_change = {
    operation: "ACTIVATION_DRAFT",
    changed_at: approvalTime,
    summary: "形成待授权状态；尚未激活。",
  };
  const result = await service.callTool("prepare_activation", {
    project_root: projectRoot, project_id: "project-1", project_type_id: "mod",
    session_id: "session-1", summary: "激活 Mod 孵化器", state: stale,
    product_decisions: productDecisions(),
  });
  assert.equal(result.isError, true);
  assert.equal(result.structuredContent.error.code, "INITIAL_STATE_NOT_POST_ACTIVATION");
  await assert.rejects(() => access(path.join(projectRoot, ".project-incubator")), /ENOENT/);
});

test("prepare_activation rejects a project that already has complete authority state", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await fixture(t);
  await initializeProjectState(projectRoot, {
    schema_version: "1.0", project_id: "project-1",
    plugin_id: "project-incubator-plugin", plugin_version: "0.1.0", status: "ACTIVE",
    project_type_id: "mod", child_skill_id: "mod-incubator", host_profile_id: null,
  }, initialState(), {
    authorization_id: "authorization-existing", request_id: "activation-existing",
    prompt_digest: "a".repeat(64),
  });
  const result = await service.callTool("prepare_activation", {
    project_root: projectRoot, project_id: "project-1", project_type_id: "mod",
    session_id: "session-1", summary: "重复激活", state: initialState(),
    product_decisions: productDecisions(),
  });
  assert.equal(result.isError, true);
  assert.equal(result.structuredContent.error.code, "PROJECT_ALREADY_INITIALIZED");
  assert.deepEqual(await readdir(runtimeDataRoot), []);
});

test("prepare_activation fails closed when only part of the authority state exists", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await fixture(t);
  const control = path.join(projectRoot, ".project-incubator");
  await mkdir(control);
  await writeFile(path.join(control, "state.json"), "{}\n", "utf8");
  const result = await service.callTool("prepare_activation", {
    project_root: projectRoot, project_id: "project-1", project_type_id: "mod",
    session_id: "session-1", summary: "损坏状态下激活", state: initialState(),
    product_decisions: productDecisions(),
  });
  assert.equal(result.isError, true);
  assert.equal(result.structuredContent.error.code, "PROJECT_CONTROL_STATE_INCOMPLETE");
  assert.deepEqual(await readdir(runtimeDataRoot), []);
});

test("route migration cannot be committed without Maker authorization", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await fixture(t);
  const prepared = await service.callTool("prepare_activation", {
    project_root: projectRoot, project_id: "project-1", project_type_id: "mod",
    session_id: "session-1", summary: "激活 Mod 孵化器", state: initialState(),
    product_decisions: productDecisions(),
  });
  const request = prepared.structuredContent;
  await handleUserPromptSubmit({
    cwd: projectRoot, session_id: "session-1", turn_id: "turn-2", timestamp: approvalTime,
    prompt: `我明确批准 ${request.request_id}，scope_digest: ${request.scope_digest}`,
  }, { runtimeDataRoot, now: new Date(approvalTime) });
  await service.callTool("initialize_project", {
    project_root: projectRoot, request_id: request.request_id, scope_digest: request.scope_digest,
    session_id: "session-1", turn_id: "turn-2", state: initialState(),
  }, { now: new Date(approvalTime) });

  const snapshot = await service.callTool("get_project_state", { project_root: projectRoot });
  const proposedState = structuredClone(snapshot.structuredContent.state);
  proposedState.last_change = { operation: "MIGRATE_ROUTE", changed_at: approvalTime, summary: "迁移路由" };
  const pending = await service.callTool("prepare_change", {
    project_root: projectRoot, operation: "MIGRATE_ROUTE", change_kind: "PRODUCT_DECISION",
    session_id: "session-1", proposed_state: proposedState,
  });
  const denied = await service.callTool("commit_change", {
    project_root: projectRoot, request_id: pending.structuredContent.request_id,
    scope_digest: pending.structuredContent.scope_digest,
    session_id: "session-1", turn_id: "turn-3",
  });
  assert.equal(denied.isError, true);
  assert.equal(denied.structuredContent.error.code, "PROMPT_NOT_FOUND");
});

test("prepare_change rejects an illegal Mod stage skip before creating a pending request", async (t) => {
  const { projectRoot, service } = await activatedFixture(t);
  const before = await service.callTool("get_project_state", { project_root: projectRoot });
  const proposedState = structuredClone(before.structuredContent.state);
  proposedState.workflow.stage = "M4_TARGET_VALIDATION";

  const result = await service.callTool("prepare_change", {
    project_root: projectRoot, operation: "ADVANCE_MOD_STAGE", change_kind: "WORKFLOW_TRANSITION",
    session_id: "session-1", proposed_state: proposedState,
    workflow_transition: { target_stage: "M4_TARGET_VALIDATION", completion_satisfied: true },
  });

  assert.equal(result.isError, true);
  assert.equal(result.structuredContent.error.code, "ILLEGAL_TRANSITION");
  const after = await service.callTool("get_project_state", { project_root: projectRoot });
  assert.equal(after.structuredContent.state.revision, before.structuredContent.state.revision);
  assert.deepEqual(after.structuredContent.state.pending_requests, []);
});

test("prepare_change requires a transition contract whenever the Mod stage changes", async (t) => {
  const { projectRoot, service } = await activatedFixture(t);
  const snapshot = await service.callTool("get_project_state", { project_root: projectRoot });
  const proposedState = structuredClone(snapshot.structuredContent.state);
  proposedState.workflow.stage = "M1_RISK_MODEL";

  const result = await service.callTool("prepare_change", {
    project_root: projectRoot, operation: "ADVANCE_MOD_STAGE", change_kind: "WORKFLOW_TRANSITION",
    session_id: "session-1", proposed_state: proposedState,
  });

  assert.equal(result.isError, true);
  assert.equal(result.structuredContent.error.code, "WORKFLOW_TRANSITION_REQUIRED");
});

test("a legal Mod transition is bound into the pending request", async (t) => {
  const { projectRoot, service } = await activatedFixture(t);
  const snapshot = await service.callTool("get_project_state", { project_root: projectRoot });
  const proposedState = structuredClone(snapshot.structuredContent.state);
  proposedState.workflow.stage = "M1_RISK_MODEL";
  proposedState.workflow.allowed_next = ["M2_VERTICAL_SLICE"];

  const result = await service.callTool("prepare_change", {
    project_root: projectRoot, operation: "ADVANCE_MOD_STAGE", change_kind: "WORKFLOW_TRANSITION",
    session_id: "session-1", proposed_state: proposedState,
    workflow_transition: { target_stage: "M1_RISK_MODEL", completion_satisfied: true },
  });

  assert.equal(result.isError, undefined);
  const after = await service.callTool("get_project_state", { project_root: projectRoot });
  assert.deepEqual(after.structuredContent.state.pending_requests[0].payload.workflow_transition, {
    target_stage: "M1_RISK_MODEL", completion_satisfied: true,
  });
});

test("a legal M0 to M1 transition commits only after scoped Maker authorization", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await activatedFixture(t);
  const snapshot = await service.callTool("get_project_state", { project_root: projectRoot });
  const proposedState = structuredClone(snapshot.structuredContent.state);
  proposedState.workflow.stage = "M1_RISK_MODEL";
  proposedState.workflow.allowed_next = ["M2_VERTICAL_SLICE"];
  proposedState.plan.current_action = "评估 Capability 风险";

  const prepared = await service.callTool("prepare_change", {
    project_root: projectRoot, operation: "ADVANCE_MOD_STAGE", change_kind: "WORKFLOW_TRANSITION",
    session_id: "session-1", proposed_state: proposedState,
    workflow_transition: { target_stage: "M1_RISK_MODEL", completion_satisfied: true },
  }, { now: new Date(approvalTime) });
  const request = prepared.structuredContent;
  await handleUserPromptSubmit({
    cwd: projectRoot, session_id: "session-1", turn_id: "turn-transition", timestamp: approvalTime,
    prompt: `我明确批准 ${request.request_id}，scope_digest: ${request.scope_digest}`,
  }, { runtimeDataRoot, now: new Date(approvalTime) });

  const committed = await service.callTool("commit_change", {
    project_root: projectRoot, request_id: request.request_id, scope_digest: request.scope_digest,
    session_id: "session-1", turn_id: "turn-transition",
  }, { now: new Date(approvalTime) });

  assert.equal(committed.isError, undefined);
  assert.match(committed.structuredContent.receipt.authorization_ref.authorization_id, /^authorization-/);
  const after = await service.callTool("get_project_state", { project_root: projectRoot });
  assert.equal(after.structuredContent.state.workflow.stage, "M1_RISK_MODEL");
  assert.deepEqual(after.structuredContent.state.workflow.allowed_next, ["M2_VERTICAL_SLICE"]);
  assert.deepEqual(after.structuredContent.state.pending_requests, []);
});

test("prepare_change enforces the Mod MODEL_REVIEW entry contract", async (t) => {
  const { projectRoot, service } = await activatedFixture(t);
  const snapshot = await service.callTool("get_project_state", { project_root: projectRoot });
  const proposedState = structuredClone(snapshot.structuredContent.state);
  proposedState.workflow = {
    ...proposedState.workflow,
    stage: "MODEL_REVIEW", return_stage: "M0_BOUNDARY", allowed_next: ["M0_BOUNDARY"],
  };

  const result = await service.callTool("prepare_change", {
    project_root: projectRoot, operation: "ENTER_MODEL_REVIEW", change_kind: "WORKFLOW_TRANSITION",
    session_id: "session-1", proposed_state: proposedState,
    workflow_transition: {
      target_stage: "MODEL_REVIEW", completion_satisfied: false, model_invalidated: true,
    },
  });

  assert.equal(result.isError, true);
  assert.equal(result.structuredContent.error.code, "MODEL_REVIEW_NOT_AVAILABLE");
});
