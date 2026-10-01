const STAGES = [
  "M0_BOUNDARY", "M1_RISK_MODEL", "M2_VERTICAL_SLICE",
  "M3_BUILD_PACKAGE", "M4_TARGET_VALIDATION", "M5_EXPAND_RELEASE",
];
const REVIEW_ORIGINS = new Set(["M2_VERTICAL_SLICE", "M3_BUILD_PACKAGE", "M4_TARGET_VALIDATION"]);

function rejected(code) { return { allowed: false, code }; }

function allowedNext(stage, returnStage = null) {
  if (stage === "MODEL_REVIEW") return returnStage ? [returnStage] : [];
  const index = STAGES.indexOf(stage);
  if (index < 0 || index === STAGES.length - 1) return [];
  const next = [STAGES[index + 1]];
  if (REVIEW_ORIGINS.has(stage)) next.push("MODEL_REVIEW");
  return next;
}

function movedWorkflow(workflow, stage, returnStage = null) {
  return {
    ...workflow,
    stage,
    allowed_next: allowedNext(stage, returnStage),
    return_stage: returnStage,
  };
}

export function evaluateModTransition(state, request) {
  const current = state.workflow.stage;
  if (request.changes_boundary && !request.maker_authorized) return rejected("MAKER_AUTHORIZATION_REQUIRED");
  if (request.target_stage === "MODEL_REVIEW") {
    if (!REVIEW_ORIGINS.has(current) || !request.model_invalidated) return rejected("MODEL_REVIEW_NOT_AVAILABLE");
    return {
      allowed: true, code: "MODEL_REVIEW_ENTERED", semantic: "CORRECTION",
      workflow: movedWorkflow(state.workflow, "MODEL_REVIEW", current),
    };
  }
  if (current === "MODEL_REVIEW") {
    if (!request.model_updated || request.target_stage !== state.workflow.return_stage) {
      return rejected("MODEL_REVIEW_RETURN_INVALID");
    }
    return {
      allowed: true, code: "MODEL_REVIEW_RESUMED", semantic: "CORRECTION",
      workflow: movedWorkflow(state.workflow, request.target_stage),
    };
  }
  const index = STAGES.indexOf(current);
  if (index < 0 || STAGES[index + 1] !== request.target_stage) return rejected("ILLEGAL_TRANSITION");
  if (!request.completion_satisfied) return rejected("COMPLETION_CONDITIONS_REQUIRED");
  if (current === "M0_BOUNDARY" && !request.maker_authorized) return rejected("MAKER_AUTHORIZATION_REQUIRED");
  return {
    allowed: true, code: "TRANSITION_ALLOWED", semantic: "STAGE_ADVANCE",
    workflow: movedWorkflow(state.workflow, request.target_stage),
  };
}

export const evaluateTransition = evaluateModTransition;
export const modStages = Object.freeze([...STAGES, "MODEL_REVIEW"]);
