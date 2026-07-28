# Skill 1.0 架构重审清单

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 6 — Build |
| 文档状态 | Draft |
| 权威范围 | Skill 1.0 在 Phase 6 Build 中发现的架构偏差、已确认重审方向、现有 Draft 处理分类和已确认返工入口 |
| 消费 Phase | Phase 6 Build；后续 Design / Planning 受控修订按需消费 |
| 更新条件 | Maker 确认 runtime 架构草案、决定回到 Phase 4 / Phase 5 修订、或调整 Skill 1.0 架构拆分方案 |
| 依赖文档 | `DOCS/PROJECT_STATE.md`、`DOCS/04-design/SKILL_DESIGN.md`、`DOCS/04-design/GATE_EXECUTION_DESIGN.md`、`DOCS/05-planning/ROADMAP.md`、`DOCS/05-planning/MILESTONES.md`、`DOCS/05-planning/VERIFICATION_PLAN.md`、当前 `SKILL/` Draft |
| 最后更新 | 2026-07-28 |

## 1. 重审结论

Maker 已确认 Skill 1.0 不应继续沿着“一个总 Skill 加大量自然语言 reference，由 Agent 自行理解 if / else”的方向实现。

新的候选架构方向为：

- 总 orchestrator；
- Phase 子 Skill 或等价子模块；
- hard gate 独立模块；
- runtime scripts 控制确定性流程；
- AI 只消费脚本 / 检索输出后的最小上下文，负责语义理解、提炼、模糊判断和生成。

当前首个 `SKILL/gates/` Build 切片标记为“结构化 gate 探索性 Draft”。它证明了 gate registry、输出枚举、case fixture 和 checker 的价值，但不再作为继续线性实现的目标架构。

本轮不直接回到 Phase 4 修改设计文档；先在 Phase 6 形成架构重审文档，再由 Maker 决定返工范围。

## 2. 当前问题

- `SKILL.md` 与 `SKILL/references/` 过多承担运行手册职责，容易让 Agent 通过读长文档自行判断流程。
- Phase 0–9 尚未形成独立能力单元，当前总入口试图覆盖过多阶段行为。
- hard gate 仍未成为真正的 runtime 拦截层。
- checker 主要验证配置，还没有控制运行时跳转。
- 上下文读取仍依赖 Agent 主动判断应读哪些 reference，而不是由脚本 / RAG 返回最小相关切片。
- AI 与脚本边界偏反：当前是 Agent 管流程、脚本做辅助验证；目标应是脚本管确定性流程，AI 做语义和生成。

本次偏差的根因不是 Phase 4 采用“使用过程导向设计方法”。该方法仍适合作为默认设计方向，用于理解真实使用过程、角色、输入输出、失败点和验收点。

真正缺失的是面向 Skill / Agent runtime 类项目的专用设计模板：在设计阶段应补充检查哪些流程应由脚本、schema、validator、gate 和 context retriever 承载，哪些部分才交给 AI 推理和生成。该模板不适用于所有项目，只在目标产物是 Skill、Agent workflow、AI 协作协议、自动化 runtime、插件或子 Agent 系统时调用。

## 3. 保留现有内容

- 保留 P6 Skill Draft 中已验证有价值的概念：项目启动、项目接入、状态恢复、Phase 内推进、Maker 审阅、状态写回。
- 保留 `SKILL/references/` 中的领域知识，但降级为 AI 生成参考，不作为流程控制或 gate 判定主承载。
- 保留 `SKILL/assets/templates/` 作为未来项目初始化模板。
- 保留结构化 gate 的数据思想：gate id、输入字段、输出枚举、阻断规则、safe action 和 case fixture。

## 4. 拆成子 Skill / 子模块

- 每个 Phase 拆成独立子 Skill 或等价模块：`phase-00-idea` 至 `phase-09-archive`。
- 项目接入 / 初始化单独成模块，负责新项目、既有项目接入和模板实例化前确认。
- Skill Runtime Design Template 作为设计模板库中的项目类型专用模板，在 Phase 4 目标产物命中 Skill / Agent runtime 时调用；它不是所有项目的通用 gate。
- Builder 交接与返回审阅单独成模块。
- hard gate 单独成模块或 Skill，作为全局拦截层。
- Maker 任务 Prompt 生成单独成模块，避免混入状态恢复逻辑。

## 5. 下沉为脚本

- 状态管理与流程控制：当前 Stage / Phase、上一步输出是否合法、下一步跳转。
- Gate runtime router：候选 gate、缺失输入、命中 / 未命中、阻断输出、safe action。
- JSON schema / 输出格式校验：Phase 输出、Ticket、Builder handoff、gate case、`PROJECT_STATE.md` 字段。
- Git / 未闭环任务检查：分支、Diff、ahead / behind、是否允许进入新写入任务。
- Prompt hygiene 检查：Prompt 正文是否搬运状态、Git 历史或权威文档集合。
- Context retriever：根据当前 Phase、任务类型和 gate 结果提取最小上下文 chunk。
- 低成本确定性任务：文件存在性、路径合法性、格式转换、索引更新和简单枚举分类。

## 6. 只保留为 AI 生成 reference

- Phase 中的对话风格、提问方式和 Maker 协作语气。
- 如何解释 gate 输出给 Maker。
- 如何把脚本返回的结构化结果转成自然语言报告。
- 非结构化文档的摘要、对比和技术可行性分析。
- 模糊判断场景的指导，例如“这个想法是否值得进入下一阶段”或“这份文档是否表达清楚”。
- 示例、反例和协作边界说明。

## 7. 已确认下一步

Maker 已确认采用方案 A：

- 在 Phase 6 内先形成 runtime 架构草案，再决定是否回修 Phase 4 / Phase 5。

其余方案暂不执行：

- 方案 B：直接回到 Phase 4，受控修订 Skill 1.0 设计；
- 方案 C：回到 Phase 5，先重拆以 runtime scripts 和子 Skill 为中心的新 Build 任务；
- 方案 D：仅保留当前探索性 Draft，暂停 Skill 1.0 实现。

下一步应新增一份 Phase 6 runtime 架构草案，明确 orchestrator、Phase 子 Skill、hard gate 模块、runtime scripts、context retriever、validators 与 AI 生成 reference 的职责边界和数据流。

在 runtime 架构草案被 Maker 审阅前，不继续扩展当前 `SKILL.md`、`SKILL/references/` 或 `SKILL/gates/` 实现。
