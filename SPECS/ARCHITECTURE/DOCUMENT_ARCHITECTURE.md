# Project Incubator Document Architecture

## 1. 文档状态

| 字段 | 值 |
| --- | --- |
| Specification Version | V1.2 Plugin Web Product Extension Track |
| Status | ACTIVE |
| Released Baseline | `SPECS/_V1.0/ARCHITECTURE/DOCUMENT_ARCHITECTURE.md` |
| Development Base | Desktop Product Incubator accepted commit `3482f3b6fce98452d5f9f64e7d5c8142a4079c31` |
| Architecture Proposals | `SPECS/ARCHITECTURE/ARCHITECTURE_CHANGE_PROPOSAL.md`、`SPECS/ARCHITECTURE/WEB_PRODUCT_INCUBATOR_CHANGE_PROPOSAL.md` |

## 2. 目的

本文档定义 Project Incubator 当前规格体系的层级、职责、依赖、版本管理和加载边界。

它负责回答：

- 当前有效规格在哪里；
- 每类文档负责什么；
- Core、Extension、Optional Context 与 Project Type Profile 如何分工；
- 下游文档可以依赖什么、不得重定义什么；
- 已发布版本如何归档且不污染当前上下文。

本文档不定义具体领域模型、Contract Payload、Runtime Algorithm 或 Implementation Task。

## 3. 规格入口与版本布局

```text
SPECS/
├── README.md
├── ARCHITECTURE/
├── DESIGN/
├── EXTENSIONS/
├── PROJECT_TYPES/
├── CONTRACTS/
├── RUNTIME/
├── IMPLEMENTATION/
├── FEATURE/
└── _V<released-version>/
```

### 3.1 活动规格

`SPECS/` 的直接层级目录保存当前研发阶段最新规格。活动文件名不得携带发布版本号。

`SPECS/README.md` 是当前版本、阶段、文档状态和 Source of Truth 解释的唯一入口索引。

只有索引标记为 `ACTIVE` 或 `APPROVED` 的文档，才能作为对应职责的当前权威来源。`DRAFT`、`UPDATING`、`MIGRATING`、`PLANNED` 和 `SUPERSEDED` 必须按索引声明解释。

### 3.2 发布归档

`SPECS/_V*` 保存已经发布的只读历史快照。

归档规则：

- 不作为当前产品配置的 `source_document`；
- 不参与默认上下文恢复、扫描、打包或验证；
- 仅用于回归比较、迁移分析、历史追踪和发布审计；
- 每个归档必须包含 Release Record 和 Manifest；
- 除 Maker 明确授权修复归档完整性外，不得修改归档正文。

### 3.3 文档元数据

V1.1 及后续版本新建或实质性重写的规格至少声明：

- `Specification Version`；
- `Status`；
- `Previous Baseline`（如适用）；
- 上游 Proposal 或 Decision（如适用）。

版本信息写入文档元数据，不写入活动文件名。

## 4. 层级关系

```text
Specification Index / Governance
                ↓
          Architecture Layer
                ↓
            Design Layer
           ↙            ↘
Extension Design     Project Type Profile
           ↘            ↙
           Contract Layer
                ↓
           Runtime Layer
                ↓
       Implementation Layer
```

Release Archive 位于该依赖链之外，只保存历史快照。

Extension Design 和 Project Type Profile 都必须服从 Architecture 与 Core Design：

- Extension 提供条件触发的方法和附加 Artifact；
- Project Type Profile 提供领域默认值、代表性路径和更严格约束；
- 两者都不得新增或重定义 Core Phase、Context Authority、Maker Authority 或 Runtime Invariant。

## 5. Architecture Layer

路径：`SPECS/ARCHITECTURE/`

职责：

- 系统整体结构和职责边界；
- Source of Truth 层级；
- Core / Extension / Project Type 关系；
- Maker、Agent、Runtime、Gate、Script 和 Advisory 的 Authority；
- 跨层变更控制；
- Architecture Decision 生命周期。

当前文档：

| Document | 职责 |
| --- | --- |
| `ARCHITECTURE_CHANGE_PROPOSAL.md` | 描述 V1.1 变化动机、范围、Impact、兼容策略和批准边界 |
| `CONTEXT_MUTATION_ORCHESTRATION_CHANGE_PROPOSAL.md` | 描述人工验收发现的授权来源与多 Context 闭合缺口及修复边界 |
| `DESKTOP_PRODUCT_INCUBATOR_CHANGE_PROPOSAL.md` | 描述 Desktop Product Project Type、Host Requirement 与 Workflow Entry 的架构边界 |
| `WEB_PRODUCT_INCUBATOR_CHANGE_PROPOSAL.md` | 描述 V1.2 Web Product Project Type、localhost 验证、部署挂起与次级集成界面归属 |
| `ARCHITECTURE_DECISIONS.md` | 保存当前有效 Architecture Decision 及其状态、关系和影响 |
| `DOCUMENT_ARCHITECTURE.md` | 定义规格体系、层级职责、版本管理和加载规则 |

Architecture Layer 不定义字段级 Contract、Runtime 执行步骤或代码任务。

## 6. Design Layer

路径：`SPECS/DESIGN/`

职责：

- Core Domain Model；
- Phase、Workflow、Gate、Context、Evidence 与 Advisory 的领域语义；
- 领域对象、状态、关系、不变量和行为边界；
- Architecture Decision 在领域层的具体化。

目标文档：

| Document | 职责 |
| --- | --- |
| `PROJECT_INCUBATOR_DESIGN.md` | Project Incubator Core 总体领域设计与模块关系 |
| `EVIDENCE_MODEL_DESIGN.md` | Capability Claim、Evidence E0–E5、Confidence、Assumption、Observation、Baseline 和 Drift 模型 |
| `WORKFLOW_DESIGN.md` | P0–P6 与 P4 Creation Correction Loop 的领域行为 |
| `CONTEXT_MODEL_DESIGN.md` | Core Context、Optional Context、Authority 和生命周期 |
| `GATE_DESIGN.md` | Gate 类型、Evidence、评估边界和结论语义 |
| `PHASE_ADVISORY_DESIGN.md` | Advisory Trigger、Model Review、Drift 和 Extension Activation 建议 |
| `CONTEXT_MUTATION_ORCHESTRATION_DESIGN.md` | Mutation Set、授权来源、Extension 生命周期、Closure 与回滚领域模型 |

Design Layer 不定义序列化 Payload、API 调用顺序、Runtime Algorithm 或文件级任务拆分。

## 7. Extension Layer

路径：`SPECS/EXTENSIONS/`

职责：

- 在 Core 允许的触发条件下，为特定风险提供附加工作方法；
- 定义 Extension Artifact、启用条件、退出条件和与 Core 的接口；
- 定义不适合强制所有项目承担的验证深度。

V1.1 目标文档：

| Document | 职责 |
| --- | --- |
| `OPAQUE_CAPABILITY_EXTENSION.md` | 定义不透明 Capability 的评估、产品点螺旋、发现轮、验证轮、观察、证据闭环、单圈闭合和兼容性扩展 |

Extension 文档必须为每项能力定义：

- 中文主名称与稳定 Identifier；
- 解决的问题；
- 启用与退出条件；
- 输入、输出和失败语义；
- Agent、Maker、Gate、Script 与 Runtime 的职责；
- 持久化位置和 Source of Truth；
- 自动化边界与非职责。

Extension 不得：

- 修改 Core Phase Authority；
- 替代 Maker Decision；
- 强制透明、低风险 Capability 创建附加文档；
- 把 Extension Artifact 变成新的 Current Project State；
- 把领域特有枚举写入 Core。

## 8. Project Type Layer

路径：`SPECS/PROJECT_TYPES/`

职责：

- 提供特定项目类型的领域指导、默认值和代表性路径；
- 在 Core 下限之上收紧阈值或验证要求；
- 将重复出现且稳定的领域需求沉淀为 Profile。

Project Type 不决定 Opaque Extension 是否对整个项目永久启用。Extension 按 Capability Assessment 激活。

Project Type Profile 不得放宽 Core Gate、Evidence、Authority 或 Correction Threshold。

当前文档：

| Document | Status | 职责 |
| --- | --- | --- |
| `DESKTOP_PRODUCT_PROFILE.md` | APPROVED | 定义 Desktop Product Domain Model、P0–P6 Profile、Host 接口、交付检查点与真实环境 Evidence |
| `WEB_PRODUCT_PROFILE.md` | APPROVED | 定义 Web Product Domain Model、P0–P6 Profile、构建与 localhost 检查点、浏览器和次级界面 Evidence；Maker 于 2026-10-13 批准 |

## 9. Contract Layer

路径：`SPECS/CONTRACTS/`

职责：

- 模块交互与 Payload；
- 输入、输出、状态和错误语义；
- Context Access 与 Mutation Authority；
- Workflow Request / Result；
- Gate Evaluation；
- Script Invocation 与 Evidence Boundary。

当前文档：

| Document | 职责 |
| --- | --- |
| `CONTEXT_ACCESS_CONTRACT.md` | Context Read、Mutation、Authority、Evidence 与 Optional Context 访问规则 |
| `WORKFLOW_CONTRACT.md` | Phase、Transition、P4 Correction Request / Result 与恢复边界 |
| `GATE_CONTRACT.md` | Gate Input、Evidence、Evaluation Result 和非控制性边界 |
| `SCRIPT_CONTRACT.md` | Script Input / Output、确定性证据和禁止路径 |
| `CONTEXT_MUTATION_ORCHESTRATION_CONTRACT.md` | Multi-Context Event、Mutation Set、Authorization Provenance、Closure Result 与错误语义 |
| `DESKTOP_PRODUCT_INCUBATOR_CONTRACT.md` | Desktop Project Type、Workflow Entry、Host Requirement、激活与 evaluator 交互契约 |
| `WEB_PRODUCT_INCUBATOR_CONTRACT.md` | Web Project Type、Host Forbidden、Workflow Entry、P0–P6、P4 Checkpoint、P5 Evidence 与次级界面契约；Maker 于 2026-10-14 批准 |

Contract 必须由上游 Design 推导，不得自行创造 Domain Rule。

## 10. Runtime Layer

路径：`SPECS/RUNTIME/`

当前文档：

- `SKILL_RUNTIME_SPEC.md`；
- `CONTEXT_MUTATION_ORCHESTRATION_RUNTIME_SPEC.md`；
- `DESKTOP_PRODUCT_INCUBATOR_RUNTIME_SPEC.md`；
- `WEB_PRODUCT_INCUBATOR_RUNTIME_SPEC.md`（APPROVED，Maker 于 2026-10-14 批准）。

Web Product Contract 与 Runtime Specification 已成为当前活动实现依据；它们只授权编写 Implementation Plan 与 Acceptance Test Plan，不构成实现授权。

职责：

- 已批准 Contract 的执行机制；
- Runtime Component 协作；
- Command、Result、Persistence、Recovery 与 Failure Handling；
- Correction Counter、Structural Validation 和 Context Mutation 执行；
- Extension Activation 的确定性路由边界。

Runtime 不判断产品目标、技术解释或语义 Evidence 是否真实，不替 Agent 创造设计，也不替 Maker授权。

## 11. Implementation Layer

路径：`SPECS/IMPLEMENTATION/`

职责：

- Task、Dependency、Scope 与 Non-Goal；
- Generated / Modified Files；
- Validation Criteria；
- Migration、Compatibility 与 Regression Plan；
- Acceptance Test Plan。

当前入口：

| Document | 当前状态 |
| --- | --- |
| `IMPLEMENTATION_PLAN.md` | V1.1 已实施并通过仓库内验收；不授权 V1.2 Web Product 实现 |
| `LAYER2_RUNTIME_ACCEPTANCE_TEST_PLAN.md` | V1.1 RC Packaging Gap 已关闭；人工验收仍按索引执行 |
| `CONTEXT_MUTATION_ORCHESTRATION_IMPLEMENTATION_PLAN.md` | V1.1 RC Remediation 已实施，等待 Round 2R 人工闭合 |
| `CONTEXT_MUTATION_ORCHESTRATION_ACCEPTANCE_TEST_PLAN.md` | 自动化通过，Manual Round 2R Pending |
| `DESKTOP_PRODUCT_INCUBATOR_IMPLEMENTATION_PLAN.md` | Desktop Product 已实施并通过候选验收 |
| `DESKTOP_PRODUCT_INCUBATOR_ACCEPTANCE_TEST_PLAN.md` | Desktop Product Candidate Accepted |
| `WEB_PRODUCT_INCUBATOR_IMPLEMENTATION_PLAN.md` | DRAFT；等待 Maker 审批，不授权实现 |
| `WEB_PRODUCT_INCUBATOR_ACCEPTANCE_TEST_PLAN.md` | DRAFT；等待 Maker 审批，不授权实现或验收结论 |

Web Product Implementation Plan 与 Acceptance Test Plan 已进入草案阶段。它们依赖已批准的 Architecture、Design、Contract 和 Runtime Specification，并需 Maker 单独审批后才能授权实现。

Implementation Plan 必须等待 Architecture、Design、Contract 和 Runtime Specification 获批后编写。

## 12. Feature Specifications

路径：`SPECS/FEATURE/`

Feature Specification 描述已经获得上游授权的独立功能范围。它必须声明所依赖的 Architecture Decision、Design、Contract 和 Runtime Boundary，不得越过上游重新定义系统。

## 13. Optional Context 与 Extension Artifact

Optional Context 是 Managed Project 中按条件创建的持久上下文，不是本仓库 `SPECS/` 中的规格文件。

V1.1 可以定义 Capability Spiral Record 等 Optional Context，但必须满足：

- `PROJECT_STATE.md` 仍是 Current Project State 唯一 Source of Truth；
- Optional Context 只保存 Extension 特有信息或对 Core Authority 的引用；
- 不复制 Product Goal、Current Phase、Maker Decision 等已有权威数据；
- 生命周期、读写权限和归档规则由 Context Design 与 Contract 定义；
- 不启用 Extension 的项目无需创建。

## 14. Source of Truth 与冲突规则

同一概念出现于多个层级时：

| Layer | Authority |
| --- | --- |
| Architecture | 整体职责、权威和不可变边界 |
| Design | Domain Model、状态、关系和行为语义 |
| Extension / Project Type | 条件方法、领域默认值和附加 Artifact |
| Contract | 模块交互、Payload 和错误语义 |
| Runtime | Contract 的执行机制 |
| Implementation | 文件、任务、顺序和验证 |

低层不得隐式重定义高层。Extension 与 Project Type 发生冲突时，Core Architecture 和 Core Design 优先；Extension 不得通过 Profile 绕过 Core 下限。

发现冲突时：

1. 停止受影响的下游修改；
2. 定位最早发生冲突的层级；
3. 创建或更新对应 Change Proposal / Decision；
4. 获得所需 Authority 确认；
5. 按层级顺序更新下游。

## 15. 加载与验证规则

Agent 恢复当前规格时：

1. 先读取 `SPECS/README.md`；
2. 只加载当前任务需要且状态允许的活动规格；
3. 默认排除 `_V*`；
4. 仅在迁移、回归或历史追踪时显式读取归档；
5. 不把 `PLANNED` 或 `MIGRATING` 文档当作已批准实现依据。

产品 JSON 的 `source_document` 必须指向活动规格。文档验证至少检查：

- 活动文件路径存在；
- 不意外引用 `_V*`；
- 文档状态与 `SPECS/README.md` 一致；
- 下游新增概念可以追踪到 Architecture Decision；
- 归档目录未被当前配置或打包加载。
