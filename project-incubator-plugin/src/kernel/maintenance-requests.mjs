import { randomUUID } from "node:crypto";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";

import { hashJson } from "./canonical-json.mjs";
import { canonicalProjectPath } from "./project-root.mjs";

const MAX_AGE_MS = 24 * 60 * 60 * 1000;

function requestFile(runtimeDataRoot, requestId) {
  if (!/^[a-z]+-[a-z0-9-]+$/u.test(requestId)) throw new Error("MAINTENANCE_REQUEST_INVALID");
  return path.join(runtimeDataRoot, `maintenance-${requestId}.json`);
}

function requestCodes(operation) {
  if (operation === "AGENT_ENTRY_INSTALL") {
    return { notFound: "AGENT_ENTRY_REQUEST_NOT_FOUND", expired: "AGENT_ENTRY_REQUEST_EXPIRED" };
  }
  if (operation === "AUTHORITY_RECOVERY") {
    return {
      notFound: "AUTHORITY_RECOVERY_REQUEST_NOT_FOUND",
      expired: "AUTHORITY_RECOVERY_REQUEST_EXPIRED",
    };
  }
  return { notFound: "MAINTENANCE_REQUEST_NOT_FOUND", expired: "MAINTENANCE_REQUEST_EXPIRED" };
}

function scopeFor({ operation, project_root, session_id, payload }) {
  return { operation, project_root, session_id, payload };
}

function parseRequest(raw) {
  let request;
  try {
    request = JSON.parse(raw);
  } catch (error) {
    throw new Error("MAINTENANCE_REQUEST_INVALID", { cause: error });
  }
  for (const field of [
    "request_id", "scope_digest", "operation", "project_root", "session_id", "created_at", "expires_at",
  ]) {
    if (typeof request?.[field] !== "string" || request[field].length === 0) {
      throw new Error("MAINTENANCE_REQUEST_INVALID");
    }
  }
  if (!request.payload || typeof request.payload !== "object" || Array.isArray(request.payload)) {
    throw new Error("MAINTENANCE_REQUEST_INVALID");
  }
  if (request.scope_digest !== hashJson(scopeFor(request))) {
    throw new Error("MAINTENANCE_REQUEST_INVALID");
  }
  return request;
}

export async function prepareMaintenanceRequest({
  runtimeDataRoot,
  projectRoot,
  sessionId,
  operation,
  requestPrefix,
  payload,
  now = new Date(),
}) {
  if (typeof sessionId !== "string" || sessionId.length === 0
    || typeof operation !== "string" || operation.length === 0
    || !/^[a-z]+$/u.test(requestPrefix ?? "")
    || !payload || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("MAINTENANCE_REQUEST_INVALID");
  }
  const projectRootCanonical = await canonicalProjectPath(projectRoot);
  const requestId = `${requestPrefix}-${randomUUID()}`;
  const base = {
    operation,
    project_root: projectRootCanonical,
    session_id: sessionId,
    payload: structuredClone(payload),
  };
  const request = {
    request_id: requestId,
    scope_digest: hashJson(base),
    ...base,
    created_at: now.toISOString(),
    expires_at: new Date(now.getTime() + MAX_AGE_MS).toISOString(),
    status: "PENDING",
  };
  await mkdir(runtimeDataRoot, { recursive: true });
  const filePath = requestFile(runtimeDataRoot, requestId);
  await writeFile(filePath, `${JSON.stringify(request)}\n`, { encoding: "utf8", flag: "wx" });
  return { ...request, file_path: filePath };
}

export async function getMaintenanceRequest({
  runtimeDataRoot,
  projectRoot,
  requestId,
  scopeDigest,
  sessionId,
  operation,
  now = new Date(),
}) {
  const codes = requestCodes(operation);
  let filePath;
  let request;
  try {
    filePath = requestFile(runtimeDataRoot, requestId);
    request = parseRequest(await readFile(filePath, "utf8"));
  } catch (error) {
    if (error?.code === "ENOENT" || error?.message === "MAINTENANCE_REQUEST_INVALID") {
      throw new Error(codes.notFound, { cause: error });
    }
    throw error;
  }
  if (request.request_id !== requestId || request.operation !== operation || request.status !== "PENDING") {
    throw new Error(codes.notFound);
  }
  if (new Date(request.expires_at) <= now) {
    await rm(filePath, { force: true });
    throw new Error(codes.expired);
  }
  const canonicalRoot = await canonicalProjectPath(projectRoot);
  if (request.project_root !== canonicalRoot) throw new Error("PROJECT_CONTEXT_MISMATCH");
  if (request.session_id !== sessionId) throw new Error("PROMPT_CONTEXT_MISMATCH");
  if (request.scope_digest !== scopeDigest) throw new Error("SCOPE_DIGEST_MISMATCH");
  return { ...request, file_path: filePath };
}

export async function consumeMaintenanceRequest(request) {
  await rm(request.file_path);
}

export const maintenanceRequestPolicy = Object.freeze({ maxAgeMs: MAX_AGE_MS });
