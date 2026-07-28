# Skill 1.0 Runtime 架构草案

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 6 — Build |
| 文档状态 | Draft |
| 权威范围 | Skill 1.0 runtime 候选架构、Skill Runtime Design Template 定位、组件职责、脚本 / AI 分工、上下文提取方式、数据流、验证样例和后续是否回修 Phase 4 / Phase 5 的判断依据 |
| 消费 Phase | Phase 6 Build；后续 Phase 4 / Phase 5 受控修订按需消费 |
| 更新条件 | Maker 调整 runtime 架构方向、确认组件边界、决定回修 Phase 4 / Phase 5，或批准进入 runtime scripts / 子 Skill 拆解 |
| 依赖文档 | `DOCS/06-build/SKILL_1_ARCHITECTURE_REVIEW.md`、`DOCS/04-design/SKILL_DESIGN.md`、`DOCS/04-design/GATE_EXECUTION_DESIGN.md`、`DOCS/04-design/TECHNICAL_DESIGN.md`、`DOCS/PROJECT_STATE.md` |
| 最后更新 | 2026-07-28 |

## 1. 目标

Skill 1.0 runtime 的目标不是把所有项目孵化规则写进一个 `SKILL.md`，而是把确定性流程、状态跳转、数据校验、上下文提取和硬性门槛交给可验证的 runtime 组件；AI 只在收到最小必要上下文和结构化运行结果后，负责语义理解、提炼、模糊判断和生成。

本草案只定义 runtime 架构，不实现脚本、不拆最终 Ticket、不修改当前 `SKILL/` Draft。

## 2. Skill Runtime Design Template

Skill Runtime Design Template 是设计模板库中的项目类型专用模板，不是 Project Incubator 所有项目都必须经过的通用 gate。

调用条件：

- 目标产物是 Codex Skill；
- 或目标产物是 Agent workflow、AI 协作协议、自动化 runtime、插件系统、子 Agent 系统；
- 或项目的核心风险来自 AI / 脚本 / 状态 / 上下文 / gate 的运行时分工。

不默认调用的项目：

- 普通 App；
- 内容作品；
- 普通个人工具；
- 研究项目；
- 不涉及 AI runtime 的方法论或决策项目。

该模板在 Phase 4 Design 中作为“设计面补充”使用。它不替代使用过程导向设计方法；使用过程导向方法仍用于理解项目的真实使用过程，Skill Runtime Design Template 用于补充 runtime 实现原则检查。

该模板必须回答：

- runtime 边界是什么；
- 哪些判断应由脚本、schema、validator、gate 或 context retriever 执行；
- 哪些判断保留给 AI；
- 上下文如何切片和注入；
- 子 Skill / 子模块如何被 orchestrator 调用；
- hard gate 如何阻断；
- natural-language reference 只解释什么；
- Build 前必须用哪些样例验证。

这次 Phase 6 返工的关键结论是：Project Incubator Skill 1.0 在 Phase 4 已使用过程导向方法形成总体流程，但缺少 Skill Runtime Design Template 这一专用设计面，导致 Phase 6 实现时把运行时原则落成了自然语言 reference。

## 3. 总体架构

候选架构由七类组件组成：

| 组件 | 职责 | 主要承载 |
| --- | --- | --- |
| 总 orchestrator | 读取当前项目入口，调用状态引擎、gate、context retriever 和对应 Phase 模块 | `SKILL.md` + runtime script |
| Phase 子 Skill / 子模块 | 承载单个 Phase 的目标、输入、输出、交互方式和验收要求 | `phase-00-idea` 至 `phase-09-archive` |
| hard gate 模块 | 在受限动作前输出非黑即白的 gate 结果；分为通用 hard gate Skill 与 Project Incubator gate 模块 | gate config + router script + case fixtures |
| state engine | 判断当前 Stage / Phase、上一步输出是否合法、下一步应跳转到哪里 | state schema + transition rules |
| context retriever | 根据当前任务、Phase、gate 结果和文件索引返回最小上下文 chunk | 文档索引 + chunk selector / RAG |
| validators | 执行 schema、路径、Git、Prompt、Builder handoff 等确定性校验 | scripts + JSON schema + regex |
| AI generation layer | 基于 runtime 输出生成说明、文档草案、代码或 JSON | AI reference + templates |

核心原则：runtime 组件负责“能不能继续、读什么、跳到哪里、格式是否合法”；AI 负责“这段内容是什么意思、如何表达、如何生成有用产物”。

## 4. 运行数据流

一次普通任务的 runtime 流程：

1. Orchestrator 接收 Maker 指令、当前工作区和项目入口。
2. State engine 读取状态入口摘要，输出当前 Phase / Stage、任务状态和允许动作集合。
3. Orchestrator 调用 task classifier，得到任务类型和候选 Phase 子模块。
4. Hard gate router 对即将执行的动作做低成本判定，输出 `MISS`、`INPUT_INCOMPLETE`、`HIT_BLOCK`、`HIT_NEEDS_AUTH` 或 `HIT_SAFE_ALTERNATIVE`。
5. 若 gate 阻断，AI 只消费 gate 输出并组织 Maker 回应。
6. 若 gate 允许继续，context retriever 根据任务类型和 Phase 子模块返回最小上下文 chunk。
7. Phase 子模块给出本 Phase 的输出要求和验收标准。
8. Validators 校验 AI 生成结果的结构、路径、schema 或 Prompt hygiene。
9. Orchestrator 根据 state engine 结果决定下一步：继续当前 Phase、请求 Maker 决定、写回状态、进入 Maker Review，或停止。

## 5. 脚本与 AI 分工

### 5.1 必须优先脚本化

- 当前 Phase / Stage、任务状态和下一步跳转；
- 上一步输出格式是否合法；
- gate router 与关键 gate 输出枚举；
- `PROJECT_STATE.md`、Ticket、Builder handoff、Prompt 正文和 gate case 的 schema 校验；
- Git 只读状态、未闭环任务和授权字段完整性；
- 文档路径存在性、权威索引有效性和 forbidden runtime path；
- context chunk 检索、排序和最小读取包生成；
- 文件读写、格式转换、索引更新和低成本 API 调用。

### 5.2 保留给 AI

- 从 Maker 模糊描述中提取结构化任务输入；
- 对非结构化文档做摘要、比较、推理和风险分析；
- 判断文档表达、代码风格、设计可行性等模糊质量问题；
- 根据 runtime 输出生成自然语言回应、文档草案、代码或 JSON；
- 在脚本返回多个允许路径时，解释取舍并等待 Maker 决定。

### 5.3 禁止的混用

- 不让 AI 代替脚本判断 gate 是否阻断；
- 不让自然语言 reference 代替 schema / validator；
- 不让脚本替 Maker 做 Phase 切换、范围改变或验收决定；
- 不让 context retriever 返回整份大文档作为默认上下文。

## 6. 子 Skill / 子模块边界

每个 Phase 子模块至少声明：

- `phase_id`；
- 入口条件；
- 必需输入；
- 允许输出；
- 输出 schema；
- Exit Criteria；
- 可调用 validators；
- 可调用 hard gates；
- 推荐 AI reference；
- 下一步候选跳转。

Phase 子模块只负责本 Phase 内的协作和输出，不负责全局状态跳转、Git 边界或跨 Phase 决策。跨 Phase 行为由 state engine 和 Maker 决定。

除 Phase 子模块外，还需要以下非 Phase 模块：

- `project-intake`：新项目与既有项目接入；
- `builder-handoff`：Builder 启动前完整性检查；
- `builder-return-review`：Builder 返回后验收与写回判断；
- `maker-prompt`：下一任务 Prompt 生成与 hygiene 检查；
- `common-hard-gate`：跨 Skill / Agent runtime 复用的通用受限动作拦截；
- `project-incubator-gate`：Project Incubator 特有 Phase、状态、权威文档和孵化流程拦截。

通用 hard gate 不应依赖 Project Incubator 的 `DOCS/PROJECT_STATE.md`、Phase 0–9、`FRAMEWORK/` 或项目文档结构。Project Incubator gate 可以在通用 gate 通过后，继续消费项目孵化器状态入口、Phase 规则和权威文档集合。

## 7. Runtime 脚本候选清单

首批 runtime scripts 不应追求完整自动化，建议从最小可验证闭环开始：

| 脚本 | 输入 | 输出 |
| --- | --- | --- |
| `state-engine.mjs` | project state summary、last output、intended action | current stage、allowed actions、next transition、errors |
| `route-gate.mjs` | intended action、state flags、authorization summary | applicable gates、output enum、blocking、safe actions、missing inputs |
| `retrieve-context.mjs` | phase id、task type、gate result、document index | ranked chunks、source paths、reason |
| `validate-output.mjs` | output artifact、schema id、carrier type | pass / fail、violations |
| `check-git-boundary.mjs` | git status summary、intended action、authorization | safe / blocked、required authorization fields |
| `check-prompt-hygiene.mjs` | prompt body、prompt type | pass / fail、blacklist hits |

当前 `SKILL/tools/check-gates.mjs` 可保留为探索性 checker，但不能替代 `route-gate.mjs`。后续可迁移其中的 registry / case 校验能力。

## 8. Context Retriever 设计

Context retriever 的目标是让 AI 不再盲读大文档。

最小输入：

- 当前 Phase / Stage；
- 任务类型；
- gate 输出；
- 权威文档索引；
- Maker 本轮指令摘要；
- 目标文件或承载类型。

最小输出：

```json
{
  "chunks": [
    {
      "source": "DOCS/04-design/GATE_EXECUTION_DESIGN.md",
      "anchor": "## 8. Gate 路由与执行顺序",
      "reason": "runtime gate router design",
      "content": "..."
    }
  ],
  "excluded": [
    {
      "source": "DOCS/04-design/SKILL_DESIGN.md",
      "reason": "not needed for this gate runtime decision"
    }
  ]
}
```

默认不得返回全文。全文读取只在章节定位失败、文档结构冲突、跨 Phase 设计或 Maker 要求完整审阅时发生。

## 9. 输出与状态管理

State engine 应维护的不是聊天历史，而是流程状态：

- 当前 Phase / Stage；
- 当前任务类型；
- 当前产物承载类型；
- 上一步输出 id 与 schema；
- 当前 gate 状态；
- 是否允许写入；
- 是否等待 Maker；
- 下一步候选 transition。

状态输出必须使用封闭枚举。无法判断时输出 `INPUT_INCOMPLETE` 或 `STATE_INVALID`，不得让 AI 猜。

`DOCS/PROJECT_STATE.md` 仍是项目状态权威入口；runtime state 是每次执行时从项目状态、Git 状态、Maker 指令和脚本结果生成的运行态摘要，不替代项目状态文档。

## 10. 验证样例

runtime 架构至少需要以下样例验证：

| 样例 | 预期 |
| --- | --- |
| Maker 只说“继续”，当前 Diff 待审阅 | gate 输出不是 Git 授权；state engine 要求澄清继续对象 |
| 当前任务为 Phase 6 runtime 架构草案 | context retriever 只返回架构重审、Skill design、gate design 和 technical design 相关 chunk |
| Builder Ticket 缺少验证步骤 | validator fail，hard gate 输出 `INPUT_INCOMPLETE` |
| Prompt 正文搬运当前 Phase / Git 历史 | prompt hygiene fail |
| 只读解释任务 | state engine 允许只读；gate router 跳过 Git / Phase 写入 gate |
| 目标文档路径不存在 | authority / state validator fail，停止写入 |

通过标准不是“AI 能解释规则”，而是同一输入能得到稳定的结构化输出。

## 11. 对现有 Draft 的处理

| 现有资产 | 建议处理 |
| --- | --- |
| `SKILL/SKILL.md` | 降级为 orchestrator 入口草稿，后续应大幅收缩 |
| `SKILL/references/main-runtime-chain.md` | 拆分为 state engine / orchestrator / AI reference 输入 |
| `SKILL/references/task-type-and-writeback.md` | 任务类型和写回触发下沉为 state engine / validators；解释部分保留为 AI reference |
| `SKILL/references/hard-gate-matrix.md` | 降级为 gate 输出解释层 |
| `SKILL/references/gate-response-and-authorization.md` | 保留为 AI 组织 Maker 回应的 reference |
| `SKILL/references/builder-*` | 拆入 Builder 子模块和 validator |
| `SKILL/gates/` | 标记为探索性 Draft；保留 schema / case 思路，后续迁移到 hard gate 模块 |
| `SKILL/tools/check-gates.mjs` | 保留为 registry checker 探索，不作为 runtime router |

探索性 `SKILL/gates/` 迁移前必须先分类：

- 通用 hard gate 候选：Git 写操作、上下文完整性、本地协议、承载类型、纠偏沉淀、架构决策写回的通用部分；
- Project Incubator gate 候选：Phase 切换、权威文档集合、范围推进、Builder 交接和未闭环任务的项目孵化语义部分；
- 共享候选：未闭环工作和架构决策写回可拆为通用底层检查 + Project Incubator 语义扩展。

## 12. 是否回修 Phase 4 / Phase 5 的判断门

runtime 架构草案经 Maker 审阅后，再判断：

- Maker 已确认不回 Phase 4。现有设计流程和边界继续成立；本轮偏差主要来自 Phase 5 / Phase 6 未把 Skill runtime 实现原则拆成清晰任务路径；
- 因此下一步采用 Phase 5 级别的 runtime-first 重新规划，并新增 `DOCS/05-planning/SKILL_1_RUNTIME_REBUILD_PLAN.md`；
- 若 Maker 认为架构过重，应收缩为最小 orchestrator + hard gate runtime；
- 若 Maker 暂不继续 Skill 1.0，应保留当前 Draft 和本文档，暂停实现。

## 13. Maker 待确认

- 是否接受 Skill Runtime Design Template 作为只面向 Skill / Agent runtime 类项目的专用设计模板；
- 是否接受七类 runtime 组件划分；
- 是否接受 Phase 子 Skill / 子模块的最小字段；
- 首批 runtime scripts 是否过多，是否需要先收缩为 `state-engine`、`route-gate`、`retrieve-context` 三个；
- context retriever 首版采用脚本索引、简单 chunk 映射，还是需要 RAG；
- 当前探索性 `SKILL/gates/` 资产是迁移、保留参考，还是后续重建。
