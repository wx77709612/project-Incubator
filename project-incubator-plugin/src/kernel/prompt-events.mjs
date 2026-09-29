import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, rm, stat, utimes, writeFile } from "node:fs/promises";
import path from "node:path";

import { parseActivation } from "./schemas.mjs";

const MAX_EXCERPT_LENGTH = 240;
const MAX_AGE_MS = 24 * 60 * 60 * 1000;

function digest(value) {
  return createHash("sha256").update(value, "utf8").digest("hex");
}

function eventId(event) {
  return digest(`${event.project_id}\0${event.session_id}\0${event.turn_id}\0${event.text}`);
}

async function cleanupExpired(runtimeDataRoot, now) {
  let entries;
  try {
    entries = await readdir(runtimeDataRoot, { withFileTypes: true });
  } catch (error) {
    if (error?.code === "ENOENT") return;
    throw error;
  }
  await Promise.all(entries
    .filter((entry) => entry.isFile() && entry.name.endsWith(".json"))
    .map(async (entry) => {
      const target = path.join(runtimeDataRoot, entry.name);
      const details = await stat(target);
      if (now.getTime() - details.mtimeMs > MAX_AGE_MS) await rm(target, { force: true });
    }));
}

async function recordScopedPrompt(event, runtimeDataRoot, options = {}) {
  if (event.role !== "maker") throw new Error("MAKER_PROMPT_REQUIRED");
  for (const field of ["project_id", "session_id", "turn_id", "text", "captured_at"]) {
    if (typeof event[field] !== "string" || event[field].length === 0) {
      throw new Error(`PROMPT_${field.toUpperCase()}_REQUIRED`);
    }
  }
  const capturedAt = new Date(event.captured_at);
  if (Number.isNaN(capturedAt.getTime())) throw new Error("PROMPT_CAPTURED_AT_INVALID");
  const now = options.now ?? new Date();
  await cleanupExpired(runtimeDataRoot, now);
  await mkdir(runtimeDataRoot, { recursive: true });

  const id = eventId(event);
  const filePath = path.join(runtimeDataRoot, `${id}.json`);
  const promptDigest = digest(event.text);
  const stored = {
    project_id: event.project_id,
    session_id: event.session_id,
    turn_id: event.turn_id,
    prompt_digest: promptDigest,
    excerpt: event.text.slice(0, MAX_EXCERPT_LENGTH),
  };
  await writeFile(filePath, `${JSON.stringify(stored)}\n`, { encoding: "utf8", flag: "wx" });
  await utimes(filePath, capturedAt, capturedAt);
  return {
    event_id: id,
    file_path: filePath,
    project_id: event.project_id,
    session_id: event.session_id,
    turn_id: event.turn_id,
    prompt_digest: promptDigest,
  };
}

export async function recordMakerPrompt(event, runtimeDataRoot, options = {}) {
  const activation = parseActivation(event.activation);
  if (activation.status !== "ACTIVE") return null;
  if (event.project_id !== activation.project_id) throw new Error("PROMPT_PROJECT_MISMATCH");
  return recordScopedPrompt(event, runtimeDataRoot, options);
}

export async function recordBootstrapPrompt(event, request, runtimeDataRoot, options = {}) {
  if (request.status !== "PENDING") throw new Error("ACTIVATION_REQUEST_NOT_PENDING");
  if (event.project_id !== request.project_id || event.session_id !== request.session_id) {
    throw new Error("PROMPT_CONTEXT_MISMATCH");
  }
  return recordScopedPrompt(event, runtimeDataRoot, options);
}

export async function findPromptRef(runtimeDataRoot, context) {
  let entries;
  try {
    entries = await readdir(runtimeDataRoot, { withFileTypes: true });
  } catch (error) {
    if (error?.code === "ENOENT") throw new Error("PROMPT_NOT_FOUND");
    throw error;
  }
  for (const entry of entries) {
    if (!entry.isFile() || !entry.name.endsWith(".json")
      || entry.name.startsWith("activation-") || entry.name.startsWith("turn-")) continue;
    const filePath = path.join(runtimeDataRoot, entry.name);
    let stored;
    try {
      stored = JSON.parse(await readFile(filePath, "utf8"));
    } catch {
      continue;
    }
    if (stored.project_id === context.project_id
      && stored.session_id === context.session_id
      && stored.turn_id === context.turn_id
      && typeof stored.prompt_digest === "string") {
      return {
        event_id: path.basename(entry.name, ".json"), file_path: filePath,
        project_id: stored.project_id, session_id: stored.session_id,
        turn_id: stored.turn_id, prompt_digest: stored.prompt_digest,
      };
    }
  }
  throw new Error("PROMPT_NOT_FOUND");
}

export async function readPrompt(promptRef) {
  let raw;
  try {
    raw = await readFile(promptRef.file_path, "utf8");
  } catch (error) {
    if (error?.code === "ENOENT") throw new Error("PROMPT_NOT_FOUND");
    throw error;
  }
  let stored;
  try {
    stored = JSON.parse(raw);
  } catch (error) {
    throw new Error("PROMPT_RECORD_INVALID", { cause: error });
  }
  for (const field of ["project_id", "session_id", "turn_id", "prompt_digest", "excerpt"]) {
    if (typeof stored[field] !== "string" || stored[field].length === 0) {
      throw new Error("PROMPT_RECORD_INVALID");
    }
  }
  if (stored.prompt_digest !== promptRef.prompt_digest) throw new Error("PROMPT_DIGEST_MISMATCH");
  return stored;
}

export async function promptAgeMs(promptRef, now = new Date()) {
  let details;
  try {
    details = await stat(promptRef.file_path);
  } catch (error) {
    if (error?.code === "ENOENT") throw new Error("PROMPT_NOT_FOUND");
    throw error;
  }
  return now.getTime() - details.mtimeMs;
}

export async function consumePrompt(promptRef) {
  try {
    await rm(promptRef.file_path);
  } catch (error) {
    if (error?.code === "ENOENT") throw new Error("PROMPT_NOT_FOUND");
    throw error;
  }
}

export const promptPolicy = Object.freeze({ maxAgeMs: MAX_AGE_MS, maxExcerptLength: MAX_EXCERPT_LENGTH });
