import assert from "node:assert/strict";
import test from "node:test";

import {
  desktopStages,
  evaluateDesktopEntry,
  evaluateDesktopTransition,
} from "../../src/domains/desktop/workflow.mjs";

const assessedAt = "2026-10-05T00:00:00.000Z";

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
        assessment_summary: "Agent 基于已有 Artifact 判断当前阶段。",
        evidence_refs: evidenceRefs,
        assessed_at: assessedAt,
      },
    },
  };
}

test("Desktop NEW_PROJECT starts only at P0", () => {
  const entered = evaluateDesktopEntry(state("P0", "NEW_PROJECT", []));
  assert.equal(entered.allowed, true);
  assert.deepEqual(entered.workflow, { stage: "P0", allowed_next: ["P1"], return_stage: null });
  assert.equal(evaluateDesktopEntry(state("P3", "NEW_PROJECT", [])).code, "WORKFLOW_ENTRY_STAGE_INVALID");
});

test("Desktop ADOPT_EXISTING accepts every normal P0-P6 stage with evidence", () => {
  const expectedNext = {
    P0: ["P1"], P1: ["P2"], P2: ["P3"], P3: ["P4"],
    P4: ["P5"], P5: ["P6"], P6: ["P2", "P3", "P4", "P5"],
  };
  for (const stage of desktopStages) {
    const entered = evaluateDesktopEntry(state(stage));
    assert.equal(entered.allowed, true, stage);
    assert.deepEqual(entered.workflow.allowed_next, expectedNext[stage], stage);
  }
});

test("Desktop entry rejects missing evidence, stage mismatch, invalid mode and unknown stage", () => {
  assert.equal(evaluateDesktopEntry(state("P2", "ADOPT_EXISTING", [])).code, "WORKFLOW_ENTRY_EVIDENCE_REQUIRED");
  const mismatch = state("P2");
  mismatch.workflow.entry.initial_stage = "P3";
  assert.equal(evaluateDesktopEntry(mismatch).code, "WORKFLOW_ENTRY_STATE_MISMATCH");
  assert.equal(evaluateDesktopEntry(state("P2", "UNKNOWN")).code, "WORKFLOW_ENTRY_MODE_INVALID");
  assert.equal(evaluateDesktopEntry(state("P7")).code, "WORKFLOW_ENTRY_STAGE_INVALID");
});

test("Desktop stages advance through P0-P6 without skipping", () => {
  const sequence = ["P0", "P1", "P2", "P3", "P4", "P5", "P6"];
  for (let index = 0; index < sequence.length - 1; index += 1) {
    const current = sequence[index];
    const target = sequence[index + 1];
    const result = evaluateDesktopTransition(state(current), {
      target_stage: target,
      completion_satisfied: true,
      maker_authorized: current === "P0",
    });
    assert.equal(result.allowed, true, `${current}->${target}`);
    assert.equal(result.workflow.stage, target);
  }
  assert.equal(evaluateDesktopTransition(state("P2"), {
    target_stage: "P5", completion_satisfied: true,
  }).code, "ILLEGAL_TRANSITION");
});

test("Desktop P6 iteration returns only to P2-P5", () => {
  for (const target of ["P2", "P3", "P4", "P5"]) {
    assert.equal(evaluateDesktopTransition(state("P6"), {
      target_stage: target, completion_satisfied: true,
    }).allowed, true, target);
  }
  for (const target of ["P0", "P1", "P6"]) {
    assert.equal(evaluateDesktopTransition(state("P6"), {
      target_stage: target, completion_satisfied: true,
    }).code, "ILLEGAL_TRANSITION", target);
  }
});

test("Desktop transitions require completion and Maker-owned boundary authorization", () => {
  assert.equal(evaluateDesktopTransition(state("P2"), {
    target_stage: "P3", completion_satisfied: false,
  }).code, "COMPLETION_CONDITIONS_REQUIRED");
  assert.equal(evaluateDesktopTransition(state("P0"), {
    target_stage: "P1", completion_satisfied: true,
  }).code, "MAKER_AUTHORIZATION_REQUIRED");
  assert.equal(evaluateDesktopTransition(state("P3"), {
    target_stage: "P4", completion_satisfied: true, changes_boundary: true,
  }).code, "MAKER_AUTHORIZATION_REQUIRED");
});
