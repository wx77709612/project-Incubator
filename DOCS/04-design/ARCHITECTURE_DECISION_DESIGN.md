# Project Incubator Architecture Decision Design

> Phase 4 — Design 的架构决策文档设计

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 4 — Design |
| 文档状态 | Active |
| 权威范围 | `SPECS/ARCHITECTURE_DECISIONS.md` 的职责、内容结构、写入门槛、更新流程与读取方式 |
| 消费 Phase | Phase 4–9，按需读取 |
| 更新条件 | Maker 调整 Architecture Decision 的用途、结构、写入门槛、读取策略或写回规则 |
| 依赖文档 | `SPECS/ARCHITECTURE_DECISIONS.md`、`DOCS/04-design/SCOPE.md`、`DOCS/04-design/TECHNICAL_DESIGN.md`、`DOCS/04-design/SKILL_DESIGN.md`、`DOCS/PROJECT_STATE.md` |
| 最后更新 | 2026-07-23 |

## 1. 文档职责

本文档定义 `SPECS/ARCHITECTURE_DECISIONS.md` 应如何作为 Project Incubator 的高权威架构边界文档存在。

本文档不直接替代 `SPECS/ARCHITECTURE_DECISIONS.md`，也不重写现有 Decision 正文。现有架构决策文档的内容审计与结构重构应作为独立治理任务处理。

## 2. Architecture Decision 的定位

`ARCHITECTURE_DECISIONS.md` 应是低频、高权威、原则型的架构边界文档。

它用于记录 Maker 已确认、AI 不得静默改变的长期架构决定。它不应承担以下职责：

- 记录普通协作纠偏；
- 记录一次性任务过程；
- 重复维护 `AGENTS.md`、`FRAMEWORK/` 或 `DOCS/PROJECT_STATE.md` 中已有的执行细则；
- 作为每轮启动的普通事实库全文加载；
- 替代 Phase 文档保存当前项目状态。

## 3. 写入门槛

AI 不得自行新增或修改 Architecture Decision。

只有当某项变化满足以下条件时，AI 才能向 Maker 提议形成或修改 Architecture Decision：

- 影响跨项目复用规则；
- 影响多个 Phase 的流程边界；
- 改变 Maker、AI Collaborator 或 AI Builder 的职责；
- 改变文档权威来源、目录结构或状态恢复机制；
- 改变 Git 治理、验收门或人工闭环原则；
- 改变 Project Incubator 是否 Skill 化、如何 Skill 化的高层方向；
- 推翻或收束既有架构原则。

普通协作偏差应优先归入现有边界原则、当前 Phase 文档、交互设计或任务规则。只有现有原则无法覆盖，且 Maker 确认具有长期复用价值时，才上升为 Architecture Decision。

## 4. 建议结构

每条 Architecture Decision 应使用稳定结构：

```text
## Decision NNN：标题

| 字段 | 当前值 |
| --- | --- |
| 状态 | Active / Superseded / Proposed / Archived |
| 适用范围 | Project Incubator / 未来项目 / 特定 Phase / 特定治理域 |
| 影响文件 | 精确路径 |
| 更新条件 | 何时需要复审或修改 |

### 背景问题

### 决定

### 原因

### 被拒绝或替代的方案

### 执行边界

### 下游引用
```

其中，“决定”和“原因”应保留为核心；其他字段用于防止 Decision 变成无上下文条目堆积。

## 5. 读取方式

Skill 运行时不应默认全文读取所有 Decision 正文。

推荐读取方式：

- 启动时读取文档职责和 Decision 标题；
- 根据本轮任务判断是否涉及某个架构域；
- 只读取相关 Decision 正文；
- 当任务会修改 Framework、目录结构、角色边界、文档规则、Git 治理或 Skill 形态时，读取相关 Decision 正文并检查冲突；
- 若 Decision 索引不足以判断相关性，才全文读取，并在收尾时记录索引改进需求。

## 6. Skill 写回行为

Skill 应支持的行为是：

- 识别某个分叉是否可能影响长期架构边界；
- 向 Maker 提议是否形成或修改 Architecture Decision；
- 在 Maker 确认后，按本文档结构执行写回；
- 在后续启动或任务执行中，将 Active Decision 作为不可静默改变的边界。

Skill 不应在没有 Maker 确认的情况下，把自己的纠偏、偏好或推断写成 Architecture Decision。
