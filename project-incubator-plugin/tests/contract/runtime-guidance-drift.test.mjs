import assert from "node:assert/strict";
import { cp, mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import test from "node:test";
const plugin = path.resolve(import.meta.dirname, "../..");
const repository = path.resolve(plugin, "..");
const read = (relative) => readFile(path.join(repository, relative), "utf8");

import { obsoleteInstructions, validateRuntimeGuidance } from "../../scripts/runtime-guidance.mjs";
async function markdownFiles(root) {
  const result = [];
  for (const entry of await readdir(root, { withFileTypes: true })) {
    const name = path.join(root, entry.name);
    if (entry.isDirectory()) result.push(...await markdownFiles(name));
    else if (entry.name.endsWith(".md")) result.push(name);
  }
  return result;
}

test("旧全局入口只路由到 Plugin Router，不包含第二套执行流程", async () => {
  const source = await read("PROJECT_INCUBATOR/SKILL.md");
  assert.match(source, /project-incubator-router/u);
  assert.ok(source.length < 1500, "兼容入口必须最小化");
  assert.deepEqual(obsoleteInstructions(source), []);
  assert.doesNotMatch(source, /## Core Workflow|## Core Context|## Runtime 入口|## Multi-Context/u);
});
test("六个 Plugin Skill 及所有参考文档无过时运行指令或包外规格依赖", async () => {
  const files = await markdownFiles(path.join(plugin, "skills"));
  assert.equal(files.filter((name) => name.endsWith("SKILL.md")).length, 6);
  const errors = [];
  for (const name of files) {
    const source = await readFile(name, "utf8");
    if (obsoleteInstructions(source).length) errors.push(path.relative(plugin, name));
    assert.doesNotMatch(source, /`SPECS\//u, name);
  }
  assert.deepEqual(errors, []);
});
for (const skill of ["mod-incubator", "desktop-product-incubator", "web-product-incubator"]) {
  test(`${skill} 恢复使用 Receipt 验证入口，明确三个权威文件`, async () => {
    const source = await read(`project-incubator-plugin/skills/${skill}/SKILL.md`);
    assert.match(source, /inspect_project/u);
    for (const name of ["activation.json", "state.json", "latest-receipt.json"]) assert.ok(source.includes(name), name);
    assert.doesNotMatch(source, /开始前调用 `get_project_state`/u);
  });
}
for (const host of ["sims-4-host-profile", "windows-desktop-host-profile"]) {
  test(`${host} 依赖已验证的 Router 激活和 inspect_project`, async () => {
    const source = await read(`project-incubator-plugin/skills/${host}/SKILL.md`);
    assert.match(source, /inspect_project/u);
    assert.match(source, /Router/u);
  });
}
test("分发 AGENTS 统一 Router/Kernel，模板逐份分类为非现行", async () => {
  for (const relative of ["PROJECT_INCUBATOR/AGENTS.md", "PROJECT_INCUBATOR/templates/integrations/codex/AGENTS.template.md"]) {
    const source = await read(relative);
    assert.match(source, /project-incubator-router/u);
    assert.match(source, /inspect_project/u);
    assert.deepEqual(obsoleteInstructions(source), [], relative);
  }
  for (const directory of ["context", "artifacts"]) {
    for (const name of await markdownFiles(path.join(repository, "PROJECT_INCUBATOR/templates", directory))) {
      assert.match(await readFile(name, "utf8"), /Legacy.*非现行/u, name);
    }
  }
});
test("检查拒绝正向旧指令，也允许禁止条款与历史说明", () => {
  for (const source of ["`PROJECT_STATE.md` 是唯一 Source of Truth。", "通过 BOOTSTRAP_HOST_INTEGRATION 初始化。", "开始前调用 `get_project_state`。", "先形成 Mutation Set。", "Runtime 支持由 runtime/ 提供。"]) assert.equal(obsoleteInstructions(source).length, 1, source);
  for (const source of ["不得以 PROJECT_STATE.md 为权威。", "Legacy 历史：PROJECT_STATE.md 是唯一状态。", "禁止调用 BOOTSTRAP_HOST_INTEGRATION。", "不得通过 get_project_state 恢复。", "PROJECT_STATE.md 是普通 Artifact，不属于状态权威。"]) assert.deepEqual(obsoleteInstructions(source), [], source);
});

test("源码 Skill 使用与候选包相同的完整漂移检查", async () => {
  assert.ok((await validateRuntimeGuidance(plugin)).files_checked >= 7);
});

test("否定条款不得掩盖同一行的独立旧执行指令", () => {
  for (const text of ["开始前调用 get_project_state；不得直接编辑权威文件。", "PROJECT_STATE.md 是唯一状态权威；禁止从聊天恢复。", "禁止从聊天恢复，开始前调用 get_project_state。", "请读取历史资料，然后执行 BOOTSTRAP_HOST_INTEGRATION。"])
    assert.ok(obsoleteInstructions(text).length > 0, text);
});
test("源码检查拒绝代码引用中的相对、绝对与 Windows 包外规格路径", async (t) => {
  for (const reference of ["../../../SPECS/DESIGN/CONTEXT_MODEL_DESIGN.md", "C:/repo/SPECS/DESIGN/CONTEXT_MODEL_DESIGN.md", "..\\..\\..\\SPECS\\DESIGN\\CONTEXT_MODEL_DESIGN.md"]) {
    await t.test(reference, async (t) => {
      const root = await mkdtemp(path.join(os.tmpdir(), "guidance-reference-"));
      t.after(() => rm(root, { recursive: true, force: true }));
      await cp(path.join(plugin, "skills"), path.join(root, "skills"), { recursive: true });
      const target = path.join(root, "skills/mod-incubator/SKILL.md");
      await writeFile(target, `${await readFile(target, "utf8")}\n请先读取 \`${reference}\` 再恢复项目。`);
      await assert.rejects(validateRuntimeGuidance(root), /CANDIDATE_GUIDANCE_DRIFT/);
    });
  }
});
