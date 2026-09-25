# Context Mutation Orchestration Acceptance Test Plan

| Field | Value |
| --- | --- |
| Target | V1.1 RC Remediation / `1.1.0-rc.2` |
| Status | AUTOMATED PASSED / MANUAL ROUND 2R PENDING |
| Finding | `MULTI_CONTEXT_MUTATION_ORCHESTRATION_GAP` |
| Implementation Plan | `SPECS/IMPLEMENTATION/CONTEXT_MUTATION_ORCHESTRATION_IMPLEMENTATION_PLAN.md` |
| Manual Baseline | Round 2 FAIL；Round 2C PASS |

## 1. 验收目标

证明 RC 能阻止虚假 Maker Authorization、阻止多 Context 部分完成，并在有效授权下将 State、Plan 与 Capability Spiral Record 一次性闭合为同一状态。

## 2. 通用规则

- 每个 Stage 可独立运行；
- 自动化测试只能验证结构、引用、顺序、Scope、持久化和确定性 Closure；
- Maker 自然语言是否明确授权由 Agent 从实际 Maker 输入提取，测试使用显式 Fixture，不伪造技术语义；
- 所有失败注入必须检查文件最终内容，而不只检查 Result Code；
- 所有临时目录在测试结束后清理；
- Stage F 通过后仍不能替代 Round 2R 人工验收。

## 3. Stage A — Domain and Recipe

| ID | Scenario | Expected Result |
| --- | --- | --- |
| A01 | 合法 Extension Activation Recipe | Definition Resolution 成功 |
| A02 | 未知 Event Type | `EVENT_RECIPE_MISMATCH` |
| A03 | Required Target 重复 | Definition Resolution 失败 |
| A04 | PROJECT_STATE 不是最后目标 | Definition Resolution 失败 |
| A05 | 非法 Closure Operator | Definition Resolution 失败 |
| A06 | Runtime State Set 检查 | 仍只有原六种状态 |

通过标准：A01–A06 全部通过。

## 4. Stage B — Authorization Provenance

| ID | Scenario | Expected Result |
| --- | --- | --- |
| B01 | 只有 `source=MAKER, confirmed=true` | `AUTHORIZATION_REQUIRED` |
| B02 | 没有 Pending Request | `AUTHORIZATION_REQUIRED` |
| B03 | Request ID 不匹配 | `AUTHORIZATION_INVALID` |
| B04 | Source Message Ref 指向 Agent | `AUTHORIZATION_INVALID` |
| B05 | Maker Excerpt 为空或 Digest 不匹配 | `AUTHORIZATION_INVALID` |
| B06 | Capability / Event 不匹配 | `AUTHORIZATION_SCOPE_MISMATCH` |
| B07 | Authorized Scope 小于 Mutation Scope | `AUTHORIZATION_SCOPE_MISMATCH` |
| B08 | Authorized Targets 不覆盖全部目标 | `AUTHORIZATION_SCOPE_MISMATCH` |
| B09 | Request 已过期、拒绝或被替代 | `AUTHORIZATION_INVALID` |
| B10 | 完整、匹配、未过期的 Maker 授权 | Authorization Validation 通过 |

通过标准：B01–B10 全部通过；Round 2 原始语境不能进入 Active。

## 5. Stage C — Persistence and Rollback

| ID | Scenario | Expected Result |
| --- | --- | --- |
| C01 | 全部 Preflight 通过 | 写入尚未开始 |
| C02 | 任一 Preflight 失败 | 零文件变化 |
| C03 | Plan Commit 失败 | 已写 Optional Context 恢复 |
| C04 | State Commit 失败 | Plan 与 Optional Context 恢复 |
| C05 | 新建 Spiral 后失败 | Spiral 文件被删除并验证缺失 |
| C06 | Context Closure 失败 | Result=`ROLLED_BACK`，全部前镜像恢复 |
| C07 | Authorization Finalization 失败 | Request 回到 PENDING，Context 恢复 |
| C08 | Final Closure 失败 | Request 与 Context 均恢复 |
| C09 | Rollback 注入失败 | Result=`FAILED`，列出未恢复目标 |
| C10 | Commit 顺序 | PROJECT_STATE 最后 |

通过标准：C01–C10 全部通过；不存在部分激活。

## 6. Stage D — Runtime Routing and Recovery

| ID | Scenario | Expected Result |
| --- | --- | --- |
| D01 | Authorization Pending | Runtime=`WAITING_FOR_MAKER` |
| D02 | Verified | Runtime=`COMPLETED` |
| D03 | Rejected / Rolled Back / Suspended | Runtime=`SUSPENDED` |
| D04 | Rollback Failed | Runtime=`FAILED` |
| D05 | Mutation Set Route | 不调用 legacy per-file executor 或 Workflow Transition |
| D06 | Set 与独立 Intents 目标重叠 | 请求被拒绝 |
| D07 | 重放已 Verified Idempotency Key | 返回原结果，不重复写入 |
| D08 | 相同 Key 不同 Payload | `IDEMPOTENCY_CONFLICT` |
| D09 | 恢复 `COMMITTING` | 完成 Closure 或整体回滚 |
| D10 | 恢复 `FINALIZING_AUTHORIZATION` | 完成 Final Closure 或恢复 Request/Context |

通过标准：D01–D10 全部通过，Runtime State Enum 未增加。

## 7. Stage E — Skill and Template Behavior

| ID | Scenario | Expected Result |
| --- | --- | --- |
| E01 | Agent 收到“评估并提出启用请求” | 只形成 Proposed / Pending，不声称授权 |
| E02 | Pending Extension | State 与 Plan 一致；Spiral 缺失或 `INACTIVE_DRAFT` |
| E03 | 明确 Maker 授权 | Agent 引用原文、Request ID、Scope 与 Targets |
| E04 | Completion Report | 包含 Event、Authorization Basis、Targets、Closure、Phase |
| E05 | 透明 Capability | 不创建 Mutation Set 或 Extension 字段 |
| E06 | 单文件非受保护 Mutation | 继续走旧轻量路径 |

通过标准：E01–E06 全部通过。

## 8. Stage F — End-to-End RC Acceptance

| ID | Scenario | Expected Result |
| --- | --- | --- |
| F01 | 自动重放 Round 2 原始输入 | 不产生 Active，不消耗人工预算 |
| F02 | 重放 Round 2C | State / Plan 为 Pending，Phase=P2 |
| F03 | 合法 Maker Activation | State / Plan / Spiral 全部 Active |
| F04 | Activation 后检查 | Phase 仍 P2，预算仍 0/4 |
| F05 | Activation 中间失败 | 所有文件恢复到 Round 2C |
| F06 | RC Package Build | Manifest、Identity、唯一入口、自包含通过 |
| F07 | Installed RC 外部目录运行 | 不依赖 Implementation Repository |
| F08 | Stable V1.0 Digest | 安装前后不变 |
| F09 | Full Regression | 既有 Unit / Integration / E2E / V1.0 / V1.1 / Layer2 全部通过 |

通过标准：F01–F09 全部通过。

### 自动化执行结果

- Stage A：6 / 6；Stage B：8 / 8；Stage C：7 / 7；Stage D：8 / 8；Stage E：8 / 8；Stage F：2 / 2。
- 仓库 Unit / Integration / E2E：158 / 158；Layer 2：40 / 40。
- RC 构建与安装后验证各 9 / 9；Installed Runtime 仓库外导入通过。
- Stable V1.0 安装前后摘要一致。
- 本结果只关闭自动化与打包部分；Manual Round 2R 保持 Pending。

## 9. Manual Round 2R

前置条件：

- 新 RC 已安装；
- `ProjectSimulator` 保持 Round 2C 状态；
- State 与 Plan 为 `PENDING_MAKER_AUTHORIZATION`；
- Spiral Record 为 `DRAFT / INACTIVE`；
- Phase 为 P2；
- 人工预算为 0/4。

Maker 对现有 Pending Request 明确授权后，检查：

1. Agent 没有重新解释或扩大授权范围；
2. Agent 报告匹配的 Authorization Request Ref；
3. State、Plan、Spiral Record 均为 `ACTIVE`；
4. Capability ID、Scope 和 Evidence Level 一致；
5. Phase 保持 P2；
6. 人工预算保持 0/4；
7. 完成报告包含 Mutation Set 与 Closure Result；
8. 不开始实验、实现或 API 选型。

任一项失败，Round 2R 为 FAIL，原 Round 3 继续暂停。

## 10. Release Blocking Conditions

- 任意路径允许布尔授权直接激活 Extension；
- 任意失败留下 State、Plan、Spiral 的状态分裂；
- PROJECT_STATE 不是最后提交目标；
- Rollback Failure 被报告为普通 `SUSPENDED` 或成功；
- Activation 改变 Phase、消耗人工预算或授权实验/实现；
- V1.0 稳定包被覆盖或摘要变化；
- Installed RC 依赖 Implementation Repository；
- Manual Round 2R 未通过。

## 11. 完成记录格式

```text
Stage:
Result: PASS | FAIL | INCONCLUSIVE
Tests Executed:
Observed Behavior:
Files Verified:
Evidence:
Failure Signal: 无 | ...
Notes:
```
