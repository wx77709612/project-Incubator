import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";

import { loadRegistry, loadWorkflowEvaluators, resolveRoute } from "../../src/kernel/registry.mjs";

const pluginRoot = path.resolve(import.meta.dirname, "../..");

test("Web Profile 沿用现有 Project Type Shape，不加入 Deployment、MCP 或 Browser Runtime 字段", async () => {
  const profile = await readFile(path.join(pluginRoot, "profiles/project-types/web-product.json"), "utf8")
    .then(JSON.parse).catch((error) => { if (error.code === "ENOENT") return null; throw error; });
  assert.deepEqual(profile, {
    schema_version: "1.0",
    project_type_id: "web-product",
    child_skill_id: "web-product-incubator",
    stages: ["P0", "P1", "P2", "P3", "P4", "P5", "P6"],
    subflows: [],
    evidence_levels: ["E0", "E1", "E2", "E3", "E4", "E5"],
    human_validation_default: "UNSET",
  });
});

test("Registry 1.1 加载 Web Skill、Profile 和 Workflow，并且没有 Web Host Profile", async () => {
  const registry = await loadRegistry(pluginRoot);
  assert.equal(registry.schema_version, "1.1");
  assert.deepEqual(registry.project_types.find((item) => item.id === "web-product"), {
    id: "web-product",
    child_skill_id: "web-product-incubator",
    host_profile_requirement: "FORBIDDEN",
    profile_path: "profiles/project-types/web-product.json",
    workflow_module: "src/domains/web/workflow.mjs",
  });
  assert.deepEqual(registry.child_skills.find((item) => item.id === "web-product-incubator"), {
    id: "web-product-incubator", skill_path: "skills/web-product-incubator/SKILL.md",
  });
  assert.equal(registry.host_profiles.some((item) => item.project_type_id === "web-product"), false);
  const evaluators = await loadWorkflowEvaluators(pluginRoot, registry);
  assert.equal(typeof evaluators.get("web-product").evaluateEntry, "function");
  assert.equal(typeof evaluators.get("web-product").evaluateTransition, "function");
});

test("Web Route 无 Host 时成功，任何非空 Host 均返回 HOST_PROFILE_FORBIDDEN", async () => {
  const registry = await loadRegistry(pluginRoot);
  assert.deepEqual(resolveRoute(registry, "web-product"), {
    project_type_id: "web-product", child_skill_id: "web-product-incubator", host_profile_id: null,
  });
  for (const host of ["sims-4", "windows-desktop", "web-host", "unknown", " "]) {
    assert.throws(() => resolveRoute(registry, "web-product", host), /HOST_PROFILE_FORBIDDEN/);
  }
});
