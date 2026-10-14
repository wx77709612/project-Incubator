import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { lstat, mkdir, mkdtemp, readFile, readdir, realpath, rm } from "node:fs/promises";
import { createRequire } from "node:module";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const allowedRoots = new Set([
  ".codex-plugin", ".mcp.json", "hooks", "profiles", "scripts", "skills", "src",
  "package.json", "package-lock.json", "CANDIDATE.json", "node_modules",
]);

function check(condition, code) {
  if (!condition) throw new Error(code);
}

function inside(root, target) {
  const relative = path.relative(root, target);
  return relative !== ".." && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative);
}

async function reference(root, relative) {
  check(typeof relative === "string" && !path.isAbsolute(relative), "CANDIDATE_REFERENCE_ESCAPE");
  const requested = path.resolve(root, relative);
  check(inside(root, requested), "CANDIDATE_REFERENCE_ESCAPE");
  const resolved = await realpath(requested);
  check(inside(root, resolved), "CANDIDATE_REFERENCE_ESCAPE");
  check((await lstat(resolved)).isFile(), "CANDIDATE_REFERENCE_NOT_FILE");
  await readFile(resolved);
  return resolved;
}

async function json(root, relative) {
  return JSON.parse(await readFile(await reference(root, relative), "utf8"));
}

async function candidateFiles(root, relative = "") {
  const files = [];
  for (const entry of await readdir(path.join(root, relative), { withFileTypes: true })) {
    const name = relative ? `${relative}/${entry.name}` : entry.name;
    check(relative || allowedRoots.has(entry.name), "CANDIDATE_FORBIDDEN_CONTENT");
    check(!entry.isSymbolicLink(), "CANDIDATE_REFERENCE_ESCAPE");
    if (name === "node_modules") continue;
    check(!name.split("/").some((part) => /^(?:SPECS|tests|PROJECT_INCUBATOR|\.project-incubator|_V\d.*)$/iu.test(part)), "CANDIDATE_FORBIDDEN_CONTENT");
    if (entry.isDirectory()) files.push(...await candidateFiles(root, name));
    else {
      check(entry.isFile(), "CANDIDATE_REFERENCE_NOT_FILE");
      files.push(name);
    }
  }
  return files;
}

async function aggregateHash(root, files) {
  const records = [];
  for (const name of [...files].sort()) {
    const hash = createHash("sha256").update(await readFile(path.join(root, name))).digest("hex");
    records.push(`${name}:${hash}`);
  }
  // V1：UTF-8、正斜杠相对路径、字典序、LF 分隔，末尾不额外添加 LF。
  return createHash("sha256").update(records.join("\n"), "utf8").digest("hex");
}

async function structure(root) {
  const files = await candidateFiles(root);
  const manifest = await json(root, ".codex-plugin/plugin.json");
  const metadata = await json(root, "package.json");
  const lock = await json(root, "package-lock.json");
  const candidate = await json(root, "CANDIDATE.json");
  check(/^0\.3\.0\+codex\.\d{14}$/u.test(manifest.version), "CANDIDATE_VERSION_INVALID");
  check(metadata.version === "0.3.0" && lock.version === "0.3.0" && lock.packages?.[""]?.version === "0.3.0", "CANDIDATE_VERSION_INVALID");
  check(manifest.name === metadata.name && candidate.plugin === metadata.name && candidate.version === manifest.version, "CANDIDATE_IDENTITY_MISMATCH");
  check(manifest.skills === "./skills/" && manifest.mcpServers === "./.mcp.json", "CANDIDATE_ENTRY_INVALID");
  const mcp = await json(root, ".mcp.json");
  const definition = mcp.mcpServers?.project_incubator;
  check(definition?.command === "node" && definition.cwd === ".", "CANDIDATE_ENTRY_INVALID");
  assert.deepEqual(definition.args, ["./src/server.mjs"]);
  for (const name of ["src/server.mjs", "src/kernel/registry.mjs", "hooks/hooks.json", "hooks/user-prompt-submit.mjs", "scripts/verify-candidate.mjs"]) await reference(root, name);
  const registry = await json(root, "profiles/registry.json");
  check(registry.schema_version === "1.1", "CANDIDATE_REGISTRY_INVALID");
  for (const skill of registry.child_skills) await reference(root, skill.skill_path);
  for (const type of registry.project_types) {
    await reference(root, type.profile_path);
    await reference(root, type.workflow_module);
  }
  for (const host of registry.host_profiles) await reference(root, host.profile_path);
  check(!registry.host_profiles.some(({ project_type_id }) => project_type_id === "web-product"), "CANDIDATE_WEB_HOST_INVALID");
  const web = registry.project_types.find(({ id }) => id === "web-product");
  check(web?.child_skill_id === "web-product-incubator" && web.host_profile_requirement === "FORBIDDEN", "CANDIDATE_WEB_ID_INVALID");
  const profile = await json(root, web.profile_path);
  check(profile.schema_version === "1.0" && profile.project_type_id === web.id && profile.child_skill_id === web.child_skill_id, "CANDIDATE_WEB_ID_INVALID");
  assert.deepEqual(profile.stages, ["P0", "P1", "P2", "P3", "P4", "P5", "P6"]);
  const skill = registry.child_skills.find(({ id }) => id === web.child_skill_id);
  const text = await readFile(await reference(root, skill?.skill_path), "utf8");
  check(/^---\r?\nname: web-product-incubator\r?\n/u.test(text), "CANDIDATE_WEB_ID_INVALID");
  const workflow = await import(pathToFileURL(await reference(root, web.workflow_module)).href);
  check(typeof workflow.evaluateEntry === "function" && typeof workflow.evaluateTransition === "function", "CANDIDATE_WORKFLOW_INVALID");
  return {
    candidate_root: root,
    candidate_hash_algorithm: "SHA-256-AGGREGATE-V1",
    candidate_hash: await aggregateHash(root, files),
    manifest_version: manifest.version,
    package_version: metadata.version,
    source_fallback_detected: false,
    web_profile_verified: true,
    web_skill_verified: true,
    web_workflow_verified: true,
  };
}

async function candidateImport(root, moduleName) {
  const require = createRequire(path.join(root, "package.json"));
  const resolved = await realpath(require.resolve(moduleName));
  check(inside(path.join(root, "node_modules"), resolved), "CANDIDATE_DEPENDENCY_FALLBACK");
  return import(pathToFileURL(resolved).href);
}

function smokeState(timestamp) {
  return {
    schema_version: "1.1", project_id: "candidate-web-smoke", revision: 0,
    boundary: { objective: "候选包本地激活烟雾验证", supported: ["本地测试夹具"], excluded: ["真实项目验收", "公开部署"] },
    workflow: {
      stage: "P0", status: "ACTIVE", completed: [], allowed_next: ["P1"], return_stage: null,
      entry: { mode: "NEW_PROJECT", initial_stage: "P0", assessment_summary: "最小测试夹具，仅验证候选包控制语义。", evidence_refs: [], assessed_at: timestamp },
    },
    capabilities: [], decisions: { active: [], archive_ref: null }, assumptions: [],
    plan: { current_action: "验证候选激活", next_action: "执行独立真实项目验收", completion_conditions: ["Receipt Read-back 成功"] },
    gates: [], risks: [], pending_requests: [], baselines: [],
    human_validation: { limit: "UNSET", consumed: 0 },
    last_change: { operation: "INITIALIZE_PROJECT", changed_at: timestamp, summary: "候选烟雾验证" }, archive_refs: [],
  };
}

async function full(root, managedRoot) {
  check(!inside(root, managedRoot) && !inside(managedRoot, root), "CANDIDATE_MANAGED_ROOT_INVALID");
  await mkdir(managedRoot, { recursive: true });
  check((await readdir(managedRoot)).length === 0, "CANDIDATE_MANAGED_ROOT_NOT_EMPTY");
  const { loadRegistry, loadWorkflowEvaluators } = await import(pathToFileURL(await reference(root, "src/kernel/registry.mjs")).href);
  await loadWorkflowEvaluators(root, await loadRegistry(root));
  const { Client } = await candidateImport(root, "@modelcontextprotocol/sdk/client/index.js");
  const { getDefaultEnvironment, StdioClientTransport } = await candidateImport(root, "@modelcontextprotocol/sdk/client/stdio.js");
  const { handleUserPromptSubmit } = await import(pathToFileURL(await reference(root, "hooks/user-prompt-submit.mjs")).href);
  const pluginData = await mkdtemp(path.join(os.tmpdir(), "candidate-verifier-runtime-"));
  const client = new Client({ name: "project-incubator-candidate-verifier", version: "1.0.0" });
  const definition = (await json(root, ".mcp.json")).mcpServers.project_incubator;
  const transport = new StdioClientTransport({
    command: process.execPath, args: definition.args, cwd: root,
    env: { ...getDefaultEnvironment(), PLUGIN_DATA: pluginData }, stderr: "pipe",
  });
  let stderr = "";
  transport.stderr?.on("data", (chunk) => { stderr += chunk.toString(); });
  const call = async (name, args) => {
    const result = await client.callTool({ name, arguments: args });
    check(!result.isError, result.structuredContent?.error?.code ?? "CANDIDATE_MCP_CALL_FAILED");
    return result.structuredContent;
  };
  try {
    await client.connect(transport);
    const version = client.getServerVersion()?.version;
    check(version === "0.3.0", "CANDIDATE_MCP_VERSION_INVALID");
    const route = async (type, host) => (await call("propose_route", { project_root: managedRoot, project_type_id: type, host_profile_id: host })).route;
    const mod = await route("mod", "sims-4");
    const desktop = await route("desktop-product", "windows-desktop");
    const web = await route("web-product", null);
    assert.deepEqual(mod, { project_type_id: "mod", child_skill_id: "mod-incubator", host_profile_id: "sims-4" });
    assert.deepEqual(desktop, { project_type_id: "desktop-product", child_skill_id: "desktop-product-incubator", host_profile_id: "windows-desktop" });
    assert.deepEqual(web, { project_type_id: "web-product", child_skill_id: "web-product-incubator", host_profile_id: null });
    for (const host of ["sims-4", "windows-desktop", "browser", "unknown-host"]) {
      const rejected = await client.callTool({ name: "propose_route", arguments: { project_root: managedRoot, project_type_id: "web-product", host_profile_id: host } });
      check(rejected.isError && rejected.structuredContent?.error?.code === "HOST_PROFILE_FORBIDDEN", "CANDIDATE_HOST_FORBIDDEN_FAILED");
    }
    const timestamp = new Date().toISOString();
    const request = await call("prepare_activation", {
      project_root: managedRoot, project_id: "candidate-web-smoke", project_type_id: "web-product", host_profile_id: null,
      session_id: "candidate-smoke", summary: "批准隔离测试夹具激活，仅用于候选包烟雾验证。", state: smokeState(timestamp),
      product_decisions: [{ decision_id: "candidate-boundary", statement: "仅验证本地测试夹具控制语义，不构成真实项目或生产验收。" }],
    });
    // 模拟 Maker 输入仅用于此临时烟雾夹具，不能作为 Stage H 的真实 Maker Authorization。
    await handleUserPromptSubmit({
      cwd: managedRoot, session_id: "candidate-smoke", turn_id: "activation",
      prompt: `我明确批准 ${request.request_id}，scope_digest: ${request.scope_digest}`, timestamp,
    }, { runtimeDataRoot: path.join(pluginData, "runtime-events"), now: new Date(timestamp) });
    const initialized = await call("initialize_project", {
      project_root: managedRoot, request_id: request.request_id, scope_digest: request.scope_digest,
      session_id: "candidate-smoke", turn_id: "activation",
    });
    const readback = await call("get_project_state", { project_root: managedRoot });
    assert.deepEqual(readback.activation, initialized.activation);
    check(readback.activation.plugin_version === "0.3.0" && readback.activation.host_profile_id === null, "CANDIDATE_ACTIVATION_INVALID");
    check(readback.state.schema_version === "1.1" && readback.state.decisions.active[0].authorization_ref === initialized.receipt.authorization_ref.authorization_id, "CANDIDATE_READBACK_INVALID");
    const receipt = await call("verify_receipt", { project_root: managedRoot, receipt_id: initialized.receipt.receipt_id });
    check(receipt.verified === true, "CANDIDATE_RECEIPT_INVALID");
    return { mcp_server_version: version, mod_route: mod, desktop_route: desktop, web_route: web, host_forbidden_verified: true, activation: readback.activation, receipt_verified: true };
  } catch (error) {
    if (stderr) process.stderr.write(stderr);
    throw error;
  } finally {
    await client.close();
    await transport.close();
    await rm(pluginData, { recursive: true, force: true });
  }
}

try {
  const [mode, candidateRoot, managedRoot, ...extra] = process.argv.slice(2);
  check(extra.length === 0 && candidateRoot && (["--structure-only", "--full"].includes(mode)), "CANDIDATE_ARGUMENTS_INVALID");
  check(mode === "--full" ? Boolean(managedRoot) : !managedRoot, "CANDIDATE_ARGUMENTS_INVALID");
  const root = await realpath(path.resolve(candidateRoot));
  const result = await structure(root);
  if (mode === "--full") Object.assign(result, await full(root, path.resolve(managedRoot)));
  process.stdout.write(`${JSON.stringify(result)}\n`);
} catch (error) {
  process.stdout.write(`${JSON.stringify({ error: { code: error.code ?? error.message, message: error.message } })}\n`);
  process.exitCode = 1;
}
