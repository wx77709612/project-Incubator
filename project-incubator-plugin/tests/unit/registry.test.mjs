import assert from "node:assert/strict";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import {
  loadRegistry, loadWorkflowEvaluators, resolveRoute, validateRegistry,
} from "../../src/kernel/registry.mjs";

function registry() {
  return {
    schema_version: "1.1",
    kernel_constraints: {
      maker_authorization: "REQUIRED",
      state_mutation: "MCP_ONLY",
      receipt: "REQUIRED",
    },
    child_skills: [{ id: "mod-incubator", skill_path: "skills/mod-incubator/SKILL.md" }],
    project_types: [{
      id: "mod", child_skill_id: "mod-incubator", host_profile_requirement: "OPTIONAL",
      workflow_module: "src/domains/mod/workflow.mjs",
    }],
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
  duplicate.project_types.push({
    id: "mod", child_skill_id: "mod-incubator", host_profile_requirement: "OPTIONAL",
    workflow_module: "src/domains/mod/workflow.mjs",
  });
  assert.throws(() => validateRegistry(duplicate), /DUPLICATE_PROJECT_TYPE_ID/);
});

test("registry 1.1 requires an explicit valid host requirement on every project type", () => {
  const legacy = registry();
  legacy.schema_version = "1.0";
  assert.throws(() => validateRegistry(legacy));

  const missing = registry();
  delete missing.project_types[0].host_profile_requirement;
  assert.throws(() => validateRegistry(missing));

  const invalid = registry();
  invalid.project_types[0].host_profile_requirement = "DEFAULT";
  assert.throws(() => validateRegistry(invalid));
});

test("host profiles belong to exactly one project type", () => {
  const value = registry();
  value.project_types.push({
    id: "desktop-tool", child_skill_id: "mod-incubator", host_profile_requirement: "REQUIRED",
    workflow_module: "src/domains/mod/workflow.mjs",
  });
  const parsed = validateRegistry(value);
  assert.throws(() => resolveRoute(parsed, "desktop-tool", "sims-4"), /HOST_PROFILE_PROJECT_TYPE_MISMATCH/);
  assert.throws(() => resolveRoute(parsed, "mod", "unknown"), /HOST_PROFILE_NOT_FOUND/);
});

test("route resolution enforces REQUIRED, OPTIONAL and FORBIDDEN without selecting a default host", () => {
  const value = registry();
  value.child_skills.push({ id: "desktop-product-incubator", skill_path: "skills/desktop-product-incubator/SKILL.md" });
  value.project_types.push({
    id: "desktop-product", child_skill_id: "desktop-product-incubator",
    host_profile_requirement: "REQUIRED", workflow_module: "src/domains/desktop/workflow.mjs",
  });
  value.host_profiles.push({
    id: "windows-desktop", project_type_id: "desktop-product",
    profile_path: "profiles/hosts/windows-desktop.json", kernel_constraints: {},
  });
  const parsed = validateRegistry(value);

  assert.equal(resolveRoute(parsed, "mod").host_profile_id, null);
  assert.throws(() => resolveRoute(parsed, "desktop-product"), /HOST_PROFILE_REQUIRED/);
  assert.equal(resolveRoute(parsed, "desktop-product", "windows-desktop").host_profile_id, "windows-desktop");

  const forbidden = registry();
  forbidden.project_types[0].host_profile_requirement = "FORBIDDEN";
  assert.equal(resolveRoute(validateRegistry(forbidden), "mod").host_profile_id, null);
  assert.throws(() => resolveRoute(validateRegistry(forbidden), "mod", "sims-4"), /HOST_PROFILE_FORBIDDEN/);
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
  value.project_types[0].workflow_module = "domains/desktop-workflow.mjs";
  value.child_skills.push({ id: "desktop-incubator", skill_path: "skills/desktop-incubator/SKILL.md" });
  value.project_types.push({
    id: "desktop-tool", child_skill_id: "desktop-incubator", host_profile_requirement: "OPTIONAL",
    workflow_module: "domains/desktop-workflow.mjs",
  });
  await mkdir(path.join(root, "domains"), { recursive: true });
  await writeFile(path.join(root, "domains", "desktop-workflow.mjs"), [
    "export function evaluateEntry() {",
    "  return { allowed: true, code: 'ENTRY_ALLOWED' };",
    "}",
    "export function evaluateTransition(state, request) {",
    "  return { allowed: true, code: 'DESKTOP_ALLOWED', workflow: { ...state.workflow, stage: request.target_stage } };",
    "}",
  ].join("\n"));
  await writeFile(path.join(root, "profiles", "registry.json"), JSON.stringify(value));
  const loaded = await loadRegistry(root);
  assert.equal(resolveRoute(loaded, "desktop-tool").child_skill_id, "desktop-incubator");
  const evaluators = await loadWorkflowEvaluators(root, loaded);
  assert.equal(evaluators.get("desktop-tool").evaluateEntry().code, "ENTRY_ALLOWED");
  assert.equal(evaluators.get("desktop-tool").evaluateTransition({}, { target_stage: "D1" }).code, "DESKTOP_ALLOWED");
});

test("workflow modules must stay inside the plugin", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-registry-module-"));
  try {
    const value = registry();
    value.project_types[0].workflow_module = "../outside.mjs";
    assert.throws(() => validateRegistry(value), /INVALID_WORKFLOW_MODULE_PATH/);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("workflow modules must expose both entry and transition evaluators", async (t) => {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-registry-interface-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  await mkdir(path.join(root, "profiles"), { recursive: true });
  await mkdir(path.join(root, "domains"), { recursive: true });
  const value = registry();
  await writeFile(path.join(root, "profiles", "registry.json"), JSON.stringify(value));

  value.project_types[0].workflow_module = "domains/missing-entry.mjs";
  await writeFile(
    path.join(root, "domains", "missing-entry.mjs"),
    "export function evaluateTransition() {}\n",
  );
  await assert.rejects(() => loadWorkflowEvaluators(root, value), /WORKFLOW_EVALUATOR_INVALID/);

  value.project_types[0].workflow_module = "domains/missing-transition.mjs";
  await writeFile(
    path.join(root, "domains", "missing-transition.mjs"),
    "export function evaluateEntry() {}\n",
  );
  await assert.rejects(() => loadWorkflowEvaluators(root, value), /WORKFLOW_EVALUATOR_INVALID/);
});
