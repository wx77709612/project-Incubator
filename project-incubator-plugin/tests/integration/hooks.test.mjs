import assert from "node:assert/strict";
import { access, mkdtemp, readFile, rm, symlink, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { handlePreToolUse } from "../../hooks/pre-tool-use.mjs";
import { handleStop } from "../../hooks/stop.mjs";
import { handleUserPromptSubmit } from "../../hooks/user-prompt-submit.mjs";
import { commitProjectState, initializeProjectState } from "../../src/kernel/state-store.mjs";

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
