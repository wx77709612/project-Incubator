import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const desktopProfileUrl = new URL("../../profiles/project-types/desktop-product.json", import.meta.url);
const windowsProfileUrl = new URL("../../profiles/hosts/windows-desktop.json", import.meta.url);

async function readJson(url) {
  return JSON.parse(await readFile(url, "utf8"));
}

test("desktop product profile declares exactly P0-P6 without a subflow", async () => {
  const profile = await readJson(desktopProfileUrl);
  assert.equal(profile.project_type_id, "desktop-product");
  assert.equal(profile.child_skill_id, "desktop-product-incubator");
  assert.deepEqual(profile.stages, ["P0", "P1", "P2", "P3", "P4", "P5", "P6"]);
  assert.deepEqual(profile.subflows, []);
});

test("windows desktop profile binds the required environment context and shared constraints", async () => {
  const profile = await readJson(windowsProfileUrl);
  assert.equal(profile.host_profile_id, "windows-desktop");
  assert.equal(profile.project_type_id, "desktop-product");
  assert.equal(profile.skill_id, "windows-desktop-host-profile");
  assert.deepEqual(profile.required_context, [
    "windows_version", "architecture", "install_scope", "privilege_mode", "distribution_format",
  ]);
  assert.deepEqual(profile.kernel_constraints, {
    maker_authorization: "REQUIRED", state_mutation: "MCP_ONLY", receipt: "REQUIRED",
  });
});

test("desktop and windows profiles do not claim browser or domain ownership", async () => {
  const profiles = JSON.stringify([await readJson(desktopProfileUrl), await readJson(windowsProfileUrl)]);
  for (const forbidden of ["browser_extension", "mod_website", "game_installation_environment", "domain_profile"]) {
    assert.equal(profiles.includes(forbidden), false);
  }
});
