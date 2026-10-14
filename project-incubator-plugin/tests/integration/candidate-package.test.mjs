import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { cp, mkdir, mkdtemp, readFile, readdir, realpath, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

const pluginRoot = path.resolve(import.meta.dirname, "../..");
const verifier = path.join(pluginRoot, "scripts/verify-candidate.mjs");

async function candidate(t) {
  const directory = await mkdtemp(path.join(os.tmpdir(), "candidate-package-test-"));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const root = path.join(directory, "plugin");
  const packed = spawnSync(process.execPath, ["scripts/package-candidate.mjs", root], { cwd: pluginRoot, encoding: "utf8" });
  assert.equal(packed.status, 0, packed.stderr);
  return { root, managed: path.join(directory, "managed") };
}

function verify(root, mode = "--structure-only", managed) {
  const result = spawnSync(process.execPath, [verifier, mode, root, ...(managed ? [managed] : [])], {
    cwd: os.tmpdir(), encoding: "utf8", timeout: 30000,
  });
  return { ...result, json: result.stdout.trim() ? JSON.parse(result.stdout) : null };
}

async function independentHash(root) {
  const files = await readdir(root, { recursive: true, withFileTypes: true });
  const relativeNames = files.filter((entry) => entry.isFile())
    .map((entry) => path.relative(root, path.join(entry.parentPath, entry.name)).split(path.sep).join("/"))
    .filter((name) => !name.startsWith("node_modules/")).sort();
  const records = await Promise.all(relativeNames.map(async (name) => `${name}:${createHash("sha256").update(await readFile(path.join(root, name))).digest("hex")}`));
  return createHash("sha256").update(records.join("\n"), "utf8").digest("hex");
}

test("候选结构模式从仓库外目录输出固定 JSON 和可独立重算的稳定聚合哈希", async (t) => {
  const { root } = await candidate(t);
  const result = verify(root);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(Object.keys(result.json).sort(), [
    "candidate_root", "candidate_hash_algorithm", "candidate_hash", "manifest_version", "package_version",
    "source_fallback_detected", "web_profile_verified", "web_skill_verified", "web_workflow_verified",
  ].sort());
  assert.equal(result.json.candidate_root, await realpath(root));
  assert.equal(result.json.candidate_hash_algorithm, "SHA-256-AGGREGATE-V1");
  assert.match(result.json.manifest_version, /^0\.3\.0\+codex\.\d{14}$/);
  assert.equal(result.json.package_version, "0.3.0");
  for (const name of ["web_profile_verified", "web_skill_verified", "web_workflow_verified"]) assert.equal(result.json[name], true);
  assert.equal(result.json.source_fallback_detected, false);
  assert.equal(result.json.candidate_hash, await independentHash(root));
  assert.equal(verify(root).json.candidate_hash, result.json.candidate_hash);
  await mkdir(path.join(root, "node_modules"));
  await writeFile(path.join(root, "node_modules/ignored.txt"), "依赖不进入聚合哈希");
  assert.equal(verify(root).json.candidate_hash, result.json.candidate_hash);
  await writeFile(path.join(root, "skills/web-product-incubator/SKILL.md"), `${await readFile(path.join(root, "skills/web-product-incubator/SKILL.md"), "utf8")}\n变更内容\n`);
  assert.notEqual(verify(root).json.candidate_hash, result.json.candidate_hash);
});

test("候选缺少 Web Profile、Skill、Workflow 或必要入口时失败关闭且不读取源码副本", async (t) => {
  for (const name of ["profiles/project-types/web-product.json", "skills/web-product-incubator/SKILL.md", "src/domains/web/workflow.mjs", ".mcp.json"]) {
    await t.test(name, async (t) => {
      const { root } = await candidate(t);
      await rm(path.join(root, name));
      const result = verify(root);
      assert.equal(result.status, 1);
      assert.ok(result.json?.error, result.stderr);
      assert.equal(result.json.web_skill_verified, undefined);
    });
  }
});

test("Registry 指向源码工作树的可读文件仍拒绝来源回退", async (t) => {
  const { root } = await candidate(t);
  const registryPath = path.join(root, "profiles/registry.json");
  const registry = JSON.parse(await readFile(registryPath, "utf8"));
  registry.child_skills.find(({ id }) => id === "web-product-incubator").skill_path = path.join(pluginRoot, "skills/web-product-incubator/SKILL.md");
  await writeFile(registryPath, JSON.stringify(registry));
  const result = verify(root);
  assert.equal(result.status, 1);
  assert.equal(result.json?.error?.code, "CANDIDATE_REFERENCE_ESCAPE", result.stderr);
});

test("候选白名单拒绝规格、测试、历史、Legacy 与 Managed Project 内容", async (t) => {
  for (const name of ["SPECS/README.md", "tests/hidden.mjs", "src/_V1.0/state.json", "PROJECT_INCUBATOR/runtime.py", "skills/.project-incubator/state.json"]) {
    await t.test(name, async (t) => {
      const { root } = await candidate(t);
      await mkdir(path.dirname(path.join(root, name)), { recursive: true });
      await writeFile(path.join(root, name), "禁止内容");
      const result = verify(root);
      assert.equal(result.status, 1);
      assert.equal(result.json?.error?.code, "CANDIDATE_FORBIDDEN_CONTENT", result.stderr);
    });
  }
});

test("候选锁文件版本或 Web ID 不一致使结构检查失败", async (t) => {
  for (const name of ["package-lock.json", "profiles/project-types/web-product.json"]) {
    await t.test(name, async (t) => {
      const { root } = await candidate(t);
      const value = JSON.parse(await readFile(path.join(root, name), "utf8"));
      if (name === "package-lock.json") value.packages[""].version = "0.2.0";
      else value.child_skill_id = "desktop-product-incubator";
      await writeFile(path.join(root, name), JSON.stringify(value));
      const result = verify(root);
      assert.equal(result.status, 1);
      assert.ok(result.json?.error, result.stderr);
    });
  }
});

test("完整模式没有候选自身生产依赖时失败而不使用源码依赖", async (t) => {
  const { root, managed } = await candidate(t);
  const result = verify(root, "--full", managed);
  assert.equal(result.status, 1);
  assert.ok(result.json?.error, result.stderr);
});

test("完整模式通过真实 stdio MCP 验证三种 Route、Host Forbidden、Web Activation 和 Receipt", async (t) => {
  const { root, managed } = await candidate(t);
  // 仓库内测试只复制已安装依赖，避免网络服务；Stage G 另行执行全新 npm ci。
  await cp(path.join(pluginRoot, "node_modules"), path.join(root, "node_modules"), { recursive: true });
  const structure = verify(root);
  assert.equal(structure.status, 0, structure.stderr);
  const full = verify(root, "--full", managed);
  assert.equal(full.status, 0, full.stderr || full.stdout);
  assert.equal(full.json.candidate_hash, structure.json.candidate_hash);
  assert.equal(full.json.mcp_server_version, "0.3.0");
  assert.deepEqual(full.json.web_route, { project_type_id: "web-product", child_skill_id: "web-product-incubator", host_profile_id: null });
  assert.equal(full.json.mod_route.project_type_id, "mod");
  assert.equal(full.json.desktop_route.host_profile_id, "windows-desktop");
  assert.equal(full.json.host_forbidden_verified, true);
  assert.equal(full.json.activation.plugin_version, "0.3.0");
  assert.equal(full.json.receipt_verified, true);
  const activation = JSON.parse(await readFile(path.join(managed, ".project-incubator/activation.json"), "utf8"));
  assert.deepEqual(full.json.activation, activation);
});
