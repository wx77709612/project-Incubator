import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";

import { findActivatedProjectRoot } from "../src/kernel/project-root.mjs";
import { resolveRuntimeDataRoot } from "../src/kernel/runtime-paths.mjs";
import { readProjectSnapshot, verifyLatestReceipt } from "../src/kernel/state-store.mjs";
import { turnMarkerPath } from "./user-prompt-submit.mjs";

function block(reason) {
  return { decision: "block", reason: `Project Incubator 无法闭合本轮：${reason}` };
}

export async function handleStop(event, options = {}) {
  const root = await findActivatedProjectRoot(event.cwd ?? ".");
  if (!root) return { continue: true };
  try {
    const snapshot = await readProjectSnapshot(root);
    const verified = await verifyLatestReceipt(root);
    if (!verified.verified) return block(`Receipt 校验失败（${verified.reason}）`);
    const runtimeDataRoot = options.runtimeDataRoot ?? resolveRuntimeDataRoot(options.env ?? process.env);
    const markerRaw = await readFile(turnMarkerPath(
      runtimeDataRoot, snapshot.state.project_id, event.session_id, event.turn_id,
    ), "utf8");
    const marker = JSON.parse(markerRaw);
    if (marker.project_id !== snapshot.state.project_id
      || marker.session_id !== event.session_id
      || marker.turn_id !== event.turn_id) return block("轮次来源不匹配");
    if (!Number.isInteger(marker.baseline_revision)) return block("轮次基线损坏");
    if (snapshot.state.revision < marker.baseline_revision) return block("项目 revision 回退");
    if (snapshot.state.revision === marker.baseline_revision) return { continue: true };
    if (new Date(snapshot.receipt.committed_at) <= new Date(marker.started_at)) {
      return block("最新 Receipt 不属于当前轮次");
    }
    const message = event.last_assistant_message ?? "";
    if (!message.includes(snapshot.receipt.receipt_id)) {
      return block(`状态已变化，完成报告必须包含 receipt_id ${snapshot.receipt.receipt_id}`);
    }
    return { continue: true };
  } catch (error) {
    return block(error.message);
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
