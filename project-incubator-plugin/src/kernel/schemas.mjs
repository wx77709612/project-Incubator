import { z } from "zod";

const id = z.string().min(1).max(128).regex(/^[A-Za-z0-9][A-Za-z0-9._:-]*$/);
const text = z.string().min(1).max(4000);
const shortText = z.string().min(1).max(500);
const timestamp = z.string().datetime({ offset: true });
const digest = z.string().regex(/^[a-f0-9]{64}$/);
const evidenceLevel = z.enum(["E0", "E1", "E2", "E3", "E4", "E5"]);
const boundedTextList = z.array(shortText).max(100);

const activationSchema = z.object({
  schema_version: z.literal("1.0"), project_id: id,
  plugin_id: z.literal("project-incubator-plugin"), plugin_version: z.string().min(1).max(64),
  status: z.enum(["ACTIVE", "INACTIVE"]), project_type_id: id, child_skill_id: id,
  host_profile_id: id.nullable(),
}).strict();

const capabilitySchema = z.object({
  capability_id: id, claim: text, evidence_level: evidenceLevel,
  status: z.enum(["HYPOTHESIZED", "ACTIVE", "SUPPORTED", "BLOCKED"]).optional(),
  supported_boundary: boundedTextList.optional(), excluded_boundary: boundedTextList.optional(),
  evidence_refs: z.array(shortText).max(100).optional(), baseline_id: id.nullable().optional(),
  confidence: z.enum(["LOW", "MEDIUM", "HIGH"]).optional(),
}).strict();

const decisionSchema = z.object({
  decision_id: id, kind: z.enum(["PRODUCT", "ARCHITECTURE"]),
  status: z.enum(["ACTIVE", "SUPERSEDED", "PARTIALLY_SUPERSEDED", "REVOKED"]),
  statement: text, authorization_ref: id, confirmed_at: timestamp,
}).strict();

const activationProductDecisionSchema = z.object({
  decision_id: id,
  statement: text,
}).strict();

const assumptionSchema = z.object({
  assumption_id: id, statement: text,
  status: z.enum(["ACTIVE", "SUPPORTED", "INVALIDATED"]),
  evidence_refs: z.array(shortText).max(100), invalidated_at: timestamp.optional(),
}).strict();

const gateSchema = z.object({
  gate_id: id, status: z.enum(["PENDING", "BLOCKED", "PASSED"]),
  reason: shortText.optional(), required_evidence_level: evidenceLevel.optional(),
}).strict();

const riskSchema = z.object({
  risk_id: id, summary: text, severity: z.enum(["LOW", "MEDIUM", "HIGH"]),
  status: z.enum(["OPEN", "MITIGATED", "ACCEPTED"]),
}).strict();

const pendingRequestSchema = z.object({
  request_id: id, operation: id, scope_digest: digest,
  status: z.enum(["PENDING", "AUTHORIZED", "CONSUMED", "DECLINED", "EXPIRED"]),
  created_at: timestamp, project_revision: z.number().int().nonnegative(),
  payload: z.record(z.unknown()).optional(),
}).strict();

const baselineSchema = z.object({
  baseline_id: id, capability_id: id, evidence_level: evidenceLevel,
  environment: shortText, artifact_refs: z.array(shortText).max(100), established_at: timestamp,
}).strict();

const projectStateSchema = z.object({
  schema_version: z.literal("1.0"), project_id: id, revision: z.number().int().nonnegative(),
  boundary: z.object({ objective: text, supported: boundedTextList, excluded: boundedTextList }).strict(),
  workflow: z.object({
    stage: id, status: z.enum(["NOT_STARTED", "ACTIVE", "BLOCKED", "AWAITING_GATE", "COMPLETED"]),
    completed: boundedTextList, allowed_next: z.array(id).max(20), return_stage: id.nullable().optional(),
  }).strict(),
  capabilities: z.array(capabilitySchema).max(100),
  decisions: z.object({ active: z.array(decisionSchema).max(100), archive_ref: shortText.nullable() }).strict(),
  assumptions: z.array(assumptionSchema).max(100),
  plan: z.object({ current_action: shortText, next_action: shortText, completion_conditions: boundedTextList }).strict(),
  gates: z.array(gateSchema).max(100), risks: z.array(riskSchema).max(100),
  pending_requests: z.array(pendingRequestSchema).max(50), baselines: z.array(baselineSchema).max(100),
  human_validation: z.object({
    limit: z.union([z.literal("UNSET"), z.number().int().nonnegative()]),
    consumed: z.number().int().nonnegative(),
  }).strict(),
  last_change: z.object({
    operation: id, changed_at: timestamp, summary: shortText, receipt_id: id.optional(),
  }).strict(),
  archive_refs: z.array(shortText).max(100),
}).strict();

const authorizationRefSchema = z.object({
  authorization_id: id, request_id: id, prompt_digest: digest,
}).strict();

const receiptSchema = z.object({
  schema_version: z.literal("1.0"), receipt_id: id, project_id: id, operation: id,
  previous_revision: z.number().int().nonnegative().nullable(), new_revision: z.number().int().nonnegative(),
  previous_state_hash: digest.nullable(), new_state_hash: digest,
  authorization_ref: authorizationRefSchema.nullable(), committed_at: timestamp,
}).strict();

export function parseActivation(value) { return activationSchema.parse(value); }
export function parseProjectState(value) { return projectStateSchema.parse(value); }
export function parseReceipt(value) { return receiptSchema.parse(value); }
export function parseActivationProductDecisions(value) {
  return z.array(activationProductDecisionSchema).min(1).max(100).parse(value);
}

const preActivationNarrative = /(?:ACTIVATION_DRAFT|initialize_project|activation request|not yet activated|awaiting activation|pending activation|等待.{0,30}(?:激活|Activation)|尚未激活|激活前)/iu;

export function parsePostActivationInitialState(value) {
  const state = parseProjectState(value);
  const narrative = [
    state.plan.current_action,
    ...state.plan.completion_conditions,
    state.last_change.summary,
  ].join("\n");
  if (
    state.last_change.operation !== "INITIALIZE_PROJECT"
    || state.pending_requests.length !== 0
    || state.decisions.active.length !== 0
    || preActivationNarrative.test(narrative)
  ) throw new Error("INITIAL_STATE_NOT_POST_ACTIVATION");
  return state;
}

export const schemas = Object.freeze({
  activation: activationSchema, projectState: projectStateSchema, receipt: receiptSchema,
});
