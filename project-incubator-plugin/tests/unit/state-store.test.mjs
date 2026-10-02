import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import {
  commitProjectState,
  createStateStore,
  initializeProjectState,
  readProjectSnapshot,
} from "../../src/kernel/state-store.mjs";

const now = "2026-09-29T00:00:00.000Z";
const authorizationRef = {
  authorization_id: "authorization-1",
  request_id: "request-1",
  prompt_digest: "b".repeat(64),
};

function activation() {
  return {
    schema_version: "1.0", project_id: "project-1",
    plugin_id: "project-incubator-plugin", plugin_version: "0.1.0", status: "ACTIVE",
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

async function projectRoot(t) {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-store-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  return root;
}

test("initialization is the only path that creates revision zero", async (t) => {
  const root = await projectRoot(t);
  const receipt = await initializeProjectState(root, activation(), state(), authorizationRef);
  const snapshot = await readProjectSnapshot(root);
  assert.equal(receipt.new_revision, 0);
  assert.equal(snapshot.state.revision, 0);
  await assert.rejects(() => initializeProjectState(root, activation(), state(), authorizationRef));
});

test("commit increments revision and rejects stale expected revision", async (t) => {
  const root = await projectRoot(t);
  await initializeProjectState(root, activation(), state(), authorizationRef);
  const receipt = await commitProjectState(root, {
    operation: "ADVANCE_PLAN", expectedRevision: 0, authorizationRef,
    mutate(current) {
      current.plan.next_action = "构建垂直切片";
      current.last_change = { operation: "ADVANCE_PLAN", changed_at: now, summary: "更新计划" };
      return current;
    },
  });
  assert.equal(receipt.new_revision, 1);
  await assert.rejects(
    () => commitProjectState(root, {
      operation: "STALE", expectedRevision: 0, authorizationRef, mutate: (current) => current,
    }),
    /REVISION_CONFLICT/,
  );
});

test("corrupt authority fails closed", async (t) => {
  const root = await projectRoot(t);
  await initializeProjectState(root, activation(), state(), authorizationRef);
  await writeFile(path.join(root, ".project-incubator", "state.json"), "{broken");
  await assert.rejects(() => readProjectSnapshot(root));
  await assert.rejects(() => commitProjectState(root, {
    operation: "NOPE", expectedRevision: 0, authorizationRef, mutate: (current) => current,
  }));
});

test("receipt write failure restores the previous state and receipt", async (t) => {
  const root = await projectRoot(t);
  await initializeProjectState(root, activation(), state(), authorizationRef);
  const beforeState = await readFile(path.join(root, ".project-incubator", "state.json"), "utf8");
  const beforeReceipt = await readFile(path.join(root, ".project-incubator", "latest-receipt.json"), "utf8");
  const store = createStateStore({
    beforeAtomicWrite(target) {
      if (target.endsWith("latest-receipt.json")) throw new Error("injected receipt failure");
    },
  });
  await assert.rejects(() => store.commitProjectState(root, {
    operation: "FAIL_RECEIPT", expectedRevision: 0, authorizationRef,
    mutate(current) {
      current.plan.next_action = "不应保留";
      current.last_change = { operation: "FAIL_RECEIPT", changed_at: now, summary: "失败" };
      return current;
    },
  }), /injected receipt failure/);
  assert.equal(await readFile(path.join(root, ".project-incubator", "state.json"), "utf8"), beforeState);
  assert.equal(await readFile(path.join(root, ".project-incubator", "latest-receipt.json"), "utf8"), beforeReceipt);
});

test("read-back mismatch rolls back the transaction", async (t) => {
  const root = await projectRoot(t);
  await initializeProjectState(root, activation(), state(), authorizationRef);
  const store = createStateStore({ corruptStateReadback: true });
  await assert.rejects(() => store.commitProjectState(root, {
    operation: "MISMATCH", expectedRevision: 0, authorizationRef,
    mutate(current) {
      current.last_change = { operation: "MISMATCH", changed_at: now, summary: "失败" };
      return current;
    },
  }), /STATE_READBACK_MISMATCH/);
  assert.equal((await readProjectSnapshot(root)).state.revision, 0);
});

test("concurrent commits cannot both consume the same revision", async (t) => {
  const root = await projectRoot(t);
  await initializeProjectState(root, activation(), state(), authorizationRef);
  const request = (operation) => commitProjectState(root, {
    operation, expectedRevision: 0, authorizationRef,
    mutate(current) {
      current.last_change = { operation, changed_at: now, summary: operation };
      return current;
    },
  });
  const results = await Promise.allSettled([request("FIRST"), request("SECOND")]);
  assert.equal(results.filter((item) => item.status === "fulfilled").length, 1);
  assert.equal(results.filter((item) => item.status === "rejected").length, 1);
  assert.equal((await readProjectSnapshot(root)).state.revision, 1);
});
