# Codex 协作入口与权威恢复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

状态：APPROVED / IMPLEMENTATION AUTHORIZED；Maker 于 2026-10-23 批准在当前任务逐项实施。

**Goal:** 首次接入和任务首次进入时正确处理 `AGENTS.md`，并在三个权威 JSON 实际使用时发现损坏后提供 Maker 授权的受控恢复。

**Architecture:** Agent Entry 使用独立模板与安全文件模块；Router 只在当前任务首次进入项目时调用一次轻量检查。权威 JSON 沿用按需验证，新增 Runtime Data 两步恢复请求和 Kernel 三文件恢复事务，不改变正常初始化、Mutation、Gate 或阶段流程。

**Tech Stack:** Node.js ≥24、MCP SDK、Zod、`node:fs/promises`、`node:test`；不新增生产依赖。

**Spec:** [Design](../DESIGN/CODEX_PROJECT_AGENT_ENTRY_DESIGN.md)、[Contract](../CONTRACTS/CODEX_PROJECT_AGENT_ENTRY_CONTRACT.md)、[Runtime](../RUNTIME/CODEX_PROJECT_AGENT_ENTRY_RUNTIME_SPEC.md)。

## Global Constraints

- `AGENTS.md` 不是权威状态；已有文件不得自动覆盖或合并。
- 三个 JSON 只由 Kernel 写入；`inspect_project` 保持只读。
- Agent Entry 每个 Codex 任务／项目首次进入检查一次；三个 JSON 只在实际使用时验证。
- 恢复需要 request ID、scope digest 和 Maker 下一轮明确批准；旧 Pending Request 不继承。
- 不新增阶段、Gate、生产依赖，不修改 `_V*`、真实 Managed Project 或已安装插件缓存。

## Review Focus

1. 同一任务多次调用 Plugin 时 Router 不要求重复 Agent Entry 检查；切换项目根目录后应检查新项目（Task 2、4）。
2. 已有 `AGENTS.md` 与模板相同或不同都不能被覆盖；准备后新出现的文件必须保留（Task 1、2）。
3. 权威恢复准备后任一文件被新增、删除或改写时，提交必须零写入失败（Task 3、4）。
4. 可解析旧 State 使用下一 revision；缺失或不可解析 State 使用 revision 0，且两者新 Receipt 都可验证（Task 3、4）。
5. 正常完整项目继续直接执行 `inspect_project` 和 Mutation，不经过恢复诊断或额外四文件预检（Task 4、5）。

---

### Task 1: 包内 AGENTS 模板与安全文件操作

**Files:** Create `project-incubator-plugin/templates/codex/AGENTS.md`、`project-incubator-plugin/src/kernel/agent-entry.mjs`、`project-incubator-plugin/tests/unit/agent-entry.test.mjs`。

**Interfaces:** Produces `loadAgentEntryTemplate(pluginRoot): Promise<{bytes:Buffer,sha256:string}>`、`inspectAgentEntry(projectRoot,template): Promise<AgentEntryResult>`、`createAgentEntry(projectRoot,template): Promise<{result,rollbackToken}>`、`rollbackAgentEntry(projectRoot,rollbackToken): Promise<void>`。

- [ ] **Step 1: 写失败测试。** 覆盖模板内容边界、`MISSING`、`CURRENT`、`EXISTING_REVIEW_REQUIRED`、目录／链接／不可读对象、排他创建、回读不一致及只删除本次未变化文件的撤销。
- [ ] **Step 2: 运行红灯。** 执行 `node --test tests/unit/agent-entry.test.mjs`；预期因模块或接口不存在失败。
- [ ] **Step 3: 写最小实现。** 使用 `lstat`、`open("wx")`、`sync`、Buffer 回读和 SHA-256；模板只从当前 plugin root 加载。
- [ ] **Step 4: 运行绿灯并提交。** 同一命令全部通过；提交 Task 1 文件。

### Task 2: 首次接入与已接入项目的 AGENTS 补建

**Files:** Create `project-incubator-plugin/src/kernel/maintenance-requests.mjs`、`project-incubator-plugin/tests/unit/maintenance-requests.test.mjs`；Modify `project-incubator-plugin/src/kernel/state-store.mjs`、`project-incubator-plugin/src/server.mjs`、`project-incubator-plugin/skills/project-incubator-router/SKILL.md`；Test `project-incubator-plugin/tests/unit/state-store.test.mjs`、`project-incubator-plugin/tests/integration/router-mcp.test.mjs`、`project-incubator-plugin/tests/integration/inspect-project.test.mjs`。

**Interfaces:** Produces Runtime Data request helpers with 24-hour expiry; MCP `prepare_agent_entry(project_root,session_id)` and `install_agent_entry(project_root,request_id,scope_digest,session_id,turn_id)`；extends successful `initialize_project` with `agent_entry`。

- [ ] **Step 1: 写失败测试。** 证明 `NEW_PROJECT` 与 `ADOPT_EXISTING` 首次接入创建入口、已有文件不变；已接入项目缺失时先产生请求、未授权不能创建、批准后创建；Router 文案限定当前任务首次进入一次并要求中途创建后显式读取。
- [ ] **Step 2: 运行红灯。** 执行 `node --test tests/unit/state-store.test.mjs tests/unit/maintenance-requests.test.mjs tests/integration/router-mcp.test.mjs tests/integration/inspect-project.test.mjs`。
- [ ] **Step 3: 写最小实现。** 激活授权范围包含入口处理；初始化协调 Task 1 与现有三 JSON 闭合。补建请求绑定规范路径、session 和模板 SHA；提交前重新检查目标仍缺失。
- [ ] **Step 4: 运行绿灯并提交。** 重跑本 Task 测试，确认现有 `inspect_project` 只读测试仍通过后提交。

### Task 3: 权威逐文件诊断与恢复事务

**Files:** Create `project-incubator-plugin/src/kernel/authority-recovery.mjs`、`project-incubator-plugin/tests/unit/authority-recovery.test.mjs`；Modify `project-incubator-plugin/src/kernel/state-store.mjs`、`project-incubator-plugin/tests/unit/state-store.test.mjs`。

**Interfaces:** Produces `diagnoseAuthority(root): Promise<AuthorityDiagnostics>`、`normalizeRecoveryCandidate(diagnostics,activation,state,now): RecoveryCandidate`、`recoverProjectAuthority(root,candidate,expectedFingerprints,authorizationRef): Promise<RecoveryResult>`。

- [ ] **Step 1: 写失败测试。** 覆盖每个 JSON 缺失／非法、完整有效时拒绝恢复、有效旧 State 的下一 revision、无有效 State 的 revision 0、清空 Pending Request、新 Receipt 验证、来源指纹变化、逐文件写入故障和回滚残留。
- [ ] **Step 2: 运行红灯。** 执行 `node --test tests/unit/authority-recovery.test.mjs tests/unit/state-store.test.mjs`。
- [ ] **Step 3: 写最小实现。** 诊断独立读取固定三路径；恢复在项目队列内二次核对指纹、保存原始字节、规范化 `RECOVER_PROJECT_AUTHORITY` State、写入／回读／验证，失败恢复原字节。
- [ ] **Step 4: 运行绿灯并提交。** 重跑本 Task 测试并提交。

### Task 4: 两步恢复 MCP 与 Router 失败转向

**Files:** Modify `project-incubator-plugin/src/kernel/maintenance-requests.mjs`、`project-incubator-plugin/src/server.mjs`、`project-incubator-plugin/skills/project-incubator-router/SKILL.md`；Create `project-incubator-plugin/tests/integration/authority-recovery-mcp.test.mjs`；Modify `project-incubator-plugin/tests/contract/runtime-guidance-drift.test.mjs`、`project-incubator-plugin/tests/e2e/status-summary-flow.test.mjs`。

**Interfaces:** Produces MCP `prepare_authority_recovery(project_root,session_id,summary,proposed_activation,proposed_state)` and `recover_project_authority(project_root,request_id,scope_digest,session_id,turn_id)`；consumes Task 3 interfaces。

- [ ] **Step 1: 写失败测试。** 证明准备阶段零项目写入、有效项目返回 `AUTHORITY_RECOVERY_NOT_REQUIRED`、授权错误零写入、Maker 批准后两种基线均闭合、准备后来源变化失败、旧 Pending Request 不继承；正常状态查询不调用恢复诊断。
- [ ] **Step 2: 运行红灯。** 执行 `node --test tests/integration/authority-recovery-mcp.test.mjs tests/contract/runtime-guidance-drift.test.mjs tests/e2e/status-summary-flow.test.mjs`。
- [ ] **Step 3: 写最小实现。** Runtime 请求包含诊断指纹和完整候选；复用现有 Prompt 授权证据，成功后消费请求。Router 在权威读取失败时报告具体状态并提出恢复，不从聊天自动生成状态。
- [ ] **Step 4: 运行绿灯并提交。** 重跑本 Task 测试并提交。

### Task 5: 候选分发与完整验收

**Files:** Modify `project-incubator-plugin/scripts/package-candidate.mjs`、`project-incubator-plugin/scripts/verify-candidate.mjs`、`project-incubator-plugin/scripts/runtime-guidance.mjs`、`project-incubator-plugin/tests/integration/candidate-package.test.mjs`、`SPECS/IMPLEMENTATION/CODEX_PROJECT_AGENT_ENTRY_ACCEPTANCE_TEST_PLAN.md`。

**Interfaces:** Candidate includes `templates/codex/AGENTS.md` and all new Kernel modules；produces source commit、candidate version/hash、repository-external verification and temporary-project host evidence。

- [ ] **Step 1: 写失败测试。** 候选必须包含模板与新模块；缺失、链接、篡改、包外回退或旧指令均失败；聚合哈希覆盖模板。
- [ ] **Step 2: 运行红灯。** 执行 `node --test tests/integration/candidate-package.test.mjs tests/contract/runtime-guidance-drift.test.mjs`。
- [ ] **Step 3: 写最小打包改动并运行绿灯。** 扩展白名单和候选验证，不包含 Legacy Runtime。
- [ ] **Step 4: 全量验证。** 在 `project-incubator-plugin/` 运行 `npm test`，再执行现有 Legacy 回归；记录退出码和计数。
- [ ] **Step 5: 候选与宿主验收。** 从仓库外验证候选；通过受支持安装方式加载新候选，在临时项目验证首次接入、下一任务入口加载、已接入补建和权威恢复。缺少新任务宿主证据时标记 `BLOCKED`。
- [ ] **Step 6: 记录结果并提交。** 更新验收计划结果区；只有全部标准实际通过后才声明实现完成。
