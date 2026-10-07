import assert from "node:assert/strict";
import path from "node:path";
import test from "node:test";

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
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
