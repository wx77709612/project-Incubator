import assert from "node:assert/strict";
import { access, mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { handleUserPromptSubmit } from "../../hooks/user-prompt-submit.mjs";
import { createKernelService } from "../../src/server.mjs";
import { initializeProjectState } from "../../src/kernel/state-store.mjs";

const nowText = "2026-10-05T08:00:00.000Z";
const nextByStage = {
  P0: ["P1"], P1: ["P2"], P2: ["P3"], P3: ["P4"], P4: ["P5"], P5: ["P6"],
  P6: ["P2", "P3", "P4", "P5"],
};

function desktopState(stage = "P0", mode = "NEW_PROJECT", evidenceRefs = []) {
  return {
    schema_version: "1.1", project_id: "desktop-project", revision: 0,
    boundary: { objective: "孵化一个桌面产品", supported: ["桌面交付"], excluded: ["浏览器扩展"] },
    workflow: {
      stage, status: "ACTIVE", completed: [], allowed_next: nextByStage[stage],
      entry: {
        mode, initial_stage: stage, assessment_summary: "已根据现有项目证据判断当前阶段。",
        evidence_refs: evidenceRefs, assessed_at: nowText,
      },
    },
    capabilities: [], decisions: { active: [], archive_ref: null }, assumptions: [],
    plan: { current_action: "推进当前阶段", next_action: "验证阶段出口", completion_conditions: ["阶段证据成立"] },
    gates: [], risks: [], pending_requests: [], baselines: [],
    human_validation: { limit: "UNSET", consumed: 0 },
    last_change: { operation: "INITIALIZE_PROJECT", changed_at: nowText, summary: "桌面项目已激活" },
    archive_refs: [],
  };
}

function productDecisions() {
  return [{ decision_id: "desktop-boundary", statement: "本项目交付主体为桌面产品。" }];
}

async function fixture(t) {
  const projectRoot = await mkdtemp(path.join(os.tmpdir(), "desktop-router-project-"));
  const runtimeDataRoot = await mkdtemp(path.join(os.tmpdir(), "desktop-router-runtime-"));
  t.after(() => rm(projectRoot, { recursive: true, force: true }));
  t.after(() => rm(runtimeDataRoot, { recursive: true, force: true }));
  const pluginRoot = path.resolve(import.meta.dirname, "../..");
  return {
    projectRoot, runtimeDataRoot,
    service: await createKernelService({ pluginRoot, runtimeDataRoot }),
  };
}

async function activatedFixture(t, state = desktopState("P4", "ADOPT_EXISTING", ["evidence://existing-design"])) {
  const value = await fixture(t);
  await initializeProjectState(value.projectRoot, {
    schema_version: "1.0", project_id: "desktop-project", plugin_id: "project-incubator-plugin",
    plugin_version: "0.2.0", status: "ACTIVE", project_type_id: "desktop-product",
    child_skill_id: "desktop-product-incubator", host_profile_id: "windows-desktop",
  }, state, {
    authorization_id: "authorization-existing", request_id: "activation-existing",
    prompt_digest: "a".repeat(64),
  });
  return value;
}

async function prepareDesktop(service, projectRoot, state, overrides = {}) {
  return service.callTool("prepare_activation", {
    project_root: projectRoot, project_id: "desktop-project", project_type_id: "desktop-product",
    host_profile_id: "windows-desktop", session_id: "desktop-session", summary: "激活桌面产品孵化器",
    state, product_decisions: productDecisions(), ...overrides,
  }, { now: new Date(nowText) });
}

async function approve(runtimeDataRoot, projectRoot, request, turnId) {
  await handleUserPromptSubmit({
    cwd: projectRoot, session_id: "desktop-session", turn_id: turnId, timestamp: nowText,
    prompt: `我明确批准 ${request.request_id}，scope_digest: ${request.scope_digest}`,
  }, { runtimeDataRoot, now: new Date(nowText) });
}

test("desktop routing requires an explicit matching host and never selects a default", async (t) => {
  const { projectRoot, service } = await fixture(t);
  const missing = await service.callTool("propose_route", {
    project_root: projectRoot, project_type_id: "desktop-product",
  });
  assert.equal(missing.structuredContent.error.code, "HOST_PROFILE_REQUIRED");

  const wrong = await service.callTool("propose_route", {
    project_root: projectRoot, project_type_id: "desktop-product", host_profile_id: "sims-4",
  });
  assert.equal(wrong.structuredContent.error.code, "HOST_PROFILE_PROJECT_TYPE_MISMATCH");

  const valid = await service.callTool("propose_route", {
    project_root: projectRoot, project_type_id: "desktop-product", host_profile_id: "windows-desktop",
  });
  assert.equal(valid.structuredContent.route.host_profile_id, "windows-desktop");
});

test("desktop activation validates NEW_PROJECT and ADOPT_EXISTING entry contracts", async (t) => {
  const fresh = await fixture(t);
  const validNew = await prepareDesktop(fresh.service, fresh.projectRoot, desktopState());
  assert.equal(validNew.isError, undefined);

  const invalidNewState = desktopState("P3");
  const invalidNew = await prepareDesktop(fresh.service, fresh.projectRoot, invalidNewState);
  assert.equal(invalidNew.structuredContent.error.code, "WORKFLOW_ENTRY_STAGE_INVALID");

  const adopted = await fixture(t);
  const validAdopt = await prepareDesktop(
    adopted.service, adopted.projectRoot, desktopState("P3", "ADOPT_EXISTING", ["evidence://architecture"]),
  );
  assert.equal(validAdopt.isError, undefined);

  const noEvidence = await fixture(t);
  const invalidAdopt = await prepareDesktop(
    noEvidence.service, noEvidence.projectRoot, desktopState("P3", "ADOPT_EXISTING", []),
  );
  assert.equal(invalidAdopt.structuredContent.error.code, "WORKFLOW_ENTRY_EVIDENCE_REQUIRED");
});

test("desktop activation returns the workflow mode error for an invalid entry mode", async (t) => {
  const { projectRoot, service } = await fixture(t);
  const result = await prepareDesktop(
    service, projectRoot, desktopState("P2", "UNKNOWN", ["evidence://existing-design"]),
  );
  assert.equal(result.structuredContent.error.code, "WORKFLOW_ENTRY_MODE_INVALID");
});

test("desktop activation returns the entry-required error when entry is null", async (t) => {
  const { projectRoot, service } = await fixture(t);
  const state = desktopState();
  state.workflow.entry = null;
  const result = await prepareDesktop(service, projectRoot, state);
  assert.equal(result.structuredContent.error.code, "WORKFLOW_ENTRY_REQUIRED");
});

test("ADOPT_EXISTING P3 with evidence initializes from P3 after Maker authorization", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await fixture(t);
  const initialState = desktopState("P3", "ADOPT_EXISTING", ["evidence://existing-architecture"]);
  const prepared = await prepareDesktop(service, projectRoot, initialState);
  const request = prepared.structuredContent;
  await approve(runtimeDataRoot, projectRoot, request, "adopt-p3");

  const initialized = await service.callTool("initialize_project", {
    project_root: projectRoot, request_id: request.request_id, scope_digest: request.scope_digest,
    session_id: "desktop-session", turn_id: "adopt-p3",
  }, { now: new Date(nowText) });
  assert.equal(initialized.isError, undefined);
  assert.equal(initialized.structuredContent.activation.project_type_id, "desktop-product");
  assert.equal(initialized.structuredContent.activation.host_profile_id, "windows-desktop");
  assert.equal(initialized.structuredContent.receipt.new_revision, 0);

  const snapshot = await service.callTool("get_project_state", { project_root: projectRoot });
  assert.equal(snapshot.structuredContent.state.workflow.stage, "P3");
  assert.deepEqual(snapshot.structuredContent.state.workflow.allowed_next, ["P4"]);
  assert.deepEqual(snapshot.structuredContent.state.workflow.entry, initialState.workflow.entry);
  assert.deepEqual(await readdir(runtimeDataRoot), []);
});

test("initialize revalidates a drifted route and leaves no authority files", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await fixture(t);
  const prepared = await prepareDesktop(service, projectRoot, desktopState());
  const request = prepared.structuredContent;
  const [pendingName] = (await readdir(runtimeDataRoot)).filter((name) => name.startsWith("activation-"));
  const pendingPath = path.join(runtimeDataRoot, pendingName);
  const pending = JSON.parse(await readFile(pendingPath, "utf8"));
  pending.route.child_skill_id = "mod-incubator";
  await writeFile(pendingPath, `${JSON.stringify(pending)}\n`, "utf8");
  await approve(runtimeDataRoot, projectRoot, request, "route-drift");

  const result = await service.callTool("initialize_project", {
    project_root: projectRoot, request_id: request.request_id, scope_digest: request.scope_digest,
    session_id: "desktop-session", turn_id: "route-drift",
  }, { now: new Date(nowText) });
  assert.equal(result.structuredContent.error.code, "ACTIVATION_ROUTE_MISMATCH");
  await assert.rejects(() => access(path.join(projectRoot, ".project-incubator")), /ENOENT/);
});

test("initialize revalidates a drifted entry and leaves no authority files", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await fixture(t);
  const prepared = await prepareDesktop(service, projectRoot, desktopState());
  const request = prepared.structuredContent;
  const [pendingName] = (await readdir(runtimeDataRoot)).filter((name) => name.startsWith("activation-"));
  const pendingPath = path.join(runtimeDataRoot, pendingName);
  const pending = JSON.parse(await readFile(pendingPath, "utf8"));
  pending.initial_state.workflow.entry.initial_stage = "P3";
  await writeFile(pendingPath, `${JSON.stringify(pending)}\n`, "utf8");
  await approve(runtimeDataRoot, projectRoot, request, "entry-drift");

  const result = await service.callTool("initialize_project", {
    project_root: projectRoot, request_id: request.request_id, scope_digest: request.scope_digest,
    session_id: "desktop-session", turn_id: "entry-drift",
  }, { now: new Date(nowText) });
  assert.equal(result.structuredContent.error.code, "WORKFLOW_ENTRY_STATE_MISMATCH");
  await assert.rejects(() => access(path.join(projectRoot, ".project-incubator")), /ENOENT/);
});

test("initialize rejects a structurally valid activation scope drift", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await fixture(t);
  const prepared = await prepareDesktop(service, projectRoot, desktopState());
  const request = prepared.structuredContent;
  const [pendingName] = (await readdir(runtimeDataRoot)).filter((name) => name.startsWith("activation-"));
  const pendingPath = path.join(runtimeDataRoot, pendingName);
  const pending = JSON.parse(await readFile(pendingPath, "utf8"));
  pending.initial_state.workflow = {
    ...pending.initial_state.workflow,
    stage: "P3",
    allowed_next: ["P4"],
    entry: {
      ...pending.initial_state.workflow.entry,
      mode: "ADOPT_EXISTING",
      initial_stage: "P3",
      assessment_summary: "已根据现有架构和计划证据判断当前处于执行规划阶段。",
      evidence_refs: ["evidence://existing-architecture"],
    },
  };
  await writeFile(pendingPath, `${JSON.stringify(pending)}\n`, "utf8");
  await approve(runtimeDataRoot, projectRoot, request, "valid-scope-drift");

  const result = await service.callTool("initialize_project", {
    project_root: projectRoot, request_id: request.request_id, scope_digest: request.scope_digest,
    session_id: "desktop-session", turn_id: "valid-scope-drift",
  }, { now: new Date(nowText) });
  assert.equal(result.structuredContent.error.code, "SCOPE_DIGEST_MISMATCH");
  await assert.rejects(() => access(path.join(projectRoot, ".project-incubator")), /ENOENT/);
});

test("State 1.1 workflow entry is immutable during prepare_change", async (t) => {
  const { projectRoot, service } = await activatedFixture(t);
  const snapshot = await service.callTool("get_project_state", { project_root: projectRoot });
  const proposed = structuredClone(snapshot.structuredContent.state);
  proposed.workflow.entry.assessment_summary = "试图改写激活时判断";
  const result = await service.callTool("prepare_change", {
    project_root: projectRoot, operation: "ALTER_ENTRY", change_kind: "PRODUCT_DECISION",
    session_id: "desktop-session", proposed_state: proposed,
  });
  assert.equal(result.structuredContent.error.code, "WORKFLOW_ENTRY_IMMUTABLE");
});

test("State 1.1 cannot be downgraded to remove entry during prepare_change", async (t) => {
  const { projectRoot, service } = await activatedFixture(t);
  const snapshot = await service.callTool("get_project_state", { project_root: projectRoot });
  const proposed = structuredClone(snapshot.structuredContent.state);
  proposed.schema_version = "1.0";
  delete proposed.workflow.entry;
  const result = await service.callTool("prepare_change", {
    project_root: projectRoot, operation: "REMOVE_ENTRY", change_kind: "PRODUCT_DECISION",
    session_id: "desktop-session", proposed_state: proposed,
  });
  assert.equal(result.structuredContent.error.code, "WORKFLOW_ENTRY_IMMUTABLE");
});

test("State 1.1 workflow entry is rechecked during commit_change", async (t) => {
  const current = desktopState("P4", "ADOPT_EXISTING", ["evidence://existing-design"]);
  const proposed = structuredClone(current);
  proposed.workflow.entry.assessment_summary = "提交阶段漂移";
  const requestId = "request-entry-drift";
  const scopeDigest = "b".repeat(64);
  current.pending_requests = [{
    request_id: requestId, operation: "ALTER_ENTRY", scope_digest: scopeDigest, status: "PENDING",
    created_at: nowText, project_revision: 0,
    payload: {
      change_kind: "PRODUCT_DECISION", proposed_state: proposed, session_id: "desktop-session",
      requires_authorization: true,
    },
  }];
  const { projectRoot, runtimeDataRoot, service } = await activatedFixture(t, current);
  await approve(runtimeDataRoot, projectRoot, { request_id: requestId, scope_digest: scopeDigest }, "commit-drift");
  const result = await service.callTool("commit_change", {
    project_root: projectRoot, request_id: requestId, scope_digest: scopeDigest,
    session_id: "desktop-session", turn_id: "commit-drift",
  }, { now: new Date(nowText) });
  assert.equal(result.structuredContent.error.code, "WORKFLOW_ENTRY_IMMUTABLE");
  const after = await service.callTool("get_project_state", { project_root: projectRoot });
  assert.equal(after.structuredContent.state.workflow.entry.assessment_summary, current.workflow.entry.assessment_summary);
});

test("State 1.1 cannot be downgraded to remove entry during commit_change", async (t) => {
  const current = desktopState("P4", "ADOPT_EXISTING", ["evidence://existing-design"]);
  const proposed = structuredClone(current);
  proposed.schema_version = "1.0";
  delete proposed.workflow.entry;
  const requestId = "request-remove-entry";
  const scopeDigest = "c".repeat(64);
  current.pending_requests = [{
    request_id: requestId, operation: "REMOVE_ENTRY", scope_digest: scopeDigest, status: "PENDING",
    created_at: nowText, project_revision: 0,
    payload: {
      change_kind: "PRODUCT_DECISION", proposed_state: proposed, session_id: "desktop-session",
      requires_authorization: true,
    },
  }];
  const { projectRoot, runtimeDataRoot, service } = await activatedFixture(t, current);
  await approve(runtimeDataRoot, projectRoot, { request_id: requestId, scope_digest: scopeDigest }, "remove-entry");
  const result = await service.callTool("commit_change", {
    project_root: projectRoot, request_id: requestId, scope_digest: scopeDigest,
    session_id: "desktop-session", turn_id: "remove-entry",
  }, { now: new Date(nowText) });
  assert.equal(result.structuredContent.error.code, "WORKFLOW_ENTRY_IMMUTABLE");
  const after = await service.callTool("get_project_state", { project_root: projectRoot });
  assert.equal(after.structuredContent.state.schema_version, "1.1");
  assert.equal(after.structuredContent.state.workflow.entry.initial_stage, "P4");
});

test("P4 Creation Correction remains a same-stage authorized mutation", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await activatedFixture(t);
  const snapshot = await service.callTool("get_project_state", { project_root: projectRoot });
  const proposed = structuredClone(snapshot.structuredContent.state);
  proposed.plan.current_action = "根据反例修正 Desktop System Model";
  const prepared = await service.callTool("prepare_change", {
    project_root: projectRoot, operation: "P4_CREATION_CORRECTION", change_kind: "PRODUCT_DECISION",
    session_id: "desktop-session", proposed_state: proposed,
  }, { now: new Date(nowText) });
  assert.equal(prepared.isError, undefined);
  assert.equal(prepared.structuredContent.workflow_transition, undefined);
  await approve(runtimeDataRoot, projectRoot, prepared.structuredContent, "p4-correction");
  const committed = await service.callTool("commit_change", {
    project_root: projectRoot, request_id: prepared.structuredContent.request_id,
    scope_digest: prepared.structuredContent.scope_digest,
    session_id: "desktop-session", turn_id: "p4-correction",
  }, { now: new Date(nowText) });
  assert.equal(committed.isError, undefined);
  const after = await service.callTool("get_project_state", { project_root: projectRoot });
  assert.equal(after.structuredContent.state.workflow.stage, "P4");
  assert.equal(after.structuredContent.state.plan.current_action, "根据反例修正 Desktop System Model");
});
