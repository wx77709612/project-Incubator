const STAGES = ["P0", "P1", "P2", "P3", "P4", "P5", "P6"];
const ITERATION_TARGETS = ["P2", "P3", "P4", "P5"];

function rejected(code) { return { allowed: false, code }; }

function allowedNext(stage) {
  if (stage === "P6") return [...ITERATION_TARGETS];
  const index = STAGES.indexOf(stage);
  if (index < 0 || index === STAGES.length - 1) return [];
  return [STAGES[index + 1]];
}

function entryWorkflow(stage) {
  return { stage, allowed_next: allowedNext(stage), return_stage: null };
}

function movedWorkflow(workflow, stage) {
  return { ...workflow, stage, allowed_next: allowedNext(stage), return_stage: null };
}

export function evaluateWebEntry(state) {
  const entry = state?.workflow?.entry;
  if (!entry) return rejected("WORKFLOW_ENTRY_REQUIRED");
  if (!new Set(["NEW_PROJECT", "ADOPT_EXISTING"]).has(entry.mode)) {
    return rejected("WORKFLOW_ENTRY_MODE_INVALID");
  }
  if (entry.initial_stage !== state.workflow.stage) return rejected("WORKFLOW_ENTRY_STATE_MISMATCH");
  if (!STAGES.includes(entry.initial_stage)) return rejected("WORKFLOW_ENTRY_STAGE_INVALID");
  if (entry.mode === "NEW_PROJECT" && entry.initial_stage !== "P0") {
    return rejected("WORKFLOW_ENTRY_STAGE_INVALID");
  }
  if (entry.mode === "ADOPT_EXISTING"
    && (!Array.isArray(entry.evidence_refs) || entry.evidence_refs.length === 0)) {
    return rejected("WORKFLOW_ENTRY_EVIDENCE_REQUIRED");
  }
  return {
    allowed: true,
    code: "WORKFLOW_ENTRY_ALLOWED",
    semantic: "ENTRY",
    workflow: entryWorkflow(entry.initial_stage),
  };
}

export function evaluateWebTransition(state, request) {
  const current = state.workflow.stage;
  if (request.changes_boundary && !request.maker_authorized) return rejected("MAKER_AUTHORIZATION_REQUIRED");
  if (!allowedNext(current).includes(request.target_stage)) return rejected("ILLEGAL_TRANSITION");
  if (!request.completion_satisfied) return rejected("COMPLETION_CONDITIONS_REQUIRED");
  if (current === "P0" && !request.maker_authorized) return rejected("MAKER_AUTHORIZATION_REQUIRED");
  return {
    allowed: true,
    code: "TRANSITION_ALLOWED",
    semantic: current === "P6" ? "ITERATION" : "STAGE_ADVANCE",
    workflow: movedWorkflow(state.workflow, request.target_stage),
  };
}

export const evaluateEntry = evaluateWebEntry;
export const evaluateTransition = evaluateWebTransition;
export const webStages = Object.freeze([...STAGES]);
