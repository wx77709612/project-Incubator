# Project Incubator Specifications

## 当前研发状态

| 字段 | 值 |
| --- | --- |
| 当前研发版本 | V1.2 Plugin Web Product Incubator（独立分支） |
| 上一发布基线 | `SPECS/_V1.0/` |
| 当前阶段 | Architecture Approved / Project Type Design Draft |
| 产品实现状态 | V1.2 尚未授权实现；V1.1 RC 状态保持不变，继续等待 Maker 执行 Round 2R |
| 当前入口 | 本文件 |

## 版本管理规则

`SPECS/` 的直接层级目录保存当前研发阶段最新文档，文件名不携带版本号。`SPECS/_V*` 保存已发布版本的只读历史快照。

历史归档不参与当前 Source of Truth 解析、产品配置引用或默认上下文加载。需要进行回归、迁移和历史追踪时，才显式读取对应归档。

## Plugin 后续架构提案

| Layer | Document | Status | 说明 |
| --- | --- | --- | --- |
| Architecture | `ARCHITECTURE/DESKTOP_PRODUCT_INCUBATOR_CHANGE_PROPOSAL.md` | APPROVED / IMPLEMENTED | 新增 `desktop-product` 与 `desktop-product-incubator`；Workflow Entry 与显式 Host Requirement 已进入 0.2.0 候选 |
| Architecture | `ARCHITECTURE/WEB_PRODUCT_INCUBATOR_CHANGE_PROPOSAL.md` | APPROVED | V1.2 新增 `web-product` 与 `web-product-incubator`；Maker 于 2026-10-13 批准，Implementation Authorization 尚未授予 |

这些提案用于 Project Incubator Plugin 的版本化迭代，不改变 V1.1 RC 的人工验收状态。Desktop 提案已获批准并实施；Web Product 提案已获 Maker 书面批准，当前只授权 Architecture Decisions 与 Design Layer。Contract、Runtime、Implementation 与 Acceptance 必须分别按 Change Control 顺序推进。

## 当前文档状态

| Layer | Document | Status | 说明 |
| --- | --- | --- | --- |
| Architecture | `ARCHITECTURE/ARCHITECTURE_CHANGE_PROPOSAL.md` | APPROVED | V1.1 变更总规格；Maker 于 2026-09-23 批准 |
| Architecture | `ARCHITECTURE/DOCUMENT_ARCHITECTURE.md` | ACTIVE | 定义活动规格职责、层级、版本和加载规则，并登记 V1.2 Plugin Extension Track |
| Architecture | `ARCHITECTURE/ARCHITECTURE_DECISIONS.md` | ACTIVE | 保留 V1.0 Decision 001–006、V1.1 Decision 007–012，并登记 Plugin Decision 013–014 |
| Architecture | `ARCHITECTURE/CONTEXT_MUTATION_ORCHESTRATION_CHANGE_PROPOSAL.md` | APPROVED | Round 2 授权误判与多 Context 不闭合的 RC 修复提案；Maker 于 2026-09-24 批准 |
| Project Type Design | `PROJECT_TYPES/DESKTOP_PRODUCT_PROFILE.md` | APPROVED | 定义 P0–P6 Phase Profile、Workflow Entry、显式 Host Requirement、Creation Checkpoint、Evidence 与安全边界；Maker 于 2026-10-05 批准 |
| Project Type Design | `PROJECT_TYPES/WEB_PRODUCT_PROFILE.md` | DRAFT | 定义 Web Product Model、P0–P6 Profile、Build/localhost/Browser/MCP Evidence 与部署挂起边界；等待 Maker 审阅 |
| Design | `DESIGN/PROJECT_INCUBATOR_DESIGN.md` | APPROVED | V1.0 非冲突设计与 V1.1 Evidence-driven Evolution 总体关系 |
| Design | `DESIGN/EVIDENCE_MODEL_DESIGN.md` | APPROVED | V1.1 Core Evidence、Claim、Assumption、Baseline 与 Drift 模型 |
| Design | `DESIGN/WORKFLOW_DESIGN.md` | APPROVED | P4 Creation Correction 内部活动模型 |
| Design | `DESIGN/CONTEXT_MODEL_DESIGN.md` | APPROVED | Decision 活动视图与 Evidence Optional Context |
| Design | `DESIGN/GATE_DESIGN.md` | APPROVED | Evidence、Correction、Baseline 与 Drift 评估政策 |
| Design | `DESIGN/PHASE_ADVISORY_DESIGN.md` | APPROVED | Model Review、Regression、Drift 与 Extension Reason Code |
| Design | `DESIGN/RC_PACKAGING_DESIGN.md` | APPROVED / IMPLEMENTED / PACKAGING ACCEPTED | V1.1 RC 并行身份、自包含打包、安装烟雾测试与模拟验收隔离 |
| Design | `DESIGN/CONTEXT_MUTATION_ORCHESTRATION_DESIGN.md` | APPROVED | Mutation Set、Extension 生命周期、授权来源与 Closure Check 设计 |
| Extension | `EXTENSIONS/OPAQUE_CAPABILITY_EXTENSION.md` | APPROVED | Capability 级不透明性评估与产品点螺旋方法 |
| Contract | `CONTRACTS/CONTEXT_ACCESS_CONTRACT.md` | APPROVED | Decision 活动视图、Optional Evidence Context 与 Assumption Mutation |
| Contract | `CONTRACTS/WORKFLOW_CONTRACT.md` | APPROVED | P4 Correction Assessment、Result、Activity State 与 Resume Contract |
| Contract | `CONTRACTS/GATE_CONTRACT.md` | APPROVED | Evidence Input、Evaluation Rule 与 Reason Code |
| Contract | `CONTRACTS/SCRIPT_CONTRACT.md` | APPROVED | 确定性 Evidence、Failure Signature 与 Structural Drift |
| Contract | `CONTRACTS/CONTEXT_MUTATION_ORCHESTRATION_CONTRACT.md` | APPROVED | 多 Context Mutation、Authorization Provenance 与闭合结果 Contract |
| Contract | `CONTRACTS/DESKTOP_PRODUCT_INCUBATOR_CONTRACT.md` | APPROVED / IMPLEMENTED | 显式 Host Requirement、Workflow Entry、Desktop P0–P6 evaluator、Activation 与兼容契约已实现并通过自动化验收 |
| Runtime | `RUNTIME/SKILL_RUNTIME_SPEC.md` | APPROVED | V1.1 Evidence、Correction、Baseline、Drift 与 Extension 执行机制 |
| Runtime | `RUNTIME/CONTEXT_MUTATION_ORCHESTRATION_RUNTIME_SPEC.md` | APPROVED | Prepare、Stage、Commit、Read-back、Rollback 与恢复语义 |
| Runtime | `RUNTIME/DESKTOP_PRODUCT_INCUBATOR_RUNTIME_SPEC.md` | APPROVED / IMPLEMENTED | Entry/Host 双重校验、Desktop Workflow、失败恢复与验证义务已实现并通过自动化验收 |
| Implementation | `IMPLEMENTATION/IMPLEMENTATION_PLAN.md` | IMPLEMENTED / ACCEPTANCE PASSED | V1.1 Tasks 1–10 已完成，等待 Maker 发布审阅 |
| Implementation | `IMPLEMENTATION/RC_PACKAGING_IMPLEMENTATION_PLAN.md` | IMPLEMENTED / PACKAGING ACCEPTED | RC 已构建并行安装；195 项矩阵、唯一发现入口、Managed Project RC 绑定和安装后九项检查通过 |
| Implementation | `IMPLEMENTATION/LAYER2_RUNTIME_ACCEPTANCE_TEST_PLAN.md` | PASSED / PACKAGING GAP CLOSED FOR RC | RC 可发现且独立运行；下一步为人工行为验收 |
| Implementation | `IMPLEMENTATION/CONTEXT_MUTATION_ORCHESTRATION_IMPLEMENTATION_PLAN.md` | IMPLEMENTED / AUTOMATED ACCEPTANCE PASSED | Tasks 1–8 已完成；RC 1.1.0-rc.2 已构建并行安装，等待 Manual Round 2R |
| Implementation | `IMPLEMENTATION/CONTEXT_MUTATION_ORCHESTRATION_ACCEPTANCE_TEST_PLAN.md` | AUTOMATED PASSED / MANUAL ROUND 2R PENDING | Authorization、Rollback、Runtime Routing、Stage F 已通过；Manual Round 2R 尚未执行 |
| Implementation | `IMPLEMENTATION/DESKTOP_PRODUCT_INCUBATOR_IMPLEMENTATION_PLAN.md` | IMPLEMENTED / ACCEPTANCE PASSED | Tasks 1–7 已实施；M1–M6、Bootstrap Activation、Receipt 与真实 Stop Hook 闭合验收通过 |
| Implementation | `IMPLEMENTATION/DESKTOP_PRODUCT_INCUBATOR_ACCEPTANCE_TEST_PLAN.md` | PASSED / CANDIDATE ACCEPTED | Plugin `137/137`、Legacy `132/32/3`、受保护文件、M1–M6 与候选 `0.2.0+codex.20261009161423` 均通过；该结论不等于 V1.1 RC Round 2R 或发布归档完成 |

## 人工验收入口

- 操作手册：`../ACCEPTANCE_TESTS/manual/v1_1_rc/README.md`；
- 逐轮 Agent Prompt：`../ACCEPTANCE_TESTS/manual/v1_1_rc/AGENT_PROMPTS.md`；
- Maker 专用答案与评分：`../ACCEPTANCE_TESTS/manual/v1_1_rc/MAKER_ANSWER_KEY.md`。

Maker 专用答案不得加入模拟项目或发送给被测 Agent。

当前人工验收结论：Round 2 的 Capability 分析通过，但旧 RC 的 Authority Boundary 失败；Round 2C 纠正通过。缺陷 `MULTI_CONTEXT_MUTATION_ORCHESTRATION_GAP` 已完成自动化修复验证，仍需在已安装的 `1.1.0-rc.2` 上执行 Round 2R；原 Round 3 在此之前继续暂停。

## 当前 Source of Truth 解释

在 V1.2 Plugin Web Product 独立分支的规格阶段：

1. V1.0 已发布行为以 `_V1.0` 与当前产品实现为发布基线证据；
2. V1.1 架构、设计、契约和 Runtime 规格及其已完成实现构成 V1.2 的开发基础，但 V1.1 Round 2R 人工验收与发布归档仍在并行轨道中，不得被 V1.2 提前声明为已发布；
3. Web Product Architecture Change Proposal 已获批准，Decision 014 已进入活动架构；
4. `PROJECT_TYPES/WEB_PRODUCT_PROFILE.md` 当前为 `DRAFT`，只能作为 Maker 审阅对象，不能作为 Contract、Runtime 或实现授权；
5. 活动层文档是当前规格依据，`_V1.0` 仅用于回归比较、迁移分析和历史追踪；
6. 若下游规格或实现与上游冲突，必须先登记并解决 `DESIGN_GAP`；
7. V1.1 RC 自动化通过不替代 Maker 的 Round 2R 人工行为验收；V1.2 也不得改变或关闭该验收状态。

## V1.2 Web Product 文档推进顺序

1. Architecture Change Proposal 已批准；
2. Architecture Decisions 与 Document Architecture 已更新；
3. 编写并审批 Web Product Project Type Design；
4. Design 获批后编写并审批 Contract 与 Runtime Specification；
5. 编写并审批 Implementation Plan 与 Acceptance Test Plan；
6. 两份 Plan 获批后进入 Skill、Runtime、Profile、Registry、Router、Manifest 与 Test 实现；
7. 完成自动化、候选包、仓库外安装和真实已有 Web 项目验收后，才评估 V1.2 发布归档。

## 历史基线

- V1.0：`SPECS/_V1.0/`
- V1.0 发布记录：`SPECS/_V1.0/RELEASE_RECORD.md`
- V1.0 文件清单：`SPECS/_V1.0/MANIFEST.md`
