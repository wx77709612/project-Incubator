import assert from "node:assert/strict";
import test from "node:test";
import { evaluateModEntry, evaluateModTransition } from "../../src/domains/mod/workflow.mjs";

const state = (stage, return_stage = null) => ({ workflow: { stage, return_stage } });

test("Mod stages advance in order and reject skips", () => {
  const advanced = evaluateModTransition(state("M1_RISK_MODEL"), { target_stage: "M2_VERTICAL_SLICE", completion_satisfied: true });
  assert.equal(advanced.allowed, true);
  assert.deepEqual(advanced.workflow.allowed_next, ["M3_BUILD_PACKAGE", "MODEL_REVIEW"]);
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
    assert.deepEqual(entered.workflow.allowed_next, [origin]);
    assert.notEqual(entered.semantic, "ITERATION");
    const resumed = evaluateModTransition({ workflow: entered.workflow }, { target_stage: origin, model_updated: true });
    assert.equal(resumed.allowed, true);
    assert.equal(resumed.workflow.return_stage, null);
  }
});

function entryState(stage, mode = "ADOPT_EXISTING", evidenceRefs = ["artifact:existing-mod"]) {
  return {
    workflow: {
      stage,
      entry: {
        mode,
        initial_stage: stage,
        assessment_summary: "Agent 基于已有 Mod Artifact 判断当前阶段。",
        evidence_refs: evidenceRefs,
        assessed_at: "2026-10-05T00:00:00.000Z",
      },
    },
  };
}

test("Mod NEW_PROJECT starts only at M0", () => {
  assert.equal(evaluateModEntry(entryState("M0_BOUNDARY", "NEW_PROJECT", [])).allowed, true);
  assert.equal(evaluateModEntry(entryState("M1_RISK_MODEL", "NEW_PROJECT", [])).code, "WORKFLOW_ENTRY_STAGE_INVALID");
});

test("Mod ADOPT_EXISTING accepts M0-M5 but never MODEL_REVIEW", () => {
  for (const stage of [
    "M0_BOUNDARY", "M1_RISK_MODEL", "M2_VERTICAL_SLICE",
    "M3_BUILD_PACKAGE", "M4_TARGET_VALIDATION", "M5_EXPAND_RELEASE",
  ]) {
    assert.equal(evaluateModEntry(entryState(stage)).allowed, true, stage);
  }
  assert.equal(evaluateModEntry(entryState("MODEL_REVIEW")).code, "WORKFLOW_ENTRY_STAGE_INVALID");
  assert.equal(evaluateModEntry(entryState("M3_BUILD_PACKAGE", "ADOPT_EXISTING", [])).code, "WORKFLOW_ENTRY_EVIDENCE_REQUIRED");
});
