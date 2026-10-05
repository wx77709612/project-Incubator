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
  ["skills/mod-incubator/SKILL.md", "304a789b6b28058d5dfa5382ffd718cb8cf4e10cd1f6d592746d75ff8f535017"],
  ["skills/sims-4-host-profile/SKILL.md", "b159ded0bbb8cc265fec25c1ec9d752668d4416b781c725bbf5f54b84617bc4a"],
  ["profiles/project-types/mod.json", "a959016c7488031f9f29c3b6f80e2345807ce36a1c54a4d48c0dec4ac231f83a"],
  ["profiles/hosts/sims-4.json", "f47f129237c272a22cc049a2073ed898ca6d750344105ed8bb236de4e02000bf"],
]);

test("released Mod and Sims 4 assets remain byte-for-byte unchanged", async () => {
  for (const [relative, expected] of protectedDigests) {
    const bytes = await readFile(path.join(root, relative));
    assert.equal(createHash("sha256").update(bytes).digest("hex"), expected, relative);
  }
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
