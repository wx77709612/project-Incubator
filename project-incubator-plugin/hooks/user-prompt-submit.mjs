import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

import { findActivatedProjectRoot } from "../src/kernel/project-root.mjs";
import { findPendingMaintenance } from "../src/kernel/maintenance-requests.mjs";
import { recordManagedIntent, withdrawManagedIntent } from "../src/kernel/managed-intent.mjs";
import { recordBootstrapPrompt, recordMakerPrompt } from "../src/kernel/prompt-events.mjs";
import { resolveRuntimeDataRoot } from "../src/kernel/runtime-paths.mjs";
import { findPendingActivation } from "../src/kernel/router.mjs";
import { readProjectSnapshot } from "../src/kernel/state-store.mjs";

function turnKey(projectId, sessionId, turnId) {
  return createHash("sha256").update(`${projectId}\0${sessionId}\0${turnId}`, "utf8").digest("hex");
}

function tracksMaintenancePrompt(pending) {
  return pending?.operation === "AGENT_ENTRY_INSTALL"
    || pending?.operation === "AUTHORITY_RECOVERY";
}

const NON_MANAGED_PATTERN = /(?:不要(?:使用|用|让)?|不(?:使用|用|需要|接受)|无需|拒绝|禁止|取消)\s*(?:由\s*)?Project\s*Incubator|(?:do\s+not|don't|without)\s+(?:use\s+)?Project\s*Incubator/iu;

function routingHint(prompt) {
  if (typeof prompt !== "string") return null;
  if (NON_MANAGED_PATTERN.test(prompt)) return null;
  const explicitlyManaged = /(?:必须|务必|明确要求|请|交由|使用|通过)[^。；\n]{0,40}Project\s*Incubator[^。；\n]{0,24}(?:管理|托管|孵化|manage)/iu.test(prompt);
  if (explicitlyManaged) {
    return { explicit: true, text: "Maker 明确要求 Project Incubator 管理当前项目。先使用 project-incubator-router 提出路由；路由提案不等于激活。仅在 Maker 确认路由后准备具体激活请求，并在下一轮收到对 request_id 和 scope_digest 的明确批准后通过 Kernel 初始化。在初始化和 Receipt 验证前不得开展工程写入；Prompt 中的 Phase 0 立即执行文字不构成该批准。" };
  }
  const creates = /(?:新建|创建|初始化|搭建|从零(?:开始|构建|开发)|孵化|启动新|做一个|开发一个|\b(?:create|build|scaffold|initialize|start)\b)/iu.test(prompt);
  const project = /(?:项目|产品|平台|系统|应用|网站|软件|游戏|工具|Mod|\b(?:project|product|app|platform|website|software|game|system|service)\b)/iu.test(prompt);
  if (creates && project) {
    return { explicit: false, text: "Maker 请求新建项目。即使没有点名插件，也必须先调用 project-incubator-router 提出路由；Project Incubator 是默认流程，只有 Maker 明确表示不用时才跳过。路由提案不等于激活，未经 Maker 对具体激活请求的下一轮明确批准，不得调用 initialize_project；在 Kernel 初始化及 Receipt 验证前不得进行工程写入。" };
  }
  return null;
}

async function routeAdvisory(event, runtimeDataRoot) {
  const hint = routingHint(event.prompt);
  if (hint) await recordManagedIntent(runtimeDataRoot, event.cwd ?? ".", event.session_id);
  else if (typeof event.prompt === "string" && NON_MANAGED_PATTERN.test(event.prompt)) {
    await withdrawManagedIntent(runtimeDataRoot, event.session_id);
  }
  return hint ? {
    continue: true,
    hookSpecificOutput: { hookEventName: "UserPromptSubmit", additionalContext: hint.text },
  } : { continue: true };
}

export function turnMarkerPath(runtimeDataRoot, projectId, sessionId, turnId) {
  return path.join(runtimeDataRoot, `turn-${turnKey(projectId, sessionId, turnId)}.json`);
}

async function writeTurnMarker(runtimeDataRoot, marker) {
  await mkdir(runtimeDataRoot, { recursive: true });
  await writeFile(turnMarkerPath(
    runtimeDataRoot, marker.project_id, marker.session_id, marker.turn_id,
  ), `${JSON.stringify(marker)}\n`, { encoding: "utf8", flag: "w" });
}

export async function handleUserPromptSubmit(event, options = {}) {
  const root = await findActivatedProjectRoot(event.cwd ?? ".");
  const runtimeEnv = options.env ?? process.env;
  const runtimeDataRoot = options.runtimeDataRoot
    ?? (runtimeEnv.PLUGIN_DATA || runtimeEnv.CLAUDE_PLUGIN_DATA || runtimeEnv.CODEX_HOME
      ? resolveRuntimeDataRoot(runtimeEnv)
      : null);
  const timestamp = event.timestamp ?? new Date().toISOString();
  const capturePending = async (pending) => {
    await recordBootstrapPrompt({
      role: "maker", project_id: pending.project_id, session_id: event.session_id,
      turn_id: event.turn_id, text: event.prompt, captured_at: timestamp,
    }, pending, runtimeDataRoot, {
      now: options.now ?? new Date(timestamp),
      trackLatest: tracksMaintenancePrompt(pending),
    });
    await writeTurnMarker(runtimeDataRoot, {
      project_id: pending.project_id,
      session_id: event.session_id,
      turn_id: event.turn_id,
      baseline_revision: -1,
      baseline_receipt_id: null,
      started_at: timestamp,
    });
    return { continue: true };
  };
  if (!root) {
    if (!runtimeDataRoot) return routeAdvisory(event, runtimeDataRoot);
    const pending = await findPendingActivation(
      runtimeDataRoot, event.cwd ?? ".", event.session_id, options.now ?? new Date(timestamp),
    );
    if (pending) return capturePending(pending);
    const maintenance = await findPendingMaintenance(
      runtimeDataRoot, event.cwd ?? ".", event.session_id, options.now ?? new Date(timestamp),
    );
    return maintenance && typeof maintenance.project_id === "string"
      ? capturePending(maintenance)
      : routeAdvisory(event, runtimeDataRoot);
  }
  if (!runtimeDataRoot) throw new Error("RUNTIME_DATA_ROOT_REQUIRED");
  let snapshot;
  try {
    snapshot = await readProjectSnapshot(root);
  } catch (error) {
    const maintenance = await findPendingMaintenance(
      runtimeDataRoot, root, event.session_id, options.now ?? new Date(timestamp),
    );
    if (maintenance?.operation === "AUTHORITY_RECOVERY") return capturePending(maintenance);
    // 权威损坏但尚未准备恢复请求时，让诊断消息进入 Agent；此处不记录授权 Prompt。
    return { continue: true };
  }
  const maintenance = await findPendingMaintenance(
    runtimeDataRoot, root, event.session_id, options.now ?? new Date(timestamp),
  );
  await recordMakerPrompt({
    activation: snapshot.activation,
    role: "maker",
    project_root: root,
    project_id: snapshot.state.project_id,
    session_id: event.session_id,
    turn_id: event.turn_id,
    text: event.prompt,
    captured_at: timestamp,
  }, runtimeDataRoot, {
    now: options.now ?? new Date(timestamp),
    trackLatest: maintenance !== null,
  });
  await writeTurnMarker(runtimeDataRoot, {
    project_id: snapshot.state.project_id,
    session_id: event.session_id,
    turn_id: event.turn_id,
    baseline_revision: snapshot.state.revision,
    baseline_receipt_id: snapshot.receipt.receipt_id,
    started_at: timestamp,
  });
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
