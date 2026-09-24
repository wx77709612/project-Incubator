# Project Incubator V1.1 Runtime Acceptance Test Plan

## 1. 文档状态

| 字段 | 值 |
| --- | --- |
| Target Version | V1.1 |
| Status | PASSED / RELEASE REVIEW REQUIRED |
| Approved By | Maker, 2026-09-23 |
| Execution Result | PASSED，2026-09-24；A01–E07 共 36 项通过 |
| Previous Baseline | `SPECS/_V1.0/IMPLEMENTATION/LAYER2_RUNTIME_ACCEPTANCE_TEST_PLAN.md` |
| Implementation Plan | `SPECS/IMPLEMENTATION/IMPLEMENTATION_PLAN.md` |

## 2. 目标

证明 V1.1 新能力按批准边界运行，同时 V1.0 正常路径、Authority、Phase、Gate 和 Context Source of Truth 不回归。

## 3. 执行原则

- 每个 Stage 可以独立运行；
- 测试只使用公开 Contract 和 Runtime 入口；
- Maker 语义判断通过明确 Fixture 表示，不由测试代码伪造 Runtime 决策；
- 所有临时文件创建在对应 Stage 的 `.tmp_*` 下并在测试结束后清理；
- Stage E 同时执行 V1.0 与 V1.1 全量回归。

## 4. Stage A — Evidence Model Acceptance

| ID | Scenario | Expected Result |
| --- | --- | --- |
| A01 | E2 Evidence 支持局部机制 Claim | Gate 可以满足局部 Claim |
| A02 | E2 Evidence 声称完整目标环境能力 | `REQUIREMENT_UNSATISFIED` / `CLAIM_EXCEEDS_EVIDENCE` |
| A03 | E3 Evidence 声称代表性稳定 | 被拒绝 |
| A04 | Evidence Scope 小于 Claim Scope | `EVIDENCE_INSUFFICIENT` |
| A05 | Confidence 因反证降低 | 降级被持久化且不改变 Maker Decision |
| A06 | Structural 与 Semantic Drift | Script 只产生 Structural，Semantic 由 Agent Fixture 提供 |

通过标准：A01–A06 全部通过。

## 5. Stage B — Creation Correction Acceptance

| ID | Scenario | Expected Result |
| --- | --- | --- |
| B01 | 同 Signature 第 1 次失败 | `NO_CORRECTION` |
| B02 | 连续第 2 次失败 | `MODEL_REVIEW_ADVISORY`，Runtime 仍 `EXECUTING` |
| B03 | 连续第 3 次失败 | `P4_CORRECTION_REQUIRED`，Runtime `SUSPENDED` |
| B04 | 合法局部 Correction Action | P4 内以 `CORRECTION_ACTIVE` 恢复 |
| B05 | Impact 触及 Maker Scope | `MAKER_SCOPE_REVIEW_REQUIRED` / `WAITING_FOR_MAKER` |
| B06 | 非 P4 Correction Request | Contract Violation，Phase 不变 |
| B07 | Candidate Model Version 更新 | 新计数序列从 0 开始，旧 Evidence 保留 |
| B08 | Correction Result 试图产生 Transition | 被拒绝 |

通过标准：B01–B08 全部通过，`PROJECT_STATE.md` Current Phase 始终为 P4。

## 6. Stage C — Context, Decision and Baseline Acceptance

| ID | Scenario | Expected Result |
| --- | --- | --- |
| C01 | Assumption 由 Evidence 判定失效 | 无需伪造 Maker Decision Authorization |
| C02 | Product Decision Supersession | 必须具有 Maker Authorization |
| C03 | Decision Archive 成功 | History 可读，Active View 只保留当前决策与引用 |
| C04 | Archive 中途失败 | 原 Active View 完整保留 |
| C05 | Baseline Pass → Fail | Baseline `REGRESSED`、Gate `ACTION_BLOCKED` |
| C06 | Optional Context 缺失 | 未启用 V1.1 的 legacy route 正常执行 |
| C07 | Optional Context 覆盖 Core Authority | `BOUNDARY_VIOLATION` |

通过标准：C01–C07 全部通过，无半持久化状态。

## 7. Stage D — Opaque Capability Extension Acceptance

| ID | Scenario | Expected Result |
| --- | --- | --- |
| D01 | 任一维度 HIGH | 产生 Extension Recommendation，不自动启用 |
| D02 | 两项 ELEVATED | 产生 Recommendation |
| D03 | Maker 未确认成本边界 | 不创建 Spiral Record |
| D04 | Maker 确认启用 | 创建 Optional Spiral Record，不修改 Phase |
| D05 | Profile 配置 3/4 阈值 | Definition Resolution 失败 |
| D06 | Profile 配置 1/2 阈值 | 接受更严格阈值 |
| D07 | 人工预算耗尽且无新 Evidence | 不再要求重复同一测试 |
| D08 | 透明 Capability | 不强制创建 Extension Artifact |

通过标准：D01–D08 全部通过。

## 8. Stage E — Regression and Package Acceptance

| ID | Scenario | Expected Result |
| --- | --- | --- |
| E01 | 完整现有 `TESTS` | 0 failure |
| E02 | V1.0 Acceptance Stage A–E | 0 failure |
| E03 | Legacy Runtime Request | 与 V1.0 Phase / Result 语义一致 |
| E04 | Definition IDs | 保持稳定，version 更新为 V1.1 projection |
| E05 | Active source paths | 全部存在且不指向 `_V*` |
| E06 | Package isolation | 不包含历史 Specs、测试临时目录或缓存 |
| E07 | Runtime invariant scan | 无新增 Phase、Transition、Gate Type、Script Purpose、Runtime State |

通过标准：E01–E07 全部通过。

## 9. Human Validation Protocol Acceptance

本项验证协议结构，不伪造真实外部环境：

- 每项 Maker Action 有明确场景、步骤、预期观察和最小 Evidence；
- 有批次、最大重复次数和停止条件；
- 相同测试达到预算上限且无新区分 Evidence 后停止；
- Maker Observation 作为 Evidence Input，不自动成为技术根因；
- Agent 负责从 Observation 提取 Hypothesis 与后续验证。

## 10. Release Blocking Conditions

任一情况阻止 V1.1 Release：

- V1.0 回归失败；
- P4 Correction 改变 Current Phase；
- Script 产生语义决策或 Maker Authorization；
- Decision Archive 出现半持久化；
- Extension 未经 Maker 确认自动启用；
- E0–E2 被接受为完整目标环境能力；
- Package 或活动配置加载 `_V*`；
- Installed Skill Package 依赖 Implementation Repository 才能加载 Runtime 或 Script；
- 任一 Acceptance ID 未通过或无实际证据。

## 11. 实际验收结果

| Stage | Result |
| --- | --- |
| Stage A — Evidence Model | 6 / 6 通过 |
| Stage B — Creation Correction | 8 / 8 通过 |
| Stage C — Context, Decision and Baseline | 7 / 7 通过 |
| Stage D — Opaque Capability Extension | 8 / 8 通过 |
| Stage E — Regression and Package | 7 / 7 通过 |

补充回归证据：

- V1.0 Acceptance Stage A–E：40 / 40 通过；
- Unit、Integration、E2E、V1.0 Acceptance 与 V1.1 Acceptance 合并直接测试矩阵：170 / 170 通过；
- Stage E 另以独立进程重放现有 `TESTS` 与 V1.0 Acceptance，结果通过；
- 原计划覆盖范围内未发现 Release Blocking Condition；
- 当前等待 Maker 审阅最终验收证据，尚未创建 V1.1 发布归档。

## 12. 验收后发现的 Packaging Gap

2026-09-24 在 Implementation Repository 之外直接运行当前全局 Skill 的确定性脚本时，实际得到：

```text
ModuleNotFoundError: No module named 'PROJECT_INCUBATOR'
```

该结果不推翻 A01–E07 对 Runtime Domain Behavior 的结论，但证明 E06 的 Package Isolation 只覆盖了仓库内打包排除规则，没有覆盖 Installed Skill 从无关工作目录独立执行的能力。

处理状态：

- 分类：Delivery Artifact / Installation Verification Gap；
- 严重性：Release Blocking；
- 当前设计：`SPECS/DESIGN/RC_PACKAGING_DESIGN.md`；
- 要求：建立自包含 RC、仓库外 Smoke Test 和 Installed Smoke Test；
- 在该 Gap 关闭前，不得将 V1.1 标记为 Release Ready。
