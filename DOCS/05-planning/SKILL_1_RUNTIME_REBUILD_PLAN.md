# Skill 1.0 Runtime Rebuild Plan

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 5 — Planning |
| 文档状态 | Draft |
| 权威范围 | Skill 1.0 在 Phase 6 架构重审后确认的 runtime-first 重新实现路径、任务顺序、非目标、验证口径和重新进入 Phase 6 Build 的边界 |
| 消费 Phase | Phase 5–6，后续 Phase 按需 |
| 更新条件 | Maker 调整 runtime-first 实现路径、首批任务顺序、脚本范围、子 Skill 拆分方式、验证口径或 Build 进入条件 |
| 依赖文档 | `DOCS/06-build/SKILL_1_ARCHITECTURE_REVIEW.md`、`DOCS/06-build/SKILL_1_RUNTIME_ARCHITECTURE_DRAFT.md`、`DOCS/05-planning/ROADMAP.md`、`DOCS/05-planning/MILESTONES.md`、`DOCS/05-planning/VERIFICATION_PLAN.md`、`DOCS/PROJECT_STATE.md` |
| 最后更新 | 2026-07-28 |

## 1. 背景

Maker 已确认不回 Phase 4。现有 Phase 4 设计流程和边界本身成立，问题主要出在 Phase 5 / Phase 6 没有把 Skill runtime 的实现原则拆成可执行路径，导致 Phase 6 Build 将大量确定性流程落成自然语言 reference。

因此当前不再继续扩展现有 `SKILL.md`、`SKILL/references/` 或 `SKILL/gates/` Draft，而是在 Phase 5 重新规划 runtime-first 的任务实现路径，再回到 Phase 6 重新构建。

## 2. Rebuild 原则

- 过程导向设计方法继续保留为默认设计方向。
- Skill Runtime Design Template 作为 Skill / Agent runtime 类项目的专用设计模板，补充 runtime 实现原则。
- 确定性流程优先脚本化，不交给 Agent 脑内判断。
- AI 负责语义理解、非结构化提炼、模糊判断和动态生成。
- Context 必须由索引 / 检索 / chunk selector 控制，不让 AI 盲读大文档。
- Gate 必须成为 runtime 拦截能力，不只是解释性 reference。
- Build 任务必须先能用样例验证，再进入实现。

## 3. 保留与暂停

保留：

- Phase 4 的总体 Skill 设计、流程边界和 Maker 决策权；
- 当前 P6 Draft 中已验证有价值的项目启动、接入、恢复、Maker 审阅和状态写回概念；
- `SKILL/gates/` 中 gate schema、输出枚举、case fixture 和 checker 的探索价值；
- `SKILL/assets/templates/` 的生产模板方向。

暂停：

- 继续扩展当前 `SKILL.md`；
- 继续扩展自然语言 runtime references；
- 沿当前 `SKILL/gates/` Draft 继续实现完整 gate runtime；
- 安装、发布、完整自动化或 Codex Skill 分发。

## 4. 新实现路径

### R1 — Runtime Orchestrator 与 State Engine

目标：优先让 Skill 1.0 的主流程具备可运行的 runtime 控制入口，定义总 orchestrator 与 state engine 的最小输入、输出和跳转规则。

输出：

- 当前 Phase / Stage 枚举；
- 任务类型枚举；
- 上一步输出合法性检查；
- 下一步 transition 枚举；
- `INPUT_INCOMPLETE` / `STATE_INVALID` 失败输出。

验收：

- 给定当前 `PROJECT_STATE.md` 摘要和 Maker 指令，能稳定输出当前任务类型、允许动作和下一步候选；
- Maker 只说“继续”时，不自动解释为 Git 授权、Phase 切换或实现继续。

### R2 — Hard Gate Runtime Router

目标：把探索性 gate registry / case 迁移为真正 runtime router 的规划输入，并区分可跨 Skill 复用的通用门槛与 Project Incubator 专用门槛。

R2 不应把所有门槛都绑定到 Project Incubator Skill。应拆为两层：

| 层级 | 职责 | 适用范围 |
| --- | --- | --- |
| 通用 hard gate Skill | AI 执行安全、Git 写操作、上下文完整性、本地协议、承载类型、Prompt hygiene、长期规则沉淀等通用拦截 | 不依赖 Project Incubator 生成的项目，也可供其他 Skill / Agent runtime 复用 |
| Project Incubator gate Skill / 模块 | Phase 切换、项目孵化状态、权威文档集合、范围推进、Builder 交接、Project Incubator 特有状态写回 | 只在 Project Incubator 或采用其协议的项目中使用 |

当前探索性 `SKILL/gates/` 资产应先分类，再迁移或重建。

候选分类：

| Gate | 建议归属 | 说明 |
| --- | --- | --- |
| `GATE_GIT_WRITE` | 通用 hard gate Skill | Git 写操作授权是跨项目通用 AI 执行边界 |
| `GATE_CONTEXT_INTEGRITY` | 通用 hard gate Skill | 长上下文、压缩污染和关键动作前重读权威输入是通用风险 |
| `GATE_LOCAL_PROTOCOL` | 通用 hard gate Skill | 避免通用模型习惯覆盖本地协议，适用于任意有本地协议的项目 |
| `GATE_CARRIER_TYPE` | 通用 hard gate Skill | 产物承载类型错位是跨 Skill / 文档 / 代码 / Prompt 的通用问题 |
| `GATE_CORRECTION_DEPOSITION` | 通用 hard gate Skill | 单次纠偏不应自动沉淀为长期规则，适用于所有长期协作 Skill |
| `GATE_ARCHITECTURE_DECISION` | 通用 hard gate Skill；Project Incubator 可扩展 | 长期架构边界写回是通用高风险动作；Project Incubator 可补自身 Decision 结构 |
| `GATE_PHASE_TRANSITION` | Project Incubator gate Skill / 模块；可抽象通用阶段机接口 | 当前 Phase 0–9 和 Exit Criteria 属于项目孵化器协议 |
| `GATE_AUTHORITY_SOURCE` | Project Incubator gate Skill / 模块；通用 Skill 可保留 authority path check | 当前权威文档集合和状态入口属于 Project Incubator 文档系统 |
| `GATE_SCOPE_EXPANSION` | Project Incubator gate Skill / 模块 | 当前范围、Phase 和孵化目标推进属于项目孵化器语义 |
| `GATE_BUILDER_HANDOFF` | Project Incubator gate Skill / 模块；通用 Skill 可保留 task completeness validator | AI Builder 角色和交接协议来自 Project Incubator / Codex 协作模型 |
| `GATE_UNCLOSED_WORK` | 两层共享 | Git / Diff 状态可通用；“是否属于同一项目孵化任务续作”属于 Project Incubator |

输出：

- `route-gate` 的结构化输入；
- gate candidate selection；
- 缺失输入处理；
- 封闭输出枚举；
- 阻断结果和 safe action；
- gate case fixtures。
- 通用 hard gate registry / cases；
- Project Incubator gate registry / cases；
- 两层 gate 调用顺序和冲突处理规则。

验收：

- 同一输入稳定输出同一 gate 结果；
- 命中阻断后停止后续实现动作；
- checker 只负责配置验证，router 负责运行时判定。
- 通用 gate 不依赖 Project Incubator 的 `DOCS/`、Phase、状态入口或特定文档结构；
- Project Incubator gate 可以消费项目孵化器状态入口和 Phase 规则；
- 同一动作同时命中通用 gate 和项目孵化器 gate 时，先执行通用安全阻断，再执行项目语义阻断。

### R3 — Context Retriever

目标：定义最小上下文提取机制，避免 AI 盲读完整大文档。

输出：

- 文档索引字段；
- chunk anchor / reason / source 格式；
- 全文读取例外条件；
- retriever 输出 schema。

验收：

- 给定 Phase、任务类型和 gate 结果，只返回相关 chunk；
- 能说明哪些文档被排除及原因；
- 默认不返回全文。

### R4 — Phase 子 Skill / 子模块

目标：把 Phase 0–9 从总入口中拆为可单独消费的阶段能力单元。

输出：

- Phase 子模块最小 schema；
- 每个 Phase 的入口条件、输入、输出、validator / gate 契约和下一步候选；
- 非 Phase 模块清单：project intake、builder handoff、builder return review、maker prompt、hard gate。

验收：

- 总 orchestrator 不再承载全部 Phase 细节；
- Phase 子模块不负责全局状态跳转或 Git 边界；
- 子模块能被 state engine / orchestrator 调用。

### R5 — AI Generation References

目标：把自然语言 reference 降级为解释层和生成辅助，不再承载确定性流程控制。

输出：

- gate 输出解释 reference；
- Phase 对话风格 reference；
- 文档生成 reference；
- 模糊判断 reference。

验收：

- reference 不再独立决定 gate、状态跳转、读取范围或 schema 合法性；
- AI 只在收到 runtime 输出后消费 reference。

### R6 — Script / Validator Contracts 汇总

目标：在完整 Skill runtime 流程、Phase 子模块和 AI reference 边界明确后，汇总所有应由脚本处理的确定性任务契约。本阶段只定义契约、schema 和 fixtures，不实现脚本。

输出：

- `PROJECT_STATE.md` schema / field check contract；
- Ticket / Builder handoff schema contract；
- Prompt hygiene check contract；
- Git boundary read-only check contract；
- path / authority index check contract；
- output artifact schema check contract；
- 每个 contract 的输入、输出枚举、失败输出和 fixtures。

验收：

- 每个确定性判断都有脚本契约或明确说明为何暂不脚本化；
- 结构缺失、Prompt 搬运状态、Builder Ticket 缺字段等场景都有 fixtures；
- 不要求 AI 自行发现确定性格式错误。

### R7 — Script Implementation

目标：在 R1–R6 已明确 Skill 全流程、AI / 脚本分工、确定性判断契约和 fixtures 后，再实现脚本。脚本实现不提前于契约完成。

输出：

- `state-engine`；
- `route-gate`；
- `retrieve-context`；
- validators：Prompt hygiene、Builder handoff、authority path、Git boundary、output artifact 等按契约逐步实现；
- 对应测试。

验收：

- 脚本输入 / 输出与 R6 contracts 一致；
- fixtures 通过；
- 脚本只处理确定性任务，不替 Maker 或 AI 做模糊判断。

### R8 — Runtime 实现原则和设计模板沉淀

目标：在主流程 runtime 路径和脚本实现边界可验证后，再把 Skill Runtime Design Template 沉淀为 Phase 4 可复用的项目类型专用设计模板输入。本项不阻塞 R1–R7。

输出：

- runtime 实现原则清单；
- Skill / Agent runtime 项目触发条件；
- 设计阶段必须回答的问题；
- Build 前必须验证的样例类型。

验收：

- 能解释为什么本项目命中该模板；
- 能区分模板适用项目和不适用项目；
- 不把该模板升级为所有项目通用 gate。

## 5. 首批 Build 切片建议

重新进入 Phase 6 Build 时，首个切片不应再从 `SKILL.md` 或自然语言 gate reference 开始。

建议顺序：

1. 创建 runtime schema 与 fixtures：state input、task input、gate input、context request；
2. 实现最小 `state-engine`；
3. 实现最小 `route-gate`；
4. 实现最小 `retrieve-context`，先用静态索引 / chunk map，不引入复杂 RAG；
5. 定义 Phase 子模块 schema 和 AI generation references；
6. 汇总 script / validator contracts 与 fixtures；
7. 最后按 contracts 实现脚本；
8. 再重写 `SKILL.md` 为薄 orchestrator 入口，并迁移 / 精简现有 references。

## 6. 非目标

本轮 replanning 不处理：

- Phase 4 Active 设计文档回修；
- 完整插件或 Skill 安装发布；
- 完整 RAG 系统；
- 所有 Phase 子 Skill 一次性实现；
- 全量迁移当前 `SKILL/references/`；
- Git 写操作自动化；
- 外部用户验证。

## 7. 进入 Phase 6 Rebuild 的条件

在重新 Build 前，至少需要确认：

- Maker 接受 runtime-first 任务顺序；
- 首批 Build 切片只做 schema / state-engine / route-gate / retrieve-context 的最小闭环；
- 当前探索性 `SKILL/gates/` 资产作为参考迁移，而不是继续线性扩展；
- 探索性 gate 资产已按通用 hard gate 与 Project Incubator gate 分类；
- 自然语言 reference 不再作为确定性流程控制承载；
- 验证方式以 fixtures 和脚本输出为主，而不是文本完整性。

## 8. Maker 待确认

- 是否接受 R1–R5 先明确 runtime 主流程和 AI reference，R6 汇总 script / validator contracts，R7 最后实现脚本，R8 再沉淀设计模板；
- 首批 Build 是否收缩为 `state-engine`、`route-gate`、`retrieve-context` 三件套；
- R6 是否只沉淀 script / validator contracts，不提前实现脚本；
- R7 脚本实现是否等 R1–R6 完成后再开始；
- Phase 子 Skill 是否先定义 schema，暂不一次性实现所有 Phase；
- 当前探索性 `SKILL/gates/` 资产迁移还是后续重建；
- 是否接受通用 hard gate Skill 与 Project Incubator gate Skill / 模块分层。
