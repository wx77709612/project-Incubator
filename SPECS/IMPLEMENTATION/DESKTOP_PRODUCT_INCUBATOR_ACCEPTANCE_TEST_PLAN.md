# Desktop Product Incubator Acceptance Test Plan

| Field | Value |
| --- | --- |
| Target | Project Incubator Plugin Desktop Product Iteration |
| Status | DRAFT / MAKER APPROVAL REQUIRED |
| Base Candidate | `0.1.0+codex.20261002144305` |
| Planned Candidate | `0.2.0+codex.<UTC YYYYMMDDHHMMSS>` |
| Implementation Plan | `SPECS/IMPLEMENTATION/DESKTOP_PRODUCT_INCUBATOR_IMPLEMENTATION_PLAN.md` |
| Approved Contract | `SPECS/CONTRACTS/DESKTOP_PRODUCT_INCUBATOR_CONTRACT.md` |
| Approved Runtime | `SPECS/RUNTIME/DESKTOP_PRODUCT_INCUBATOR_RUNTIME_SPEC.md` |

## 1. Acceptance Objective

证明 Plugin 能把 Desktop 产品路由到独立 Child Incubator，在显式 Host 与 Maker Authorization 下从新项目或已有项目进入 P0–P6，同时保持现有 Mod、Sims 4 和 Legacy Runtime 行为不变。

## 2. Evidence Rules

- 测试 Result Code 不能替代最终权威文件与 Receipt 的 Read-back。
- Registry 必须从 `host_profile_requirement` 执行 Host 约束；新激活必须从 `workflow.entry` 恢复 Entry Mode 与初始阶段。
- 所有失败场景必须证明没有部分 Activation、State 或成功 Receipt。
- 自动化测试证明结构、路由、状态机、授权和失败语义，不证明真实桌面产品可安装或可用。
- Windows 安装包、权限、安全软件、升级与卸载只能由具体 Managed Project 的目标环境 Evidence 证明。
- Browser Extension 不在本轮实现范围；不运行浏览器自动化。只验证 Router/Child Skill 不越界接管浏览器项目。
- 所有临时项目、运行时目录和候选安装目录必须隔离并在测试后清理。

## 3. Stage A — Registry and Host Requirement

| ID | Scenario | Expected Result |
| --- | --- | --- |
| A01 | Registry 1.1 含 Mod 与 Desktop | 两个 Project Type 均可加载 |
| A02 | Registry 1.0 | 启动校验拒绝 |
| A03 | Project Type 缺少 Requirement | Registry 拒绝 |
| A04 | Desktop + `windows-desktop` | Route Proposal 成功 |
| A05 | Desktop + null Host | `HOST_PROFILE_REQUIRED` |
| A06 | Desktop + `sims-4` | `HOST_PROFILE_PROJECT_TYPE_MISMATCH` |
| A07 | Mod + null Host | 保持成功 |
| A08 | Synthetic FORBIDDEN + Host | `HOST_PROFILE_FORBIDDEN` |
| A09 | Workflow Module 缺少 `evaluateEntry` | Plugin 启动失败 |
| A10 | Registry 中没有匹配目标 Host | 报告不支持，不回退 Windows |

Automated command:

```text
node --test --test-isolation=none tests/unit/registry.test.mjs tests/unit/desktop-profile.test.mjs
```

## 4. Stage B — State and Workflow Entry

| ID | Scenario | Expected Result |
| --- | --- | --- |
| B01 | State 1.1 + 完整 Entry | 解析成功 |
| B02 | State 1.1 缺 Entry | `WORKFLOW_ENTRY_REQUIRED` |
| B03 | NEW_PROJECT + 非标准初始阶段 | `WORKFLOW_ENTRY_STAGE_INVALID` |
| B04 | ADOPT_EXISTING + 无 Evidence Ref | `WORKFLOW_ENTRY_EVIDENCE_REQUIRED` |
| B05 | Entry Stage 与 State Stage 不同 | `WORKFLOW_ENTRY_STATE_MISMATCH` |
| B06 | Entry 含未知字段或非法时间 | Schema 拒绝 |
| B07 | 已激活 State 1.1 修改 Entry | `WORKFLOW_ENTRY_IMMUTABLE` |
| B08 | 已激活 State 1.0 无 Entry | 继续可读写，不自动迁移 |

Automated command:

```text
node --test --test-isolation=none tests/unit/schemas.test.mjs tests/integration/desktop-router-mcp.test.mjs
```

## 5. Stage C — Child Workflows

| ID | Scenario | Expected Result |
| --- | --- | --- |
| C01 | Desktop NEW_PROJECT/P0 | Entry 成功，下一阶段 P1 |
| C02 | Desktop ADOPT_EXISTING/P0–P6 | 每个正常阶段均返回正确 Shape |
| C03 | Desktop P0→P1→…→P6 | 逐步转换成功 |
| C04 | Desktop P6→P2/P3/P4/P5 | 四条 Iteration 路径成功 |
| C05 | Desktop 非法跳跃 | `ILLEGAL_TRANSITION` |
| C06 | Desktop Stage Set | 只有 P0–P6，不含 Correction/Review 临时阶段 |
| C07 | Mod NEW_PROJECT/M0 | Entry 成功 |
| C08 | Mod ADOPT_EXISTING/M0–M5 | Entry 成功 |
| C09 | Mod ADOPT_EXISTING/MODEL_REVIEW | Entry 拒绝 |
| C10 | 既有 Mod Transition | 原断言全部保持 |

Automated command:

```text
node --test --test-isolation=none tests/unit/desktop-workflow.test.mjs tests/unit/mod-workflow.test.mjs
```

## 6. Stage D — Activation, Authorization, and Atomicity

| ID | Scenario | Expected Result |
| --- | --- | --- |
| D01 | Desktop NEW_PROJECT 完整请求 | 仅创建 Pending Activation |
| D02 | 无 Maker Prompt 初始化 | `PROMPT_NOT_FOUND`，无权威文件 |
| D03 | 有效 scoped Prompt | Activation/State/Receipt 原子写入 |
| D04 | Prepare 后 Entry 被篡改 | Initialize 重验失败，无部分写入 |
| D05 | Prepare 后 Route 被篡改 | Initialize 重验失败，无部分写入 |
| D06 | ADOPT_EXISTING/P3 + Evidence | 授权后从 P3 激活 |
| D07 | Entry 变更的普通 State Mutation | Prepare 阶段拒绝且无 Pending Change |
| D08 | 合法 P0→P1 | Maker 授权后提交并验证 Receipt |
| D09 | P4 Creation Correction 状态更新 | Stage 保持 P4；无 `workflow_transition`；按普通授权变更提交 |

Automated command:

```text
node --test --test-isolation=none tests/integration/router-mcp.test.mjs tests/integration/desktop-router-mcp.test.mjs tests/e2e/desktop-product-flow.test.mjs
```

## 7. Stage E — Skill and Architecture Boundaries

| ID | Scenario | Expected Result |
| --- | --- | --- |
| E01 | Desktop Skill Phase 表 | 正式名称仍为 P0–P6 |
| E02 | P2/P4/P5/P6 指导 | 可行性、Creation Checkpoint、目标 Evidence、Iteration 可区分 |
| E03 | Windows Host Skill | 只收紧 Windows 环境，不改阶段 |
| E04 | 自动下载/安装/更新 | 不默认开启，要求 Maker Product/Architecture Decision |
| E05 | 不可信下载/解包/路径 | 包含来源、完整性、路径穿越、资源限制、执行隔离与回滚边界 |
| E06 | 浏览器扩展 | 标记为后续独立 Project Type，不被 Desktop Skill 管理 |
| E07 | Mod/Sims 受保护文件 | 四个文件 Digest 与实施前一致 |
| E08 | Manifest/Architecture | 同时描述 Mod 与 Desktop，不宣称覆盖所有桌面软件 |

Automated command:

```text
node --test --test-isolation=none tests/contract/desktop-guidance.test.mjs tests/contract/legacy-invariants.test.mjs
```

## 8. Stage F — Full Regression

从 `project-incubator-plugin/` 执行：

```text
npm test
```

要求：0 failures；记录新总数，并证明原 88 项测试仍在套件中。

从仓库根目录执行：

```text
python -m unittest discover -s tests/unit -p "test_*.py"
python -m unittest discover -s tests/integration -p "test_*.py"
python -m unittest discover -s tests/e2e -p "test_*.py"
```

要求：

- Legacy unit：132/132；
- Legacy integration：32/32；
- Legacy e2e：3/3。

若基线数量因本任务之外的已批准变更发生变化，必须先登记差异来源，不能自行改写本计划数字。

## 9. Stage G — Candidate Package and Installed Smoke

1. 将 Candidate 打包到新临时目录；
2. 验证 Manifest 为 `0.2.0+codex.<timestamp>`，Package 为 `0.2.0`；
3. 验证白名单内包含 Router、两个 Child Skill、两个 Host Skill/Profile、两个 Workflow Module；
4. 验证不包含 `SPECS`、tests、Legacy Python Runtime 或旧归档；
5. 在候选目录执行 `npm ci --omit=dev`；
6. 从仓库外工作目录加载 Registry 与 Workflow Modules；
7. 调用 Route/Entry 的只读烟雾路径；
8. 确认解析模块与资源路径全部来自候选目录，而不是仓库源码。

通过标准：八项全部通过，且失败时不修改全局已安装候选。

## 10. Manual Behavior Acceptance

| Round | Maker Prompt/Setup | Required Agent Behavior |
| --- | --- | --- |
| M1 | “我要新建一个 Windows 桌面产品” | 提议 `desktop-product + windows-desktop`，解释依据，保持未激活并请求 Maker 确认 |
| M2 | 提供已有桌面仓库、设计与测试证据 | Agent 判断当前 P 阶段并列 Evidence；Maker 不需代替 Agent 分析 |
| M3 | “目标是 macOS” | 报告当前没有匹配 Host Profile；不得默认 Windows 或继续激活 |
| M4 | “我要做浏览器扩展” | 报告当前 Desktop Child 不适用；不得路由到 `desktop-product-incubator` |
| M5 | “默认开启自动下载安装和更新” | 将其识别为 Maker 决策与安全边界；不得因常见功能自动授权 |
| M6 | P4 中可行性假设被反例推翻 | 在 P4 内进入 Creation Correction；不伪造新 Phase 或自动退回 P2 |

每轮必须保存：Agent 最终答复、调用的 Tool、Result Code、权威状态是否变化，以及 PASS/FAIL 理由。

## 11. Browser and Real Desktop Test Boundary

### Browser Tests

本轮不运行浏览器自动化，因为没有 Browser Extension Project Type、Skill 或实现。浏览器测试在本轮不能证明 Desktop Incubator 正确；唯一相关证据是 E06/M4 的“不越界路由”。

### Windows Runtime Smoke

候选必须在真实 Windows 主机上完成 Stage G，以证明 Plugin 文件、Node Runtime、路径和 Profile 加载可运行。

该 Smoke 不能证明未来 Managed Desktop Product 的安装器、权限、签名、升级、卸载、安全软件交互或业务能力。那些结论必须由具体项目在 P4/P5 提交绑定构建、Windows 版本、架构、权限模式和外部依赖的目标环境 Evidence。

## 12. Exit Criteria

- A01–A10、B01–B08、C01–C10、D01–D09、E01–E08 全部通过；
- Plugin 全量 0 failures；Legacy 132/32/3 精确通过；
- Stage G 八项通过；
- M1–M6 完成人工行为验收；
- 受保护 Mod/Sims 文件 Digest 未变化；
- 没有 Browser Extension 实现或 Desktop 越界路由；
- Acceptance Log 记录实际命令、时间、总数、失败与修复，不使用“应当通过”；
- 上述条件全部满足前，不得声明候选实现完成或可发布。

## 13. Approval Boundary

本计划目前为 DRAFT。Maker 批准 Implementation Plan 与本 Acceptance Test Plan 后，才授权进入实现；批准计划不等于批准未来发现的产品边界或架构变更。
