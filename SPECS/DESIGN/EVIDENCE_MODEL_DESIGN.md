# Project Incubator Evidence Model Design

## 1. 文档状态

| 字段 | 值 |
| --- | --- |
| Specification Version | V1.1 |
| Status | APPROVED |
| Previous Baseline | 无；V1.1 新增 |
| Architecture Decisions | Decision 007、008、009、011 |

## 2. 目的与边界

本文档定义 Project Incubator Core 的能力声明与证据领域模型，使 Agent 能够区分“已完成 Artifact”“局部机制可用”和“目标环境能力成立”。

本文档定义 Domain Entity、关系、状态和不变量，不定义序列化格式、Runtime API、文件模板或具体项目领域的验证步骤。

## 3. 核心模型

```text
Product Point
    ↓ described by
Capability Claim
    ↓ explained by
Candidate Model
    ↓ contains
Runtime Assumption / Hypothesis
    ↓ evaluated by
Evidence Record
    ↓ updates
Evidence Level / Confidence
    ↓ protects
Known-Good Baseline
```

Observation 是已发生事实。Evidence Record 是带来源、范围和可追踪性的观察或验证结果。Hypothesis 是对事实的临时解释。三者不得互相替代。

## 4. Product Point

Product Point 是最小但具有用户意义的产品能力。

必须表达：

- Actor；
- Preconditions；
- Action；
- Observable Outcome；
- Failure Outcome；
- Non-Commitment。

模块、API、文件或 Task 本身不是 Product Point，除非它们直接构成用户可观察结果。

## 5. Capability Claim

Capability Claim 是对 Product Point 当前支持边界的正式声明。

最低语义字段：

```text
claim_id
product_point_id
supported_boundary
excluded_boundary
required_evidence_level
current_evidence_level
confidence
known_limitations
evidence_refs
baseline_ref
status
```

Claim Status：

- `HYPOTHESIZED`；
- `LOCALLY_VERIFIED`；
- `OBSERVED_WORKING`；
- `MECHANISM_SUPPORTED`；
- `REPRESENTATIVE_BOUNDARY_VALIDATED`；
- `PENDING_LONG_TERM_VALIDATION`；
- `INVALIDATED`。

状态描述不同维度，不得把一次目标环境成功直接提升为代表性边界已验证。

## 6. Evidence Maturity

| Level | 证据来源 | 结论上限 |
| --- | --- | --- |
| E0 | 推测、未验证假设 | 只能陈述 Hypothesis |
| E1 | 文档、规范、公开契约或源码 | 声明接口或规则有依据 |
| E2 | 隔离实验、局部调用、本地自动化 | 声明局部机制可用 |
| E3 | 单个完整目标环境场景 | 声明该场景 Observed Working |
| E4 | 代表性变体与关键失败路径 | 声明已定义边界具有代表性支持 |
| E5 | 重复、长期、兼容性或真实使用 | 声明对应时间、版本和使用边界内稳定 |

Evidence Level 绑定 `claim_id + evaluated_scope`。同一 Evidence 不得在未说明适用范围时提升其他 Claim。

Evidence Level 可以升高、降低或失效。外部版本变化、Baseline 回归、证据撤销或 Scope 扩大都可以导致降级。

## 7. Evidence Record

Evidence Record 最低语义字段：

```text
evidence_id
claim_id
evidence_type
source
observed_at
environment
evaluated_scope
observation
result
reproducibility
artifact_refs
limitations
```

Evidence Type 至少区分：

- `DOCUMENTARY`；
- `SOURCE_INSPECTION`；
- `ISOLATED_EXPERIMENT`；
- `AUTOMATED_VERIFICATION`；
- `TARGET_ENVIRONMENT_OBSERVATION`；
- `MAKER_VALIDATION`；
- `LONG_TERM_USAGE`；
- `EXTERNAL_FEEDBACK`。

Evidence Record 只记录证据及适用边界，不自动作出 Product Decision。

## 8. Observation、Hypothesis 与 Runtime Assumption

### Observation

已经发生且可引用来源的事实，不包含原因解释。

### Hypothesis

对一个或多个 Observation 的可推翻解释。必须能够列出支持信号、不支持信号和区分证据。

### Runtime Assumption

当前实现或 Candidate Model 正在依赖、但仍可能被证据推翻的技术判断。

最低语义字段：

```text
assumption_id
statement
effective_scope
dependent_claims
dependent_artifacts
supporting_evidence_refs
invalidation_signals
status
```

Assumption Status：`UNTESTED`、`SUPPORTED`、`WEAKENED`、`INVALIDATED`、`RETIRED`。

Assumption 失效可以由 Evidence 直接记录；如果后续变化涉及 Product Decision 或 Architecture Decision，仍须取得对应 Authority。

## 9. Candidate Model

Candidate Model 是解释并实现一个或多个 Capability Claim 的最小模型。

模型升级必须引用真实反例，并说明：

- 旧模型无法解释、重建、区分或安全处理什么；
- 新概念解释什么；
- 新数据从何处取得；
- 如何消费、重建及处理缺失；
- 什么 Evidence 可以再次推翻新模型。

不得因为未来可能需要而提前增加模型复杂度。

## 10. Confidence

Confidence 表达对当前 Claim 在指定 Scope 内成立的综合判断，不替代 Evidence Level。

Confidence 使用有限枚举：

- `LOW`；
- `MEDIUM`；
- `HIGH`。

每次变化必须记录依据。Evidence Level 较高不保证 Confidence 必然较高，例如环境漂移、样本偏差或未解释异常仍可降低 Confidence。

## 11. Failure Signature 与重复失败

Failure Signature 用于识别同一产品路径上的重复失败：

```text
capability_id + scenario_id + boundary_step + observed_outcome
```

推测根因不进入 Signature。

- 连续 2 次：`MODEL_REVIEW_ADVISORY`；
- 连续 3 次：`P4_CORRECTION_REQUIRED`；
- 中间出现同 Signature 成功或 Candidate Model 正式更新：结束当前连续序列；
- Project Type Profile 只能收紧阈值。

## 12. Known-Good Baseline

Known-Good Baseline 是经适当目标环境 Evidence 确认、在明确 Capability Boundary 内工作的版本、场景、交付物和证据集合。

最低语义字段：

```text
baseline_id
claim_id
version_or_revision
environment
scenario_set
delivery_artifact_refs
evidence_refs
validated_boundary
known_limitations
established_at
status
```

Baseline Status：`CURRENT`、`STALE`、`REGRESSED`、`SUPERSEDED`。

高风险改变前必须识别受影响 Baseline；出现同一 Baseline Scenario 的 Pass → Fail 时，立即要求 Correction 和回归影响分析。

## 13. Drift

Drift 比较以下对象：

- Capability Claim；
- Active Design；
- Active Decision；
- Implementation；
- Repeatable Verification；
- Target-Environment Evidence；
- Known-Good Baseline。

Drift Type：

- `STRUCTURAL_DRIFT`：Schema、引用、字段、Artifact 或可确定规则不一致，可由 Script 报告；
- `SEMANTIC_DRIFT`：行为、模型或结论含义不一致，由 Agent 基于 Evidence 提出；
- `AUTHORIZED_TRANSITION`：已获授权但下游尚未同步的临时差异，不作为静默 Drift。

Drift Record 必须引用冲突双方、Evidence、影响范围和建议处理方式。

## 14. Authority 与持久化边界

- Product Decision 与 Architecture Decision 由对应 Authority 确认；
- Agent 负责 Observation、Hypothesis、Assumption、Candidate Model 与语义 Drift；
- Script 只产生确定性 Evidence 和 Structural Drift；
- Gate 评估 Evidence 是否满足已声明要求，不创造 Evidence；
- Runtime 执行已获授权的持久化和计数，不判断技术解释；
- Maker 提供 Agent 无法访问的目标环境观察并确认产品边界。

Core Context 保存当前权威摘要和引用。高体积 Evidence、Baseline、Trace 与 Capability Spiral Record 应进入 Optional Context 或项目 Artifact，不得塞入 `PROJECT_STATE.md`。

## 15. 不变量

1. Artifact 完成不等于 Capability Claim 成立；
2. API 可用不等于目标环境产品语义成立；
3. 自动化验证不替代目标环境 Evidence；
4. Evidence 必须绑定 Claim 与 Scope；
5. Confidence 可以降低；
6. Observation 不自动成为解释；
7. Runtime Assumption 不自动成为 Maker Decision；
8. Baseline 只保护其已声明边界；
9. 未覆盖范围必须进入 Excluded Boundary 或 Known Limitations；
10. Evidence、Decision、Design 和 Implementation 的冲突不得静默存在。
