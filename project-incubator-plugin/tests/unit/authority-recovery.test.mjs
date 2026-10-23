import assert from "node:assert/strict";
import { mkdtemp, mkdir, readFile, rm, unlink, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import {
  diagnoseAuthority,
  normalizeRecoveryCandidate,
  recoverProjectAuthority,
} from "../../src/kernel/authority-recovery.mjs";
import {
  initializeProjectState,
  readProjectSnapshot,
  verifyLatestReceipt,
} from "../../src/kernel/state-store.mjs";

const now = new Date("2026-10-23T03:00:00.000Z");
const authorizationRef = {
  authorization_id: "authorization-recovery",
  request_id: "recovery-1",
  prompt_digest: "c".repeat(64),
};

function activation() {
  return {
    schema_version: "1.0", project_id: "project-1",
    plugin_id: "project-incubator-plugin", plugin_version: "0.3.0", status: "ACTIVE",
    project_type_id: "mod", child_skill_id: "mod-incubator", host_profile_id: "sims-4",
  };
}

function state(revision = 0) {
  return {
    schema_version: "1.0", project_id: "project-1", revision,
    boundary: { objective: "恢复项目", supported: ["权威恢复"], excluded: [] },
    workflow: { stage: "M0_BOUNDARY", status: "ACTIVE", completed: [], allowed_next: ["M1_RISK_MODEL"] },
    capabilities: [], decisions: { active: [], archive_ref: null }, assumptions: [],
    plan: { current_action: "恢复权威", next_action: "继续孵化", completion_conditions: ["恢复验证"] },
    gates: [], risks: [], pending_requests: [], baselines: [],
    human_validation: { limit: "UNSET", consumed: 0 },
    last_change: { operation: "RECOVERY_DRAFT", changed_at: now.toISOString(), summary: "恢复候选" },
    archive_refs: [],
  };
}

async function projectRoot(t) {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-authority-recovery-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  return root;
}

function item(diagnostics, name) {
  return diagnostics.items.find((entry) => entry.path.endsWith(name));
}

test("diagnosis reports every missing or invalid authority file with raw-byte fingerprints", async (t) => {
  const root = await projectRoot(t);
  let diagnostics = await diagnoseAuthority(root);
  assert.equal(diagnostics.snapshot_valid, false);
  assert.deepEqual(diagnostics.items.map((entry) => entry.status), ["MISSING", "MISSING", "MISSING"]);
  assert.deepEqual(Object.values(diagnostics.fingerprints), [
    { exists: false }, { exists: false }, { exists: false },
  ]);

  const control = path.join(root, ".project-incubator");
  await mkdir(control);
  for (const name of ["activation.json", "state.json", "latest-receipt.json"]) {
    await writeFile(path.join(control, name), `{broken-${name}`);
  }
  diagnostics = await diagnoseAuthority(root);
  for (const entry of diagnostics.items) {
    assert.equal(entry.status, "INVALID");
    assert.match(entry.sha256, /^[a-f0-9]{64}$/);
    assert.match(entry.error_code, /_INVALID_JSON$/);
  }
});

test("a complete verified authority set is not eligible for recovery", async (t) => {
  const root = await projectRoot(t);
  await initializeProjectState(root, activation(), state(), authorizationRef);
  const diagnostics = await diagnoseAuthority(root);
  assert.equal(diagnostics.snapshot_valid, true);
  assert.deepEqual(diagnostics.items.map((entry) => entry.status), ["VALID", "VALID", "VALID"]);
  assert.throws(
    () => normalizeRecoveryCandidate(diagnostics, activation(), state(1), now),
    /AUTHORITY_RECOVERY_NOT_REQUIRED/,
  );
});

test("normalization continues a valid old State, clears pending requests, and enforces next revision", async (t) => {
  const root = await projectRoot(t);
  await initializeProjectState(root, activation(), state(), authorizationRef);
  const receiptPath = path.join(root, ".project-incubator", "latest-receipt.json");
  const receipt = JSON.parse(await readFile(receiptPath, "utf8"));
  receipt.new_state_hash = "0".repeat(64);
  await writeFile(receiptPath, JSON.stringify(receipt));
  const diagnostics = await diagnoseAuthority(root);
  const proposed = state(1);
  proposed.pending_requests = [{
    request_id: "request-old", operation: "OLD", scope_digest: "d".repeat(64),
    status: "PENDING", created_at: now.toISOString(), project_revision: 1,
  }];
  const candidate = normalizeRecoveryCandidate(diagnostics, activation(), proposed, now);

  assert.equal(candidate.baseline, "CONTINUED");
  assert.equal(candidate.previous_state.revision, 0);
  assert.equal(candidate.state.revision, 1);
  assert.deepEqual(candidate.state.pending_requests, []);
  assert.equal(candidate.state.last_change.operation, "RECOVER_PROJECT_AUTHORITY");
  assert.equal(candidate.state.last_change.changed_at, now.toISOString());
  assert.throws(
    () => normalizeRecoveryCandidate(diagnostics, activation(), state(0), now),
    /RECOVERY_STATE_REVISION_INVALID/,
  );
});

test("normalization establishes revision zero when no valid old State exists", async (t) => {
  const root = await projectRoot(t);
  const control = path.join(root, ".project-incubator");
  await mkdir(control);
  await writeFile(path.join(control, "state.json"), "{broken");
  const diagnostics = await diagnoseAuthority(root);
  const candidate = normalizeRecoveryCandidate(diagnostics, activation(), state(0), now);
  assert.equal(candidate.baseline, "REESTABLISHED");
  assert.equal(candidate.previous_state, null);
  assert.equal(candidate.state.revision, 0);
  assert.throws(
    () => normalizeRecoveryCandidate(diagnostics, activation(), state(1), now),
    /RECOVERY_STATE_REVISION_INVALID/,
  );
});

test("recovery writes and verifies a new Receipt for continued and reestablished baselines", async (t) => {
  const continuedRoot = await projectRoot(t);
  await initializeProjectState(continuedRoot, activation(), state(), authorizationRef);
  const receiptPath = path.join(continuedRoot, ".project-incubator", "latest-receipt.json");
  const receipt = JSON.parse(await readFile(receiptPath, "utf8"));
  receipt.new_revision += 1;
  await writeFile(receiptPath, JSON.stringify(receipt));
  let diagnostics = await diagnoseAuthority(continuedRoot);
  let result = await recoverProjectAuthority(
    continuedRoot,
    normalizeRecoveryCandidate(diagnostics, activation(), state(1), now),
    diagnostics.fingerprints,
    authorizationRef,
  );
  assert.equal(result.recovery.baseline, "CONTINUED");
  assert.equal(result.receipt.operation, "RECOVER_PROJECT_AUTHORITY");
  assert.equal((await readProjectSnapshot(continuedRoot)).state.revision, 1);
  assert.equal((await verifyLatestReceipt(continuedRoot, result.receipt.receipt_id)).verified, true);

  const reestablishedRoot = await projectRoot(t);
  diagnostics = await diagnoseAuthority(reestablishedRoot);
  result = await recoverProjectAuthority(
    reestablishedRoot,
    normalizeRecoveryCandidate(diagnostics, activation(), state(0), now),
    diagnostics.fingerprints,
    authorizationRef,
  );
  assert.equal(result.recovery.baseline, "REESTABLISHED");
  assert.equal((await readProjectSnapshot(reestablishedRoot)).state.revision, 0);
  assert.equal((await verifyLatestReceipt(reestablishedRoot, result.receipt.receipt_id)).verified, true);
});

test("recovery rejects any source fingerprint change before writing", async (t) => {
  const root = await projectRoot(t);
  const diagnostics = await diagnoseAuthority(root);
  const control = path.join(root, ".project-incubator");
  await mkdir(control);
  await writeFile(path.join(control, "activation.json"), "{}\n");
  await assert.rejects(
    () => recoverProjectAuthority(
      root,
      normalizeRecoveryCandidate(diagnostics, activation(), state(0), now),
      diagnostics.fingerprints,
      authorizationRef,
    ),
    /RECOVERY_SOURCE_CHANGED/,
  );
  await unlink(path.join(control, "activation.json"));
});
