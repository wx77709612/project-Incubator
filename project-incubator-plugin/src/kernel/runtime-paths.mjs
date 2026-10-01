import path from "node:path";

function legacyPluginDataRoot(pluginRoot) {
  if (typeof pluginRoot !== "string" || pluginRoot.trim().length === 0) return null;
  const versionRoot = path.resolve(pluginRoot);
  const pluginRootParent = path.dirname(versionRoot);
  const marketplaceRoot = path.dirname(pluginRootParent);
  const cacheRoot = path.dirname(marketplaceRoot);
  const pluginsRoot = path.dirname(cacheRoot);
  if (path.basename(cacheRoot).toLowerCase() !== "cache"
    || path.basename(pluginsRoot).toLowerCase() !== "plugins") return null;
  const pluginName = path.basename(pluginRootParent);
  const marketplaceName = path.basename(marketplaceRoot);
  if (!pluginName || !marketplaceName) return null;
  return path.join(pluginsRoot, "data", `${pluginName}-${marketplaceName}`);
}

export function resolveRuntimeDataRoot(env = process.env, pluginRoot = null) {
  const pluginData = env.PLUGIN_DATA?.trim() || env.CLAUDE_PLUGIN_DATA?.trim();
  if (pluginData) return path.resolve(pluginData, "runtime-events");
  const derivedPluginData = legacyPluginDataRoot(pluginRoot);
  if (derivedPluginData) return path.join(derivedPluginData, "runtime-events");
  const codexHome = env.CODEX_HOME?.trim();
  if (codexHome) return path.resolve(codexHome, "project-incubator-plugin", "runtime-events");
  throw new Error("RUNTIME_DATA_ROOT_REQUIRED");
}
