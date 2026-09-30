import path from "node:path";
import { pathToFileURL } from "node:url";

import { findActivatedProjectRoot, isProtectedProjectPath } from "../src/kernel/project-root.mjs";

const CONTROL_PATTERN = /(?:^|[^a-z0-9_.-])\.project-incubator[\\/](?:activation|state|latest-receipt)\.json(?=$|[^a-z0-9_.-])/iu;
const KERNEL_TOOL_PREFIXES = ["mcp__project_incubator__", "mcp__project-incubator-plugin__"];
const READ_ONLY_TOOL_PATTERN = /^(?:.*__)?(?:read_file|read_text_file|read_multiple_files|get_file_info)$/iu;
const SHELL_TOOL_NAMES = new Set(["bash", "exec_command"]);
const READ_ONLY_POWERSHELL_COMMANDS = new Set([
  "convertfrom-json",
  "convertto-json",
  "format-list",
  "format-table",
  "get-childitem",
  "get-content",
  "get-filehash",
  "get-item",
  "measure-object",
  "select-object",
  "sort-object",
  "test-path",
  "write-output",
]);

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

function isReadOnlyPowerShell(command) {
  if (!command || /[<>]/u.test(command)) return false;
  if (/[`(){}]/u.test(command)) return false;
  if (/::(?:write|append|delete|move|copy|replace)\w*\s*\(/iu.test(command)) return false;

  const segments = command.split(/[;|&\r\n]+/u).map((segment) => segment.trim()).filter(Boolean);
  if (segments.length === 0) return false;

  return segments.every((segment) => {
    const match = /^(?:&\s*)?([a-z][a-z0-9-]*)\b/iu.exec(segment);
    return Boolean(match && READ_ONLY_POWERSHELL_COMMANDS.has(match[1].toLowerCase()));
  });
}

function isReadOnlyAccess(event) {
  const toolName = event.tool_name?.toLowerCase() ?? "";
  if (READ_ONLY_TOOL_PATTERN.test(toolName)) return true;
  if (!SHELL_TOOL_NAMES.has(toolName)) return false;

  const command = event.tool_input?.command ?? event.tool_input?.cmd;
  return typeof command === "string" && isReadOnlyPowerShell(command);
}

async function referencesProtectedState(root, toolInput) {
  for (const item of strings(toolInput)) {
    const normalized = item.value.replaceAll("\\", "/");
    if (CONTROL_PATTERN.test(item.value) || CONTROL_PATTERN.test(normalized)) return true;
    if (looksLikePathField(item.key)) {
      const candidate = path.isAbsolute(item.value) ? item.value : path.resolve(root, item.value);
      if (await isProtectedProjectPath(root, candidate)) return true;
    }
  }
  return false;
}

export async function handlePreToolUse(event) {
  const root = await findActivatedProjectRoot(event.cwd ?? ".");
  if (!root) return {};
  if (KERNEL_TOOL_PREFIXES.some((prefix) => event.tool_name?.startsWith(prefix))) return {};

  if (!await referencesProtectedState(root, event.tool_input)) return {};
  return isReadOnlyAccess(event) ? {} : deny();
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
