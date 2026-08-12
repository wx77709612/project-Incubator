# Project Incubator V1 Design Traceability

# 1. Mapping Overview

本文档用于追踪 `PROJECT_INCUBATOR_V1_DESIGN.md` 与既有 Project Incubator v0.1 / v0.2 设计文档之间的来源关系。

本文档只负责：

1. 建立 V1 Design 章节与旧文档来源之间的映射关系。
2. 标识哪些旧设计内容需要迁移。
3. 标识哪些旧内容属于 Implementation Plan。
4. 标识哪些旧内容应该废弃。

本文档不负责：

- 修改 `PROJECT_INCUBATOR_V1_DESIGN.md`。
- 修改任何输入文档。
- 创建新的架构方案。
- 补充不存在的设计。
- 执行 Skill、Runtime、references、templates 或 scripts 的实现。

当前 V1 Design 的来源文档包括：


| Source Document                                               | Role in Traceability                                                   |
| ------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `SPECS/PROJECT_INCUBATOR_V1_DESIGN.md`                        | 目标设计文档；本追踪文件以其章节为 Target Chapter。                                      |
| `SPECS/PROJECT_INCUBATOR_DESIGN_SPEC.md`                      | v0.1 / 原始定义来源；提供 Maker、AI、Phase、文档、项目类型、会话规范和愿景。                       |
| `SPECS/PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`              | v0.2 Runtime 架构来源；提供 Runtime / Skill / Agent / Script / Adapter 边界。    |
| `SPECS/PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`      | 迁移来源；提供 Keep / Extract / Refactor / Move / Replace / Deprecated 的判断依据。 |
| `SPECS/PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md` | 实施边界来源；用于识别哪些内容应进入 Implementation Plan 而不是 V1 Design。                  |
| `SPECS/PROJECT_INCUBATOR_RUNTIME_V0.2_TASK_BOARD.md`          | 任务拆分来源；用于识别 Task 级内容不应进入 V1 Design。                                    |
| `SPECS/PROJECT_INCUBATOR_RUNTIME_V0.2_EXECUTION_PROTOCOL.md`  | 执行治理来源；用于识别 Execution Protocol / Builder 执行细节。                         |
| `SPECS/PROJECT_INCUBATOR_RUNTIME_V0.2_VALIDATION_SPEC.md`     | 验证治理来源；用于识别 Validation Level、Acceptance Criteria 和 Result Format。      |
| `SPECS/ARCHITECTURE_DECISIONS.md`                             | 不可违背的长期边界来源；提供 Maker 决策权、状态恢复、Framework 分离、流程深度和 Git 写操作边界。            |




## Source Authority Order

当多个来源文档存在冲突时，按照以下优先级判断：

1. ARCHITECTURE_DECISIONS.md
  作为长期架构约束。
   不允许其他文档覆盖。
2. PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md
  作为 Runtime 边界、职责分离和系统约束来源。
3. PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md
  作为迁移判断依据。
4. PROJECT_INCUBATOR_DESIGN_SPEC.md
  作为原始产品设计和理念来源。
5. PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md
  作为实现顺序参考。
6. PROJECT_INCUBATOR_RUNTIME_V0.2_TASK_BOARD.md
  作为任务拆分参考。
7. PROJECT_INCUBATOR_RUNTIME_V0.2_EXECUTION_PROTOCOL.md
  作为执行治理参考。
8. PROJECT_INCUBATOR_RUNTIME_V0.2_VALIDATION_SPEC.md
  作为验证治理参考。

规则：

- Implementation 文档不能覆盖 Architecture 决策。
- Task 文档不能改变 Design 方向。
- Validation 文档不能定义系统架构。
- Traceability 只能记录关系，不能产生新设计。

Migration Action 定义：


| Migration Action            | Meaning                                                                   |
| --------------------------- | ------------------------------------------------------------------------- |
| Keep                        | 原意适合保留在 V1 Design 中。                                                      |
| Merge                       | 多个旧来源需要合并到同一个 V1 Design 章节。                                               |
| Refine                      | 旧内容方向保留，但需要收敛、改写或去除实现细节。                                                  |
| Move to Implementation Plan | 内容属于任务、执行、验证、文件迁移或实现顺序，应进入 `PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md`。 |
| Deprecated                  | 旧内容不应进入 V1 Design，或已被新的 V1 / Runtime 边界取代。                                |




# 2. Chapter Mapping


| V1 Design Chapter　　　　　　　　　　　　　 | Source Document                                         | Source Section　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Migration Action            |
| ---------------------------------------------| ---------------------------------------------------------| -----------------------------------------------------------------------------------------------------------| -----------------------------|
| `# 1. 项目概述`　　　　　　　　　　　　　　 | `PROJECT_INCUBATOR_DESIGN_SPEC.md`                      | `# 2. 系统定位`、`# 14. 最终愿景`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 | Refine                      |
| `# 1. 项目概述`　　　　　　　　　　　　　　 | `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`              | `# 2. 核心定位`、`# 19. Final Architecture Principle`　　　　　　　　　　　　　　　　　　　　　　　　　　 | Merge                       |
| `# 2. 设计背景`　　　　　　　　　　　　　　 | `PROJECT_INCUBATOR_DESIGN_SPEC.md`                      | `# 1. 文档目的`、`# 13. 系统的核心创新`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 | Merge                       |
| `# 2. 设计背景`　　　　　　　　　　　　　　 | `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`              | `# 1. 文档目的`、`## 2.2 核心目标`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Merge                       |
| `# 3. 设计原则`　　　　　　　　　　　　　　 | `PROJECT_INCUBATOR_DESIGN_SPEC.md`                      | `# 4. 核心设计原则`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 | Refine                      |
| `# 3. 设计原则`　　　　　　　　　　　　　　 | `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`              | `# 3.3 Runtime 核心设计原则`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Merge                       |
| `# 3. 设计原则`　　　　　　　　　　　　　　 | `ARCHITECTURE_DECISIONS.md`                             | `Decision 001` 至 `Decision 004`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Merge                       |
| `# 5. Skill 架构`　　　　　　　　　　　　　 | `PROJECT_INCUBATOR_V1_DESIGN.md`                        | `# 5. Skill 架构`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 | Keep                        |
| `# 5. Skill 架构`　　　　　　　　　　　　　 | `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`              | `# 5. Runtime 与 Skill 的关系`、`# 7. Script 与 AI 职责边界`　　　　　　　　　　　　　　　　　　　　　　　| Refine                      |
| `# 5. Skill 架构`　　　　　　　　　　　　　 | `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`      | `### 6.3 Skill 与 Runtime 的边界`、`## 8. Runtime Physical Boundary`、`### 13.3 Refactor`　　　　　　　　 | Refine                      |
| `# 4. 核心工作流程`　　　　　　　　　　　　 | `PROJECT_INCUBATOR_DESIGN_SPEC.md`                      | `# 6. 项目生命周期`、`# 7. 不同项目类型的推荐路径`　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Refine                      |
| `# 4. 核心工作流程`　　　　　　　　　　　　 | `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`      | `## 4. Default Runtime Lifecycle Stage Model`、`### 4.1 v0.1 Phase 到 Default Lifecycle Stage 的映射`　　 | Merge                       |
| `# 4. 核心工作流程`　　　　　　　　　　　　 | `PROJECT_INCUBATOR_RUNTIME_V0.2_TASK_BOARD.md`          | P0-P5 Task definitions　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Move to Implementation Plan |
| `# 6. 项目上下文模型`　　　　　　　　　　　 | `PROJECT_INCUBATOR_DESIGN_SPEC.md`                      | `# 5. 项目状态模型`、`# 8. 文档体系`、`# 9. 文档生成原则`　　　　　　　　　　　　　　　　　　　　　　　　 | Refine                      |
| `# 6. 项目上下文模型`　　　　　　　　　　　 | `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`              | `# 12. Runtime Data Model Specification`、`# 14. Artifact System Design`、`# 16. Writeback System Design` | Merge                       |
| `# 7. References 设计`　　　　　　　　　　　| `PROJECT_INCUBATOR_DESIGN_SPEC.md`                      | `# 11. 项目共创会话规范`、`# 10. 阶段切换机制`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Refine                      |
| `# 7. References 设计`　　　　　　　　　　　| `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`              | `# 6. Agent 职责模型`、`# 7. Script 与 AI 职责边界`　　　　　　　　　　　　　　　　　　　　　　　　　　　 | Merge                       |
| `# 7. References 设计`　　　　　　　　　　　| `ARCHITECTURE_DECISIONS.md`                             | `Decision 001` 至 `Decision 005`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Merge                       |
| `# 8. Templates 设计`　　　　　　　　　　　 | `PROJECT_INCUBATOR_DESIGN_SPEC.md`                      | `# 8. 文档体系`、`# 9. 文档生成原则`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Refine                      |
| `# 8. Templates 设计`　　　　　　　　　　　 | `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`      | `### 10.7 Templates`、`### 13.1 Keep`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 | Keep                        |
| `# 9. Scripts 设计`　　　　　　　　　　　　 | `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`              | `# 7. Script 与 AI 职责边界`、`# 17. Runtime Evaluation Model`　　　　　　　　　　　　　　　　　　　　　　| Refine                      |
| `# 9. Scripts 设计`　　　　　　　　　　　　 | `PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md` | `## 4. Runtime Component 实施矩阵`、`## 5. 文件迁移策略`　　　　　　　　　　　　　　　　　　　　　　　　　| Move to Implementation Plan |
| `# 10. 非目标`　　　　　　　　　　　　　　　| `PROJECT_INCUBATOR_V1_DESIGN.md`                        | `# 10. 非目标`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Keep                        |
| `# 10. 非目标`　　　　　　　　　　　　　　　| `PROJECT_INCUBATOR_DESIGN_SPEC.md`                      | `## 4.4 Smallest Useful Outcome`、`# 12. 与规格驱动开发流程的关系`　　　　　　　　　　　　　　　　　　　　| Refine                      |
| `# 10. 非目标`　　　　　　　　　　　　　　　| `PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md` | `## 9. 非目标`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Merge                       |
| `# 11. V1 成功标准`　　　　　　　　　　　　 | `PROJECT_INCUBATOR_V1_DESIGN.md`                        | `# 11. V1 成功标准`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 | Keep                        |
| `# 11. V1 成功标准`　　　　　　　　　　　　 | `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`              | `# 10. v0.2 验收标准`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 | Refine                      |
| `# 11. V1 成功标准`　　　　　　　　　　　　 | `PROJECT_INCUBATOR_RUNTIME_V0.2_VALIDATION_SPEC.md`     | `# 8. Acceptance Criteria`、`# 11. Completion Judgment`　　　　　　　　　　　　　　　　　　　　　　　　　 | Move to Implementation Plan |
| `# 12. 后续演进方向`　　　　　　　　　　　　| `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`              | `# 11. 后续演进方向`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Refine                      |
| `# 12. 后续演进方向`　　　　　　　　　　　　| `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`      | `## 14. 迁移优先级`、`## 15. 建议迁移顺序`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Move to Implementation Plan |
| Execution governance　　　　　　　　　　　　| `PROJECT_INCUBATOR_RUNTIME_V0.2_EXECUTION_PROTOCOL.md`  | Whole document　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Move to Implementation Plan |
| Task breakdown　　　　　　　　　　　　　　　| `PROJECT_INCUBATOR_RUNTIME_V0.2_TASK_BOARD.md`          | Whole document　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Move to Implementation Plan |
| Validation governance　　　　　　　　　　　 | `PROJECT_INCUBATOR_RUNTIME_V0.2_VALIDATION_SPEC.md`     | Whole document　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Move to Implementation Plan |
| Deprecated long-form Runtime manual pattern | `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`      | `### 13.6 Deprecated`、`## 11. 架构冲突`　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| Deprecated                  |




# 3. Detailed Mapping



## Target Chapter

`# 1. 项目概述`

来源：

- `PROJECT_INCUBATOR_V1_DESIGN.md`
- `PROJECT_INCUBATOR_DESIGN_SPEC.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`

来源章节：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md`：`# 2. 系统定位`、`# 14. 最终愿景`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`：`# 2. 核心定位`、`# 19. Final Architecture Principle`

迁移内容：

- Project Incubator 是面向 Maker 的 AI 共创项目孵化系统。
- V1 Design 面向重新生成 Skill，而不是复制完整 Framework。
- Maker 保留方向、范围、决策和验收权。
- AI / Skill / Runtime 只帮助项目有序推进。

保留：

- Maker-centered 的系统定位。
- Project Incubator 帮助个人把想法推进为项目的原始目标。
- “Maker 决定方向，系统提供秩序，AI 产生智能”的边界。

删除：

- v0.2 Runtime Component 的具体实现清单。
- P0-P5 任务顺序。
- 目录迁移细节。

后续需要补充：

- V1 Skill 的一句话定位是否要明确为“Codex Skill”。
- V1 Design 是否需要声明它是“基于原定义重新生成的 Skill 设计”。



## Target Chapter

`# 2. 设计背景`

来源：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`
- `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`

来源章节：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md`：`# 1. 文档目的`、`# 13. 系统的核心创新`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`：`# 1. 文档目的`、`## 2.2 核心目标`
- `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`：`## 11. 架构冲突`

迁移内容：

- 上下文丢失、AI 自由发挥、状态缺失是 V1 Design 的核心背景。
- v0.2 文档进一步证明：仅靠自然语言 Skill Instructions 不足以稳定控制流程、状态、Gate 和写回。
- 旧实现中的 Runtime / Skill / Script 混用问题应作为背景，不应直接变成 V1 的实现方案。

保留：

- 问题陈述。
- “对话驱动不足，状态和 Artifact 需要成为恢复依据”的判断。
- AI 需要被边界和项目状态约束的判断。

删除：

- 具体 Runtime Component 迁移矩阵。
- v0.2 P0-P5 执行计划。
- 已经被证伪的“超长 Skill.md 承载全部流程控制”模式。

后续需要补充：

- V1 Design 中“V1 重新生成 Skill”的背景说明目前偏弱，需要标明它与 v0.2 Runtime 设计的关系：吸收边界原则，不直接实现完整 Runtime。



## Target Chapter

`# 3. 设计原则`

来源：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`
- `ARCHITECTURE_DECISIONS.md`

来源章节：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md`：`# 4. 核心设计原则`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`：`# 3.3 Runtime 核心设计原则`
- `ARCHITECTURE_DECISIONS.md`：`Decision 001`、`Decision 002`、`Decision 003`、`Decision 004`

迁移内容：

- Intent First 来自 `Intent Before Process`。
- State Driven 来自 v0.2 的 `状态驱动，而不是对话驱动`。
- Artifact Oriented 来自 v0.1 的 `Documents Drive the Project` 和 v0.2 的 Artifact System。
- Human Decision Boundary 来自 Maker 决策权、Phase 边界和 Agent 权限边界。

保留：

- Intent 优先。
- 项目路径自适应。
- 文档 / Artifact 驱动。
- Maker 决策权。
- 最小有用成果。

删除：

- 将所有项目强制走完整 Phase 0-9 的倾向。
- 让 AI 根据聊天记忆自行决定流程的倾向。
- 将 Runtime 确定性控制完全写成长自然语言说明的倾向。

后续需要补充：

- V1 是否保留 `Runtime First` 作为设计原则，或只保留为 Skill 的边界原则。



## Target Chapter

`# 5. Skill 架构`

来源：

- `PROJECT_INCUBATOR_V1_DESIGN.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`
- `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md`

来源章节：

- `PROJECT_INCUBATOR_V1_DESIGN.md`：`# 5. Skill 架构`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`：`# 5. Runtime 与 Skill 的关系`、`# 7. Script 与 AI 职责边界`
- `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`：`### 6.3 Skill 与 Runtime 的边界`、`## 8. Runtime Physical Boundary`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md`：`## 5. 文件迁移策略`

迁移内容：

- `AGENTS.md`、`SKILL.md`、`SPECS/`、`references/`、`templates/`、`scripts/` 的职责划分应保留为 V1 Skill 架构。
- Skill 应保存入口、加载方式、调用协议和面向 Agent 的解释。
- Runtime-like 确定性流程控制不应继续放在 Skill instruction 主体中。

保留：

- V1 Design 中当前目录结构章节。
- `AGENTS.md` 作为启动 / governance 文档的定位。
- `SKILL.md` 作为 Skill 入口的定位。
- `references/`、`templates/`、`scripts/` 的顶层职责分类。

删除：

- 把 `SKILL.md` 当作完整流程手册的设计。
- 把 Gate、State、Lifecycle 的最终判断写进自然语言 reference 的设计。
- 在 V1 Design 中直接规定 P0-P5 目录迁移任务。

后续需要补充：

- V1 Skill 是否需要单独声明 Runtime Interface 的最小形态。
- `scripts/` 在 V1 中是轻量确定性工具，还是承接未来 Runtime-like 能力的兼容层。



## Target Chapter

`# 4. 核心工作流程`

来源：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md`
- `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`

来源章节：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md`：`# 6. 项目生命周期`、`# 7. 不同项目类型的推荐路径`
- `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`：`## 4. Default Runtime Lifecycle Stage Model`、`### 4.1 v0.1 Phase 到 Default Lifecycle Stage 的映射`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`：`# 15. Task System Design`

迁移内容：

- V1 的 Intent Discovery、Project Definition、Planning、Creation、Validation、Iteration 可从 v0.1 Phase 0-9 压缩而来。
- Default Runtime Lifecycle Stage Model 可作为参考，但不应强制 V1 Skill 实现完整 Runtime lifecycle。
- Task System 的“Task 必须有目标、输入、输出、执行者、验证”可作为流程原则保留。

保留：

- 从想法到定义、计划、创建、验证、迭代的主流程。
- 项目类型影响路径深度的原则。
- 阶段切换需要 Maker 或明确 Gate 的原则。

删除：

- 完整 Phase 0-9 正文展开。
- P0-P5 Runtime Migration 任务清单。
- Runtime Task Execution Lifecycle 的详细执行协议。

后续需要补充：

- V1 工作流程是否需要明确映射到原 Phase 0-9，还是保持 V1 当前更轻量的 6 步流程。



## Target Chapter

`# 6. 项目上下文模型`

来源：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`
- `ARCHITECTURE_DECISIONS.md`

来源章节：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md`：`# 5. 项目状态模型`、`# 8. 文档体系`、`# 9. 文档生成原则`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`：`# 12. Runtime Data Model Specification`、`# 14. Artifact System Design`、`# 16. Writeback System Design`
- `ARCHITECTURE_DECISIONS.md`：`Decision 002`

迁移内容：

- `PROJECT_PROFILE.md`、`PROJECT_STATE.md`、`PROJECT_PLAN.md` 是 V1 Skill 的核心上下文文件候选。
- Project State / Runtime State 的分离原则需要保留为设计边界。
- Artifact authority 和 writeback policy 的思想应保留，但具体 schema 进入 Implementation Plan 或 templates。

保留：

- 项目状态是恢复入口。
- 文档 / Artifact 是长期上下文。
- 一个事实只保留一个权威来源。
- 写回必须服务于后续恢复。

删除：

- 完整 Runtime State YAML schema。
- Event Model、Action Result schema 的实现细节。
- Component 之间的数据交换实现。

后续需要补充：

- V1 的 `PROJECT_PROFILE.md`、`PROJECT_STATE.md`、`PROJECT_PLAN.md` 是否替代原 v0.1 多 Phase 文档，还是作为 Skill 层最小上下文模型。
- 每个上下文文件的最小字段是否放在 V1 Design 或 templates。



## Target Chapter

`# 7. References 设计`

来源：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`
- `ARCHITECTURE_DECISIONS.md`

来源章节：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md`：`# 10. 阶段切换机制`、`# 11. 项目共创会话规范`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`：`# 6. Agent 职责模型`、`# 7. Script 与 AI 职责边界`
- `ARCHITECTURE_DECISIONS.md`：`Decision 001` 至 `Decision 005`

迁移内容：

- References 应保存 Agent 可读的协作规则、判断说明、阶段说明和边界提醒。
- References 不能成为最终 Gate Decision、Runtime Decision 或 Maker Decision 的执行源。
- Maker 决策权、状态恢复、Framework 分离、流程深度、Git 里程碑边界需要在 references 中可被 Agent 消费。

保留：

- `INTENT_DISCOVERY.md`
- `PROJECT_PHASE_MODEL.md`
- `DECISION_RULES.md`
- `VALIDATION_RULES.md`

删除：

- 让 references 承担确定性 gate 执行。
- 让 references 代替 scripts / Runtime Component。
- 长篇无结构的 Agent 流程手册。

后续需要补充：

- 每个 reference 的边界：解释性 guidance，还是可由脚本校验的 rule source。



## Target Chapter

`# 8. Templates 设计`

来源：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md`
- `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`

来源章节：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md`：`# 8. 文档体系`、`# 9. 文档生成原则`
- `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`：`### 10.7 Templates`、`### 13.1 Keep`

迁移内容：

- Templates 是可实例化文档结构，不是当前项目事实。
- Templates 应服务于 `PROJECT_PROFILE.md`、`PROJECT_STATE.md`、`PROJECT_PLAN.md` 等 V1 上下文文件。
- 模板不能替代 Maker 决策或 AI 真实澄清。

保留：

- 模板按需创建。
- 不为完整而完整。
- 模板只保存结构，不保存当前项目事实。

删除：

- 预生成所有 Phase 文档的模式。
- 把模板当作项目状态的模式。

后续需要补充：

- V1 Design 是否列出模板名称即可，还是需要最小字段说明。



## Target Chapter

`# 9. Scripts 设计`

来源：

- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_VALIDATION_SPEC.md`

来源章节：

- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`：`# 7. Script 与 AI 职责边界`、`# 17. Runtime Evaluation Model`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md`：`## 4. Runtime Component 实施矩阵`、`## 5. 文件迁移策略`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_VALIDATION_SPEC.md`：`# 4. Validation Level`、`# 5. Component Validation Rules`

迁移内容：

- Scripts 应承担确定性检查、解析、格式校验和低成本工具执行。
- Runtime Component 的完整迁移矩阵不应进入 V1 Design。
- 测试层级和验证格式属于 Implementation Plan 或 scripts 设计细化。

保留：

- scripts 负责确定性、低成本、可验证的任务。
- scripts 不判断业务价值、不替代 Maker approval、不擅自改变架构。

删除：

- 在 V1 Design 中直接列出 Runtime Component 实施矩阵。
- 在 V1 Design 中实现 Component Test / Integration Test / Scenario Test / Fixture Test 细节。

后续需要补充：

- V1 Skill 的 scripts 是否只包含最小校验器，还是保留 Runtime-like compatibility scripts。



## Target Chapter

`# 10. 非目标`

来源：

- `PROJECT_INCUBATOR_V1_DESIGN.md`
- `PROJECT_INCUBATOR_DESIGN_SPEC.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md`
- `ARCHITECTURE_DECISIONS.md`

来源章节：

- `PROJECT_INCUBATOR_V1_DESIGN.md`：`# 10. 非目标`
- `PROJECT_INCUBATOR_DESIGN_SPEC.md`：`## 4.4 Smallest Useful Outcome`、`# 12. 与规格驱动开发流程的关系`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md`：`## 9. 非目标`
- `ARCHITECTURE_DECISIONS.md`：`Decision 004`

迁移内容：

- V1 不做项目管理平台。
- V1 不自动替代 Maker 决策。
- V1 不强制企业级研发流程。
- V1 不实现复杂 Runtime 系统。
- V1 不把 v0.2 Implementation Plan 的任务细节塞入设计文档。

保留：

- 当前 V1 Design 的非目标列表。
- 小而有用、流程深度自适应的原则。

删除：

- 任何会把 V1 变成完整 runtime implementation 的内容。
- 任何会让 Personal Tool 被迫走商业化验证的内容。

后续需要补充：

- 是否明确声明 V1 不执行 v0.2 P0-P5 Runtime Migration。



## Target Chapter

`# 11. V1 成功标准`

来源：

- `PROJECT_INCUBATOR_V1_DESIGN.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_VALIDATION_SPEC.md`

来源章节：

- `PROJECT_INCUBATOR_V1_DESIGN.md`：`# 11. V1 成功标准`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`：`# 10. v0.2 验收标准`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_VALIDATION_SPEC.md`：`# 8. Acceptance Criteria`、`# 11. Completion Judgment`

迁移内容：

- V1 成功标准应聚焦 Skill 是否可触发、上下文是否可建立、项目是否可持续推进、AI 发散是否受控。
- v0.2 的 Runtime 验收标准可作为参考，但不应原样迁入。
- Validation Spec 的详细验收协议属于 Implementation Plan。

保留：

- V1 当前成功标准。
- 状态恢复、上下文建立、边界控制这些高层验收点。

删除：

- Component Validation、Integration Validation、Fixture Validation 的细则。
- Execution Completion Criteria 的 Task 协议格式。

后续需要补充：

- V1 成功标准是否需要区分“设计完成标准”和“Skill 实现完成标准”。



## Target Chapter

`# 12. 后续演进方向`

来源：

- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`
- `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md`

来源章节：

- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`：`# 11. 后续演进方向`
- `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`：`## 14. 迁移优先级`、`## 15. 建议迁移顺序`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md`：`## 3. P0-P5 实施计划`

迁移内容：

- V1 后续演进可以保留从轻量 Skill 到更强 Runtime / Adapter / Evaluation 的方向。
- P0-P5 迁移优先级不应进入 V1 Design 正文，应转入 Implementation Plan。

保留：

- 后续可能增强 Runtime、Agent 协作、Context Retrieval、Adapter 支持的方向。

删除：

- P0-P5 任务级实施计划。
- Runtime Component physical boundary 的实施细节。

后续需要补充：

- V1 的后续演进是面向 Skill v1.x，还是面向 Runtime v0.2 / v0.3 的衔接路线。



# 4. Implementation Boundary



## 进入：`PROJECT_INCUBATOR_V1_DESIGN.md`

以下内容适合进入 V1 Design：

- Project Incubator 的项目定位。
- Maker / AI / Skill 的高层职责边界。
- Intent First、State Driven、Artifact Oriented、Human Decision Boundary。
- V1 Skill 的目录结构和目录职责。
- V1 核心工作流程。
- V1 项目上下文模型。
- references、templates、scripts 的设计职责。
- V1 非目标。
- V1 成功标准。
- 后续演进方向的高层说明。

不应进入 V1 Design：

- P0-P5 任务拆分。
- Runtime Component 实施矩阵。
- Execution Protocol 的 Task Claim / Validation / Result Report 细节。
- Validation Spec 的测试等级和失败分类细则。
- 文件移动计划。
- 具体 scripts 实现。



## 进入：`PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md`

以下内容应进入后续 Implementation Plan：

- V1 Skill 文件创建 / 修改任务。
- `AGENTS.md`、`SKILL.md`、`references/`、`templates/`、`scripts/` 的具体落地步骤。
- 从旧文档提取 references 的任务拆分。
- 模板文件清单和实例化规则。
- scripts 的最小实现任务。
- 测试和验证步骤。
- 兼容旧项目状态的迁移步骤。
- 是否复用 v0.2 Runtime-like scripts 的执行策略。
- 验收 checklist。

来源依据：

- `PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_TASK_BOARD.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_EXECUTION_PROTOCOL.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_VALIDATION_SPEC.md`



## 进入：`references/`

以下内容适合进入 V1 Skill 的 references：

- Intent discovery guidance。
- Project phase / workflow guidance。
- Decision rules。
- Validation rules。
- Maker decision boundary。
- Agent role boundary。
- AI 不得替代 Maker、不得自行扩 scope、不得跳过阶段门的说明。
- Git / Maker Review 边界的 Agent-facing 说明。

来源依据：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md`
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`
- `ARCHITECTURE_DECISIONS.md`

注意：

references 只能保存解释性和协作性 guidance，不应成为确定性 Runtime Decision source。

## 进入：`templates/`

以下内容适合进入 V1 Skill 的 templates：

- `PROJECT_PROFILE.md` template。
- `PROJECT_STATE.md` template。
- `PROJECT_PLAN.md` template。
- 可选的 Decision / Validation / Review template。
- 文档 metadata 或 authority 字段模板。

来源依据：

- `PROJECT_INCUBATOR_DESIGN_SPEC.md` 的文档体系和文档生成原则。
- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md` 的 Artifact System / Writeback System。
- `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md` 的 Template Asset 判断。

注意：

templates 只保存结构，不保存当前项目事实。

## 进入：`scripts/`

以下内容适合进入 V1 Skill 的 scripts：

- 项目状态文件存在性检查。
- 文档结构校验。
- 模板实例化检查。
- reference / template 路径检查。
- 低成本 deterministic validation。
- 可选的 compatibility check。

来源依据：

- `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md` 的 Script / Runtime 职责边界。
- `PROJECT_INCUBATOR_RUNTIME_V0.2_VALIDATION_SPEC.md` 的 validation 思路。
- `PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md` 的已有效能力优先原则。

注意：

scripts 不应判断业务价值，不应替代 Maker approval，不应自行改变项目方向或设计。

# 5. Pending Design Decisions



## 5.1 Design Decision Required

以下问题必须在更新 PROJECT_INCUBATOR_V1_DESIGN.md 前由 Maker 明确。

### V1 Design 与 Runtime 的关系

需要确定：

- V1 是否只实现 Skill Layer。
- 是否保留 Runtime Interface 概念。
- Runtime-like 能力是否属于未来版本。

当前状态：

Pending Decision。

---



### Context Model 边界

需要确定：

- PROJECT_PROFILE.md
- PROJECT_STATE.md
- PROJECT_PLAN.md

是否作为 V1 最小上下文模型。

需要确定：

- 最小字段。
- 权威来源。
- 更新规则。

当前状态：

Pending Decision。

---



### Reference 与 Script 权限边界

需要确定：

References：

是否只提供解释性规则。

Scripts：

是否只提供 deterministic validation。

当前状态：

Pending Decision。

---



### Phase Model

需要确定：

- V1 是否保留旧 Phase 0-9 映射。
- 是否只保留当前六阶段流程。
- Phase 是否需要 Gate。

当前状态：

Pending Decision。

---



### Project Type Adaptive Depth

需要确定：

不同项目类型：

- Personal Tool
- Public Project
- Business Product
- Content Project
- Learning Project

是否影响：

- Phase 深度。
- Artifact 数量。
- Validation 强度。

当前状态：

Pending Decision。

## 5.2 Missing Design Areas

以下只记录缺失项，不提供解决方案。


| Missing Area　　　　　　　　　　　　　　 | Current Evidence　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 | Impact　　　　　　　　　　　　　　　　　　　　　　　　　|
| ------------------------------------------| --------------------------------------------------------------------------------------------------------------| ---------------------------------------------------------|
| V1 Design 与 v0.2 Runtime 的关系尚未明确 | V1 Design 使用轻量 Skill 架构；v0.2 文档定义完整 Runtime 架构。　　　　　　　　　　　　　　　　　　　　　　　| 后续可能混淆“重新生成 Skill”和“实现 Runtime v0.2”。　　 |
| V1 Skill 的最小 Runtime Interface 未定义 | V1 Design 有 `SKILL.md` 和 `scripts/`，但没有明确 Runtime Interface 边界。　　　　　　　　　　　　　　　　　 | 后续可能让 `SKILL.md` 再次承担过多流程控制。　　　　　　|
| V1 上下文文件字段未冻结　　　　　　　　　| V1 Design 列出 `PROJECT_PROFILE.md`、`PROJECT_STATE.md`、`PROJECT_PLAN.md`，但字段细节未完全对应旧状态模型。 | 后续 templates 难以稳定生成。　　　　　　　　　　　　　 |
| References 的执行权边界未完全写明　　　　| V1 Design 设计 references，但旧 v0.2 明确 references 不应承担 deterministic decision。　　　　　　　　　　　 | 后续可能把 references 写成新的长流程手册。　　　　　　　|
| Scripts 的最小范围未冻结　　　　　　　　 | V1 Design 有 scripts 设计，v0.2 文档有 Runtime Component 和 Evaluation 细则。　　　　　　　　　　　　　　　　| 后续可能过度实现 Runtime-like scripts。　　　　　　　　 |
| V1 Design 成功标准与实现验收标准未分离　 | V1 成功标准偏设计层；Validation Spec 偏实施层。　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　| 后续评审可能混淆设计完成与 Skill 实现完成。　　　　　　 |
| V1 的项目类型路径深度未明确　　　　　　　| 原设计有 Personal Tool / Public Project / Business Product / Content / Learning Project。　　　　　　　　　　| V1 Skill 可能无法判断不同项目应走多深流程。　　　　　　 |
| V1 是否保留 Phase 0-9 映射未明确　　　　 | v0.1 原设计以 Phase 0-9 为主；V1 当前流程压缩为 6 个步骤。　　　　　　　　　　　　　　　　　　　　　　　　　 | 后续完善设计时需要决定是否保留旧 Phase 作为 reference。 |



# 6. Deprecated Source Content

以下旧内容不应迁入 V1 Design：


| Source Content                           | Source Document                                                                               | Reason                                                                     |
| ---------------------------------------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| 超长 `SKILL.md` 作为完整流程手册                   | `PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`、`PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md` | 已被识别为 Skill 过度承担 Runtime 职责的风险。                                            |
| 自然语言 Gate 作为最终判断来源                       | `PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`、`PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md` | 确定性 Gate 应由 scripts / Runtime-like deterministic checks 承担，references 只解释。 |
| AI 根据聊天记忆自行恢复项目状态                        | `ARCHITECTURE_DECISIONS.md`、`PROJECT_INCUBATOR_RUNTIME_V0.2_DESIGN.md`                        | 项目状态必须来自文档 / Artifact，不来自会话记忆。                                             |
| 强制所有项目走完整 Phase 0-9                      | `PROJECT_INCUBATOR_DESIGN_SPEC.md`、`PROJECT_INCUBATOR_V0.1_TO_V0.2_MIGRATION_PLAN.md`         | 与流程深度自适应原则冲突。                                                              |
| 在 V1 Design 中直接嵌入 Runtime Component 实施矩阵 | `PROJECT_INCUBATOR_RUNTIME_V0.2_IMPLEMENTATION_PLAN.md`                                       | 属于 Implementation Plan，不属于设计定位。                                            |
| Task Board 任务正文进入 V1 Design              | `PROJECT_INCUBATOR_RUNTIME_V0.2_TASK_BOARD.md`                                                | 属于执行拆分，不属于 V1 Design。                                                      |
| Execution Protocol 全文进入 V1 Design        | `PROJECT_INCUBATOR_RUNTIME_V0.2_EXECUTION_PROTOCOL.md`                                        | 属于执行治理，应进入 Implementation Plan 或 agent execution reference。                |
| Validation Spec 全文进入 V1 Design           | `PROJECT_INCUBATOR_RUNTIME_V0.2_VALIDATION_SPEC.md`                                           | 属于验证治理，应进入 Implementation Plan 或 scripts validation reference。             |




# 7. Traceability Completion Check


| Check                                  | Result |
| -------------------------------------- | ------ |
| 能解释旧文档如何映射到 V1 Design                  | PASS   |
| 标识旧设计内容迁移方向                            | PASS   |
| 标识 Implementation Plan 内容              | PASS   |
| 标识 references / templates / scripts 边界 | PASS   |
| 标识 Deprecated 内容                       | PASS   |
| 未修改 `PROJECT_INCUBATOR_V1_DESIGN.md`   | PASS   |
| 未修改任何输入文档                              | PASS   |
| 未创建新的架构方案                              | PASS   |
| 未补充不存在的设计方案                            | PASS   |




# 8. Next Use

本文件可作为后续完善 `PROJECT_INCUBATOR_V1_DESIGN.md` 的依据。

建议后续使用顺序：

1. 先依据第 2 节和第 3 节审阅 V1 Design 是否遗漏关键来源。
2. 再依据第 4 节把 implementation、references、templates、scripts 内容分流。
3. 最后依据第 5 节只记录缺失设计区域，由 Maker 决定是否补充到 V1 Design。



# 9. Modification Restriction

在以下决策完成前：

禁止自动修改：

PROJECT_INCUBATOR_V1_DESIGN.md

禁止：

- 根据 Mapping 自动补充设计。
- 根据 Missing Area 自动生成方案。
- 根据旧 Runtime 文档恢复完整 Runtime。

允许：

- 标记来源。
- 标记冲突。
- 提供待决问题。

只有经过 Design Decision 确认后：

才允许更新 V1 Design。