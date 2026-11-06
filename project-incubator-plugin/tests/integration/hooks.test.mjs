import assert from "node:assert/strict";
import { access, mkdtemp, readFile, rm, symlink, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { handlePreToolUse } from "../../hooks/pre-tool-use.mjs";
import { handleStop } from "../../hooks/stop.mjs";
import { handleUserPromptSubmit, turnMarkerPath } from "../../hooks/user-prompt-submit.mjs";
import { commitProjectState, initializeProjectState } from "../../src/kernel/state-store.mjs";
import { createKernelService } from "../../src/server.mjs";

const now = "2026-09-29T08:00:00.000Z";
const authorizationRef = {
  authorization_id: "authorization-1", request_id: "request-1", prompt_digest: "b".repeat(64),
};

function activation(status = "ACTIVE") {
  return {
    schema_version: "1.0", project_id: "project-1",
    plugin_id: "project-incubator-plugin", plugin_version: "0.1.0", status,
    project_type_id: "mod", child_skill_id: "mod-incubator", host_profile_id: "sims-4",
  };
}

function state() {
  return {
    schema_version: "1.0", project_id: "project-1", revision: 0,
    boundary: { objective: "最小 Mod", supported: ["一项能力"], excluded: [] },
    workflow: { stage: "M0_BOUNDARY", status: "ACTIVE", completed: [], allowed_next: ["M1_RISK_MODEL"] },
    capabilities: [], decisions: { active: [], archive_ref: null }, assumptions: [],
    plan: { current_action: "确认边界", next_action: "风险建模", completion_conditions: ["Maker 确认"] },
    gates: [], risks: [], pending_requests: [], baselines: [],
    human_validation: { limit: "UNSET", consumed: 0 },
    last_change: { operation: "INITIALIZE_PROJECT", changed_at: now, summary: "初始化" },
    archive_refs: [],
  };
}

async function workspace(t) {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-hooks-"));
  const codexHome = await mkdtemp(path.join(os.tmpdir(), "incubator-hooks-home-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  t.after(() => rm(codexHome, { recursive: true, force: true }));
  return { root, codexHome, env: { CODEX_HOME: codexHome } };
}

async function initialize(root) {
  await initializeProjectState(root, activation(), state(), authorizationRef);
}

function promptEvent(root, overrides = {}) {
  return {
    cwd: root, prompt: "继续只读检查", session_id: "session-1", turn_id: "turn-1",
    timestamp: "2026-09-29T08:01:00.000Z", ...overrides,
  };
}

test("all hooks are side-effect free for unmanaged projects", async (t) => {
  const { root, codexHome, env } = await workspace(t);
  assert.deepEqual(await handleUserPromptSubmit(promptEvent(root), { env }), { continue: true });
  assert.deepEqual(await handlePreToolUse({ cwd: root, tool_name: "apply_patch", tool_input: {} }), {});
  assert.deepEqual(await handleStop({ cwd: root, session_id: "session-1", turn_id: "turn-1" }, { env }), { continue: true });
  await assert.rejects(() => access(path.join(codexHome, "project-incubator-plugin")), /ENOENT/);
});

const englishHubHandoff = `# English Learning Hub 交接说明
目标：在空工作区新建一个长期使用的本地产品，包含前端学习界面、后端课程和进度数据。
Phase 0：立即初始化项目目录、前后端工程和文档。
Phase 1：完成产品边界与架构。Phase 2：建立基础功能。Phase 3：运行并验收。`;

test("explicit managed handoff receives Router-first guidance before any activation", async (t) => {
  const { root, env } = await workspace(t);
  const result = await handleUserPromptSubmit(promptEvent(root, {
    prompt: `${englishHubHandoff}\n本项目必须由 Project Incubator 管理，先确认路由和激活。`,
  }), { env });
  assert.match(result.hookSpecificOutput?.additionalContext ?? "", /project-incubator-router/u);
  assert.match(result.hookSpecificOutput?.additionalContext ?? "", /工程写入/u);
  await assert.rejects(() => access(path.join(root, ".project-incubator")), /ENOENT/);
  const write = { cwd: root, session_id: "session-1", tool_name: "apply_patch", tool_input: { patch: "*** Add File: app.js" } };
  assert.equal((await handlePreToolUse(write, { env })).hookSpecificOutput?.permissionDecision, "deny");
  assert.equal((await handlePreToolUse({ cwd: root, session_id: "session-1", tool_name: "exec_command", tool_input: { cmd: "New-Item app.js" } }, { env })).hookSpecificOutput?.permissionDecision, "deny");
  assert.deepEqual(await handlePreToolUse({ cwd: root, session_id: "session-1", tool_name: "mcp__project_incubator__propose_route", tool_input: {} }, { env }), {});
  assert.deepEqual(await handlePreToolUse({ cwd: root, session_id: "session-1", tool_name: "read_file", tool_input: { path: "README.md" } }, { env }), {});
  assert.deepEqual(await handlePreToolUse({ ...write, session_id: "another-session" }, { env }), {});
  await initialize(root);
  assert.deepEqual(await handlePreToolUse(write, { env }), {});
});

test("new-product handoff without plugin name requires Router before engineering writes", async (t) => {
  const { root, env } = await workspace(t);
  const result = await handleUserPromptSubmit(promptEvent(root, { prompt: englishHubHandoff }), { env });
  assert.match(result.hookSpecificOutput?.additionalContext ?? "", /必须先调用 project-incubator-router/u);
  const write = { cwd: root, session_id: "session-1", tool_name: "apply_patch", tool_input: { patch: "*** Add File: app.js" } };
  assert.equal((await handlePreToolUse(write, { env })).hookSpecificOutput?.permissionDecision, "deny");
  assert.deepEqual(await handlePreToolUse({ cwd: root, session_id: "session-1", tool_name: "mcp__project_incubator__propose_route", tool_input: {} }, { env }), {});
  await handleUserPromptSubmit(promptEvent(root, { prompt: "明确不用 Project Incubator，按普通项目创建。" }), { env });
  assert.deepEqual(await handlePreToolUse(write, { env }), {});
});

test("Maker can withdraw a pre-activation managed intent without leaving a write block", async (t) => {
  const { root, env } = await workspace(t);
  await handleUserPromptSubmit(promptEvent(root, { prompt: "本项目必须由 Project Incubator 管理。" }), { env });
  const write = { cwd: root, session_id: "session-1", tool_name: "apply_patch", tool_input: { patch: "*** Add File: app.js" } };
  assert.equal((await handlePreToolUse(write, { env })).hookSpecificOutput?.permissionDecision, "deny");
  await handleUserPromptSubmit(promptEvent(root, { prompt: "我改主意了，不要使用 Project Incubator 管理。" }), { env });
  assert.deepEqual(await handlePreToolUse(write, { env }), {});
});

test("ordinary or explicitly non-managed work receives no Router hint", async (t) => {
  const { root, env } = await workspace(t);
  for (const prompt of [
    "修复这个函数的空值错误",
    "新建一次性演示页面，不使用 Project Incubator 管理",
    "新建一个长期使用的产品，但不要使用 Project Incubator 管理。",
    "请不要让 Project Incubator 管理这个长期项目。",
    "调查 Project Incubator 管理新项目时的历史故障，只检查插件源码和测试。",
  ]) {
    assert.deepEqual(await handleUserPromptSubmit(promptEvent(root, { prompt }), { env }), { continue: true });
  }
});

test("activated projects block direct writes through shell, patch and editor tools", async (t) => {
  const { root } = await workspace(t);
  await initialize(root);
  const alias = path.join(root, "authority-alias");
  await symlink(path.join(root, ".project-incubator"), alias, "junction");
  const cases = [
    { tool_name: "exec_command", tool_input: { cmd: "Set-Content .project-incubator/state.json '{}'" } },
    { tool_name: "apply_patch", tool_input: { patch: "*** Update File: .project-incubator/activation.json" } },
    { tool_name: "write_file", tool_input: { path: path.join(root, ".project-incubator", "latest-receipt.json") } },
    { tool_name: "write_file", tool_input: { path: path.join(alias, "state.json") } },
  ];
  for (const current of cases) {
    const result = await handlePreToolUse({ cwd: root, ...current });
    assert.equal(result.hookSpecificOutput.permissionDecision, "deny");
  }
  assert.deepEqual(await handlePreToolUse({
    cwd: root, tool_name: "mcp__project_incubator__commit_change", tool_input: {},
  }), {});
});

test("activated projects block shell writes when the protected path is quoted", async (t) => {
  const { root } = await workspace(t);
  await initialize(root);
  const result = await handlePreToolUse({
    cwd: root,
    tool_name: "Bash",
    tool_input: {
      command: "Set-Content -LiteralPath '.project-incubator\\state.json' -Value 'blocked'",
    },
  });
  assert.equal(result.hookSpecificOutput?.permissionDecision, "deny");
});

test("activated projects block basename writes from inside the authority directory", async (t) => {
  const { root } = await workspace(t);
  await initialize(root);
  const cwd = path.join(root, ".project-incubator");
  const cases = [
    { tool_name: "exec_command", tool_input: { cmd: "Set-Content state.json hacked" } },
    { tool_name: "write_file", tool_input: { path: "latest-receipt.json" } },
  ];
  for (const current of cases) {
    const result = await handlePreToolUse({ cwd, ...current });
    assert.equal(result.hookSpecificOutput?.permissionDecision, "deny");
  }
  assert.deepEqual(await handlePreToolUse({
    cwd, tool_name: "exec_command", tool_input: { cmd: "Get-Content state.json" },
  }), {});
});

test("activated projects allow explicit read-only access to authority files", async (t) => {
  const { root } = await workspace(t);
  await initialize(root);
  const cases = [
    "Get-FileHash -Algorithm SHA256 -LiteralPath '.project-incubator\\state.json'",
    "Get-Content -Raw -LiteralPath '.project-incubator\\state.json' | ConvertFrom-Json | Select-Object revision",
  ];
  for (const command of cases) {
    assert.deepEqual(await handlePreToolUse({
      cwd: root, tool_name: "Bash", tool_input: { command },
    }), {});
  }
  assert.deepEqual(await handlePreToolUse({
    cwd: root,
    tool_name: "read_file",
    tool_input: { path: path.join(root, ".project-incubator", "state.json") },
  }), {});
});

test("activated projects deny mixed or unknown shell access to authority files", async (t) => {
  const { root } = await workspace(t);
  await initialize(root);
  const cases = [
    "Get-Content -Raw '.project-incubator\\state.json'; Set-Content '.project-incubator\\state.json' '{}'",
    "Write-Output $(Set-Content '.project-incubator\\state.json' '{}')",
    "python -c \"open('.project-incubator/state.json','w').write('{}')\"",
  ];
  for (const command of cases) {
    const result = await handlePreToolUse({
      cwd: root, tool_name: "Bash", tool_input: { command },
    });
    assert.equal(result.hookSpecificOutput?.permissionDecision, "deny");
  }
});

test("read-only turns do not require a new receipt", async (t) => {
  const { root, env } = await workspace(t);
  await initialize(root);
  await handleUserPromptSubmit(promptEvent(root), { env });
  assert.deepEqual(await handleStop({
    cwd: root, session_id: "session-1", turn_id: "turn-1", last_assistant_message: "只读完成",
  }, { env }), { continue: true });
});

test("a host-resumed turn without an exact marker closes only from an unchanged same-session baseline", async (t) => {
  const { root, env } = await workspace(t);
  await initialize(root);
  await handleUserPromptSubmit(promptEvent(root), { env });

  assert.deepEqual(await handleStop({
    cwd: root,
    session_id: "session-1",
    turn_id: "host-resumed-turn",
    last_assistant_message: "只修改了普通验证文档",
  }, { env }), { continue: true });
});

test("a missing exact marker cannot reuse another session baseline", async (t) => {
  const { root, env } = await workspace(t);
  await initialize(root);
  await handleUserPromptSubmit(promptEvent(root), { env });

  const result = await handleStop({
    cwd: root,
    session_id: "session-2",
    turn_id: "host-resumed-turn",
  }, { env });
  assert.equal(result.decision, "block");
  assert.match(result.reason, /没有可验证的同 session 基线/);
});

test("a missing exact marker fails closed when state changed after the same-session baseline", async (t) => {
  const { root, env } = await workspace(t);
  await initialize(root);
  await handleUserPromptSubmit(promptEvent(root), { env });
  await commitProjectState(root, {
    operation: "ADVANCE_PLAN", expectedRevision: 0, authorizationRef,
    mutate(current) {
      current.plan.next_action = "实现垂直切片";
      current.last_change = {
        operation: "ADVANCE_PLAN", changed_at: "2026-09-29T08:02:00.000Z", summary: "推进",
      };
      return current;
    },
  });

  const result = await handleStop({
    cwd: root,
    session_id: "session-1",
    turn_id: "host-resumed-turn",
    last_assistant_message: "已完成",
  }, { env });
  assert.equal(result.decision, "block");
  assert.match(result.reason, /同 session 基线 revision 不匹配/);
});

test("a missing exact marker requires the same baseline receipt id even at the same revision", async (t) => {
  const { root, codexHome, env } = await workspace(t);
  await initialize(root);
  await handleUserPromptSubmit(promptEvent(root), { env });
  const runtimeDataRoot = path.join(codexHome, "project-incubator-plugin", "runtime-events");
  const markerPath = turnMarkerPath(runtimeDataRoot, "project-1", "session-1", "turn-1");
  const marker = JSON.parse(await readFile(markerPath, "utf8"));
  await writeFile(markerPath, `${JSON.stringify({
    ...marker, baseline_receipt_id: "receipt-from-another-baseline",
  })}\n`, "utf8");

  const result = await handleStop({
    cwd: root,
    session_id: "session-1",
    turn_id: "host-resumed-turn",
  }, { env });
  assert.equal(result.decision, "block");
  assert.match(result.reason, /同 session 基线 Receipt 不匹配/);
});

test("Stop never blocks twice when a previous Stop already continued the turn", async (t) => {
  const { root } = await workspace(t);
  await initialize(root);
  const result = await handleStop({
    cwd: root,
    session_id: "session-1",
    turn_id: "turn-1",
    stop_hook_active: true,
    last_assistant_message: "再次尝试结束",
  }, { env: {} });
  assert.equal(result.continue, true);
  assert.match(result.systemMessage, /RUNTIME_DATA_ROOT_REQUIRED/);
});

test("a changed state requires the current verified receipt in the final message", async (t) => {
  const { root, env } = await workspace(t);
  await initialize(root);
  await handleUserPromptSubmit(promptEvent(root), { env });
  const receipt = await commitProjectState(root, {
    operation: "ADVANCE_PLAN", expectedRevision: 0, authorizationRef,
    mutate(current) {
      current.plan.next_action = "实现垂直切片";
      current.last_change = { operation: "ADVANCE_PLAN", changed_at: "2026-09-29T08:02:00.000Z", summary: "推进" };
      return current;
    },
  });
  const blocked = await handleStop({
    cwd: root, session_id: "session-1", turn_id: "turn-1", last_assistant_message: "已完成",
  }, { env });
  assert.equal(blocked.decision, "block");
  const allowed = await handleStop({
    cwd: root, session_id: "session-1", turn_id: "turn-1",
    last_assistant_message: `已完成，receipt_id: ${receipt.receipt_id}`,
  }, { env });
  assert.deepEqual(allowed, { continue: true });
});

test("prepared change supplies a copyable approval and Stop checks this turn's request", async (t) => {
  const { root, codexHome, env } = await workspace(t);
  await initialize(root);
  await handleUserPromptSubmit(promptEvent(root, { prompt: "请准备下一步变更" }), { env });
  const runtimeDataRoot = path.join(codexHome, "project-incubator-plugin", "runtime-events");
  const service = await createKernelService({
    pluginRoot: path.resolve(import.meta.dirname, "../.."), runtimeDataRoot,
  });
  const snapshot = (await service.callTool("get_project_state", { project_root: root })).structuredContent;
  const proposedState = structuredClone(snapshot.state);
  proposedState.plan.next_action = "准备风险建模";
  const preparedResult = await service.callTool("prepare_change", {
    project_root: root, operation: "ADVANCE_PLAN", change_kind: "PRODUCT_DECISION",
    session_id: "session-1", proposed_state: proposedState,
  });
  assert.equal(preparedResult.isError, undefined);
  const prepared = preparedResult.structuredContent;
  const expectedApproval = `我明确批准变更请求 ${prepared.request_id}，scope_digest: ${prepared.scope_digest}。`;
  assert.equal(prepared.approval_message, expectedApproval);
  assert.equal(prepared.receipt.operation, "PREPARE_CHANGE");
  const latest = (await service.callTool("get_project_state", { project_root: root })).structuredContent;
  const pending = latest.state.pending_requests.find((item) => item.request_id === prepared.request_id);
  assert.equal(pending.scope_digest, prepared.scope_digest);
  assert.equal(pending.project_revision, latest.state.revision);

  const receipt = `receipt_id: ${prepared.receipt.receipt_id}`;
  const stop = (message, extra = {}) => handleStop({
    cwd: root, session_id: "session-1", turn_id: "turn-1",
    last_assistant_message: message, ...extra,
  }, { env });
  const cases = [
    { message: receipt, missing: /request_id/u },
    { message: `request-wrong\nscope_digest: ${prepared.scope_digest}\n${receipt}`, missing: /request_id/u },
    { message: `${prepared.request_id}\n${receipt}`, missing: /scope_digest/u },
    { message: `${prepared.request_id}\nscope_digest: ${"a".repeat(64)}\n${receipt}`, missing: /scope_digest/u },
    { message: `${prepared.request_id}\nscope_digest: ${prepared.scope_digest}\n${receipt}`, missing: /批准句/u },
    { message: expectedApproval, missing: /receipt_id/u },
  ];
  for (const { message, missing } of cases) {
    const result = await stop(message);
    assert.equal(result.decision, "block");
    assert.match(result.reason, missing);
  }
  assert.deepEqual(await stop(`${expectedApproval}\n${receipt}`), { continue: true });

  const continued = await stop(receipt, { stop_hook_active: true });
  assert.equal(continued.continue, true);
  assert.match(continued.systemMessage, /request_id/u);
  assert.match(continued.systemMessage, new RegExp(prepared.request_id, "u"));
  assert.match(continued.systemMessage, new RegExp(prepared.scope_digest, "u"));

  const hostResumed = await stop(receipt, {
    turn_id: "host-resumed-turn", stop_hook_active: true,
  });
  assert.equal(hostResumed.continue, true);
  assert.match(hostResumed.systemMessage, /轮次 marker 缺失/u);
  assert.match(hostResumed.systemMessage, new RegExp(prepared.request_id, "u"));
  assert.match(hostResumed.systemMessage, new RegExp(prepared.scope_digest, "u"));

  await handleUserPromptSubmit(promptEvent(root, {
    turn_id: "turn-2", prompt: "只查询已有待批准请求",
  }), { env });
  assert.deepEqual(await handleStop({
    cwd: root, session_id: "session-1", turn_id: "turn-2", last_assistant_message: "当前仍有待批准请求。",
  }, { env }), { continue: true });
});

test("Stop blocks hash mismatch, revision mismatch, and receipts older than the turn", async (t) => {
  const { root, env } = await workspace(t);
  await initialize(root);
  await handleUserPromptSubmit(promptEvent(root), { env });
  const receiptPath = path.join(root, ".project-incubator", "latest-receipt.json");
  const statePath = path.join(root, ".project-incubator", "state.json");
  const originalState = JSON.parse(await readFile(statePath, "utf8"));
  const originalReceipt = JSON.parse(await readFile(receiptPath, "utf8"));

  await writeFile(statePath, `${JSON.stringify({ ...originalState, revision: 1 })}\n`);
  let result = await handleStop({ cwd: root, session_id: "session-1", turn_id: "turn-1" }, { env });
  assert.equal(result.decision, "block");

  await writeFile(statePath, `${JSON.stringify(originalState)}\n`);
  await writeFile(receiptPath, `${JSON.stringify({ ...originalReceipt, new_revision: 9 })}\n`);
  result = await handleStop({ cwd: root, session_id: "session-1", turn_id: "turn-1" }, { env });
  assert.equal(result.decision, "block");

  const staleChangedState = { ...originalState, revision: 1 };
  const staleReceipt = {
    ...originalReceipt, previous_revision: 0, new_revision: 1,
    previous_state_hash: originalReceipt.new_state_hash,
    committed_at: "2026-09-29T07:59:00.000Z",
  };
  await writeFile(statePath, `${JSON.stringify(staleChangedState)}\n`);
  await writeFile(receiptPath, `${JSON.stringify(staleReceipt)}\n`);
  result = await handleStop({ cwd: root, session_id: "session-1", turn_id: "turn-1" }, { env });
  assert.equal(result.decision, "block");
});
