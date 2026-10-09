# Desktop Product Incubator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** IMPLEMENTATION CODE COMPLETE / AUTOMATED ACCEPTANCE PASSED / MANUAL M1–M6 PENDING

**Approved By:** Maker, 2026-10-05

**Goal:** 在不改变既有 Mod 领域语义的前提下，为 Project Incubator Plugin 增加 `desktop-product`、`desktop-product-incubator`、`windows-desktop`，并实现通用 Workflow Entry 与显式 Host Requirement。

**Architecture:** Registry 继续负责 Project Type、Child Skill、Workflow Module 与 Host Profile 路由；Shared Kernel 新增通用 Entry/Host 结构校验，不出现 Desktop 条件分支。Desktop Workflow 独立实现 P0–P6，桌面阶段解释、安全边界和 Windows 收紧规则分别放入 Child Skill 与 Host Profile。

**Tech Stack:** Node.js 24+、ES Modules、Zod 3、Node Test Runner、Codex Plugin Skills/Profiles、JSON 权威状态。

**Spec:** `SPECS/ARCHITECTURE/DESKTOP_PRODUCT_INCUBATOR_CHANGE_PROPOSAL.md`、`SPECS/PROJECT_TYPES/DESKTOP_PRODUCT_PROFILE.md`、`SPECS/CONTRACTS/DESKTOP_PRODUCT_INCUBATOR_CONTRACT.md`、`SPECS/RUNTIME/DESKTOP_PRODUCT_INCUBATOR_RUNTIME_SPEC.md`

## Global Constraints

- 从 `main-restructure-v2` 已验证提交 `6f4daf0` 派生的独立分支实施。
- 不修改或删除 `skills/mod-incubator/SKILL.md`、`skills/sims-4-host-profile/SKILL.md`、`profiles/project-types/mod.json` 或 `profiles/hosts/sims-4.json`。
- 允许为通用 Entry Contract 向 `src/domains/mod/workflow.mjs` 增加 `evaluateEntry`，但不得改变 M0–M5、`MODEL_REVIEW` 或现有 Transition 语义。
- Browser Extension 不属于本计划；不得新增浏览器 Project Type、Skill、Profile 或 Runtime 字段。
- 不新增 Markdown 运行态状态文件；权威状态继续是 Activation、Project State、Receipt 三份机器可读状态。
- `desktop-product` 的 Host Requirement 为 `REQUIRED`；`windows-desktop` 不得成为默认值。
- 新激活使用 Project State `1.1`；既有 State `1.0` 保持可读写且不自动迁移。
- Registry 使用 `schema_version = 1.1`；Project Type 必须显式声明 `host_profile_requirement`。
- 全部实现按 TDD 进行；每个任务先证明测试失败，再写最小实现。
- 新候选基础版本为 `0.2.0`；候选 Manifest 使用 `0.2.0+codex.<UTC YYYYMMDDHHMMSS>`。

## Review Focus

- REQUIRED 类型遗漏 Host 时必须失败，不能选择 Registry 中第一个 Host；由 Task 3、4 覆盖。
- `ADOPT_EXISTING` 的阶段来自 Agent Evidence 判断，但 Kernel 只能校验结构，不能读取内容后替 Agent改阶段；由 Task 2、4 覆盖。
- State 1.0 既有项目必须继续 Transition，State 1.1 的 Entry 必须不可变；由 Task 1、4 覆盖。
- `MODEL_REVIEW` 和 P4 Correction 均不得成为已有项目接管入口；由 Task 2、6 覆盖。
- Browser Extension、网站和游戏安装环境不能被 Desktop Router/Skill 误写成 Host；由 Task 5、6 覆盖。

---

## File Structure

| File | Responsibility |
| --- | --- |
| `project-incubator-plugin/src/kernel/schemas.mjs` | Project State 1.0/1.1 解析与新激活 1.1 约束 |
| `project-incubator-plugin/src/kernel/registry.mjs` | Registry 1.1、Host Requirement、Workflow Module 双接口加载 |
| `project-incubator-plugin/src/kernel/router.mjs` | Route/Activation Request 持久化；保持完整 Scope Digest |
| `project-incubator-plugin/src/server.mjs` | Entry 双重校验、Route 重验、Entry 不可变与既有 Transition 集成 |
| `project-incubator-plugin/src/domains/desktop/workflow.mjs` | Desktop P0–P6 Entry 与 Transition evaluator |
| `project-incubator-plugin/src/domains/mod/workflow.mjs` | Mod 的通用 Entry evaluator；保留现有 Transition |
| `project-incubator-plugin/profiles/registry.json` | 两个 Project Type 与两个 Host Profile 的权威注册 |
| `project-incubator-plugin/profiles/project-types/desktop-product.json` | Desktop Project Type 机器 Profile |
| `project-incubator-plugin/profiles/hosts/windows-desktop.json` | Windows Host 机器 Profile |
| `project-incubator-plugin/skills/desktop-product-incubator/SKILL.md` | P0–P6 Desktop 指导、Evidence、安全与纠正规则 |
| `project-incubator-plugin/skills/windows-desktop-host-profile/SKILL.md` | Windows 安装、权限、升级、卸载、恢复与真实环境约束 |
| `project-incubator-plugin/skills/project-incubator-router/SKILL.md` | Entry Mode、显式 Host、Desktop 路由与不支持边界 |
| `project-incubator-plugin/.codex-plugin/plugin.json` | 新能力描述与候选版本 |
| `project-incubator-plugin/ARCHITECTURE.md` | 已实现 Router/Kernel/Child/Host 架构与兼容矩阵 |
| `project-incubator-plugin/tests/**` | Unit、Integration、Contract、E2E 与回归证据 |

### Task 1: Project State 1.1 and Workflow Entry Schema

**Files:**
- Modify: `project-incubator-plugin/src/kernel/schemas.mjs`
- Modify: `project-incubator-plugin/tests/unit/schemas.test.mjs`

**Interfaces:**
- Preserves: `parseProjectState(value)` accepts legacy `schema_version = "1.0"` without Entry.
- Produces: State `1.1` requires `workflow.entry` with `mode`、`initial_stage`、`assessment_summary`、`evidence_refs`、`assessed_at`.
- Produces: `parsePostActivationInitialState(value)` accepts only State 1.1 for new Activation while retaining existing post-activation narrative checks.

- [ ] **Step 1: Write failing tests for valid State 1.1, missing Entry, unknown Entry field, invalid timestamp and over-bound text/list values**

```javascript
assert.equal(parseProjectState(validState11()).workflow.entry.mode, "NEW_PROJECT");
assert.throws(() => parseProjectState(state11WithoutEntry()));
```
- [ ] **Step 2: Add a failing compatibility test proving State 1.0 without Entry still parses unchanged**
- [ ] **Step 3: Add a failing activation test proving `parsePostActivationInitialState` rejects State 1.0 with `WORKFLOW_ENTRY_REQUIRED` rather than silently upgrading it**
- [ ] **Step 4: Implement separate strict Workflow 1.0/1.1 schemas and the new-activation guard without changing Activation or Receipt schema versions**
- [ ] **Step 5: Run `node --test --test-isolation=none tests/unit/schemas.test.mjs`; expected all tests pass**
- [ ] **Step 6: Commit `feat(plugin): add workflow entry state schema`**

### Task 2: Child Workflow Entry and Desktop P0–P6

**Files:**
- Create: `project-incubator-plugin/src/domains/desktop/workflow.mjs`
- Create: `project-incubator-plugin/tests/unit/desktop-workflow.test.mjs`
- Modify: `project-incubator-plugin/src/domains/mod/workflow.mjs`
- Modify: `project-incubator-plugin/tests/unit/mod-workflow.test.mjs`

**Interfaces:**
- Produces: `evaluateDesktopEntry(initialState) -> EntryEvaluation` and alias `evaluateEntry`.
- Produces: `evaluateDesktopTransition(state, request) -> TransitionEvaluation` and alias `evaluateTransition`.
- Produces: `desktopStages = Object.freeze(["P0", ..., "P6"])`.
- Adds: `evaluateModEntry(initialState) -> EntryEvaluation` and alias `evaluateEntry`.
- Preserves: `evaluateModTransition` and `modStages` public behavior.

- [ ] **Step 1: Write failing Desktop Entry tests: NEW_PROJECT only P0; ADOPT_EXISTING accepts P0–P6 with non-empty refs; Entry/State mismatch and unknown stage reject with approved codes**

```javascript
assert.equal(evaluateDesktopEntry(desktopState("P0", "NEW_PROJECT")).allowed, true);
assert.equal(evaluateDesktopEntry(desktopState("P3", "NEW_PROJECT")).code, "WORKFLOW_ENTRY_STAGE_INVALID");
```
- [ ] **Step 2: Write failing Desktop Transition tests for P0→P1→…→P6, P6→P2/P3/P4/P5, illegal skips, incomplete conditions and boundary authorization**
- [ ] **Step 3: Write failing Mod Entry tests: NEW_PROJECT only M0, ADOPT_EXISTING accepts M0–M5, and `MODEL_REVIEW` is rejected**
- [ ] **Step 4: Implement shared local helpers only where they do not create cross-domain policy; keep Desktop and Mod stage maps in their own modules**
- [ ] **Step 5: Run both workflow test files; expected all tests pass and all pre-existing Mod assertions remain unchanged**
- [ ] **Step 6: Commit `feat(plugin): add desktop workflow and entry evaluators`**

### Task 3: Registry 1.1, Profiles, and Explicit Host Requirement

**Files:**
- Modify: `project-incubator-plugin/src/kernel/registry.mjs`
- Modify: `project-incubator-plugin/profiles/registry.json`
- Create: `project-incubator-plugin/profiles/project-types/desktop-product.json`
- Create: `project-incubator-plugin/profiles/hosts/windows-desktop.json`
- Modify: `project-incubator-plugin/tests/unit/registry.test.mjs`
- Create: `project-incubator-plugin/tests/unit/desktop-profile.test.mjs`

**Interfaces:**
- Changes: `validateRegistry(value)` requires Registry 1.1 and `host_profile_requirement` enum on every Project Type.
- Changes: `loadWorkflowEvaluators(pluginRoot, registry)` returns `Map<projectTypeId, { evaluateEntry, evaluateTransition }>`.
- Preserves: `resolveRoute(registry, projectTypeId, hostProfileId)` return shape.
- Adds failure codes: `HOST_PROFILE_REQUIRED` and `HOST_PROFILE_FORBIDDEN`; preserves existing mismatch/not-found codes.
- Defines: Desktop Profile stages exactly `P0`–`P6`, no subflow stage; Windows Profile required context is `windows_version`、`architecture`、`install_scope`、`privilege_mode`、`distribution_format`.

- [ ] **Step 1: Write failing Registry tests for 1.0 rejection, missing/invalid Requirement, Desktop REQUIRED, Mod OPTIONAL and synthetic FORBIDDEN behavior**

```javascript
assert.throws(() => validateRegistry(registry10()));
assert.throws(() => resolveRoute(registry11(), "desktop-product", null), /HOST_PROFILE_REQUIRED/);
```
- [ ] **Step 2: Write failing loader tests for missing `evaluateEntry`, missing `evaluateTransition`, out-of-root module and valid dual-interface module**
- [ ] **Step 3: Write failing profile tests for Desktop P0–P6, Windows identity, Kernel constraints, required environment context and forbidden browser/domain ownership**
- [ ] **Step 4: Implement Registry 1.1, dual evaluator loading and fail-closed Route resolution without default Host selection**
- [ ] **Step 5: Register `desktop-product` / `desktop-product-incubator` / `windows-desktop`; add only the two new JSON Profiles**
- [ ] **Step 6: Run Registry and Desktop Profile unit tests; expected all pass**
- [ ] **Step 7: Commit `feat(plugin): register desktop product and windows host`**

### Task 4: Kernel Activation Validation and Entry Immutability

**Files:**
- Modify: `project-incubator-plugin/src/server.mjs`
- Modify: `project-incubator-plugin/tests/integration/router-mcp.test.mjs`
- Create: `project-incubator-plugin/tests/integration/desktop-router-mcp.test.mjs`
- Modify: `project-incubator-plugin/tests/e2e/enforcement-flow.test.mjs`

**Interfaces:**
- Adds internal: `validateWorkflowEntry(initialState, evaluator)` using `evaluator.evaluateEntry` and existing Workflow Shape comparison.
- Changes internal: `validateWorkflowTransition(..., evaluator)` calls `evaluator.evaluateTransition`.
- Adds internal: `assertWorkflowEntryImmutable(currentState, proposedState)`.
- Preserves MCP Tool names and request shapes; Entry remains inside `state.workflow.entry` and the full Initial State remains covered by `scope_digest`.

- [ ] **Step 1: Update only new-activation Mod fixtures to State 1.1 + `NEW_PROJECT/M0`; retain already-activated State 1.0 fixtures as legacy evidence**
- [ ] **Step 2: Write failing Desktop tests for missing Host, wrong Host, NEW_PROJECT/P0 activation, ADOPT_EXISTING/P3 activation with Evidence, and no-Evidence rejection**

```javascript
assert.equal((await prepareDesktop({ host: null })).structuredContent.error.code, "HOST_PROFILE_REQUIRED");
assert.equal((await prepareDesktop({ mode: "ADOPT_EXISTING", stage: "P3", evidence_refs: [] })).structuredContent.error.code, "WORKFLOW_ENTRY_EVIDENCE_REQUIRED");
```
- [ ] **Step 3: Write failing prepare/initialize drift tests proving Entry and Route are revalidated before commit and no authority files are partially written**
- [ ] **Step 4: Write failing mutation tests proving State 1.1 Entry cannot change, while State 1.0 can still perform an existing legal Mod Transition**
- [ ] **Step 5: Write a failing P4 Correction test proving a same-stage, no-`workflow_transition` State Mutation follows the ordinary authorized change path**
- [ ] **Step 6: Implement generic Entry validation in `prepare_activation` and `initialize_project`, include no Desktop-specific branch, and preserve the existing Scope Digest payload**
- [ ] **Step 7: Implement Entry immutability in both prepare and commit validation paths**
- [ ] **Step 8: Run the three integration/E2E files; expected all pass**
- [ ] **Step 9: Commit `feat(plugin): enforce activation entry and host contracts`**

### Task 5: Desktop Child Skill, Windows Host Skill, and Router Guidance

**Files:**
- Create: `project-incubator-plugin/skills/desktop-product-incubator/SKILL.md`
- Create: `project-incubator-plugin/skills/windows-desktop-host-profile/SKILL.md`
- Modify: `project-incubator-plugin/skills/project-incubator-router/SKILL.md`
- Modify: `project-incubator-plugin/.codex-plugin/plugin.json`
- Modify: `project-incubator-plugin/package.json`
- Modify: `project-incubator-plugin/package-lock.json`
- Modify: `project-incubator-plugin/ARCHITECTURE.md`
- Create: `project-incubator-plugin/tests/contract/desktop-guidance.test.mjs`
- Modify: `project-incubator-plugin/tests/contract/legacy-invariants.test.mjs`

**Interfaces:**
- Produces: Desktop Child Skill with P0–P6 names unchanged and Desktop-specific descriptions/checkpoints.
- Produces: Windows Host Skill that tightens environment/Evidence without changing phases.
- Changes: Router requires Entry Mode and explicit matching Host before Desktop Activation.
- Preserves: existing `mod-incubator` and `sims-4-host-profile` file bytes.
- Defines: Skill frontmatter names exactly `desktop-product-incubator` and `windows-desktop-host-profile`; descriptions require prior Router selection and do not claim Browser ownership.

- [ ] **Step 1: Write a failing invariant test that pins implementation-start SHA-256 digests of the four protected Mod/Sims files**

```javascript
assert.equal(await sha256File("skills/mod-incubator/SKILL.md"), protectedDigests.modSkill);
assert.equal(await sha256File("profiles/hosts/sims-4.json"), protectedDigests.simsProfile);
```

- [ ] **Step 2: Invoke the skill-authoring workflow, then write failing content tests for P0–P6 names, P2 feasibility, P4 checkpoints/correction, P5 target evidence, P6 routing and Maker boundaries**
- [ ] **Step 3: Add failing Host Skill tests for Windows version/architecture, install scope, permissions, filesystem/process/security software, packaging/signing, upgrade/uninstall/recovery and real-environment Evidence**
- [ ] **Step 4: Add failing Router tests proving no default Host, ADOPT_EXISTING responsibility split, unsupported Host stop, and Browser Extension remains unsupported rather than routed to Desktop**
- [ ] **Step 5: Implement `desktop-product-incubator` and `windows-desktop-host-profile` with no new reference files**
- [ ] **Step 6: Update Router guidance for Entry/Host confirmation and unsupported Browser/Host handling**
- [ ] **Step 7: Update Architecture and manifest descriptions without presenting Desktop as the only product type; set Package/lockfile base version to `0.2.0` and manifest candidate version using the approved timestamp format**
- [ ] **Step 8: Run Contract tests and re-check protected file digests; expected all pass and all four digests unchanged**
- [ ] **Step 9: Commit `docs(plugin): add desktop incubation guidance`**

### Task 6: End-to-End Acceptance, Packaging, and Regression

**Files:**
- Create: `project-incubator-plugin/tests/e2e/desktop-product-flow.test.mjs`
- Modify: `project-incubator-plugin/ACCEPTANCE_TEST_LOG.md`
- Modify: `SPECS/README.md`
- Modify: `SPECS/IMPLEMENTATION/DESKTOP_PRODUCT_INCUBATOR_IMPLEMENTATION_PLAN.md`
- Modify: `SPECS/IMPLEMENTATION/DESKTOP_PRODUCT_INCUBATOR_ACCEPTANCE_TEST_PLAN.md`
- Verify only: `project-incubator-plugin/scripts/package-candidate.mjs`
- Test: all Plugin and Legacy suites

**Interfaces:**
- Produces: full Desktop route → authorized activation → P0/P1 transition evidence.
- Produces: packaged candidate containing both project types and both Host Profiles.
- Preserves: existing Plugin, Legacy unit, Legacy integration and Legacy e2e behavior.

- [x] **Step 1: Write a failing E2E test for explicit `desktop-product + windows-desktop`, NEW_PROJECT/P0 Activation, scoped Maker authorization, Receipt verification and legal P0→P1 Transition**

```javascript
assert.equal(snapshot.activation.project_type_id, "desktop-product");
assert.equal(snapshot.state.workflow.stage, "P1");
assert.equal(receipt.authorization_ref.request_id, request.request_id);
```
- [x] **Step 2: Add E2E negative cases for absent Host, illegal initial phase, altered Entry and Browser-only scope**
- [x] **Step 3: Run `npm test`; require zero failures and record the new exact Plugin total, with the previous 88 tests still represented**
- [x] **Step 4: From repository root run Legacy unit, integration and e2e commands; require exactly 132/132、32/32、3/3**
- [x] **Step 5: Package to a fresh temporary directory, run `npm ci --omit=dev`, then load Registry and both Workflow Modules from outside the repository**
- [x] **Step 6: Verify package whitelist excludes `SPECS`、tests、legacy runtime and includes the two new Skills/Profiles plus Candidate metadata**
- [ ] **Step 7: Execute the approved Acceptance Test Plan, record actual evidence and update statuses only from observed results**
- [x] **Step 8: Commit `test(plugin): accept desktop product incubator`**

### Task 6 Execution Record

- 2026-10-07：Desktop E2E 以 `0.1.0 !== 0.2.0` 形成预期 RED；Kernel 改为从候选 `package.json` 读取激活版本后，E2E `5/5` GREEN。
- 整分支审阅复现并修复 Activation Scope 合法漂移、State 1.1 Entry 删除错误码、非法 Entry Mode 错误码、`Entry = null` 内部异常、ESM 缓存伪覆盖与 MCP 握手旧版本；补齐 D06 完整接管激活证据，并把 P4 恢复为一个模型一致性约束与两个批准检查点。
- Plugin 全量：`132/132`，0 failures。
- Legacy：unit `132/132`、integration `32/32`、e2e `3/3`。
- Candidate：Manifest `0.2.0+codex.20261008084456`、Package `0.2.0`；安装 94 个生产依赖；白名单、仓库外 Registry/Workflow/Kernel Route/Entry/version smoke 均通过。
- 最终整分支复审：HEAD `ffc38f2` 相对 `6f4daf0` 无 Critical、Important 或 Minor；工作树干净，临时夹具与候选已清理。
- 自动化 Acceptance Stage A–G 已通过；Manual Behavior Acceptance M1–M6 尚未执行，因此未达到发布 Exit Criteria。

### Task 7: Manual Acceptance Remediation and Hook Closure

**Files:**
- Modify: `project-incubator-plugin/tests/integration/router-mcp.test.mjs`
- Modify: `project-incubator-plugin/hooks/user-prompt-submit.mjs`
- Modify: `project-incubator-plugin/ACCEPTANCE_TEST_LOG.md`
- Modify: `SPECS/README.md`
- Modify: `SPECS/IMPLEMENTATION/DESKTOP_PRODUCT_INCUBATOR_IMPLEMENTATION_PLAN.md`
- Modify: `SPECS/IMPLEMENTATION/DESKTOP_PRODUCT_INCUBATOR_ACCEPTANCE_TEST_PLAN.md`

**Interfaces:**
- Preserves: Pending Activation Prompt provenance, scoped Maker Authorization and three-file atomic initialization.
- Produces: a bootstrap-turn marker whose virtual pre-activation revision lets Stop verify a same-turn initialization Receipt.
- Does not decide: the separate uninitialized `inspect_project` / `get_project_state` error contract.

- [ ] **Step 1: Add an integration test reproducing a Maker-approved initialization followed by Stop in the same turn; verify RED is missing turn marker**
- [ ] **Step 2: Implement the minimal bootstrap turn marker with virtual pre-activation revision `-1`; require the initialization Receipt ID in the final message**
- [ ] **Step 3: Run the focused integration test and full Plugin suite; require zero failures**
- [ ] **Step 4: Build and install a fresh candidate, then reproduce the same-turn activation closure in a real Codex task**
- [ ] **Step 5: Execute M1–M5 as five distinct Maker Prompt/Setup rounds and preserve each final answer, tool result, state effect and PASS/FAIL reason**
- [ ] **Step 6: Rewrite the manual acceptance report into one current conclusion plus clearly labelled historical evidence; do not leave competing “latest” conclusions**
- [ ] **Step 7: Synchronize Active Specifications, exact candidate identity, test totals and acceptance status only from fresh evidence**
- [ ] **Step 8: Re-run Plugin and Legacy regression, verify protected Mod/Sims digests, and commit the remediation**

## Plan Acceptance Criteria

- Tasks 1–6 have independent red/green evidence and commits.
- Registry 1.1、State 1.1、Entry evaluator 与 Host Requirement match the approved Contract exactly.
- Desktop NEW_PROJECT and ADOPT_EXISTING both work; unsupported/missing Host and insufficient Entry fail before mutation.
- State 1.0 Managed Projects and existing Mod Workflow remain compatible.
- `mod-incubator`、`sims-4` Skill/Profile protected files are byte-for-byte unchanged.
- Browser Extension is neither implemented nor routed to Desktop.
- Plugin full suite and Legacy 132/32/3 suites pass with zero failures.
- Candidate package works from outside the repository and reports a `0.2.0+codex.<timestamp>` identity.
- No implementation is declared complete until the Acceptance Test Plan criteria and actual evidence are recorded.

## Execution Authorization

Maker 于 2026-10-05 确认审阅清单 1–8，并选择当前会话串行实施。Maker 于 2026-10-09 批准 Task 7 的 Stop Hook 修复、独立 M1–M5 重放、验收记录整理与活动规格同步。未初始化状态查询的替代错误码仍是独立 Design Gap，不在 Task 7 中实现。新发现的 Product 或 Architecture 变更仍需另行确认。

Maker 于 2026-10-09 进一步确认 Task 7 人工验收发现的授权识别修复：`我批准激活请求` 在同时精确匹配唯一 `request_id` 与 `scope_digest` 时属于显式批准；实现必须保持否定与拒绝语义不被误判，统一结构化 Claim 与 Legacy Fallback 的判断规则，并以真实 Bootstrap / Stop Hook 闭合重放验证。该修复不放宽 Scope、Prompt 来源、Session、Turn、时效或 Maker 身份校验。
