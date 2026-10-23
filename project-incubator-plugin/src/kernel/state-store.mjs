import { createHash, randomUUID } from "node:crypto";
import { mkdir, open, readFile, rename, rm } from "node:fs/promises";
import path from "node:path";

import { createAgentEntry, inspectAgentEntry, rollbackAgentEntry } from "./agent-entry.mjs";
import { canonicalJson, hashJson } from "./canonical-json.mjs";
import { buildReceipt, evaluateReceipt } from "./receipt.mjs";
import { parseActivation, parseProjectState, parseReceipt } from "./schemas.mjs";

const CONTROL_DIR = ".project-incubator";
const ACTIVATION_FILE = "activation.json";
const STATE_FILE = "state.json";
const RECEIPT_FILE = "latest-receipt.json";
const queues = new Map();

function controlPaths(root) {
  const control = path.join(root, CONTROL_DIR);
  return {
    control,
    activation: path.join(control, ACTIVATION_FILE),
    state: path.join(control, STATE_FILE),
    receipt: path.join(control, RECEIPT_FILE),
  };
}

async function readOptional(target) {
  try {
    return await readFile(target, "utf8");
  } catch (error) {
    if (error?.code === "ENOENT") return null;
    throw error;
  }
}

async function atomicWrite(target, content, hooks = {}, useHook = true, operation = undefined) {
  if (useHook) hooks.beforeAtomicWrite?.(target, content, operation);
  const temporary = `${target}.${process.pid}.${randomUUID()}.tmp`;
  const handle = await open(temporary, "wx");
  try {
    await handle.writeFile(content, "utf8");
    await handle.sync();
  } finally {
    await handle.close();
  }
  try {
    await rename(temporary, target);
  } catch (error) {
    await rm(temporary, { force: true });
    throw error;
  }
}

async function restore(target, previous) {
  if (previous === null) {
    await rm(target, { force: true });
  } else {
    await atomicWrite(target, previous, {}, false);
  }
}

async function readOptionalBytes(target) {
  try {
    return await readFile(target);
  } catch (error) {
    if (error?.code === "ENOENT") return null;
    throw error;
  }
}

function bytesFingerprint(bytes) {
  return bytes === null
    ? { exists: false }
    : { exists: true, sha256: createHash("sha256").update(bytes).digest("hex") };
}

function authorityFingerprints(values) {
  return {
    activation: bytesFingerprint(values[0]),
    state: bytesFingerprint(values[1]),
    receipt: bytesFingerprint(values[2]),
  };
}

function sameFingerprints(left, right) {
  return canonicalJson(left) === canonicalJson(right);
}

async function withProjectQueue(root, operation) {
  const key = path.resolve(root).toLowerCase();
  const previous = queues.get(key) ?? Promise.resolve();
  let release;
  const gate = new Promise((resolve) => { release = resolve; });
  const chain = previous.then(() => gate);
  queues.set(key, chain);
  await previous;
  try {
    return await operation();
  } finally {
    release();
    if (queues.get(key) === chain) queues.delete(key);
  }
}

function jsonFile(value) {
  return `${canonicalJson(value)}\n`;
}

function parseJson(raw, label) {
  try {
    return JSON.parse(raw);
  } catch (error) {
    throw new Error(`${label}_INVALID_JSON`, { cause: error });
  }
}

export async function assertProjectUninitialized(root) {
  const files = controlPaths(root);
  const existing = await Promise.all([
    readOptional(files.activation), readOptional(files.state), readOptional(files.receipt),
  ]);
  const present = existing.filter((value) => value !== null).length;
  if (present === 0) return;
  if (present === existing.length) throw new Error("PROJECT_ALREADY_INITIALIZED");
  throw new Error("PROJECT_CONTROL_STATE_INCOMPLETE");
}

export function createStateStore(hooks = {}) {
  async function readProjectSnapshot(root) {
    const files = controlPaths(root);
    const [activationRaw, stateRaw, receiptRaw] = await Promise.all([
      readFile(files.activation, "utf8"),
      readFile(files.state, "utf8"),
      readFile(files.receipt, "utf8"),
    ]);
    const activation = parseActivation(parseJson(activationRaw, "ACTIVATION"));
    const state = parseProjectState(parseJson(stateRaw, "STATE"));
    const receipt = parseReceipt(parseJson(receiptRaw, "RECEIPT"));
    if (activation.project_id !== state.project_id || state.project_id !== receipt.project_id) {
      throw new Error("PROJECT_ID_MISMATCH");
    }
    return { root, activation, state, receipt, state_hash: hashJson(state) };
  }

  async function verifyLatestReceipt(root, expectedReceiptId) {
    const snapshot = await readProjectSnapshot(root);
    return evaluateReceipt(snapshot.state, snapshot.receipt, expectedReceiptId);
  }

  async function initialize(root, activationInput, stateInput, authorizationRef, agentEntryTemplate) {
    return withProjectQueue(root, async () => {
      const files = controlPaths(root);
      await mkdir(files.control, { recursive: true });
      const existing = await Promise.all([
        readOptional(files.activation), readOptional(files.state), readOptional(files.receipt),
      ]);
      if (existing.some((value) => value !== null)) throw new Error("PROJECT_ALREADY_INITIALIZED");

      const activation = parseActivation(activationInput);
      const receiptId = `receipt-${randomUUID()}`;
      const state = parseProjectState({
        ...stateInput,
        revision: 0,
        project_id: activation.project_id,
        last_change: { ...stateInput.last_change, receipt_id: receiptId },
      });
      const receipt = buildReceipt({
        projectId: activation.project_id,
        operation: "INITIALIZE_PROJECT",
        previousState: null,
        nextState: state,
        authorizationRef,
        receiptId,
      });
      let agentEntry = null;
      let agentEntryRollback = null;
      try {
        if (agentEntryTemplate) {
          const inspected = await inspectAgentEntry(root, agentEntryTemplate);
          if (inspected.status === "MISSING") {
            const created = await createAgentEntry(root, agentEntryTemplate);
            agentEntry = created.result;
            agentEntryRollback = created.rollbackToken;
          } else {
            agentEntry = { path: inspected.path, status: inspected.status };
          }
        }
        await atomicWrite(files.activation, jsonFile(activation), hooks);
        await atomicWrite(files.state, jsonFile(state), hooks);
        await atomicWrite(files.receipt, jsonFile(receipt), hooks);
        const verified = await verifyLatestReceipt(root, receipt.receipt_id);
        if (!verified.verified) throw new Error(verified.reason);
        return { receipt, agent_entry: agentEntry };
      } catch (error) {
        await Promise.all(existing.map((value, index) => restore(
          [files.activation, files.state, files.receipt][index], value,
        )));
        if (agentEntryRollback) {
          const rollback = await rollbackAgentEntry(root, agentEntryRollback);
          if (rollback.residual_paths.length) {
            const rollbackError = new Error("AGENT_ENTRY_ROLLBACK_INCOMPLETE", { cause: error });
            rollbackError.residual_paths = rollback.residual_paths;
            throw rollbackError;
          }
        }
        throw error;
      }
    });
  }

  async function initializeProjectState(root, activationInput, stateInput, authorizationRef) {
    return (await initialize(root, activationInput, stateInput, authorizationRef, null)).receipt;
  }

  async function initializeProjectWithAgentEntry(
    root, activationInput, stateInput, authorizationRef, agentEntryTemplate,
  ) {
    return initialize(root, activationInput, stateInput, authorizationRef, agentEntryTemplate);
  }

  async function commitProjectState(root, request) {
    return withProjectQueue(root, async () => {
      const files = controlPaths(root);
      const [activationRaw, stateRaw, receiptRaw] = await Promise.all([
        readFile(files.activation, "utf8"), readFile(files.state, "utf8"), readFile(files.receipt, "utf8"),
      ]);
      const activation = parseActivation(parseJson(activationRaw, "ACTIVATION"));
      const current = parseProjectState(parseJson(stateRaw, "STATE"));
      parseReceipt(parseJson(receiptRaw, "RECEIPT"));
      if (current.revision !== request.expectedRevision) throw new Error("REVISION_CONFLICT");
      if (typeof request.mutate !== "function") throw new Error("MUTATE_REQUIRED");

      const receiptId = `receipt-${randomUUID()}`;
      const candidate = request.mutate(structuredClone(current));
      const next = parseProjectState({
        ...candidate,
        project_id: activation.project_id,
        revision: current.revision + 1,
        last_change: { ...candidate.last_change, operation: request.operation, receipt_id: receiptId },
      });
      const receipt = buildReceipt({
        projectId: activation.project_id,
        operation: request.operation,
        previousState: current,
        nextState: next,
        authorizationRef: request.authorizationRef ?? null,
        receiptId,
      });

      try {
        await atomicWrite(files.state, jsonFile(next), hooks);
        let stateReadback = await readFile(files.state, "utf8");
        if (hooks.corruptStateReadback) stateReadback = `${stateReadback} `;
        if (stateReadback !== jsonFile(next)) throw new Error("STATE_READBACK_MISMATCH");
        await atomicWrite(files.receipt, jsonFile(receipt), hooks);
        const verified = await verifyLatestReceipt(root, receipt.receipt_id);
        if (!verified.verified) throw new Error(verified.reason);
        return receipt;
      } catch (error) {
        await restore(files.state, stateRaw);
        await restore(files.receipt, receiptRaw);
        throw error;
      }
    });
  }

  async function recoverProjectAuthority(root, candidateInput, expectedFingerprints, authorizationRef) {
    return withProjectQueue(root, async () => {
      const files = controlPaths(root);
      await mkdir(files.control, { recursive: true });
      const targets = [files.activation, files.state, files.receipt];
      const relativeTargets = [
        ".project-incubator/activation.json",
        ".project-incubator/state.json",
        ".project-incubator/latest-receipt.json",
      ];
      const original = await Promise.all(targets.map((target) => readOptionalBytes(target)));
      if (!sameFingerprints(authorityFingerprints(original), expectedFingerprints)) {
        throw new Error("RECOVERY_SOURCE_CHANGED");
      }

      const activation = parseActivation(candidateInput.activation);
      const previousState = candidateInput.previous_state === null
        ? null
        : parseProjectState(candidateInput.previous_state);
      const candidateState = parseProjectState(candidateInput.state);
      const baseline = previousState ? "CONTINUED" : "REESTABLISHED";
      const expectedRevision = previousState ? previousState.revision + 1 : 0;
      if (candidateInput.baseline !== baseline || candidateState.revision !== expectedRevision) {
        throw new Error("RECOVERY_STATE_REVISION_INVALID");
      }
      if (activation.project_id !== candidateState.project_id
        || previousState?.project_id !== undefined
          && previousState.project_id !== candidateState.project_id) {
        throw new Error("PROJECT_ID_MISMATCH");
      }
      if (candidateState.pending_requests.length !== 0
        || candidateState.last_change.operation !== "RECOVER_PROJECT_AUTHORITY") {
        throw new Error("RECOVERY_CANDIDATE_INVALID");
      }

      const receiptId = `receipt-${randomUUID()}`;
      const state = parseProjectState({
        ...candidateState,
        last_change: { ...candidateState.last_change, receipt_id: receiptId },
      });
      const receipt = buildReceipt({
        projectId: activation.project_id,
        operation: "RECOVER_PROJECT_AUTHORITY",
        previousState,
        nextState: state,
        authorizationRef,
        committedAt: state.last_change.changed_at,
        receiptId,
      });
      const nextBytes = [
        Buffer.from(jsonFile(activation)),
        Buffer.from(jsonFile(state)),
        Buffer.from(jsonFile(receipt)),
      ];

      try {
        for (let index = 0; index < targets.length; index += 1) {
          await atomicWrite(targets[index], nextBytes[index], hooks, true, "RECOVERY_WRITE");
          let readback = await readFile(targets[index]);
          if (hooks.corruptRecoveryReadback === relativeTargets[index]) {
            readback = Buffer.concat([readback, Buffer.from(" ")]);
          }
          if (!readback.equals(nextBytes[index])) throw new Error("RECOVERY_READBACK_MISMATCH");
        }
        const verified = await verifyLatestReceipt(root, receipt.receipt_id);
        if (!verified.verified) throw new Error(verified.reason);
        return {
          activation,
          receipt,
          recovery: { baseline },
        };
      } catch (cause) {
        const restoreFailures = new Set();
        for (let index = 0; index < targets.length; index += 1) {
          try {
            hooks.beforeRecoveryRestore?.(targets[index]);
            if (original[index] === null) {
              await rm(targets[index], { force: true });
            } else {
              await atomicWrite(targets[index], original[index], {}, false, "RECOVERY_ROLLBACK");
            }
          } catch {
            restoreFailures.add(index);
          }
        }
        for (let index = 0; index < targets.length; index += 1) {
          try {
            const readback = await readOptionalBytes(targets[index]);
            const matches = original[index] === null
              ? readback === null
              : readback !== null && readback.equals(original[index]);
            if (matches) restoreFailures.delete(index);
            else restoreFailures.add(index);
          } catch {
            restoreFailures.add(index);
          }
        }
        if (restoreFailures.size === 0) {
          throw new Error("RECOVERY_WRITE_FAILED", { cause });
        }
        const error = new Error("RECOVERY_ROLLBACK_INCOMPLETE", { cause });
        error.residual_paths = [...restoreFailures].map((index) => relativeTargets[index]);
        throw error;
      }
    });
  }

  return {
    readProjectSnapshot,
    verifyLatestReceipt,
    initializeProjectState,
    initializeProjectWithAgentEntry,
    commitProjectState,
    recoverProjectAuthority,
  };
}

const defaultStore = createStateStore();
export const readProjectSnapshot = defaultStore.readProjectSnapshot;
export const verifyLatestReceipt = defaultStore.verifyLatestReceipt;
export const initializeProjectState = defaultStore.initializeProjectState;
export const initializeProjectWithAgentEntry = defaultStore.initializeProjectWithAgentEntry;
export const commitProjectState = defaultStore.commitProjectState;
export const recoverProjectAuthority = defaultStore.recoverProjectAuthority;
