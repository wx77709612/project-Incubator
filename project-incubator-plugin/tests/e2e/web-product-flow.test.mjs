import assert from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { handleUserPromptSubmit } from "../../hooks/user-prompt-submit.mjs";
import { parseProjectState } from "../../src/kernel/schemas.mjs";
import { createKernelService } from "../../src/server.mjs";

const nowText = "2026-10-14T08:00:00.000Z";
const nextByStage = { P0: ["P1"], P1: ["P2"], P2: ["P3"], P3: ["P4"], P4: ["P5"], P5: ["P6"], P6: ["P2", "P3", "P4", "P5"] };

function initialState(stage = "P0", gates = []) {
  return {
    schema_version: "1.1", project_id: "web-e2e", revision: 0,
    boundary: { objective: "验证浏览器与后端的核心旅程", supported: ["本地 Web 产品"], excluded: ["公开部署"] },
    workflow: {
      stage, status: "ACTIVE", completed: [], allowed_next: nextByStage[stage], return_stage: null,
      entry: {
        mode: stage === "P0" ? "NEW_PROJECT" : "ADOPT_EXISTING", initial_stage: stage,
        assessment_summary: "根据已有实现及有界 Evidence 确认当前阶段。",
        evidence_refs: stage === "P0" ? [] : ["evidence://existing-web-project"], assessed_at: nowText,
      },
    },
    capabilities: [], decisions: { active: [], archive_ref: null }, assumptions: [],
    plan: { current_action: "执行当前阶段工作包", next_action: "评估阶段完成条件", completion_conditions: ["逐项评估必要 Requirement"] },
    gates, risks: [], pending_requests: [], baselines: [],
    human_validation: { limit: "UNSET", consumed: 0 },
    last_change: { operation: "INITIALIZE_PROJECT", changed_at: nowText, summary: "初始化 Web 项目" },
    archive_refs: [],
  };
}

async function fixture(t) {
  const root = await mkdtemp(path.join(os.tmpdir(), "web-e2e-project-"));
  const runtime = await mkdtemp(path.join(os.tmpdir(), "web-e2e-runtime-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  t.after(() => rm(runtime, { recursive: true, force: true }));
  const service = await createKernelService({ pluginRoot: path.resolve(import.meta.dirname, "../.."), runtimeDataRoot: runtime });
  return { root, runtime, service };
}

function assertError(result, code) {
  assert.equal(result.isError, true);
  assert.equal(result.structuredContent.error.code, code);
}

async function snapshot(value) {
  const result = await value.service.callTool("get_project_state", { project_root: value.root });
  assert.equal(result.isError, undefined);
  return result.structuredContent;
}

async function approve(value, request, turnId) {
  await handleUserPromptSubmit({
    cwd: value.root, session_id: "web-e2e-session", turn_id: turnId, timestamp: nowText,
    prompt: `我明确批准 ${request.request_id}，scope_digest: ${request.scope_digest}`,
  }, { runtimeDataRoot: value.runtime, now: new Date(nowText) });
}

async function activate(value, state = initialState()) {
  const prepared = await value.service.callTool("prepare_activation", {
    project_root: value.root, project_id: "web-e2e", project_type_id: "web-product", host_profile_id: null,
    session_id: "web-e2e-session", summary: "批准本地 Web 产品边界与完整 Entry", state,
    product_decisions: [{ decision_id: "web-boundary", statement: "以浏览器为主要界面，验证后端结果，部署保持挂起。" }],
  }, { now: new Date(nowText) });
  assert.equal(prepared.isError, undefined);
  await approve(value, prepared.structuredContent, "activate");
  const initialized = await value.service.callTool("initialize_project", {
    project_root: value.root, request_id: prepared.structuredContent.request_id,
    scope_digest: prepared.structuredContent.scope_digest, session_id: "web-e2e-session", turn_id: "activate",
  }, { now: new Date(nowText) });
  assert.equal(initialized.isError, undefined);
  return initialized.structuredContent;
}

async function prepareTransition(value, target, completion, gates) {
  const proposed = structuredClone((await snapshot(value)).state);
  proposed.workflow.stage = target;
  proposed.workflow.allowed_next = nextByStage[target] ?? [];
  if (gates) proposed.gates = gates;
  return value.service.callTool("prepare_change", {
    project_root: value.root, operation: "ADVANCE_WEB_STAGE", change_kind: "WORKFLOW_TRANSITION",
    session_id: "web-e2e-session", proposed_state: proposed,
    workflow_transition: { target_stage: target, completion_satisfied: completion },
  }, { now: new Date(nowText) });
}

async function commit(value, request, turnId) {
  return value.service.callTool("commit_change", {
    project_root: value.root, request_id: request.request_id, scope_digest: request.scope_digest,
    session_id: "web-e2e-session", turn_id: turnId,
  }, { now: new Date(nowText) });
}

async function verify(value, receipt) {
  const result = await value.service.callTool("verify_receipt", { project_root: value.root, receipt_id: receipt.receipt_id });
  assert.equal(result.structuredContent.verified, true);
}

test("Web Route → Maker 授权激活 → Receipt → P0-P1 → Read-back 完整闭合", async (t) => {
  const value = await fixture(t);
  const route = await value.service.callTool("propose_route", { project_root: value.root, project_type_id: "web-product", host_profile_id: null });
  assert.equal(route.isError, undefined);
  assert.deepEqual(route.structuredContent.route, { project_type_id: "web-product", child_skill_id: "web-product-incubator", host_profile_id: null });
  const initialized = await activate(value);
  await verify(value, initialized.receipt);
  const before = await snapshot(value);
  assert.deepEqual(before.activation, initialized.activation);
  assert.equal(before.activation.host_profile_id, null);
  assert.equal(before.state.workflow.stage, "P0");
  assert.equal(before.state.decisions.active[0].authorization_ref, initialized.receipt.authorization_ref.authorization_id);

  const prepared = await prepareTransition(value, "P1", true);
  assert.equal(prepared.isError, undefined);
  const pending = await snapshot(value);
  assert.equal(pending.state.workflow.stage, "P0");
  assertError(await commit(value, prepared.structuredContent, "advance"), "PROMPT_NOT_FOUND");
  assert.deepEqual(await snapshot(value), pending);
  await approve(value, prepared.structuredContent, "advance");
  const committed = await commit(value, prepared.structuredContent, "advance");
  assert.equal(committed.isError, undefined);
  assert.equal(committed.structuredContent.receipt.authorization_ref.request_id, prepared.structuredContent.request_id);
  await verify(value, committed.structuredContent.receipt);
  const after = await snapshot(value);
  assert.equal(after.state.workflow.stage, "P1");
  assert.deepEqual(after.state.workflow.allowed_next, ["P2"]);
  assert.deepEqual(after.state.workflow.entry, before.state.workflow.entry);
  assert.equal(after.state.revision, 2);
  assert.deepEqual(after.state.pending_requests, []);
  assert.equal(after.state.last_change.receipt_id, committed.structuredContent.receipt.receipt_id);
});

test("ADOPT_EXISTING 从 P3/P5 接管并推进后保留完整 Entry", async (t) => {
  for (const [stage, target] of [["P3", "P4"], ["P5", "P6"]]) {
    await t.test(stage, async (t) => {
      const value = await fixture(t);
      const initial = initialState(stage);
      const initialized = await activate(value, initial);
      await verify(value, initialized.receipt);
      assert.deepEqual((await snapshot(value)).state.workflow.entry, initial.workflow.entry);
      const prepared = await prepareTransition(value, target, true);
      assert.equal(prepared.isError, undefined);
      await approve(value, prepared.structuredContent, "adopt-advance");
      const committed = await commit(value, prepared.structuredContent, "adopt-advance");
      assert.equal(committed.isError, undefined);
      await verify(value, committed.structuredContent.receipt);
      const after = await snapshot(value);
      assert.equal(after.state.workflow.stage, target);
      assert.deepEqual(after.state.workflow.entry, initial.workflow.entry);
      const altered = structuredClone(after.state);
      altered.workflow.entry.assessment_summary = "事后重写接管结论";
      assertError(await value.service.callTool("prepare_change", {
        project_root: value.root, operation: "ALTER_ENTRY", change_kind: "PRODUCT_DECISION",
        session_id: "web-e2e-session", proposed_state: altered,
      }), "WORKFLOW_ENTRY_IMMUTABLE");
      assert.deepEqual(await snapshot(value), after);
    });
  }
});

test("P4/P5 只消费显式 Completion，Gate 内容不自动转换阶段且 true 仍需 Maker 授权", async (t) => {
  for (const [stage, target] of [["P4", "P5"], ["P5", "P6"]]) {
    await t.test(stage, async (t) => {
      const value = await fixture(t);
      await activate(value, initialState(stage, [{ gate_id: "recorded-gate", status: "PASSED", reason: "REQUIREMENT_SATISFIED" }]));
      const before = await snapshot(value);
      const inspected = await value.service.callTool("inspect_project", { project_root: value.root });
      assert.equal(inspected.isError, undefined);
      assert.deepEqual(await snapshot(value), before);
      assertError(await prepareTransition(value, target, false), "COMPLETION_CONDITIONS_REQUIRED");
      assert.deepEqual(await snapshot(value), before);

      // 这是 Kernel 权责测试：Agent 对 Completion 的语义判断由 Child Skill 合同约束。
      // 即使状态含未解释的 Gate，Kernel 仍只校验显式 Completion 与授权，不充当 Gate Engine。
      const blockedGate = [{ gate_id: "recorded-gate", status: "BLOCKED", reason: "未经 Kernel 解释的领域结论" }];
      const prepared = await prepareTransition(value, target, true, blockedGate);
      assert.equal(prepared.isError, undefined);
      const pending = await snapshot(value);
      assert.equal(pending.state.workflow.stage, stage);
      assert.deepEqual(pending.state.gates, before.state.gates);
      assertError(await commit(value, prepared.structuredContent, "explicit-completion"), "PROMPT_NOT_FOUND");
      assert.deepEqual(await snapshot(value), pending);
      await approve(value, prepared.structuredContent, "explicit-completion");
      const committed = await commit(value, prepared.structuredContent, "explicit-completion");
      assert.equal(committed.isError, undefined);
      await verify(value, committed.structuredContent.receipt);
      const after = await snapshot(value);
      assert.equal(after.state.workflow.stage, target);
      assert.deepEqual(after.state.gates, blockedGate);
      assert.deepEqual(after.state.workflow.entry, before.state.workflow.entry);
      assert.deepEqual(after.state.pending_requests, []);
    });
  }
});

test("Checkpoint、Validation Channel、MCP 和 Deployment 不能成为 Web Runtime Stage", async (t) => {
  for (const stage of ["USABLE_WEB_SLICE", "BUILD_READINESS", "LOCAL_PRODUCT_VALIDATION", "LOGIC_AUTOMATION", "BUILD_VALIDATION", "LOCAL_INTEGRATION_VALIDATION", "LOCAL_BROWSER_VALIDATION", "SECONDARY_INTERFACE_VALIDATION", "HUMAN_VALIDATION", "MCP", "DEPLOYMENT"]) {
    await t.test(stage, async (t) => {
      const value = await fixture(t);
      await activate(value, initialState("P4"));
      const before = await snapshot(value);
      assertError(await prepareTransition(value, stage, true), "ILLEGAL_TRANSITION");
      assert.deepEqual(await snapshot(value), before);
    });
  }
});

test("Core State Schema 拒绝 Checkpoint、Channel、MCP 和 Deployment 专用字段", () => {
  for (const field of ["checkpoints", "validation_channels", "mcp", "deployment_capability", "primary_surface", "integration_surface"]) {
    const state = initialState();
    assert.throws(() => parseProjectState({ ...state, [field]: {} }), field);
    state.workflow[field] = {};
    assert.throws(() => parseProjectState(state), `workflow.${field}`);
  }
});
