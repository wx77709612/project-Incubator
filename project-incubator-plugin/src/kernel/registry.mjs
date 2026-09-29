import { readFile } from "node:fs/promises";
import path from "node:path";
import { z } from "zod";

const id = z.string().min(1).max(128).regex(/^[A-Za-z0-9][A-Za-z0-9._:-]*$/);
const relativePath = z.string().min(1).max(500).refine((value) => !path.isAbsolute(value), "路径必须为相对路径");
const constraints = z.object({
  maker_authorization: z.string().optional(),
  state_mutation: z.string().optional(),
  receipt: z.string().optional(),
}).strict();

const registrySchema = z.object({
  schema_version: z.literal("1.0"),
  kernel_constraints: z.object({
    maker_authorization: z.literal("REQUIRED"),
    state_mutation: z.literal("MCP_ONLY"),
    receipt: z.literal("REQUIRED"),
  }).strict(),
  child_skills: z.array(z.object({ id, skill_path: relativePath }).strict()).max(100),
  project_types: z.array(z.object({ id, child_skill_id: id }).strict()).max(100),
  host_profiles: z.array(z.object({
    id, project_type_id: id, profile_path: relativePath,
    kernel_constraints: constraints.default({}),
  }).strict()).max(200),
}).strict();

function assertUnique(values, code) {
  if (new Set(values).size !== values.length) throw new Error(code);
}

export function validateRegistry(value) {
  const parsed = registrySchema.parse(value);
  assertUnique(parsed.child_skills.map((item) => item.id), "DUPLICATE_CHILD_SKILL_ID");
  assertUnique(parsed.project_types.map((item) => item.id), "DUPLICATE_PROJECT_TYPE_ID");
  assertUnique(parsed.host_profiles.map((item) => item.id), "DUPLICATE_HOST_PROFILE_ID");
  const childIds = new Set(parsed.child_skills.map((item) => item.id));
  const typeIds = new Set(parsed.project_types.map((item) => item.id));
  for (const type of parsed.project_types) {
    if (!childIds.has(type.child_skill_id)) throw new Error("UNKNOWN_CHILD_SKILL");
  }
  for (const profile of parsed.host_profiles) {
    if (!typeIds.has(profile.project_type_id)) throw new Error("UNKNOWN_PROFILE_PROJECT_TYPE");
    for (const [key, value] of Object.entries(profile.kernel_constraints)) {
      if (value !== parsed.kernel_constraints[key]) throw new Error("HOST_PROFILE_WEAKENS_KERNEL");
    }
  }
  return parsed;
}

export async function loadRegistry(pluginRoot) {
  let value;
  try {
    value = JSON.parse(await readFile(path.join(pluginRoot, "profiles", "registry.json"), "utf8"));
  } catch (error) {
    if (error instanceof SyntaxError) throw new Error("REGISTRY_INVALID_JSON", { cause: error });
    throw error;
  }
  return validateRegistry(value);
}

export function resolveRoute(registry, projectTypeId, hostProfileId = null) {
  const projectType = registry.project_types.find((item) => item.id === projectTypeId);
  if (!projectType) throw new Error("PROJECT_TYPE_NOT_FOUND");
  let hostProfile = null;
  if (hostProfileId) {
    hostProfile = registry.host_profiles.find((item) => item.id === hostProfileId);
    if (!hostProfile) throw new Error("HOST_PROFILE_NOT_FOUND");
    if (hostProfile.project_type_id !== projectTypeId) {
      throw new Error("HOST_PROFILE_PROJECT_TYPE_MISMATCH");
    }
  }
  return Object.freeze({
    project_type_id: projectType.id,
    child_skill_id: projectType.child_skill_id,
    host_profile_id: hostProfile?.id ?? null,
  });
}
