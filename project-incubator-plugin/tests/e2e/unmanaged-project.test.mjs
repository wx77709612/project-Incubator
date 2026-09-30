import assert from "node:assert/strict";
import { access, mkdtemp, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { handleUserPromptSubmit } from "../../hooks/user-prompt-submit.mjs";
import { handlePreToolUse } from "../../hooks/pre-tool-use.mjs";
import { handleStop } from "../../hooks/stop.mjs";

test("an unmanaged project remains completely untouched end to end", async (t) => {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-e2e-unmanaged-"));
  const home = await mkdtemp(path.join(os.tmpdir(), "incubator-e2e-home-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  t.after(() => rm(home, { recursive: true, force: true }));
  const env = { CODEX_HOME: home };
  assert.deepEqual(await handleUserPromptSubmit({ cwd: root, session_id: "s", turn_id: "t", prompt: "hello" }, { env }), { continue: true });
  assert.deepEqual(await handlePreToolUse({ cwd: root, tool_name: "apply_patch", tool_input: {} }), {});
  assert.deepEqual(await handleStop({ cwd: root, session_id: "s", turn_id: "t" }, { env }), { continue: true });
  await assert.rejects(() => access(path.join(home, "project-incubator-plugin")), /ENOENT/);
});
