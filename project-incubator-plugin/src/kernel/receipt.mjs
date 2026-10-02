import { randomUUID } from "node:crypto";

import { hashJson } from "./canonical-json.mjs";
import { parseReceipt } from "./schemas.mjs";

export function buildReceipt({
  projectId,
  operation,
  previousState,
  nextState,
  authorizationRef,
  committedAt = new Date().toISOString(),
  receiptId = `receipt-${randomUUID()}`,
}) {
  return parseReceipt({
    schema_version: "1.0",
    receipt_id: receiptId,
    project_id: projectId,
    operation,
    previous_revision: previousState?.revision ?? null,
    new_revision: nextState.revision,
    previous_state_hash: previousState ? hashJson(previousState) : null,
    new_state_hash: hashJson(nextState),
    authorization_ref: authorizationRef ?? null,
    committed_at: committedAt,
  });
}

export function evaluateReceipt(state, receipt, expectedReceiptId) {
  if (expectedReceiptId && receipt.receipt_id !== expectedReceiptId) {
    return { verified: false, reason: "RECEIPT_ID_MISMATCH", receipt };
  }
  if (receipt.project_id !== state.project_id) {
    return { verified: false, reason: "PROJECT_ID_MISMATCH", receipt };
  }
  if (receipt.new_revision !== state.revision) {
    return { verified: false, reason: "REVISION_MISMATCH", receipt };
  }
  if (receipt.new_state_hash !== hashJson(state)) {
    return { verified: false, reason: "STATE_HASH_MISMATCH", receipt };
  }
  if (state.last_change.receipt_id !== receipt.receipt_id) {
    return { verified: false, reason: "STATE_RECEIPT_REF_MISMATCH", receipt };
  }
  return { verified: true, reason: null, receipt };
}
