import assert from "node:assert/strict";
import { access, mkdir, mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { handleUserPromptSubmit } from "../../hooks/user-prompt-submit.mjs";
import { createKernelService } from "../../src/server.mjs";
import { initializeProjectState, readProjectSnapshot, verifyLatestReceipt } from "../../src/kernel/state-store.mjs";

const now = new Date("2026-10-23T05:00:00.000Z");
const authorizationRef = {
  authorization_id: "authorization-old", request_id: "request-old", prompt_digest: "a".repeat(64),
};

function activation() {
  return {
    schema_version: "1.0", project_id: "recovery-project",
    plugin_id: "project-incubator-plugin", plugin_version: "0.3.0", status: "ACTIVE",
    project_type_id: "mod", child_skill_id: "mod-incubator", host_profile_id: "sims-4",
  };
}

function state(revision = 0, pendingRequests = []) {
  return {
    schema_version: "1.0", project_id: "recovery-project", revision,
    boundary: { objective: "恢复 Managed Project", supported: ["权威恢复"], excluded: [] },
    workflow: { stage: "M0_BOUNDARY", status: "ACTIVE", completed: [], allowed_next: ["M1_RISK_MODEL"] },
    capabilities: [], decisions: { active: [], archive_ref: null }, assumptions: [],
    plan: { current_action: "恢复权威", next_action: "继续孵化", completion_conditions: ["Receipt 验证"] },
    gates: [], risks: [], pending_requests: pendingRequests, baselines: [],
    human_validation: { limit: "UNSET", consumed: 0 },
    last_change: { operation: "RECOVERY_DRAFT", changed_at: now.toISOString(), summary: "恢复候选" },
    archive_refs: [],
  };
}

async function fixture(t) {
  const projectRoot = await mkdtemp(path.join(os.tmpdir(), "incubator-recovery-mcp-project-"));
  const runtimeDataRoot = await mkdtemp(path.join(os.tmpdir(), "incubator-recovery-mcp-runtime-"));
  t.after(() => rm(projectRoot, { recursive: true, force: true }));
  t.after(() => rm(runtimeDataRoot, { recursive: true, force: true }));
  const pluginRoot = path.resolve(import.meta.dirname, "../..");
  return {
    projectRoot,
    runtimeDataRoot,
    service: await createKernelService({ pluginRoot, runtimeDataRoot }),
  };
}

async function authorityBytes(root) {
  return Promise.all(["activation.json", "state.json", "latest-receipt.json"].map(async (name) => {
    try {
      return await readFile(path.join(root, ".project-incubator", name));
    } catch (error) {
      if (error?.code === "ENOENT") return null;
      throw error;
    }
  }));
}

async function prepare(service, projectRoot, proposedState, summary = "根据现有 Artifact 恢复权威") {
  return service.callTool("prepare_authority_recovery", {
    project_root: projectRoot,
    session_id: "session-recovery",
    summary,
    proposed_activation: activation(),
    proposed_state: proposedState,
  }, { now });
}

async function approve(projectRoot, runtimeDataRoot, request) {
  await handleUserPromptSubmit({
    cwd: projectRoot,
    session_id: "session-recovery",
    turn_id: "turn-recovery",
    timestamp: now.toISOString(),
    prompt: `我明确批准恢复请求 request_id=${request.request_id}，scope_digest=${request.scope_digest}`,
  }, { runtimeDataRoot, now });
}

test("recovery preparation diagnoses missing files without writing the project", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await fixture(t);
  const before = await authorityBytes(projectRoot);
  const prepared = await prepare(service, projectRoot, state(0));

  assert.equal(prepared.isError, undefined);
  assert.equal(prepared.structuredContent.event, "AUTHORITY_RECOVERY_PREPARED");
  assert.match(prepared.structuredContent.request_id, /^recovery-/);
  assert.equal(prepared.structuredContent.proposed_revision, 0);
  assert.deepEqual(
    prepared.structuredContent.authority_diagnostics.map((entry) => entry.status),
    ["MISSING", "MISSING", "MISSING"],
  );
  assert.deepEqual(await authorityBytes(projectRoot), before);
  assert.equal((await readdir(runtimeDataRoot)).length, 1);
});

test("a complete verified project rejects recovery and creates no request", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await fixture(t);
  await initializeProjectState(projectRoot, activation(), state(0), authorizationRef);
  const result = await prepare(service, projectRoot, state(1));
  assert.equal(result.isError, true);
  assert.equal(result.structuredContent.error.code, "AUTHORITY_RECOVERY_NOT_REQUIRED");
  assert.deepEqual(await readdir(runtimeDataRoot), []);
});

test("recovery accepts an advanced State 1.1 while validating its original entry", async (t) => {
  const { projectRoot, service } = await fixture(t);
  const advanced = state(0);
  advanced.schema_version = "1.1";
  advanced.workflow = {
    stage: "M3_BUILD_PACKAGE",
    status: "ACTIVE",
    completed: ["M0_BOUNDARY", "M1_RISK_MODEL", "M2_VERTICAL_SLICE"],
    allowed_next: ["M4_TARGET_VALIDATION", "MODEL_REVIEW"],
    return_stage: null,
    entry: {
      mode: "NEW_PROJECT",
      initial_stage: "M0_BOUNDARY",
      assessment_summary: "项目最初从 M0 创建，当前证据支持恢复到 M3。",
      evidence_refs: [],
      assessed_at: now.toISOString(),
    },
  };
  const prepared = await prepare(service, projectRoot, advanced);
  assert.equal(prepared.isError, undefined);
  assert.equal(prepared.structuredContent.proposed_revision, 0);
});

test("reestablished recovery requires exact Maker approval and closes revision zero", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await fixture(t);
  const prepared = (await prepare(service, projectRoot, state(0))).structuredContent;
  const before = await authorityBytes(projectRoot);
  let recovered = await service.callTool("recover_project_authority", {
    project_root: projectRoot,
    request_id: prepared.request_id,
    scope_digest: prepared.scope_digest,
    session_id: "session-recovery",
    turn_id: "turn-recovery",
  }, { now });
  assert.equal(recovered.isError, true);
  assert.equal(recovered.structuredContent.error.code, "PROMPT_NOT_FOUND");
  assert.deepEqual(await authorityBytes(projectRoot), before);

  await approve(projectRoot, runtimeDataRoot, prepared);
  recovered = await service.callTool("recover_project_authority", {
    project_root: projectRoot,
    request_id: prepared.request_id,
    scope_digest: prepared.scope_digest,
    session_id: "session-recovery",
    turn_id: "turn-recovery",
  }, { now });
  assert.equal(recovered.isError, undefined);
  assert.equal(recovered.structuredContent.recovery.baseline, "REESTABLISHED");
  assert.equal(recovered.structuredContent.receipt.new_revision, 0);
  assert.equal((await verifyLatestReceipt(projectRoot, recovered.structuredContent.receipt.receipt_id)).verified, true);
});

test("continued recovery advances revision and never inherits old pending requests", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await fixture(t);
  const oldPending = [{
    request_id: "request-abandoned", operation: "OLD_CHANGE", scope_digest: "b".repeat(64),
    status: "PENDING", created_at: now.toISOString(), project_revision: 0,
  }];
  await initializeProjectState(projectRoot, activation(), state(0, oldPending), authorizationRef);
  const receiptPath = path.join(projectRoot, ".project-incubator", "latest-receipt.json");
  const receipt = JSON.parse(await readFile(receiptPath, "utf8"));
  receipt.new_state_hash = "0".repeat(64);
  await writeFile(receiptPath, JSON.stringify(receipt));

  const prepared = (await prepare(service, projectRoot, state(1))).structuredContent;
  assert.equal(prepared.proposed_revision, 1);
  await approve(projectRoot, runtimeDataRoot, prepared);
  const recovered = await service.callTool("recover_project_authority", {
    project_root: projectRoot,
    request_id: prepared.request_id,
    scope_digest: prepared.scope_digest,
    session_id: "session-recovery",
    turn_id: "turn-recovery",
  }, { now });

  assert.equal(recovered.isError, undefined);
  assert.equal(recovered.structuredContent.recovery.baseline, "CONTINUED");
  const snapshot = await readProjectSnapshot(projectRoot);
  assert.equal(snapshot.state.revision, 1);
  assert.deepEqual(snapshot.state.pending_requests, []);
  assert.equal(snapshot.state.last_change.operation, "RECOVER_PROJECT_AUTHORITY");
});

test("recovery rejects source changes made after preparation without overwriting them", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await fixture(t);
  const prepared = (await prepare(service, projectRoot, state(0))).structuredContent;
  const control = path.join(projectRoot, ".project-incubator");
  await mkdir(control);
  await writeFile(path.join(control, "activation.json"), "{}\n");
  await approve(projectRoot, runtimeDataRoot, prepared);
  const before = await authorityBytes(projectRoot);

  const recovered = await service.callTool("recover_project_authority", {
    project_root: projectRoot,
    request_id: prepared.request_id,
    scope_digest: prepared.scope_digest,
    session_id: "session-recovery",
    turn_id: "turn-recovery",
  }, { now });
  assert.equal(recovered.isError, true);
  assert.equal(recovered.structuredContent.error.code, "RECOVERY_SOURCE_CHANGED");
  assert.deepEqual(await authorityBytes(projectRoot), before);
});
