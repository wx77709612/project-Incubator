import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";

import { evaluateReceipt } from "./receipt.mjs";
import { parseActivation, parseProjectState, parseReceipt } from "./schemas.mjs";
import { recoverProjectAuthority as recoverFromStateStore } from "./state-store.mjs";

const DEFINITIONS = [
  {
    key: "activation",
    path: ".project-incubator/activation.json",
    parser: parseActivation,
    invalidJson: "ACTIVATION_INVALID_JSON",
    invalidSchema: "ACTIVATION_SCHEMA_INVALID",
  },
  {
    key: "state",
    path: ".project-incubator/state.json",
    parser: parseProjectState,
    invalidJson: "STATE_INVALID_JSON",
    invalidSchema: "STATE_SCHEMA_INVALID",
  },
  {
    key: "receipt",
    path: ".project-incubator/latest-receipt.json",
    parser: parseReceipt,
    invalidJson: "RECEIPT_INVALID_JSON",
    invalidSchema: "RECEIPT_SCHEMA_INVALID",
  },
];

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

async function inspectOne(root, definition) {
  const target = path.join(root, ...definition.path.split("/"));
  let bytes;
  try {
    bytes = await readFile(target);
  } catch (error) {
    if (error?.code === "ENOENT") {
      return {
        key: definition.key,
        item: { path: definition.path, status: "MISSING" },
        fingerprint: { exists: false },
        value: null,
      };
    }
    return {
      key: definition.key,
      item: { path: definition.path, status: "INVALID", error_code: `${definition.key.toUpperCase()}_READ_FAILED` },
      fingerprint: { exists: true, sha256: null },
      value: null,
    };
  }
  const fingerprint = { exists: true, sha256: sha256(bytes) };
  let json;
  try {
    json = JSON.parse(bytes.toString("utf8"));
  } catch {
    return {
      key: definition.key,
      item: { path: definition.path, status: "INVALID", sha256: fingerprint.sha256, error_code: definition.invalidJson },
      fingerprint,
      value: null,
    };
  }
  try {
    const value = definition.parser(json);
    return {
      key: definition.key,
      item: { path: definition.path, status: "VALID", sha256: fingerprint.sha256 },
      fingerprint,
      value,
    };
  } catch {
    return {
      key: definition.key,
      item: { path: definition.path, status: "INVALID", sha256: fingerprint.sha256, error_code: definition.invalidSchema },
      fingerprint,
      value: null,
    };
  }
}

function invalidate(entry, errorCode) {
  entry.item.status = "INVALID";
  entry.item.error_code = errorCode;
}

export async function diagnoseAuthority(root) {
  const inspected = await Promise.all(DEFINITIONS.map((definition) => inspectOne(root, definition)));
  const byKey = Object.fromEntries(inspected.map((entry) => [entry.key, entry]));
  const { activation, state, receipt } = byKey;

  if (activation.value && state.value && activation.value.project_id !== state.value.project_id) {
    invalidate(activation, "PROJECT_ID_MISMATCH");
    invalidate(state, "PROJECT_ID_MISMATCH");
  }
  if (state.value && receipt.value) {
    const verification = evaluateReceipt(state.value, receipt.value);
    if (!verification.verified) invalidate(receipt, verification.reason);
  }
  if (activation.value && receipt.value && activation.value.project_id !== receipt.value.project_id) {
    invalidate(receipt, "PROJECT_ID_MISMATCH");
  }

  const snapshotValid = inspected.every((entry) => entry.item.status === "VALID");
  return {
    items: inspected.map((entry) => entry.item),
    fingerprints: Object.fromEntries(inspected.map((entry) => [entry.key, entry.fingerprint])),
    snapshot_valid: snapshotValid,
    valid_activation: activation.value,
    valid_state: state.value,
    valid_receipt: receipt.value,
  };
}

export function normalizeRecoveryCandidate(diagnostics, activationInput, stateInput, now = new Date()) {
  if (diagnostics?.snapshot_valid) throw new Error("AUTHORITY_RECOVERY_NOT_REQUIRED");
  const activation = parseActivation(activationInput);
  const parsedState = parseProjectState(stateInput);
  if (activation.project_id !== parsedState.project_id) throw new Error("PROJECT_ID_MISMATCH");
  const previousState = diagnostics?.valid_state ? parseProjectState(diagnostics.valid_state) : null;
  const expectedRevision = previousState ? previousState.revision + 1 : 0;
  if (parsedState.revision !== expectedRevision) throw new Error("RECOVERY_STATE_REVISION_INVALID");
  const changedAt = (now instanceof Date ? now : new Date(now)).toISOString();
  const state = parseProjectState({
    ...parsedState,
    project_id: activation.project_id,
    revision: expectedRevision,
    pending_requests: [],
    last_change: {
      operation: "RECOVER_PROJECT_AUTHORITY",
      changed_at: changedAt,
      summary: "已按 Maker 授权恢复 Managed Project 权威集合。",
    },
  });
  return {
    activation,
    state,
    previous_state: previousState,
    baseline: previousState ? "CONTINUED" : "REESTABLISHED",
  };
}

export async function recoverProjectAuthority(root, candidate, expectedFingerprints, authorizationRef) {
  return recoverFromStateStore(root, candidate, expectedFingerprints, authorizationRef);
}
