import path from "node:path";

export function resolveRuntimeDataRoot(env = process.env) {
  const pluginData = env.PLUGIN_DATA?.trim() || env.CLAUDE_PLUGIN_DATA?.trim();
  if (pluginData) return path.resolve(pluginData, "runtime-events");
  const codexHome = env.CODEX_HOME?.trim();
  if (!codexHome) throw new Error("RUNTIME_DATA_ROOT_REQUIRED");
  return path.resolve(codexHome, "project-incubator-plugin", "runtime-events");
}
