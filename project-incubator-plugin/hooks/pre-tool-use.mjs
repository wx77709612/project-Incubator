import path from "node:path";
import { pathToFileURL } from "node:url";

import { findActivatedProjectRoot, isProtectedProjectPath } from "../src/kernel/project-root.mjs";

const CONTROL_PATTERN = /(?:^|[\s\\/])\.project-incubator[\\/](?:activation|state|latest-receipt)\.json(?:$|[\s'"`])/iu;
const KERNEL_TOOL_PREFIXES = ["mcp__project_incubator__", "mcp__project-incubator-plugin__"];

function strings(value, key = "") {
  if (typeof value === "string") return [{ key, value }];
  if (Array.isArray(value)) return value.flatMap((item) => strings(item, key));
  if (value && typeof value === "object") {
    return Object.entries(value).flatMap(([childKey, child]) => strings(child, childKey));
  }
  return [];
}

function looksLikePathField(key) {
  return /(?:path|file|target|destination|source)/iu.test(key);
}

export async function handlePreToolUse(event) {
  const root = await findActivatedProjectRoot(event.cwd ?? ".");
  if (!root) return {};
  if (KERNEL_TOOL_PREFIXES.some((prefix) => event.tool_name?.startsWith(prefix))) return {};

  for (const item of strings(event.tool_input)) {
    const normalized = item.value.replaceAll("\\", "/");
    if (CONTROL_PATTERN.test(item.value) || CONTROL_PATTERN.test(normalized)) {
      return deny();
    }
    if (looksLikePathField(item.key)) {
      const candidate = path.isAbsolute(item.value) ? item.value : path.resolve(root, item.value);
      if (await isProtectedProjectPath(root, candidate)) return deny();
    }
  }
  return {};
}

function deny() {
  return {
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Project Incubator 权威状态只能通过受控 Kernel MCP 修改。",
    },
  };
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export async function runCli() {
  process.stdout.write(`${JSON.stringify(await handlePreToolUse(await readStdin()))}\n`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  runCli().catch((error) => {
    process.stdout.write(`${JSON.stringify(deny(error.message))}\n`);
    process.exitCode = 1;
  });
}
