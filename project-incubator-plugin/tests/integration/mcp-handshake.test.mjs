import assert from "node:assert/strict";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { getDefaultEnvironment, StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";

import { createMcpServer } from "../../src/server.mjs";

test("MCP handshake reports the installed package version", async (t) => {
  const pluginRoot = path.resolve(import.meta.dirname, "../..");
  const server = await createMcpServer({ pluginRoot });
  const client = new Client({ name: "project-incubator-test", version: "1.0.0" });
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  t.after(async () => {
    await client.close();
    await server.close();
  });

  await server.connect(serverTransport);
  await client.connect(clientTransport);

  assert.equal(client.getServerVersion()?.version, "0.2.0");
});

test("installed MCP manifest launches the real server and exposes kernel tools", async (t) => {
  const pluginRoot = path.resolve(import.meta.dirname, "../..");
  const pluginData = await mkdtemp(path.join(os.tmpdir(), "project-incubator-mcp-data-"));
  t.after(() => rm(pluginData, { recursive: true, force: true }));
  const manifest = JSON.parse(await readFile(path.join(pluginRoot, ".mcp.json"), "utf8"));
  const definition = manifest.mcpServers.project_incubator;
  const transport = new StdioClientTransport({
    command: definition.command,
    args: definition.args,
    cwd: path.resolve(pluginRoot, definition.cwd ?? "."),
    env: { ...getDefaultEnvironment(), PLUGIN_DATA: pluginData },
    stderr: "pipe",
  });
  let stderr = "";
  transport.stderr?.on("data", (chunk) => { stderr += chunk.toString(); });
  const client = new Client({ name: "project-incubator-installed-test", version: "1.0.0" });
  t.after(async () => client.close());

  try {
    await client.connect(transport);
  } catch (error) {
    assert.fail(`${error.message}\n${stderr}`);
  }
  const tools = await client.listTools();

  assert.ok(tools.tools.some(({ name }) => name === "propose_route"));
  assert.ok(tools.tools.some(({ name }) => name === "prepare_activation"));
});
