import { createHash, randomUUID } from "node:crypto";
import { link, lstat, open, readFile, realpath, rename, rm } from "node:fs/promises";
import path from "node:path";

const AGENT_ENTRY_FILE = "AGENTS.md";
const REQUIRED_TEMPLATE_TERMS = [
  "project-incubator-router",
  "inspect_project",
  "activation.json",
  "state.json",
  "latest-receipt.json",
  "Maker",
  "Kernel",
  "简体中文",
];
const FORBIDDEN_TEMPLATE_INSTRUCTIONS = [
  "开始前调用 get_project_state",
  "PROJECT_STATE.md 是唯一状态权威",
];

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function fail(code, cause) {
  throw new Error(code, cause ? { cause } : undefined);
}

function normalizeTemplate(template) {
  if (!template || !Buffer.isBuffer(template.bytes) || typeof template.sha256 !== "string") {
    fail("AGENT_ENTRY_TEMPLATE_INVALID");
  }
  if (sha256(template.bytes) !== template.sha256) fail("AGENT_ENTRY_TEMPLATE_INVALID");
  return template;
}

function fileIdentity(metadata) {
  return {
    dev: metadata.dev.toString(),
    ino: metadata.ino.toString(),
    birthtime_ns: metadata.birthtimeNs.toString(),
  };
}

function sameIdentity(metadata, identity) {
  return identity?.dev === metadata.dev.toString()
    && identity?.ino === metadata.ino.toString()
    && identity?.birthtime_ns === metadata.birthtimeNs.toString();
}

async function inspectTarget(target) {
  let metadata;
  try {
    metadata = await lstat(target, { bigint: true });
  } catch (error) {
    if (error?.code === "ENOENT") return null;
    fail("AGENT_ENTRY_PATH_UNSAFE", error);
  }
  if (!metadata.isFile() || metadata.isSymbolicLink()) fail("AGENT_ENTRY_PATH_UNSAFE");
  return metadata;
}

async function readTarget(target) {
  try {
    return await readFile(target);
  } catch (error) {
    fail("AGENT_ENTRY_PATH_UNSAFE", error);
  }
}

export async function loadAgentEntryTemplate(pluginRoot) {
  const resolvedRoot = path.resolve(pluginRoot);
  const target = path.join(resolvedRoot, "templates", "codex", AGENT_ENTRY_FILE);
  try {
    const [rootReal, targetReal, metadata] = await Promise.all([
      realpath(resolvedRoot),
      realpath(target),
      lstat(target),
    ]);
    const relative = path.relative(rootReal, targetReal);
    if (relative.startsWith("..") || path.isAbsolute(relative) || !metadata.isFile() || metadata.isSymbolicLink()) {
      fail("AGENT_ENTRY_TEMPLATE_INVALID");
    }
    const bytes = await readFile(target);
    const text = bytes.toString("utf8");
    if (!text.trim()
      || REQUIRED_TEMPLATE_TERMS.some((term) => !text.includes(term))
      || FORBIDDEN_TEMPLATE_INSTRUCTIONS.some((term) => text.includes(term))) {
      fail("AGENT_ENTRY_TEMPLATE_INVALID");
    }
    return { bytes, sha256: sha256(bytes) };
  } catch (error) {
    if (error?.message === "AGENT_ENTRY_TEMPLATE_INVALID") throw error;
    fail("AGENT_ENTRY_TEMPLATE_INVALID", error);
  }
}

export async function inspectAgentEntry(projectRoot, templateInput) {
  const template = normalizeTemplate(templateInput);
  const target = path.join(path.resolve(projectRoot), AGENT_ENTRY_FILE);
  const metadata = await inspectTarget(target);
  if (metadata === null) {
    return { path: AGENT_ENTRY_FILE, status: "MISSING", template_sha256: template.sha256 };
  }
  const bytes = await readTarget(target);
  const existingSha256 = sha256(bytes);
  return {
    path: AGENT_ENTRY_FILE,
    status: existingSha256 === template.sha256 ? "CURRENT" : "EXISTING_REVIEW_REQUIRED",
    existing_sha256: existingSha256,
    template_sha256: template.sha256,
  };
}

export async function createAgentEntry(projectRoot, templateInput, hooks = {}) {
  const template = normalizeTemplate(templateInput);
  const target = path.join(path.resolve(projectRoot), AGENT_ENTRY_FILE);
  const existing = await inspectTarget(target);
  if (existing !== null) fail("AGENT_ENTRY_SOURCE_CHANGED");

  let handle;
  let created = false;
  const rollbackToken = { path: AGENT_ENTRY_FILE, sha256: template.sha256, identity: null };
  try {
    handle = await open(target, "wx");
    created = true;
    await handle.writeFile(template.bytes);
    await handle.sync();
    rollbackToken.identity = fileIdentity(await handle.stat({ bigint: true }));
    await handle.close();
    handle = undefined;
    await hooks.beforeReadback?.(target);
    const readback = await readTarget(target);
    if (!readback.equals(template.bytes)) fail("AGENT_ENTRY_READBACK_MISMATCH");
    return {
      result: { path: AGENT_ENTRY_FILE, status: "CREATED" },
      rollbackToken,
    };
  } catch (error) {
    await handle?.close().catch(() => {});
    if (created) {
      const rollback = await rollbackAgentEntry(projectRoot, rollbackToken);
      if (rollback.residual_paths.length) {
        const rollbackError = new Error("AGENT_ENTRY_ROLLBACK_INCOMPLETE", { cause: error });
        rollbackError.residual_paths = rollback.residual_paths;
        throw rollbackError;
      }
    }
    if (error?.code === "EEXIST") fail("AGENT_ENTRY_SOURCE_CHANGED", error);
    throw error;
  }
}

export async function rollbackAgentEntry(projectRoot, rollbackToken, hooks = {}) {
  if (rollbackToken?.path !== AGENT_ENTRY_FILE || !/^[a-f0-9]{64}$/.test(rollbackToken?.sha256 ?? "")) {
    return { rolled_back: false, residual_paths: [] };
  }
  const target = path.join(path.resolve(projectRoot), AGENT_ENTRY_FILE);
  let before;
  try {
    before = await inspectTarget(target);
  } catch (error) {
    if (error?.message === "AGENT_ENTRY_PATH_UNSAFE") return { rolled_back: false, residual_paths: [] };
    throw error;
  }
  if (before === null || !sameIdentity(before, rollbackToken.identity)) {
    return { rolled_back: false, residual_paths: [] };
  }
  const bytes = await readTarget(target);
  if (sha256(bytes) !== rollbackToken.sha256) {
    return { rolled_back: false, residual_paths: [] };
  }

  await hooks.beforeQuarantine?.(target);
  const quarantine = path.join(
    path.dirname(target), `.AGENTS.md.rollback-${process.pid}-${randomUUID()}`,
  );
  try {
    await rename(target, quarantine);
  } catch (error) {
    if (error?.code === "ENOENT") return { rolled_back: false, residual_paths: [] };
    throw error;
  }

  let moved;
  let movedBytes = null;
  try {
    moved = await lstat(quarantine, { bigint: true });
    if (moved.isFile() && !moved.isSymbolicLink()) movedBytes = await readFile(quarantine);
  } catch {
    moved = null;
  }
  if (moved?.isFile()
    && !moved.isSymbolicLink()
    && sameIdentity(moved, rollbackToken.identity)
    && sha256(movedBytes) === rollbackToken.sha256) {
    await rm(quarantine);
    return { rolled_back: true, residual_paths: [] };
  }

  try {
    if (!moved?.isFile() || moved.isSymbolicLink()) throw new Error("AGENT_ENTRY_RESTORE_UNSAFE");
    await link(quarantine, target);
    await rm(quarantine);
    return { rolled_back: false, residual_paths: [] };
  } catch {
    return {
      rolled_back: false,
      residual_paths: [path.relative(path.resolve(projectRoot), quarantine).replaceAll(path.sep, "/")],
    };
  }
}
