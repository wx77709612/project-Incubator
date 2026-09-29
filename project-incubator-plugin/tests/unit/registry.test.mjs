import assert from "node:assert/strict";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { loadRegistry, resolveRoute, validateRegistry } from "../../src/kernel/registry.mjs";

function registry() {
  return {
    schema_version: "1.0",
    kernel_constraints: {
      maker_authorization: "REQUIRED",
      state_mutation: "MCP_ONLY",
      receipt: "REQUIRED",
    },
    child_skills: [{ id: "mod-incubator", skill_path: "skills/mod-incubator/SKILL.md" }],
    project_types: [{ id: "mod", child_skill_id: "mod-incubator" }],
    host_profiles: [{
      id: "sims-4", project_type_id: "mod", profile_path: "profiles/sims-4.json",
      kernel_constraints: {},
    }],
  };
}

test("registry rejects unknown child skills and duplicate identifiers", () => {
  const unknown = registry();
  unknown.project_types[0].child_skill_id = "missing";
  assert.throws(() => validateRegistry(unknown), /UNKNOWN_CHILD_SKILL/);

  const duplicate = registry();
  duplicate.project_types.push({ id: "mod", child_skill_id: "mod-incubator" });
  assert.throws(() => validateRegistry(duplicate), /DUPLICATE_PROJECT_TYPE_ID/);
});

test("host profiles belong to exactly one project type", () => {
  const value = registry();
  value.project_types.push({ id: "desktop-tool", child_skill_id: "mod-incubator" });
  const parsed = validateRegistry(value);
  assert.throws(() => resolveRoute(parsed, "desktop-tool", "sims-4"), /HOST_PROFILE_PROJECT_TYPE_MISMATCH/);
  assert.throws(() => resolveRoute(parsed, "mod", "unknown"), /HOST_PROFILE_NOT_FOUND/);
});

test("profiles cannot loosen shared kernel constraints", () => {
  const value = registry();
  value.host_profiles[0].kernel_constraints.maker_authorization = "OPTIONAL";
  assert.throws(() => validateRegistry(value), /HOST_PROFILE_WEAKENS_KERNEL/);
});

test("a new legal project type is loaded from data without kernel changes", async (t) => {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-registry-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  await mkdir(path.join(root, "profiles"), { recursive: true });
  const value = registry();
  value.child_skills.push({ id: "desktop-incubator", skill_path: "skills/desktop-incubator/SKILL.md" });
  value.project_types.push({ id: "desktop-tool", child_skill_id: "desktop-incubator" });
  await writeFile(path.join(root, "profiles", "registry.json"), JSON.stringify(value));
  const loaded = await loadRegistry(root);
  assert.equal(resolveRoute(loaded, "desktop-tool").child_skill_id, "desktop-incubator");
});
