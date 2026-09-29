import assert from "node:assert/strict";
import test from "node:test";
import { applySims4Profile } from "../../src/domains/mod/sims4-profile.mjs";

function policy() {
  return {
    kernel_constraints: { maker_authorization: "REQUIRED", state_mutation: "MCP_ONLY", receipt: "REQUIRED" },
    minimum_evidence: "E3", gates: ["MOD_VERTICAL_SLICE"],
  };
}

test("profile always requires Sims 4 delivery and diagnostic evidence", () => {
  const result = applySims4Profile(policy(), {
    capability_id: "cap-core", claim: "脚本能力", mod_types: ["SCRIPT"], facets: {},
  });
  assert.deepEqual(result.required_context, ["game_version", "patch_version", "mod_types"]);
  for (const check of ["build_artifact_contents", "mods_install_structure", "loading_logs", "exceptions"]) {
    assert.ok(result.verification_checks.includes(check));
  }
});

test("capability facets select UI, interaction, save and compatibility checks", () => {
  const plain = applySims4Profile(policy(), {
    capability_id: "cap-package", claim: "资源替换", mod_types: ["PACKAGE"], facets: {},
  });
  for (const check of ["ui_observation", "interaction_observation", "save_compatibility", "cross_version_matrix"]) {
    assert.ok(!plain.verification_checks.includes(check));
  }
  const scoped = applySims4Profile(policy(), {
    capability_id: "cap-ui", claim: "可存档交互", mod_types: ["SCRIPT", "PACKAGE"],
    facets: { ui: true, interaction: true, persistence: true, version_sensitive: true },
  });
  for (const check of ["ui_observation", "interaction_observation", "save_compatibility", "cross_version_matrix"]) {
    assert.ok(scoped.verification_checks.includes(check));
  }
});

test("host profile narrows and never weakens shared authority", () => {
  const base = policy();
  const result = applySims4Profile(base, {
    capability_id: "cap-1", claim: "能力", mod_types: ["SCRIPT"], facets: {},
  });
  assert.deepEqual(result.kernel_constraints, base.kernel_constraints);
  assert.ok(result.gates.includes("MOD_VERTICAL_SLICE"));
  assert.ok(result.gates.includes("SIMS4_DELIVERY_VERIFIED"));
  assert.equal(result.minimum_evidence, "E3");
  assert.deepEqual(result.maker_observation_fields, [
    "scenario", "game_version", "patch_version", "observed_result", "failure_or_side_effect", "evidence_ref",
  ]);
});
