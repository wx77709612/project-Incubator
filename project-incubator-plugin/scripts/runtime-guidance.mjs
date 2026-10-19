import { readFile, readdir } from "node:fs/promises";
import path from "node:path";

export function obsoleteInstructions(text) {
  return text.split(/\r?\n|[。；;，,]/u).filter((line) => !/^\s*(?:[-*>]\s*)?(?:Legacy\b|历史(?:说明|参考)[:：])/iu.test(line))
    .filter((line) => !/不得|禁止|不再|不是|不参与|不属于|非现行/u.test(line))
    .filter((line) => /PROJECT_STATE\.md.*(?:唯一|权威|Source of Truth)|(?:通过|调用|运行|执行|支持由).*BOOTSTRAP_HOST_INTEGRATION|(?:Runtime 支持|通过|调用|执行).*runtime[\\/]|先形成.*Mutation Set|(?:开始前|恢复|查询).*调用.*get_project_state|(?:先读取|必须读取|必须维护|必须创建).*PROJECT_(?:PROFILE|STATE|PLAN|DECISIONS)\.md/u.test(line));
}

async function markdown(root) {
  const files = [];
  for (const entry of await readdir(root, { withFileTypes: true })) {
    const target = path.join(root, entry.name);
    if (entry.isDirectory()) files.push(...await markdown(target));
    else if (entry.name.endsWith(".md")) files.push(target);
  }
  return files;
}

export async function validateRuntimeGuidance(root) {
  const violations = [];
  const required = ["project-incubator-router", "mod-incubator", "desktop-product-incubator", "web-product-incubator", "sims-4-host-profile", "windows-desktop-host-profile"];
  const files = await markdown(path.join(root, "skills"));
  const entryFiles = files.filter((name) => path.basename(name) === "SKILL.md");
  if (entryFiles.length !== required.length) violations.push("SKILL_ENTRY_SET");
  for (const name of files) {
    const source = await readFile(name, "utf8");
    const relative = path.relative(root, name);
    if (obsoleteInstructions(source).length) violations.push(`${relative}:OBSOLETE_INSTRUCTION`);
    if (/\bSPECS[\\/]/iu.test(source)) violations.push(`${relative}:EXTERNAL_SPEC_DEPENDENCY`);
  }
  for (const id of required) {
    const relative = `skills/${id}/SKILL.md`;
    let source;
    try { source = await readFile(path.join(root, relative), "utf8"); }
    catch (error) { if (error.code !== "ENOENT") throw error; violations.push(`${relative}:MISSING`); continue; }
    if (!source.startsWith(`---\nname: ${id}\n`) && !source.startsWith(`---\r\nname: ${id}\r\n`)) violations.push(`${relative}:IDENTITY`);
    for (const term of ["project-incubator-router", "inspect_project", "activation.json", "state.json", "latest-receipt.json"]) {
      if (!source.includes(term)) violations.push(`${relative}:MISSING_${term}`);
    }
  }
  if (violations.length) {
    const error = new Error("CANDIDATE_GUIDANCE_DRIFT");
    error.violations = violations;
    throw error;
  }
  return { files_checked: files.length };
}
