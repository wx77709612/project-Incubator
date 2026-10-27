# Codex 协作入口与权威恢复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

状态：IMPLEMENTED / ACCEPTANCE PASSED；Maker 于 2026-10-23 批准实施，真实宿主授权上下文修正于 2026-10-26 获批，全部验收于 2026-10-27 通过。

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

- [x] **Step 1: 写失败测试。** 覆盖模板内容边界、`MISSING`、`CURRENT`、`EXISTING_REVIEW_REQUIRED`、目录／链接／不可读对象、排他创建、回读不一致及只删除本次未变化文件的撤销。
- [x] **Step 2: 运行红灯。** 执行 `node --test tests/unit/agent-entry.test.mjs`；预期因模块或接口不存在失败。
- [x] **Step 3: 写最小实现。** 使用 `lstat`、`open("wx")`、`sync`、Buffer 回读和 SHA-256；模板只从当前 plugin root 加载。
- [x] **Step 4: 运行绿灯并提交。** 同一命令全部通过；提交 Task 1 文件。

### Task 2: 首次接入与已接入项目的 AGENTS 补建

**Files:** Create `project-incubator-plugin/src/kernel/maintenance-requests.mjs`、`project-incubator-plugin/tests/unit/maintenance-requests.test.mjs`；Modify `project-incubator-plugin/src/kernel/state-store.mjs`、`project-incubator-plugin/src/server.mjs`、`project-incubator-plugin/skills/project-incubator-router/SKILL.md`；Test `project-incubator-plugin/tests/unit/state-store.test.mjs`、`project-incubator-plugin/tests/integration/router-mcp.test.mjs`、`project-incubator-plugin/tests/integration/inspect-project.test.mjs`。

**Interfaces:** Produces Runtime Data request helpers with 24-hour expiry; MCP `prepare_agent_entry(project_root,session_id)` and `install_agent_entry(project_root,request_id,scope_digest,session_id)`（经 Task 6 修正，兼容但不要求 `turn_id`）；extends successful `initialize_project` with `agent_entry`。

- [x] **Step 1: 写失败测试。** 证明 `NEW_PROJECT` 与 `ADOPT_EXISTING` 首次接入创建入口、已有文件不变；已接入项目缺失时先产生请求、未授权不能创建、批准后创建；Router 文案限定当前任务首次进入一次并要求中途创建后显式读取。
- [x] **Step 2: 运行红灯。** 执行 `node --test tests/unit/state-store.test.mjs tests/unit/maintenance-requests.test.mjs tests/integration/router-mcp.test.mjs tests/integration/inspect-project.test.mjs`。
- [x] **Step 3: 写最小实现。** 激活授权范围包含入口处理；初始化协调 Task 1 与现有三 JSON 闭合。补建请求绑定规范路径、session 和模板 SHA；提交前重新检查目标仍缺失。
- [x] **Step 4: 运行绿灯并提交。** 重跑本 Task 测试，确认现有 `inspect_project` 只读测试仍通过后提交。

### Task 3: 权威逐文件诊断与恢复事务

**Files:** Create `project-incubator-plugin/src/kernel/authority-recovery.mjs`、`project-incubator-plugin/tests/unit/authority-recovery.test.mjs`；Modify `project-incubator-plugin/src/kernel/state-store.mjs`、`project-incubator-plugin/tests/unit/state-store.test.mjs`。

**Interfaces:** Produces `diagnoseAuthority(root): Promise<AuthorityDiagnostics>`、`normalizeRecoveryCandidate(diagnostics,activation,state,now): RecoveryCandidate`、`recoverProjectAuthority(root,candidate,expectedFingerprints,authorizationRef): Promise<RecoveryResult>`。

- [x] **Step 1: 写失败测试。** 覆盖每个 JSON 缺失／非法、完整有效时拒绝恢复、有效旧 State 的下一 revision、无有效 State 的 revision 0、清空 Pending Request、新 Receipt 验证、来源指纹变化、逐文件写入故障和回滚残留。
- [x] **Step 2: 运行红灯。** 执行 `node --test tests/unit/authority-recovery.test.mjs tests/unit/state-store.test.mjs`。
- [x] **Step 3: 写最小实现。** 诊断独立读取固定三路径；恢复在项目队列内二次核对指纹、保存原始字节、规范化 `RECOVER_PROJECT_AUTHORITY` State、写入／回读／验证，失败恢复原字节。
- [x] **Step 4: 运行绿灯并提交。** 重跑本 Task 测试并提交。

### Task 4: 两步恢复 MCP 与 Router 失败转向

**Files:** Modify `project-incubator-plugin/src/kernel/maintenance-requests.mjs`、`project-incubator-plugin/src/server.mjs`、`project-incubator-plugin/skills/project-incubator-router/SKILL.md`；Create `project-incubator-plugin/tests/integration/authority-recovery-mcp.test.mjs`；Modify `project-incubator-plugin/tests/contract/runtime-guidance-drift.test.mjs`、`project-incubator-plugin/tests/e2e/status-summary-flow.test.mjs`。

**Interfaces:** Produces MCP `prepare_authority_recovery(project_root,session_id,summary,proposed_activation,proposed_state)` and `recover_project_authority(project_root,request_id,scope_digest,session_id)`（经 Task 6 修正，兼容但不要求 `turn_id`）；consumes Task 3 interfaces。

- [x] **Step 1: 写失败测试。** 证明准备阶段零项目写入、有效项目返回 `AUTHORITY_RECOVERY_NOT_REQUIRED`、授权错误零写入、Maker 批准后两种基线均闭合、准备后来源变化失败、旧 Pending Request 不继承；正常状态查询不调用恢复诊断。
- [x] **Step 2: 运行红灯。** 执行 `node --test tests/integration/authority-recovery-mcp.test.mjs tests/contract/runtime-guidance-drift.test.mjs tests/e2e/status-summary-flow.test.mjs`。
- [x] **Step 3: 写最小实现。** Runtime 请求包含诊断指纹和完整候选；复用现有 Prompt 授权证据，成功后消费请求。Router 在权威读取失败时报告具体状态并提出恢复，不从聊天自动生成状态。
- [x] **Step 4: 运行绿灯并提交。** 重跑本 Task 测试并提交。

### Task 5: 候选分发与完整验收

**Status:** COMPLETED；自动化、Legacy、候选、安装与真实宿主验收均通过。

**Files:** Modify `project-incubator-plugin/scripts/package-candidate.mjs`、`project-incubator-plugin/scripts/verify-candidate.mjs`、`project-incubator-plugin/scripts/runtime-guidance.mjs`、`project-incubator-plugin/tests/integration/candidate-package.test.mjs`、`SPECS/IMPLEMENTATION/CODEX_PROJECT_AGENT_ENTRY_ACCEPTANCE_TEST_PLAN.md`。

**Interfaces:** Candidate includes `templates/codex/AGENTS.md` and all new Kernel modules；produces source commit、candidate version/hash、repository-external verification and temporary-project host evidence。

- [x] **Step 1: 写失败测试。** 候选必须包含模板与新模块；缺失、链接、篡改、包外回退或旧指令均失败；聚合哈希覆盖模板。
- [x] **Step 2: 运行红灯。** 执行 `node --test tests/integration/candidate-package.test.mjs tests/contract/runtime-guidance-drift.test.mjs`。
- [x] **Step 3: 写最小打包改动并运行绿灯。** 扩展白名单和候选验证，不包含 Legacy Runtime。
- [x] **Step 4: 全量验证。** 在 `project-incubator-plugin/` 运行 `npm test`，再执行现有 Legacy 回归；记录退出码和计数。
- [x] **Step 5: 候选与宿主验收。** 从仓库外验证候选；通过受支持安装方式加载新候选，在临时项目验证首次接入、下一任务入口加载、已接入补建和权威恢复。缺少新任务宿主证据时标记 `BLOCKED`。
- [x] **Step 6: 记录结果并提交。** 更新验收计划结果区；只有全部标准实际通过后才声明实现完成。

### Task 6: 真实宿主授权上下文修正

**Status:** COMPLETED / ACCEPTANCE PASSED；真实宿主于 2026-10-26 复现 `PROMPT_NOT_FOUND` 后，Maker 明确批准本修正；2026-10-27 完成真实宿主复验。

**Files:** Modify `project-incubator-plugin/src/kernel/prompt-events.mjs`、`project-incubator-plugin/src/server.mjs`、`project-incubator-plugin/skills/project-incubator-router/SKILL.md`、`project-incubator-plugin/scripts/verify-candidate.mjs`、对应 Prompt／Router／Recovery 集成测试，以及本计划引用的 Design、Contract、Runtime 与 Acceptance 结果。

**Interfaces:** Produces `findAuthorizedPromptRef(runtimeDataRoot,{project_root,project_id,session_id,request_id,scope_digest,intent})`；`install_agent_entry` 与 `recover_project_authority` 的 Agent 输入不再要求 `turn_id`，内部授权仍使用 Hook 记录的规范项目根与真实 turn。现有 Activation、Mutation、Gate、阶段和 P0–P6 接口不变。

- [x] **Step 1: 写失败测试。** Prompt 解析只选择同规范项目根、同项目 ID、同 session、精确 request/scope 和批准意图的最新 Hook 到达记录；跨根目录复用项目 ID、宿主时钟回拨、错误 session、错误 scope、拒绝或无 Prompt 均不得回退旧批准；Agent Entry 与 Authority Recovery 在省略 `turn_id` 时成功。
- [x] **Step 2: 运行红灯。** 执行 `node --test tests/unit/prompt-events.test.mjs tests/integration/router-mcp.test.mjs tests/integration/authority-recovery-mcp.test.mjs`，预期因新查找接口不存在或工具仍要求 `turn_id` 失败。
- [x] **Step 3: 写最小实现。** Hook 记录规范项目根，并在任何异步清理前登记带进程身份的写入意图，再为维护授权在带唯一所有者、持久冲突屏障与陈旧锁/意图恢复的同一上下文排他锁内以 `PENDING → READY` 发布最新 Prompt 指针；重叠记录不排队竞争，统一标记为顺序歧义并失败关闭。后续第一条无并发 Prompt 只确认冲突且仍失败，下一条独立明确 Prompt 才重建指针；确认写失败仍保留阻断，禁止在发现冲突的同一调用恢复授权。Kernel 不按墙钟扫描排序，不回退旧记录，取得指针记录内真实 `turn_id` 后复用 `authorizePreparedChange`，消费前被替代则失败关闭；Router 明确从 `CODEX_SESSION_ID` 取 session；候选 Full 改为不传新工具的 `turn_id`。
- [x] **Step 4: 运行绿灯与全量回归。** 先重跑本 Task 测试，再运行 Plugin 全量、Legacy 回归和仓库外 Candidate Structure/Full。
- [x] **Step 5: 正式安装与真实宿主复验。** 使用受支持插件安装器加载新候选；在新 Codex 任务完成原生 AGENTS 加载、单次入口检查、删除后准备、Maker 精确批准、补建和显式回读。不得读取 Runtime Data 伪造 turn。
- [x] **Step 6: 记录证据并提交。** 更新 Acceptance 状态、版本、哈希和宿主证据；只有所有步骤通过才关闭 Task 5/6。

## 最终结果

Tasks 1–6 已全部完成。Plugin `399/399`、Legacy `168/168`、候选 Structure/Full、安装后补建与新任务只读复验均通过；详细证据见 [验收计划](CODEX_PROJECT_AGENT_ENTRY_ACCEPTANCE_TEST_PLAN.md)。
