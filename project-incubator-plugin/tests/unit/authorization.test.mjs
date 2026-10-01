import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, utimes, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import {
  authorizePreparedChange,
  authorizePreparedDecline,
  prepareChange,
} from "../../src/kernel/authorization.mjs";
import { recordMakerPrompt } from "../../src/kernel/prompt-events.mjs";

const scopeDigest = "a".repeat(64);
const now = "2026-09-29T08:00:00.000Z";

function snapshot(overrides = {}) {
  return {
    activation: { status: "ACTIVE", project_id: "project-1" },
    state: {
      project_id: "project-1", revision: 4,
      pending_requests: [{
        request_id: "request-1", operation: "ADD_PRODUCT_DECISION",
        scope_digest: scopeDigest, status: "PENDING", created_at: now,
        project_revision: 4,
      }],
      ...overrides,
    },
  };
}

function proposal(overrides = {}) {
  return {
    request_id: "request-1", scope_digest: scopeDigest,
    operation: "ADD_PRODUCT_DECISION", change_kind: "PRODUCT_DECISION",
    project_id: "project-1", session_id: "session-1", turn_id: "turn-2",
    ...overrides,
  };
}

function activeEvent(text, overrides = {}) {
  return {
    activation: {
      schema_version: "1.0", project_id: "project-1",
      plugin_id: "project-incubator-plugin", plugin_version: "0.1.0",
      status: "ACTIVE", project_type_id: "mod", child_skill_id: "mod-incubator",
      host_profile_id: "sims-4",
    },
    role: "maker", project_id: "project-1", session_id: "session-1", turn_id: "turn-2",
    text, captured_at: now, ...overrides,
  };
}

async function runtimeRoot(t) {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-auth-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  return root;
}

test("prepareChange requires an exact pending request and scope", () => {
  assert.throws(() => prepareChange(snapshot(), proposal({ request_id: undefined })), /REQUEST_ID_REQUIRED/);
  assert.throws(() => prepareChange(snapshot(), proposal({ scope_digest: "b".repeat(64) })), /SCOPE_DIGEST_MISMATCH/);
  assert.throws(() => prepareChange(snapshot({ pending_requests: [] }), proposal()), /PENDING_REQUEST_NOT_FOUND/);
});

test("authorization is bound to the same project, session and turn", async (t) => {
  const root = await runtimeRoot(t);
  const prepared = prepareChange(snapshot(), proposal());
  await assert.rejects(
    () => recordMakerPrompt(activeEvent(
      `我明确批准 request-1，scope_digest: ${scopeDigest}`,
      { project_id: "project-2" },
    ), root),
    /PROMPT_PROJECT_MISMATCH/,
  );
  const otherProject = await recordMakerPrompt(activeEvent(
    `我明确批准 request-1，scope_digest: ${scopeDigest}`,
    {
      project_id: "project-2",
      activation: { ...activeEvent("x").activation, project_id: "project-2" },
    },
  ), root);
  await assert.rejects(
    () => authorizePreparedChange(prepared, otherProject),
    /PROMPT_CONTEXT_MISMATCH/,
  );
  for (const mismatch of [{ session_id: "session-2" }, { turn_id: "turn-3" }]) {
    const ref = await recordMakerPrompt(activeEvent(
      `我明确批准 request-1，scope_digest: ${scopeDigest}`,
      mismatch,
    ), root);
    await assert.rejects(() => authorizePreparedChange(prepared, ref), /PROMPT_CONTEXT_MISMATCH/);
  }
});

test("agent text and ambiguous Maker text cannot authorize", async (t) => {
  const root = await runtimeRoot(t);
  const prepared = prepareChange(snapshot(), proposal());
  await assert.rejects(
    () => recordMakerPrompt(activeEvent(`我明确批准 request-1，scope_digest: ${scopeDigest}`, { role: "agent" }), root),
    /MAKER_PROMPT_REQUIRED/,
  );
  const ambiguous = await recordMakerPrompt(activeEvent(`request-1 看起来可以，scope_digest: ${scopeDigest}`), root);
  await assert.rejects(
    () => authorizePreparedChange(prepared, ambiguous, { now: new Date(now) }),
    /EXPLICIT_APPROVAL_REQUIRED/,
  );
});

test("authorization rejects expired prompts and cannot be consumed twice", async (t) => {
  const root = await runtimeRoot(t);
  const prepared = prepareChange(snapshot(), proposal());
  const expired = await recordMakerPrompt(activeEvent(
    `我明确批准 request-1，scope_digest: ${scopeDigest}`,
    { captured_at: "2026-09-28T07:59:59.000Z" },
  ), root);
  await assert.rejects(
    () => authorizePreparedChange(prepared, expired, { now: new Date(now) }),
    /PROMPT_EXPIRED/,
  );

  const fresh = await recordMakerPrompt(activeEvent(`我明确批准 request-1，scope_digest: ${scopeDigest}`), root);
  const authorization = await authorizePreparedChange(prepared, fresh, { now: new Date(now) });
  assert.equal(authorization.request_id, "request-1");
  assert.equal(authorization.prompt_digest, fresh.prompt_digest);
  await assert.rejects(
    () => authorizePreparedChange(prepared, fresh, { now: new Date(now) }),
    /PROMPT_NOT_FOUND|PROMPT_ALREADY_CONSUMED/,
  );
});

test("authorization uses structured scope evidence beyond the excerpt boundary", async (t) => {
  const root = await runtimeRoot(t);
  const prepared = prepareChange(snapshot(), proposal());
  const longPrompt = `${"审批背景。".repeat(80)}\n我明确批准 request-1，scope_digest: ${scopeDigest}`;
  const ref = await recordMakerPrompt(activeEvent(longPrompt), root);
  const authorization = await authorizePreparedChange(prepared, ref, { now: new Date(now) });
  assert.equal(authorization.request_id, "request-1");
  assert.equal(authorization.prompt_digest, ref.prompt_digest);
});

test("authorization keeps excerpt fallback for legacy prompt records", async (t) => {
  const root = await runtimeRoot(t);
  const prepared = prepareChange(snapshot(), proposal());
  const ref = await recordMakerPrompt(activeEvent(
    `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  ), root);
  const stored = JSON.parse(await readFile(ref.file_path, "utf8"));
  delete stored.authorization_claim;
  await writeFile(ref.file_path, `${JSON.stringify(stored)}\n`, "utf8");
  await utimes(ref.file_path, new Date(now), new Date(now));
  const authorization = await authorizePreparedChange(prepared, ref, { now: new Date(now) });
  assert.equal(authorization.request_id, "request-1");
});

test("decline authorization requires an exact explicit Maker rejection", async (t) => {
  const root = await runtimeRoot(t);
  const prepared = prepareChange(snapshot(), proposal());
  const approval = await recordMakerPrompt(activeEvent(
    `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  ), root);
  await assert.rejects(
    () => authorizePreparedDecline(prepared, approval, { now: new Date(now) }),
    /EXPLICIT_DECLINE_REQUIRED/,
  );

  const ambiguous = await recordMakerPrompt(activeEvent(
    `request-1 先不要处理，scope_digest: ${scopeDigest}`,
    { turn_id: "turn-3" },
  ), root);
  await assert.rejects(
    () => authorizePreparedDecline(
      { ...prepared, turn_id: "turn-3" }, ambiguous, { now: new Date(now) },
    ),
    /EXPLICIT_DECLINE_REQUIRED/,
  );

  const rejected = await recordMakerPrompt(activeEvent(
    `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
    { turn_id: "turn-4" },
  ), root);
  const authorization = await authorizePreparedDecline(
    { ...prepared, turn_id: "turn-4" }, rejected, { now: new Date(now) },
  );
  assert.equal(authorization.request_id, "request-1");
  assert.equal(authorization.prompt_digest, rejected.prompt_digest);
});

test("decision mutations require authorization but evidence may invalidate an assumption", () => {
  for (const change_kind of ["PRODUCT_DECISION", "ARCHITECTURE_DECISION"] ) {
    for (const operation of ["ADD", "SUPERSEDE", "REVOKE"]) {
      const prepared = prepareChange(snapshot({
        pending_requests: [{
          request_id: "request-1", operation, scope_digest: scopeDigest,
          status: "PENDING", created_at: now, project_revision: 4,
        }],
      }), proposal({ change_kind, operation }));
      assert.equal(prepared.requires_authorization, true);
    }
  }

  const evidenceChange = prepareChange(snapshot({ pending_requests: [] }), proposal({
    request_id: null, scope_digest: null, operation: "INVALIDATE_ASSUMPTION",
    change_kind: "RUNTIME_ASSUMPTION_EVIDENCE", evidence_refs: ["evidence:trace-1"],
  }));
  assert.equal(evidenceChange.requires_authorization, false);
});
