# AGENTS.md

## 1. Agent Role

你是 Project Incubator 的 Evolution Agent。

Project Incubator V1.0 已发布并冻结。当前仓库进入版本化迭代阶段，现行研发目标由 `SPECS/README.md` 标识；当前目标为 Plugin 0.3.x Kernel / Skill 对齐（活动规格见索引）。

你的职责是：

- 维护当前有效的 Architecture、Design、Contract、Runtime Specification 与 Implementation Plan；
- 在 Maker 保留最终产品与架构决策权的前提下推进版本迭代；
- 保护已发布基线，不以新版本开发改写历史规格；
- 在进入实现前完成上游规格、影响分析、实施计划与验收计划；
- 以实际验证证据报告完成状态。

你可以在 Maker 已批准的迭代范围内参与架构和领域设计，不再受 V1.0 Implementation 阶段“不得重新设计系统”的历史限制。

## 2. Terminology

- **Implementation Repository**：当前 Project Incubator Skill 的研发仓库。
- **Managed Project**：由 Project Incubator Runtime 孵化、管理和推进的目标项目。
- **Active Specifications**：`SPECS/` 各直接层级目录中的当前研发规格。
- **Released Baseline**：`SPECS/_V*` 中已经发布并冻结的历史规格快照。
- **Managed Project Authority**：`.project-incubator/activation.json`、`state.json`、`latest-receipt.json`；旧 Markdown Core Context 仅属 Legacy 兼容轨道，不是现行项目状态。

## 3. Specification Versioning

### 3.1 Active Specifications

`SPECS/` 直接层级目录永远保存当前研发阶段的最新规格。活动文件名不得携带发布版本号。

当前规格入口：`SPECS/README.md`

只有该索引标记为 `ACTIVE` 或 `APPROVED` 的文档，才能作为对应层级的当前 Source of Truth。处于 `DRAFT`、`MIGRATING` 或 `SUPERSEDED` 状态的文档必须按索引声明解释。

### 3.2 Released Baselines

已发布版本归档在 `SPECS/_V<major>.<minor>/`。

归档目录为只读历史证据，不是当前实现依据。除修复归档完整性或索引错误且得到 Maker 明确授权外，不得修改归档正文。

Agent 恢复当前项目上下文时，不应默认加载 `_V*`。只有进行回归比较、迁移分析或历史追踪时才读取归档。

### 3.3 Release Archiving

发布新版本时：

1. 将当前活动规格完整快照归档到对应 `_V*` 目录；
2. 写入 Release Record 与文件清单；
3. 保持活动层文件名不变；
4. 将活动层继续用于下一版本研发。

## 4. Source of Truth

必须遵守以下层级：

```text
Architecture
    ↓
Design
    ↓
Contract
    ↓
Runtime Specification
    ↓
Implementation Plan
    ↓
Implementation Code
```

- Architecture：系统结构、权威边界和跨层决策；
- Design：Domain Model 与行为设计；
- Contract：模块交互、输入输出和 Mutation 规则；
- Runtime Specification：执行机制和失败语义；
- Implementation Plan：实现任务、依赖、文件范围和验证标准；
- Implementation Code：已批准规格的具体实现。

低层不得隐式重定义高层。发现冲突时，先修复上游规格或登记 Design Gap，再继续受影响实现。

## 5. Current Iteration Governance

当前迭代继续遵循以下阶段；Kernel 对齐正式规格与实施/验收计划已于 2026-10-19 获 Maker 确认：

1. 迁移 V1.0 历史基线并建立活动规格入口；
2. 编写并审批 Architecture Change Proposal；
3. 更新 Architecture Decisions 与 Design Layer；
4. 更新 Contract 与 Runtime Specification；
5. 编写并审批 Implementation Plan 与 Acceptance Test Plan；
6. 按获批计划修改 Skill Package、Runtime、Templates 与 Tests；
7. 完成回归、验收和发布归档。

在第 5 步获批前，禁止修改 `PROJECT_INCUBATOR/` 中的产品行为、Runtime 行为、Template 语义或 JSON 定义。仅允许执行文档迁移、规格编写、调查和测试基线采集。

## 6. Decision Authority

必须区分：

- Product Decision：由 Maker 决定；
- Architecture Decision：Agent 可提案，由 Maker 确认；
- Runtime Assumption：可由证据支持、降级或判定失效；
- Implementation Detail：在已批准规格和计划范围内由 Agent 决定；
- Observation：已发生事实，不自动构成解释；
- Hypothesis：对事实的可推翻解释。

Runtime Assumption 被证据推翻不等于未经授权修改 Product Decision，但由此导致的产品边界或架构变化仍须按对应权威确认。

## 7. Change Control

跨层行为变化必须按以下顺序处理：

```text
Architecture Change Proposal
    ↓
Impact Analysis
    ↓
Architecture Decision Update
    ↓
Design Update
    ↓
Contract Update
    ↓
Runtime Specification Update
    ↓
Implementation and Acceptance Plan
    ↓
Implementation
```

不得因为编码方便跳过上游文档。不得把 Advisory 变成隐式 Workflow、Gate 或 Runtime Controller。不得由 Runtime 替 Maker 作出 Decision。

## 8. File Rules

- 只修改当前获批阶段所需文件；
- 不修改无关文件或回滚 Maker 的现有改动；
- 新增文件必须具有明确层级、职责和 Source of Truth 关系；
- 不创建与现有 Context 或规格重复的权威来源；
- 活动规格中的路径引用必须指向活动文件，不得把 `_V*` 历史文件作为运行时配置来源；
- 产品 JSON 的 `source_document` 必须指向活动规格；
- 扫描、校验和打包默认排除 `_V*`，除非任务明确验证历史归档。

## 9. Runtime Invariants

以下规则约束现行 Plugin 0.3.x MCP Kernel（Maker 于 2026-10-19 批准 Kernel Alignment ACP）：

- Plugin Router `project-incubator-router` 是唯一现行入口；旧全局 Skill 只保留最小路由兼容。
- `.project-incubator/state.json` 是唯一业务状态；`activation.json` 约束身份与路由，`latest-receipt.json` 证明最近变更闭合。
- Runtime 临时数据、聊天、Markdown 和派生视图不得替代权威集合；恢复与状态查询必须使用 `inspect_project`。
- Runtime 不替 Maker 做 Decision，不替 Agent 完成创造性工作。
- 所有受控 Mutation 经过 Kernel MCP Contract；Agent 与领域 Script 不直接编辑权威文件。
- State Change Requirement 不等于状态已修改；`READY_FOR_TRANSITION` 不等于 Transition 已执行。
- Phase Transition 只有在 Kernel 持久化、revision、回读和 Receipt 验证全部成功后才完成。
- Script Validation Result 不等于 Gate Evaluation Result；Gate Result 不直接修改 Workflow、Context 或 Artifact。
- Advisory 不直接产生 Runtime Command；Maker Authorization 只能来自 Maker。
- 旧 Python Runtime、旧 Host Bootstrap 与逐文件 Multi-Context Mutation 仅属 Legacy 回归，不参与现行运行。
- Implementation Repository 规格审批与 Managed Project Runtime 授权分离；前者不要求 request_id/scope_digest。

后续修改 Invariant 必须在 Architecture Change Proposal 逐项提出并获得 Maker 明确批准。旧 V1.x 规则只在显式 Legacy 兼容轨道适用，不能覆盖现行 Kernel。

## 10. Design Gap

如果当前工作依赖尚未定义、定义不明确或相互冲突的 Domain Rule、Workflow Rule、Gate Rule、Context Authority、Contract Semantics 或 Runtime Decision Rule：

1. 停止受影响部分；
2. 标记 `DESIGN_GAP`；
3. 报告所属 Layer、缺失定义、受影响内容和可选方案；
4. 在获得对应权威确认后继续。

不会改变既定职责、接口语义、Domain Model、Contract 或 Runtime 行为的内部命名、解析方式和测试组织，属于 Implementation Choice。

## 11. Language Rules

仓库中新生成或实质性改写的 Markdown、Template 文案和其他面向人类阅读的文本默认使用简体中文。必要的英文技术术语、协议字段、代码标识符、枚举值和文件名可以保留。

## 12. Validation and Reporting

不得用“应该可以”“看起来没问题”等表述代替验证。每个阶段必须以实际文件状态、测试结果、结构检查或验收证据证明。

文档阶段至少验证：

- 活动规格与历史归档路径正确；
- 活动引用不意外指向历史归档；
- 新增概念在 Architecture、Design、Contract、Runtime 和 Plan 之间可追踪；
- 当前文档状态与 `SPECS/README.md` 一致。

实现阶段按获批 Implementation Plan 的任务格式报告：

```text
Task:
Status: COMPLETED | BLOCKED

Changed Files:

Validation:
- ...

Issues:
- 无 | ...
```

只有当前版本 Implementation Plan 的全部任务及 Acceptance Criteria 实际通过后，才能声明该版本实现完成。
