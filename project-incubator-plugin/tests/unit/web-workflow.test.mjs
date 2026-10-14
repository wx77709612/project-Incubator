import assert from "node:assert/strict";
import test from "node:test";

import {
  evaluateEntry,
  evaluateTransition,
  evaluateWebEntry,
  evaluateWebTransition,
  webStages,
} from "../../src/domains/web/workflow.mjs";

const expectedNext = {
  P0: ["P1"], P1: ["P2"], P2: ["P3"], P3: ["P4"],
  P4: ["P5"], P5: ["P6"], P6: ["P2", "P3", "P4", "P5"],
};

function state(stage, mode = "ADOPT_EXISTING", evidenceRefs = ["artifact:existing-project"]) {
  return {
    workflow: {
      stage,
      status: "ACTIVE",
      completed: [],
      allowed_next: [],
      entry: {
        mode,
        initial_stage: stage,
        assessment_summary: "已有项目阶段由证据支持。",
        evidence_refs: evidenceRefs,
        assessed_at: "2026-10-14T00:00:00.000Z",
      },
    },
  };
}

test("Web NEW_PROJECT starts only at P0 with the expected entry workflow", () => {
  const entered = evaluateWebEntry(state("P0", "NEW_PROJECT", []));
  assert.deepEqual(entered, {
    allowed: true,
    code: "WORKFLOW_ENTRY_ALLOWED",
    semantic: "ENTRY",
    workflow: { stage: "P0", allowed_next: ["P1"], return_stage: null },
  });
  assert.equal(evaluateWebEntry(state("P3", "NEW_PROJECT", [])).code, "WORKFLOW_ENTRY_STAGE_INVALID");
});

test("Web ADOPT_EXISTING accepts P0-P6 when evidence is present", () => {
  assert.deepEqual(webStages, ["P0", "P1", "P2", "P3", "P4", "P5", "P6"]);
  assert.equal(Object.isFrozen(webStages), true);
  for (const stage of webStages) {
    const entered = evaluateWebEntry(state(stage));
    assert.equal(entered.allowed, true, stage);
    assert.equal(entered.workflow.stage, stage);
    assert.deepEqual(entered.workflow.allowed_next, expectedNext[stage], stage);
    assert.equal(entered.workflow.return_stage, null);
  }
  assert.equal(evaluateWebEntry(state("P2", "ADOPT_EXISTING", [])).code, "WORKFLOW_ENTRY_EVIDENCE_REQUIRED");
});

test("Web entry rejects missing entry, mismatch, unknown mode, and invalid stage", () => {
  const missing = state("P2");
  delete missing.workflow.entry;
  assert.equal(evaluateWebEntry(missing).code, "WORKFLOW_ENTRY_REQUIRED");
  const mismatch = state("P2");
  mismatch.workflow.entry.initial_stage = "P3";
  assert.equal(evaluateWebEntry(mismatch).code, "WORKFLOW_ENTRY_STATE_MISMATCH");
  assert.equal(evaluateWebEntry(state("P2", "UNKNOWN")).code, "WORKFLOW_ENTRY_MODE_INVALID");
  assert.equal(evaluateWebEntry(state("P7")).code, "WORKFLOW_ENTRY_STAGE_INVALID");
});

test("Web stages advance P0-P6 one step at a time with the expected state shape", () => {
  const sequence = ["P0", "P1", "P2", "P3", "P4", "P5", "P6"];
  for (let index = 0; index < sequence.length - 1; index += 1) {
    const current = sequence[index];
    const target = sequence[index + 1];
    const result = evaluateWebTransition(state(current), {
      target_stage: target,
      completion_satisfied: true,
      maker_authorized: current === "P0",
    });
    assert.equal(result.allowed, true, `${current}->${target}`);
    assert.equal(result.semantic, "STAGE_ADVANCE");
    assert.deepEqual(result.workflow, {
      stage: target,
      status: "ACTIVE",
      completed: [],
      allowed_next: expectedNext[target],
      return_stage: null,
      entry: {
        mode: "ADOPT_EXISTING",
        initial_stage: current,
        assessment_summary: "已有项目阶段由证据支持。",
        evidence_refs: ["artifact:existing-project"],
        assessed_at: "2026-10-14T00:00:00.000Z",
      },
    });
  }
  assert.equal(evaluateWebTransition(state("P2"), {
    target_stage: "P5", completion_satisfied: true,
  }).code, "ILLEGAL_TRANSITION");
});

test("Web P6 iteration can return to P2-P5 but not P0 or P1", () => {
  for (const target of ["P2", "P3", "P4", "P5"]) {
    const result = evaluateWebTransition(state("P6"), {
      target_stage: target, completion_satisfied: true,
    });
    assert.equal(result.allowed, true, target);
    assert.equal(result.semantic, "ITERATION");
    assert.equal(result.workflow.return_stage, null);
  }
  for (const target of ["P0", "P1", "P6"]) {
    assert.equal(evaluateWebTransition(state("P6"), {
      target_stage: target, completion_satisfied: true,
    }).code, "ILLEGAL_TRANSITION", target);
  }
});

test("Web transitions require completion and Maker authorization when required", () => {
  assert.equal(evaluateWebTransition(state("P2"), {
    target_stage: "P3", completion_satisfied: false,
  }).code, "COMPLETION_CONDITIONS_REQUIRED");
  assert.equal(evaluateWebTransition(state("P0"), {
    target_stage: "P1", completion_satisfied: true,
  }).code, "MAKER_AUTHORIZATION_REQUIRED");
  assert.equal(evaluateWebTransition(state("P3"), {
    target_stage: "P4", completion_satisfied: true, changes_boundary: true,
  }).code, "MAKER_AUTHORIZATION_REQUIRED");
});

test("Web evaluator aliases preserve the public entry and transition behavior", () => {
  assert.equal(evaluateEntry, evaluateWebEntry);
  assert.equal(evaluateTransition, evaluateWebTransition);
  assert.deepEqual(evaluateEntry(state("P0")), evaluateWebEntry(state("P0")));
  assert.deepEqual(evaluateTransition(state("P0"), {
    target_stage: "P1", completion_satisfied: true, maker_authorized: true,
  }), evaluateWebTransition(state("P0"), {
    target_stage: "P1", completion_satisfied: true, maker_authorized: true,
  }));
});

