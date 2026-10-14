import assert from "node:assert/strict";
import { access, mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { handleUserPromptSubmit } from "../../hooks/user-prompt-submit.mjs";
import { createKernelService } from "../../src/server.mjs";
import { initializeProjectState } from "../../src/kernel/state-store.mjs";

const nowText = "2026-10-14T08:00:00.000Z";
const nextByStage = {
  P0: ["P1"], P1: ["P2"], P2: ["P3"], P3: ["P4"],
  P4: ["P5"], P5: ["P6"], P6: ["P2", "P3", "P4", "P5"],
};
const productDecisions = [
  { decision_id: "web-boundary", statement: "本项目以浏览器中的用户结果为主要交付。" },
  { decision_id: "deployment-policy", statement: "本轮验证限定于本地环境，部署能力挂起。" },
];

function webState(stage = "P0", mode = "NEW_PROJECT", evidenceRefs = []) {
  return {
    schema_version: "1.1", project_id: "web-project", revision: 0,
    boundary: { objective: "孵化一个 Web 产品", supported: ["浏览器用户旅程"], excluded: ["公开部署"] },
    workflow: {
      stage, status: "ACTIVE", completed: [], allowed_next: nextByStage[stage] ?? [],
      entry: {
        mode, initial_stage: stage, assessment_summary: "已根据现有项目证据判断当前阶段。",
        evidence_refs: evidenceRefs, assessed_at: nowText,
      },
    },
    capabilities: [], decisions: { active: [], archive_ref: null }, assumptions: [],
    plan: { current_action: "推进当前阶段", next_action: "验证阶段出口", completion_conditions: ["阶段证据成立"] },
    gates: [], risks: [], pending_requests: [], baselines: [],
    human_validation: { limit: "UNSET", consumed: 0 },
    last_change: { operation: "INITIALIZE_PROJECT", changed_at: nowText, summary: "Web 项目已激活" },
    archive_refs: [],
  };
}

async function fixture(t) {
  const projectRoot = await mkdtemp(path.join(os.tmpdir(), "web-router-project-"));
  const runtimeDataRoot = await mkdtemp(path.join(os.tmpdir(), "web-router-runtime-"));
  t.after(() => rm(projectRoot, { recursive: true, force: true }));
  t.after(() => rm(runtimeDataRoot, { recursive: true, force: true }));
  return {
    projectRoot, runtimeDataRoot,
    service: await createKernelService({ pluginRoot: path.resolve(import.meta.dirname, "../.."), runtimeDataRoot }),
  };
}

async function prepare(value, state = webState(), overrides = {}) {
  return value.service.callTool("prepare_activation", {
    project_root: value.projectRoot, project_id: "web-project", project_type_id: "web-product",
    host_profile_id: null, session_id: "web-session", summary: "激活 Web 产品孵化器",
    state, product_decisions: productDecisions, ...overrides,
  }, { now: new Date(nowText) });
}

async function approve(value, request, turnId) {
  await handleUserPromptSubmit({
    cwd: value.projectRoot, session_id: "web-session", turn_id: turnId, timestamp: nowText,
    prompt: `我明确批准 ${request.request_id}，scope_digest: ${request.scope_digest}`,
  }, { runtimeDataRoot: value.runtimeDataRoot, now: new Date(nowText) });
}

async function initialize(value, request, turnId, overrides = {}) {
  return value.service.callTool("initialize_project", {
    project_root: value.projectRoot, request_id: request.request_id, scope_digest: request.scope_digest,
    session_id: "web-session", turn_id: turnId, ...overrides,
  }, { now: new Date(nowText) });
}

async function activate(value, state = webState()) {
  const prepared = await prepare(value, state);
  assert.equal(prepared.isError, undefined, JSON.stringify(prepared.structuredContent));
  await approve(value, prepared.structuredContent, "activate");
  const initialized = await initialize(value, prepared.structuredContent, "activate");
  assert.equal(initialized.isError, undefined, JSON.stringify(initialized.structuredContent));
  return initialized.structuredContent;
}

async function snapshot(value) {
  const result = await value.service.callTool("get_project_state", { project_root: value.projectRoot });
  assert.equal(result.isError, undefined);
  return result.structuredContent;
}

async function noAuthority(value) {
  await assert.rejects(() => access(path.join(value.projectRoot, ".project-incubator")), /ENOENT/);
}

function assertError(result, code) {
  assert.equal(result.isError, true);
  assert.equal(result.structuredContent.error.code, code);
  assert.equal(result.structuredContent.receipt, undefined);
}

async function driftPending(value, mutate) {
  const names = (await readdir(value.runtimeDataRoot)).filter((name) => name.startsWith("activation-"));
  assert.equal(names.length, 1);
  const target = path.join(value.runtimeDataRoot, names[0]);
  const pending = JSON.parse(await readFile(target, "utf8"));
  mutate(pending);
  await writeFile(target, `${JSON.stringify(pending)}\n`, "utf8");
}

test("Web 路由使用 Web Child Skill、空 Host，且不写权威状态", async (t) => {
  const value = await fixture(t);
  for (const host of [{ host_profile_id: null }, {}]) {
    const result = await value.service.callTool("propose_route", {
      project_root: value.projectRoot, project_type_id: "web-product", ...host,
    });
    assert.equal(result.isError, undefined);
    assert.equal(result.structuredContent.event, "ROUTE_PROPOSED");
    assert.deepEqual(result.structuredContent.route, {
      project_type_id: "web-product", child_skill_id: "web-product-incubator", host_profile_id: null,
    });
  }
  await noAuthority(value);
  assert.deepEqual(await readdir(value.runtimeDataRoot), []);
});

test("Web Route 与 Prepare 拒绝非空 Host，未知类型保持稳定错误", async (t) => {
  for (const host of ["windows-desktop", "sims-4", "browser", "unknown-host"]) {
    await t.test(host, async (t) => {
      const value = await fixture(t);
      assertError(await value.service.callTool("propose_route", {
        project_root: value.projectRoot, project_type_id: "web-product", host_profile_id: host,
      }), "HOST_PROFILE_FORBIDDEN");
      assertError(await prepare(value, webState(), { host_profile_id: host }), "HOST_PROFILE_FORBIDDEN");
      await noAuthority(value);
      assert.deepEqual(await readdir(value.runtimeDataRoot), []);
    });
  }
  const value = await fixture(t);
  for (const host_profile_id of [null, "windows-desktop"]) {
    assertError(await value.service.callTool("propose_route", {
      project_root: value.projectRoot, project_type_id: "independent-mcp-service", host_profile_id,
    }), "PROJECT_TYPE_NOT_FOUND");
    assertError(await prepare(value, webState(), {
      project_type_id: "independent-mcp-service", host_profile_id,
    }), "PROJECT_TYPE_NOT_FOUND");
  }
  await noAuthority(value);
  assert.deepEqual(await readdir(value.runtimeDataRoot), []);
});

test("Web NEW_PROJECT 只接受 P0，Prepare 仅保存 Pending Activation", async (t) => {
  for (const stage of ["P0", "P1", "P2", "P3", "P4", "P5", "P6"]) {
    await t.test(stage, async (t) => {
      const value = await fixture(t);
      const result = await prepare(value, webState(stage));
      if (stage === "P0") {
        assert.equal(result.isError, undefined);
        assert.equal(result.structuredContent.event, "ACTIVATION_PREPARED");
        assert.match(result.structuredContent.scope_digest, /^[a-f0-9]{64}$/u);
        assert.equal(result.structuredContent.receipt, undefined);
        const files = await readdir(value.runtimeDataRoot);
        assert.equal(files.length, 1);
        assert.match(files[0], /^activation-[a-f0-9]{64}\.json$/u);
      } else {
        assertError(result, "WORKFLOW_ENTRY_STAGE_INVALID");
        assert.deepEqual(await readdir(value.runtimeDataRoot), []);
      }
      await noAuthority(value);
    });
  }
});

test("Web ADOPT_EXISTING 在 P0–P6 均要求 Evidence 并按原阶段激活", async (t) => {
  for (const stage of ["P0", "P1", "P2", "P3", "P4", "P5", "P6"]) {
    await t.test(stage, async (t) => {
      const value = await fixture(t);
      assertError(await prepare(value, webState(stage, "ADOPT_EXISTING")), "WORKFLOW_ENTRY_EVIDENCE_REQUIRED");
      await noAuthority(value);
      assert.deepEqual(await readdir(value.runtimeDataRoot), []);
      const state = webState(stage, "ADOPT_EXISTING", [`evidence://existing-${stage}`]);
      await activate(value, state);
      const after = await snapshot(value);
      assert.equal(after.state.workflow.stage, stage);
      assert.deepEqual(after.state.workflow.allowed_next, nextByStage[stage]);
      assert.deepEqual(after.state.workflow.entry, state.workflow.entry);
      assert.equal(after.activation.host_profile_id, null);
    });
  }
});

const invalidInitialStates = [
  ["缺少 Entry", (state) => { delete state.workflow.entry; }, "WORKFLOW_ENTRY_REQUIRED"],
  ["空 Entry", (state) => { state.workflow.entry = null; }, "WORKFLOW_ENTRY_REQUIRED"],
  ["新激活不得使用 State 1.0", (state) => { state.schema_version = "1.0"; delete state.workflow.entry; }, "WORKFLOW_ENTRY_REQUIRED"],
  ["未知 Mode", (state) => { state.workflow.entry.mode = "UNKNOWN"; }, "WORKFLOW_ENTRY_MODE_INVALID"],
  ["接管项目缺少 Evidence", (state) => { state.workflow.entry.evidence_refs = []; }, "WORKFLOW_ENTRY_EVIDENCE_REQUIRED"],
  ["Entry 与 Stage 不一致", (state) => { state.workflow.entry.initial_stage = "P3"; }, "WORKFLOW_ENTRY_STATE_MISMATCH"],
  ["未知 Stage", (state) => { state.workflow.stage = "P7"; state.workflow.entry.initial_stage = "P7"; }, "WORKFLOW_ENTRY_STAGE_INVALID"],
  ["错误 Allowed Next", (state) => { state.workflow.allowed_next = ["P6"]; }, "WORKFLOW_ALLOWED_NEXT_MISMATCH"],
  ["错误 Return Stage", (state) => { state.workflow.return_stage = "P2"; }, "WORKFLOW_RETURN_STAGE_MISMATCH"],
];

test("Web Prepare 拒绝非法 Entry、Schema 与 Workflow Shape，且不创建 Pending", async (t) => {
  for (const [name, mutate, code] of invalidInitialStates) {
    await t.test(name, async (t) => {
      const value = await fixture(t);
      const state = webState("P0", "ADOPT_EXISTING", ["evidence://existing-project"]);
      mutate(state);
      assertError(await prepare(value, state), code);
      await noAuthority(value);
      assert.deepEqual(await readdir(value.runtimeDataRoot), []);
    });
  }
});

const validEntryDrifts = [
  ["Mode", (state) => { state.workflow.entry.mode = "NEW_PROJECT"; }],
  ["Initial Stage", (state) => {
    state.workflow.entry.initial_stage = "P3";
    state.workflow.stage = "P3";
    state.workflow.allowed_next = ["P4"];
  }],
  ["Assessment Summary", (state) => { state.workflow.entry.assessment_summary = "已补充新的评估结论。"; }],
  ["Evidence Refs", (state) => { state.workflow.entry.evidence_refs = ["evidence://different-project"]; }],
  ["Assessed At", (state) => { state.workflow.entry.assessed_at = "2026-10-14T07:00:00.000Z"; }],
];

test("Activation Digest 覆盖完整 Entry 与 Initial State，合法内容漂移也失败关闭", async (t) => {
  const drifts = [...validEntryDrifts, ["非 Entry 的 Initial State", (state) => { state.plan.current_action = "变更后的行动"; }]];
  for (const [name, mutate] of drifts) {
    await t.test(name, async (t) => {
      const value = await fixture(t);
      const state = webState("P0", "ADOPT_EXISTING", ["evidence://existing-project"]);
      const first = await prepare(value, state);
      assert.equal(first.isError, undefined);
      const changed = structuredClone(state);
      mutate(changed);
      const second = await prepare(value, changed);
      assert.equal(second.isError, undefined);
      assert.notEqual(first.structuredContent.scope_digest, second.structuredContent.scope_digest);
      const prepared = await prepare(value, state);
      assert.equal(prepared.structuredContent.scope_digest, first.structuredContent.scope_digest);
      await driftPending(value, (pending) => { mutate(pending.initial_state); });
      await approve(value, prepared.structuredContent, "scope-drift");
      assertError(await initialize(value, prepared.structuredContent, "scope-drift"), "SCOPE_DIGEST_MISMATCH");
      await noAuthority(value);
    });
  }
});

test("Initialize 重验 Host、Route、Entry、Schema 与 Workflow Shape", async (t) => {
  const drifts = [
    ["非空 Host", (pending) => { pending.route.host_profile_id = "windows-desktop"; }, "HOST_PROFILE_FORBIDDEN"],
    ["Child Skill", (pending) => { pending.route.child_skill_id = "mod-incubator"; }, "ACTIVATION_ROUTE_MISMATCH"],
    ...invalidInitialStates.map(([name, mutate, code]) => [name, (pending) => { mutate(pending.initial_state); }, code]),
  ];
  for (const [name, mutate, code] of drifts) {
    await t.test(name, async (t) => {
      const value = await fixture(t);
      const prepared = await prepare(value, webState("P0", "ADOPT_EXISTING", ["evidence://existing-project"]));
      assert.equal(prepared.isError, undefined);
      await driftPending(value, mutate);
      await approve(value, prepared.structuredContent, "invalid-drift");
      assertError(await initialize(value, prepared.structuredContent, "invalid-drift"), code);
      await noAuthority(value);
    });
  }
});

test("Web 初始化必须获得精确 Maker 授权，并持久化 Decision、Receipt 与 Read-back", async (t) => {
  const value = await fixture(t);
  const prepared = await prepare(value);
  assert.equal(prepared.isError, undefined);
  const request = prepared.structuredContent;
  assertError(await initialize(value, request, "no-prompt"), "PROMPT_NOT_FOUND");
  await noAuthority(value);
  await approve(value, { ...request, scope_digest: "a".repeat(64) }, "wrong-scope");
  assertError(await initialize(value, request, "wrong-scope"), "PROMPT_SCOPE_NOT_CONFIRMED");
  await noAuthority(value);
  await approve(value, request, "approved");
  const initialized = await initialize(value, request, "approved");
  assert.equal(initialized.isError, undefined);
  const { activation, receipt } = initialized.structuredContent;
  assert.equal(activation.project_type_id, "web-product");
  assert.equal(activation.child_skill_id, "web-product-incubator");
  assert.equal(activation.host_profile_id, null);
  assert.equal(receipt.operation, "INITIALIZE_PROJECT");
  assert.equal(receipt.previous_revision, null);
  assert.equal(receipt.new_revision, 0);
  assert.equal(receipt.authorization_ref.request_id, request.request_id);
  assert.match(receipt.authorization_ref.authorization_id, /^authorization-/u);
  const after = await snapshot(value);
  assert.deepEqual(after.activation, activation);
  assert.deepEqual(after.receipt, receipt);
  assert.equal(after.state.schema_version, "1.1");
  assert.deepEqual(after.state.workflow.entry, webState().workflow.entry);
  assert.equal(after.state.last_change.receipt_id, receipt.receipt_id);
  assert.deepEqual(after.state.decisions.active, productDecisions.map((decision) => ({
    ...decision, kind: "PRODUCT", status: "ACTIVE",
    authorization_ref: receipt.authorization_ref.authorization_id, confirmed_at: nowText,
  })));
  const verification = await value.service.callTool("verify_receipt", {
    project_root: value.projectRoot, receipt_id: receipt.receipt_id,
  });
  assert.equal(verification.structuredContent.verified, true);
  const inspected = await value.service.callTool("inspect_project", { project_root: value.projectRoot });
  assert.equal(inspected.structuredContent.summary.integrity.receipt_verified, true);
  assert.equal(inspected.structuredContent.summary.routing.host_profile_id, null);
  assert.equal((await readdir(value.runtimeDataRoot)).some((name) => name.startsWith("activation-")), false);
  assertError(await initialize(value, request, "approved"), "ACTIVATION_REQUEST_NOT_FOUND");
});

test("Web Product Decision 变更复用授权与 Receipt，并保留未变 Decision 的授权", async (t) => {
  const value = await fixture(t);
  const { receipt: initialReceipt } = await activate(value);
  const before = await snapshot(value);
  const proposed = structuredClone(before.state);
  proposed.decisions.active[0].statement = "主要浏览器旅程增加本地失败反馈。";
  const prepared = await value.service.callTool("prepare_change", {
    project_root: value.projectRoot, operation: "UPDATE_WEB_BOUNDARY", change_kind: "PRODUCT_DECISION",
    session_id: "web-session", proposed_state: proposed,
  }, { now: new Date(nowText) });
  assert.equal(prepared.isError, undefined);
  const request = prepared.structuredContent;
  const commitArgs = {
    project_root: value.projectRoot, request_id: request.request_id, scope_digest: request.scope_digest,
    session_id: "web-session", turn_id: "decision-change",
  };
  const pending = await snapshot(value);
  assertError(await value.service.callTool("commit_change", commitArgs), "PROMPT_NOT_FOUND");
  assert.deepEqual(await snapshot(value), pending);
  await approve(value, request, "decision-change");
  const committed = await value.service.callTool("commit_change", commitArgs, { now: new Date(nowText) });
  assert.equal(committed.isError, undefined);
  const receipt = committed.structuredContent.receipt;
  assert.equal(receipt.previous_revision, 1);
  assert.equal(receipt.new_revision, 2);
  assert.equal(receipt.authorization_ref.request_id, request.request_id);
  const after = await snapshot(value);
  assert.equal(after.state.decisions.active[0].statement, "主要浏览器旅程增加本地失败反馈。");
  assert.equal(after.state.decisions.active[0].authorization_ref, receipt.authorization_ref.authorization_id);
  assert.equal(after.state.decisions.active[1].authorization_ref, initialReceipt.authorization_ref.authorization_id);
  assert.deepEqual(after.state.workflow.entry, before.state.workflow.entry);
  assert.deepEqual(after.state.pending_requests, []);
  const verified = await value.service.callTool("verify_receipt", {
    project_root: value.projectRoot, receipt_id: receipt.receipt_id,
  });
  assert.equal(verified.structuredContent.verified, true);
  const statePath = path.join(value.projectRoot, ".project-incubator", "state.json");
  const tampered = structuredClone(after.state);
  tampered.plan.current_action = "未经过 Mutation 的磁盘改写";
  await writeFile(statePath, `${JSON.stringify(tampered)}\n`, "utf8");
  const invalidReceipt = await value.service.callTool("verify_receipt", {
    project_root: value.projectRoot, receipt_id: receipt.receipt_id,
  });
  assert.equal(invalidReceipt.structuredContent.verified, false);
  assert.equal(invalidReceipt.structuredContent.reason, "STATE_HASH_MISMATCH");
  assertError(await value.service.callTool("inspect_project", { project_root: value.projectRoot }), "RECEIPT_UNVERIFIABLE");
});

const immutableEntryDrifts = [
  ...validEntryDrifts.filter(([name]) => name !== "Initial Stage"),
  ["Initial Stage", (state) => { state.workflow.entry.initial_stage = "P3"; }],
  ["降级并删除 Entry", (state) => { state.schema_version = "1.0"; delete state.workflow.entry; }],
];

test("Web 激活后的完整 Entry 在 Prepare Change 中不可改写或降级删除", async (t) => {
  for (const [name, mutate] of immutableEntryDrifts) {
    await t.test(name, async (t) => {
      const value = await fixture(t);
      await activate(value, webState("P0", "ADOPT_EXISTING", ["evidence://existing-project"]));
      const before = await snapshot(value);
      const proposed = structuredClone(before.state);
      mutate(proposed);
      assertError(await value.service.callTool("prepare_change", {
        project_root: value.projectRoot, operation: "ALTER_ENTRY", change_kind: "PRODUCT_DECISION",
        session_id: "web-session", proposed_state: proposed,
      }), "WORKFLOW_ENTRY_IMMUTABLE");
      assert.deepEqual(await snapshot(value), before);
    });
  }
});

test("Web Commit Change 重验完整 Entry，Maker 授权也不能改写或删除 Entry", async (t) => {
  for (const [name, mutate] of immutableEntryDrifts) {
    await t.test(name, async (t) => {
      const value = await fixture(t);
      const state = webState("P0", "ADOPT_EXISTING", ["evidence://existing-project"]);
      const proposed = structuredClone(state);
      mutate(proposed);
      const request = { request_id: "request-entry-drift", scope_digest: "b".repeat(64) };
      state.pending_requests = [{
        ...request, operation: "ALTER_ENTRY", status: "PENDING", created_at: nowText, project_revision: 0,
        payload: { change_kind: "PRODUCT_DECISION", proposed_state: proposed, session_id: "web-session", requires_authorization: true },
      }];
      await initializeProjectState(value.projectRoot, {
        schema_version: "1.0", project_id: "web-project", plugin_id: "project-incubator-plugin",
        plugin_version: "0.3.0", status: "ACTIVE", project_type_id: "web-product",
        child_skill_id: "web-product-incubator", host_profile_id: null,
      }, state, { authorization_id: "authorization-existing", request_id: "activation-existing", prompt_digest: "a".repeat(64) });
      const before = await snapshot(value);
      await approve(value, request, "immutable-entry");
      assertError(await value.service.callTool("commit_change", {
        project_root: value.projectRoot, ...request, session_id: "web-session", turn_id: "immutable-entry",
      }, { now: new Date(nowText) }), "WORKFLOW_ENTRY_IMMUTABLE");
      assert.deepEqual(await snapshot(value), before);
    });
  }
});

test("既有 State 1.0 的 Mod 与 Desktop 保持 Inspect、Mutation、阶段转换及原路由", async (t) => {
  for (const route of [
    { project_type_id: "mod", child_skill_id: "mod-incubator", host_profile_id: "sims-4", stage: "M0_BOUNDARY", next: "M1_RISK_MODEL", afterNext: ["M2_VERTICAL_SLICE"] },
    { project_type_id: "desktop-product", child_skill_id: "desktop-product-incubator", host_profile_id: "windows-desktop", stage: "P0", next: "P1", afterNext: ["P2"] },
  ]) {
    await t.test(route.project_type_id, async (t) => {
      const value = await fixture(t);
      const state = webState();
      state.schema_version = "1.0";
      delete state.workflow.entry;
      state.workflow.stage = route.stage;
      state.workflow.allowed_next = [route.next];
      const activation = {
        schema_version: "1.0", project_id: "web-project", plugin_id: "project-incubator-plugin",
        plugin_version: "0.2.0", status: "ACTIVE", project_type_id: route.project_type_id,
        child_skill_id: route.child_skill_id, host_profile_id: route.host_profile_id,
      };
      await initializeProjectState(value.projectRoot, activation, state, {
        authorization_id: "authorization-existing", request_id: "activation-existing", prompt_digest: "a".repeat(64),
      });
      const inspected = await value.service.callTool("inspect_project", { project_root: value.projectRoot });
      assert.equal(inspected.isError, undefined);
      assert.equal(inspected.structuredContent.summary.workflow.entry, undefined);
      assert.equal(inspected.structuredContent.summary.routing.project_type_id, route.project_type_id);
      const proposed = structuredClone((await snapshot(value)).state);
      proposed.workflow.stage = route.next;
      proposed.workflow.allowed_next = route.afterNext;
      proposed.plan.current_action = "推进已授权的下一阶段";
      const prepared = await value.service.callTool("prepare_change", {
        project_root: value.projectRoot, operation: "ADVANCE_LEGACY_STAGE", change_kind: "WORKFLOW_TRANSITION",
        session_id: "web-session", proposed_state: proposed,
        workflow_transition: { target_stage: route.next, completion_satisfied: true },
      }, { now: new Date(nowText) });
      assert.equal(prepared.isError, undefined);
      await approve(value, prepared.structuredContent, "legacy-transition");
      const committed = await value.service.callTool("commit_change", {
        project_root: value.projectRoot, request_id: prepared.structuredContent.request_id,
        scope_digest: prepared.structuredContent.scope_digest, session_id: "web-session", turn_id: "legacy-transition",
      }, { now: new Date(nowText) });
      assert.equal(committed.isError, undefined);
      const after = await snapshot(value);
      assert.equal(after.state.schema_version, "1.0");
      assert.equal(after.state.workflow.entry, undefined);
      assert.equal(after.state.workflow.stage, route.next);
      assert.equal(after.state.plan.current_action, "推进已授权的下一阶段");
      assert.deepEqual(after.activation, activation);
      assert.deepEqual(after.state.pending_requests, []);
      assert.equal(after.state.revision, 2);
      const verified = await value.service.callTool("verify_receipt", {
        project_root: value.projectRoot, receipt_id: committed.structuredContent.receipt.receipt_id,
      });
      assert.equal(verified.structuredContent.verified, true);
    });
  }
});
