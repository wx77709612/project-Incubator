import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const pluginRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const destination = path.resolve(process.argv[2] ?? path.join(pluginRoot, "dist", "project-incubator-plugin"));
const entries = [
  ".codex-plugin", ".mcp.json", "hooks", "profiles", "scripts", "skills", "src",
  "package.json", "package-lock.json",
];
await rm(destination, { recursive: true, force: true });
await mkdir(destination, { recursive: true });
for (const entry of entries) await cp(path.join(pluginRoot, entry), path.join(destination, entry), { recursive: true });
const manifest = JSON.parse(await readFile(path.join(destination, ".codex-plugin", "plugin.json"), "utf8"));
await writeFile(path.join(destination, "CANDIDATE.json"), `${JSON.stringify({
  plugin: manifest.name, version: manifest.version, created_at: new Date().toISOString(),
  install: "Run npm ci --omit=dev in this directory before activation.",
}, null, 2)}\n`, "utf8");
process.stdout.write(`${destination}\n`);
