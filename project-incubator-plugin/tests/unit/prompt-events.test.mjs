import assert from "node:assert/strict";
import { access, mkdir, mkdtemp, readdir, readFile, rm, utimes, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import {
  consumePrompt,
  findAuthorizedPromptRef,
  recordMakerPrompt,
} from "../../src/kernel/prompt-events.mjs";
import { resolveRuntimeDataRoot } from "../../src/kernel/runtime-paths.mjs";

const now = "2026-09-29T08:00:00.000Z";

function activation(status = "ACTIVE") {
  return {
    schema_version: "1.0", project_id: "project-1",
    plugin_id: "project-incubator-plugin", plugin_version: "0.1.0", status,
    project_type_id: "mod", child_skill_id: "mod-incubator", host_profile_id: "sims-4",
  };
}

function event(overrides = {}) {
  return {
    activation: activation(), role: "maker", project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1", turn_id: "turn-1", text: "我明确批准 request-1",
    captured_at: now, ...overrides,
  };
}

async function tempRoot(t) {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-prompts-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  return root;
}

async function waitForPath(target) {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    try {
      await access(target);
      return;
    } catch (error) {
      if (error?.code !== "ENOENT") throw error;
      await new Promise((resolve) => setTimeout(resolve, 10));
    }
  }
  throw new Error(`TEST_PATH_TIMEOUT: ${target}`);
}

async function waitForClaimedConflict(root, conflictPath) {
  const prefix = `${path.basename(conflictPath)}.claimed-`;
  for (let attempt = 0; attempt < 100; attempt += 1) {
    const found = (await readdir(root)).find((name) => name.startsWith(prefix));
    if (found) return path.join(root, found);
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  throw new Error(`TEST_CLAIM_TIMEOUT: ${conflictPath}`);
}

test("runtime data root prefers plugin writable data and keeps CODEX_HOME fallback", () => {
  assert.equal(
    resolveRuntimeDataRoot({ PLUGIN_DATA: "C:\\PluginData", CODEX_HOME: "C:\\CodexHome" }),
    path.resolve("C:\\PluginData", "runtime-events"),
  );
  assert.equal(
    resolveRuntimeDataRoot({ CODEX_HOME: "C:\\CodexHome" }),
    path.resolve("C:\\CodexHome", "project-incubator-plugin", "runtime-events"),
  );
  assert.throws(() => resolveRuntimeDataRoot({}), /RUNTIME_DATA_ROOT_REQUIRED/);
});

test("legacy plugin MCP derives the same writable data root when host env is absent", () => {
  const codexHome = path.join(os.tmpdir(), "codex-home");
  const pluginRoot = path.join(
    codexHome, "plugins", "cache", "personal", "project-incubator-plugin", "0.1.0",
  );
  assert.equal(
    resolveRuntimeDataRoot({}, pluginRoot),
    path.join(codexHome, "plugins", "data", "project-incubator-plugin-personal", "runtime-events"),
  );
  assert.equal(
    resolveRuntimeDataRoot({ CODEX_HOME: path.join(codexHome, "legacy-home") }, pluginRoot),
    path.join(codexHome, "plugins", "data", "project-incubator-plugin-personal", "runtime-events"),
  );
});

test("inactive projects do not create runtime data", async (t) => {
  const root = path.join(await tempRoot(t), "does-not-exist");
  const result = await recordMakerPrompt(event({ activation: activation("INACTIVE") }), root);
  assert.equal(result, null);
  await assert.rejects(() => access(root), /ENOENT/);
});

test("active prompt stores only bounded provenance fields", async (t) => {
  const root = await tempRoot(t);
  const ref = await recordMakerPrompt(event({ text: `我明确批准 ${"x".repeat(500)}` }), root);
  const stored = JSON.parse(await readFile(ref.file_path, "utf8"));
  assert.deepEqual(Object.keys(stored).sort(), [
    "authorization_claim", "excerpt", "project_id", "project_root", "prompt_digest", "session_id", "turn_id",
  ]);
  assert.ok(stored.excerpt.length <= 240);
  assert.equal(stored.project_id, "project-1");
});

test("authorization claim is extracted from the full prompt beyond the excerpt boundary", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  const text = `${"背景说明。".repeat(80)}\n我明确批准 request-1，scope_digest: ${scopeDigest}`;
  const ref = await recordMakerPrompt(event({ text }), root);
  const stored = JSON.parse(await readFile(ref.file_path, "utf8"));
  assert.equal(stored.excerpt.includes(scopeDigest), false);
  assert.deepEqual(stored.authorization_claim, {
    intent: "APPROVE", request_id: "request-1", scope_digest: scopeDigest,
  });
  assert.equal(JSON.stringify(stored).includes(text), false);
});

test("kernel resolves the host turn from the latest exact scoped approval", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  await recordMakerPrompt(event({
    turn_id: "host-turn-approval",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { trackLatest: true });

  const ref = await findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "APPROVE",
  });

  assert.equal(ref.turn_id, "host-turn-approval");
});

test("kernel does not fall back to an older approval after a newer Maker prompt", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  await recordMakerPrompt(event({
    turn_id: "host-turn-old",
    captured_at: "2026-09-29T07:59:00.000Z",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  await recordMakerPrompt(event({
    turn_id: "host-turn-current",
    text: `我明确批准 request-2，scope_digest: ${"b".repeat(64)}`,
  }), root, { trackLatest: true });

  await assert.rejects(() => findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "APPROVE",
  }), /PROMPT_SCOPE_NOT_CONFIRMED/);
});

test("kernel never reuses an approval captured from another project root", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  await recordMakerPrompt(event({
    project_root: "C:\\managed\\project-b",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { trackLatest: true });

  await assert.rejects(() => findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "APPROVE",
  }), /PROMPT_NOT_FOUND/);
});

test("kernel follows Hook arrival order when the host clock moves backward", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  await recordMakerPrompt(event({
    turn_id: "host-turn-approve",
    captured_at: "2026-09-29T08:01:00.000Z",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date("2026-09-29T08:02:00.000Z"), trackLatest: true });
  await recordMakerPrompt(event({
    turn_id: "host-turn-decline",
    captured_at: "2026-09-29T08:00:00.000Z",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date("2026-09-29T08:02:00.000Z"), trackLatest: true });

  await assert.rejects(() => findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "APPROVE",
  }), /EXPLICIT_APPROVAL_REQUIRED/);
});

test("an approval cannot be consumed after a later Prompt supersedes it", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  await recordMakerPrompt(event({
    turn_id: "host-turn-approve",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const approval = await findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "APPROVE",
  });
  await recordMakerPrompt(event({
    turn_id: "host-turn-decline",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });

  await assert.rejects(() => consumePrompt(approval), /PROMPT_SUPERSEDED/);
  await access(approval.file_path);
});

test("overlapping maintenance Prompts require conflict acknowledgement before a new authorization", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  const seed = await recordMakerPrompt(event({
    turn_id: "host-turn-seed",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const lockPath = `${seed.latest_marker_path}.lock`;
  const conflictPath = `${seed.latest_marker_path}.conflict.json`;
  await mkdir(lockPath);
  await writeFile(path.join(lockPath, "external-owner.owner"), `${JSON.stringify({
    token: "external-owner", created_at_ms: Date.now(),
  })}\n`, "utf8");

  const approval = recordMakerPrompt(event({
    turn_id: "host-turn-overlap-approve",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const decline = recordMakerPrompt(event({
    turn_id: "host-turn-overlap-decline",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const overlapped = await Promise.allSettled([approval, decline]);
  assert.equal(overlapped.every((result) => (
    result.status === "rejected" && /PROMPT_ORDER_AMBIGUOUS/u.test(result.reason.message)
  )), true);
  await waitForPath(conflictPath);
  await rm(lockPath, { recursive: true, force: true });

  await assert.rejects(() => findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "APPROVE",
  }), /PROMPT_ORDER_AMBIGUOUS/);

  await assert.rejects(() => recordMakerPrompt(event({
    turn_id: "host-turn-acknowledge-overlap",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true }), /PROMPT_ORDER_AMBIGUOUS/);
  await recordMakerPrompt(event({
    turn_id: "host-turn-after-overlap",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const recovered = await findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "DECLINE",
  });
  assert.equal(recovered.turn_id, "host-turn-after-overlap");
});

test("a stale Prompt lock requires acknowledgement before a later Prompt rebuilds the pointer", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  const seed = await recordMakerPrompt(event({
    turn_id: "host-turn-before-stale-lock",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const lockPath = `${seed.latest_marker_path}.lock`;
  await mkdir(lockPath);
  await writeFile(path.join(lockPath, "stale-owner.owner"), `${JSON.stringify({
    token: "stale-owner", created_at_ms: Date.now() - 60_000,
  })}\n`, "utf8");

  await assert.rejects(() => recordMakerPrompt(event({
    turn_id: "host-turn-acknowledge-stale-lock",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true }), /PROMPT_ORDER_AMBIGUOUS/);
  await recordMakerPrompt(event({
    turn_id: "host-turn-after-stale-lock",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const recovered = await findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "DECLINE",
  });
  assert.equal(recovered.turn_id, "host-turn-after-stale-lock");
});

test("a crashed Prompt intent is converted into a conflict instead of blocking forever", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  const seed = await recordMakerPrompt(event({
    turn_id: "host-turn-before-stale-intent",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const intentDir = `${seed.latest_marker_path}.intents`;
  await mkdir(intentDir);
  await writeFile(path.join(intentDir, "crashed.intent"), `${JSON.stringify({
    token: "crashed", pid: process.pid, created_at_ms: Date.now() - 60_000,
  })}\n`, "utf8");

  await assert.rejects(() => recordMakerPrompt(event({
    turn_id: "host-turn-acknowledge-stale-intent",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true }), /PROMPT_ORDER_AMBIGUOUS/);
  await recordMakerPrompt(event({
    turn_id: "host-turn-after-stale-intent",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const recovered = await findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "DECLINE",
  });
  assert.equal(recovered.turn_id, "host-turn-after-stale-intent");
});

test("a resumed Prompt cannot publish after its stale intent was reclaimed", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  await recordMakerPrompt(event({
    turn_id: "host-turn-before-live-reclaim",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });

  let releaseOld;
  const oldReleased = new Promise((resolve) => { releaseOld = resolve; });
  let signalOld;
  const oldRegistered = new Promise((resolve) => { signalOld = resolve; });
  const oldApproval = recordMakerPrompt(event({
    turn_id: "host-turn-old-approve",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, {
    now: new Date(now),
    trackLatest: true,
    afterIntentRegistration: async ({ markerPath, token }) => {
      await writeFile(path.join(`${markerPath}.intents`, `${token}.intent`), `${JSON.stringify({
        token, pid: process.pid, created_at_ms: Date.now() - 60_000,
      })}\n`, "utf8");
      signalOld();
      await oldReleased;
    },
  });
  await oldRegistered;

  await assert.rejects(() => recordMakerPrompt(event({
    turn_id: "host-turn-newer-decline",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true }), /PROMPT_ORDER_AMBIGUOUS/);
  releaseOld();
  await assert.rejects(() => oldApproval, /PROMPT_ORDER_AMBIGUOUS/);

  await recordMakerPrompt(event({
    turn_id: "host-turn-after-live-reclaim",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const recovered = await findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "DECLINE",
  });
  assert.equal(recovered.turn_id, "host-turn-after-live-reclaim");
});

test("a maintenance Prompt publishes its intent before asynchronous cleanup", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  await recordMakerPrompt(event({
    turn_id: "host-turn-before-intent-barrier",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });

  let releaseIntent;
  const intentReleased = new Promise((resolve) => { releaseIntent = resolve; });
  let signalIntent;
  const intentRegistered = new Promise((resolve) => { signalIntent = resolve; });
  const recording = recordMakerPrompt(event({
    turn_id: "host-turn-after-intent-barrier",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, {
    now: new Date(now),
    trackLatest: true,
    afterIntentRegistration: async () => {
      signalIntent();
      await intentReleased;
    },
  });
  await Promise.race([
    intentRegistered,
    new Promise((_, reject) => setTimeout(() => reject(new Error("INTENT_NOT_REGISTERED")), 250)),
  ]);
  await assert.rejects(() => findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "APPROVE",
  }), /PROMPT_ORDER_AMBIGUOUS/);
  releaseIntent();
  await recording;
});

test("an empty intent directory still blocks consumption during intent publication", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  const seed = await recordMakerPrompt(event({
    turn_id: "host-turn-before-empty-intent",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  await mkdir(`${seed.latest_marker_path}.intents`);
  await assert.rejects(() => findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "APPROVE",
  }), /PROMPT_ORDER_AMBIGUOUS/);
});

test("an acknowledgement write failure leaves a durable authorization barrier", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  const seed = await recordMakerPrompt(event({
    turn_id: "host-turn-before-ack-failure",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const conflictPath = `${seed.latest_marker_path}.conflict.json`;
  await mkdir(conflictPath);
  await writeFile(path.join(conflictPath, "old.conflict"), `${JSON.stringify({
    kind: "CONFLICT", lock_token: "old-lock",
  })}\n`, "utf8");

  let acknowledgementAttempted = false;
  await assert.rejects(() => recordMakerPrompt(event({
    turn_id: "host-turn-ack-failure",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, {
    now: new Date(now),
    trackLatest: true,
    beforeConflictAcknowledgement: async () => {
      acknowledgementAttempted = true;
      throw new Error("SIMULATED_ACK_FAILURE");
    },
  }), /SIMULATED_ACK_FAILURE/);
  assert.equal(acknowledgementAttempted, true);
  await assert.rejects(() => findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "APPROVE",
  }), /PROMPT_ORDER_AMBIGUOUS/);
});

test("an orphaned claimed conflict blocks old approval and is recovered in two steps", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  const seed = await recordMakerPrompt(event({
    turn_id: "host-turn-before-orphaned-claim",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const conflictPath = `${seed.latest_marker_path}.conflict.json`;
  const orphanedClaim = `${conflictPath}.claimed-crashed`;
  await mkdir(orphanedClaim);
  await writeFile(path.join(orphanedClaim, "old.conflict"), `${JSON.stringify({
    kind: "CONFLICT", lock_token: "crashed",
  })}\n`, "utf8");

  await assert.rejects(() => findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "APPROVE",
  }), /PROMPT_ORDER_AMBIGUOUS/);
  await assert.rejects(() => recordMakerPrompt(event({
    turn_id: "host-turn-acknowledge-orphaned-claim",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true }), /PROMPT_ORDER_AMBIGUOUS/);
  await recordMakerPrompt(event({
    turn_id: "host-turn-after-orphaned-claim",
    text: `我明确拒绝 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const recovered = await findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "DECLINE",
  });
  assert.equal(recovered.turn_id, "host-turn-after-orphaned-claim");
});

test("a conflict refreshed during the quiet window cannot be deleted or publish READY", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  const seed = await recordMakerPrompt(event({
    turn_id: "host-turn-before-quiet-race",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const conflictPath = `${seed.latest_marker_path}.conflict.json`;
  await mkdir(conflictPath);
  await writeFile(path.join(conflictPath, "old.conflict"), "\n", "utf8");

  const recording = recordMakerPrompt(event({
    turn_id: "host-turn-quiet-race",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  await waitForClaimedConflict(root, conflictPath);
  await mkdir(conflictPath, { recursive: true });
  await writeFile(path.join(conflictPath, "new.conflict"), "\n", "utf8");
  await assert.rejects(() => recording, /PROMPT_ORDER_AMBIGUOUS/);
  await waitForPath(conflictPath);

  await assert.rejects(() => findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "APPROVE",
  }), /PROMPT_ORDER_AMBIGUOUS/);
});

test("a conflict written just before claim stays bound to the current lock", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  const seed = await recordMakerPrompt(event({
    turn_id: "host-turn-before-claim-race",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const conflictPath = `${seed.latest_marker_path}.conflict.json`;
  await mkdir(conflictPath);
  await writeFile(path.join(conflictPath, "old.conflict"), `${JSON.stringify({
    lock_token: "old-lock",
  })}\n`, "utf8");

  const recording = recordMakerPrompt(event({
    turn_id: "host-turn-claim-race",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, {
    now: new Date(now),
    trackLatest: true,
    beforeConflictClaim: async ({ token }) => {
      await writeFile(path.join(conflictPath, "current.conflict"), `${JSON.stringify({
        lock_token: token,
      })}\n`, "utf8");
    },
  });
  await assert.rejects(() => recording, /PROMPT_ORDER_AMBIGUOUS/);
  await waitForPath(conflictPath);

  await assert.rejects(() => findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "APPROVE",
  }), /PROMPT_ORDER_AMBIGUOUS/);
});

test("a conflict arriving after the first quiet-window snapshot is never deleted", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  const seed = await recordMakerPrompt(event({
    turn_id: "host-turn-before-settlement-race",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, { now: new Date(now), trackLatest: true });
  const conflictPath = `${seed.latest_marker_path}.conflict.json`;
  await mkdir(conflictPath);
  await writeFile(path.join(conflictPath, "old.ack"), `${JSON.stringify({
    kind: "ACK", lock_token: "old-lock",
  })}\n`, "utf8");

  const recording = recordMakerPrompt(event({
    turn_id: "host-turn-settlement-race",
    text: `我明确批准 request-1，scope_digest: ${scopeDigest}`,
  }), root, {
    now: new Date(now),
    trackLatest: true,
    beforeConflictSettlement: async () => {
      await writeFile(path.join(conflictPath, "late.conflict"), `${JSON.stringify({
        kind: "CONFLICT", lock_token: "late-lock",
      })}\n`, "utf8");
    },
  });
  await assert.rejects(() => recording, /PROMPT_ORDER_AMBIGUOUS/);
  await waitForPath(conflictPath);
  await assert.rejects(() => findAuthorizedPromptRef(root, {
    project_id: "project-1",
    project_root: "C:\\managed\\project-a",
    session_id: "session-1",
    request_id: "request-1",
    scope_digest: scopeDigest,
    intent: "APPROVE",
  }), /PROMPT_ORDER_AMBIGUOUS/);
});

test("plain first-person activation approval is explicit without weakening negative intent", async (t) => {
  const root = await tempRoot(t);
  const scopeDigest = "a".repeat(64);
  const approved = await recordMakerPrompt(event({
    text: `我批准激活请求 request-1，scope_digest: ${scopeDigest}`,
  }), root);
  const approvedStored = JSON.parse(await readFile(approved.file_path, "utf8"));
  assert.deepEqual(approvedStored.authorization_claim, {
    intent: "APPROVE", request_id: "request-1", scope_digest: scopeDigest,
  });

  for (const [turnId, text, intent] of [
    ["turn-negative", `我不批准激活请求 request-1，scope_digest: ${scopeDigest}`, "NONE"],
    ["turn-decline", `我拒绝批准 request-1，scope_digest: ${scopeDigest}`, "DECLINE"],
  ]) {
    const ref = await recordMakerPrompt(event({ turn_id: turnId, text }), root);
    const stored = JSON.parse(await readFile(ref.file_path, "utf8"));
    assert.equal(stored.authorization_claim.intent, intent);
  }
});

test("ambiguous intent and multiple scope tokens do not produce an authorization claim", async (t) => {
  const root = await tempRoot(t);
  const digestA = "a".repeat(64);
  const digestB = "b".repeat(64);
  const ambiguous = await recordMakerPrompt(event({
    text: `我明确批准但也明确拒绝 request-1，scope_digest: ${digestA}`,
  }), root);
  const ambiguousStored = JSON.parse(await readFile(ambiguous.file_path, "utf8"));
  assert.deepEqual(ambiguousStored.authorization_claim, {
    intent: "AMBIGUOUS", request_id: "request-1", scope_digest: digestA,
  });

  const multiple = await recordMakerPrompt(event({
    turn_id: "turn-multiple",
    text: `我明确批准 request-1 和 request-2，scope_digest: ${digestA}，scope_digest: ${digestB}`,
  }), root);
  const multipleStored = JSON.parse(await readFile(multiple.file_path, "utf8"));
  assert.deepEqual(multipleStored.authorization_claim, {
    intent: "APPROVE", request_id: null, scope_digest: null,
  });
});

test("consumePrompt deletes the prompt immediately", async (t) => {
  const root = await tempRoot(t);
  const ref = await recordMakerPrompt(event(), root);
  await consumePrompt(ref);
  await assert.rejects(() => access(ref.file_path), /ENOENT/);
  await assert.rejects(() => consumePrompt(ref), /PROMPT_NOT_FOUND/);
});

test("recording a prompt cleans orphan records older than 24 hours", async (t) => {
  const root = await tempRoot(t);
  const old = await recordMakerPrompt(event({ turn_id: "old-turn" }), root);
  const oldDate = new Date("2026-09-27T00:00:00.000Z");
  await utimes(old.file_path, oldDate, oldDate);
  await recordMakerPrompt(event({ turn_id: "new-turn", captured_at: now }), root, { now: new Date(now) });
  const files = await readdir(root);
  assert.equal(files.length, 1);
  assert.ok(!files.includes(path.basename(old.file_path)));
});
