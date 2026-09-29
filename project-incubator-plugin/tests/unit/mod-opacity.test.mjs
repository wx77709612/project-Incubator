import assert from "node:assert/strict";
import test from "node:test";
import { assessCapabilityOpacity, compareEvidence, constrainSemanticEvidence, resolveHumanBudget } from "../../src/domains/mod/opacity.mjs";

const base = { contract: 0, hidden_state: 0, control: 0, determinism: 0, observability: 0, automation: 0, attribution: 0, version_stability: 0 };

test("opacity uses eight dimensions and treats unknown as visible score one", () => {
  const assessed = assessCapabilityOpacity({ ...base, hidden_state: "UNKNOWN", control: 2 });
  assert.equal(Object.keys(assessed.scores).length, 8);
  assert.equal(assessed.scores.hidden_state, 1);
  assert.deepEqual(assessed.unknown_dimensions, ["hidden_state"]);
  assert.equal(assessed.vertical_slice_recommended, true);
});

test("one score two or two score ones recommends a vertical slice", () => {
  assert.equal(assessCapabilityOpacity({ ...base, contract: 2 }).vertical_slice_recommended, true);
  assert.equal(assessCapabilityOpacity({ ...base, contract: 1, automation: 1 }).vertical_slice_recommended, true);
  assert.equal(assessCapabilityOpacity({ ...base, contract: 1 }).vertical_slice_recommended, false);
});

test("evidence ordering and semantic ceilings stay honest", () => {
  assert.ok(compareEvidence("E5", "E0") > 0);
  assert.equal(constrainSemanticEvidence({ current: "E0", api_availability: "E1" }), "E0");
  assert.equal(constrainSemanticEvidence({ current: "E2", target_environment_successes: 1 }), "E3");
});

test("only Maker input can set a human validation limit", () => {
  assert.equal(resolveHumanBudget({ agent_proposed_limit: 4 }), "UNSET");
  assert.equal(resolveHumanBudget({ maker_limit: 4, agent_proposed_limit: 2 }), 4);
});
