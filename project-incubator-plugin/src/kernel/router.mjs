import { createHash, randomUUID } from "node:crypto";
import { mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";

import { hashJson } from "./canonical-json.mjs";
import { canonicalProjectPath } from "./project-root.mjs";
import { resolveRoute } from "./registry.mjs";

const MAX_BOOTSTRAP_AGE_MS = 24 * 60 * 60 * 1000;

function comparable(value) {
  const normalized = path.normalize(value);
  return process.platform === "win32" ? normalized.toLowerCase() : normalized;
}

function activationFile(runtimeDataRoot, canonicalRoot) {
  const key = createHash("sha256").update(comparable(canonicalRoot), "utf8").digest("hex");
  return path.join(runtimeDataRoot, `activation-${key}.json`);
}

function within(candidate, root) {
  const relative = path.relative(root, candidate);
  return relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative));
}

function parseRequest(raw) {
  const request = JSON.parse(raw);
  const required = ["request_id", "scope_digest", "project_root", "project_id", "session_id", "created_at", "expires_at"];
  if (required.some((field) => typeof request[field] !== "string" || request[field].length === 0)) {
    throw new Error("ACTIVATION_REQUEST_INVALID");
  }
  return request;
}

export function proposeRoute(registry, input) {
  return Object.freeze({
    event: "ROUTE_PROPOSED",
    route: resolveRoute(registry, input.project_type_id, input.host_profile_id ?? null),
    project_root: input.project_root,
  });
}

export async function prepareActivationRequest({
  runtimeDataRoot, projectRoot, projectId, route, sessionId, summary, initialState, now = new Date(),
}) {
  const canonicalRoot = await canonicalProjectPath(projectRoot);
  const requestId = `activation-${randomUUID()}`;
  const payload = {
    project_root: canonicalRoot, project_id: projectId, route,
    summary, initial_state: initialState,
  };
  const request = {
    request_id: requestId,
    operation: "ACTIVATE_PROJECT",
    scope_digest: hashJson(payload),
    project_root: canonicalRoot,
    project_id: projectId,
    session_id: sessionId,
    summary,
    route,
    initial_state: initialState,
    created_at: now.toISOString(),
    expires_at: new Date(now.getTime() + MAX_BOOTSTRAP_AGE_MS).toISOString(),
    status: "PENDING",
  };
  await mkdir(runtimeDataRoot, { recursive: true });
  await writeFile(activationFile(runtimeDataRoot, canonicalRoot), `${JSON.stringify(request)}\n`, "utf8");
  return request;
}

export async function findPendingActivation(runtimeDataRoot, cwd, sessionId, now = new Date()) {
  let entries;
  try {
    entries = await readdir(runtimeDataRoot, { withFileTypes: true });
  } catch (error) {
    if (error?.code === "ENOENT") return null;
    throw error;
  }
  const canonicalCwd = await canonicalProjectPath(cwd);
  const matches = [];
  for (const entry of entries) {
    if (!entry.isFile() || !entry.name.startsWith("activation-") || !entry.name.endsWith(".json")) continue;
    const target = path.join(runtimeDataRoot, entry.name);
    const request = parseRequest(await readFile(target, "utf8"));
    if (new Date(request.expires_at) <= now) {
      await rm(target, { force: true });
      continue;
    }
    if (request.status === "PENDING" && request.session_id === sessionId
      && within(canonicalCwd, request.project_root)) matches.push({ ...request, file_path: target });
  }
  matches.sort((left, right) => right.project_root.length - left.project_root.length);
  return matches[0] ?? null;
}

export async function getPendingActivation(runtimeDataRoot, projectRoot, requestId, now = new Date()) {
  const canonicalRoot = await canonicalProjectPath(projectRoot);
  let request;
  const filePath = activationFile(runtimeDataRoot, canonicalRoot);
  try {
    request = parseRequest(await readFile(filePath, "utf8"));
  } catch (error) {
    if (error?.code === "ENOENT") throw new Error("ACTIVATION_REQUEST_NOT_FOUND");
    throw error;
  }
  if (request.request_id !== requestId) throw new Error("ACTIVATION_REQUEST_NOT_FOUND");
  if (new Date(request.expires_at) <= now) {
    await rm(filePath, { force: true });
    throw new Error("ACTIVATION_REQUEST_EXPIRED");
  }
  return { ...request, file_path: filePath };
}

export async function consumeActivationRequest(request) {
  await rm(request.file_path, { force: true });
}

export const activationBootstrapPolicy = Object.freeze({ maxAgeMs: MAX_BOOTSTRAP_AGE_MS });
