import { randomUUID } from "node:crypto";

import { consumePrompt, promptAgeMs, promptPolicy, readPrompt } from "./prompt-events.mjs";

const DECISION_KINDS = new Set(["PRODUCT_DECISION", "ARCHITECTURE_DECISION"]);

function findPendingRequest(snapshot, proposal) {
  if (typeof proposal.request_id !== "string" || proposal.request_id.length === 0) {
    throw new Error("REQUEST_ID_REQUIRED");
  }
  const pending = snapshot.state.pending_requests.find((request) => (
    request.request_id === proposal.request_id && request.status === "PENDING"
  ));
  if (!pending) throw new Error("PENDING_REQUEST_NOT_FOUND");
  if (pending.scope_digest !== proposal.scope_digest) throw new Error("SCOPE_DIGEST_MISMATCH");
  if (pending.operation !== proposal.operation) throw new Error("OPERATION_MISMATCH");
  if (pending.project_revision !== snapshot.state.revision) throw new Error("REQUEST_REVISION_MISMATCH");
  return pending;
}

export function prepareChange(snapshot, proposal) {
  if (snapshot.activation.status !== "ACTIVE") throw new Error("PROJECT_NOT_ACTIVE");
  if (proposal.project_id !== snapshot.state.project_id) throw new Error("PROJECT_CONTEXT_MISMATCH");

  if (proposal.change_kind === "RUNTIME_ASSUMPTION_EVIDENCE") {
    if (!Array.isArray(proposal.evidence_refs) || proposal.evidence_refs.length === 0) {
      throw new Error("EVIDENCE_REQUIRED");
    }
    return Object.freeze({ ...proposal, requires_authorization: false, project_revision: snapshot.state.revision });
  }

  const pending = findPendingRequest(snapshot, proposal);
  const requiresAuthorization = DECISION_KINDS.has(proposal.change_kind)
    || proposal.requires_authorization === true;
  return Object.freeze({
    ...proposal,
    requires_authorization: requiresAuthorization,
    project_revision: snapshot.state.revision,
    pending_request: structuredClone(pending),
  });
}

function hasExplicitApproval(text) {
  return /(?:明确批准|正式批准|明确同意|\b(?:approve|approved|authorize|authorized)\b)/iu.test(text);
}

function hasExplicitDecline(text) {
  return /(?:明确拒绝|正式拒绝|明确撤回|正式撤回|拒绝批准|明确不同意|\b(?:reject|rejected|decline|declined|withdraw|withdrawn)\b)/iu.test(text);
}

async function authorizePreparedPrompt(prepared, promptRef, options, intentMatches, errorCode) {
  if (!prepared.requires_authorization) throw new Error("AUTHORIZATION_NOT_REQUIRED");
  const stored = await readPrompt(promptRef);
  if (
    stored.project_id !== prepared.project_id
    || stored.session_id !== prepared.session_id
    || stored.turn_id !== prepared.turn_id
  ) throw new Error("PROMPT_CONTEXT_MISMATCH");

  const age = await promptAgeMs(promptRef, options.now ?? new Date());
  if (age < 0 || age > promptPolicy.maxAgeMs) {
    await consumePrompt(promptRef);
    throw new Error("PROMPT_EXPIRED");
  }
  if (!stored.excerpt.includes(prepared.request_id) || !stored.excerpt.includes(prepared.scope_digest)) {
    throw new Error("PROMPT_SCOPE_NOT_CONFIRMED");
  }
  if (!intentMatches(stored.excerpt)) throw new Error(errorCode);

  const authorization = Object.freeze({
    authorization_id: `authorization-${randomUUID()}`,
    request_id: prepared.request_id,
    prompt_digest: stored.prompt_digest,
  });
  await consumePrompt(promptRef);
  return authorization;
}

export async function authorizePreparedChange(prepared, promptRef, options = {}) {
  return authorizePreparedPrompt(
    prepared, promptRef, options, hasExplicitApproval, "EXPLICIT_APPROVAL_REQUIRED",
  );
}

export async function authorizePreparedDecline(prepared, promptRef, options = {}) {
  return authorizePreparedPrompt(
    prepared, promptRef, options, hasExplicitDecline, "EXPLICIT_DECLINE_REQUIRED",
  );
}
