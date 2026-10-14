# Web Product Incubator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 按任务实施；每个任务都必须使用 `superpowers:test-driven-development`，完成声明前使用 `superpowers:verification-before-completion`。

> Specification Version: Plugin Web Product V1.2
> Status: APPROVED
> Approved By: Maker，2026-10-14
> Implementation Authorization: GRANTED FOR TASKS 1–7
> Depends On: `SPECS/PROJECT_TYPES/WEB_PRODUCT_PROFILE.md`、`SPECS/CONTRACTS/WEB_PRODUCT_INCUBATOR_CONTRACT.md`、`SPECS/RUNTIME/WEB_PRODUCT_INCUBATOR_RUNTIME_SPEC.md`

## 1. 一页摘要

本计划把 `web-product` 加入现有 Project Incubator Plugin。它复用已经存在的 Registry、Router、Activation、Project State 1.1、授权、Receipt 和 P0–P6 控制面，只新增 Web Project Type 的配置、Workflow evaluator、Child Skill 和验证覆盖。

完成后，Plugin 能够：

- 把“浏览器是主要界面，同时具有前端与后端职责”的项目路由为 `web-product`；
- 对 Web Project 强制 `host_profile_requirement = FORBIDDEN`；
- 支持新项目从 P0 激活，已有项目凭 Evidence 从 P0–P6 接管；
- 以 Child Skill 指导 Build、localhost、真实浏览器、适用次级界面和人工验证；
- 保持 MCP 等次级界面属于同一 Web Product 的条件边界；
- 明确停止在本地验证，不声称已部署或 Production Ready。

本计划不新增 Web 专用 Runtime Tool、State 字段、Gate 类型、Host Profile 或 Deployment 能力。预计候选 Package 版本为 `0.3.0`，Manifest 使用 `0.3.0+codex.<14 位时间戳>`。

## 2. 全局约束

1. 实现前必须先获得本计划与 Acceptance Test Plan 的 Maker 明确批准。
2. 不修改 `SPECS/_V*`、V1.1 RC 人工验收状态或 Managed Project Core Context。
3. 不修改 `src/kernel/schemas.mjs` 的 State/Activation Schema，不新增 Web/MCP Runtime 枚举。
4. 不新增 Browser、localhost、OS 或 Deployment Host Profile。
5. 不在 Kernel 中解释自然语言、Evidence 强弱、Build 日志、浏览器结果或 MCP 业务结果。
6. Web、Desktop、Mod 使用同一 Maker Authorization、Pending Request、Digest、Receipt 与 Context Mutation 机制。
7. 若实现需要改变 Tool Shape、Core Schema、Runtime Invariant 或已批准语义，停止并登记 `DESIGN_GAP`。
8. 每个任务按“先失败测试、再最小实现、再回归”的顺序完成，并单独提交。
9. 保护现有 Maker 改动，不回滚无关文件。
10. 本计划中的 `node`、`npm` 和相对测试路径命令默认从 `project-incubator-plugin/` 执行；仓库级 Python 回归从 Implementation Repository 根目录执行。

## 3. 文件范围

计划新增：

- `project-incubator-plugin/src/domains/web/workflow.mjs`
- `project-incubator-plugin/profiles/project-types/web-product.json`
- `project-incubator-plugin/skills/web-product-incubator/SKILL.md`
- `project-incubator-plugin/tests/unit/web-workflow.test.mjs`
- `project-incubator-plugin/tests/unit/web-profile.test.mjs`
- `project-incubator-plugin/tests/contract/web-guidance.test.mjs`
- `project-incubator-plugin/tests/contract/plugin-manifest.test.mjs`
- `project-incubator-plugin/tests/integration/web-router-mcp.test.mjs`
- `project-incubator-plugin/tests/e2e/web-product-flow.test.mjs`
- `project-incubator-plugin/scripts/verify-candidate.mjs`
- `project-incubator-plugin/tests/integration/candidate-package.test.mjs`

计划修改：

- `project-incubator-plugin/profiles/registry.json`
- `project-incubator-plugin/skills/project-incubator-router/SKILL.md`
- `project-incubator-plugin/.codex-plugin/plugin.json`
- `project-incubator-plugin/package.json`
- `project-incubator-plugin/package-lock.json`
- `project-incubator-plugin/ARCHITECTURE.md`
- `project-incubator-plugin/src/kernel/registry.mjs`
- `project-incubator-plugin/tests/unit/registry.test.mjs`
- `project-incubator-plugin/tests/contract/desktop-guidance.test.mjs`
- `project-incubator-plugin/tests/contract/legacy-invariants.test.mjs`
- `project-incubator-plugin/tests/integration/mcp-handshake.test.mjs`
- `project-incubator-plugin/tests/e2e/desktop-product-flow.test.mjs`
- `project-incubator-plugin/ACCEPTANCE_TEST_LOG.md`（仅在验收产生真实证据后写入）

预期不修改：

- `project-incubator-plugin/src/server.mjs`
- `project-incubator-plugin/src/kernel/schemas.mjs`
- `project-incubator-plugin/src/kernel/authorization.mjs`
- `project-incubator-plugin/src/kernel/state-store.mjs`
- 既有 Mod、Sims 4、Desktop 与 Windows Profile/Skill/Workflow 正文

若通用 Kernel 无法通过配置加载 Web 类型，先判断是既有实现缺陷还是规格缺口；未经 Maker 批准不得扩大范围。

## 4. 任务顺序

### Task 1：建立 Web Workflow evaluator

**Files**

- Create: `project-incubator-plugin/tests/unit/web-workflow.test.mjs`
- Create: `project-incubator-plugin/src/domains/web/workflow.mjs`

**接口**

```js
evaluateWebEntry(state) -> EntryEvaluation
evaluateWebTransition(state, request) -> TransitionEvaluation
evaluateEntry = evaluateWebEntry
evaluateTransition = evaluateWebTransition
webStages = Object.freeze(["P0", "P1", "P2", "P3", "P4", "P5", "P6"])
```

**步骤**

- [ ] 写失败测试：`NEW_PROJECT` 只接受 P0；`ADOPT_EXISTING` 接受 P0–P6 且要求 Evidence。
- [ ] 写失败测试：Entry Stage、State Stage、`allowed_next`、`return_stage` 的期望形状。
- [ ] 写失败测试：P0→P1→…→P6、P6→P2/P3/P4/P5；拒绝跳级、P6→P0/P1、缺 Completion、缺必要 Maker Authorization。
- [ ] 运行并确认因模块缺失而失败：

```powershell
node --test --test-isolation=none tests/unit/web-workflow.test.mjs
```

- [ ] 以 Desktop evaluator 的通用接口实现最小 Web evaluator，不引入 Checkpoint、Validation Channel 或 Deployment Stage。
- [ ] 重跑测试并通过。
- [ ] Commit：`feat(plugin): add web product workflow evaluator`

### Task 2：注册 Web Project Type 与 Profile

**Files**

- Create: `project-incubator-plugin/tests/unit/web-profile.test.mjs`
- Modify: `project-incubator-plugin/tests/unit/registry.test.mjs`
- Modify: `project-incubator-plugin/src/kernel/registry.mjs`
- Create: `project-incubator-plugin/profiles/project-types/web-product.json`
- Modify: `project-incubator-plugin/profiles/registry.json`

**Project Type Profile 的精确形状**

```json
{
  "schema_version": "1.0",
  "project_type_id": "web-product",
  "child_skill_id": "web-product-incubator",
  "stages": ["P0", "P1", "P2", "P3", "P4", "P5", "P6"],
  "subflows": [],
  "evidence_levels": ["E0", "E1", "E2", "E3", "E4", "E5"],
  "human_validation_default": "UNSET"
}
```

**Registry Project Type 条目的精确形状**

```json
{
  "id": "web-product",
  "child_skill_id": "web-product-incubator",
  "host_profile_requirement": "FORBIDDEN",
  "profile_path": "profiles/project-types/web-product.json",
  "workflow_module": "src/domains/web/workflow.mjs"
}
```

对应 `child_skills` 条目为 `web-product-incubator → skills/web-product-incubator/SKILL.md`；不得新增 Web `host_profiles` 条目。Route 与 Activation 的期望输出另为 `host_profile_id = null`，该字段不写入 Project Type Profile 或 Registry Project Type 条目。

**步骤**

- [ ] 写失败测试：Profile 使用现有 Project Type Profile Shape，不出现 Deployment、MCP 或 Browser Runtime 字段。
- [ ] 写失败测试：Registry 可加载 Web Skill/Profile/Workflow；Web Route 无 Host 成功，任何 Host 均返回 `HOST_PROFILE_FORBIDDEN`。
- [ ] 写失败测试：Registry 中不存在 Web Host Profile，Registry Schema 仍为 1.1。
- [ ] 写失败测试：缺失、不可读或逃逸 Plugin Root 的 Child Skill、Project Type Profile、Host Profile 与 Workflow 引用均使启动失败关闭；Existing Mod/Desktop 合法引用继续通过。
- [ ] 运行失败测试：

```powershell
node --test --test-isolation=none tests/unit/registry.test.mjs tests/unit/web-profile.test.mjs
```

- [ ] 新增最小 Profile 和 Registry 条目；在通用 Registry 加载路径中统一解析并验证所有引用留在 Plugin Root 且目标存在/可读，禁止 Web 专用分支；不改 State/Activation Schema。
- [ ] 重跑测试并通过。
- [ ] Commit：`feat(plugin): register web product project type`

### Task 3：编写 Web Child Skill 与 Router 边界

**Files**

- Create: `project-incubator-plugin/tests/contract/web-guidance.test.mjs`
- Create: `project-incubator-plugin/skills/web-product-incubator/SKILL.md`
- Modify: `project-incubator-plugin/skills/project-incubator-router/SKILL.md`
- Modify: `project-incubator-plugin/ARCHITECTURE.md`

**Child Skill 必须覆盖**

- P0–P6 每阶段目标、输入、产物、Completion Conditions 和失败路由；
- P4 `Usable Web Slice` 与 `Build Readiness` 两个 Checkpoint，且都不是 Stage；
- 每个 P4 Checkpoint 分别要求 Evidence Refs、Claim Scope、Known Limitations、Failure Routing 与独立 Gate Evaluation；只有两项均为 `REQUIREMENT_SATISFIED` 时才不阻止 P4→P5；
- P5 六类 Design Channel 及其 Claim 上限；
- P5 的 Build、Local Integration、Local Browser 和适用 Secondary Interface Requirement 必须分别得到 `REQUIREMENT_SATISFIED`，不能只出现 Channel 名称；
- Build、localhost、真实浏览器核心旅程的最低要求；
- 前端、后端、数据和适用外部依赖的绑定；
- MCP/REST/GraphQL/WebSocket/Webhook 等次级界面的同项目归属条件和独立 Evidence；
- 真实 MCP Client 的允许路径、未授权/越权拒绝、协议/业务失败、审计与副作用；
- P4 Creation Correction 复用普通 Context Mutation；
- Deployment 为 `DEFERRED_CAPABILITY`，不得声称 Production Ready。

**Router 必须覆盖**

- `web-product` 的适用条件：浏览器主界面 + 前端职责 + 后端职责 + 跨边界核心旅程；
- `NEW_PROJECT` 标准阶段 P0；`ADOPT_EXISTING` 可评估 P0–P6；
- Host 为 FORBIDDEN，不能创建 Browser/localhost/OS Host；
- 排除浏览器扩展、静态前端、纯后端、独立 MCP Service、CLI、SDK、库、移动、桌面和 Mod；
- 绑定在 Web 后端上的 MCP 不改变 Project Type；是否独立只触发 Maker Review，不自动迁移。

**步骤**

- [ ] 先写文案契约测试，逐条绑定上述稳定术语、逐项 `REQUIREMENT_SATISFIED` 条件、阻断语义与否定边界。
- [ ] 运行并确认失败：

```powershell
node --test --test-isolation=none tests/contract/web-guidance.test.mjs
```

- [ ] 新增 Web Child Skill，并对 Router 做最小增量修改。
- [ ] 更新 Plugin `ARCHITECTURE.md` 的当前组合、Registry/Host Requirement 和 Web 边界；不改写 Legacy 集成矩阵的既有语义。
- [ ] 验证 Router 不把 `web-product` 写成默认类型，也不执行激活。
- [ ] 重跑 Web 与 Desktop Guidance 测试。
- [ ] Commit：`feat(plugin): add web product incubation guidance`

### Task 4：覆盖 Route、Activation 与 Entry 集成

**Files**

- Create: `project-incubator-plugin/tests/integration/web-router-mcp.test.mjs`

**步骤**

- [ ] 写失败测试：`propose_route(web-product, null)` 返回 Web Child Skill 且 Host 为 null。
- [ ] 写失败测试：任意非空 Host 返回 `HOST_PROFILE_FORBIDDEN`；未知类型仍返回 `PROJECT_TYPE_NOT_FOUND`。
- [ ] 写失败测试：`prepare_activation` 对 NEW/P0、ADOPT/P0–P6 的合法/非法矩阵。
- [ ] 写失败测试：`scope_digest` 覆盖完整 Entry；Prepare 后输入漂移导致 Initialize 失败关闭。
- [ ] 写失败测试：激活后 Entry 不可变；State 1.0 兼容行为不变。
- [ ] 写失败测试：Receipt、Product Decision Authorization 与 Read-back 使用既有机制。
- [ ] 运行测试；若失败仅因 Registry/Workflow 未接线，使用现有配置路径修复。若必须改 Tool Shape 或 Core Schema，停止并登记 `DESIGN_GAP`。
- [ ] 通过：

```powershell
node --test --test-isolation=none tests/integration/web-router-mcp.test.mjs
```

- [ ] Commit：`test(plugin): cover web route and activation contract`

### Task 5：建立端到端流程与结论上限保护

**Files**

- Create: `project-incubator-plugin/tests/e2e/web-product-flow.test.mjs`
- Modify: `project-incubator-plugin/tests/contract/legacy-invariants.test.mjs`

**步骤**

- [ ] 写 E2E：Web Route → Prepare → Maker 授权事件 → Initialize → Receipt → P0→P1 → Read-back。
- [ ] 写 E2E：ADOPT_EXISTING 从代表性中后期阶段激活，并保持 Entry 不可变。
- [ ] 写否定测试：Build-only、localhost-only、Browser-only、Secondary-interface-only 都不能被 Guidance 表述为完整 P5。
- [ ] 在 Contract content tests 中证明 Child Skill 要求 Agent/Gate 仅在 P4 两项 Gate、P5 各项必需/适用 Requirement 分别满足后声明 Completion；Runtime E2E 只证明 `completion_satisfied = false` 会阻止 Transition、`true` 仍需正常授权提交，且 Kernel 不从具体 Gate Result 自动推导 Completion 或修改状态。
- [ ] 写否定测试：P4 Checkpoint、Validation Channel、MCP 与 Deployment 不进入 Runtime Stage/Schema。
- [ ] 扩展受保护摘要：Mod/Sims 4 和 Desktop/Windows 领域资产保持 byte-for-byte 不变；Router/Manifest 等明确允许修改的聚合文件不锁摘要。
- [ ] 运行：

```powershell
node --test --test-isolation=none tests/e2e/web-product-flow.test.mjs tests/contract/legacy-invariants.test.mjs
```

- [ ] Commit：`test(plugin): close web product end-to-end flow`

### Task 6：更新 Candidate 身份与发现信息

**Files**

- Modify: `project-incubator-plugin/tests/contract/desktop-guidance.test.mjs`
- Create: `project-incubator-plugin/tests/contract/plugin-manifest.test.mjs`
- Modify: `project-incubator-plugin/tests/integration/mcp-handshake.test.mjs`
- Modify: `project-incubator-plugin/tests/e2e/desktop-product-flow.test.mjs`
- Modify: `project-incubator-plugin/.codex-plugin/plugin.json`
- Modify: `project-incubator-plugin/package.json`
- Modify: `project-incubator-plugin/package-lock.json`

**步骤**

- [ ] 把候选身份断言从 Desktop 专用测试移入通用 `plugin-manifest.test.mjs`，再要求 Package `0.3.0`、Manifest `0.3.0+codex.<timestamp>`，并要求能力列表/长描述同时包含 Mod、Desktop、Web。
- [ ] 更新 MCP Server Version 期望值。
- [ ] 更新 Desktop E2E 中“新激活项目读取当前 Package Version”的断言为 `0.3.0`；保留 `desktop-router-mcp.test.mjs` 等用于兼容旧激活记录的 `0.2.0` fixtures，不做全局替换。
- [ ] 运行并确认版本测试失败。
- [ ] 更新 Package、Lock 与 Manifest；不得把 Web 描述成已部署能力。
- [ ] 运行 Guidance、Handshake 与全量 Plugin 测试。
- [ ] Commit：`chore(plugin): identify web product candidate`

### Task 7：全量回归、候选包与验收交接

**Files**

- Create: `project-incubator-plugin/scripts/verify-candidate.mjs`
- Create: `project-incubator-plugin/tests/integration/candidate-package.test.mjs`
- Modify after evidence exists: `project-incubator-plugin/ACCEPTANCE_TEST_LOG.md`

**Candidate Verifier 接口**

```powershell
node scripts/verify-candidate.mjs --structure-only <candidate-root>
node scripts/verify-candidate.mjs --full <candidate-root> <temporary-managed-project-root>
```

两种模式都只从 `<candidate-root>` 解析文件，并输出固定 JSON。`--structure-only` 验证白名单、版本、Registry、Web Profile/Skill/Workflow 路径与聚合 SHA-256；`--full` 在 Candidate 已执行 `npm ci --omit=dev` 后，再完成真实 MCP 启动、三种 Route、Web Host Forbidden、最小 Web Activation、Receipt Read-back。聚合哈希按相对路径排序，对除 `node_modules/` 外每个 Candidate 文件计算 SHA-256，再对规范化的 `relative-path:file-hash` 清单计算最终 SHA-256。

**步骤**

- [ ] 先写 `candidate-package.test.mjs`：打包到系统临时目录，验证 `--structure-only` 的固定 JSON、来源路径、Profile/Skill/Workflow、禁止内容和稳定聚合哈希；确认缺文件与源码回退均失败关闭。
- [ ] 运行测试并确认 verifier 尚不存在而失败。
- [ ] 实现 `verify-candidate.mjs`；测试通过后 Commit：`test(plugin): add candidate verification harness`。
- [ ] 执行 `SPECS/IMPLEMENTATION/WEB_PRODUCT_INCUBATOR_ACCEPTANCE_TEST_PLAN.md` 的自动化阶段 A–F。
- [ ] 构建仓库外 Candidate，执行全新生产依赖安装和加载烟雾测试。
- [ ] 在 Candidate 路径内验证 Web Registry、Profile、Child Skill 与 Workflow 均存在、可读且相互引用正确。
- [ ] 使用同一个仓库外已安装 Candidate 驱动首个真实已有 Web 项目的 `ADOPT_EXISTING` Field Validation，并绑定 Candidate version、hash 与安装路径。
- [ ] 若该项目包含 MCP 或其他次级界面，执行独立真实 Client 验证；若不包含，记录不适用理由。
- [ ] 把命令、版本、Revision、Artifact、浏览器、localhost 端点、观察结果、限制和 Evidence 路径写入 Acceptance Log。
- [ ] 只有 Acceptance Exit Criteria 全部满足后，Commit：`test(plugin): accept web product candidate`

## 5. Review Focus

审阅本计划时重点确认：

1. 是否只通过配置、领域 evaluator 和 Skill 扩展，而没有为 Web 分叉 Kernel；
2. `FORBIDDEN` Host 是否贯穿 Registry、Route、Activation 和测试；
3. 真实浏览器旅程与真实次级 Client Evidence 是否彼此独立；
4. P4 Checkpoint、P5 Channel、MCP 与 Deployment 是否都没有进入 Core Stage/Schema；
5. 已有项目接管是否覆盖 P0–P6，而不是只测新项目；
6. 是否保留 Desktop、Mod、V1.1 RC 和历史基线的兼容边界；
7. 是否在 Candidate 之外安排了真实已有 Web 项目的现场验证。

## 6. 完成定义

只有以下条件全部成立，才能声明 V1.2 Web Product 实现完成：

- Tasks 1–7 均有实际提交和验证证据；
- 全量 Plugin、Legacy、Mod、Desktop 回归通过；
- Candidate 能在仓库外安装并从 Candidate 路径加载 Web Registry/Profile/Skill/Workflow；
- 一个真实已有 Web 项目完成接管、Build、localhost 和真实浏览器核心旅程验证；
- 真实项目的 Activation Read-back 绑定同一 Candidate hash，且 `plugin_version = 0.3.0`；
- 适用次级界面有独立真实 Client Evidence；
- 没有 Deployment 或 Production Ready 越界结论；
- Acceptance Test Plan 的全部 Exit Criteria 通过；
- Maker 审阅验收证据后再决定是否发布和归档。

## 7. Maker Approval

Maker 于 2026-10-14 批准本计划与 `WEB_PRODUCT_INCUBATOR_ACCEPTANCE_TEST_PLAN.md`，并要求：存在依赖关系的任务串行实施，没有依赖关系的任务并行实施。

本批准授权 Tasks 1–7 的实现与验收，不授权超出已批准 Product Boundary、Deployment Boundary、Core Schema、Tool Shape 或 Runtime Invariant 的变化；发现此类变化时仍须按 Change Control 停止受影响部分。

