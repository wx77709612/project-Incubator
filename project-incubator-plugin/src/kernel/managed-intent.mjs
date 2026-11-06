import { createHash } from "node:crypto";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";

import { canonicalProjectPath } from "./project-root.mjs";

function markerPath(runtimeDataRoot, sessionId) {
  const key = createHash("sha256").update(sessionId, "utf8").digest("hex");
  return path.join(runtimeDataRoot, `managed-intent-${key}.json`);
}

export async function recordManagedIntent(runtimeDataRoot, cwd, sessionId) {
  if (!runtimeDataRoot || !sessionId) return;
  const projectRoot = await canonicalProjectPath(cwd);
  await mkdir(runtimeDataRoot, { recursive: true });
  await writeFile(markerPath(runtimeDataRoot, sessionId), `${JSON.stringify({ project_root: projectRoot, session_id: sessionId })}\n`, "utf8");
}

export async function withdrawManagedIntent(runtimeDataRoot, sessionId) {
  if (!runtimeDataRoot || !sessionId) return;
  await rm(markerPath(runtimeDataRoot, sessionId), { force: true });
}

export async function hasManagedIntent(runtimeDataRoot, cwd, sessionId) {
  if (!runtimeDataRoot || !sessionId) return false;
  let marker;
  try {
    marker = JSON.parse(await readFile(markerPath(runtimeDataRoot, sessionId), "utf8"));
  } catch (error) {
    if (error?.code === "ENOENT") return false;
    throw error;
  }
  const candidate = await canonicalProjectPath(cwd);
  const relative = path.relative(marker.project_root, candidate);
  return marker.session_id === sessionId
    && (relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative)));
}
