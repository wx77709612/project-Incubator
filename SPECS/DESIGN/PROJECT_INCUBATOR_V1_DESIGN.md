# Project Incubator V1 Design


# 1. 项目概述


## 1.1 项目名称

Project Incubator


## 1.2 项目定位

Project Incubator 是一个 AI 辅助项目孵化 Skill。

它帮助 Maker 将一个初始 Idea 转化为：

- 明确的问题定义；
- 可执行的项目计划；
- 可验证的项目成果；
- 持续迭代的项目状态。


Project Incubator 的目标不是替代 Maker 做项目管理，而是帮助 AI Agent 在长期项目协作过程中：

- 理解项目目标；
- 保持项目上下文；
- 遵循项目状态推进；
- 降低 AI 发散风险；
- 提升项目交付质量。


---

# 2. 设计背景


## 2.1 当前问题


在长期 AI 协作项目中，常见问题包括：


### 上下文丢失

AI 在不同对话中无法持续理解：

- 项目目标；
- 当前阶段；
- 已完成内容；
- 未解决问题。


### AI 自由发挥

AI 可能：

- 自行改变项目方向；
- 生成大量无价值文档；
- 进行未经授权的架构调整；
- 优化不存在的问题。


### 缺少项目状态管理

AI 不知道：

- 当前项目在哪里；
- 下一步应该做什么；
- 什么事情已经确定不能修改。



---

# 3. 设计原则


## 3.1 Intent First

项目首先必须明确：

- 为什么创建；
- 解决什么问题；
- 服务什么对象；
- 成功标准是什么。


Agent 不应在项目 Intent 不明确时直接进入实现阶段。


---

## 3.2 State Driven

项目推进必须基于明确且唯一的当前状态来源。

PROJECT_STATE.md 是项目当前状态的唯一 Source of Truth。

Agent 不得根据：

- 历史对话；
- 个人推测；
- 未确认计划；
- 未执行方案；

判断项目当前状态。

Workflow、Gate、Agent 与 Runtime 必须以 PROJECT_STATE.md 表达的当前状态作为项目推进依据。

PROJECT_STATE.md 的具体结构、生命周期和 Authority 由：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_CONTEXT_MODEL_DESIGN.md

定义。

PROJECT_STATE.md 的访问与修改规则由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md

定义。

---

## 3.3 Artifact Oriented

项目推进以实际成果为核心。


Artifact 包括：

- 文档；
- 代码；
- 设计稿；
- 视频；
- Skill；
- 发布成果。


不以：

- 文档数量；
- 流程完整度；
- 计划复杂度

作为项目进展衡量标准。


---

## 3.4 Human Decision Boundary

Maker 保留最终决策权。


Agent 可以：

- 分析；
- 提供方案；
- 发现风险；
- 执行明确任务。


Agent 不可以：

- 替代 Maker 做战略决策；
- 修改项目目标；
- 自行扩大项目范围。


---

# 4. Workflow Architecture


Project Incubator V1 使用 Workflow 作为项目推进流程管理模块。


Workflow 在系统架构中的职责：

- 定义项目推进流程的组织方式；
- 管理 Phase 之间的架构关系；
- 提供 Runtime 执行所需的流程定义。


Workflow 不负责：

- 定义具体 Phase Domain Model；
- 定义 Phase 生命周期细节；
- 定义 Phase 输入输出；
- 定义 Artifact Flow；
- 执行 Runtime 操作。


Workflow 与其他模块关系：

- Workflow 提供流程方向；
- Runtime 根据 Workflow 执行确定性流程；
- Gate 根据流程要求提供验证机制；
- Context 提供 Workflow 执行所需项目上下文。


具体 Workflow Domain Model 由：

PROJECT_INCUBATOR_V1_WORKFLOW_DESIGN.md

定义。

---

# 5. Skill 架构


## 5.1 Skill Architecture Overview


Project Incubator V1 Skill 采用：

Skill Package + Runtime Architecture

模型。


Skill Package 负责：

- 提供 Project Incubator 能力入口；
- 组织 References；
- 管理 Templates；
- 管理 Runtime 能力。


Runtime Architecture 负责：

- 支撑项目流程的确定性执行；
- 协调 Workflow、Context 与 Gate；
- 使用 Script 等确定性能力完成自动化处理和验证；
- 保证项目状态推进符合既定规则。

Artifact 不属于独立 Core Module。

Artifact 是 Workflow 推进过程中产生和流转的项目成果。


Runtime 不替代 Agent：

Agent 负责：

- 理解项目目标；
- 生成方案；
- 提供创造性内容；
- 处理非确定性问题。


Runtime 负责：

- 执行确定性流程；
- 维护系统边界；
- 防止非法状态变化。


Runtime 详细执行机制由：

PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

---

## 5.2 Skill Package Structure

Project Incubator V1 采用以下 Skill Package 顶层结构：

PROJECT_INCUBATOR/

├── SKILL.md
├── README.md
├── AGENTS.md
├── runtime/
├── references/
├── templates/
└── scripts/

各部分的架构职责：

SKILL.md：

- 提供 Project Incubator 的 Skill 入口。

README.md：

- 提供面向使用者的说明。

AGENTS.md：

- 定义 Agent 使用该 Skill 时需要遵守的行为边界。

runtime/：

- 承载 Project Incubator 的确定性执行能力。

references/：

- 承载 Agent 和 Runtime 所需的知识与定义。

templates/：

- 承载项目上下文和项目成果的标准化生成基础。

scripts/：

- 承载可自动化执行的确定性工具能力。

本文件只定义 Skill Package 的顶层结构和总体职责。

Runtime 内部结构、具体生成文件和实现位置分别由 Runtime Specification 与 Implementation Plan 定义。

---

## 5.3 Maker、Agent 与 Runtime 边界

Project Incubator V1 采用 Maker、Agent 与 Runtime 职责分离模型。

Maker 负责：

- 确认项目目标；
- 确认项目范围；
- 作出重要项目决策；
- 授权影响项目方向的变更。

Agent 负责：

- 理解 Maker 意图；
- 分析项目上下文；
- 提出方案和建议；
- 完成需要判断、推理和创造性的任务；
- 向 Runtime 提出确定性执行请求。

Runtime 负责：

- 承载确定性执行能力；
- 维护项目推进的系统边界；
- 协调 Workflow、Context、Gate 和 Artifact 等核心模块；
- 防止未经允许的状态变化。

职责边界：

- Maker 保留最终决策权；
- Agent 不直接改变 Runtime State；
- Agent 不绕过 Runtime 执行确定性状态变化；
- Runtime 不替代 Maker 作出项目决策；
- Runtime 不替代 Agent 完成创造性工作。

Runtime 的具体执行机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

---

## 5.4 Runtime Architecture Boundary

Runtime Architecture 是 Project Incubator V1 的确定性执行层。

Runtime Architecture 与核心模块及能力的关系：

- Workflow 提供项目推进流程定义；
- Context 提供项目身份、当前状态、计划和决策信息；
- Gate 提供项目推进必须满足的门槛；
- Script 提供可自动执行的确定性工具能力；
- Runtime 协调上述模块与能力完成受控执行。

Artifact 是 Workflow 推进过程中产生和流转的项目成果，不属于独立 Core Module。

Runtime 可以协调 Artifact 相关的确定性处理，但不定义：

- Artifact Domain Model；
- Artifact Lifecycle；
- Artifact Flow；
- Artifact 数据结构。

Validation 是 Runtime 使用的确定性能力，不属于独立 Core Module。

Validation 用于：

- 检查既定条件是否满足；
- 为 Gate Evaluation 提供验证结果；
- 支撑 Runtime 阻止不符合规则的项目推进。

Runtime Architecture 只在本文件中定义：

- Runtime 在整体系统中的定位；
- Runtime 与 Workflow、Context、Gate、Script 的关系；
- Runtime 与 Maker、Agent 的职责边界；
- Artifact 与 Validation 的架构归属。

本文件不定义：

- Runtime Lifecycle；
- Component Loading；
- Execution Flow；
- Context Interaction 执行机制；
- Gate Invocation；
- Script Invocation；
- Validation 执行流程；
- Runtime Component 的内部行为。

Workflow Domain Model 与 Artifact Flow 由：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_WORKFLOW_DESIGN.md

定义。

Runtime 与 Validation 的具体执行机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

---


## 5.5 Runtime Specification Reference

Skill Runtime 的具体执行机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

---


## 5.6 Phase Advisory Layer


Phase Advisory 是 Project Incubator V1 提供的 Agent 辅助能力。


Phase Advisory 在系统中的职责：

- 帮助 Agent 理解当前项目阶段；
- 提供阶段性指导能力；
- 辅助 Maker 进行项目判断。


Phase Advisory 不属于 Workflow Runtime。


Phase Advisory 与其他模块关系：

- Workflow 提供当前流程阶段信息；
- Context 提供项目上下文；
- Agent 基于 Context 生成阶段指导。


Phase Advisory 不负责：

- 修改项目状态；
- 执行 Workflow Transition；
- 执行 Gate Decision。


Phase Advisory 详细设计由：

PROJECT_INCUBATOR_V1_PHASE_ADVISORY_DESIGN.md

定义。

---

## 5.7 Gate Architecture

Gate 是 Project Incubator V1 的项目推进边界模块。

Gate 在系统架构中的职责：

- 表达项目推进必须满足的门槛；
- 连接 Workflow 的推进要求与 Runtime 的受控执行；
- 防止项目在条件不足或未经授权时继续推进；
- 为需要 Maker 确认的项目变化提供边界。

Gate 与其他模块的关系：

- Workflow 表达项目推进过程中的 Gate Requirement；
- Gate Domain Model 定义 Gate 的领域语义；
- Runtime 根据 Gate Contract 执行 Gate 检查；
- Agent 可以提供需要判断和推理的评估信息；
- Maker 对需要人工授权的项目变化保留最终决定权。

Gate 不负责：

- 执行 Runtime 流程；
- 定义 Script 实现；
- 替代 Maker 作出项目决策；
- 在本文件中定义具体 Gate Type、Lifecycle 或 Invocation 规则。

Gate Domain Model 由：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_GATE_DESIGN.md

定义。

Gate Invocation Contract 由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_GATE_CONTRACT.md

定义。

---

## 5.8 Artifact Boundary

Artifact 是 Project Incubator V1 项目推进过程中产生的实际成果。

Artifact 不属于独立 Core Module。

Artifact 在总体架构中的作用：

- 表示项目推进产生的实际成果；
- 连接项目阶段、执行任务和成果验证；
- 为 Maker 与 Agent 提供可识别的项目产出；
- 支撑项目进展以实际成果衡量。

Artifact 的架构归属：

- Workflow 定义何时需要产生 Artifact；
- Workflow 定义 Artifact 在项目阶段之间的流转关系；
- Agent 负责生成需要判断、推理或创造性的 Artifact；
- Runtime 协调 Artifact 相关的确定性处理；
- Validation 检查 Artifact 是否满足既定要求；
- Gate 使用相关验证结果判断项目是否可以继续推进。

Artifact 不负责：

- 定义项目当前状态；
- 执行 Workflow Transition；
- 执行 Gate Decision；
- 控制 Runtime；
- 保存项目长期上下文。

本文件不定义：

- Artifact 类型模型；
- Artifact 数据结构；
- Artifact Schema；
- Artifact Lifecycle；
- Artifact Runtime Flow。

Artifact Flow 由：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_WORKFLOW_DESIGN.md

定义。

Artifact 相关的确定性执行与验证机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

---

# 6. Context Architecture

Project Incubator V1 使用 Context Layer 管理项目长期上下文。

V1 Core Context 包括：

- PROJECT_PROFILE.md；
- PROJECT_STATE.md；
- PROJECT_PLAN.md；
- PROJECT_DECISIONS.md。

各 Core Context 的架构定位：

PROJECT_PROFILE.md：

- 表达项目身份、长期目标和核心约束。

PROJECT_STATE.md：

- 表达项目当前实际状态；
- 是项目当前状态的唯一 Source of Truth。

PROJECT_PLAN.md：

- 表达项目未来准备如何推进。

PROJECT_DECISIONS.md：

- 保存 Maker 已确认的重要项目决策。

Context Layer 与其他模块的关系：

- Agent 使用 Context 理解项目；
- Workflow 使用 Context 判断项目所处位置；
- Gate 使用 Context 获取门槛判断所需的项目事实；
- Runtime 负责协调 Context 的加载和受控更新。

本文件不定义：

- Context 字段；
- Context Schema；
- Context 访问权限；
- Context Mutation 流程；
- Runtime Context Invocation。

Context 的具体领域模型由：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_CONTEXT_MODEL_DESIGN.md

定义。

Context 的访问规则由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md

定义。

---

# 7. References Architecture

References 是 Project Incubator Skill Package 的知识层。

References 在系统架构中的职责：

- 为 Agent 提供项目协作所需的背景知识和判断依据；
- 为 Runtime 所依赖的结构化定义提供承载位置；
- 支撑不同 Project Type 和 Runtime Capability 的知识扩展。

References 与 Agent 的关系：

- Agent 可以使用 References 理解项目规则、设计原则和判断依据；
- References 不替代 Agent 进行推理或作出项目决策。

References 与 Runtime 的关系：

- Runtime 可以使用符合对应 Contract 的结构化定义；
- References 不直接执行 Runtime 行为；
- References 不直接修改 State；
- References 不直接执行 Gate；
- References 不替代 Script。

References 的具体领域模型、交互规则、加载方式和实现文件，由对应 Design、Contract、Runtime 和 Implementation 文档定义。、

---


# 8. Templates Architecture

Templates 是 Project Incubator Skill Package 的标准化生成基础。

V1 Core Templates 包括：

- PROJECT_PROFILE.template.md；
- PROJECT_STATE.template.md；
- PROJECT_PLAN.template.md；
- DECISION_RECORD.template.md；
- IMPLEMENTATION_PLAN.template.md。

各 Template 的架构作用：

PROJECT_PROFILE.template.md：

- 用于创建项目身份与长期目标上下文。

PROJECT_STATE.template.md：

- 用于创建项目当前状态上下文。

PROJECT_PLAN.template.md：

- 用于创建项目生命周期规划 Context。

IMPLEMENTATION_PLAN.template.md：

- 用于创建 P3 Execution Planning 的 Implementation Plan Phase Artifact。
- 用于将 Solution Design 转换为可执行实施方案。
- 不属于 Core Context，不替代 PROJECT_PLAN.md。

DECISION_RECORD.template.md：

- 用于创建 Maker 已确认的重要决策记录。

Templates 与其他模块的关系：

- Context Model 定义这些 Context 的领域含义、结构和生命周期；
- Agent 根据项目情况生成对应内容；
- Runtime 可以协调模板的初始化和受控更新流程；
- Implementation Layer 负责创建具体模板文件。

本文件不定义：

- Template 字段；
- Template Schema；
- Template 渲染机制；
- Template 生成脚本；
- Template 校验实现。

---

# 9. Scripts Architecture

Scripts 是 Project Incubator Skill Package 的确定性工具能力层。

Scripts 在系统架构中的职责：

- 承载可以自动化执行的确定性操作；
- 支撑 Runtime 完成文件处理、数据处理和自动化验证；
- 降低 Agent 使用推理处理确定性问题的需要。

Scripts 与 Runtime 的关系：

- Runtime 负责协调和调用 Script 能力；
- Scripts 向 Runtime 返回确定性执行结果；
- Scripts 不直接控制项目状态变化。

Scripts 不负责：

- 作出 Maker Decision；
- 决定 Project Direction；
- 替代 Agent Reasoning；
- 自主执行 Phase Transition；
- 自主执行 State Transition。

Script 的输入输出规则由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_SCRIPT_CONTRACT.md

定义。

Script 的调用机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

具体 Script 文件及实现任务由：

SPECS/IMPLEMENTATION/PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md

定义。

---

# 10. 非目标


Project Incubator V1 不负责：


## 项目管理平台

不替代：

- Jira；
- Notion；
- Trello。


---

## 自动替代 Maker 决策

Agent 不自动决定：

- 产品方向；
- 商业策略；
- 项目价值。


---

## 企业级研发流程

不实现：

- 审批流程；
- 团队权限管理；
- 企业项目治理。


---

## 独立 Runtime 平台

V1 不实现：

- 独立 Runtime 平台；
- 多项目 Runtime 服务；
- 企业级 Agent 编排平台；
- 分布式任务调度系统。

V1 实现：

- Skill Package 内嵌 Runtime Layer；
- Runtime 的确定性执行能力；
- 对 Workflow、Context 与 Gate 的执行支撑；
- Script 调度与确定性验证能力。

Validation 是 Runtime 使用的确定性能力，不作为独立 Core Module。

---

# 11. V1 成功标准


Project Incubator V1 成功标准：


## Skill 可以被触发

Agent 能正确理解：

什么时候使用 Project Incubator。


---

## 项目上下文可以建立

Project Incubator V1 能够创建并持续维护：

- PROJECT_PROFILE.md；
- PROJECT_STATE.md；
- PROJECT_PLAN.md；
- PROJECT_DECISIONS.md。

这些文件共同构成 V1 Core Context。

项目可以依靠 Core Context 在不同会话中恢复：

- 项目身份；
- 当前状态；
- 未来计划；
- 已确认决策。

---

## 项目可以持续推进

Agent 能根据：

- Intent；
- State；
- Plan；

执行下一步行动。


---

## AI 发散得到控制

Agent 不会：

- 随意改变目标；
- 无意义扩展范围；
- 创建大量无价值文档。

---

## Agent 可以提供阶段性项目指导


Agent 能根据：

- Project Type；
- Current Phase；
- Project Context；

提供：

- 当前阶段关注事项；
- 风险提醒；
- 推荐 Artifact；
- Maker 决策问题。


Agent 不替代 Maker 决策。

该能力由：

Phase Advisory Layer

提供。

详细设计见：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_PHASE_ADVISORY_DESIGN.md

---

## Runtime 可以控制项目推进

Runtime 能够依据：

- Workflow；
- Core Context；
- Gate；

约束项目的确定性推进过程。

Runtime 可以协调 Workflow 产生的 Artifact，并使用确定性 Validation 能力为 Gate Evaluation 提供验证结果。

Runtime 能够阻止不符合既定规则或未经授权的项目状态变化。

具体 Runtime 执行机制由 Runtime Specification 定义。

---
# 12. 后续演进方向


未来版本可以增加：


- 自动状态更新；
- 更强 Validation；
- Agent 编排；
- 多 Skill 协作；
- 项目历史分析；
- 项目复盘能力。


V1 优先验证：

简单、稳定、可使用的 AI 项目孵化流程。
