import { randomUUID } from "node:crypto";
import { mkdir, open, readFile, rename, rm } from "node:fs/promises";
import path from "node:path";

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

async function atomicWrite(target, content, hooks = {}, useHook = true) {
  if (useHook) hooks.beforeAtomicWrite?.(target, content);
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

  async function initializeProjectState(root, activationInput, stateInput, authorizationRef) {
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
      try {
        await atomicWrite(files.activation, jsonFile(activation), hooks);
        await atomicWrite(files.state, jsonFile(state), hooks);
        await atomicWrite(files.receipt, jsonFile(receipt), hooks);
        const verified = await verifyLatestReceipt(root, receipt.receipt_id);
        if (!verified.verified) throw new Error(verified.reason);
        return receipt;
      } catch (error) {
        await Promise.all(existing.map((value, index) => restore(
          [files.activation, files.state, files.receipt][index], value,
        )));
        throw error;
      }
    });
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

  return { readProjectSnapshot, verifyLatestReceipt, initializeProjectState, commitProjectState };
}

const defaultStore = createStateStore();
export const readProjectSnapshot = defaultStore.readProjectSnapshot;
export const verifyLatestReceipt = defaultStore.verifyLatestReceipt;
export const initializeProjectState = defaultStore.initializeProjectState;
export const commitProjectState = defaultStore.commitProjectState;
