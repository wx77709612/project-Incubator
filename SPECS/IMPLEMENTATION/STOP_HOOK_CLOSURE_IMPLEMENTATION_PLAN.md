# Stop Hook 续轮闭合修复实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复宿主自动续轮未触发 `UserPromptSubmit` 时 Stop Hook 因精确 turn marker 缺失而误阻断的问题，同时保持状态变更轮次失败关闭。

**Architecture:** 保留精确 marker 为正常路径；只在精确 marker 返回 `ENOENT` 时查找最近的同 project、同 session 有效基线。兼容路径仅在 baseline revision 与 receipt ID 都等于当前已验证 Snapshot 时放行，因此只能证明零状态变化，不能闭合状态变更。

**Tech Stack:** Node.js >= 24、`node:test`、现有 Project Incubator Hook 与 State Store API。

**Spec:** `SPECS/DESIGN/KERNEL_ALIGNMENT_DESIGN.md` → `SPECS/CONTRACTS/KERNEL_ALIGNMENT_CONTRACT.md` → `SPECS/RUNTIME/KERNEL_ALIGNMENT_RUNTIME_SPEC.md`

## Global Constraints

- 不补造缺失 marker，不修改 `F:/projects/Player_Needs_Hunter/.project-incubator/` 中三个权威 JSON。
- 不跳过或降级 `verifyLatestReceipt`、revision、state hash、Receipt ID 与最终报告校验。
- 只修改 Hook 闭合实现、相关测试、活动规格与验收记录；不改变授权、Schema、MCP Tool 或领域 Workflow。
- 保留正常轮次、Bootstrap、受控状态变更与 `stop_hook_active` 防循环行为。
- 所有实现按 TDD 进行；先观察 marker 缺失回归测试因 ENOENT 阻断而失败，再写最小修复。

## Review Focus

- 其他 session 的 marker 不能给当前续轮提供基线。
- 同 session 但 revision 已变化时必须阻断，即使 Receipt 本身有效。
- 同 revision 但 receipt ID 不一致时必须阻断。
- 精确 marker 存在时不得被较新的无关 marker 改变现有闭合语义。
- 损坏或读取竞态中的 marker 不能导致未验证放行。

---

### Task 1: marker 缺失回归与最小修复

**Files:**
- Modify: `project-incubator-plugin/tests/integration/hooks.test.mjs`
- Modify: `project-incubator-plugin/hooks/stop.mjs`

**Interfaces:**
- Consumes: `turnMarkerPath(runtimeDataRoot, projectId, sessionId, turnId)`、`readProjectSnapshot(root)`、`verifyLatestReceipt(root)`。
- Produces: `handleStop(event, options)` 对宿主续轮的保守零变更闭合行为；不新增公开 API。

- [x] **Step 1: 写入失败测试**

  覆盖：正常精确 marker；精确 marker 缺失且同 session 基线完全相同；marker 缺失但无同 session 基线；marker 缺失且 revision 已变化；marker 缺失且 receipt ID 不一致；受控状态变更仍要求当前 Receipt ID。

- [x] **Step 2: 运行定向测试并确认 RED**

  Run: `node --test --test-isolation=none tests/integration/hooks.test.mjs`

  Expected: 新增“同 session 零变化续轮”用例因当前实现返回 ENOENT block 而失败；既有用例保持通过。

- [x] **Step 3: 实现最小兼容读取**

  仅捕获精确 marker 的 `ENOENT`；枚举并解析 turn marker，选择最新的同 project/session 有效基线。兼容路径要求 revision 与 receipt ID 双重相等，否则返回稳定闭合失败原因。其他读取错误继续失败关闭。

- [x] **Step 4: 运行定向测试并确认 GREEN**

  Run: `node --test --test-isolation=none tests/integration/hooks.test.mjs`

  Expected: 全部通过，包含正常、无状态变更、受控状态变更与 marker 缺失矩阵。

### Task 2: 全量验证与受保护资产核对

**Files:**
- Modify: `SPECS/IMPLEMENTATION/STOP_HOOK_CLOSURE_IMPLEMENTATION_PLAN.md`
- Modify: `SPECS/IMPLEMENTATION/STOP_HOOK_CLOSURE_ACCEPTANCE_TEST_PLAN.md`
- Modify: `SPECS/README.md`

**Interfaces:**
- Consumes: Task 1 的 Hook 行为与测试。
- Produces: 可重放的测试结果、活动规格状态与真实项目零修改证明。

- [x] **Step 1: 运行 Plugin 全量测试**

  Run: `npm test`

  Expected: `399 + 新增用例` 全部通过，0 failures。

- [x] **Step 2: 检查源码与活动规格**

  Run: `git diff --check`，并扫描活动规格不得引用 `_V*` 作为运行时来源。

  Expected: 无 whitespace error；Design → Contract → Runtime → Plan/Acceptance 可追踪。

- [x] **Step 3: 核对真实项目保护资产**

  比较修复前后 `activation.json`、`state.json`、`latest-receipt.json` 的 SHA-256，并确认报错中的缺失 marker 仍不存在。

  Expected: 三个哈希逐字节不变，缺失 marker 未被创建。

- [x] **Step 4: 更新实际结果**

  将命令、数量、限制和旧轮次安全处理写入验收计划与索引；未完成候选打包、正式安装或新宿主重放时不得声称已发布或已安装。

## Maker Approval

Maker 于 2026-10-31 明确同意“同 project、同 session 最近 marker 的 revision 与 receipt ID 双重一致才放行”的保守方案，并重申不得补造 marker、修改真实项目权威 JSON 或跳过 Receipt/revision 校验。

## 实际完成记录

2026-10-31：Task 1–2 已完成。定向 Hook 测试先得到 10 pass / 4 expected failures，最小修复后为 14/14；Plugin 全量回归为 403/403。使用原报错的 session/turn 对 `Player_Needs_Hunter` 只读重放返回 `continue: true`；修复前后三个权威 JSON 的 SHA-256 完全一致，缺失 marker 仍不存在，项目 Git 状态为空。`git diff --check` 与活动引用检查通过。

上述记录对应 Task 1–2 的源码验收时点；后续分发由下列 Task 3 承接。

### Task 3: 候选打包、正式安装与恢复使用

**Files:**
- Modify: `project-incubator-plugin/.codex-plugin/plugin.json`
- Modify: `SPECS/IMPLEMENTATION/STOP_HOOK_CLOSURE_IMPLEMENTATION_PLAN.md`
- Modify: `SPECS/IMPLEMENTATION/STOP_HOOK_CLOSURE_ACCEPTANCE_TEST_PLAN.md`
- Modify: `SPECS/README.md`

**Interfaces:**
- Consumes: 已通过源码验收的 Stop Hook 修复、现有 Candidate Packager/Verifier、personal marketplace 正式安装机制。
- Produces: 新版本化候选、候选 Structure/Full 证据、正式安装结果与新进程加载验证。

- [x] **Step 1: 更新版本并重新验证源码**

  将 Manifest 更新为新的 `0.3.0+codex.<timestamp>` 构建号；Package/Lock 继续保持兼容版本 `0.3.0`。运行 Plugin 全量测试与 `git diff --check`。

- [x] **Step 2: 构建并验证仓库外候选**

  在确认全新目标目录不存在后，以白名单 Packager 生成版本化候选；执行 `npm ci --omit=dev`、`verify-candidate --structure-only` 与 `--full`。记录聚合哈希且要求 `source_fallback_detected=false`。

- [x] **Step 3: 通过 personal marketplace 正式安装**

  备份 marketplace 配置；将 source 精确切换到新版本化候选；执行 `codex plugin add project-incubator-plugin@personal --json`。禁止直接修改安装缓存。

- [x] **Step 4: 安装后与真实项目保护验证**

  核对 `codex plugin list`、实际加载路径与安装目录聚合哈希；用新安装路径启动独立 Node 进程重放原缺陷闭合，并确认 `Player_Needs_Hunter` 三个权威 JSON 哈希及缺失 marker 仍不变。若当前聊天不能热加载新版，则明确要求新开聊天后恢复工作。

## Task 3 Maker Approval

Maker 于 2026-10-31 要求“另外更新并打包，我要在 Player Needs Hunter 中恢复使用”，授权上述候选构建、personal marketplace source 更新与正式安装；该授权不包含修改 Managed Project 权威状态或补造历史 marker。

## Task 3 实际完成记录

2026-10-31：Manifest 更新为 `0.3.0+codex.20261031145522`，Package/Lock 保持 `0.3.0`；源码全量测试为 403/403。仓库外候选与正式安装目录的 `SHA-256-AGGREGATE-V1` 均为 `920569dc52ce8087b29839806e632d2b1dfeceeb4919e4e21243688da56fd0a2`，Structure/Full 均通过且 `source_fallback_detected=false`。`npm ci --omit=dev` 成功，当前审计数据库报告 3 个 moderate、3 个 high；未执行自动依赖升级。

personal marketplace 原文件已备份到 `C:/Users/Xenia_Woo/.codex/backups/stop-hook-closure/0.3.0+codex.20261031145522/marketplace.json`，原哈希为 `765f23bd2dc769748432b0c71d02b1c47c131ca47c3fe01146d9bdfc04bf1158`。正式安装返回新路径 `C:/Users/Xenia_Woo/.codex/plugins/cache/personal/project-incubator-plugin/0.3.0+codex.20261031145522`；源码、候选与安装目录的 `hooks/stop.mjs` SHA-256 均为 `bbbc89d267914b66932c4bfbb99ed79b11403a593ec3a125b2b564d59a3a6190`。

从新安装路径启动独立 Node 进程，使用原缺陷的 project/session/turn 和实际 Runtime Data 目录只读重放，返回 `{ "continue": true }`。重放后 `Player_Needs_Hunter` 三个权威 JSON 哈希仍逐字节不变，指定缺失 marker 仍不存在，项目 Git 状态为空。当前已存在的聊天不承诺热加载新插件；在 `Player_Needs_Hunter` 新开聊天后由宿主加载新版本。
