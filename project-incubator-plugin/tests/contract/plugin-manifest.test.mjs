import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";

const root = path.resolve(import.meta.dirname, "../..");
const read = (relative) => readFile(path.join(root, relative), "utf8");

test("manifest and package identify the 0.3.0 multi-type candidate", async () => {
  const manifest = JSON.parse(await read(".codex-plugin/plugin.json"));
  const packageJson = JSON.parse(await read("package.json"));
  const lock = JSON.parse(await read("package-lock.json"));
  assert.match(manifest.version, /^0\.3\.0\+codex\.\d{14}$/);
  assert.equal(packageJson.version, "0.3.0");
  assert.equal(lock.version, "0.3.0");
  assert.equal(lock.packages[""].version, "0.3.0");

  const capabilities = manifest.interface.capabilities.join(" ");
  const description = manifest.interface.longDescription;
  for (const productType of ["Mod", "Desktop", "Web"]) {
    assert.match(capabilities, new RegExp(productType, "i"));
    assert.match(description, new RegExp(productType, "i"));
  }
  assert.doesNotMatch(description, /部署|deploy(?:ment)?/i);
});
