import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

import { findActivatedProjectRoot } from "../src/kernel/project-root.mjs";
import { recordBootstrapPrompt, recordMakerPrompt } from "../src/kernel/prompt-events.mjs";
import { resolveRuntimeDataRoot } from "../src/kernel/runtime-paths.mjs";
import { findPendingActivation } from "../src/kernel/router.mjs";
import { readProjectSnapshot } from "../src/kernel/state-store.mjs";

function turnKey(projectId, sessionId, turnId) {
  return createHash("sha256").update(`${projectId}\0${sessionId}\0${turnId}`, "utf8").digest("hex");
}

export function turnMarkerPath(runtimeDataRoot, projectId, sessionId, turnId) {
  return path.join(runtimeDataRoot, `turn-${turnKey(projectId, sessionId, turnId)}.json`);
}

export async function handleUserPromptSubmit(event, options = {}) {
  const root = await findActivatedProjectRoot(event.cwd ?? ".");
  const runtimeDataRoot = options.runtimeDataRoot
    ?? (options.env?.CODEX_HOME || process.env.CODEX_HOME
      ? resolveRuntimeDataRoot(options.env ?? process.env)
      : null);
  const timestamp = event.timestamp ?? new Date().toISOString();
  if (!root) {
    if (!runtimeDataRoot) return { continue: true };
    const pending = await findPendingActivation(
      runtimeDataRoot, event.cwd ?? ".", event.session_id, options.now ?? new Date(timestamp),
    );
    if (!pending) return { continue: true };
    await recordBootstrapPrompt({
      role: "maker", project_id: pending.project_id, session_id: event.session_id,
      turn_id: event.turn_id, text: event.prompt, captured_at: timestamp,
    }, pending, runtimeDataRoot, { now: options.now ?? new Date(timestamp) });
    return { continue: true };
  }
  const snapshot = await readProjectSnapshot(root);
  if (!runtimeDataRoot) throw new Error("CODEX_HOME_REQUIRED");
  await recordMakerPrompt({
    activation: snapshot.activation,
    role: "maker",
    project_id: snapshot.state.project_id,
    session_id: event.session_id,
    turn_id: event.turn_id,
    text: event.prompt,
    captured_at: timestamp,
  }, runtimeDataRoot, { now: options.now ?? new Date(timestamp) });
  await mkdir(runtimeDataRoot, { recursive: true });
  await writeFile(turnMarkerPath(
    runtimeDataRoot, snapshot.state.project_id, event.session_id, event.turn_id,
  ), `${JSON.stringify({
    project_id: snapshot.state.project_id,
    session_id: event.session_id,
    turn_id: event.turn_id,
    baseline_revision: snapshot.state.revision,
    baseline_receipt_id: snapshot.receipt.receipt_id,
    started_at: timestamp,
  })}\n`, { encoding: "utf8", flag: "w" });
  return { continue: true };
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export async function runCli() {
  const result = await handleUserPromptSubmit(await readStdin());
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  runCli().catch((error) => {
    process.stdout.write(`${JSON.stringify({ continue: false, reason: `Project Incubator: ${error.message}` })}\n`);
    process.exitCode = 1;
  });
}
