import { readFile, readdir } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

import { findActivatedProjectRoot } from "../src/kernel/project-root.mjs";
import { resolveRuntimeDataRoot } from "../src/kernel/runtime-paths.mjs";
import { readProjectSnapshot, verifyLatestReceipt } from "../src/kernel/state-store.mjs";
import { turnMarkerPath } from "./user-prompt-submit.mjs";

function block(reason) {
  return { decision: "block", reason: `Project Incubator 无法闭合本轮：${reason}` };
}

function closureFailure(event, reason) {
  if (event.stop_hook_active === true) {
    return {
      continue: true,
      systemMessage: `Project Incubator 闭合检查仍未通过，已停止重复阻断：${reason}`,
    };
  }
  return block(reason);
}

function isValidSessionMarker(marker, projectId, sessionId) {
  return marker !== null
    && typeof marker === "object"
    && marker.project_id === projectId
    && marker.session_id === sessionId
    && typeof marker.turn_id === "string"
    && marker.turn_id.length > 0
    && Number.isInteger(marker.baseline_revision)
    && (marker.baseline_receipt_id === null || typeof marker.baseline_receipt_id === "string")
    && typeof marker.started_at === "string"
    && Number.isFinite(Date.parse(marker.started_at));
}

async function findLatestSessionMarker(runtimeDataRoot, projectId, sessionId) {
  let names;
  try {
    names = await readdir(runtimeDataRoot);
  } catch (error) {
    if (error?.code === "ENOENT") return null;
    throw error;
  }
  let latest = null;
  for (const name of names) {
    if (!/^turn-[a-f0-9]{64}\.json$/u.test(name)) continue;
    try {
      const marker = JSON.parse(await readFile(path.join(runtimeDataRoot, name), "utf8"));
      if (!isValidSessionMarker(marker, projectId, sessionId)) continue;
      const startedAt = Date.parse(marker.started_at);
      if (latest === null || startedAt > latest.startedAt
        || (startedAt === latest.startedAt && name > latest.name)) {
        latest = { marker, name, startedAt };
      }
    } catch (error) {
      if (error?.code !== "ENOENT" && !(error instanceof SyntaxError)) throw error;
    }
  }
  return latest?.marker ?? null;
}

async function readStopMarker(runtimeDataRoot, projectId, sessionId, turnId) {
  try {
    return {
      exact: true,
      marker: JSON.parse(await readFile(
        turnMarkerPath(runtimeDataRoot, projectId, sessionId, turnId), "utf8",
      )),
    };
  } catch (error) {
    if (error?.code !== "ENOENT") throw error;
  }
  const marker = await findLatestSessionMarker(runtimeDataRoot, projectId, sessionId);
  if (!marker) throw new Error("轮次 marker 缺失且没有可验证的同 session 基线");
  return { exact: false, marker };
}

export async function handleStop(event, options = {}) {
  const root = await findActivatedProjectRoot(event.cwd ?? ".");
  if (!root) return { continue: true };
  try {
    const snapshot = await readProjectSnapshot(root);
    const verified = await verifyLatestReceipt(root);
    if (!verified.verified) return closureFailure(event, `Receipt 校验失败（${verified.reason}）`);
    const runtimeDataRoot = options.runtimeDataRoot ?? resolveRuntimeDataRoot(options.env ?? process.env);
    const { exact, marker } = await readStopMarker(
      runtimeDataRoot, snapshot.state.project_id, event.session_id, event.turn_id,
    );
    if (!exact) {
      if (snapshot.state.revision !== marker.baseline_revision) {
        return closureFailure(event, "轮次 marker 缺失且同 session 基线 revision 不匹配");
      }
      if (snapshot.receipt.receipt_id !== marker.baseline_receipt_id) {
        return closureFailure(event, "轮次 marker 缺失且同 session 基线 Receipt 不匹配");
      }
      return { continue: true };
    }
    if (marker.project_id !== snapshot.state.project_id
      || marker.session_id !== event.session_id
      || marker.turn_id !== event.turn_id) return closureFailure(event, "轮次来源不匹配");
    if (!Number.isInteger(marker.baseline_revision)) return closureFailure(event, "轮次基线损坏");
    if (snapshot.state.revision < marker.baseline_revision) return closureFailure(event, "项目 revision 回退");
    if (snapshot.state.revision === marker.baseline_revision) return { continue: true };
    if (new Date(snapshot.receipt.committed_at) <= new Date(marker.started_at)) {
      return closureFailure(event, "最新 Receipt 不属于当前轮次");
    }
    const message = event.last_assistant_message ?? "";
    if (!message.includes(snapshot.receipt.receipt_id)) {
      return closureFailure(event, `状态已变化，完成报告必须包含 receipt_id ${snapshot.receipt.receipt_id}`);
    }
    return { continue: true };
  } catch (error) {
    return closureFailure(event, error.message);
  }
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export async function runCli() {
  process.stdout.write(`${JSON.stringify(await handleStop(await readStdin()))}\n`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  runCli().catch((error) => {
    process.stdout.write(`${JSON.stringify(block(error.message))}\n`);
    process.exitCode = 1;
  });
}
