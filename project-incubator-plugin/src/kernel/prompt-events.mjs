import { createHash, randomUUID } from "node:crypto";
import { mkdir, readFile, readdir, rename, rm, rmdir, stat, utimes, writeFile } from "node:fs/promises";
import path from "node:path";

import { parseActivation } from "./schemas.mjs";

const MAX_EXCERPT_LENGTH = 240;
const MAX_AGE_MS = 24 * 60 * 60 * 1000;
const PROMPT_CONFLICT_QUIET_MS = 100;
const PROMPT_LOCK_STALE_MS = 30_000;
const APPROVAL_PATTERN = /(?:明确批准|正式批准|明确同意|我批准激活请求|\b(?:approve|approved|authorize|authorized)\b)/iu;
const DECLINE_PATTERN = /(?:明确拒绝|正式拒绝|明确撤回|正式撤回|拒绝批准|明确不同意|\b(?:reject|rejected|decline|declined|withdraw|withdrawn)\b)/iu;

export function hasExplicitApproval(text) {
  return APPROVAL_PATTERN.test(text);
}

export function hasExplicitDecline(text) {
  return DECLINE_PATTERN.test(text);
}

function uniqueMatches(text, pattern, transform = (value) => value) {
  return [...new Set([...text.matchAll(pattern)].map((match) => transform(match[0])))];
}

function extractAuthorizationClaim(text) {
  const approves = hasExplicitApproval(text);
  const declines = hasExplicitDecline(text);
  const intent = approves && declines ? "AMBIGUOUS"
    : approves ? "APPROVE"
      : declines ? "DECLINE"
        : "NONE";
  const requestIds = uniqueMatches(
    text,
    /\b(?:request|activation|recovery)-[a-z0-9][a-z0-9-]*\b/giu,
  );
  const scopeDigests = uniqueMatches(text, /\b[a-f0-9]{64}\b/giu, (value) => value.toLowerCase());
  return {
    intent,
    request_id: requestIds.length === 1 ? requestIds[0] : null,
    scope_digest: scopeDigests.length === 1 ? scopeDigests[0] : null,
  };
}

function digest(value) {
  return createHash("sha256").update(value, "utf8").digest("hex");
}

function eventId(event) {
  return digest(`${event.project_root}\0${event.project_id}\0${event.session_id}\0${event.turn_id}\0${event.text}`);
}

function latestPromptMarkerPath(runtimeDataRoot, context) {
  const key = digest(`${context.project_root}\0${context.project_id}\0${context.session_id}`);
  return path.join(runtimeDataRoot, `prompt-latest-${key}.json`);
}

function promptCoordinationPaths(markerPath) {
  return {
    lockPath: `${markerPath}.lock`,
    conflictPath: `${markerPath}.conflict.json`,
    intentDir: `${markerPath}.intents`,
  };
}

async function pathExists(target) {
  try {
    await stat(target);
    return true;
  } catch (error) {
    if (error?.code === "ENOENT") return false;
    throw error;
  }
}

async function releasePromptLock(lock) {
  await rm(lock.ownerPath, { force: true });
  await rmdir(lock.lockPath).catch(() => {});
  await rm(lock.intentPath, { force: true });
  await rmdir(lock.intentDir).catch(() => {});
}

async function releasePromptIntent(intent) {
  if (!intent) return;
  await rm(intent.intentPath, { force: true });
  await rmdir(intent.intentDir).catch(() => {});
}

async function promptLockAgeMs(lockPath) {
  try {
    const owners = (await readdir(lockPath)).filter((name) => name.endsWith(".owner"));
    for (const owner of owners) {
      try {
        const metadata = JSON.parse(await readFile(path.join(lockPath, owner), "utf8"));
        if (Number.isFinite(metadata?.created_at_ms)) return Date.now() - metadata.created_at_ms;
      } catch {
        // 损坏的 owner 元数据不能被当作新鲜锁；回退到目录时间。
      }
    }
    return Date.now() - (await stat(lockPath)).mtimeMs;
  } catch (error) {
    if (error?.code === "ENOENT") return null;
    throw error;
  }
}

async function currentPromptLockToken(lockPath) {
  try {
    const owners = (await readdir(lockPath)).filter((name) => name.endsWith(".owner"));
    if (owners.length !== 1) return null;
    const metadata = JSON.parse(await readFile(path.join(lockPath, owners[0]), "utf8"));
    return typeof metadata?.token === "string" ? metadata.token : null;
  } catch {
    return null;
  }
}

async function recordPromptConflict(conflictPath, lockToken) {
  const event = `${JSON.stringify({ kind: "CONFLICT", lock_token: lockToken })}\n`;
  while (true) {
    try {
      await mkdir(conflictPath, { recursive: true });
    } catch (error) {
      if (error?.code !== "EEXIST") throw error;
    }
    const details = await stat(conflictPath).catch(() => null);
    if (details?.isFile()) {
      try {
        await writeFile(conflictPath, event, "utf8");
        return;
      } catch (error) {
        if (error?.code === "ENOENT") continue;
        throw error;
      }
    }
    if (!details?.isDirectory()) continue;
    try {
      await writeFile(path.join(conflictPath, `${randomUUID()}.conflict`), event, { flag: "wx" });
      return;
    } catch (error) {
      if (["ENOENT", "ENOTDIR", "EEXIST"].includes(error?.code)) continue;
      throw error;
    }
  }
}

async function recordPromptAcknowledgement(conflictPath, lockToken) {
  await mkdir(conflictPath, { recursive: true });
  await writeFile(path.join(conflictPath, `${randomUUID()}.ack`), `${JSON.stringify({
    kind: "ACK", lock_token: lockToken,
  })}\n`, { flag: "wx" });
}

async function registerPromptIntent(intentDir, token) {
  await mkdir(intentDir, { recursive: true });
  const intentPath = path.join(intentDir, `${token}.intent`);
  await writeFile(intentPath, `${JSON.stringify({
    token, pid: process.pid, created_at_ms: Date.now(),
  })}\n`, { flag: "wx" });
  return intentPath;
}

async function assertPromptIntentOwner(intent) {
  try {
    const metadata = JSON.parse(await readFile(intent.intentPath, "utf8"));
    if (metadata?.token !== intent.token) throw new Error("PROMPT_ORDER_AMBIGUOUS");
  } catch (error) {
    if (error?.message === "PROMPT_ORDER_AMBIGUOUS") throw error;
    throw new Error("PROMPT_ORDER_AMBIGUOUS", { cause: error });
  }
}

async function hasPromptIntents(intentDir, exceptToken = null) {
  try {
    return (await readdir(intentDir)).some((name) => (
      name.endsWith(".intent") && name !== `${exceptToken}.intent`
    ));
  } catch (error) {
    if (error?.code === "ENOENT") return false;
    throw error;
  }
}

async function claimedConflictNeedsAcknowledgement(claimedPath) {
  const details = await stat(claimedPath);
  const files = details.isDirectory()
    ? (await readdir(claimedPath)).map((name) => path.join(claimedPath, name))
    : [claimedPath];
  if (files.length === 0) return true;
  for (const filePath of files) {
    try {
      const event = JSON.parse(await readFile(filePath, "utf8"));
      if (event?.kind !== "ACK") return true;
    } catch {
      return true;
    }
  }
  return false;
}

async function orphanedClaimedConflictPaths(conflictPath) {
  const directory = path.dirname(conflictPath);
  const prefix = `${path.basename(conflictPath)}.claimed-`;
  try {
    return (await readdir(directory))
      .filter((name) => name.startsWith(prefix))
      .map((name) => path.join(directory, name));
  } catch (error) {
    if (error?.code === "ENOENT") return [];
    throw error;
  }
}

async function recoverOrphanedClaimedConflicts(conflictPath, lockToken) {
  for (const claimedPath of await orphanedClaimedConflictPaths(conflictPath)) {
    await recordPromptConflict(conflictPath, lockToken);
    await rm(claimedPath, { recursive: true, force: true });
  }
}

async function recoverStalePromptIntents(lock) {
  let names;
  try {
    names = await readdir(lock.intentDir);
  } catch (error) {
    if (error?.code === "ENOENT") return;
    throw error;
  }
  for (const name of names) {
    if (!name.endsWith(".intent") || name === `${lock.token}.intent`) continue;
    const intentPath = path.join(lock.intentDir, name);
    let metadata = null;
    try {
      metadata = JSON.parse(await readFile(intentPath, "utf8"));
    } catch {
      // 损坏的陈旧意图仍须先转成冲突证据，不能永久阻塞。
    }
    const details = await stat(intentPath).catch(() => null);
    if (!details) continue;
    const createdAt = Number.isFinite(metadata?.created_at_ms)
      ? metadata.created_at_ms : details.mtimeMs;
    const age = Date.now() - createdAt;
    const stale = age > PROMPT_LOCK_STALE_MS || age < -PROMPT_LOCK_STALE_MS;
    if (!stale) continue;
    await recordPromptConflict(lock.conflictPath, lock.token);
    await rm(intentPath, { force: true });
  }
}

async function createPromptClaimBarrier(conflictPath, token) {
  try {
    await mkdir(conflictPath);
  } catch (error) {
    if (error?.code !== "EEXIST") throw error;
  }
  const claimPath = path.join(conflictPath, `${token}.claim`);
  await writeFile(claimPath, `${JSON.stringify({ kind: "CLAIM", lock_token: token })}\n`, {
    flag: "wx",
  });
  return claimPath;
}

async function conflictHasOtherEvents(conflictPath, claimPath) {
  try {
    const details = await stat(conflictPath);
    if (!details.isDirectory()) return true;
    return (await readdir(conflictPath)).some((name) => path.join(conflictPath, name) !== claimPath);
  } catch (error) {
    if (error?.code === "ENOENT") return false;
    throw error;
  }
}

async function markLatestPromptAmbiguous(markerPath) {
  let marker;
  try {
    marker = JSON.parse(await readFile(markerPath, "utf8"));
  } catch (error) {
    if (error?.code === "ENOENT") return;
    throw error;
  }
  await writeFile(markerPath, `${JSON.stringify({ ...marker, status: "AMBIGUOUS" })}\n`, "utf8");
}

async function acquirePromptLock(markerPath, options = {}, registeredIntent = null) {
  const { lockPath, conflictPath, intentDir } = promptCoordinationPaths(markerPath);
  const token = registeredIntent?.token ?? randomUUID();
  const intentPath = registeredIntent?.intentPath ?? await registerPromptIntent(intentDir, token);
  await assertPromptIntentOwner({ intentPath, token });
  while (true) {
    try {
      await mkdir(lockPath);
    } catch (error) {
      if (error?.code !== "EEXIST") {
        await rm(intentPath, { force: true });
        await rmdir(intentDir).catch(() => {});
        throw error;
      }
      await recordPromptConflict(conflictPath, await currentPromptLockToken(lockPath));
      const lockAge = await promptLockAgeMs(lockPath);
      if (lockAge !== null && lockAge > PROMPT_LOCK_STALE_MS) {
        try {
          await rm(lockPath, { recursive: true, force: true });
          await new Promise((resolve) => setTimeout(resolve, PROMPT_CONFLICT_QUIET_MS));
          continue;
        } catch (recoveryError) {
          if (!["ENOENT", "EEXIST", "EPERM"].includes(recoveryError?.code)) throw recoveryError;
        }
      }
      await rm(intentPath, { force: true });
      await rmdir(intentDir).catch(() => {});
      throw new Error("PROMPT_ORDER_AMBIGUOUS");
    }
    const ownerPath = path.join(lockPath, `${token}.owner`);
    const lock = { lockPath, conflictPath, intentDir, intentPath, ownerPath, token };
    try {
      await writeFile(ownerPath, `${JSON.stringify({ token, created_at_ms: Date.now() })}\n`, {
        encoding: "utf8", flag: "wx",
      });
      await assertPromptIntentOwner(lock);
      await recoverStalePromptIntents(lock);
      await recoverOrphanedClaimedConflicts(conflictPath, token);
      if (await pathExists(conflictPath)) {
        const claimedConflictPath = `${conflictPath}.claimed-${token}`;
        await options.beforeConflictClaim?.({ conflictPath, lockPath, token });
        try {
          await rename(conflictPath, claimedConflictPath);
        } catch (error) {
          throw new Error("PROMPT_ORDER_AMBIGUOUS", { cause: error });
        }
        let claimPath;
        try {
          claimPath = await createPromptClaimBarrier(conflictPath, token);
        } catch (error) {
          if (!await pathExists(conflictPath)) {
            await rename(claimedConflictPath, conflictPath).catch(() => {});
          }
          throw error;
        }
        await new Promise((resolve) => setTimeout(resolve, PROMPT_CONFLICT_QUIET_MS));
        const needsAcknowledgement = await claimedConflictNeedsAcknowledgement(claimedConflictPath);
        const newerConflictExists = await conflictHasOtherEvents(conflictPath, claimPath)
          || await hasPromptIntents(intentDir, token);
        if (newerConflictExists || needsAcknowledgement) {
          await options.beforeConflictAcknowledgement?.({ conflictPath, lockPath, token });
          await recordPromptAcknowledgement(conflictPath, token);
          await rm(claimPath, { force: true });
          await rm(claimedConflictPath, { recursive: true, force: true });
          throw new Error("PROMPT_ORDER_AMBIGUOUS");
        }
        const settledBarrierPath = `${conflictPath}.claimed-${token}-barrier`;
        await options.beforeConflictSettlement?.({ conflictPath, lockPath, token });
        await rename(conflictPath, settledBarrierPath);
        const settledClaimPath = path.join(settledBarrierPath, path.basename(claimPath));
        await new Promise((resolve) => setTimeout(resolve, PROMPT_CONFLICT_QUIET_MS));
        const conflictDuringSettlement = await conflictHasOtherEvents(
          settledBarrierPath, settledClaimPath,
        ) || await pathExists(conflictPath) || await hasPromptIntents(intentDir, token);
        if (conflictDuringSettlement) {
          await recordPromptConflict(conflictPath, token);
          await rm(settledBarrierPath, { recursive: true, force: true });
          await rm(claimedConflictPath, { recursive: true, force: true });
          throw new Error("PROMPT_ORDER_AMBIGUOUS");
        }
        await markLatestPromptAmbiguous(markerPath);
        await rm(settledBarrierPath, { recursive: true, force: true });
        await rm(claimedConflictPath, { recursive: true, force: true });
      }
      await assertPromptLockOwner(lock);
      return lock;
    } catch (error) {
      await releasePromptLock(lock);
      throw error;
    }
  }
}

async function assertPromptLockOwner(lock) {
  try {
    const owner = JSON.parse(await readFile(lock.ownerPath, "utf8"));
    if (owner?.token !== lock.token) throw new Error("PROMPT_ORDER_AMBIGUOUS");
  } catch (error) {
    if (error?.message === "PROMPT_ORDER_AMBIGUOUS") throw error;
    throw new Error("PROMPT_ORDER_AMBIGUOUS", { cause: error });
  }
  await assertPromptIntentOwner(lock);
}

async function readLatestPromptMarker(markerPath) {
  const { lockPath, conflictPath, intentDir } = promptCoordinationPaths(markerPath);
  if (await pathExists(lockPath) || await pathExists(conflictPath) || await pathExists(intentDir)
    || (await orphanedClaimedConflictPaths(conflictPath)).length > 0) {
    throw new Error("PROMPT_ORDER_AMBIGUOUS");
  }
  let marker;
  try {
    marker = JSON.parse(await readFile(markerPath, "utf8"));
  } catch (error) {
    if (error?.code === "ENOENT") throw new Error("PROMPT_NOT_FOUND");
    throw new Error("PROMPT_ORDER_AMBIGUOUS", { cause: error });
  }
  if (await pathExists(lockPath) || await pathExists(conflictPath) || await pathExists(intentDir)
    || (await orphanedClaimedConflictPaths(conflictPath)).length > 0
    || marker?.status !== "READY" || !/^[a-f0-9]{64}$/u.test(marker.event_id ?? "")) {
    throw new Error("PROMPT_ORDER_AMBIGUOUS");
  }
  return marker;
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
  for (const field of ["project_root", "project_id", "session_id", "turn_id", "text", "captured_at"]) {
    if (typeof event[field] !== "string" || event[field].length === 0) {
      throw new Error(`PROMPT_${field.toUpperCase()}_REQUIRED`);
    }
  }
  const capturedAt = new Date(event.captured_at);
  if (Number.isNaN(capturedAt.getTime())) throw new Error("PROMPT_CAPTURED_AT_INVALID");
  const now = options.now ?? new Date();
  const id = eventId(event);
  const filePath = path.join(runtimeDataRoot, `${id}.json`);
  const promptDigest = digest(event.text);
  const stored = {
    project_root: event.project_root,
    project_id: event.project_id,
    session_id: event.session_id,
    turn_id: event.turn_id,
    prompt_digest: promptDigest,
    excerpt: event.text.slice(0, MAX_EXCERPT_LENGTH),
    authorization_claim: extractAuthorizationClaim(event.text),
  };
  let latestMarkerPath = null;
  let promptIntent = null;
  let promptLock = null;
  const latestMarker = {
    status: "PENDING",
    event_id: id,
    project_root: event.project_root,
    project_id: event.project_id,
    session_id: event.session_id,
  };
  if (options.trackLatest === true) {
    latestMarkerPath = latestPromptMarkerPath(runtimeDataRoot, event);
    const { intentDir } = promptCoordinationPaths(latestMarkerPath);
    const token = randomUUID();
    const intentPath = await registerPromptIntent(intentDir, token);
    promptIntent = { intentDir, intentPath, token };
  }
  try {
    await options.afterIntentRegistration?.({
      markerPath: latestMarkerPath,
      token: promptIntent?.token ?? null,
    });
    await cleanupExpired(runtimeDataRoot, now);
    await mkdir(runtimeDataRoot, { recursive: true });
    if (latestMarkerPath) {
      promptLock = await acquirePromptLock(latestMarkerPath, options, promptIntent);
      promptIntent = null;
    }
    if (latestMarkerPath) {
      await assertPromptLockOwner(promptLock);
      await writeFile(latestMarkerPath, `${JSON.stringify(latestMarker)}\n`, "utf8");
    }
    await writeFile(filePath, `${JSON.stringify(stored)}\n`, { encoding: "utf8", flag: "wx" });
    await utimes(filePath, capturedAt, capturedAt);
    if (latestMarkerPath) {
      await assertPromptLockOwner(promptLock);
      const status = await pathExists(promptLock.conflictPath)
        || await hasPromptIntents(promptLock.intentDir, promptLock.token)
        ? "AMBIGUOUS" : "READY";
      await writeFile(latestMarkerPath, `${JSON.stringify({ ...latestMarker, status })}\n`, "utf8");
      if (status === "READY" && (
        await pathExists(promptLock.conflictPath)
        || await hasPromptIntents(promptLock.intentDir, promptLock.token)
      )) {
        await writeFile(latestMarkerPath, `${JSON.stringify({ ...latestMarker, status: "AMBIGUOUS" })}\n`, "utf8");
      }
      await assertPromptLockOwner(promptLock);
    }
  } finally {
    if (promptLock) await releasePromptLock(promptLock);
    else await releasePromptIntent(promptIntent);
  }
  return {
    event_id: id,
    file_path: filePath,
    latest_marker_path: latestMarkerPath,
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
  return recordScopedPrompt({ ...event, project_root: request.project_root }, runtimeDataRoot, options);
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
      || entry.name.startsWith("activation-") || entry.name.startsWith("turn-")
      || entry.name.startsWith("prompt-latest-")) continue;
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
        project_root: stored.project_root,
        project_id: stored.project_id, session_id: stored.session_id,
        turn_id: stored.turn_id, prompt_digest: stored.prompt_digest,
      };
    }
  }
  throw new Error("PROMPT_NOT_FOUND");
}

export async function findAuthorizedPromptRef(runtimeDataRoot, context) {
  const markerPath = latestPromptMarkerPath(runtimeDataRoot, context);
  const marker = await readLatestPromptMarker(markerPath);
  if (marker.project_root !== context.project_root || marker.project_id !== context.project_id
    || marker.session_id !== context.session_id) throw new Error("PROMPT_NOT_FOUND");
  const filePath = path.join(runtimeDataRoot, `${marker.event_id}.json`);
  let stored;
  try {
    stored = JSON.parse(await readFile(filePath, "utf8"));
  } catch (error) {
    if (error?.code === "ENOENT") throw new Error("PROMPT_ORDER_AMBIGUOUS");
    throw new Error("PROMPT_RECORD_INVALID", { cause: error });
  }
  if (stored.project_root !== context.project_root || stored.project_id !== context.project_id
    || stored.session_id !== context.session_id
    || typeof stored.turn_id !== "string" || typeof stored.prompt_digest !== "string") {
    throw new Error("PROMPT_CONTEXT_MISMATCH");
  }
  const claim = stored.authorization_claim;
  if (!claim || claim.request_id !== context.request_id || claim.scope_digest !== context.scope_digest) {
    throw new Error("PROMPT_SCOPE_NOT_CONFIRMED");
  }
  if (claim.intent !== context.intent) {
    throw new Error(context.intent === "DECLINE" ? "EXPLICIT_DECLINE_REQUIRED" : "EXPLICIT_APPROVAL_REQUIRED");
  }
  return {
    event_id: marker.event_id,
    file_path: filePath,
    latest_marker_path: markerPath,
    project_root: stored.project_root,
    project_id: stored.project_id,
    session_id: stored.session_id,
    turn_id: stored.turn_id,
    prompt_digest: stored.prompt_digest,
  };
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
  if (stored.authorization_claim !== undefined) {
    const claim = stored.authorization_claim;
    if (!claim || typeof claim !== "object"
      || !["APPROVE", "DECLINE", "AMBIGUOUS", "NONE"].includes(claim.intent)
      || !(claim.request_id === null || typeof claim.request_id === "string")
      || !(claim.scope_digest === null || /^[a-f0-9]{64}$/u.test(claim.scope_digest))) {
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
  if (promptRef.latest_marker_path) {
    const marker = await readLatestPromptMarker(promptRef.latest_marker_path);
    if (marker.event_id !== promptRef.event_id) throw new Error("PROMPT_SUPERSEDED");
  }
  try {
    await rm(promptRef.file_path);
  } catch (error) {
    if (error?.code === "ENOENT") throw new Error("PROMPT_NOT_FOUND");
    throw error;
  }
  if (promptRef.latest_marker_path) {
    const marker = await readLatestPromptMarker(promptRef.latest_marker_path);
    if (marker.event_id !== promptRef.event_id) throw new Error("PROMPT_SUPERSEDED");
  }
}

export const promptPolicy = Object.freeze({ maxAgeMs: MAX_AGE_MS, maxExcerptLength: MAX_EXCERPT_LENGTH });
