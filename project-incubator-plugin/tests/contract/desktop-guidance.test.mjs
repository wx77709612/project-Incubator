import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";

const root = path.resolve(import.meta.dirname, "../..");
const read = (relative) => readFile(path.join(root, relative), "utf8");

test("desktop child skill is discoverable only after the approved route", async () => {
  const skill = await read("skills/desktop-product-incubator/SKILL.md");
  assert.match(skill, /^---\r?\nname: desktop-product-incubator\r?\n/);
  assert.match(skill, /description: Use when[：:].*Router.*desktop-product/s);
  assert.match(skill, /不适用.*浏览器扩展/s);
});

test("desktop child skill reuses P0-P6 names and adds desktop-specific checkpoints", async () => {
  const skill = await read("skills/desktop-product-incubator/SKILL.md");
  for (const phase of [
    "P0 `Intent Discovery`", "P1 `Project Definition`", "P2 `Solution Design`",
    "P3 `Execution Planning`", "P4 `Creation`", "P5 `Validation`", "P6 `Iteration`",
  ]) assert.ok(skill.includes(phase), `缺少 ${phase}`);
  for (const checkpoint of [
    "FEASIBILITY_PROBE", "Desktop System Model", "Usable Slice", "Delivery Hardening",
    "Creation Correction", "TARGET_HOST_VALIDATION",
  ]) assert.ok(skill.includes(checkpoint), `缺少 ${checkpoint}`);
  assert.match(skill, /P6.*P2.*P3.*P4.*P5/s);
  assert.match(skill, /推翻 P0.*P1.*Maker Review/s);
});

test("desktop guidance preserves Maker authority and evidence ceilings", async () => {
  const skill = await read("skills/desktop-product-incubator/SKILL.md");
  for (const boundary of [
    "Product Boundary", "Architecture Decision", "高风险", "人工验证", "Maker Authorization",
  ]) assert.ok(skill.includes(boundary), `缺少 Maker 边界：${boundary}`);
  assert.match(skill, /逻辑自动化.*不能.*真实.*Windows/s);
  assert.match(skill, /下载.*不可信/s);
  assert.match(skill, /解包.*路径穿越/s);
  assert.match(skill, /安装.*回滚/s);
});

test("windows host skill tightens environment and delivery evidence without owning phases", async () => {
  const skill = await read("skills/windows-desktop-host-profile/SKILL.md");
  assert.match(skill, /^---\r?\nname: windows-desktop-host-profile\r?\n/);
  assert.match(skill, /description: Use when[：:].*desktop-product.*windows-desktop/s);
  for (const requirement of [
    "Windows 版本", "架构", "安装范围", "权限", "文件系统", "进程", "安全软件",
    "打包", "签名", "升级", "卸载", "恢复", "TARGET_HOST_VALIDATION",
  ]) assert.ok(skill.includes(requirement), `缺少 Windows 约束：${requirement}`);
  assert.match(skill, /不得.*P0–P6/s);
});

test("router requires entry mode and explicit host while browser extension remains unsupported", async () => {
  const router = await read("skills/project-incubator-router/SKILL.md");
  for (const requirement of [
    "NEW_PROJECT", "ADOPT_EXISTING", "assessment_summary", "evidence_refs",
    "host_profile_requirement", "HOST_PROFILE_REQUIRED", "windows-desktop",
  ]) assert.ok(router.includes(requirement), `Router 缺少 ${requirement}`);
  assert.match(router, /不得.*默认.*Host/s);
  assert.match(router, /ADOPT_EXISTING.*Agent.*Evidence.*阶段/s);
  assert.match(router, /浏览器扩展.*不支持/s);
  assert.match(router, /我明确批准激活请求.*request_id.*scope_digest/s);
});
