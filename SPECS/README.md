# Project Incubator Specifications

## 当前研发状态

| 字段 | 值 |
| --- | --- |
| 当前研发版本 | V1.1 |
| 上一发布基线 | `SPECS/_V1.0/` |
| 当前阶段 | Manual Acceptance Execution |
| 产品实现状态 | RC Packaging Gap 已关闭；193 项矩阵通过，进入“雾港提醒器”人工行为验收 |
| 当前入口 | 本文件 |

## 版本管理规则

`SPECS/` 的直接层级目录保存当前研发阶段最新文档，文件名不携带版本号。`SPECS/_V*` 保存已发布版本的只读历史快照。

历史归档不参与当前 Source of Truth 解析、产品配置引用或默认上下文加载。需要进行回归、迁移和历史追踪时，才显式读取对应归档。

## 当前文档状态

| Layer | Document | Status | 说明 |
| --- | --- | --- | --- |
| Architecture | `ARCHITECTURE/ARCHITECTURE_CHANGE_PROPOSAL.md` | APPROVED | V1.1 变更总规格；Maker 于 2026-09-23 批准 |
| Architecture | `ARCHITECTURE/DOCUMENT_ARCHITECTURE.md` | ACTIVE | 定义 V1.1 文档职责、层级、版本和加载规则 |
| Architecture | `ARCHITECTURE/ARCHITECTURE_DECISIONS.md` | ACTIVE | 保留 V1.0 Decision 001–006，并登记 V1.1 Decision 007–011 |
| Design | `DESIGN/PROJECT_INCUBATOR_DESIGN.md` | APPROVED | V1.0 非冲突设计与 V1.1 Evidence-driven Evolution 总体关系 |
| Design | `DESIGN/EVIDENCE_MODEL_DESIGN.md` | APPROVED | V1.1 Core Evidence、Claim、Assumption、Baseline 与 Drift 模型 |
| Design | `DESIGN/WORKFLOW_DESIGN.md` | APPROVED | P4 Creation Correction 内部活动模型 |
| Design | `DESIGN/CONTEXT_MODEL_DESIGN.md` | APPROVED | Decision 活动视图与 Evidence Optional Context |
| Design | `DESIGN/GATE_DESIGN.md` | APPROVED | Evidence、Correction、Baseline 与 Drift 评估政策 |
| Design | `DESIGN/PHASE_ADVISORY_DESIGN.md` | APPROVED | Model Review、Regression、Drift 与 Extension Reason Code |
| Design | `DESIGN/RC_PACKAGING_DESIGN.md` | APPROVED / IMPLEMENTED / PACKAGING ACCEPTED | V1.1 RC 并行身份、自包含打包、安装烟雾测试与模拟验收隔离 |
| Extension | `EXTENSIONS/OPAQUE_CAPABILITY_EXTENSION.md` | APPROVED | Capability 级不透明性评估与产品点螺旋方法 |
| Contract | `CONTRACTS/CONTEXT_ACCESS_CONTRACT.md` | APPROVED | Decision 活动视图、Optional Evidence Context 与 Assumption Mutation |
| Contract | `CONTRACTS/WORKFLOW_CONTRACT.md` | APPROVED | P4 Correction Assessment、Result、Activity State 与 Resume Contract |
| Contract | `CONTRACTS/GATE_CONTRACT.md` | APPROVED | Evidence Input、Evaluation Rule 与 Reason Code |
| Contract | `CONTRACTS/SCRIPT_CONTRACT.md` | APPROVED | 确定性 Evidence、Failure Signature 与 Structural Drift |
| Runtime | `RUNTIME/SKILL_RUNTIME_SPEC.md` | APPROVED | V1.1 Evidence、Correction、Baseline、Drift 与 Extension 执行机制 |
| Implementation | `IMPLEMENTATION/IMPLEMENTATION_PLAN.md` | IMPLEMENTED / ACCEPTANCE PASSED | V1.1 Tasks 1–10 已完成，等待 Maker 发布审阅 |
| Implementation | `IMPLEMENTATION/RC_PACKAGING_IMPLEMENTATION_PLAN.md` | IMPLEMENTED / PACKAGING ACCEPTED | RC 已构建并行安装；193 项矩阵、唯一发现入口和安装后九项检查通过 |
| Implementation | `IMPLEMENTATION/LAYER2_RUNTIME_ACCEPTANCE_TEST_PLAN.md` | PASSED / PACKAGING GAP CLOSED FOR RC | RC 可发现且独立运行；下一步为人工行为验收 |

## 人工验收入口

- 操作手册：`../ACCEPTANCE_TESTS/manual/v1_1_rc/README.md`；
- 逐轮 Agent Prompt：`../ACCEPTANCE_TESTS/manual/v1_1_rc/AGENT_PROMPTS.md`；
- Maker 专用答案与评分：`../ACCEPTANCE_TESTS/manual/v1_1_rc/MAKER_ANSWER_KEY.md`。

Maker 专用答案不得加入模拟项目或发送给被测 Agent。

## 当前 Source of Truth 解释

在 V1.1 最终验收审阅期间：

1. V1.0 已发布行为以 `_V1.0` 与当前产品实现为基线证据；
2. V1.1 架构、设计、契约和 Runtime 规格均已批准，产品实现与仓库内自动化验收已按 Implementation Plan 完成；
3. 活动层文档是当前实现依据，`_V1.0` 仅用于回归比较、迁移分析和历史追踪；
4. 若下游实现与上游规格冲突，必须先登记并解决 Design Gap；
5. RC 自包含打包、仓库外安装烟雾测试和 Maker 人工验收完成前，不创建 V1.1 发布归档，也不将当前活动规格标记为已发布。

## V1.1 文档推进顺序

1. 审批 Architecture Change Proposal；
2. 更新 Architecture Decisions 与 Document Architecture；
3. 更新 Core Design，并新增 Opaque Capability Extension；
4. 更新 Contract 与 Runtime Specification；
5. 编写 V1.1 Implementation Plan 与 Acceptance Test Plan；
6. 审批计划后进入 Skill、Runtime、Template 与 Test 实现。

## 历史基线

- V1.0：`SPECS/_V1.0/`
- V1.0 发布记录：`SPECS/_V1.0/RELEASE_RECORD.md`
- V1.0 文件清单：`SPECS/_V1.0/MANIFEST.md`
