# Project Incubator Plugin MVP 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 交付一个可全局安装、仅在 Managed Project 显式激活后执行强约束的 Project Incubator Plugin，并以 Mod Incubator 与 Sims 4 Host Profile 完成首个可扩展项目类型闭环。

**Architecture:** Router 只提议项目类型，Maker 确认后由 MCP Kernel 持久化。Kernel 独占 `.project-incubator` 三个权威文件的校验和写入，Hooks 阻止绕过并要求 Receipt 闭合；Child Skill 与 Host Profile 通过注册表提供领域流程，不改变 Kernel 权限边界。Maker 查询项目状态时，Skill 必须调用 `inspect_project`，由 Kernel 从已校验状态生成固定摘要。

**Tech Stack:** Node.js 24 ESM、`@modelcontextprotocol/sdk` `^1.18.2`、Zod `^3.25.76`、Node 内置 `node:test`、Codex Plugin Skills/MCP/Hooks；旧 RC.2 回归继续使用 Python 测试栈。

**Spec:** `project-incubator-plugin/ARCHITECTURE.md`

## Global Constraints

- 不修改现有 `PROJECT_INCUBATOR/`、`SPECS/`、V1.1 RC 或 `zzztemp/project-incubator-enforcement-spike/`。
- 新产品代码只进入 `project-incubator-plugin/`；Spike 只能作为宿主能力证据，不能复制其宽松状态解析。
- Managed Project 核心状态仅包含 `.project-incubator/activation.json`、`state.json`、`latest-receipt.json`。
- `state.json` 是唯一项目状态 Source of Truth；Markdown、聊天记录和 Runtime 临时数据均不得覆盖它。
- 未激活且没有路径严格匹配的有效 Pending Activation Bootstrap 时，所有 Hooks 必须无副作用放行；Bootstrap 只存在于 Plugin Runtime Data，不得创建项目状态。
- 状态、Schema、Receipt 或授权证据损坏时必须 fail closed，不得自动当作空状态恢复。
- Maker Authorization 只能来自当前项目、当前 Pending Request 对应的 Maker Prompt。
- Prompt 临时记录位于 Plugin Runtime Data，不属于 Managed Project；按 project/session/turn 隔离，授权消费或过期后删除。
- 人工测试预算没有 Maker 明确输入时必须为 `UNSET`。
- `PROJECT_OVERVIEW.md` 不默认生成；如 Maker 明确要求导出，它仍不参与 Gate 或状态判断。
- 新增或实质性改写的人读文本默认使用简体中文。
- 每项先写失败测试，再写最小实现；每个 Task 独立提交。

## Review Focus

- `state.json` 可解析但缺少恢复项目所需的逻辑分区时，Kernel 应拒绝，而不是返回不完整摘要。
- `latest-receipt.json` 的 ID 正确但状态哈希或 revision 不一致时，`inspect_project` 和 `Stop` 都应报告不可验证。
- 从子目录、软链接、`..`、大小写差异或相似目录名访问时，受保护路径判断不能被绕过。
- 旧 Prompt、其他项目 Prompt、Agent 文本或已消费 Prompt 不能授权当前 Pending Request。
- Pending Activation 必须绑定项目规范路径、request、scope、session 与当前授权 turn；消费或 24 小时过期后删除，且不得成为第四份项目权威状态。
- 新增项目类型或 Host Profile 只能通过注册表扩展，不能修改 Kernel 的状态、授权或 Receipt 规则。

---

### Task 1: Plugin Scaffold、激活边界与共享 Schema

**Files:**
- Create: `project-incubator-plugin/.codex-plugin/plugin.json`
- Create: `project-incubator-plugin/.mcp.json`
- Create: `project-incubator-plugin/package.json`
- Create: `project-incubator-plugin/package-lock.json`
- Create: `project-incubator-plugin/src/kernel/schemas.mjs`
- Create: `project-incubator-plugin/src/kernel/project-root.mjs`
- Create: `project-incubator-plugin/tests/unit/schemas.test.mjs`
- Create: `project-incubator-plugin/tests/unit/project-root.test.mjs`

**Interfaces:**
- Produces: `parseActivation(value: unknown): Activation`
- Produces: `parseProjectState(value: unknown): ProjectState`
- Produces: `parseReceipt(value: unknown): Receipt`
- Produces: `findActivatedProjectRoot(cwd: string): Promise<string | null>`
- Produces: `isProtectedProjectPath(projectRoot: string, candidatePath: string): Promise<boolean>`

- [ ] **Step 1: Scaffold Plugin and pin dependencies**

  使用 `plugin-creator` 在现有 `project-incubator-plugin/` 中补齐 Skills、Hooks、MCP 和 manifest 结构；安装并锁定计划头部声明的两个依赖。

- [ ] **Step 2: Write failing Schema tests**

  在 `schemas.test.mjs` 覆盖 `activation.json`、`state.json`、Receipt 的合法最小值，以及字符串 JSON、缺失逻辑分区、负数/小数/`null` revision、未知 schema version 和未知额外权威字段。

- [ ] **Step 3: Write failing project-root tests**

  在 `project-root.test.mjs` 覆盖未激活目录、从子目录发现根、错误 plugin ID、非 `ACTIVE`、软链接、`..`、大小写和相似目录名。

- [ ] **Step 4: Verify tests fail**

  Run: `node --test tests/unit/schemas.test.mjs tests/unit/project-root.test.mjs`

  Expected: FAIL because exported parsers and root helpers do not exist.

- [ ] **Step 5: Implement strict schemas and canonical root resolution**

  `ProjectState` 顶层固定为 `schema_version`、`project_id`、`revision`、`boundary`、`workflow`、`capabilities`、`decisions`、`assumptions`、`plan`、`gates`、`risks`、`pending_requests`、`baselines`、`human_validation`、`last_change`、`archive_refs`。所有集合设置有界数量并拒绝隐式类型转换。

- [ ] **Step 6: Verify tests and plugin shape pass**

  Run: `node --test tests/unit/schemas.test.mjs tests/unit/project-root.test.mjs`

  Run: `python C:/Users/Xenia_Woo/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py project-incubator-plugin`

  Expected: all tests PASS and plugin validation succeeds.

- [ ] **Step 7: Commit**

  Commit: `feat(plugin): establish activation boundary and state schema`

### Task 2: Fail-Closed State Transaction 与 Receipt

**Files:**
- Create: `project-incubator-plugin/src/kernel/canonical-json.mjs`
- Create: `project-incubator-plugin/src/kernel/state-store.mjs`
- Create: `project-incubator-plugin/src/kernel/receipt.mjs`
- Create: `project-incubator-plugin/tests/unit/state-store.test.mjs`
- Create: `project-incubator-plugin/tests/unit/receipt.test.mjs`

**Interfaces:**
- Consumes: Task 1 parsers and protected-root resolution.
- Produces: `readProjectSnapshot(root: string): Promise<ProjectSnapshot>`
- Produces: `initializeProjectState(root: string, activation: Activation, state: ProjectState, authorizationRef: AuthorizationRef): Promise<Receipt>`
- Produces: `commitProjectState(root: string, request: CommitRequest): Promise<Receipt>`
- Produces: `verifyLatestReceipt(root: string, expectedReceiptId?: string): Promise<ReceiptVerification>`

- [ ] **Step 1: Write failing state transaction tests**

  覆盖仅初始化可创建 revision `0`、普通提交严格递增、expected revision 冲突、损坏 JSON、原子替换失败、回读不一致、Receipt 写入失败和并发提交。

- [ ] **Step 2: Write failing Receipt tests**

  断言 Receipt 绑定 `project_id`、operation、previous/new revision、previous/new state hash、authorization ref 和 timestamp；只匹配 Receipt ID 不得通过。

- [ ] **Step 3: Verify tests fail**

  Run: `node --test tests/unit/state-store.test.mjs tests/unit/receipt.test.mjs`

  Expected: FAIL because transaction and Receipt APIs do not exist.

- [ ] **Step 4: Implement canonical hashing and transactional commit**

  使用同目录临时文件、flush、原子替换、回读和哈希校验；失败时恢复前一状态或明确返回未闭合，不得产生 `null`、`NaN` 或无法递增的 revision。

- [ ] **Step 5: Verify tests pass**

  Run: `node --test tests/unit/state-store.test.mjs tests/unit/receipt.test.mjs`

  Expected: PASS, including state-written/receipt-failed recovery.

- [ ] **Step 6: Commit**

  Commit: `feat(kernel): add fail-closed state transactions`

### Task 3: Maker Authorization Provenance

**Files:**
- Create: `project-incubator-plugin/src/kernel/authorization.mjs`
- Create: `project-incubator-plugin/src/kernel/prompt-events.mjs`
- Create: `project-incubator-plugin/src/kernel/runtime-paths.mjs`
- Create: `project-incubator-plugin/tests/unit/authorization.test.mjs`
- Create: `project-incubator-plugin/tests/unit/prompt-events.test.mjs`

**Interfaces:**
- Consumes: Task 1 schemas and Task 2 commit API.
- Produces: `prepareChange(snapshot: ProjectSnapshot, proposal: ChangeProposal): PreparedChange`
- Produces: `resolveRuntimeDataRoot(env: NodeJS.ProcessEnv): string`
- Produces: `recordMakerPrompt(event: PromptEvent, runtimeDataRoot: string): Promise<PromptRef>`
- Produces: `authorizePreparedChange(prepared: PreparedChange, promptRef: PromptRef): Promise<AuthorizationRef>`
- Produces: `consumePrompt(promptRef: PromptRef): Promise<void>`

- [ ] **Step 1: Write failing authorization tests**

  覆盖缺少 request ID、scope digest 不符、其他 project/session/turn、Agent 文本、模糊同意、过期、重复消费和不存在的 Pending Request；授权只在捕获 Prompt 的同一 turn 有效。另验证 Evidence 可以判定 Runtime Assumption 失效，但 Product / Architecture Decision 的新增、替代或撤销仍必须经过 Maker Authorization。

- [ ] **Step 2: Write failing Prompt lifecycle tests**

  断言未激活项目不写入 Runtime Data；激活项目只保存 session、turn、project、hash 和最小必要原文；Plugin 运行时优先解析到官方提供的 `$PLUGIN_DATA/runtime-events/`，并保留 `$CODEX_HOME/project-incubator-plugin/runtime-events/` 作为非 Plugin 运行与测试兼容回退；两者均不存在时 fail closed；消费后立即删除，超过 24 小时的孤立记录在下次访问时清理。Stop 首次闭合失败可继续本轮一次，但 `stop_hook_active=true` 时必须停止重复阻断并输出警告，避免不可终止循环。

- [ ] **Step 3: Verify tests fail**

  Run: `node --test tests/unit/authorization.test.mjs tests/unit/prompt-events.test.mjs`

  Expected: FAIL because authorization provenance APIs do not exist.

- [ ] **Step 4: Implement two-step authorization**

  Pending Request 写入 `state.json.pending_requests`；Prompt Event 写入 Plugin Runtime Data，并使用 project/session/turn 复合键。Receipt 保存 AuthorizationRef，不保存无来源的 `confirmed: true`；24 小时只用于清理，不延长“同一 turn”授权有效期。

- [ ] **Step 5: Verify tests pass**

  Run: `node --test tests/unit/authorization.test.mjs tests/unit/prompt-events.test.mjs`

  Expected: PASS and cross-project Prompt reuse is rejected.

- [ ] **Step 6: Commit**

  Commit: `feat(kernel): bind maker authorization to prompt provenance`

### Task 4: Shared Hooks 与项目隔离

**Files:**
- Create: `project-incubator-plugin/hooks/hooks.json`
- Create: `project-incubator-plugin/hooks/user-prompt-submit.mjs`
- Create: `project-incubator-plugin/hooks/pre-tool-use.mjs`
- Create: `project-incubator-plugin/hooks/stop.mjs`
- Create: `project-incubator-plugin/tests/integration/hooks.test.mjs`

**Interfaces:**
- Consumes: Tasks 1-3 root、protected path、Prompt 与 Receipt APIs.
- Produces: Codex `UserPromptSubmit`、`PreToolUse`、`Stop` Hook handlers.

- [ ] **Step 1: Write failing Hook isolation tests**

  断言未激活项目三个 Hook 全部放行且不创建 Prompt Event；激活项目中 Shell、`apply_patch` 和本地编辑工具直接写三个权威文件时被拒绝。

- [ ] **Step 2: Write failing Stop tests**

  覆盖状态变更后 final 缺 Receipt ID、Receipt 过期、哈希不符、revision 不符，以及只读任务不需要新 Receipt。

- [ ] **Step 3: Verify tests fail**

  Run: `node --test tests/integration/hooks.test.mjs`

  Expected: FAIL because Hook handlers do not exist.

- [ ] **Step 4: Implement synchronous, project-scoped Hooks**

  Hooks 只在 Task 1 识别到有效激活根后工作；Kernel MCP 自身受控写入不得被误拒绝，其他路径不得通过别名绕过。

- [ ] **Step 5: Verify tests pass**

  Run: `node --test tests/integration/hooks.test.mjs`

  Expected: PASS for activated and unmanaged project cases.

- [ ] **Step 6: Commit**

  Commit: `feat(plugin): enforce activated project boundaries`

### Task 5: MCP Kernel、Router 与扩展注册表

**Files:**
- Create: `project-incubator-plugin/src/server.mjs`
- Create: `project-incubator-plugin/src/kernel/registry.mjs`
- Create: `project-incubator-plugin/src/kernel/router.mjs`
- Create: `project-incubator-plugin/profiles/registry.json`
- Create: `project-incubator-plugin/skills/project-incubator-router/SKILL.md`
- Create: `project-incubator-plugin/tests/integration/router-mcp.test.mjs`
- Create: `project-incubator-plugin/tests/unit/registry.test.mjs`

**Interfaces:**
- Consumes: Tasks 1-3 schemas, state transaction and authorization APIs.
- Produces: `loadRegistry(pluginRoot: string): Promise<Registry>`
- Produces: `resolveRoute(registry: Registry, projectTypeId: string, hostProfileId?: string): RouteResolution`
- Produces MCP tools: `propose_route`、`prepare_activation`、`prepare_change`、`initialize_project`、`get_project_state`、`commit_change`、`verify_receipt`.

- [ ] **Step 1: Write failing registry tests**

  覆盖未知 Child Skill、Host Profile 不属于项目类型、重复 ID、Profile 尝试放宽 Kernel 权限，以及新增合法类型无需修改 Kernel 源码。

- [ ] **Step 2: Write failing Router/MCP tests**

  断言 `propose_route` 不修改状态；`prepare_activation` 只创建有界 Runtime 候选请求；普通未激活项目仍零副作用；未经 Maker 授权不能初始化或迁移项目类型；MCP 错误使用稳定错误码而不是成功文本。

- [ ] **Step 3: Verify tests fail**

  Run: `node --test tests/unit/registry.test.mjs tests/integration/router-mcp.test.mjs`

  Expected: FAIL because registry, Router and MCP tools do not exist.

- [ ] **Step 4: Implement registry-driven routing and MCP server**

  Router Skill 只负责识别候选类型、说明依据和请求 Maker 确认。首次激活通过短期 Pending Activation Bootstrap 捕获下一轮 Maker Prompt；Kernel 只有校验 request、scope、项目路径、session、turn 和批准语义后才创建三个权威文件。Bootstrap 消费或 24 小时过期后删除。

- [ ] **Step 5: Verify tests and plugin manifest pass**

  Run: `node --test tests/unit/registry.test.mjs tests/integration/router-mcp.test.mjs`

  Run: `python C:/Users/Xenia_Woo/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py project-incubator-plugin`

  Expected: PASS and Plugin manifest validates.

- [ ] **Step 6: Commit**

  Commit: `feat(router): add maker-confirmed extensible routing`

### Task 6: `inspect_project` 与人读摘要

**Files:**
- Create: `project-incubator-plugin/src/kernel/project-summary.mjs`
- Create: `project-incubator-plugin/skills/project-incubator-router/references/status-summary.md`
- Create: `project-incubator-plugin/tests/unit/project-summary.test.mjs`
- Create: `project-incubator-plugin/tests/integration/inspect-project.test.mjs`
- Modify: `project-incubator-plugin/src/server.mjs`
- Modify: `project-incubator-plugin/skills/project-incubator-router/SKILL.md`

**Interfaces:**
- Consumes: Task 2 `readProjectSnapshot` and `verifyLatestReceipt`; Task 3 Prompt provenance for explicit overview export.
- Produces: `buildProjectSummary(snapshot: ProjectSnapshot, receipt: ReceiptVerification): ProjectSummary`
- Produces: `renderProjectSummary(summary: ProjectSummary): string`
- Produces: `writeProjectOverview(root: string, summary: ProjectSummary, promptRef: PromptRef): Promise<ProjectionResult>`
- Produces MCP tools: `inspect_project`、`export_project_overview`.

- [ ] **Step 1: Write failing summary contract tests**

  断言结果固定包含目标与边界、routing、阶段、最近完成事项及证据上限、当前与下一步行动、完成条件、阻塞、风险、待 Maker 决策、Capability Evidence、Baseline、人工预算、last change、revision 和 Receipt 状态。

- [ ] **Step 2: Write failing integrity and read-only tests**

  覆盖损坏状态、不支持版本、Receipt 不一致、缺失 Baseline、预算 `UNSET`；断言调用前后三个文件字节和 revision 完全不变。`inspect_project` 不得创建 `PROJECT_OVERVIEW.md`；只有同一 turn 的 Maker Prompt 明确要求导出时，`export_project_overview` 才能写入该 Projection，且仍不改变三个核心文件。

- [ ] **Step 3: Write failing Skill trigger checks**

  断言 Skill 对“项目状态”“进度”“下一步”“阻塞”“需要我决定什么”及等价语义明确要求调用 `inspect_project`，并禁止从聊天记忆补全。

- [ ] **Step 4: Verify tests fail**

  Run: `node --test tests/unit/project-summary.test.mjs tests/integration/inspect-project.test.mjs`

  Expected: FAIL because summary builder and MCP tool do not exist.

- [ ] **Step 5: Implement deterministic summary and Skill trigger contract**

  `renderProjectSummary` 使用简体中文固定顺序；`inspect_project` 返回 structured content 与同源 Markdown 文本但不写文件。`export_project_overview` 校验同轮 PromptRef 后写入同源 Markdown，并在文件头声明其非权威、可重建性质。

- [ ] **Step 6: Verify tests pass**

  Run: `node --test tests/unit/project-summary.test.mjs tests/integration/inspect-project.test.mjs`

  Expected: PASS and malformed authority is reported as unverifiable.

- [ ] **Step 7: Commit**

  Commit: `feat(kernel): add verified project status summaries`

### Task 7: Mod Incubator 领域流程

**Files:**
- Create: `project-incubator-plugin/profiles/project-types/mod.json`
- Create: `project-incubator-plugin/skills/mod-incubator/SKILL.md`
- Create: `project-incubator-plugin/src/domains/mod/workflow.mjs`
- Create: `project-incubator-plugin/src/domains/mod/opacity.mjs`
- Create: `project-incubator-plugin/tests/unit/mod-workflow.test.mjs`
- Create: `project-incubator-plugin/tests/unit/mod-opacity.test.mjs`
- Modify: `project-incubator-plugin/profiles/registry.json`

**Interfaces:**
- Consumes: Task 5 Registry contract and Task 1 shared state fields.
- Produces: `evaluateModTransition(state: ProjectState, request: TransitionRequest): TransitionEvaluation`
- Produces: `assessCapabilityOpacity(input: OpacityInput): OpacityAssessment`
- Produces: registered Child Skill `mod-incubator` with stages `M0_BOUNDARY` through `M5_EXPAND_RELEASE` and `MODEL_REVIEW`.

- [ ] **Step 1: Write failing workflow tests**

  覆盖合法顺序、非法跳转、Maker-owned boundary、M2/M3/M4 进入并恢复 `MODEL_REVIEW`，以及不得把 Model Review 表述为 M5 Iteration。

- [ ] **Step 2: Write failing Evidence and opacity tests**

  覆盖八维 `0/1/2`、未知按 `1` 显示、任一 `2` 或至少两个 `1` 时建议 Vertical Slice、Evidence `E0-E5` 的顺序和结论上限、API Availability 不提升 Semantic Capability、预算不得由 Agent 猜测。

- [ ] **Step 3: Verify tests fail**

  Run: `node --test tests/unit/mod-workflow.test.mjs tests/unit/mod-opacity.test.mjs`

  Expected: FAIL because Mod domain evaluators do not exist.

- [ ] **Step 4: Implement Mod workflow and Skill**

  Child Skill 只声明领域阶段、风险、产物、Gate 和下一步；所有持久化继续通过 Kernel MCP。

- [ ] **Step 5: Verify tests pass**

  Run: `node --test tests/unit/mod-workflow.test.mjs tests/unit/mod-opacity.test.mjs`

  Expected: PASS for workflow, Evidence and budget boundaries.

- [ ] **Step 6: Commit**

  Commit: `feat(mod): add evidence-driven mod incubation`

### Task 8: Sims 4 Host Profile

**Files:**
- Create: `project-incubator-plugin/profiles/hosts/sims-4.json`
- Create: `project-incubator-plugin/skills/sims-4-host-profile/SKILL.md`
- Create: `project-incubator-plugin/src/domains/mod/sims4-profile.mjs`
- Create: `project-incubator-plugin/tests/unit/sims4-profile.test.mjs`
- Modify: `project-incubator-plugin/profiles/registry.json`

**Interfaces:**
- Consumes: Task 7 Mod Child contract.
- Produces: `applySims4Profile(modPolicy: ModPolicy, capability: CapabilityState): HostPolicy`
- Produces: registered Host Profile `sims-4`.

- [ ] **Step 1: Write failing Host Profile tests**

  覆盖游戏/补丁版本、Script/Package 类型、构建包内容、Mods 安装结构、加载日志、异常和 UI/交互观察入口；不相关 Capability 不得被强制要求 UI、存档或跨版本测试。

- [ ] **Step 2: Write failing authority narrowing tests**

  断言 Sims 4 Profile 只能增加或具体化验证要求，不能放宽 Maker Authorization、Kernel Gate、Evidence 等级或 Receipt 规则。

- [ ] **Step 3: Verify tests fail**

  Run: `node --test tests/unit/sims4-profile.test.mjs`

  Expected: FAIL because Sims 4 Profile does not exist.

- [ ] **Step 4: Implement profile and structured Maker observation format**

  Profile 按 Capability Claim 生成适用检查，不建立全项目固定清单；真实游戏观察保持 Maker 输入，Agent 负责结构化和判断证据边界。

- [ ] **Step 5: Verify tests pass**

  Run: `node --test tests/unit/sims4-profile.test.mjs`

  Expected: PASS and profile cannot broaden Kernel authority.

- [ ] **Step 6: Commit**

  Commit: `feat(sims4): add host-specific mod verification profile`

### Task 9: Legacy Invariant、端到端验收与候选打包

**Files:**
- Create: `project-incubator-plugin/tests/contract/legacy-invariants.test.mjs`
- Create: `project-incubator-plugin/tests/e2e/enforcement-flow.test.mjs`
- Create: `project-incubator-plugin/tests/e2e/unmanaged-project.test.mjs`
- Create: `project-incubator-plugin/tests/e2e/status-summary-flow.test.mjs`
- Create: `project-incubator-plugin/scripts/package-candidate.mjs`

**Interfaces:**
- Consumes: Tasks 1-8 complete Plugin.
- Produces: independently installable candidate package and machine-verifiable test results.

- [ ] **Step 1: Write Legacy integration contract tests**

  将 Architecture 第 13 节每个 `PRESERVE`、`ADAPT`、`SPECIALIZE` 项映射到至少一个测试 ID；若矩阵新增无测试项，contract test 失败。

- [ ] **Step 2: Write end-to-end flows**

  自动重放：未激活项目无副作用；Maker 授权路由和初始化；直接写入被拒绝；MCP 提交和 Receipt 闭合；状态查询生成固定摘要；新增虚拟 Child Type 无需修改 Kernel。

- [ ] **Step 3: Verify new tests fail before final wiring**

  Run: `node --test tests/contract/*.test.mjs tests/e2e/*.test.mjs`

  Expected: FAIL until all Plugin wiring and packaging entrypoints are complete.

- [ ] **Step 4: Complete server wiring and candidate packaging**

  候选包不得包含绝对研发路径、Spike、旧 RC 或开发缓存；`.mcp.json` 与启动脚本必须使用 Plugin 打包和安装流程支持的可迁移入口，并由仓库外安装测试证明，不能假设未经文档或测试确认的环境变量展开。

- [ ] **Step 5: Run complete new Plugin test suite**

  Run: `node --test tests/unit/*.test.mjs tests/integration/*.test.mjs tests/contract/*.test.mjs tests/e2e/*.test.mjs`

  Expected: all tests PASS.

- [ ] **Step 6: Run legacy regression**

  Run: `python -m unittest discover -s TESTS/unit -p "test_*.py"`

  Run: `python -m unittest discover -s TESTS/integration -p "test_*.py"`

  Run: `python -m unittest discover -s TESTS/e2e -p "test_*.py"`

  Expected: all existing RC.2 tests PASS without modifying legacy files.

- [ ] **Step 7: Validate and install candidate outside repository**

  使用 `plugin-creator` 校验工具、候选打包脚本和本地独立安装流程；从干净目录验证 MCP 启动、Router、Hooks、Mod Skill、Sims 4 Profile 与 `inspect_project`。

- [ ] **Step 8: Perform one bounded Codex host walkthrough**

  仅覆盖未激活项目、激活 Mod 项目、受保护写入、授权提交、状态摘要和 Receipt Stop Gate。结果在最终验收报告中简明呈现，不生成逐轮对话档案。

- [ ] **Step 9: Commit**

  Commit: `test(plugin): verify extensible enforced incubation flow`

### Correction Task: Mod Workflow Runtime Wiring

**Files:**
- Modify: `project-incubator-plugin/src/server.mjs`
- Modify: `project-incubator-plugin/src/domains/mod/workflow.mjs`
- Modify: `project-incubator-plugin/tests/integration/router-mcp.test.mjs`
- Modify: `project-incubator-plugin/tests/e2e/enforcement-flow.test.mjs`

**Contract:**
- `prepare_change` 在 `workflow.stage` 变化时要求并校验 `workflow_transition`；
- Kernel 根据激活的 `project_type_id` 调用领域 Workflow，不由 Agent 自行宣称转换合法；
- 缺少转换描述、目标不一致、非法跳级和无效 `MODEL_REVIEW` 在创建 Pending Request 前失败；
- `scope_digest` 与 Pending Payload 必须绑定转换描述；
- `commit_change` 在授权后针对最新状态再次校验，防止准备与提交之间绕过规则；
- 不改变阶段的普通 Mutation 保持现有兼容行为。

- [x] **Step 1: 写入 Runtime 集成失败测试，证明当前 `M0 -> M4` 可穿透**
- [x] **Step 2: 验证测试因缺少 Workflow Runtime Wiring 而失败**
- [x] **Step 3: 实现最小 Workflow Transition Contract 与双重校验**
- [x] **Step 4: 验证合法 `M0 -> M1`、非法跳级、描述缺失和 `MODEL_REVIEW` 路径**
- [x] **Step 5: 运行完整 Plugin、结构与安装缓存验证**
- [x] **Step 6: 安装新候选版本并执行 Round 9 非法跳级宿主走查**

### Correction Task: Pending Request Recovery 与 Decision Authorization Binding

**Files:**
- Modify: `project-incubator-plugin/src/kernel/authorization.mjs`
- Modify: `project-incubator-plugin/src/server.mjs`
- Modify: `project-incubator-plugin/tests/unit/authorization.test.mjs`
- Modify: `project-incubator-plugin/tests/integration/router-mcp.test.mjs`
- Modify: `project-incubator-plugin/skills/mod-incubator/SKILL.md`

**Contract:**
- `decline_change` 只处理精确匹配的 Pending Request，并要求当前拒绝 Prompt 属于同一项目、精确匹配请求 ID 与 Digest 且包含 Maker 明确拒绝；允许从新会话恢复并拒绝旧请求；
- 拒绝成功后只移除目标 Pending Request，生成带真实 Authorization 的 `DECLINE_CHANGE` Receipt，不应用拟议业务状态；
- 被拒绝的 Request 后续不能提交；
- `commit_change` 对新增或内容发生变化的 Decision 覆盖绑定本次真实 Authorization 与确认时间；
- 未变化的 Decision 保留原授权与确认时间。

- [x] **Step 1: 编写并运行失败测试，覆盖拒绝恢复与 Decision 授权重绑定**
- [x] **Step 2: 实现最小 Authorization 与 Runtime Tool 变更**
- [x] **Step 3: 更新 Mod Skill 调用规则并运行完整测试**
- [x] **Step 4: 打包安装修复版，拒绝 Round 10A 错误请求并重放**

### Correction Task: Structured Prompt Authorization Evidence

**Files:**
- Modify: `project-incubator-plugin/src/kernel/prompt-events.mjs`
- Modify: `project-incubator-plugin/src/kernel/authorization.mjs`
- Modify: `project-incubator-plugin/tests/unit/prompt-events.test.mjs`
- Modify: `project-incubator-plugin/tests/unit/authorization.test.mjs`

**Contract:**
- 继续只保存完整 Prompt 哈希和最多 240 字符的 `excerpt`，不保存完整 Prompt；
- 从完整 Prompt 提取唯一 Request ID、唯一 Scope Digest 与 `APPROVE` / `DECLINE` / `AMBIGUOUS` / `NONE` 意图；
- 授权校验优先使用结构化证据，授权令牌位于 240 字符之后时仍可正常闭合；
- 同时出现批准与拒绝、多个 Request 或多个 Digest 时不得形成可用授权声明；
- 旧 Prompt Record 缺少结构化字段时继续使用 `excerpt` 校验。

- [x] **Step 1: 编写长 Prompt 失败测试并确认当前实现返回 `PROMPT_SCOPE_NOT_CONFIRMED`**
- [x] **Step 2: 实现有界结构化授权证据提取与兼容读取**
- [x] **Step 3: 运行完整测试、打包、安装并验证安装缓存**
- [ ] **Step 4: 在新 Codex 会话中执行一次长 Prompt 宿主重放**

## 完成判定

只有以下事实全部有实际证据时，才能声明 MVP 完成：

- Tasks 1-9 各自测试通过并形成独立提交；
- Architecture 第 13 节所有继承项均可追溯到测试；
- 三个 Managed Project 文件足以恢复项目并生成完整 `inspect_project` 摘要；
- 未激活项目无副作用，激活项目不能绕过 Kernel；
- Mod 与 Sims 4 规则未渗入 Shared Kernel；
- 增加虚拟第二项目类型时不修改 Kernel；
- 旧 RC.2 自动化回归全部通过；
- 候选包在研发仓库外独立运行；
- 一次受限 Codex 宿主走查通过。

实施中若发现架构缺口，停止受影响 Task 并回到 `ARCHITECTURE.md` 修订；不新增平行 Architecture、Design、Contract 或 Runtime Spec 文档。

