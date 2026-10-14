import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";

const root = path.resolve(import.meta.dirname, "../..");
const read = async (relative) => {
  try { return await readFile(path.join(root, relative), "utf8"); }
  catch (error) { if (error.code === "ENOENT") return ""; throw error; }
};
const section = (text, heading) => {
  const start = text.indexOf(heading);
  assert.notEqual(start, -1, `缺少指引：${heading}`);
  const rest = text.slice(start + heading.length);
  return rest.split(/\n#{2,3} /)[0];
};

test("web child requires an approved active route and evidence-based entry", async () => {
  const skill = await read("skills/web-product-incubator/SKILL.md");
  assert.match(skill, /^---\r?\nname: web-product-incubator\r?\n/);
  assert.match(skill, /description:.*Router.*web-product/);
  assert.match(skill, /有效激活状态/);
  assert.match(skill, /inspect_project/);
  assert.match(skill, /NEW_PROJECT[^\n]*P0/);
  assert.match(skill, /ADOPT_EXISTING[^\n]*P0–P6[^\n]*evidence_refs/);
  assert.match(skill, /Entry[^\n]*不可修改/);
});

test("each web phase declares inputs outputs completion and failure routing", async () => {
  const skill = await read("skills/web-product-incubator/SKILL.md");
  for (const [id, name] of [["P0", "Intent Discovery"], ["P1", "Project Definition"], ["P2", "Solution Design"], ["P3", "Execution Planning"], ["P4", "Creation"], ["P5", "Validation"], ["P6", "Iteration"]]) {
    const phase = section(skill, `### ${id} \`${name}\``);
    for (const field of ["目标", "输入", "产物", "Completion Conditions", "失败路由"]) assert.ok(phase.includes(field), `${id} 缺少 ${field}`);
  }
  assert.match(skill, /P6→P2\/P3\/P4\/P5/);
  assert.match(skill, /不得[^\n]*P6→P0\/P1/);
});

test("P4 requires independent satisfied gates for both non-stage checkpoints", async () => {
  const skill = await read("skills/web-product-incubator/SKILL.md");
  const p4 = section(skill, "### P4 `Creation`");
  for (const checkpoint of ["Usable Web Slice", "Build Readiness"]) {
    const row = p4.split("\n").find(line => line.startsWith(`| ${checkpoint} |`));
    assert.ok(row, `缺少 ${checkpoint} 独立要求`);
    for (const field of ["Evidence Refs", "Claim Scope", "Known Limitations", "Failure Routing", "Gate Evaluation", "REQUIREMENT_SATISFIED"]) assert.ok(row.includes(field), `${checkpoint} 缺少 ${field}`);
  }
  assert.match(p4, /都不是 Stage/);
  assert.match(p4, /只有两项均为 `REQUIREMENT_SATISFIED`[^\n]*P4→P5/);
  assert.match(p4, /不得[^\n]*不适用/);
  assert.match(p4, /Creation Correction[^\n]*普通[^\n]*Context Mutation/);
  assert.match(p4, /不提交 `workflow_transition`/);
});

test("P5 distinguishes channel ceilings and independently satisfied requirements", async () => {
  const skill = await read("skills/web-product-incubator/SKILL.md");
  const p5 = section(skill, "### P5 `Validation`");
  for (const channel of ["LOGIC_AUTOMATION", "BUILD_VALIDATION", "LOCAL_INTEGRATION_VALIDATION", "LOCAL_BROWSER_VALIDATION", "SECONDARY_INTERFACE_VALIDATION", "HUMAN_VALIDATION"]) {
    const row = p5.split("\n").find(line => line.startsWith(`| ${channel} |`));
    assert.ok(row && /仅|不能|不证明/.test(row), `${channel} 缺少 Claim 上限`);
  }
  for (const requirement of ["Build Requirement", "Local Integration Requirement", "Local Browser Requirement", "Secondary Interface Requirement"]) {
    assert.match(p5, new RegExp(`${requirement}[^\\n]*Gate Evaluation[^\\n]*REQUIREMENT_SATISFIED`));
  }
  assert.match(p5, /至少(?:覆盖)?一条真实浏览器核心旅程/);
  assert.match(p5, /Build-only[^\n]*不能[^\n]*P5/);
  assert.match(p5, /Script Validation Result[^\n]*不能[^\n]*Gate Evaluation/);
});

test("local evidence binds reproducible build runtime browser and dependency results", async () => {
  const skill = await read("skills/web-product-incubator/SKILL.md");
  const binding = section(skill, "## 本地运行与 Evidence 绑定");
  for (const field of ["Revision", "Artifact", "依赖", "版本", "构建命令", "启动命令", "readiness", "停止", "清理", "浏览器名称与版本", "localhost URL", "端口", "协议", "用户步骤", "可见结果", "后端或数据结果", "前端", "后端", "数据", "外部依赖", "模拟", "失败反馈", "副作用"]) assert.ok(binding.includes(field), `缺少 ${field}`);
  assert.match(binding, /进程存活[^\n]*不等于[^\n]*readiness/);
});

test("secondary interfaces share product policies but require independent client evidence", async () => {
  const skill = await read("skills/web-product-incubator/SKILL.md");
  const secondary = section(skill, "## 次级界面");
  for (const term of ["REST", "GraphQL", "WebSocket", "Webhook", "MCP", "Product Boundary", "主要用户结果", "业务模型", "数据所有权", "授权", "审计", "副作用", "版本", "生命周期", "主要独立交付物", "独立 Claim", "Evidence", "真实 MCP Client", "Transport", "允许路径", "未授权", "越权", "协议失败", "业务失败"]) assert.ok(secondary.includes(term), `缺少 ${term}`);
  assert.match(secondary, /不能[^\n]*替代[^\n]*浏览器 Evidence/);
  assert.match(secondary, /Maker Project Type Review[^\n]*不自动迁移/);
});

test("router enforces web eligibility exclusions host forbidden and Maker review", async () => {
  const router = await read("skills/project-incubator-router/SKILL.md");
  const web = section(router, "## Web Product 路由边界");
  for (const term of ["浏览器", "前端", "后端", "核心旅程", "NEW_PROJECT", "P0", "ADOPT_EXISTING", "P0–P6", "FORBIDDEN", "host_profile_id", "localhost", "操作系统", "浏览器扩展", "静态前端", "纯后端", "独立 MCP Service", "CLI", "SDK", "库", "移动", "桌面", "Mod"]) assert.ok(web.includes(term), `Router 缺少 ${term}`);
  assert.match(web, /不得[^\n]*创建[^\n]*Host/);
  assert.match(web, /MCP[^\n]*不改变 Project Type/);
  assert.match(web, /Maker Review[^\n]*不自动迁移/);
  assert.match(web, /不得[^\n]*默认类型/);
  assert.match(web, /提议不是激活/);
});

test("architecture composes web without a host or deployment authority", async () => {
  const architecture = await read("ARCHITECTURE.md");
  assert.match(architecture, /Web Product Incubator Skill[^\n]*无 Host Profile/);
  assert.match(architecture, /web-product[^\n]*FORBIDDEN/);
  assert.match(architecture, /Registry 1\.1/);
  for (const source of [architecture, await read("skills/web-product-incubator/SKILL.md")]) {
    assert.match(source, /DEFERRED_CAPABILITY/);
    assert.match(source, /不得[^\n]*Production Ready/);
    assert.match(source, /不新增[^\n]*Deployment[^\n]*Stage/);
  }
});
