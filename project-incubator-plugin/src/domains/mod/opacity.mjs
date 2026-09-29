const DIMENSIONS = [
  "contract", "hidden_state", "control", "determinism",
  "observability", "automation", "attribution", "version_stability",
];
const LEVELS = ["E0", "E1", "E2", "E3", "E4", "E5"];

export function assessCapabilityOpacity(input) {
  const scores = {};
  const unknown = [];
  for (const dimension of DIMENSIONS) {
    const value = input[dimension];
    if (value === "UNKNOWN") {
      scores[dimension] = 1;
      unknown.push(dimension);
    } else if (Number.isInteger(value) && value >= 0 && value <= 2) {
      scores[dimension] = value;
    } else {
      throw new Error(`INVALID_OPACITY_DIMENSION_${dimension.toUpperCase()}`);
    }
  }
  const values = Object.values(scores);
  return {
    scores,
    unknown_dimensions: unknown,
    total: values.reduce((sum, value) => sum + value, 0),
    vertical_slice_recommended: values.includes(2) || values.filter((value) => value === 1).length >= 2,
  };
}

export function compareEvidence(left, right) {
  const a = LEVELS.indexOf(left); const b = LEVELS.indexOf(right);
  if (a < 0 || b < 0) throw new Error("INVALID_EVIDENCE_LEVEL");
  return a - b;
}

export function constrainSemanticEvidence(input) {
  let level = input.current;
  if (!LEVELS.includes(level)) throw new Error("INVALID_EVIDENCE_LEVEL");
  if ((input.target_environment_successes ?? 0) > 0 && compareEvidence(level, "E3") < 0) level = "E3";
  return level;
}

export function resolveHumanBudget(input) {
  if (input.maker_limit === undefined) return "UNSET";
  if (!Number.isInteger(input.maker_limit) || input.maker_limit < 0) throw new Error("INVALID_HUMAN_VALIDATION_LIMIT");
  return input.maker_limit;
}

export const opacityDimensions = Object.freeze([...DIMENSIONS]);
export const evidenceLevels = Object.freeze([...LEVELS]);
