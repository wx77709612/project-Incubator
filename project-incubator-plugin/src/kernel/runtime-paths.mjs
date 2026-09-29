import path from "node:path";

export function resolveRuntimeDataRoot(env = process.env) {
  const codexHome = env.CODEX_HOME?.trim();
  if (!codexHome) throw new Error("CODEX_HOME_REQUIRED");
  return path.resolve(codexHome, "project-incubator-plugin", "runtime-events");
}
