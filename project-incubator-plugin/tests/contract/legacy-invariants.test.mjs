import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";

const root = path.resolve(import.meta.dirname, "../..");
const mappings = [
  ["Maker 最终权威", "tests/unit/authorization.test.mjs", "decision mutations require authorization"],
  ["Runtime 独占变更", "tests/integration/hooks.test.mjs", "block direct writes"],
  ["原子回滚", "tests/unit/state-store.test.mjs", "restores the previous state"],
  ["Mutation Closure", "tests/integration/hooks.test.mjs", "requires the current verified receipt"],
  ["单一状态源", "tests/integration/inspect-project.test.mjs", "strictly read-only"],
  ["逻辑分区", "tests/unit/schemas.test.mjs", "minimum complete authority"],
  ["Decision 与 Assumption", "tests/unit/authorization.test.mjs", "evidence may invalidate an assumption"],
  ["Evidence E0-E5", "tests/unit/mod-opacity.test.mjs", "evidence ordering"],
  ["Opaque Spiral", "tests/unit/mod-opacity.test.mjs", "vertical slice"],
  ["MODEL_REVIEW", "tests/unit/mod-workflow.test.mjs", "MODEL_REVIEW"],
  ["Baseline 与 Confidence", "tests/unit/project-summary.test.mjs", "Baseline"],
  ["Sims 4 经验", "tests/unit/sims4-profile.test.mjs", "Sims 4 delivery"],
];

const protectedDigests = new Map([
  ["profiles/project-types/mod.json", "a959016c7488031f9f29c3b6f80e2345807ce36a1c54a4d48c0dec4ac231f83a"],
  ["profiles/hosts/sims-4.json", "f47f129237c272a22cc049a2073ed898ca6d750344105ed8bb236de4e02000bf"],
  ["src/domains/mod/workflow.mjs", "d5484e450bdd8585ba5c2a8876676f52119ab54c589a1c0f15b9953d8cf95672"],
  ["src/domains/mod/opacity.mjs", "8216c9d905283d6b0a2f1ed0fa1286b3d85c959ab6d9fc5d36be0b7c0004b291"],
  ["src/domains/mod/sims4-profile.mjs", "251d8d0ea2e9c594302edae5bd327f9bf403d6a86c2078b1cfe3ded004308283"],
  ["profiles/project-types/desktop-product.json", "a6cbfdb1cde85cb7dadf88a67fab209afdaddca7d1858af1bb69f8e02773c134"],
  ["profiles/hosts/windows-desktop.json", "2c2f294c41086dd642e7f59bf93e88ede917ddb283fa63b9c9dc2cce5344fb6c"],
  ["src/domains/desktop/workflow.mjs", "045ef3da14204c4a96b6130c10f55997917275a554822b4486a6c557feb01cde"],
]);

test("Mod/Sims 4 与 Desktop/Windows 领域代码及 Profile 保持 byte-for-byte 不变", async () => {
  for (const [relative, expected] of protectedDigests) {
    const bytes = await readFile(path.join(root, relative));
    assert.equal(createHash("sha256").update(bytes).digest("hex"), expected, relative);
  }
});

test("Web Child Skill 的 P4 Completion 必须由两项独立 Gate 满足后声明", async () => {
  const skill = await readFile(path.join(root, "skills/web-product-incubator/SKILL.md"), "utf8");
  const p4 = skill.split("### P4 `Creation`")[1]?.split("### P5 `Validation`")[0];
  assert.ok(p4, "缺少 P4 合同");
  for (const checkpoint of ["Usable Web Slice", "Build Readiness"]) {
    const row = p4.split("\n").find((line) => line.startsWith(`| ${checkpoint} |`));
    assert.ok(row, checkpoint);
    for (const field of ["Evidence Refs", "Claim Scope", "Known Limitations", "Failure Routing", "独立 Gate Evaluation", "REQUIREMENT_SATISFIED"]) assert.ok(row.includes(field), `${checkpoint}: ${field}`);
  }
  assert.match(p4, /Completion Conditions：只有两项均为 `REQUIREMENT_SATISFIED`[^\n]*P4→P5/);
  assert.match(p4, /不得[^\n]*不适用[^\n]*绕过/);
  assert.match(p4, /两项分别[^\n]*留在 P4[^\n]*不用一项成功替代另一项/);
});

test("Web P5 各项必需或适用 Requirement 分别满足，四种 only 均不构成 Completion", async () => {
  const skill = await readFile(path.join(root, "skills/web-product-incubator/SKILL.md"), "utf8");
  const p5 = skill.split("### P5 `Validation`")[1]?.split("### P6 `Iteration`")[0];
  assert.ok(p5, "缺少 P5 合同");
  assert.match(p5, /Completion Conditions：[^\n]*Requirement 必须分别评估[^\n]*不能仅列出 Channel/);
  const requirements = ["Build Requirement", "Local Integration Requirement", "Local Browser Requirement", "Secondary Interface Requirement"];
  for (const [only, available] of [["Build-only", "Build Requirement"], ["localhost-only", "Local Integration Requirement"], ["Browser-only", "Local Browser Requirement"], ["Secondary-interface-only", "Secondary Interface Requirement"]]) {
    assert.doesNotMatch(p5, new RegExp(`${only}[^。\\n]*(?<!不)(?:能满足|可以满足|足以通过|足以满足|即可满足|可通过|已满足)[^。\\n]*P5`, "i"), `${only} 不得被声明为完整 P5`);
    for (const missing of requirements.filter((item) => item !== available)) {
      const row = p5.split("\n").find((line) => line.startsWith("- ") && line.includes(missing));
      assert.ok(row && /Gate Evaluation[^\n]*为 `REQUIREMENT_SATISFIED`/.test(row), `${only} 仍需 ${missing}`);
      if (missing === "Secondary Interface Requirement") assert.match(row, /Product Boundary 包含次级界面时，适用/);
    }
  }
  assert.match(p5, /Local Browser Requirement[^\n]*至少覆盖一条真实浏览器核心旅程/);
  assert.match(p5, /Build、Logic、Browser、Secondary Interface 与 Human Evidence 不能互相替代/);
  assert.match(p5, /Script Validation Result、Observation 或 Human Judgment 不能直接替代 Gate Evaluation Result/);
  assert.match(p5, /未满足必要 Requirement 则留在 P5[^\n]*不得伪称通过/);
  assert.match(skill, /Gate Result 不直接修改状态/);
});

test("every PRESERVE, ADAPT and SPECIALIZE matrix item maps to an automated test", async () => {
  const architecture = await readFile(path.join(root, "ARCHITECTURE.md"), "utf8");
  const governedRows = architecture.split("\n").filter((line) => /^\|.*`(?:PRESERVE|ADAPT|SPECIALIZE)`/.test(line));
  assert.equal(mappings.length, governedRows.length);
  for (const [id, file, needle] of mappings) {
    const source = await readFile(path.join(root, file), "utf8");
    assert.ok(source.includes(needle), `${id} 未绑定有效测试`);
  }
});

test("REFERENCE assets remain outside the new plugin runtime package", async () => {
  const architecture = await readFile(path.join(root, "ARCHITECTURE.md"), "utf8");
  assert.match(architecture, /P0-P6 通用 Workflow.*`REFERENCE`/);
  assert.match(architecture, /V1\.1 模板、规格与人工验收案例.*`REFERENCE`/);
});

test("candidate packager uses a runtime whitelist without legacy or design archives", async () => {
  const source = await readFile(path.join(root, "scripts", "package-candidate.mjs"), "utf8");
  for (const excluded of ["PROJECT_INCUBATOR", "SPECS", "zzztemp", "ARCHITECTURE.md", "tests"]) {
    assert.ok(!source.includes(`\"${excluded}\"`), `${excluded} 不应进入候选白名单`);
  }
});

 test("Mod 指导保留 M0–M5、MODEL_REVIEW、Evidence 与 Maker 预算边界", async () => {
  const mod = await readFile(path.join(root, "skills/mod-incubator/SKILL.md"), "utf8");
  for (const term of ["M0_BOUNDARY", "M1_RISK_MODEL", "M2_VERTICAL_SLICE", "M3_BUILD_PACKAGE", "M4_TARGET_VALIDATION", "M5_EXPAND_RELEASE", "MODEL_REVIEW", "E0", "E5", "UNSET", "Maker Authorization", "inspect_project"]) assert.ok(mod.includes(term), term);
  const host = await readFile(path.join(root, "skills/sims-4-host-profile/SKILL.md"), "utf8");
  for (const term of ["游戏版本", "补丁版本", "SCRIPT", "PACKAGE", "Mods", "inspect_project", "不得改变 Kernel Authorization"]) assert.ok(host.includes(term), term);
});
