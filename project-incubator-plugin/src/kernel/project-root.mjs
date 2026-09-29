import { readFile, realpath } from "node:fs/promises";
import path from "node:path";

import { parseActivation } from "./schemas.mjs";

const CONTROL_DIR = ".project-incubator";
const ACTIVATION_FILE = "activation.json";
const PROTECTED_FILES = new Set([ACTIVATION_FILE, "state.json", "latest-receipt.json"]);

function comparable(value) {
  const normalized = path.normalize(value);
  return process.platform === "win32" ? normalized.toLowerCase() : normalized;
}

async function canonicalizePossiblyMissing(candidatePath) {
  const suffix = [];
  let cursor = path.resolve(candidatePath);
  while (true) {
    try {
      const existing = await realpath(cursor);
      return path.join(existing, ...suffix.reverse());
    } catch (error) {
      if (error?.code !== "ENOENT") throw error;
      const parent = path.dirname(cursor);
      if (parent === cursor) return path.resolve(candidatePath);
      suffix.push(path.basename(cursor));
      cursor = parent;
    }
  }
}

async function readActivation(root) {
  try {
    const raw = await readFile(path.join(root, CONTROL_DIR, ACTIVATION_FILE), "utf8");
    const activation = parseActivation(JSON.parse(raw));
    return activation.status === "ACTIVE" ? activation : null;
  } catch (error) {
    if (error?.code === "ENOENT" || error instanceof SyntaxError || error?.name === "ZodError") return null;
    throw error;
  }
}

export async function findActivatedProjectRoot(cwd) {
  let cursor = await canonicalizePossiblyMissing(cwd);
  while (true) {
    if (await readActivation(cursor)) return cursor;
    const parent = path.dirname(cursor);
    if (parent === cursor) return null;
    cursor = parent;
  }
}

export async function isProtectedProjectPath(projectRoot, candidatePath) {
  const canonicalRoot = await canonicalizePossiblyMissing(projectRoot);
  const canonicalCandidate = await canonicalizePossiblyMissing(candidatePath);
  return comparable(path.dirname(canonicalCandidate)) === comparable(path.join(canonicalRoot, CONTROL_DIR))
    && PROTECTED_FILES.has(path.basename(canonicalCandidate).toLowerCase());
}

export const protectedProjectFiles = Object.freeze([...PROTECTED_FILES]);
