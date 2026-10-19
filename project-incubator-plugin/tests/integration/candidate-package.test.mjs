import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { execFile, spawnSync } from "node:child_process";
import { cp, mkdir, mkdtemp, readFile, readdir, realpath, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { pathToFileURL } from "node:url";

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

test("两种模式都在执行前拒绝 Workflow 经传递 re-export 加载 Candidate 外源码", async (t) => {
  for (const mode of ["--structure-only", "--full"]) {
    await t.test(mode, async (t) => {
      const { root, managed } = await candidate(t);
      const workflow = "src/domains/web/workflow.mjs";
      const outside = path.join(path.dirname(root), "outside-workflow.mjs");
      const marker = path.join(path.dirname(root), "outside-executed.txt");
      await writeFile(outside, `import { writeFileSync } from 'node:fs';\nwriteFileSync(${JSON.stringify(marker)}, 'executed');\nexport * from ${JSON.stringify(pathToFileURL(path.join(pluginRoot, workflow)).href)};\n`);
      await writeFile(path.join(root, workflow), "export * from './bridge.mjs';\n");
      await writeFile(path.join(root, "src/domains/web/bridge.mjs"), `export * from ${JSON.stringify(pathToFileURL(outside).href)};\n`);
      if (mode === "--full") await cp(path.join(pluginRoot, "node_modules"), path.join(root, "node_modules"), { recursive: true });
      const result = verify(root, mode, mode === "--full" ? managed : undefined);
      assert.equal(result.status, 1, result.stdout);
      assert.equal(result.json?.error?.code, "CANDIDATE_MODULE_ESCAPE", result.stderr);
      await assert.rejects(readFile(marker), { code: "ENOENT" }, "Candidate 外模块不能执行副作用");
    });
  }
});

test("完整模式拒绝缺失 zod 或 SDK 传递依赖时从祖先 node_modules 回退", async (t) => {
  for (const missing of ["zod", "fast-deep-equal"]) {
    await t.test(missing, async (t) => {
      const { root, managed } = await candidate(t);
      await cp(path.join(pluginRoot, "node_modules"), path.join(root, "node_modules"), { recursive: true });
      const parentModules = path.join(path.dirname(root), "node_modules");
      await mkdir(parentModules, { recursive: true });
      await cp(path.join(root, "node_modules", missing), path.join(parentModules, missing), { recursive: true });
      await rm(path.join(root, "node_modules", missing), { recursive: true });
      const result = verify(root, "--full", managed);
      assert.equal(result.status, 1, result.stdout);
      assert.equal(result.json?.error?.code, "CANDIDATE_MODULE_ESCAPE", result.stderr);
    });
  }
});

test("完整模式的真实 MCP 子进程也在执行前拒绝 Candidate 外 import", async (t) => {
  const { root, managed } = await candidate(t);
  await cp(path.join(pluginRoot, "node_modules"), path.join(root, "node_modules"), { recursive: true });
  const outside = path.join(path.dirname(root), "outside-server.mjs");
  const marker = path.join(path.dirname(root), "server-outside-executed.txt");
  await writeFile(outside, `import { writeFileSync } from 'node:fs';\nwriteFileSync(${JSON.stringify(marker)}, 'executed');\n`);
  const entry = path.join(root, "src/server.mjs");
  await writeFile(entry, `${await readFile(entry, "utf8")}\nimport ${JSON.stringify(pathToFileURL(outside).href)};\n`);
  const result = verify(root, "--full", managed);
  assert.equal(result.status, 1, result.stdout);
  assert.ok(result.json?.error, result.stderr);
  assert.match(result.stderr, /CANDIDATE_MODULE_ESCAPE/u, "必须由子进程隔离约束拒绝，而不是其他启动错误");
  await assert.rejects(readFile(marker), { code: "ENOENT" }, "MCP 子进程不能执行 Candidate 外模块");
});

test("真实 MCP 子进程捕获越界 dynamic import 或 require 后继续服务仍使 Full 失败", async (t) => {
  for (const mechanism of ["dynamic import", "require", "require after unterminated diagnostic"]) {
    await t.test(mechanism, async (t) => {
      const { root, managed } = await candidate(t);
      await cp(path.join(pluginRoot, "node_modules"), path.join(root, "node_modules"), { recursive: true });
      const outside = path.join(path.dirname(root), "caught-outside.cjs");
      const marker = path.join(path.dirname(root), "caught-outside-executed.txt");
      const runtimeEvidence = path.join(path.dirname(root), "runtime-location.json");
      await writeFile(outside, `require('node:fs').writeFileSync(${JSON.stringify(marker)}, 'executed');\n`);
      const attempt = mechanism === "dynamic import"
        ? `await import(${JSON.stringify(pathToFileURL(outside).href)})`
        : `createRequire(import.meta.url)(${JSON.stringify(outside)})`;
      const server = path.join(root, "src/server.mjs");
      await writeFile(server, `${await readFile(server, "utf8")}\nimport { createRequire } from 'node:module';\nimport { writeFileSync, writeSync } from 'node:fs';\n${mechanism.endsWith("diagnostic") ? "writeSync(2, 'diagnostic without newline');" : ""}\ntry { ${attempt}; } catch {}\nwriteFileSync(${JSON.stringify(runtimeEvidence)}, JSON.stringify({ runtime: process.env.PLUGIN_DATA }));\n`);
      const result = verify(root, "--full", managed);
      assert.equal(result.status, 1, result.stdout);
      assert.equal(result.json?.error?.code, "CANDIDATE_MODULE_ESCAPE", result.stderr);
      await assert.rejects(readFile(marker), { code: "ENOENT" }, "被拦截的外部模块不能执行");
      const { runtime } = JSON.parse(await readFile(runtimeEvidence, "utf8"));
      await assert.rejects(readdir(runtime), { code: "ENOENT" }, "失败路径清理独立 Runtime/Audit 临时目录");
    });
  }
});

test("子进程审计记录缺失或绑定陈旧 nonce、其他候选根时 Full 失败关闭", async (t) => {
  for (const mutation of ["missing", "nonce", "candidate_root"]) {
    await t.test(mutation, async (t) => {
      const { root, managed } = await candidate(t);
      await cp(path.join(pluginRoot, "node_modules"), path.join(root, "node_modules"), { recursive: true });
      const server = path.join(root, "src/server.mjs");
      if (mutation === "missing") {
        // 仅子进程的 preload 被替换为不报告审计；父验证器仍为被测实现。
        await writeFile(path.join(root, "scripts/verify-candidate.mjs"), "import 'node:fs';\n");
      } else {
        await writeFile(server, `${await readFile(server, "utf8")}\nimport { writeSync } from 'node:fs';\nconst audit = { event: 'READY', nonce: process.env.PROJECT_INCUBATOR_AUDIT_NONCE, candidate_root: ${JSON.stringify(await realpath(root))}, pid: process.pid, parent_pid: process.ppid };\naudit[${JSON.stringify(mutation)}] = 'stale-or-foreign';\nwriteSync(2, '\\x1ePROJECT_INCUBATOR_CANDIDATE_AUDIT ' + JSON.stringify(audit) + '\\n');\n`);
      }
      const result = verify(root, "--full", managed);
      assert.equal(result.status, 1, result.stdout);
      assert.ok(result.json?.error, result.stderr);
    });
  }
});

test("同一 Candidate 的并发 Full 使用独立子进程审计且忽略外来 Runtime 路径和 nonce", async (t) => {
  const { root, managed } = await candidate(t);
  await cp(path.join(pluginRoot, "node_modules"), path.join(root, "node_modules"), { recursive: true });
  const foreignRoot = path.join(path.dirname(root), "foreign-shared");
  await mkdir(foreignRoot);
  await writeFile(path.join(foreignRoot, "sentinel.txt"), "外来共享目录不得被审计或清理");
  const server = path.join(root, "src/server.mjs");
  await writeFile(server, `${await readFile(server, "utf8")}\nimport { writeFileSync } from 'node:fs';\nwriteFileSync(path.join(${JSON.stringify(path.dirname(root))}, 'audit-run-' + process.ppid + '.json'), JSON.stringify({ nonce: process.env.PROJECT_INCUBATOR_AUDIT_NONCE, runtime: process.env.PLUGIN_DATA }));\n`);
  const run = (project) => new Promise((resolve, reject) => {
    execFile(process.execPath, [verifier, "--full", root, project], {
      cwd: os.tmpdir(), encoding: "utf8", timeout: 30000,
      env: { ...process.env, PLUGIN_DATA: foreignRoot, PROJECT_INCUBATOR_AUDIT_NONCE: "stale-injected-nonce" },
    }, (error, stdout, stderr) => {
      if (error) reject(new Error(`${error.message}\n${stdout}\n${stderr}`));
      else resolve(JSON.parse(stdout));
    });
  });
  const results = await Promise.all([run(managed), run(`${managed}-other`)]);
  for (const result of results) assert.equal(result.source_fallback_detected, false);
  const reports = await Promise.all((await readdir(path.dirname(root))).filter((name) => name.startsWith("audit-run-"))
    .map(async (name) => JSON.parse(await readFile(path.join(path.dirname(root), name), "utf8"))));
  assert.equal(reports.length, 2);
  assert.notEqual(reports[0].nonce, reports[1].nonce);
  assert.notEqual(reports[0].runtime, reports[1].runtime);
  for (const report of reports) {
    assert.match(report.nonce, /^[0-9a-f-]{36}$/u);
    assert.notEqual(report.runtime, foreignRoot);
    await assert.rejects(readdir(report.runtime), { code: "ENOENT" }, "成功路径清理自身临时 Runtime");
  }
  assert.deepEqual(await readdir(foreignRoot), ["sentinel.txt"]);
  assert.equal(await readFile(path.join(foreignRoot, "sentinel.txt"), "utf8"), "外来共享目录不得被审计或清理");
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
  assert.equal(full.json.source_fallback_detected, false);
  const activation = JSON.parse(await readFile(path.join(managed, ".project-incubator/activation.json"), "utf8"));
  assert.deepEqual(full.json.activation, activation);
});

test("候选拒绝所有 Child、Host 与嵌套参考中重新引入的旧运行指令", async (t) => {
  for (const relative of [
    "skills/mod-incubator/SKILL.md", "skills/desktop-product-incubator/SKILL.md",
    "skills/web-product-incubator/SKILL.md", "skills/sims-4-host-profile/SKILL.md",
    "skills/windows-desktop-host-profile/SKILL.md", "skills/project-incubator-router/references/nested/drift.md",
  ]) {
    await t.test(relative, async (t) => {
      const { root } = await candidate(t);
      const target = path.join(root, relative);
      await mkdir(path.dirname(target), { recursive: true });
      let original = "";
      try { original = await readFile(target, "utf8"); } catch (error) { if (error.code !== "ENOENT") throw error; }
      await writeFile(target, `${original}\nPROJECT_STATE.md 是唯一状态权威。\n`);
      const result = verify(root);
      assert.equal(result.status, 1, "候选指导漂移必须失败关闭");
      assert.equal(result.json?.error?.code, "CANDIDATE_GUIDANCE_DRIFT");
    });
  }
});
test("候选拒绝 Mod 恢复回退到无 Receipt 验证的工具", async (t) => {
  const { root } = await candidate(t);
  const target = path.join(root, "skills/mod-incubator/SKILL.md");
  await writeFile(target, (await readFile(target, "utf8")).replaceAll("inspect_project", "get_project_state"));
  const result = verify(root);
  assert.equal(result.status, 1);
  assert.equal(result.json?.error?.code, "CANDIDATE_GUIDANCE_DRIFT");
});

test("候选拒绝同行否定混入旧指令与相对规格路径", async (t) => {
  for (const injected of ["开始前调用 get_project_state；不得直接编辑权威文件。", "PROJECT_STATE.md 是唯一状态权威；禁止从聊天恢复。", "请先读取 `../../../SPECS/DESIGN/CONTEXT_MODEL_DESIGN.md` 再恢复项目。", "请先读取 `C:/repo/SPECS/DESIGN/CONTEXT_MODEL_DESIGN.md` 再恢复项目。", "请先读取 `..\\..\\..\\SPECS\\DESIGN\\CONTEXT_MODEL_DESIGN.md` 再恢复项目。"]) {
    await t.test(injected, async (t) => {
      const { root } = await candidate(t);
      const target = path.join(root, "skills/mod-incubator/SKILL.md");
      await writeFile(target, `${await readFile(target, "utf8")}\n${injected}\n`);
      const result = verify(root);
      assert.equal(result.status, 1);
      assert.equal(result.json?.error?.code, "CANDIDATE_GUIDANCE_DRIFT");
    });
  }
});
