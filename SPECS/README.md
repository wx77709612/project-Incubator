# Project Incubator Specifications

## 当前研发状态

| 字段 | 值 |
| --- | --- |
| 当前研发版本 | V1.1 |
| 上一发布基线 | `SPECS/_V1.0/` |
| 当前阶段 | Architecture Change Proposal Review |
| 产品实现状态 | 未开始；等待规格与实施计划获批 |
| 当前入口 | 本文件 |

## 版本管理规则

`SPECS/` 的直接层级目录保存当前研发阶段最新文档，文件名不携带版本号。`SPECS/_V*` 保存已发布版本的只读历史快照。

历史归档不参与当前 Source of Truth 解析、产品配置引用或默认上下文加载。需要进行回归、迁移和历史追踪时，才显式读取对应归档。

## 当前文档状态

| Layer | Document | Status | 说明 |
| --- | --- | --- | --- |
| Architecture | `ARCHITECTURE/ARCHITECTURE_CHANGE_PROPOSAL.md` | DRAFT / REVIEW REQUIRED | V1.1 变更总规格；当前审阅入口 |
| Architecture | `ARCHITECTURE/DOCUMENT_ARCHITECTURE.md` | MIGRATING | 从 V1.0 继承，待按提案更新 |
| Architecture | `ARCHITECTURE/ARCHITECTURE_DECISIONS.md` | MIGRATING | V1.0 决策基线；待登记 V1.1 决策 |
| Design | `DESIGN/PROJECT_INCUBATOR_DESIGN.md` | MIGRATING | 未变更部分继承 V1.0；待集成 V1.1 设计 |
| Design | `DESIGN/WORKFLOW_DESIGN.md` | MIGRATING | 待加入 P4 Creation Correction Loop |
| Design | `DESIGN/CONTEXT_MODEL_DESIGN.md` | MIGRATING | 待加入 Claim、Evidence、Assumption 与 Baseline 语义 |
| Design | `DESIGN/GATE_DESIGN.md` | MIGRATING | 待加入证据成熟度与 Drift 检查 |
| Design | `DESIGN/PHASE_ADVISORY_DESIGN.md` | MIGRATING | 待加入重复失败、模型失效与扩展触发器 |
| Extension | `EXTENSIONS/OPAQUE_CAPABILITY_EXTENSION.md` | PLANNED | 提案获批后编写 |
| Contract | `CONTRACTS/*.md` | BASELINE COPIED | 当前仍为 V1.0 语义，待 Design 获批后更新 |
| Runtime | `RUNTIME/SKILL_RUNTIME_SPEC.md` | BASELINE COPIED | 当前仍为 V1.0 语义，待 Contract 更新后修改 |
| Implementation | `IMPLEMENTATION/IMPLEMENTATION_PLAN.md` | PLANNED | V1.1 占位入口；完整计划尚未编写，不构成实施授权 |
| Implementation | `IMPLEMENTATION/LAYER2_RUNTIME_ACCEPTANCE_TEST_PLAN.md` | PLANNED | V1.1 占位入口；验收计划尚未编写 |

## 当前 Source of Truth 解释

在 V1.1 规格尚未全部获批前：

1. V1.0 已发布行为以 `_V1.0` 与当前产品实现为基线证据；
2. V1.1 拟议变化以 `ARCHITECTURE_CHANGE_PROPOSAL.md` 为审阅对象，但在 Maker 批准前不构成实施授权；
3. 活动层中标为 `MIGRATING` 或 `BASELINE COPIED` 的文件只对未被提案改变的 V1.0 语义有效；
4. 若提案与继承文档冲突，当前阶段应报告冲突，不得选择性实现；
5. `PROJECT_INCUBATOR/` 的产品行为必须保持不变，直到 V1.1 Implementation Plan 获批。

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
