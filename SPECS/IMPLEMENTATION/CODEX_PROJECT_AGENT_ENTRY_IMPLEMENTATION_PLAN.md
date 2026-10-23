# Codex 项目级 AGENTS 初始化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

状态：DRAFT / REVISION REQUIRED；本计划只覆盖首次初始化，尚未覆盖中途接入验收、已激活项目逐个补齐、旧版迁移与权威恢复。Maker 已选择分流方案，待新架构提案及下游规格获批后重写；不得据此实施。

**Goal:** Codex Plugin 初始化新 Managed Project 时可靠创建或保护项目级 `AGENTS.md`，并独立报告入口结果与权威 Receipt。

**Architecture:** 包内稳定中文模板由独立 Agent Entry 模块读取、检查、排他写入和安全撤销。Kernel 在现有项目串行化初始化过程中协调入口与三个 JSON 的闭合；现有四参 `initializeProjectState` API 保持可用，新增专用初始化入口供 MCP `initialize_project` 使用。

**Tech Stack:** Node.js ≥24、MCP SDK、`node:fs/promises`、`node:test`；不新增生产依赖。

**Spec:** [ACP](../ARCHITECTURE/CODEX_PROJECT_AGENT_ENTRY_CHANGE_PROPOSAL.md)、[Design](../DESIGN/CODEX_PROJECT_AGENT_ENTRY_DESIGN.md)、[Contract](../CONTRACTS/CODEX_PROJECT_AGENT_ENTRY_CONTRACT.md)、[Runtime](../RUNTIME/CODEX_PROJECT_AGENT_ENTRY_RUNTIME_SPEC.md)。

## Global Constraints

- 新建 `AGENTS.md` 只适用于现行 Codex Plugin 首次初始化；不得改动已激活项目。
- 文件不是第四份权威状态；不得改变 State Schema、Receipt Hash、revision、阶段或 Maker 授权。
- 已有文件不覆盖、不追加；目录、链接、不可读和并发 `EEXIST` 失败关闭。
- 模板默认简体中文、只含稳定入口规则；不引用 Legacy Runtime、四份 Markdown 状态或包外 `SPECS/`。
- 仅修改 `project-incubator-plugin/` 当前实现、对应测试与获批规格；不编辑真实 Managed Project 或插件缓存。

## Review Focus

1. 已有 `AGENTS.md` 内容恰好等于模板时仍须保持文件原样，并报告 `EXISTING_REVIEW_REQUIRED`，不能借标记覆盖它（Task 1、3）。
2. 目标为 Windows 链接或目录时不能跟随或删除，且权威 JSON 不得写入（Task 1、2）。
3. 排他创建时外部进程抢先创建，竞争者文件必须保留，错误为 `AGENT_ENTRY_CONFLICT`（Task 1）。
4. 入口创建后 Receipt 写入失败，只有身份和字节仍匹配才撤销入口；外部修改则保留并报告残留（Task 2）。
5. 候选包内模板缺失或回退到源码工作树时，仓库外验证必须失败，不得靠源码测试通过掩盖（Task 4、5）。

---

### Task 1: 包内模板与安全文件操作

**Files:** Create `project-incubator-plugin/templates/codex/AGENTS.md`、`project-incubator-plugin/src/kernel/agent-entry.mjs`、`project-incubator-plugin/tests/unit/agent-entry.test.mjs`。

**Interfaces:** `loadAgentEntryTemplate(pluginRoot): Promise<Buffer>`；`prepareAgentEntry(projectRoot, templateBuffer): Promise<{result:{path:"AGENTS.md",status:"CREATED"|"EXISTING_REVIEW_REQUIRED"}, rollbackToken:null|{dev,ino,sha256}}>`；`rollbackAgentEntry(projectRoot, rollbackToken): Promise<void>`。错误对象 `message` 使用 Contract 稳定码；安全撤销失败附 `residual_paths=["AGENTS.md"]`。

- [ ] **Step 1: 写红灯测试。** `node:test` 覆盖模板缺失/空白/旧正向指令、正常创建并逐字节回读、已有普通文件保持字节不变、目录/链接/不可读路径、排他创建 `EEXIST`、安全撤销前文件被改写或替换。测试用临时项目目录；链接或权限在宿主不支持时明确记录跳过原因，不假装通过。
- [ ] **Step 2: 验证红灯。** 在 `project-incubator-plugin/` 运行 `node --test tests/unit/agent-entry.test.mjs`；预期新增接口缺失或对应断言失败。
- [ ] **Step 3: 写最小实现。** 使用 `lstat` 区分现有对象，`open("wx")` 排他创建，写入并 `sync` 后按 Buffer 回读。撤销只在 `dev`、`ino` 与 SHA-256 均一致时 `unlink`；无法确认即抛 `AGENT_ENTRY_ROLLBACK_INCOMPLETE`，不得删除。模板从 `pluginRoot/templates/codex/AGENTS.md` 读取并完成 Contract 中的最小内容检查。
- [ ] **Step 4: 验证绿灯并提交。** 重跑 Task 1 测试；全部通过后只提交本 Task 文件。

### Task 2: 初始化事务协调与失败恢复

**Files:** Modify `project-incubator-plugin/src/kernel/state-store.mjs`；Test `project-incubator-plugin/tests/unit/state-store.test.mjs`。

**Interfaces:** 保留 `initializeProjectState(root, activation, state, authorizationRef): Promise<Receipt>`；新增 `initializeProjectWithAgentEntry(root, activation, state, authorizationRef, templateBuffer): Promise<{receipt:Receipt,agentEntry:{path,status}}>`。两个入口复用同一 JSON 初始化核心与项目队列；新入口消费 Task 1 的 `prepareAgentEntry` / `rollbackAgentEntry`。

- [ ] **Step 1: 写红灯测试。** 新入口分别断言 CREATED/已有文件、JSON activation/state/receipt 写入故障、Receipt 回读故障、安全撤销和不安全残留；已有四参 API 的调用与结果保持原样。
- [ ] **Step 2: 验证红灯。** 运行 `node --test tests/unit/state-store.test.mjs`；新增测试应因接口缺失失败。
- [ ] **Step 3: 写最小实现。** 在现有按项目队列内先做控制文件空状态检查，再处理 Agent Entry，之后执行原三 JSON 写入与 Receipt 验证。失败时先恢复 JSON，再按 rollbackToken 撤销新入口；任一恢复失败返回 `AGENT_ENTRY_ROLLBACK_INCOMPLETE` 并保留相对路径残留信息。不得让成功 Receipt 在失败结果中出现。
- [ ] **Step 4: 验证绿灯并提交。** 运行 `node --test tests/unit/state-store.test.mjs tests/unit/agent-entry.test.mjs`；全部通过后只提交本 Task 文件。

### Task 3: MCP 初始化返回与 Router 报告

**Files:** Modify `project-incubator-plugin/src/server.mjs`、`project-incubator-plugin/skills/project-incubator-router/SKILL.md`；Test `project-incubator-plugin/tests/integration/router-mcp.test.mjs`、`project-incubator-plugin/tests/e2e/web-product-flow.test.mjs`；Create `project-incubator-plugin/tests/e2e/agent-entry-flow.test.mjs`。

**Interfaces:** `initialize_project` 输入不变；成功 `structuredContent={activation,receipt,agent_entry:{path:"AGENTS.md",status:"CREATED"|"EXISTING_REVIEW_REQUIRED"}}`。错误仍用 `isError` 和 `structuredContent.error.code`；`AGENT_ENTRY_ROLLBACK_INCOMPLETE` 可附 `error.residual_paths`。

- [ ] **Step 1: 写红灯测试。** 模拟有效 Maker 下一轮批准，断言新项目创建入口并保留 Receipt、已有文件不变且返回人工核对、授权失败零副作用、`mod`/desktop/web 不因 Host Profile 差异漏生成；Router 指导要求分别报告 Receipt 和 Agent Entry。
- [ ] **Step 2: 验证红灯。** 运行 `node --test tests/integration/router-mcp.test.mjs tests/e2e/web-product-flow.test.mjs tests/e2e/agent-entry-flow.test.mjs`；新增断言应失败。
- [ ] **Step 3: 写最小实现。** 授权成功后加载 Task 1 模板并调用 Task 2 新入口，闭合后才 `consumeActivationRequest`；增加 `agent_entry` 返回与残留路径映射。Router 文案只描述初始化结果与已有文件人工核对，不让 Agent 直接编辑权威文件。
- [ ] **Step 4: 验证绿灯并提交。** 重跑本 Task 测试；全部通过后只提交本 Task 文件。

### Task 4: 候选包自包含与拒绝来源回退

**Files:** Modify `project-incubator-plugin/scripts/package-candidate.mjs`、`scripts/verify-candidate.mjs`、`scripts/runtime-guidance.mjs`；Test `project-incubator-plugin/tests/integration/candidate-package.test.mjs`、`tests/contract/runtime-guidance-drift.test.mjs`。

**Interfaces:** 候选白名单允许且只允许 `templates/codex/AGENTS.md`；验证器从候选根目录读取模板，拒绝缺失、链接、旧正向指令及候选根目录外引用；候选聚合哈希仍覆盖该模板。

- [ ] **Step 1: 写红灯测试。** 断言候选包含模板，缺失/篡改/链接模板时结构验证失败，模板变化使聚合哈希变化，源码树存在但候选缺失时不得回退；保留对 `PROJECT_INCUBATOR/` 与 `_V*` 的禁止。
- [ ] **Step 2: 验证红灯。** 运行 `node --test tests/integration/candidate-package.test.mjs tests/contract/runtime-guidance-drift.test.mjs`；新增断言应失败。
- [ ] **Step 3: 写最小实现。** 扩展打包白名单和候选结构校验，复用内容检查而不复制旧 Legacy 模板；保持候选自身依赖隔离。
- [ ] **Step 4: 验证绿灯并提交。** 重跑本 Task 测试；全部通过后只提交本 Task 文件。

### Task 5: 全量与安装后验收闭合

**Files:** Modify `SPECS/IMPLEMENTATION/CODEX_PROJECT_AGENT_ENTRY_ACCEPTANCE_TEST_PLAN.md` 的结果区；必要时补充前述测试，但不改已验收历史记录。

**Interfaces:** 消费 Tasks 1–4 的测试和候选包；产出源码 commit、候选版本/哈希、安装源、临时 Managed Project 的 `AGENTS.md`/Receipt 证据与未闭合事项。

- [ ] **Step 1: 全量验证。** 在 `project-incubator-plugin/` 运行 `npm test`，记录总数、失败数和退出码；Legacy 回归按当前获批验收脚本运行并记录结果。
- [ ] **Step 2: 候选验证。** 将候选打包到已验证的临时目录，从仓库外运行结构与完整模式；确认模板、来源隔离和哈希。不得直接改插件缓存。
- [ ] **Step 3: 宿主验证。** 经受支持的插件安装路径安装新候选，在新 Codex 任务用临时项目完成真实授权初始化，回读 `AGENTS.md`、三个 JSON 和 Receipt；再开后续任务观察原生入口加载。若安装或新任务不可用，记录 `BLOCKED`，不声称已闭合。
- [ ] **Step 4: 报告并提交。** 将证据写入 Acceptance Plan，按 Task/Status/Changed Files/Validation/Issues 报告；全部标准实际通过后再申请发布或合并，不修改任何真实 Managed Project。
