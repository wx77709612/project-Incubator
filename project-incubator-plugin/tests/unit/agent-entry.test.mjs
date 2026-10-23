import assert from "node:assert/strict";
import { mkdtemp, mkdir, readFile, rm, symlink, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import {
  createAgentEntry,
  inspectAgentEntry,
  loadAgentEntryTemplate,
  rollbackAgentEntry,
} from "../../src/kernel/agent-entry.mjs";

const pluginRoot = path.resolve(import.meta.dirname, "../..");

async function temporaryRoot(t, prefix = "incubator-agent-entry-") {
  const root = await mkdtemp(path.join(os.tmpdir(), prefix));
  t.after(() => rm(root, { recursive: true, force: true }));
  return root;
}

test("packaged AGENTS template is Chinese guidance for the current Router and Kernel", async () => {
  const template = await loadAgentEntryTemplate(pluginRoot);
  const text = template.bytes.toString("utf8");

  assert.match(template.sha256, /^[a-f0-9]{64}$/);
  assert.match(text, /project-incubator-router/);
  assert.match(text, /inspect_project/);
  assert.match(text, /activation\.json/);
  assert.match(text, /state\.json/);
  assert.match(text, /latest-receipt\.json/);
  assert.match(text, /Maker/);
  assert.match(text, /Kernel/);
  assert.match(text, /简体中文/);
  assert.doesNotMatch(text, /开始前调用 get_project_state/);
  assert.doesNotMatch(text, /PROJECT_STATE\.md 是唯一状态权威/);
});

test("template loading fails closed for missing, linked, empty, or legacy guidance", async (t) => {
  const root = await temporaryRoot(t);
  const templateDir = path.join(root, "templates", "codex");
  await mkdir(templateDir, { recursive: true });

  await assert.rejects(() => loadAgentEntryTemplate(root), /AGENT_ENTRY_TEMPLATE_INVALID/);

  const external = path.join(root, "external.md");
  await writeFile(external, "外部模板");
  await symlink(external, path.join(templateDir, "AGENTS.md"), "file");
  await assert.rejects(() => loadAgentEntryTemplate(root), /AGENT_ENTRY_TEMPLATE_INVALID/);
  await rm(path.join(templateDir, "AGENTS.md"));

  await writeFile(path.join(templateDir, "AGENTS.md"), "   \n");
  await assert.rejects(() => loadAgentEntryTemplate(root), /AGENT_ENTRY_TEMPLATE_INVALID/);

  await writeFile(path.join(templateDir, "AGENTS.md"), [
    "project-incubator-router inspect_project activation.json state.json latest-receipt.json",
    "Maker Kernel 简体中文",
    "开始前调用 get_project_state",
  ].join("\n"));
  await assert.rejects(() => loadAgentEntryTemplate(root), /AGENT_ENTRY_TEMPLATE_INVALID/);
});

test("inspection distinguishes missing, current, and existing files without modifying them", async (t) => {
  const root = await temporaryRoot(t);
  const template = await loadAgentEntryTemplate(pluginRoot);

  assert.deepEqual(await inspectAgentEntry(root, template), {
    path: "AGENTS.md",
    status: "MISSING",
    template_sha256: template.sha256,
  });

  await writeFile(path.join(root, "AGENTS.md"), template.bytes);
  assert.deepEqual(await inspectAgentEntry(root, template), {
    path: "AGENTS.md",
    status: "CURRENT",
    existing_sha256: template.sha256,
    template_sha256: template.sha256,
  });

  const existing = Buffer.from("# 项目自己的说明\n");
  await writeFile(path.join(root, "AGENTS.md"), existing);
  const result = await inspectAgentEntry(root, template);
  assert.equal(result.status, "EXISTING_REVIEW_REQUIRED");
  assert.equal(result.path, "AGENTS.md");
  assert.match(result.existing_sha256, /^[a-f0-9]{64}$/);
  assert.equal(result.template_sha256, template.sha256);
  assert.deepEqual(await readFile(path.join(root, "AGENTS.md")), existing);
});

test("inspection rejects directories and links as unsafe AGENTS paths", async (t) => {
  const template = await loadAgentEntryTemplate(pluginRoot);
  const directoryRoot = await temporaryRoot(t, "incubator-agent-entry-dir-");
  await mkdir(path.join(directoryRoot, "AGENTS.md"));
  await assert.rejects(() => inspectAgentEntry(directoryRoot, template), /AGENT_ENTRY_PATH_UNSAFE/);

  const linkRoot = await temporaryRoot(t, "incubator-agent-entry-link-");
  const external = path.join(linkRoot, "external.md");
  await writeFile(external, "外部内容");
  await symlink(external, path.join(linkRoot, "AGENTS.md"), "file");
  await assert.rejects(() => inspectAgentEntry(linkRoot, template), /AGENT_ENTRY_PATH_UNSAFE/);
});

test("creation is exclusive, durable, and returns a rollback token", async (t) => {
  const root = await temporaryRoot(t);
  const template = await loadAgentEntryTemplate(pluginRoot);
  const created = await createAgentEntry(root, template);

  assert.deepEqual(created.result, { path: "AGENTS.md", status: "CREATED" });
  assert.equal(created.rollbackToken.sha256, template.sha256);
  assert.deepEqual(await readFile(path.join(root, "AGENTS.md")), template.bytes);
  await assert.rejects(() => createAgentEntry(root, template), /AGENT_ENTRY_SOURCE_CHANGED/);
});

test("read-back mismatch fails and preserves bytes that may have been changed externally", async (t) => {
  const root = await temporaryRoot(t);
  const template = await loadAgentEntryTemplate(pluginRoot);
  const changed = Buffer.from("并发写入的内容\n");

  await assert.rejects(
    () => createAgentEntry(root, template, {
      async beforeReadback(target) { await writeFile(target, changed); },
    }),
    /AGENT_ENTRY_READBACK_MISMATCH/,
  );
  assert.deepEqual(await readFile(path.join(root, "AGENTS.md")), changed);
});

test("rollback removes only the unchanged file created by this operation", async (t) => {
  const template = await loadAgentEntryTemplate(pluginRoot);

  const unchangedRoot = await temporaryRoot(t, "incubator-agent-entry-rollback-");
  const unchanged = await createAgentEntry(unchangedRoot, template);
  await rollbackAgentEntry(unchangedRoot, unchanged.rollbackToken);
  assert.equal((await inspectAgentEntry(unchangedRoot, template)).status, "MISSING");

  const changedRoot = await temporaryRoot(t, "incubator-agent-entry-preserve-");
  const changed = await createAgentEntry(changedRoot, template);
  await writeFile(path.join(changedRoot, "AGENTS.md"), "Maker 后续修改\n");
  await rollbackAgentEntry(changedRoot, changed.rollbackToken);
  assert.equal(await readFile(path.join(changedRoot, "AGENTS.md"), "utf8"), "Maker 后续修改\n");

  const replacementRoot = await temporaryRoot(t, "incubator-agent-entry-replaced-");
  const replacement = await createAgentEntry(replacementRoot, template);
  await rm(path.join(replacementRoot, "AGENTS.md"));
  await mkdir(path.join(replacementRoot, "AGENTS.md"));
  await rollbackAgentEntry(replacementRoot, replacement.rollbackToken);
  assert.equal((await inspectAgentEntry(replacementRoot, template).catch((error) => error.message)), "AGENT_ENTRY_PATH_UNSAFE");
});
