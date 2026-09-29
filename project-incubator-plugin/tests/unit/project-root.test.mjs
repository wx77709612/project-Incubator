import assert from "node:assert/strict";
import { mkdtemp, mkdir, realpath, rm, symlink, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import {
  findActivatedProjectRoot,
  isProtectedProjectPath,
} from "../../src/kernel/project-root.mjs";

const activation = {
  schema_version: "1.0",
  project_id: "project-1",
  plugin_id: "project-incubator-plugin",
  plugin_version: "0.1.0",
  status: "ACTIVE",
  project_type_id: "mod",
  child_skill_id: "mod-incubator",
  host_profile_id: "sims-4",
};

async function makeProject(overrides = {}) {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-root-"));
  const control = path.join(root, ".project-incubator");
  await mkdir(control);
  await writeFile(
    path.join(control, "activation.json"),
    JSON.stringify({ ...activation, ...overrides }),
  );
  return root;
}

test("returns null for an unmanaged directory", async (t) => {
  const root = await mkdtemp(path.join(os.tmpdir(), "incubator-unmanaged-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  assert.equal(await findActivatedProjectRoot(root), null);
});

test("finds an activated project from a descendant", async (t) => {
  const root = await makeProject();
  const child = path.join(root, "src", "nested");
  await mkdir(child, { recursive: true });
  t.after(() => rm(root, { recursive: true, force: true }));
  assert.equal(await findActivatedProjectRoot(child), await realpath(root));
});

test("ignores malformed, inactive, and foreign activation records", async (t) => {
  const roots = await Promise.all([
    makeProject({ status: "INACTIVE" }),
    makeProject({ plugin_id: "other-plugin" }),
    makeProject(),
  ]);
  await writeFile(
    path.join(roots[2], ".project-incubator", "activation.json"),
    "{broken",
  );
  t.after(() => Promise.all(roots.map((root) => rm(root, { recursive: true, force: true }))));
  for (const root of roots) {
    assert.equal(await findActivatedProjectRoot(root), null);
  }
});

test("recognizes protected files through dot segments", async (t) => {
  const root = await makeProject();
  const state = path.join(root, "src", "..", ".project-incubator", "state.json");
  await mkdir(path.join(root, "src"));
  t.after(() => rm(root, { recursive: true, force: true }));
  assert.equal(await isProtectedProjectPath(root, state), true);
});

test("does not confuse a similarly named neighboring directory", async (t) => {
  const root = await makeProject();
  const neighbor = `${root}-copy`;
  await mkdir(path.join(neighbor, ".project-incubator"), { recursive: true });
  t.after(async () => {
    await rm(root, { recursive: true, force: true });
    await rm(neighbor, { recursive: true, force: true });
  });
  assert.equal(
    await isProtectedProjectPath(
      root,
      path.join(neighbor, ".project-incubator", "state.json"),
    ),
    false,
  );
});

test("recognizes a protected file reached through a directory link", async (t) => {
  const root = await makeProject();
  const linkParent = await mkdtemp(path.join(os.tmpdir(), "incubator-link-"));
  const link = path.join(linkParent, "project-link");
  await symlink(root, link, process.platform === "win32" ? "junction" : "dir");
  t.after(async () => {
    await rm(linkParent, { recursive: true, force: true });
    await rm(root, { recursive: true, force: true });
  });
  assert.equal(
    await isProtectedProjectPath(
      root,
      path.join(link, ".project-incubator", "latest-receipt.json"),
    ),
    true,
  );
});

test("normalizes case when the platform filesystem is case-insensitive", async (t) => {
  const root = await makeProject();
  t.after(() => rm(root, { recursive: true, force: true }));
  const alternate = root.toUpperCase();
  const expected = process.platform === "win32";
  assert.equal(
    await isProtectedProjectPath(
      root,
      path.join(alternate, ".project-incubator", "state.json"),
    ),
    expected,
  );
});
