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

本任务未构建候选、未更新 marketplace source、未正式安装新版本，也未声称当前宿主已热加载源码修复；这些属于后续分发步骤。
