import assert from "node:assert/strict";
import { access, mkdtemp, readdir, readFile, rm, utimes } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import {
  consumePrompt,
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
    session_id: "session-1", turn_id: "turn-1", text: "我明确批准 request-1",
    captured_at: now, ...overrides,
  };
}

async function tempRoot(t) {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-prompts-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  return root;
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
    "authorization_claim", "excerpt", "project_id", "prompt_digest", "session_id", "turn_id",
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
