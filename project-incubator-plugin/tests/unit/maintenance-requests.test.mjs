import assert from "node:assert/strict";
import { mkdtemp, readdir, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import {
  consumeMaintenanceRequest,
  getMaintenanceRequest,
  prepareMaintenanceRequest,
} from "../../src/kernel/maintenance-requests.mjs";
import { canonicalProjectPath } from "../../src/kernel/project-root.mjs";

const now = new Date("2026-10-23T00:00:00.000Z");

async function fixture(t) {
  const projectRoot = await mkdtemp(path.join(os.tmpdir(), "incubator-maintenance-project-"));
  const runtimeDataRoot = await mkdtemp(path.join(os.tmpdir(), "incubator-maintenance-runtime-"));
  t.after(() => rm(projectRoot, { recursive: true, force: true }));
  t.after(() => rm(runtimeDataRoot, { recursive: true, force: true }));
  return { projectRoot, runtimeDataRoot };
}

test("maintenance requests bind operation, canonical project, session, payload, and 24-hour expiry", async (t) => {
  const { projectRoot, runtimeDataRoot } = await fixture(t);
  const request = await prepareMaintenanceRequest({
    runtimeDataRoot,
    projectRoot: path.join(projectRoot, "."),
    sessionId: "session-1",
    operation: "AGENT_ENTRY_INSTALL",
    requestPrefix: "request",
    payload: { template_sha256: "a".repeat(64) },
    now,
  });

  assert.match(request.request_id, /^request-/);
  assert.match(request.scope_digest, /^[a-f0-9]{64}$/);
  assert.equal(request.project_root, await canonicalProjectPath(projectRoot));
  assert.equal(request.session_id, "session-1");
  assert.equal(request.expires_at, "2026-10-24T00:00:00.000Z");

  const loaded = await getMaintenanceRequest({
    runtimeDataRoot, projectRoot, requestId: request.request_id,
    scopeDigest: request.scope_digest, sessionId: "session-1",
    operation: "AGENT_ENTRY_INSTALL", now,
  });
  assert.deepEqual(loaded.payload, { template_sha256: "a".repeat(64) });
});

test("maintenance lookup fails closed for wrong request, scope, session, operation, and expiry", async (t) => {
  const { projectRoot, runtimeDataRoot } = await fixture(t);
  const request = await prepareMaintenanceRequest({
    runtimeDataRoot, projectRoot, sessionId: "session-1",
    operation: "AGENT_ENTRY_INSTALL", requestPrefix: "request",
    payload: { template_sha256: "b".repeat(64) }, now,
  });
  const base = {
    runtimeDataRoot, projectRoot, requestId: request.request_id,
    scopeDigest: request.scope_digest, sessionId: "session-1",
    operation: "AGENT_ENTRY_INSTALL", now,
  };

  await assert.rejects(
    () => getMaintenanceRequest({ ...base, requestId: "request-unknown" }),
    /AGENT_ENTRY_REQUEST_NOT_FOUND/,
  );
  await assert.rejects(
    () => getMaintenanceRequest({ ...base, scopeDigest: "0".repeat(64) }),
    /SCOPE_DIGEST_MISMATCH/,
  );
  await assert.rejects(
    () => getMaintenanceRequest({ ...base, sessionId: "session-2" }),
    /PROMPT_CONTEXT_MISMATCH/,
  );
  await assert.rejects(
    () => getMaintenanceRequest({ ...base, operation: "AUTHORITY_RECOVERY" }),
    /AUTHORITY_RECOVERY_REQUEST_NOT_FOUND/,
  );
  await assert.rejects(
    () => getMaintenanceRequest({ ...base, now: new Date("2026-10-24T00:00:00.001Z") }),
    /AGENT_ENTRY_REQUEST_EXPIRED/,
  );
});

test("a maintenance request is consumed only when explicitly completed", async (t) => {
  const { projectRoot, runtimeDataRoot } = await fixture(t);
  const request = await prepareMaintenanceRequest({
    runtimeDataRoot, projectRoot, sessionId: "session-1",
    operation: "AGENT_ENTRY_INSTALL", requestPrefix: "request", payload: {}, now,
  });
  await consumeMaintenanceRequest(request);
  assert.deepEqual(await readdir(runtimeDataRoot), []);
  await assert.rejects(() => getMaintenanceRequest({
    runtimeDataRoot, projectRoot, requestId: request.request_id,
    scopeDigest: request.scope_digest, sessionId: "session-1",
    operation: "AGENT_ENTRY_INSTALL", now,
  }), /AGENT_ENTRY_REQUEST_NOT_FOUND/);
});
