import assert from "node:assert/strict";
import test from "node:test";
import { evaluateModTransition } from "../../src/domains/mod/workflow.mjs";

const state = (stage, return_stage = null) => ({ workflow: { stage, return_stage } });

test("Mod stages advance in order and reject skips", () => {
  assert.equal(evaluateModTransition(state("M1_RISK_MODEL"), { target_stage: "M2_VERTICAL_SLICE", completion_satisfied: true }).allowed, true);
  assert.equal(evaluateModTransition(state("M1_RISK_MODEL"), { target_stage: "M4_TARGET_VALIDATION", completion_satisfied: true }).code, "ILLEGAL_TRANSITION");
});

test("leaving M0 requires Maker-owned boundary confirmation", () => {
  assert.equal(evaluateModTransition(state("M0_BOUNDARY"), { target_stage: "M1_RISK_MODEL", completion_satisfied: true }).code, "MAKER_AUTHORIZATION_REQUIRED");
  assert.equal(evaluateModTransition(state("M0_BOUNDARY"), { target_stage: "M1_RISK_MODEL", completion_satisfied: true, maker_authorized: true }).allowed, true);
});

test("M2 through M4 enter and return from MODEL_REVIEW without becoming iteration", () => {
  for (const origin of ["M2_VERTICAL_SLICE", "M3_BUILD_PACKAGE", "M4_TARGET_VALIDATION"]) {
    const entered = evaluateModTransition(state(origin), { target_stage: "MODEL_REVIEW", model_invalidated: true });
    assert.equal(entered.allowed, true);
    assert.equal(entered.workflow.return_stage, origin);
    assert.notEqual(entered.semantic, "ITERATION");
    const resumed = evaluateModTransition({ workflow: entered.workflow }, { target_stage: origin, model_updated: true });
    assert.equal(resumed.allowed, true);
    assert.equal(resumed.workflow.return_stage, null);
  }
});
