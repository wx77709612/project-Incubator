import assert from "node:assert/strict";
import { access, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { handleUserPromptSubmit } from "../../hooks/user-prompt-submit.mjs";
import { createKernelService } from "../../src/server.mjs";
import { initializeProjectState } from "../../src/kernel/state-store.mjs";

const now = "2026-09-29T10:00:00.000Z";
const authorizationRef = {
  authorization_id: "authorization-1", request_id: "request-1", prompt_digest: "b".repeat(64),
};

function activation() {
  return {
    schema_version: "1.0", project_id: "project-1", plugin_id: "project-incubator-plugin",
    plugin_version: "0.1.0", status: "ACTIVE", project_type_id: "mod",
    child_skill_id: "mod-incubator", host_profile_id: null,
  };
}

function state() {
  return {
    schema_version: "1.0", project_id: "project-1", revision: 0,
    boundary: { objective: "验证状态摘要", supported: ["只读查询"], excluded: [] },
    workflow: { stage: "M0_BOUNDARY", status: "ACTIVE", completed: [], allowed_next: ["M1_RISK_MODEL"] },
    capabilities: [], decisions: { active: [], archive_ref: null }, assumptions: [],
    plan: { current_action: "确认边界", next_action: "风险建模", completion_conditions: ["Maker 确认"] },
    gates: [], risks: [], pending_requests: [], baselines: [],
    human_validation: { limit: "UNSET", consumed: 0 },
    last_change: { operation: "INITIALIZE_PROJECT", changed_at: now, summary: "初始化" },
    archive_refs: [],
  };
}

async function fixture(t) {
  const projectRoot = await mkdtemp(path.join(os.tmpdir(), "incubator-inspect-project-"));
  const runtimeDataRoot = await mkdtemp(path.join(os.tmpdir(), "incubator-inspect-runtime-"));
  t.after(() => rm(projectRoot, { recursive: true, force: true }));
  t.after(() => rm(runtimeDataRoot, { recursive: true, force: true }));
  await initializeProjectState(projectRoot, activation(), state(), authorizationRef);
  return {
    projectRoot, runtimeDataRoot,
    service: await createKernelService({
      pluginRoot: path.resolve(import.meta.dirname, "../.."), runtimeDataRoot,
    }),
  };
}

async function authorityBytes(root) {
  return Promise.all(["activation.json", "state.json", "latest-receipt.json"].map(
    (name) => readFile(path.join(root, ".project-incubator", name), "utf8"),
  ));
}

test("inspect_project is verified, deterministic and strictly read-only", async (t) => {
  const { projectRoot, service } = await fixture(t);
  const before = await authorityBytes(projectRoot);
  const first = await service.callTool("inspect_project", { project_root: projectRoot });
  const second = await service.callTool("inspect_project", { project_root: projectRoot });
  assert.equal(first.isError, undefined);
  assert.deepEqual(first.structuredContent, second.structuredContent);
  assert.deepEqual(await authorityBytes(projectRoot), before);
  await assert.rejects(() => access(path.join(projectRoot, "PROJECT_OVERVIEW.md")), /ENOENT/);
  assert.equal(first.structuredContent.summary.human_validation.limit, "UNSET");
  assert.deepEqual(first.structuredContent.summary.baselines, []);
});

test("malformed state and inconsistent receipts are reported as unverifiable", async (t) => {
  const { projectRoot, service } = await fixture(t);
  const statePath = path.join(projectRoot, ".project-incubator", "state.json");
  await writeFile(statePath, "{broken");
  let result = await service.callTool("inspect_project", { project_root: projectRoot });
  assert.equal(result.isError, true);
  assert.equal(result.structuredContent.error.code, "STATE_INVALID_JSON");

  const other = await fixture(t);
  const receiptPath = path.join(other.projectRoot, ".project-incubator", "latest-receipt.json");
  const receipt = JSON.parse(await readFile(receiptPath, "utf8"));
  receipt.new_state_hash = "0".repeat(64);
  await writeFile(receiptPath, JSON.stringify(receipt));
  result = await other.service.callTool("inspect_project", { project_root: other.projectRoot });
  assert.equal(result.isError, true);
  assert.equal(result.structuredContent.error.code, "RECEIPT_UNVERIFIABLE");
});

test("overview export requires an explicit same-turn Maker prompt", async (t) => {
  const { projectRoot, runtimeDataRoot, service } = await fixture(t);
  let result = await service.callTool("export_project_overview", {
    project_root: projectRoot, session_id: "session-1", turn_id: "turn-1",
  });
  assert.equal(result.isError, true);
  assert.equal(result.structuredContent.error.code, "PROMPT_NOT_FOUND");

  await handleUserPromptSubmit({
    cwd: projectRoot, session_id: "session-1", turn_id: "turn-1", timestamp: now,
    prompt: "请在本轮明确导出项目状态概览。",
  }, { runtimeDataRoot, now: new Date(now) });
  const before = await authorityBytes(projectRoot);
  result = await service.callTool("export_project_overview", {
    project_root: projectRoot, session_id: "session-1", turn_id: "turn-1",
  }, { now: new Date(now) });
  assert.equal(result.isError, undefined);
  assert.deepEqual(await authorityBytes(projectRoot), before);
  const overview = await readFile(path.join(projectRoot, "PROJECT_OVERVIEW.md"), "utf8");
  assert.match(overview, /非权威、可重建的人读视图/);
});

test("Router Skill binds status questions to inspect_project", async () => {
  const skill = await readFile(path.resolve(import.meta.dirname, "../../skills/project-incubator-router/SKILL.md"), "utf8");
  for (const phrase of ["项目状态", "进度", "下一步", "阻塞", "需要我决定什么"]) {
    assert.ok(skill.includes(phrase), `缺少触发语义：${phrase}`);
  }
  assert.match(skill, /inspect_project/);
  assert.match(skill, /不得.*聊天.*补全/);
});

test("三种 Child 恢复对 Receipt hash、revision 和引用篡改均失败关闭", async (t) => {
  for (const [type, child, host] of [["mod", "mod-incubator", "sims-4"], ["desktop-product", "desktop-product-incubator", "windows-desktop"], ["web-product", "web-product-incubator", null]]) {
    for (const field of ["hash", "revision", "reference"]) {
      await t.test(`${type}/${field}`, async (t) => {
        const projectRoot = await mkdtemp(path.join(os.tmpdir(), "alignment-resume-"));
        const runtimeDataRoot = await mkdtemp(path.join(os.tmpdir(), "alignment-resume-events-"));
        t.after(() => rm(projectRoot, { recursive: true, force: true }));
        t.after(() => rm(runtimeDataRoot, { recursive: true, force: true }));
        const stage = type === "mod" ? "M0_BOUNDARY" : "P0";
        const initial = state();
        initial.schema_version = "1.1";
        initial.workflow = { stage, status: "ACTIVE", completed: [], allowed_next: [type === "mod" ? "M1_RISK_MODEL" : "P1"], return_stage: null,
          entry: { mode: "NEW_PROJECT", initial_stage: stage, assessment_summary: "临时恢复验证夹具", evidence_refs: [], assessed_at: now } };
        await initializeProjectState(projectRoot, { ...activation(), plugin_version: "0.3.0", project_type_id: type, child_skill_id: child, host_profile_id: host }, initial, authorizationRef);
        const service = await createKernelService({ pluginRoot: path.resolve(import.meta.dirname, "../.."), runtimeDataRoot });
        assert.equal((await service.callTool("inspect_project", { project_root: projectRoot })).isError, undefined);
        const target = path.join(projectRoot, ".project-incubator/latest-receipt.json");
        const receipt = JSON.parse(await readFile(target, "utf8"));
        if (field === "hash") receipt.new_state_hash = "0".repeat(64);
        if (field === "revision") receipt.new_revision += 1;
        if (field === "reference") receipt.receipt_id = "receipt-unrelated";
        await writeFile(target, JSON.stringify(receipt));
        const before = await authorityBytes(projectRoot);
        assert.equal((await service.callTool("get_project_state", { project_root: projectRoot })).isError, undefined, "低层 Snapshot 不验证闭合，不能作为恢复替代");
        const result = await service.callTool("inspect_project", { project_root: projectRoot });
        assert.equal(result.isError, true);
        assert.equal(result.structuredContent.error.code, "RECEIPT_UNVERIFIABLE");
        assert.deepEqual(await authorityBytes(projectRoot), before, "查询失败也不得修改状态");
      });
    }
  }
});
